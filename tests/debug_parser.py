#!/usr/bin/env python3
"""Debug script to test LinkedIn parser and see what data we're extracting."""

import json
import sys
from pathlib import Path
from src.scraper.parser import ProfileParser
from rich.console import Console
from rich.tree import Tree
from rich import print as rprint

console = Console()

def debug_profile_data(html_file_path: str):
    """Load HTML and parse it to see what data we're getting."""
    
    # Load the HTML file
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        console.print(f"[red]Error loading HTML file: {e}[/red]")
        sys.exit(1)
    
    # Parse the profile
    parser = ProfileParser()
    profile_data = parser.parse(html_content)
    
    # Create a tree view of the data
    tree = Tree("📋 [bold]Profile Data Structure[/bold]")
    
    for key, value in profile_data.items():
        if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
            # Show empty sections in dim
            tree.add(f"[dim]{key}: (empty)[/dim]")
        elif isinstance(value, list):
            branch = tree.add(f"[cyan]{key}[/cyan]: {len(value)} items")
            for i, item in enumerate(value[:3]):  # Show first 3 items
                if isinstance(item, dict):
                    subbranch = branch.add(f"Item {i+1}")
                    for k, v in item.items():
                        if v:
                            subbranch.add(f"{k}: {str(v)[:50]}...")
                else:
                    branch.add(str(item)[:50])
            if len(value) > 3:
                branch.add(f"[dim]... and {len(value) - 3} more items[/dim]")
        elif isinstance(value, dict):
            branch = tree.add(f"[cyan]{key}[/cyan]")
            for k, v in value.items():
                if v:
                    branch.add(f"{k}: {str(v)[:50]}...")
        else:
            # Show string values
            display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            tree.add(f"[green]{key}[/green]: {display_value}")
    
    console.print(tree)
    
    # Show summary
    console.print("\n[bold]📊 Summary:[/bold]")
    console.print(f"  • Name: {profile_data.get('name', 'Not found')}")
    console.print(f"  • Headline: {profile_data.get('headline', 'Not found')}")
    console.print(f"  • Location: {profile_data.get('location', 'Not found')}")
    console.print(f"  • About: {'Yes' if profile_data.get('about') else 'No'}")
    console.print(f"  • Experience: {len(profile_data.get('experience', []))} positions")
    console.print(f"  • Education: {len(profile_data.get('education', []))} entries")
    console.print(f"  • Skills: {len(profile_data.get('skills', []))} skills")
    console.print(f"  • Certifications: {len(profile_data.get('certifications', []))} certs")
    
    # Save detailed output to JSON for inspection
    output_file = Path(html_file_path).with_suffix('.debug.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[dim]Full data saved to: {output_file}[/dim]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]Usage: python debug_parser.py <html_file>[/red]")
        sys.exit(1)
    
    html_file = sys.argv[1]
    if not Path(html_file).exists():
        console.print(f"[red]File not found: {html_file}[/red]")
        sys.exit(1)
    
    debug_profile_data(html_file)