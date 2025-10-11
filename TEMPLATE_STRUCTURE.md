# LinkedIn CV Template Structure

## Current Issues

The LinkedIn scraper is getting limited data due to authentication requirements:
- Only basic profile info is accessible without login
- Experience section is incorrectly parsing mixed content  
- Most sections return empty

## Required: Login First

To get complete data:
```bash
./run.sh
# Select option 3: Login to LinkedIn
```

## Template Folder Structure

Create your own custom templates in `templates/` folder:

```
templates/
├── modern/
│   ├── template.html       # Main HTML template
│   ├── style.css          # CSS styles
│   └── assets/            # Images, fonts, etc
├── classic/
│   ├── template.html
│   └── style.css
└── minimal/
    ├── template.html
    └── style.css
```

## JSON Data Structure (When Complete)

```json
{
  "name": "Your Name",
  "headline": "Your Professional Title",
  "location": "City, Country",
  "profile_picture_url": "https://...",
  "about": "Your professional summary...",
  
  "contact_info": {
    "email": "email@example.com",
    "phone": "+1234567890",
    "website": "https://yoursite.com"
  },
  
  "stats": {
    "connections": "500+",
    "followers": "1000"
  },
  
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "employment_type": "Full-time",
      "duration": "Jan 2020 - Present",
      "location": "City, Country",
      "description": "Job description...",
      "skills": ["Skill1", "Skill2"]
    }
  ],
  
  "education": [
    {
      "institution": "University Name",
      "degree": "Degree Type",
      "field": "Field of Study",
      "duration": "2016 - 2020",
      "grade": "GPA or Grade",
      "activities": "Activities...",
      "description": "Additional info..."
    }
  ],
  
  "skills": [
    {
      "name": "Skill Name",
      "endorsements": 50
    }
  ],
  
  "certifications": [
    {
      "name": "Certification Name",
      "issuer": "Issuing Organization",
      "date": "Issue Date",
      "credential_id": "ID",
      "credential_url": "https://..."
    }
  ],
  
  "languages": [
    {
      "name": "Language",
      "proficiency": "Native/Professional/Limited"
    }
  ],
  
  "volunteer": [
    {
      "role": "Volunteer Role",
      "organization": "Organization",
      "cause": "Cause",
      "duration": "Duration",
      "description": "Description..."
    }
  ],
  
  "projects": [
    {
      "name": "Project Name",
      "description": "Description...",
      "url": "https://...",
      "date": "Date"
    }
  ],
  
  "publications": [
    {
      "title": "Publication Title",
      "publisher": "Publisher",
      "date": "Date",
      "url": "https://..."
    }
  ],
  
  "honors": [
    {
      "title": "Award Title",
      "issuer": "Issuer",
      "date": "Date",
      "description": "Description..."
    }
  ],
  
  "courses": ["Course 1", "Course 2"]
}
```

## Creating Custom Templates

### 1. HTML Template (template.html)

Use Jinja2 syntax for variables:
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ name }} - CV</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>{{ name }}</h1>
        <p>{{ headline }}</p>
    </header>
    
    {% if experience %}
    <section class="experience">
        <h2>Experience</h2>
        {% for job in experience %}
        <div class="job">
            <h3>{{ job.title }}</h3>
            <p>{{ job.company }}</p>
            <p>{{ job.duration }}</p>
            <p>{{ job.description }}</p>
        </div>
        {% endfor %}
    </section>
    {% endif %}
</body>
</html>
```

### 2. CSS Styles (style.css)

```css
body {
    font-family: Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.experience {
    margin-top: 30px;
}

.job {
    margin-bottom: 20px;
    padding: 15px;
    border-left: 3px solid #0077b5;
}
```

## Using Custom Templates

```bash
# Generate with custom template
./run.sh username --template templates/modern/template.html

# Or via menu
./run.sh
# Select option 1: Generate CV
# It will use default template or you can specify custom
```

## Next Steps

1. **Login to LinkedIn first** to get complete data
2. **Export to JSON** (option 2 in menu) to see what data you have
3. **Create your custom template** in `templates/` folder
4. **Test with your template** to generate PDF

## Tips

- The PDF generator uses WeasyPrint which supports most CSS3 features
- Keep styles simple for better PDF compatibility
- Test with small data first before full profile
- Use `--debug` flag to see what's happening