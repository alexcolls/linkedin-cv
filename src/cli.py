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
def main(
    profile_url: Optional[str],
    output_dir: str,
    template: Optional[str],
    html_file: Optional[str],
    headless: bool,
    debug: bool,
    login: bool,
):
    """Generate a professional PDF CV from a LinkedIn profile.

    PROFILE_URL: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)
                 Not required if --html-file is provided.
    """
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
        asyncio.run(generate_cv(profile_url, output_path, template, html_file, headless, debug))
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
):
    """Main workflow to generate CV from LinkedIn profile."""

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

        parser = ProfileParser()
        profile_data = parser.parse(html_content)

        progress.update(task2, completed=True)
        console.print(
            f"   [green]✓[/green] Parsed {len(profile_data.get('sections', []))} sections!"
        )

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
        username = profile_data.get("username", "linkedin-profile")
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        output_filename = f"{username}_{timestamp}.pdf"
        output_file = output_path / output_filename

        generator.generate(profile_data, str(output_file))

        progress.update(task4, completed=True)
        console.print("   [green]✓[/green] Professional PDF CV generated successfully!")

    # Success message
    console.print()
    console.print(
        Panel(
            f"[bold green]✅ Done![/bold green]\n\n"
            f"Your professional CV is ready at:\n"
            f"📄 [cyan]{output_file}[/cyan]\n\n"
            f"[dim]Ready to send to any company![/dim]",
            border_style="green",
            padding=(1, 2),
        )
    )


if __name__ == "__main__":
    main()
