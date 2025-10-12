"""Command-line interface for LinkedIn CV Generator."""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.pdf.generator import PDFGenerator
from src.scraper.linkedin_scraper import LinkedInScraper
from src.scraper.parser import ProfileParser
from src.utils.image_processor import ImageProcessor

console = Console()


def display_banner():
    """Display the ASCII art banner."""
    banner_path = Path(__file__).parent.parent / "assets" / "banner.txt"
    try:
        with open(banner_path, "r", encoding="utf-8") as f:
            banner = f.read()
        console.print(banner, style="bold cyan")
    except FileNotFoundError:
        console.print("\n[bold cyan]LinkedIn CV Generator[/bold cyan]", justify="center")
        console.print("[cyan]📄 Professional CV Generator 📄[/cyan]\n", justify="center")


def normalize_profile_url(input_str: str) -> str:
    """Normalize profile input to full LinkedIn URL.
    
    Accepts:
    - Full URL: https://www.linkedin.com/in/username/
    - Username only: username
    
    Returns:
    - Full LinkedIn profile URL
    """
    input_str = input_str.strip().rstrip('/')
    
    # If it's already a full URL, return as-is
    if input_str.startswith('http://') or input_str.startswith('https://'):
        return input_str
    
    # If it contains linkedin.com, assume it's a partial URL without protocol
    if 'linkedin.com' in input_str:
        if not input_str.startswith('http'):
            return f'https://{input_str}'
        return input_str
    
    # Otherwise, treat as username and construct full URL
    username = input_str.replace('@', '').strip()
    return f'https://www.linkedin.com/in/{username}/'


