#!/usr/bin/env python3
"""
Analyze the actual HTML being scraped to understand why experience isn't extracted.
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json

console = Console()

def analyze_scraped_html():
    """Analyze the HTML that was scraped by the CLI tool."""
    
    # The CLI saves the HTML temporarily, let's find it
    import os
    import tempfile
    import time
    from src.cli import LinkedInCVGeneratorCLI
    from src.scraper.parser import ProfileParser
    
    # Create a test run
    console.print("[yellow]Running the CLI to capture HTML...[/yellow]")
    
    # Override the CLI to save HTML for analysis
    import src.cli
    
    original_run = src.cli.LinkedInCVGeneratorCLI.run
    captured_html = None
    
    def capture_run(self):
        nonlocal captured_html
        
        # Get the original scrape method
        original_scrape = self.scraper.scrape_profile
        
        async def capture_scrape(url):
            html = await original_scrape(url)
            captured_html = html
            
            # Save to file for analysis
            with open('last_scraped.html', 'w', encoding='utf-8') as f:
                f.write(html)
            
            return html
        
        # Replace scrape method temporarily
        self.scraper.scrape_profile = capture_scrape
        
        # Run original
        return original_run(self)
    
    # Monkey patch temporarily
    src.cli.LinkedInCVGeneratorCLI.run = capture_run
    
    # Let's just analyze the most recent HTML if it exists
    if Path('last_scraped.html').exists():
        console.print("[green]Found previously scraped HTML, analyzing...[/green]")
        with open('last_scraped.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    else:
        console.print("[red]No scraped HTML found. Please run the CLI first to generate a CV.[/red]")
        console.print("[yellow]The HTML will be saved as 'last_scraped.html' for analysis.[/yellow]")
        return
    
    analyze_html_content(html_content)

def analyze_html_content(html_content):
    """Analyze HTML content in detail."""
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    console.print("\n" + "="*60)
    console.print("[bold cyan]LinkedIn HTML Analysis[/bold cyan]")
    console.print("="*60 + "\n")
    
    # Basic info
    console.print(f"[bold]HTML Size:[/bold] {len(html_content):,} characters")
    
    # Check if it's a full page or limited
    is_full = 'experience' in html_content.lower()
    console.print(f"[bold]Contains 'experience' keyword:[/bold] {is_full}")
    
    # Check for authentication issues
    if 'Sign in' in html_content or 'Join now' in html_content:
        console.print("[red]⚠️ Page appears to be login-gated![/red]")
    
    # Check for JSON-LD
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    console.print(f"\n[bold]JSON-LD Scripts:[/bold] {len(json_ld_scripts)} found")
    
    if json_ld_scripts:
        for i, script in enumerate(json_ld_scripts[:2]):
            try:
                data = json.loads(script.string)
                if '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') == 'Person':
                            console.print(f"  ✓ Person data found")
                            if 'worksFor' in item:
                                console.print(f"    - worksFor: {len(item['worksFor'])} entries")
                            if 'alumniOf' in item:
                                console.print(f"    - alumniOf: {len(item['alumniOf'])} entries")
            except:
                pass
    
    # Look for experience section
    console.print("\n[bold]Experience Section Search:[/bold]")
    
    experience_selectors = [
        ('section#experience', 'ID selector'),
        ('section[id*="experience"]', 'Partial ID'),
        ('section[data-section="experience"]', 'Data attribute'),
        ('div#experience-section', 'Legacy div'),
        ('section.experience-section', 'Class selector'),
        ('section[aria-label*="Experience"]', 'ARIA label'),
        ('div[data-view-name="profile-card"][href*="/details/experience/"]', 'Modern card'),
    ]
    
    table = Table(show_header=True)
    table.add_column("Selector", style="cyan")
    table.add_column("Type", style="yellow") 
    table.add_column("Found", style="green")
    
    for selector, desc in experience_selectors:
        found = soup.select_one(selector) is not None
        table.add_row(selector, desc, "✓" if found else "✗")
    
    console.print(table)
    
    # Look for experience-like patterns in text
    console.print("\n[bold]Experience Patterns in Text:[/bold]")
    
    # Search for date patterns that might indicate experience
    import re
    date_pattern = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[-–]\s*(Present|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec\s+\d{4})')
    dates_found = date_pattern.findall(html_content)
    
    if dates_found:
        console.print(f"  Found {len(dates_found)} date ranges that look like job dates")
        for date in dates_found[:3]:
            console.print(f"    • {date[0]} - {date[1]}")
    
    # Check for common job titles
    job_titles = ['Engineer', 'Developer', 'Manager', 'Designer', 'Analyst', 'Consultant']
    for title in job_titles:
        if title in html_content:
            console.print(f"  Found job title keyword: {title}")
    
    # Look for experience list items
    console.print("\n[bold]Experience List Items:[/bold]")
    
    item_selectors = [
        'li.pvs-list__paged-list-item',
        'li.artdeco-list__item',
        'li[class*="experience"]',
        'div.pv-entity__position-group-pager',
    ]
    
    for selector in item_selectors:
        items = soup.select(selector)
        if items:
            console.print(f"  {selector}: {len(items)} items found")
            
            # Analyze first item
            if items:
                first_item = items[0]
                text = first_item.get_text(strip=True)[:200]
                console.print(f"    First item preview: {text}...")
    
    # Test the parser
    console.print("\n[bold]Parser Test:[/bold]")
    parser = ProfileParser()
    profile = parser.parse(html_content)
    
    console.print(f"  Sections parsed: {len(profile.get('sections', []))}")
    console.print(f"  Experience items: {len(profile.get('experience', []))}")
    console.print(f"  Education items: {len(profile.get('education', []))}")
    
    if profile.get('experience'):
        console.print("\n[green]✅ Experience was extracted![/green]")
        for i, exp in enumerate(profile['experience'][:2], 1):
            console.print(f"\n  Experience {i}:")
            for key, value in exp.items():
                if value:
                    console.print(f"    {key}: {str(value)[:50]}...")
    else:
        console.print("\n[red]❌ No experience extracted[/red]")
        
        # Show what was extracted
        console.print("\n[yellow]Data that WAS extracted:[/yellow]")
        for key, value in profile.items():
            if value and key not in ['sections', 'username']:
                if isinstance(value, str):
                    console.print(f"  {key}: {value[:50]}...")
                elif isinstance(value, list) and len(value) > 0:
                    console.print(f"  {key}: {len(value)} items")
                elif isinstance(value, dict) and len(value) > 0:
                    console.print(f"  {key}: {len(value)} fields")
    
    # Save analysis results
    with open('html_analysis.txt', 'w') as f:
        f.write("HTML Structure Analysis\n")
        f.write("="*50 + "\n\n")
        f.write(f"HTML Size: {len(html_content):,} chars\n")
        f.write(f"Has experience keyword: {is_full}\n")
        f.write(f"JSON-LD scripts: {len(json_ld_scripts)}\n")
        f.write(f"Experience extracted: {len(profile.get('experience', []))} items\n")
        f.write("\nFull profile sections found:\n")
        for section in profile.get('sections', []):
            f.write(f"  - {section}\n")
    
    console.print("\n[green]Analysis complete! Results saved to html_analysis.txt[/green]")

if __name__ == "__main__":
    analyze_scraped_html()