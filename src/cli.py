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
def main(
    profile_url: Optional[str],
    output_dir: str,
    template: Optional[str],
    html_file: Optional[str],
    headless: bool,
    debug: bool,
):
    """Generate a professional PDF CV from a LinkedIn profile.

    PROFILE_URL: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)
                 Not required if --html-file is provided.
    """
    display_banner()

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
        profile_url = console.input("[cyan]Please enter your LinkedIn profile URL: [/cyan]")
        profile_url = profile_url.strip()
        
        if not profile_url:
            console.print("[red]❌ Error: Profile URL cannot be empty[/red]")
            sys.exit(1)

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

        # Step 4: Generate PDF and HTML
        task4 = progress.add_task("📄 Generating PDF and HTML...", total=None)

        generator = PDFGenerator(template_path=template)
        username = profile_data.get("username", "linkedin-profile")
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        output_filename = f"{username}_{timestamp}.pdf"
        output_file = output_path / output_filename

        html_file_path = generator.generate(profile_data, str(output_file))
        html_file = Path(html_file_path)

        progress.update(task4, completed=True)
        console.print("   [green]✓[/green] PDF and HTML generated successfully!")

    # Success message
    console.print()
    console.print(
        Panel(
            f"[bold green]✅ Done![/bold green]\n\n"
            f"Your CV is ready at:\n"
            f"📄 PDF:  [cyan]{output_file}[/cyan]\n"
            f"🌐 HTML: [cyan]{html_file}[/cyan]",
            border_style="green",
            padding=(1, 2),
        )
    )


if __name__ == "__main__":
    main()
