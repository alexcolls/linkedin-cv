#!/usr/bin/env python3
"""Generate a sample CV with test data to verify PDF generation works."""

import sys
from pathlib import Path
from datetime import datetime
from src.pdf.generator import PDFGenerator
from src.utils.image_processor import ImageProcessor

# Sample comprehensive profile data
SAMPLE_PROFILE = {
    "username": "john-doe",
    "name": "John Doe",
    "headline": "Senior Software Engineer | Full Stack Developer | Tech Lead",
    "location": "San Francisco, California, United States",
    "about": """Passionate software engineer with over 8 years of experience building scalable web applications and leading engineering teams. 

Specialized in full-stack development using modern technologies including React, Node.js, Python, and cloud platforms (AWS, GCP). Strong advocate for clean code, test-driven development, and agile methodologies.

Currently leading a team of 5 engineers at TechCorp, where we're building next-generation fintech solutions that process millions of transactions daily. Previously contributed to open-source projects and mentored junior developers.

Always eager to tackle challenging problems and learn new technologies. Open to opportunities where I can make a significant impact while continuing to grow professionally.""",
    
    "contact_info": {
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "website": "https://johndoe.dev"
    },
    
    "stats": {
        "connections": "500+",
        "followers": "2,341"
    },
    
    "experience": [
        {
            "title": "Senior Software Engineer & Tech Lead",
            "company": "TechCorp Inc.",
            "employment_type": "Full-time",
            "duration": "Jan 2020 - Present · 4 yrs 10 mos",
            "location": "San Francisco, CA",
            "description": """Leading the development of a next-generation fintech platform serving 1M+ users.
            
• Architected and implemented microservices infrastructure handling 10K+ TPS
• Led team of 5 engineers, conducting code reviews and mentoring junior developers
• Reduced system latency by 40% through optimization and caching strategies
• Implemented CI/CD pipelines reducing deployment time from hours to minutes
• Collaborated with product team to define technical requirements and roadmap""",
            "skills": ["Python", "React", "Node.js", "AWS", "Kubernetes", "PostgreSQL", "Redis"]
        },
        {
            "title": "Full Stack Developer",
            "company": "StartupXYZ",
            "employment_type": "Full-time",
            "duration": "Jun 2018 - Dec 2019 · 1 yr 7 mos",
            "location": "San Francisco, CA",
            "description": """Developed core features for a SaaS platform from MVP to 50K users.
            
• Built RESTful APIs using Node.js and Express serving React frontend
• Implemented real-time features using WebSockets and Redis pub/sub
• Designed and optimized PostgreSQL database schema for scalability
• Integrated third-party services including Stripe, SendGrid, and Twilio
• Participated in agile sprints and contributed to architectural decisions""",
            "skills": ["JavaScript", "React", "Node.js", "PostgreSQL", "Docker", "AWS"]
        },
        {
            "title": "Software Developer",
            "company": "Digital Agency Co.",
            "employment_type": "Full-time",
            "duration": "Aug 2016 - May 2018 · 1 yr 10 mos",
            "location": "Los Angeles, CA",
            "description": """Developed custom web applications for enterprise clients.
            
• Created responsive web applications using React and Angular
• Developed backend services using Python Django and Flask
• Worked with clients to gather requirements and provide technical solutions
• Maintained and upgraded legacy systems
• Mentored interns and conducted technical interviews""",
            "skills": ["Python", "Django", "React", "Angular", "MySQL", "Git"]
        }
    ],
    
    "education": [
        {
            "institution": "University of California, Berkeley",
            "degree": "Bachelor of Science (BS)",
            "field": "Computer Science",
            "duration": "2012 - 2016",
            "grade": "3.8 GPA",
            "activities": "Computer Science Club, Hackathon Organizer",
            "description": "Focus on Software Engineering, Algorithms, and Machine Learning. Dean's List 2014-2016."
        },
        {
            "institution": "Coursera",
            "degree": "Specialization Certificate",
            "field": "Deep Learning",
            "duration": "2019",
            "description": "5-course specialization covering neural networks, CNNs, RNNs, and deep learning applications."
        }
    ],
    
    "skills": [
        {"name": "Python", "endorsements": 47},
        {"name": "JavaScript", "endorsements": 42},
        {"name": "React", "endorsements": 38},
        {"name": "Node.js", "endorsements": 35},
        {"name": "AWS", "endorsements": 31},
        {"name": "Docker", "endorsements": 28},
        {"name": "Kubernetes", "endorsements": 24},
        {"name": "PostgreSQL", "endorsements": 22},
        {"name": "Git", "endorsements": 20},
        {"name": "Agile Methodologies", "endorsements": 18},
        {"name": "Machine Learning", "endorsements": 15},
        {"name": "TypeScript", "endorsements": 12}
    ],
    
    "certifications": [
        {
            "name": "AWS Certified Solutions Architect - Associate",
            "issuer": "Amazon Web Services",
            "date": "Issued Mar 2022 · No Expiration Date",
            "credential_id": "ABC123DEF456",
            "url": "https://aws.amazon.com/verification"
        },
        {
            "name": "Google Cloud Professional Cloud Architect",
            "issuer": "Google Cloud",
            "date": "Issued Jan 2021 · Expires Jan 2024",
            "credential_id": "GCP789XYZ",
            "url": "https://cloud.google.com/certification"
        },
        {
            "name": "Certified Kubernetes Administrator (CKA)",
            "issuer": "Cloud Native Computing Foundation",
            "date": "Issued Jun 2020",
            "credential_id": "CKA-2020-1234"
        }
    ],
    
    "languages": [
        {"name": "English", "proficiency": "Native"},
        {"name": "Spanish", "proficiency": "Professional Working"},
        {"name": "Mandarin", "proficiency": "Elementary"}
    ],
    
    "projects": [
        {
            "name": "Open Source Contribution - ReactQuery",
            "date": "2022 - Present",
            "description": "Contributing to ReactQuery, a popular data fetching library. Implemented caching improvements and fixed critical bugs. 15+ merged PRs.",
            "url": "https://github.com/tanstack/query"
        },
        {
            "name": "Personal Blog Platform",
            "date": "2021",
            "description": "Built a modern blog platform using Next.js, MDX, and Tailwind CSS. Features include dark mode, search, and automatic SEO optimization.",
            "url": "https://johndoe.dev/projects/blog"
        },
        {
            "name": "ML Stock Predictor",
            "date": "2020",
            "description": "Developed a machine learning model to predict stock prices using LSTM neural networks. Achieved 72% accuracy on test data.",
            "url": "https://github.com/johndoe/stock-predictor"
        }
    ],
    
    "volunteer": [
        {
            "role": "Coding Instructor",
            "organization": "Code for Kids",
            "duration": "Sep 2019 - Present",
            "cause": "Education",
            "description": "Teaching programming basics to underprivileged youth. Developed curriculum for Python and web development courses. Mentored 50+ students."
        },
        {
            "role": "Technical Advisor",
            "organization": "TechForGood",
            "duration": "2018 - 2019",
            "cause": "Science and Technology",
            "description": "Provided technical guidance to non-profits implementing technology solutions."
        }
    ],
    
    "honors": [
        {
            "title": "Employee of the Year",
            "issuer": "TechCorp Inc.",
            "date": "2022",
            "description": "Recognized for exceptional performance and leadership in delivering critical projects."
        },
        {
            "title": "Best Hackathon Project",
            "issuer": "SF Hacks 2019",
            "date": "2019",
            "description": "Won first place for developing an AI-powered accessibility tool."
        },
        {
            "title": "Dean's List",
            "issuer": "UC Berkeley",
            "date": "2014-2016",
            "description": "Maintained GPA above 3.75 for six consecutive semesters."
        }
    ],
    
    "courses": [
        "Advanced Algorithms and Data Structures",
        "Machine Learning and Neural Networks",
        "Distributed Systems",
        "Software Engineering Best Practices",
        "Cloud Architecture Patterns",
        "Microservices with Spring Boot",
        "React Advanced Patterns",
        "System Design Interview Preparation"
    ],
    
    "publications": [
        {
            "title": "Optimizing Microservice Communication Patterns",
            "publisher": "Medium Engineering Blog",
            "date": "Mar 2023"
        },
        {
            "title": "Building Scalable Real-time Applications with WebSockets",
            "publisher": "Dev.to",
            "date": "Jan 2022"
        }
    ]
}

def main():
    """Generate sample CV with comprehensive data."""
    print("🚀 Generating sample CV with comprehensive profile data...")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate PDF
    generator = PDFGenerator()
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    output_file = output_dir / f"sample_cv_{timestamp}.pdf"
    
    try:
        generator.generate(SAMPLE_PROFILE, str(output_file))
        print(f"✅ Sample CV generated successfully!")
        print(f"📄 Output: {output_file}")
        print("\n📊 Sections included:")
        print("  • Header with name, headline, and location")
        print("  • About section")
        print("  • 3 work experiences")
        print("  • 2 education entries")
        print("  • 12 skills with endorsements")
        print("  • 3 certifications")
        print("  • 3 languages")
        print("  • 3 projects")
        print("  • 2 volunteer experiences")
        print("  • 3 honors & awards")
        print("  • 8 courses")
        print("  • 2 publications")
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()