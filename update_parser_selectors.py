#!/usr/bin/env python3
"""Analyze LinkedIn HTML and suggest updated selectors for the parser."""

import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from collections import Counter

console = Console()

class SelectorAnalyzer:
    """Analyze LinkedIn HTML to find working selectors."""
    
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.findings = {}
    
    def analyze_all(self):
        """Run all analysis methods."""
        console.print("\n[bold cyan]🔍 Analyzing LinkedIn HTML Structure[/bold cyan]\n")
        
        self.analyze_profile_header()
        self.analyze_experience_section()
        self.analyze_education_section()
        self.analyze_skills_section()
        self.analyze_certifications_section()
        self.analyze_json_ld()
        self.generate_selector_recommendations()
        
        return self.findings
    
    def analyze_profile_header(self):
        """Find selectors for name, headline, location, about."""
        console.print("[yellow]▶ Analyzing Profile Header...[/yellow]")
        
        header_findings = {}
        
        # Find name - usually in h1
        h1_elements = self.soup.find_all('h1')
        for h1 in h1_elements:
            text = h1.get_text(strip=True)
            if text and len(text) < 100 and not any(x in text.lower() for x in ['sign', 'join', 'linkedin']):
                header_findings['name'] = {
                    'text': text,
                    'selector': self._get_selector(h1)
                }
                break
        
        # Find headline - usually near name
        headline_patterns = [
            'div.text-body-medium',
            'div[class*="headline"]',
            'h2.mt1',
            'div.pv-text-details__left-panel div.text-body-medium'
        ]
        
        for pattern in headline_patterns:
            elements = self.soup.select(pattern)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and 10 < len(text) < 200:
                    header_findings['headline'] = {
                        'text': text[:100],
                        'selector': pattern
                    }
                    break
            if 'headline' in header_findings:
                break
        
        # Find location
        location_patterns = [
            'span.text-body-small',
            'span[class*="location"]',
            'div[class*="location"]'
        ]
        
        for pattern in location_patterns:
            elements = self.soup.select(pattern)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and ',' in text and len(text) < 100:
                    header_findings['location'] = {
                        'text': text,
                        'selector': pattern
                    }
                    break
            if 'location' in header_findings:
                break
        
        # Find about section
        about_section = None
        for section in self.soup.find_all('section'):
            if 'about' in str(section.get('id', '')).lower():
                about_section = section
                break
        
        if about_section:
            # Look for text within about section
            for elem in about_section.find_all(['div', 'span']):
                text = elem.get_text(strip=True)
                if text and len(text) > 100:
                    header_findings['about'] = {
                        'text': text[:200] + '...',
                        'selector': f'section[id*="about"] {self._get_tag_class(elem)}'
                    }
                    break
        
        self.findings['header'] = header_findings
        self._print_findings_table('Profile Header', header_findings)
    
    def analyze_experience_section(self):
        """Find selectors for experience section."""
        console.print("\n[yellow]▶ Analyzing Experience Section...[/yellow]")
        
        exp_findings = {}
        
        # Find experience section
        exp_section = None
        for section in self.soup.find_all('section'):
            section_id = section.get('id', '')
            if 'experience' in section_id.lower():
                exp_section = section
                exp_findings['section_selector'] = f'section#{section_id}'
                break
        
        if not exp_section:
            # Try alternative patterns
            for div in self.soup.find_all('div'):
                if 'experience' in str(div.get('class', [])).lower():
                    exp_section = div
                    exp_findings['section_selector'] = self._get_selector(div)
                    break
        
        if exp_section:
            # Find list items within experience
            list_items = exp_section.find_all('li')
            if list_items:
                exp_findings['item_count'] = len(list_items)
                exp_findings['item_selector'] = self._get_selector(list_items[0])
                
                # Analyze first item structure
                first_item = list_items[0]
                
                # Find job title
                for elem in first_item.find_all(['span', 'div', 'h3']):
                    text = elem.get_text(strip=True)
                    if text and 5 < len(text) < 100:
                        exp_findings['title_example'] = text[:50]
                        break
        
        self.findings['experience'] = exp_findings
        self._print_findings_table('Experience', exp_findings)
    
    def analyze_education_section(self):
        """Find selectors for education section."""
        console.print("\n[yellow]▶ Analyzing Education Section...[/yellow]")
        
        edu_findings = {}
        
        # Find education section
        edu_section = None
        for section in self.soup.find_all('section'):
            section_id = section.get('id', '')
            if 'education' in section_id.lower():
                edu_section = section
                edu_findings['section_selector'] = f'section#{section_id}'
                break
        
        if edu_section:
            list_items = edu_section.find_all('li')
            if list_items:
                edu_findings['item_count'] = len(list_items)
                edu_findings['item_selector'] = self._get_selector(list_items[0])
        
        self.findings['education'] = edu_findings
        self._print_findings_table('Education', edu_findings)
    
    def analyze_skills_section(self):
        """Find selectors for skills section."""
        console.print("\n[yellow]▶ Analyzing Skills Section...[/yellow]")
        
        skills_findings = {}
        
        # Find skills section
        skills_section = None
        for section in self.soup.find_all('section'):
            section_id = section.get('id', '')
            if 'skill' in section_id.lower():
                skills_section = section
                skills_findings['section_selector'] = f'section#{section_id}'
                break
        
        if skills_section:
            # Look for skill items
            skill_items = []
            for elem in skills_section.find_all(['div', 'span']):
                text = elem.get_text(strip=True)
                if text and 2 < len(text) < 50 and not any(x in text.lower() for x in ['see', 'show', 'more']):
                    skill_items.append(text)
            
            if skill_items:
                skills_findings['count'] = len(set(skill_items))
                skills_findings['examples'] = list(set(skill_items))[:5]
        
        self.findings['skills'] = skills_findings
        self._print_findings_table('Skills', skills_findings)
    
    def analyze_certifications_section(self):
        """Find selectors for certifications."""
        console.print("\n[yellow]▶ Analyzing Certifications Section...[/yellow]")
        
        cert_findings = {}
        
        # Find certifications section
        cert_section = None
        for section in self.soup.find_all('section'):
            section_id = section.get('id', '')
            if any(x in section_id.lower() for x in ['certification', 'license']):
                cert_section = section
                cert_findings['section_selector'] = f'section#{section_id}'
                break
        
        if cert_section:
            list_items = cert_section.find_all('li')
            if list_items:
                cert_findings['item_count'] = len(list_items)
        
        self.findings['certifications'] = cert_findings
        self._print_findings_table('Certifications', cert_findings)
    
    def analyze_json_ld(self):
        """Check for JSON-LD structured data."""
        console.print("\n[yellow]▶ Analyzing JSON-LD Data...[/yellow]")
        
        json_ld_findings = {}
        
        scripts = self.soup.find_all('script', type='application/ld+json')
        if scripts:
            json_ld_findings['found'] = True
            json_ld_findings['count'] = len(scripts)
            
            for i, script in enumerate(scripts):
                if script.string:
                    try:
                        data = json.loads(script.string)
                        if '@type' in data:
                            json_ld_findings[f'type_{i}'] = data.get('@type')
                    except:
                        pass
        else:
            json_ld_findings['found'] = False
        
        self.findings['json_ld'] = json_ld_findings
        self._print_findings_table('JSON-LD', json_ld_findings)
    
    def generate_selector_recommendations(self):
        """Generate recommended selector updates."""
        console.print("\n[bold green]📋 Recommended Selector Updates:[/bold green]\n")
        
        recommendations = []
        
        if 'header' in self.findings:
            header = self.findings['header']
            if 'name' in header:
                recommendations.append(f"Name: {header['name']['selector']}")
            if 'headline' in header:
                recommendations.append(f"Headline: {header['headline']['selector']}")
            if 'location' in header:
                recommendations.append(f"Location: {header['location']['selector']}")
        
        if 'experience' in self.findings and 'section_selector' in self.findings['experience']:
            recommendations.append(f"Experience Section: {self.findings['experience']['section_selector']}")
        
        if 'education' in self.findings and 'section_selector' in self.findings['education']:
            recommendations.append(f"Education Section: {self.findings['education']['section_selector']}")
        
        if recommendations:
            for rec in recommendations:
                console.print(f"  • {rec}")
        else:
            console.print("  [red]No clear selectors found - HTML may be dynamic or require authentication[/red]")
    
    def _get_selector(self, element):
        """Generate a CSS selector for an element."""
        if element.get('id'):
            return f"#{element.get('id')}"
        elif element.get('class'):
            classes = element.get('class')
            return f"{element.name}.{'.'.join(classes)}"
        else:
            return element.name
    
    def _get_tag_class(self, element):
        """Get tag with primary class."""
        if element.get('class'):
            return f"{element.name}.{element.get('class')[0]}"
        return element.name
    
    def _print_findings_table(self, title, findings):
        """Pretty print findings in a table."""
        if not findings:
            console.print(f"  [dim]No {title.lower()} data found[/dim]")
            return
        
        table = Table(title=title, show_header=True)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in findings.items():
            if isinstance(value, dict):
                value = json.dumps(value, indent=2)[:100]
            elif isinstance(value, list):
                value = ', '.join(str(v)[:20] for v in value[:3])
            table.add_row(key, str(value)[:100])
        
        console.print(table)

def main():
    """Main function to analyze HTML files."""
    import sys
    
    if len(sys.argv) < 2:
        console.print("[red]Usage: python update_parser_selectors.py <html_file>[/red]")
        sys.exit(1)
    
    html_file = Path(sys.argv[1])
    if not html_file.exists():
        console.print(f"[red]File not found: {html_file}[/red]")
        sys.exit(1)
    
    # Load HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Analyze
    analyzer = SelectorAnalyzer(html_content)
    findings = analyzer.analyze_all()
    
    # Save findings
    output_file = html_file.with_suffix('.selectors.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2)
    
    console.print(f"\n[green]✅ Analysis complete! Findings saved to: {output_file}[/green]")

if __name__ == "__main__":
    main()