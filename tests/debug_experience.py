#!/usr/bin/env python3
"""
Debug tool for analyzing LinkedIn experience section extraction.
This tool helps identify why experience data might not be extracting correctly.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from bs4 import BeautifulSoup
import json
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

console = Console()

def analyze_experience_structure(html_content: str):
    """Analyze the structure of experience section in LinkedIn HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    console.print("\n[bold cyan]🔍 Analyzing LinkedIn Experience Section Structure[/bold cyan]\n")
    
    # Check for JSON-LD data first
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    if json_ld_scripts:
        console.print(f"[green]✅ Found {len(json_ld_scripts)} JSON-LD scripts[/green]")
        for i, script in enumerate(json_ld_scripts[:2]):  # Limit to first 2
            try:
                data = json.loads(script.string)
                if '@graph' in data:
                    for item in data['@graph']:
                        if 'worksFor' in item or '@type' in item:
                            console.print(f"\n[yellow]JSON-LD Item {i+1}:[/yellow]")
                            console.print(f"Type: {item.get('@type', 'Unknown')}")
                            if 'worksFor' in item:
                                console.print(f"WorksFor entries: {len(item['worksFor'])}")
                                for j, work in enumerate(item['worksFor'][:3]):  # Show first 3
                                    console.print(f"  Work {j+1}: {work.get('name', 'Unknown')}")
            except json.JSONDecodeError:
                pass
    
    # Look for experience sections with various selectors
    experience_section_patterns = [
        ('section#experience', 'Modern ID selector'),
        ('section[id*="experience"]', 'Partial ID match'),
        ('section[data-section="experience"]', 'Data attribute selector'),
        ('div#experience-section', 'Legacy div selector'),
        ('section.pv-profile-section.experience-section', 'Legacy class selector'),
        ('section.artdeco-card[id*="experience"]', 'Artdeco card pattern'),
        ('div.pvs-list__container', 'PVS list container'),
        ('section[aria-labelledby*="experience"]', 'ARIA label pattern'),
    ]
    
    console.print("\n[bold]Experience Section Detection:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Selector", style="cyan")
    table.add_column("Description", style="yellow")
    table.add_column("Found", style="green")
    table.add_column("Items", style="white")
    
    experience_section = None
    for selector, description in experience_section_patterns:
        element = soup.select_one(selector)
        if element:
            # Count potential experience items within
            items = element.select('li, div[class*="entity"], div[class*="position"]')
            table.add_row(selector, description, "✓", str(len(items)))
            if not experience_section:
                experience_section = element
        else:
            table.add_row(selector, description, "✗", "0")
    
    console.print(table)
    
    # If we found an experience section, analyze its structure
    if experience_section:
        console.print("\n[bold]Experience Items Structure:[/bold]")
        analyze_experience_items(experience_section)
    else:
        console.print("\n[red]⚠️ No experience section found with standard selectors[/red]")
        
        # Try broader search
        console.print("\n[yellow]Attempting broader search for experience-like content...[/yellow]")
        search_for_experience_content(soup)
    
    return soup

def analyze_experience_items(section):
    """Analyze individual experience items within the section."""
    
    # Try different item selectors
    item_patterns = [
        'li.pvs-list__paged-list-item',
        'li.artdeco-list__item',
        'div.pv-entity__position-group-pager',
        'div[class*="experience-item"]',
        'div[class*="position"]',
        'li[class*="profile"]',
    ]
    
    items = []
    used_selector = None
    for selector in item_patterns:
        found = section.select(selector)
        if found and len(found) > len(items):
            items = found
            used_selector = selector
    
    if items:
        console.print(f"[green]Found {len(items)} experience items using: {used_selector}[/green]\n")
        
        # Analyze first item in detail
        if items:
            console.print("[bold]Detailed analysis of first experience item:[/bold]\n")
            analyze_single_experience(items[0])
    else:
        console.print("[red]No experience items found with standard patterns[/red]")
        
        # Show raw HTML structure
        console.print("\n[yellow]Raw section HTML preview (first 500 chars):[/yellow]")
        html_preview = str(section)[:500]
        console.print(Panel(html_preview, title="HTML Structure"))

def analyze_single_experience(item):
    """Analyze a single experience item in detail."""
    
    # Define extraction patterns
    patterns = {
        'Title': [
            'div.display-flex.align-items-center span[aria-hidden="true"]',
            'div.t-bold span[aria-hidden="true"]',
            'h3 span[aria-hidden="true"]',
            'div.mr1.t-bold span',
            'span.mr1.t-bold',
            'div[class*="title"] span',
        ],
        'Company': [
            'span.t-14.t-normal span[aria-hidden="true"]',
            'div.pv-entity__secondary-title',
            'span.pv-entity__secondary-title',
            'div[class*="company"]',
            'a[data-control-name*="company"]',
        ],
        'Duration': [
            'span.t-14.t-normal.t-black--light span[aria-hidden="true"]',
            'span.pv-entity__date-range span',
            'span[class*="date-range"]',
        ],
        'Location': [
            'span.t-14.t-normal.t-black--light',
            'span.pv-entity__location span',
            'div[class*="location"]',
        ],
        'Description': [
            'div.pv-shared-text-with-see-more span[aria-hidden="true"]',
            'div.inline-show-more-text span[aria-hidden="true"]',
            'div[class*="description"]',
            'div.pv-entity__description',
        ],
    }
    
    results = {}
    for field, selectors in patterns.items():
        for selector in selectors:
            try:
                element = item.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 0:
                        results[field] = text[:100]  # Limit to 100 chars for display
                        break
            except Exception as e:
                pass
    
    # Display results
    if results:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Field", style="yellow")
        table.add_column("Extracted Value", style="white")
        
        for field, value in results.items():
            table.add_row(field, value)
        
        console.print(table)
    else:
        console.print("[red]Could not extract any fields from this item[/red]")
    
    # Show the raw text content
    console.print("\n[bold]Raw text content:[/bold]")
    text_content = item.get_text(separator=' | ', strip=True)[:300]
    console.print(Panel(text_content, title="Item Text"))
    
    # Show classes and structure
    console.print("\n[bold]Item HTML attributes:[/bold]")
    console.print(f"Tag: {item.name}")
    if item.get('class'):
        console.print(f"Classes: {' '.join(item['class'])}")
    if item.get('id'):
        console.print(f"ID: {item['id']}")

