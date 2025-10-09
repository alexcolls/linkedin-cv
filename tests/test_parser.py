"""Tests for LinkedIn HTML parser."""
import json
import pytest

from src.scraper.parser import ProfileParser


@pytest.fixture
def sample_html():
    """Sample LinkedIn HTML for testing."""
    return """
    <html>
        <head>
            <link rel="canonical" href="https://www.linkedin.com/in/john-doe/" />
        </head>
        <body>
            <h1 class="text-heading-xlarge">John Doe</h1>
            <div class="text-body-medium break-words">Software Engineer</div>
            <span class="text-body-small inline t-black--light break-words">San Francisco, CA</span>
            <section id="about">
                <div class="pv-shared-text-with-see-more">
                    <span aria-hidden="true">Experienced software engineer with expertise in Python and web development.</span>
                </div>
            </section>
        </body>
    </html>
    """


def test_parser_extract_name(sample_html):
    """Test extracting name from profile."""
    parser = ProfileParser()
    profile_data = parser.parse(sample_html)
    assert profile_data["name"] == "John Doe"


def test_parser_extract_username(sample_html):
    """Test extracting username from profile."""
    parser = ProfileParser()
    profile_data = parser.parse(sample_html)
    assert profile_data["username"] == "john-doe"


def test_parser_extract_headline(sample_html):
    """Test extracting headline from profile."""
    parser = ProfileParser()
    profile_data = parser.parse(sample_html)
    assert profile_data["headline"] == "Software Engineer"


def test_parser_extract_about(sample_html):
    """Test extracting about section."""
    parser = ProfileParser()
    profile_data = parser.parse(sample_html)
    assert "Experienced software engineer" in profile_data["about"]


def test_parser_handles_empty_sections():
    """Test parser handles missing sections gracefully."""
    parser = ProfileParser()
    profile_data = parser.parse("<html><body></body></html>")
    assert profile_data["experience"] == []
    assert profile_data["education"] == []
    assert profile_data["skills"] == []


@pytest.fixture
def json_ld_html():
    """Sample LinkedIn HTML with JSON-LD structured data."""
    json_ld_data = {
        "@context": "http://schema.org",
        "@type": "Person",
        "name": "Jane Smith",
        "sameAs": "https://www.linkedin.com/in/jane-smith",
        "jobTitle": ["Senior Engineer", "Tech Lead"],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "New York",
            "addressRegion": "NY",
            "addressCountry": "US"
        },
        "disambiguatingDescription": "Passionate about building scalable systems",
        "image": {
            "@type": "ImageObject",
            "contentUrl": "https://media.licdn.com/photo.jpg"
        },
        "interactionStatistic": {
            "@type": "InteractionCounter",
            "userInteractionCount": 5000
        },
        "worksFor": [
            {
                "@type": "Organization",
                "name": "Tech Corp",
                "location": "San Francisco, CA",
                "member": {
                    "@type": "OrganizationRole",
                    "startDate": 2020,
                    "description": "Leading backend infrastructure team"
                }
            }
        ],
        "alumniOf": [
            {
                "@type": "EducationalOrganization",
                "name": "MIT",
                "member": {
                    "@type": "OrganizationRole",
                    "startDate": 2015,
                    "endDate": 2019
                }
            }
        ],
        "knowsLanguage": [
            {"@type": "Language", "name": "English"},
            {"@type": "Language", "name": "Spanish"}
        ],
        "awards": ["Best Innovation Award 2023"]
    }
    
    return f"""
    <html>
        <head>
            <script type="application/ld+json">
            {json.dumps(json_ld_data)}
            </script>
        </head>
        <body></body>
    </html>
    """


def test_parser_json_ld_extraction(json_ld_html):
    """Test extracting data from JSON-LD."""
    parser = ProfileParser()
    profile_data = parser.parse(json_ld_html)
    
    assert profile_data["name"] == "Jane Smith"
    assert profile_data["username"] == "jane-smith"
    assert profile_data["headline"] == "Senior Engineer"
    assert profile_data["location"] == "New York, NY, US"
    assert profile_data["about"] == "Passionate about building scalable systems"
    assert profile_data["profile_picture_url"] == "https://media.licdn.com/photo.jpg"


def test_parser_json_ld_experience(json_ld_html):
    """Test extracting experience from JSON-LD."""
    parser = ProfileParser()
    profile_data = parser.parse(json_ld_html)
    
    assert len(profile_data["experience"]) == 1
    exp = profile_data["experience"][0]
    assert exp["company"] == "Tech Corp"
    assert exp["location"] == "San Francisco, CA"
    assert "2020" in exp["duration"]


def test_parser_json_ld_education(json_ld_html):
    """Test extracting education from JSON-LD."""
    parser = ProfileParser()
    profile_data = parser.parse(json_ld_html)
    
    assert len(profile_data["education"]) == 1
    edu = profile_data["education"][0]
    assert edu["institution"] == "MIT"
    assert "2015" in edu["duration"]
    assert "2019" in edu["duration"]


def test_parser_json_ld_languages(json_ld_html):
    """Test extracting languages from JSON-LD."""
    parser = ProfileParser()
    profile_data = parser.parse(json_ld_html)
    
    assert len(profile_data["languages"]) == 2
    lang_names = [lang["name"] for lang in profile_data["languages"]]
    assert "English" in lang_names
    assert "Spanish" in lang_names


def test_parser_json_ld_stats(json_ld_html):
    """Test extracting stats from JSON-LD."""
    parser = ProfileParser()
    profile_data = parser.parse(json_ld_html)
    
    assert profile_data["stats"]["followers"] == "5000"


def test_parser_fallback_to_html():
    """Test parser falls back to HTML parsing when no JSON-LD."""
    html = """
    <html>
        <head>
            <link rel="canonical" href="https://www.linkedin.com/in/test-user/" />
        </head>
        <body>
            <h1 class="text-heading-xlarge">Test User</h1>
        </body>
    </html>
    """
    parser = ProfileParser()
    profile_data = parser.parse(html)
    
    assert profile_data["name"] == "Test User"
    assert profile_data["username"] == "test-user"


def test_normalize_profile_url():
    """Test URL normalization."""
    from src.cli import normalize_profile_url
    
    # Full URL
    assert normalize_profile_url("https://www.linkedin.com/in/username/") == "https://www.linkedin.com/in/username"
    
    # Username only
    assert normalize_profile_url("username") == "https://www.linkedin.com/in/username/"
    
    # With @ symbol
    assert normalize_profile_url("@username") == "https://www.linkedin.com/in/username/"
    
    # Partial URL
    assert normalize_profile_url("linkedin.com/in/username") == "https://linkedin.com/in/username"
