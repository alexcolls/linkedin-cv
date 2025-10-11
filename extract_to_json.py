#!/usr/bin/env python3
"""
Extract LinkedIn profile data to JSON format for review and debugging.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper.linkedin_scraper import LinkedInScraper
from src.scraper.parser import ProfileParser

console = Console()


def normalize_profile_url(input_str: str) -> str:
    """Normalize profile input to full LinkedIn URL."""
    input_str = input_str.strip().rstrip('/')
    
    if input_str.startswith('http://') or input_str.startswith('https://'):
        return input_str
    
    if 'linkedin.com' in input_str:
        if not input_str.startswith('http'):
            return f'https://{input_str}'
        return input_str
    
    username = input_str.replace('@', '').strip()
    return f'https://www.linkedin.com/in/{username}/'


async def extract_profile_data(profile_url: str, save_html: bool = False) -> dict:
    """Extract all profile data from LinkedIn."""
    
    console.print(f"\n[cyan]🔍 Extracting data from: {profile_url}[/cyan]")
    
    try:
        # Initialize scraper
        scraper = LinkedInScraper(headless=True, debug=True)
        
        # Scrape the profile
        with console.status("[yellow]Scraping LinkedIn profile...[/yellow]"):
            html_content = await scraper.scrape_profile(profile_url)
        
        # Save HTML if requested
        if save_html:
            html_file = f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            console.print(f"[dim]HTML saved to: {html_file}[/dim]")
        
        # Parse the profile
        parser = ProfileParser()
        profile_data = parser.parse(html_content)
        
        # Add metadata
        profile_data['_metadata'] = {
            'extracted_at': datetime.now().isoformat(),
            'profile_url': profile_url,
            'html_length': len(html_content),
            'sections_found': len(profile_data.get('sections', [])),
        }
        
        return profile_data
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return None


def display_profile_summary(profile_data: dict):
    """Display a summary of extracted profile data."""
    
    console.print("\n[bold cyan]📊 Profile Data Summary[/bold cyan]\n")
    
    # Basic info
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Preview", style="yellow")
    
    fields = [
        ('name', 'Name'),
        ('headline', 'Headline'),
        ('location', 'Location'),
        ('about', 'About'),
        ('profile_picture_url', 'Profile Picture'),
    ]
    
    for field, label in fields:
        value = profile_data.get(field)
        status = "✅" if value else "❌"
        preview = ""
        if value:
            if isinstance(value, str):
                preview = value[:50] + "..." if len(value) > 50 else value
            else:
                preview = str(value)[:50]
        table.add_row(label, status, preview)
    
    console.print(table)
    
    # Sections summary
    console.print("\n[bold]Sections Found:[/bold]")
    sections_table = Table(show_header=True, header_style="bold magenta")
    sections_table.add_column("Section", style="cyan")
    sections_table.add_column("Count", style="green")
    sections_table.add_column("Details", style="yellow")
    
    sections_info = [
        ('experience', 'Experience'),
        ('education', 'Education'),
        ('skills', 'Skills'),
        ('certifications', 'Certifications'),
        ('languages', 'Languages'),
        ('volunteer', 'Volunteer'),
        ('projects', 'Projects'),
        ('publications', 'Publications'),
        ('honors', 'Honors'),
        ('courses', 'Courses'),
    ]
    
    for field, label in sections_info:
        section_data = profile_data.get(field, [])
        if isinstance(section_data, list):
            count = len(section_data)
            status = f"{count} items"
            if count > 0:
                # Show first item preview
                first_item = section_data[0]
                if isinstance(first_item, dict):
                    # For experience, show title and company
                    if field == 'experience':
                        details = f"{first_item.get('title', 'N/A')} at {first_item.get('company', 'N/A')}"
                    elif field == 'education':
                        details = f"{first_item.get('institution', 'N/A')}"
                    elif field == 'skills':
                        if isinstance(first_item, str):
                            details = first_item
                        else:
                            details = first_item.get('name', 'N/A')
                    else:
                        details = str(first_item)[:30]
                else:
                    details = str(first_item)[:30]
                details = details[:50] + "..." if len(details) > 50 else details
            else:
                details = ""
        else:
            count = 0
            status = "No data"
            details = ""
    
        sections_table.add_row(label, status, details)
    
    console.print(sections_table)
    
    # Missing data warnings
    missing = []
    critical_fields = ['name', 'experience', 'education']
    for field in critical_fields:
        data = profile_data.get(field)
        if not data or (isinstance(data, list) and len(data) == 0):
            missing.append(field)
    
    if missing:
        console.print(f"\n[yellow]⚠️  Missing critical data: {', '.join(missing)}[/yellow]")
        console.print("[dim]This might be due to LinkedIn authentication requirements[/dim]")


@click.command()
@click.argument('profile', required=False)
@click.option('--output', '-o', default='profile_data.json', help='Output JSON file name')
@click.option('--pretty', is_flag=True, help='Pretty print JSON')
@click.option('--save-html', is_flag=True, help='Also save the raw HTML')
@click.option('--show-json', is_flag=True, help='Display JSON in terminal')
def main(profile: Optional[str], output: str, pretty: bool, save_html: bool, show_json: bool):
    """Extract LinkedIn profile data to JSON format."""
    
    console.print(Panel.fit(
        "[bold cyan]LinkedIn Profile Data Extractor[/bold cyan]\n"
        "Extract complete profile data to JSON for analysis",
        border_style="cyan"
    ))
    
    # Get profile URL
    if not profile:
        console.print("\n[yellow]No profile URL provided[/yellow]")
        profile = console.input("[cyan]Enter LinkedIn profile URL or username: [/cyan]")
        if not profile:
            console.print("[red]No profile provided, exiting[/red]")
            sys.exit(1)
    
    profile_url = normalize_profile_url(profile)
    console.print(f"[dim]Using profile: {profile_url}[/dim]")
    
    # Extract data
    profile_data = asyncio.run(extract_profile_data(profile_url, save_html))
    
    if not profile_data:
        console.print("[red]Failed to extract profile data[/red]")
        sys.exit(1)
    
    # Display summary
    display_profile_summary(profile_data)
    
    # Save to JSON
    output_path = Path(output)
    with open(output_path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(profile_data, f, ensure_ascii=False)
    
    console.print(f"\n[green]✅ Profile data saved to: {output_path}[/green]")
    console.print(f"[dim]File size: {output_path.stat().st_size:,} bytes[/dim]")
    
    # Display JSON if requested
    if show_json:
        console.print("\n[bold]JSON Data:[/bold]")
        json_str = json.dumps(profile_data, indent=2, ensure_ascii=False)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(syntax)
    
    # Check for missing data
    console.print("\n[bold]Data Completeness Check:[/bold]")
    total_fields = len(profile_data.keys())
    filled_fields = sum(1 for v in profile_data.values() if v and (not isinstance(v, list) or len(v) > 0))
    completeness = (filled_fields / total_fields) * 100 if total_fields > 0 else 0
    
    console.print(f"Completeness: {completeness:.1f}% ({filled_fields}/{total_fields} fields)")
    
    if completeness < 50:
        console.print("\n[yellow]⚠️  Low data completeness detected![/yellow]")
        console.print("Possible reasons:")
        console.print("  1. LinkedIn requires authentication to view full profile")
        console.print("  2. Profile privacy settings restrict public access")
        console.print("  3. Profile has limited information")
        console.print("\nTo get more data:")
        console.print("  • Run './run.sh' and select option 2 to login to LinkedIn")
        console.print("  • Save your LinkedIn session for authenticated scraping")


if __name__ == "__main__":
    main()