def search_for_experience_content(soup):
    """Search for experience content using text patterns."""
    
    # Search for common experience-related terms
    experience_keywords = ['experience', 'work history', 'employment', 'positions']
    
    for keyword in experience_keywords:
        # Case-insensitive search
        elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
        if elements:
            console.print(f"\n[yellow]Found '{keyword}' in {len(elements)} places[/yellow]")
            
            # Check parent elements
            for elem in elements[:3]:  # Check first 3 occurrences
                parent = elem.parent
                if parent:
                    # Look for nearby list items or divs that might contain experience
                    siblings = parent.find_next_siblings(['li', 'div'], limit=5)
                    if siblings:
                        console.print(f"  Potential experience content near '{elem[:50]}...'")
    
    # Look for date patterns that might indicate experience
    date_pattern = re.compile(r'\b(19|20)\d{2}\b.*\b(Present|19|20)\d{2}\b')
    date_elements = soup.find_all(text=date_pattern)
    if date_elements:
        console.print(f"\n[yellow]Found {len(date_elements)} date patterns that might indicate experience[/yellow]")
        for elem in date_elements[:3]:
            console.print(f"  Date pattern: {elem.strip()[:50]}...")

def test_with_mock_profile():
    """Test with the mock LinkedIn profile if it exists."""
    mock_file = Path('test_data/mock_linkedin_profile.html')
    if mock_file.exists():
        console.print("\n[bold green]Testing with mock profile...[/bold green]")
        with open(mock_file, 'r', encoding='utf-8') as f:
            return analyze_experience_structure(f.read())
    else:
        console.print("[yellow]Mock profile not found[/yellow]")
        return None

def test_with_saved_profile(profile_path: str):
    """Test with a saved LinkedIn HTML file."""
    path = Path(profile_path)
    if path.exists():
        console.print(f"\n[bold green]Testing with saved profile: {profile_path}[/bold green]")
        with open(path, 'r', encoding='utf-8') as f:
            return analyze_experience_structure(f.read())
    else:
        console.print(f"[red]File not found: {profile_path}[/red]")
        return None

def extract_and_display_experience(soup):
    """Extract experience using the current parser logic and display results."""
    from src.scraper.parser import LinkedInParser
    
    parser = LinkedInParser()
    profile_data = parser.parse(str(soup))
    
    console.print("\n[bold cyan]Extracted Profile Data:[/bold cyan]")
    
    # Display basic info
    console.print(f"\nName: {profile_data.get('name', 'Not found')}")
    console.print(f"Headline: {profile_data.get('headline', 'Not found')}")
    console.print(f"Location: {profile_data.get('location', 'Not found')}")
    
    # Display experience
    experience = profile_data.get('experience', [])
    console.print(f"\n[bold]Experience items found: {len(experience)}[/bold]")
    
    if experience:
        for i, exp in enumerate(experience, 1):
            console.print(f"\n[yellow]Experience {i}:[/yellow]")
            table = Table(show_header=False)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")
            
            for key, value in exp.items():
                if value:
                    if isinstance(value, list):
                        value = ', '.join(value)
                    elif isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    table.add_row(key.capitalize(), str(value))
            
            console.print(table)
    else:
        console.print("[red]No experience data extracted[/red]")
    
    return profile_data

def main():
    """Main function to run the debugging tool."""
    console.print(Panel.fit(
        "[bold cyan]LinkedIn Experience Extraction Debugger[/bold cyan]\n"
        "This tool helps identify issues with experience section extraction",
        border_style="cyan"
    ))
    
    import argparse
    parser = argparse.ArgumentParser(description='Debug LinkedIn experience extraction')
    parser.add_argument('--file', help='Path to saved LinkedIn HTML file')
    parser.add_argument('--mock', action='store_true', help='Use mock profile for testing')
    parser.add_argument('--extract', action='store_true', help='Also run the parser extraction')
    
    args = parser.parse_args()
    
    soup = None
    
    if args.mock:
        soup = test_with_mock_profile()
    elif args.file:
        soup = test_with_saved_profile(args.file)
    else:
        # Try to find any saved HTML files
        import glob
        html_files = glob.glob('*.html') + glob.glob('data/*.html') + glob.glob('test_data/*.html')
        
        if html_files:
            console.print("\n[yellow]Found HTML files:[/yellow]")
            for i, file in enumerate(html_files):
                console.print(f"  {i+1}. {file}")
            
            choice = console.input("\nSelect a file number (or press Enter to skip): ")
            if choice.isdigit() and 1 <= int(choice) <= len(html_files):
                soup = test_with_saved_profile(html_files[int(choice)-1])
        else:
            console.print("[red]No HTML files found. Please provide a file path with --file[/red]")
    
    if soup and args.extract:
        extract_and_display_experience(soup)
    
    console.print("\n[green]Debug analysis complete![/green]")

if __name__ == "__main__":
    main()