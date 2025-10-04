"""Command-line interface for LinkedIn CV Generator."""
import asyncio
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
@click.argument("profile_url", type=str)
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
    profile_url: str,
    output_dir: str,
    template: Optional[str],
    headless: bool,
    debug: bool,
):
    """Generate a professional PDF CV from a LinkedIn profile.

    PROFILE_URL: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)
    """
    display_banner()

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        # Run the async workflow
        asyncio.run(generate_cv(profile_url, output_path, template, headless, debug))
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")
        if debug:
            console.print_exception()
        sys.exit(1)


async def generate_cv(
    profile_url: str,
    output_path: Path,
    template: Optional[str],
    headless: bool,
    debug: bool,
):
    """Main workflow to generate CV from LinkedIn profile."""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Step 1: Scrape LinkedIn profile
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
        task4 = progress.add_task("📄 Generating PDF...", total=None)

        generator = PDFGenerator(template_path=template)
        username = profile_data.get("username", "linkedin-profile")
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        output_filename = f"{username}_{timestamp}.pdf"
        output_file = output_path / output_filename

        generator.generate(profile_data, str(output_file))

        progress.update(task4, completed=True)
        console.print("   [green]✓[/green] PDF generated successfully!")

    # Success message
    console.print()
    console.print(
        Panel(
            f"[bold green]✅ Done![/bold green]\n\n"
            f"Your CV is ready at:\n[cyan]{output_file}[/cyan]",
            border_style="green",
            padding=(1, 2),
        )
    )


if __name__ == "__main__":
    main()