@click.command()
@click.argument("profile_url", type=str, required=False)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    default="./output",
    help="Output directory for generated PDFs",
)
@click.option(
    "-t",
    "--template",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default=None,
    help="Custom HTML template path",
)
@click.option(
    "--html-file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default=None,
    help="Path to manually saved LinkedIn profile HTML file (bypasses scraping)",
)
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
@click.option(
    "--login",
    is_flag=True,
    help="Launch browser to log in to LinkedIn and save session",
)
@click.option(
    "--json",
    "export_json",
    is_flag=True,
    help="Export profile data to JSON instead of generating PDF",
)
@click.option(
    "--json-file",
    type=click.Path(),
    default="profile_data.json",
    help="JSON output filename (default: profile_data.json)",
)
@click.option(
    "--no-banner",
    is_flag=True,
    help="Suppress banner display (used when called from menu)",
)
@click.option(
    "--extract-html",
    is_flag=True,
    help="Extract HTML from all LinkedIn profile sections",
)
@click.option(
    "--parse-html",
    type=str,
    default=None,
    help="Parse HTML files for a username to extract JSON data",
)
@click.option(
    "--generate-pdf",
    type=str,
    default=None,
    help="Generate PDF from JSON data for a username",
)
def main(
    profile_url: Optional[str],
    output_dir: str,
    template: Optional[str],
    html_file: Optional[str],
    headless: bool,
    debug: bool,
    login: bool,
    export_json: bool,
    json_file: str,
    no_banner: bool,
    extract_html: bool,
    parse_html: Optional[str],
    generate_pdf: Optional[str],
):
    """Generate a professional PDF CV from a LinkedIn profile.

    PROFILE_URL: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)
                 Not required if --html-file, --parse-html, or --generate-pdf is provided.
    
    Workflow:
    1. --extract-html: Scrape all profile sections and save HTML files
    2. --parse-html <username>: Parse saved HTML files to extract JSON data
    3. --generate-pdf <username>: Generate PDF from saved JSON data
    """
    if not no_banner:
        display_banner()
    
    # Handle login mode
    if login:
        try:
            scraper = LinkedInScraper(debug=debug)
            result = asyncio.run(scraper.login_interactive())
            sys.exit(0 if result else 1)
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Login cancelled by user[/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[red]❌ Error during login: {str(e)}[/red]")
            if debug:
                console.print_exception()
            sys.exit(1)
    
    # Handle parse-html mode
    if parse_html:
        try:
            asyncio.run(parse_html_to_json(parse_html, output_dir, debug))
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[red]❌ Error parsing HTML: {str(e)}[/red]")
            if debug:
                console.print_exception()
            sys.exit(1)
    
    # Handle generate-pdf mode
    if generate_pdf:
        try:
            asyncio.run(generate_pdf_from_json(generate_pdf, output_dir, template, debug))
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[red]❌ Error generating PDF: {str(e)}[/red]")
            if debug:
                console.print_exception()
            sys.exit(1)

    # Handle extract-html mode
    if extract_html:
        if not profile_url:
            console.print("[red]❌ Error: Profile URL required for --extract-html[/red]")
            sys.exit(1)
        try:
            asyncio.run(extract_all_html(profile_url, output_dir, headless, debug))
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[red]❌ Error extracting HTML: {str(e)}[/red]")
            if debug:
                console.print_exception()
            sys.exit(1)
    
    # Load .env file if it exists and PROFILE_URL is not provided
    if not profile_url and not html_file:
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("PROFILE_URL="):
                        profile_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if profile_url:
                            console.print(f"[dim]ℹ️  Using PROFILE_URL from .env file[/dim]")
                            break
    
    # If still no profile_url and no html_file, prompt the user
    if not profile_url and not html_file:
        console.print()
        console.print("[yellow]⚠️  No PROFILE_URL found in .env file[/yellow]")
        console.print()
        console.print("[dim]You can enter:[/dim]")
        console.print("[dim]  • Full URL: https://www.linkedin.com/in/username/[/dim]")
        console.print("[dim]  • Username only: username[/dim]")
        console.print()
        profile_input = console.input("[cyan]Enter LinkedIn profile URL or username: [/cyan]")
        profile_input = profile_input.strip()
        
        if not profile_input:
            console.print("[red]❌ Error: Profile URL/username cannot be empty[/red]")
            sys.exit(1)
        
        profile_url = normalize_profile_url(profile_input)
        console.print(f"[dim]ℹ️  Using profile: {profile_url}[/dim]")

    # Normalize profile_url if provided
    if profile_url:
        profile_url = normalize_profile_url(profile_url)
    
    if profile_url and html_file:
        console.print("[yellow]⚠️  Both URL and HTML file provided. Using HTML file.[/yellow]")

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        # Run the async workflow
        asyncio.run(generate_cv(profile_url, output_path, template, html_file, headless, debug, export_json, json_file))
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")
        if debug:
            console.print_exception()
        sys.exit(1)


async def generate_cv(
    profile_url: Optional[str],
    output_path: Path,
    template: Optional[str],
    html_file: Optional[str],
    headless: bool,
    debug: bool,
    export_json: bool,
    json_file: str,
):
    """Main workflow to generate CV from LinkedIn profile or export to JSON."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Step 1: Get HTML content (either from file or by scraping)
        if html_file:
            task1 = progress.add_task("📂 Loading HTML file...", total=None)
            
            try:
                with open(html_file, "r", encoding="utf-8") as f:
                    html_content = f.read()
                progress.update(task1, completed=True)
                console.print("   [green]✓[/green] HTML file loaded successfully!")
            except Exception as e:
                progress.update(task1, completed=True)
                raise Exception(f"Failed to read HTML file: {str(e)}")
        else:
            task1 = progress.add_task("🔍 Scraping LinkedIn profile...", total=None)

            scraper = LinkedInScraper(headless=headless, debug=debug)
            html_content = await scraper.scrape_profile(profile_url)

            progress.update(task1, completed=True)
            console.print("   [green]✓[/green] Profile scraped successfully!")

        # Step 2: Parse profile data
        task2 = progress.add_task("📋 Parsing profile data...", total=None)

        parser = ProfileParser(debug=debug)
        profile_data = parser.parse(html_content)

        progress.update(task2, completed=True)
        console.print(
            f"   [green]✓[/green] Parsed {len(profile_data.get('sections', []))} sections!"
        )
        
        # Check if we got meaningful data
        has_meaningful_data = (
            len(profile_data.get('experience', [])) > 0 or
            len(profile_data.get('education', [])) > 0 or
            len(profile_data.get('skills', [])) > 0 or
            profile_data.get('about')
        )

        # If JSON export is requested, save and exit
        if export_json:
            import json
            from datetime import datetime
            
            # Add metadata
            profile_data['_metadata'] = {
                'extracted_at': datetime.now().isoformat(),
                'profile_url': profile_url,
                'sections_found': len(profile_data.get('sections', [])),
                'has_meaningful_data': has_meaningful_data,
            }
            
            # Get username from profile data or URL
            username = profile_data.get('username', 'linkedin-profile')
            if username == 'linkedin-profile' and profile_url:
                # Try to extract from URL
                import re
                match = re.search(r'linkedin\.com/in/([^/]+)', profile_url)
                if match:
                    username = match.group(1)
            
            # Create user-specific output directory
            user_output_dir = output_path / username
            user_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON in user directory
            json_path = user_output_dir / 'profile_data.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            console.print(f"\n[green]✅ Profile data exported to: {json_path}[/green]")
            console.print(f"[dim]File size: {json_path.stat().st_size:,} bytes[/dim]")
            
            # Display summary
            console.print("\n[bold]Data Summary:[/bold]")
            for key, value in profile_data.items():
                if key.startswith('_'):
                    continue
                if isinstance(value, list):
                    console.print(f"  • {key}: {len(value)} items")
                elif value:
                    preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    console.print(f"  • {key}: {preview}")
            
            # Warning if minimal data
            if not has_meaningful_data:
                console.print("\n[yellow]⚠️  WARNING: Only basic profile data was extracted![/yellow]")
                console.print("[yellow]   This usually means you're not logged in to LinkedIn.[/yellow]")
                console.print("\n[cyan]To fix this:[/cyan]")
                console.print("  1. Run the login command: [bold]./run.sh[/bold] → option 3")
                console.print("  2. Or extract cookies: [bold]./run.sh[/bold] → option 4")
                console.print("  3. Then try exporting again")
                console.print("\n[dim]See docs/AUTHENTICATION_GUIDE.md for more details[/dim]")
            return

        # Step 3: Process profile picture (if available)
        profile_image_data = None
        if profile_data.get("profile_picture_url"):
            task3 = progress.add_task("📸 Processing profile picture...", total=None)

            try:
                image_processor = ImageProcessor()
                profile_image_data = image_processor.process(
                    profile_data["profile_picture_url"]
                )
                progress.update(task3, completed=True)
                console.print("   [green]✓[/green] Profile picture ready!")
            except Exception as e:
                progress.update(task3, completed=True)
                console.print(f"   [yellow]⚠️  Profile picture unavailable: {str(e)}[/yellow]")
        else:
            console.print("   [dim]ℹ️  No profile picture found[/dim]")

        # Add profile image to data
        profile_data["profile_image_data"] = profile_image_data

        # Step 4: Generate PDF
        task4 = progress.add_task("📄 Generating professional PDF CV...", total=None)

        generator = PDFGenerator(template_path=template)
        
        # Get username from profile data or URL
        username = profile_data.get("username", "linkedin-profile")
        if username == 'linkedin-profile' and profile_url:
            # Try to extract from URL
            import re
            match = re.search(r'linkedin\.com/in/([^/]+)', profile_url)
            if match:
                username = match.group(1)
        
        # Create user-specific output directory
        user_output_dir = output_path / username
        user_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with username and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{username}_{timestamp}.pdf"
        output_file = user_output_dir / output_filename

        generator.generate(profile_data, str(output_file))

        progress.update(task4, completed=True)
        console.print("   [green]✓[/green] Professional PDF CV generated successfully!")

    # Success message
    console.print()
    
    # Warning if minimal data
    if not has_meaningful_data:
        console.print(
            Panel(
                f"[bold yellow]⚠️  Warning: Limited Data Extracted[/bold yellow]\n\n"
                f"The generated CV only contains basic information (name, headline, location).\n"
                f"Experience, education, and skills are missing.\n\n"
                f"[bold]This usually means you're not logged in to LinkedIn.[/bold]\n\n"
                f"[cyan]To fix this:[/cyan]\n"
                f"  1. Run: [bold]./run.sh[/bold] → option 4 (Login)\n"
                f"  2. Or: [bold]./run.sh[/bold] → option 5 (Extract cookies)\n"
                f"  3. Then regenerate the CV\n\n"
                f"[dim]See: docs/AUTHENTICATION_GUIDE.md for details[/dim]",
                border_style="yellow",
                padding=(1, 2),
            )
        )
        console.print()
    
    console.print(
        Panel(
            f"[bold green]✅ Done![/bold green]\n\n"
            f"PDF saved: [cyan]{output_file}[/cyan]\n"
            f"File size: [dim]{output_file.stat().st_size:,} bytes[/dim]\n\n"
            f"[dim]Ready to send to any company![/dim]",
            border_style="green",
            padding=(1, 2),
        )
    )


async def extract_all_html(profile_url: str, output_dir: str, headless: bool, debug: bool):
    """Extract HTML from all LinkedIn profile sections."""
    import json
    import re
    
    profile_url = normalize_profile_url(profile_url)
    
    # Extract username from URL
    match = re.search(r'linkedin\.com/in/([^/]+)', profile_url)
    if not match:
        raise ValueError("Could not extract username from profile URL")
    username = match.group(1)
    
    # Create output directories
    output_path = Path(output_dir)
    user_output_dir = output_path / username / "html"
    user_output_dir.mkdir(parents=True, exist_ok=True)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🌐 Extracting HTML from all sections...", total=None)
        
        scraper = LinkedInScraper(headless=headless, debug=debug)
        html_sections = await scraper.scrape_all_sections(profile_url)
        
        progress.update(task, completed=True)
        console.print("   [green]✓[/green] HTML extraction completed!")
    
    # Save each section's HTML
    console.print("\n[cyan]Saving HTML files...[/cyan]")
    for section_name, html_content in html_sections.items():
        if html_content:
            html_file = user_output_dir / f"{section_name}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            console.print(f"  ✓ {section_name}.html ({len(html_content):,} bytes)")
        else:
            console.print(f"  [dim]⊘ {section_name}.html (no data)[/dim]")
    
    # Save metadata
    metadata = {
        'profile_url': profile_url,
        'username': username,
        'extracted_at': datetime.now().isoformat(),
        'sections': list(html_sections.keys()),
    }
    metadata_file = user_output_dir / 'metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    console.print(f"\n[green]✅ HTML extraction complete![/green]")
    console.print(f"[cyan]Files saved in: {user_output_dir}[/cyan]")
    console.print(f"\n[dim]Next step: Use option 2 to extract JSON or option 1 to generate PDF[/dim]")


async def parse_html_to_json(username: str, output_dir: str, debug: bool):
    """Parse saved HTML files to extract JSON data."""
    import json
    
    output_path = Path(output_dir)
    user_output_dir = output_path / username
    html_dir = user_output_dir / "html"
    
    # Check if HTML directory exists
    if not html_dir.exists():
        raise ValueError(f"HTML directory not found: {html_dir}\nPlease run option 1 (Extract HTML) first.")
    
    # Load metadata
    metadata_file = html_dir / 'metadata.json'
    if not metadata_file.exists():
        raise ValueError(f"Metadata file not found: {metadata_file}")
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    console.print(f"[cyan]Parsing HTML for: {username}[/cyan]")
    console.print(f"[dim]Profile URL: {metadata.get('profile_url')}[/dim]")
    console.print(f"[dim]Extracted: {metadata.get('extracted_at')}[/dim]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📊 Parsing HTML and extracting data...", total=None)
        
        parser = ProfileParser(debug=debug)
        
        # Parse each section
        profile_data = {}
        
        # Parse main profile
        profile_html_file = html_dir / 'profile.html'
        if profile_html_file.exists():
            with open(profile_html_file, 'r', encoding='utf-8') as f:
                profile_html = f.read()
            profile_data = parser.parse(profile_html)
        
        # Parse experience section
        experience_html_file = html_dir / 'experience.html'
        if experience_html_file.exists():
            with open(experience_html_file, 'r', encoding='utf-8') as f:
                experience_html = f.read()
            # Parse experience from detail page
            experience_data = parser.parse_experience_detail(experience_html)
            if experience_data:
                profile_data['experience'] = experience_data
        
        # Parse education section
        education_html_file = html_dir / 'education.html'
        if education_html_file.exists():
            with open(education_html_file, 'r', encoding='utf-8') as f:
                education_html = f.read()
            # Parse education from detail page
            education_data = parser.parse_education_detail(education_html)
            if education_data:
                profile_data['education'] = education_data
        
        # Parse skills section
        skills_html_file = html_dir / 'skills.html'
        if skills_html_file.exists():
            with open(skills_html_file, 'r', encoding='utf-8') as f:
                skills_html = f.read()
            # Parse skills from detail page
            skills_data = parser.parse_skills_detail(skills_html)
            if skills_data:
                profile_data['skills'] = skills_data
        
        # TODO: Parse other sections (certifications, projects, languages, etc.)
        
        progress.update(task, completed=True)
        console.print("   [green]✓[/green] HTML parsing completed!")
    
    # Add metadata
    profile_data['_metadata'] = {
        'extracted_at': metadata.get('extracted_at'),
        'parsed_at': datetime.now().isoformat(),
        'profile_url': metadata.get('profile_url'),
        'username': username,
    }
    
    # Save JSON
    json_file = user_output_dir / 'profile_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[green]✅ JSON data extracted![/green]")
    console.print(f"[cyan]File saved: {json_file}[/cyan]")
    console.print(f"[dim]File size: {json_file.stat().st_size:,} bytes[/dim]")
    
    # Display summary
    console.print("\n[bold]Data Summary:[/bold]")
    for key, value in profile_data.items():
        if key.startswith('_'):
            continue
        if isinstance(value, list):
            console.print(f"  • {key}: {len(value)} items")
        elif value:
            preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            console.print(f"  • {key}: {preview}")
    
    # Clean up HTML files
    import shutil
    if html_dir.exists():
        console.print(f"\n[dim]🧹 Cleaning up HTML files...[/dim]")
        shutil.rmtree(html_dir)
        console.print(f"[dim]✓ HTML files removed[/dim]")
    
    console.print(f"\n[cyan]💾 JSON data ready for PDF generation (option 1)[/cyan]")


async def generate_pdf_from_json(username: str, output_dir: str, template: Optional[str], debug: bool):
    """Generate PDF from saved JSON data."""
    import json
    
    output_path = Path(output_dir)
    user_output_dir = output_path / username
    json_file = user_output_dir / 'profile_data.json'
    
    # Check if JSON exists
    if not json_file.exists():
        raise ValueError(f"JSON file not found: {json_file}\nPlease run option 2 (Extract JSON) first.")
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        profile_data = json.load(f)
    
    console.print(f"[cyan]Generating PDF for: {username}[/cyan]")
    console.print(f"[dim]JSON file: {json_file}[/dim]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Step 1: Process profile picture (if available)
        profile_image_data = None
        if profile_data.get("profile_picture_url"):
            task1 = progress.add_task("📸 Processing profile picture...", total=None)
            
            try:
                image_processor = ImageProcessor()
                profile_image_data = image_processor.process(
                    profile_data["profile_picture_url"]
                )
                progress.update(task1, completed=True)
                console.print("   [green]✓[/green] Profile picture ready!")
            except Exception as e:
                progress.update(task1, completed=True)
                console.print(f"   [yellow]⚠️  Profile picture unavailable: {str(e)}[/yellow]")
        else:
            console.print("   [dim]ℹ️  No profile picture found[/dim]")
        
        # Add profile image to data
        profile_data["profile_image_data"] = profile_image_data
        
        # Step 2: Generate PDF
        task2 = progress.add_task("📄 Generating professional PDF CV...", total=None)
        
        generator = PDFGenerator(template_path=template)
        
        # Generate filename with username and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{username}_{timestamp}.pdf"
        output_file = user_output_dir / output_filename
        
        generator.generate(profile_data, str(output_file))
        
        progress.update(task2, completed=True)
        console.print("   [green]✓[/green] Professional PDF CV generated successfully!")
    
    # Clean up intermediate files (HTML and JSON)
    import shutil
    
    # Remove HTML directory if it exists
    html_dir = user_output_dir / "html"
    if html_dir.exists():
        console.print(f"\n[dim]🧹 Cleaning up HTML files...[/dim]")
        shutil.rmtree(html_dir)
    
    # Remove JSON file if it exists
    if json_file.exists():
        console.print(f"[dim]🧹 Cleaning up JSON file...[/dim]")
        json_file.unlink()
    
    # Success message
    console.print()
    console.print(
        Panel(
            f"[bold green]✅ Done![/bold green]\n\n"
            f"PDF saved: [cyan]{output_file}[/cyan]\n"
            f"File size: [dim]{output_file.stat().st_size:,} bytes[/dim]\n\n"
            f"[dim]Ready to send to any company![/dim]",
            border_style="green",
            padding=(1, 2),
        )
    )


if __name__ == "__main__":
    main()
