#!/usr/bin/env python3
"""Capture LinkedIn HTML for parser development and testing."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import argparse
from rich.console import Console
from src.scraper.linkedin_scraper import LinkedInScraper

console = Console()

async def capture_html(profile_url: str, output_dir: str = "test_data", headless: bool = True):
    """Capture HTML from a LinkedIn profile and save it for analysis.
    
    Args:
        profile_url: LinkedIn profile URL
        output_dir: Directory to save HTML files
        headless: Whether to run browser in headless mode
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[cyan]🔍 Capturing HTML from: {profile_url}[/cyan]")
    
    try:
        # Initialize scraper
        scraper = LinkedInScraper(headless=headless, debug=True)
        
        # Scrape profile
        console.print("[yellow]⏳ Scraping profile (this may take a moment)...[/yellow]")
        html_content = await scraper.scrape_profile(profile_url)
        
        if html_content:
            # Extract username from URL for filename
            username = profile_url.rstrip('/').split('/')[-1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save full HTML
            html_file = output_path / f"{username}_{timestamp}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            console.print(f"[green]✅ HTML saved to: {html_file}[/green]")
            
            # Also save a prettified version for easier reading
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            pretty_file = output_path / f"{username}_{timestamp}_pretty.html"
            with open(pretty_file, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
            console.print(f"[green]✅ Prettified HTML saved to: {pretty_file}[/green]")
            
            # Extract and save key sections for analysis
            analyze_html_structure(soup, output_path / f"{username}_{timestamp}_analysis.txt")
            
            return html_file
        else:
            console.print("[red]❌ Failed to capture HTML content[/red]")
            return None
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return None

def analyze_html_structure(soup, output_file):
    """Analyze HTML structure and save findings."""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("LinkedIn HTML Structure Analysis\n")
        f.write("=" * 50 + "\n\n")
        
        # Look for main profile sections
        f.write("MAIN SECTIONS FOUND:\n")
        f.write("-" * 30 + "\n")
        
        # Check for various section patterns
        section_patterns = [
            ('section', {'id': lambda x: x and 'experience' in x.lower()}),
            ('section', {'id': lambda x: x and 'education' in x.lower()}),
            ('section', {'id': lambda x: x and 'skills' in x.lower()}),
            ('section', {'id': lambda x: x and 'certifications' in x.lower()}),
            ('section', {'id': lambda x: x and 'projects' in x.lower()}),
            ('div', {'class': lambda x: x and 'experience' in str(x).lower()}),
            ('div', {'class': lambda x: x and 'education' in str(x).lower()}),
            ('div', {'class': lambda x: x and 'skills' in str(x).lower()}),
        ]
        
        for tag, attrs in section_patterns:
            elements = soup.find_all(tag, attrs)
            if elements:
                f.write(f"\nFound {len(elements)} {tag} elements matching {attrs}:\n")
                for elem in elements[:2]:  # Show first 2
                    f.write(f"  - {elem.name}")
                    if elem.get('id'):
                        f.write(f" id='{elem.get('id')}'")
                    if elem.get('class'):
                        f.write(f" class='{' '.join(elem.get('class', []))}'")
                    f.write("\n")
        
        f.write("\n\nKEY CSS CLASSES FOUND:\n")
        f.write("-" * 30 + "\n")
        
        # Find common class patterns
        all_classes = set()
        for elem in soup.find_all(class_=True):
            classes = elem.get('class', [])
            all_classes.update(classes)
        
        # Filter for interesting classes
        interesting_patterns = [
            'profile', 'experience', 'education', 'skill', 'certification',
            'pvs-', 'pv-', 'artdeco-', 't-', 'display-flex', 'entity'
        ]
        
        interesting_classes = []
        for cls in all_classes:
            if any(pattern in cls.lower() for pattern in interesting_patterns):
                interesting_classes.append(cls)
        
        # Sort and display
        for cls in sorted(interesting_classes)[:50]:  # Show first 50
            f.write(f"  .{cls}\n")
        
        f.write("\n\nSAMPLE SELECTORS TO TEST:\n")
        f.write("-" * 30 + "\n")
        
        # Test current selectors and suggest alternatives
        test_selectors = [
            "h1",  # Name
            "div.text-body-medium",  # Headline
            "section[id*='experience']",
            "section[id*='education']",
            "li.pvs-list__paged-list-item",
            "li.artdeco-list__item",
            "div[class*='entity']",
            "span[aria-hidden='true']",
        ]
        
        for selector in test_selectors:
            elements = soup.select(selector)
            f.write(f"\n'{selector}': {len(elements)} matches\n")
            if elements and len(elements) <= 3:
                for elem in elements:
                    text = elem.get_text(strip=True)[:100]
                    if text:
                        f.write(f"  → {text}...\n")
        
        f.write("\n\nJSON-LD DATA:\n")
        f.write("-" * 30 + "\n")
        
        # Check for JSON-LD
        json_ld = soup.find_all('script', type='application/ld+json')
        if json_ld:
            f.write(f"Found {len(json_ld)} JSON-LD script tags\n")
            for i, script in enumerate(json_ld):
                f.write(f"  Script {i+1}: {len(script.string) if script.string else 0} chars\n")
        else:
            f.write("No JSON-LD data found\n")
    
    console.print(f"[green]✅ Analysis saved to: {output_file}[/green]")

async def main():
    parser = argparse.ArgumentParser(description='Capture LinkedIn HTML for development')
    parser.add_argument('url', help='LinkedIn profile URL')
    parser.add_argument('--output-dir', default='test_data', help='Output directory (default: test_data)')
    parser.add_argument('--visible', action='store_true', help='Show browser window')
    
    args = parser.parse_args()
    
    await capture_html(args.url, args.output_dir, not args.visible)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(0)