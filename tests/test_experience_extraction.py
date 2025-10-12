#!/usr/bin/env python3
"""
Test experience extraction with sample LinkedIn-like HTML and JSON-LD data.
"""

from src.scraper.parser import ProfileParser
from rich.console import Console
import json

console = Console()

# Create test HTML with both JSON-LD and HTML experience data
test_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Alex Colls Outumuro - Software Engineer</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@graph": [{
            "@type": "Person",
            "name": "Alex Colls Outumuro",
            "jobTitle": ["Software, Data & Cloud Engineer", "Solana Dev", "Quant"],
            "address": {
                "addressLocality": "Barcelona",
                "addressRegion": "Catalonia",
                "addressCountry": "Spain"
            },
            "worksFor": [
                {
                    "@type": "Organization",
                    "name": "Senior Software Engineer at TechCorp Solutions",
                    "location": "Barcelona, Spain",
                    "member": {
                        "@type": "OrganizationRole",
                        "startDate": "2022-01",
                        "description": "Leading development of cloud-native applications and microservices architecture. Working with AWS, Kubernetes, and Python to build scalable solutions for enterprise clients.",
                        "employmentType": "Full-time"
                    }
                },
                {
                    "@type": "Organization", 
                    "name": "Full Stack Developer at StartupXYZ",
                    "location": "Remote",
                    "member": {
                        "@type": "OrganizationRole",
                        "startDate": "2020-06",
                        "endDate": "2021-12",
                        "description": "Developed web applications using React, Node.js, and PostgreSQL. Implemented CI/CD pipelines and improved deployment processes.",
                        "employmentType": "Full-time"
                    }
                },
                {
                    "@type": "Organization",
                    "name": "Software Engineering Intern at BigTech Inc",
                    "location": "Madrid, Spain",
                    "member": {
                        "@type": "OrganizationRole",
                        "startDate": "2019-06",
                        "endDate": "2019-09",
                        "description": "Worked on internal tools development using Python and Django. Contributed to data analysis projects and API development.",
                        "employmentType": "Internship"
                    }
                }
            ],
            "alumniOf": [
                {
                    "@type": "Organization",
                    "name": "Universitat Politècnica de Catalunya",
                    "member": {
                        "@type": "OrganizationRole",
                        "startDate": "2016",
                        "endDate": "2020"
                    }
                }
            ],
            "knowsLanguage": ["English", "Spanish", "Catalan"]
        }]
    }
    </script>
</head>
<body>
    <main>
        <section id="profile">
            <h1 class="text-heading-xlarge">Alex Colls Outumuro</h1>
            <div class="text-body-medium">Software, Data & Cloud Engineer | Solana Dev | Quant</div>
            <span class="text-body-small">Barcelona, Catalonia, Spain</span>
        </section>
        
        <section id="about">
            <h2>About</h2>
            <div class="pv-shared-text-with-see-more">
                <span aria-hidden="true">Passionate software engineer with expertise in cloud computing, blockchain development, and quantitative trading. Building scalable solutions and exploring the intersection of technology and finance.</span>
            </div>
        </section>
        
        <section id="experience">
            <h2>Experience</h2>
            <ul>
                <li class="pvs-list__paged-list-item artdeco-list__item">
                    <div class="display-flex align-items-center">
                        <span aria-hidden="true">Senior Software Engineer</span>
                    </div>
                    <span class="t-14 t-normal">
                        <span aria-hidden="true">TechCorp Solutions · Full-time</span>
                    </span>
                    <span class="t-14 t-normal t-black--light">
                        <span aria-hidden="true">Jan 2022 - Present · 2 yrs 10 mos</span>
                    </span>
                    <span class="t-14 t-normal t-black--light">
                        <span aria-hidden="true">Barcelona, Spain</span>
                    </span>
                    <div class="pv-shared-text-with-see-more">
                        <span aria-hidden="true">Leading development of cloud-native applications and microservices architecture. Working with AWS, Kubernetes, and Python to build scalable solutions for enterprise clients.</span>
                    </div>
                </li>
            </ul>
        </section>
    </main>
</body>
</html>
'''

def test_experience_extraction():
    """Test the parser's ability to extract experience data."""
    
    console.print("[bold cyan]Testing Experience Extraction[/bold cyan]\n")
    
    parser = ProfileParser()
    profile = parser.parse(test_html)
    
    # Display basic profile info
    console.print("[bold]Basic Profile Info:[/bold]")
    console.print(f"  Name: {profile.get('name', 'Not found')}")
    console.print(f"  Headline: {profile.get('headline', 'Not found')}")
    console.print(f"  Location: {profile.get('location', 'Not found')}")
    console.print(f"  About: {profile.get('about', 'Not found')[:100] if profile.get('about') else 'Not found'}...")
    
    # Check sections parsed
    console.print(f"\n[bold]Sections Parsed:[/bold] {len(profile.get('sections', []))}")
    for section in profile.get('sections', []):
        console.print(f"  • {section}")
    
    # Focus on experience
    experience = profile.get('experience', [])
    console.print(f"\n[bold]Experience Items Found:[/bold] {len(experience)}")
    
    if experience:
        console.print("\n[green]✅ Experience extraction successful![/green]\n")
        
        for i, exp in enumerate(experience, 1):
            console.print(f"[yellow]Experience {i}:[/yellow]")
            console.print(f"  Title: {exp.get('title', 'N/A')}")
            console.print(f"  Company: {exp.get('company', 'N/A')}")
            console.print(f"  Employment Type: {exp.get('employment_type', 'N/A')}")
            console.print(f"  Duration: {exp.get('duration', 'N/A')}")
            console.print(f"  Location: {exp.get('location', 'N/A')}")
            
            desc = exp.get('description', '')
            if desc:
                console.print(f"  Description: {desc[:100]}...")
            else:
                console.print(f"  Description: N/A")
            
            skills = exp.get('skills', [])
            if skills:
                console.print(f"  Skills: {', '.join(skills)}")
            
            console.print()
    else:
        console.print("\n[red]❌ No experience extracted![/red]")
        console.print("[yellow]Debug Info:[/yellow]")
        console.print(f"  HTML length: {len(test_html)} characters")
        console.print(f"  Has JSON-LD: {'application/ld+json' in test_html}")
        console.print(f"  Has experience section: {'experience' in test_html.lower()}")
    
    # Test education
    education = profile.get('education', [])
    console.print(f"[bold]Education Items Found:[/bold] {len(education)}")
    if education:
        for edu in education:
            console.print(f"  • {edu.get('institution', 'N/A')} ({edu.get('duration', 'N/A')})")
    
    # Test languages
    languages = profile.get('languages', [])
    console.print(f"\n[bold]Languages Found:[/bold] {len(languages)}")
    if languages:
        for lang in languages:
            if isinstance(lang, dict):
                console.print(f"  • {lang.get('name', 'N/A')}")
            else:
                console.print(f"  • {lang}")
    
    return profile

if __name__ == "__main__":
    test_experience_extraction()