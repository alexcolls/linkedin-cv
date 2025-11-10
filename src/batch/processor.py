"""Batch processing for generating multiple LinkedIn CVs."""
import asyncio
import csv
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from src.exceptions import LinkedInCVError, ValidationError
from src.pdf.generator import PDFGenerator
from src.exporters.html_exporter import HTMLExporter
from src.scraper.linkedin_scraper import LinkedInScraper
from src.scraper.parser import ProfileParser
from src.security import SecurityValidator
from src.utils.image_processor import ImageProcessor
from src.utils.qr_generator import QRGenerator

console = Console()


class BatchProcessor:
    """Process multiple LinkedIn profiles in batch."""

    def __init__(
        self,
        output_dir: str,
        theme: str = "modern",
        output_format: str = "pdf",
        headless: bool = True,
        add_qr_code: bool = True,
        custom_colors: Optional[Dict[str, str]] = None,
        max_concurrent: int = 3,
    ):
        """Initialize batch processor.

        Args:
            output_dir: Directory for generated CVs
            theme: Template theme to use
            output_format: Output format (pdf or html)
            headless: Run browser in headless mode
            add_qr_code: Include QR codes in CVs
            custom_colors: Custom color overrides
            max_concurrent: Maximum concurrent processing tasks
        """
        self.output_dir = Path(output_dir)
        self.theme = theme
        self.output_format = output_format
        self.headless = headless
        self.add_qr_code = add_qr_code
        self.custom_colors = custom_colors
        self.max_concurrent = max_concurrent
        self.results = []
        self.validator = SecurityValidator()

    async def process_batch(self, profiles: List[Dict[str, str]]) -> Dict[str, any]:
        """Process multiple profiles in batch.

        Args:
            profiles: List of profile dictionaries with 'url' and optional 'name'

        Returns:
            Dictionary with processing results
        """
        console.print(f"\n[bold cyan]🚀 Starting batch processing of {len(profiles)} profiles...[/bold cyan]\n")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Track results
        successful = []
        failed = []
        start_time = datetime.now()

        # Create semaphore for concurrent processing
        semaphore = asyncio.Semaphore(self.max_concurrent)

        # Process profiles with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Processing profiles ({self.max_concurrent} concurrent)...",
                total=len(profiles)
            )

            # Create tasks for all profiles
            async def process_with_semaphore(profile_data):
                async with semaphore:
                    result = await self._process_single_profile(profile_data)
                    progress.advance(task)
                    return result

            # Run all tasks
            tasks = [process_with_semaphore(profile) for profile in profiles]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Categorize results
            for i, result in enumerate(results):
                profile = profiles[i]
                if isinstance(result, Exception):
                    failed.append({
                        'profile': profile,
                        'error': str(result)
                    })
                elif result.get('success'):
                    successful.append(result)
                else:
                    failed.append({
                        'profile': profile,
                        'error': result.get('error', 'Unknown error')
                    })

        # Calculate statistics
        duration = (datetime.now() - start_time).total_seconds()
        
        # Display summary
        self._display_summary(successful, failed, duration)

        return {
            'total': len(profiles),
            'successful': len(successful),
            'failed': len(failed),
            'duration': duration,
            'results': successful,
            'errors': failed
        }

    async def _process_single_profile(self, profile_data: Dict[str, str]) -> Dict[str, any]:
        """Process a single profile.

        Args:
            profile_data: Dictionary with 'url' and optional 'name'

        Returns:
            Result dictionary
        """
        profile_url = profile_data.get('url', '').strip()
        profile_name = profile_data.get('name', '')

        try:
            # Validate profile URL
            profile_url = self.validator.validate_linkedin_url(profile_url)
            
            # Validate profile name if provided
            if profile_name:
                profile_name = self.validator.validate_username(profile_name)
            # Step 1: Scrape profile
            scraper = LinkedInScraper(headless=self.headless, debug=False)
            html_content = await scraper.scrape_profile(profile_url)

            # Step 2: Parse profile
            parser = ProfileParser(debug=False)
            parsed_data = parser.parse(html_content)

            # Step 3: Process profile picture
            profile_image_data = None
            if parsed_data.get("profile_picture_url"):
                try:
                    image_processor = ImageProcessor()
                    profile_image_data = await image_processor.process(
                        parsed_data["profile_picture_url"]
                    )
                except Exception:
                    pass  # Ignore image processing errors

            parsed_data["profile_image_data"] = profile_image_data

            # Step 4: Generate QR code if enabled
            if self.add_qr_code and profile_url:
                try:
                    qr_gen = QRGenerator(box_size=10, border=1)
                    qr_data = qr_gen.generate(profile_url)
                    parsed_data["qr_code"] = qr_data
                    parsed_data["profile_url"] = profile_url
                    parsed_data["linkedin_url"] = profile_url
                except Exception:
                    parsed_data["qr_code"] = None

            # Step 5: Generate CV
            username = parsed_data.get("username", "profile")
            if not username or username == "profile":
                # Extract from URL
                import re
                match = re.search(r'linkedin\.com/in/([^/]+)', profile_url)
                if match:
                    username = match.group(1)
                elif profile_name:
                    username = profile_name.replace(' ', '_').lower()

            # Create user directory
            user_dir = self.output_dir / username
            user_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = "html" if self.output_format.lower() == "html" else "pdf"
            output_file = user_dir / f"{username}_{timestamp}.{extension}"

            # Generate CV
            if self.output_format.lower() == "html":
                exporter = HTMLExporter(
                    theme=self.theme,
                    custom_colors=self.custom_colors,
                )
                exporter.export(parsed_data, str(output_file))
            else:
                generator = PDFGenerator(
                    theme=self.theme,
                    custom_colors=self.custom_colors,
                )
                generator.generate(parsed_data, str(output_file))

            return {
                'success': True,
                'profile_url': profile_url,
                'username': username,
                'output_file': str(output_file),
                'name': parsed_data.get('name', 'Unknown')
            }

        except Exception as e:
            return {
                'success': False,
                'profile_url': profile_url,
                'error': str(e)
            }

    def _display_summary(self, successful: List[Dict], failed: List[Dict], duration: float):
        """Display batch processing summary.

        Args:
            successful: List of successful results
            failed: List of failed results
            duration: Total processing time in seconds
        """
        console.print("\n" + "=" * 80)
        console.print("[bold cyan]📊 Batch Processing Summary[/bold cyan]")
        console.print("=" * 80 + "\n")

        # Statistics
        total = len(successful) + len(failed)
        success_rate = (len(successful) / total * 100) if total > 0 else 0

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Profiles", str(total))
        table.add_row("Successful", f"[green]{len(successful)}[/green]")
        table.add_row("Failed", f"[red]{len(failed)}[/red]")
        table.add_row("Success Rate", f"{success_rate:.1f}%")
        table.add_row("Duration", f"{duration:.2f}s")
        table.add_row("Avg Time/Profile", f"{duration/total:.2f}s" if total > 0 else "N/A")
        table.add_row("Output Format", self.output_format.upper())
        table.add_row("Theme", self.theme)

        console.print(table)
        console.print()

        # Successful profiles
        if successful:
            console.print("[bold green]✅ Successful Profiles:[/bold green]")
            for result in successful[:10]:  # Show first 10
                console.print(f"  • {result['name']} ({result['username']})")
                console.print(f"    [dim]{result['output_file']}[/dim]")
            if len(successful) > 10:
                console.print(f"  [dim]... and {len(successful) - 10} more[/dim]")
            console.print()

        # Failed profiles
        if failed:
            console.print("[bold red]❌ Failed Profiles:[/bold red]")
            for result in failed[:5]:  # Show first 5
                console.print(f"  • {result['profile'].get('url', 'Unknown')}")
                console.print(f"    [red]{result['error']}[/red]")
            if len(failed) > 5:
                console.print(f"  [dim]... and {len(failed) - 5} more[/dim]")
            console.print()

    @staticmethod
    def load_from_csv(csv_file: str) -> List[Dict[str, str]]:
        """Load profiles from CSV file.

        CSV format: url,name (name is optional)

        Args:
            csv_file: Path to CSV file

        Returns:
            List of profile dictionaries

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        csv_path = Path(csv_file)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file}")

        profiles = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate headers
            if 'url' not in reader.fieldnames:
                raise ValueError("CSV must have 'url' column")

            for row in reader:
                url = row.get('url', '').strip()
                if url:
                    profiles.append({
                        'url': url,
                        'name': row.get('name', '').strip()
                    })

        if not profiles:
            raise ValueError("No valid profiles found in CSV")

        return profiles

    @staticmethod
    def create_sample_csv(output_file: str = "profiles.csv"):
        """Create a sample CSV file for batch processing.

        Args:
            output_file: Path to output CSV file
        """
        sample_data = [
            {'url': 'https://linkedin.com/in/username1', 'name': 'John Doe'},
            {'url': 'https://linkedin.com/in/username2', 'name': 'Jane Smith'},
            {'url': 'https://linkedin.com/in/username3', 'name': ''},
        ]

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'name'])
            writer.writeheader()
            writer.writerows(sample_data)

        console.print(f"[green]✅ Sample CSV created: {output_file}[/green]")
        console.print("[dim]Edit this file and add your LinkedIn profile URLs[/dim]")
