#!/usr/bin/env python3
"""
Simple script to scrape LinkedIn and save HTML for debugging.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper.linkedin_scraper import LinkedInScraper
from src.scraper.parser import ProfileParser
from rich.console import Console

console = Console()

async def scrape_and_save(username: str = "alex-colls-outumuro"):
    """Scrape a LinkedIn profile and save the HTML."""
    
    # Convert username to full URL if needed
    if not username.startswith("http"):
        profile_url = f"https://www.linkedin.com/in/{username}/"
    else:
        profile_url = username
    
    console.print(f"\n[cyan]🔍 Scraping profile: {profile_url}[/cyan]")
    
    try:
        # Initialize scraper with debug mode
        scraper = LinkedInScraper(headless=True, debug=True)
        
        # Scrape the profile
        console.print("[yellow]⏳ Scraping... (this may take 20-30 seconds)[/yellow]")
        html_content = await scraper.scrape_profile(profile_url)
        
        # Save HTML to file
        output_file = "last_scraped.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        console.print(f"[green]✅ HTML saved to {output_file} ({len(html_content):,} bytes)[/green]")
        
        # Quick analysis
        console.print("\n[bold]Quick Analysis:[/bold]")
        console.print(f"  • Contains 'experience': {'experience' in html_content.lower()}")
        console.print(f"  • Contains 'worksFor': {'worksFor' in html_content}")
        console.print(f"  • Contains JSON-LD: {'application/ld+json' in html_content}")
        console.print(f"  • Contains auth wall: {'authwall' in html_content.lower() or 'Join now' in html_content}")
        
        # Test parser
        console.print("\n[bold]Parser Test:[/bold]")
        parser = ProfileParser()
        profile = parser.parse(html_content)
        
        console.print(f"  • Name: {profile.get('name', 'Not found')}")
        console.print(f"  • Headline: {profile.get('headline', 'Not found')}")
        console.print(f"  • Sections found: {len(profile.get('sections', []))}")
        console.print(f"  • Experience items: {len(profile.get('experience', []))}")
        console.print(f"  • Education items: {len(profile.get('education', []))}")
        
        if profile.get('experience'):
            console.print("\n[green]✅ Experience data found![/green]")
            for i, exp in enumerate(profile['experience'][:2], 1):
                console.print(f"\n  Experience {i}:")
                console.print(f"    Title: {exp.get('title', 'N/A')}")
                console.print(f"    Company: {exp.get('company', 'N/A')}")
                console.print(f"    Duration: {exp.get('duration', 'N/A')}")
        else:
            console.print("\n[red]❌ No experience data extracted[/red]")
            console.print("[yellow]This might be due to:[/yellow]")
            console.print("  1. LinkedIn auth wall (profile not publicly visible)")
            console.print("  2. Changes in LinkedIn HTML structure")
            console.print("  3. Profile doesn't have experience section")
            
        return html_content
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function."""
    import argparse
    parser = argparse.ArgumentParser(description='Scrape LinkedIn profile HTML')
    parser.add_argument('username', nargs='?', default='alex-colls-outumuro',
                       help='LinkedIn username or URL (default: alex-colls-outumuro)')
    
    args = parser.parse_args()
    
    # Run the scraper
    result = asyncio.run(scrape_and_save(args.username))
    
    if result:
        console.print("\n[green]✅ Done! Check 'last_scraped.html' for the full HTML[/green]")
        console.print("[yellow]Tip: Open the file in a browser to see what was captured[/yellow]")
    else:
        console.print("\n[red]Failed to scrape profile[/red]")

if __name__ == "__main__":
    main()