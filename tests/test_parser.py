"""Tests for LinkedIn HTML parser."""
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
