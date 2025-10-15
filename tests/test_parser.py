"""Tests for ProfileParser class."""
import pytest
from src.scraper.parser import ProfileParser


class TestProfileParser:
    """Test suite for ProfileParser."""

    def test_parser_initialization(self):
        """Test parser can be initialized."""
        parser = ProfileParser()
        assert parser is not None
        assert parser.debug is False

    def test_parser_with_debug(self):
        """Test parser can be initialized with debug mode."""
        parser = ProfileParser(debug=True)
        assert parser.debug is True

    def test_parse_basic_profile(self, sample_profile_html):
        """Test parsing basic profile information."""
        parser = ProfileParser()
        result = parser.parse(sample_profile_html)
        
        assert result is not None
        assert isinstance(result, dict)
        assert result['name'] == 'John Doe'
        assert result['headline'] == 'Senior Software Engineer'
        assert result['location'] == 'San Francisco, California'
        assert 'Experienced software engineer' in result['about']

    def test_parse_experience_detail(self, sample_experience_html):
        """Test parsing experience from detail page."""
        parser = ProfileParser()
        result = parser.parse_experience_detail(sample_experience_html)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) >= 1
        
        experience = result[0]
        assert experience['title'] == 'Senior Software Engineer'
        assert experience['company'] == 'Acme Corp'
        assert 'Jan 2020' in experience['duration']

    def test_parse_education_detail(self, sample_education_html):
        """Test parsing education from detail page."""
        parser = ProfileParser()
        result = parser.parse_education_detail(sample_education_html)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) >= 1
        
        education = result[0]
        assert education['institution'] == 'Stanford University'
        # Degree field contains full text including field of study
        assert 'Bachelor of Science' in education['degree']

    def test_parse_skills_detail(self, sample_skills_html):
        """Test parsing skills from detail page."""
        parser = ProfileParser()
        result = parser.parse_skills_detail(sample_skills_html)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) >= 2
        
        # Check first skill
        python_skill = result[0]
        assert python_skill['name'] == 'Python'
        assert python_skill['endorsements'] == 45
        
        # Check second skill
        js_skill = result[1]
        assert js_skill['name'] == 'JavaScript'
        assert js_skill['endorsements'] == 32

    def test_parse_certifications_detail(self, sample_certifications_html):
        """Test parsing certifications from detail page."""
        parser = ProfileParser()
        result = parser.parse_certifications_detail(sample_certifications_html)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) >= 1
        
        cert = result[0]
        assert cert['name'] == 'AWS Certified Solutions Architect'
        assert cert['issuer'] == 'Amazon Web Services'

    def test_parse_empty_html(self):
        """Test parsing empty HTML returns empty structures."""
        parser = ProfileParser()
        result = parser.parse("<html><body></body></html>")
        
        assert result is not None
        assert isinstance(result, dict)
        # Should have default/empty values
        assert isinstance(result.get('experience', []), list)
        assert isinstance(result.get('education', []), list)

    def test_parse_malformed_html(self):
        """Test parser handles malformed HTML gracefully."""
        parser = ProfileParser()
        # Should not raise exception
        result = parser.parse("<html><body><div>incomplete")
        assert result is not None

    def test_parse_projects_detail_empty(self):
        """Test parsing projects with no data."""
        parser = ProfileParser()
        empty_html = "<html><body><main></main></body></html>"
        result = parser.parse_projects_detail(empty_html)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

    def test_parse_languages_detail_empty(self):
        """Test parsing languages with no data."""
        parser = ProfileParser()
        empty_html = "<html><body><main></main></body></html>"
        result = parser.parse_languages_detail(empty_html)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

    def test_parse_volunteer_detail_empty(self):
        """Test parsing volunteer experiences with no data."""
        parser = ProfileParser()
        empty_html = "<html><body><main></main></body></html>"
        result = parser.parse_volunteer_detail(empty_html)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

    def test_parse_publications_detail_empty(self):
        """Test parsing publications with no data."""
        parser = ProfileParser()
        empty_html = "<html><body><main></main></body></html>"
        result = parser.parse_publications_detail(empty_html)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

    def test_parse_honors_detail_empty(self):
        """Test parsing honors with no data."""
        parser = ProfileParser()
        empty_html = "<html><body><main></main></body></html>"
        result = parser.parse_honors_detail(empty_html)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 0

    def test_safe_extract_valid(self):
        """Test _safe_extract with valid selector."""
        from bs4 import BeautifulSoup
        
        parser = ProfileParser()
        html = '<div><span class="test">Hello</span></div>'
        soup = BeautifulSoup(html, 'lxml')
        
        result = parser._safe_extract(soup, 'span.test')
        assert result == 'Hello'

    def test_safe_extract_invalid(self):
        """Test _safe_extract with invalid selector returns None."""
        from bs4 import BeautifulSoup
        
        parser = ProfileParser()
        html = '<div><span>Hello</span></div>'
        soup = BeautifulSoup(html, 'lxml')
        
        result = parser._safe_extract(soup, 'span.nonexistent')
        assert result is None

    def test_extract_username_from_profile(self):
        """Test username extraction."""
        parser = ProfileParser()
        html = """
        <html>
            <body>
                <script type="application/ld+json">
                {
                    "@type": "Person",
                    "sameAs": "https://www.linkedin.com/in/john-doe"
                }
                </script>
            </body>
        </html>
        """
        result = parser.parse(html)
        # Username should be extracted from JSON-LD
        assert 'username' in result

    def test_parse_with_sections_count(self, sample_profile_html):
        """Test that parser counts non-empty sections."""
        parser = ProfileParser()
        result = parser.parse(sample_profile_html)
        
        assert 'sections' in result
        assert isinstance(result['sections'], list)
        assert len(result['sections']) > 0


class TestParserHelpers:
    """Test suite for parser helper methods."""

    def test_extract_single_skill(self):
        """Test _extract_single_skill method."""
        from bs4 import BeautifulSoup
        
        parser = ProfileParser()
        html = """
        <li class="pvs-list__paged-list-item">
            <div class="display-flex align-items-center">
                <span aria-hidden="true">Python</span>
            </div>
            <span class="t-14 t-black--light">
                <span aria-hidden="true">25 endorsements</span>
            </span>
        </li>
        """
        soup = BeautifulSoup(html, 'lxml')
        item = soup.find('li')
        
        result = parser._extract_single_skill(item)
        assert result is not None
        assert result['name'] == 'Python'
        assert result['endorsements'] == 25

    def test_extract_single_certification(self):
        """Test _extract_single_certification method."""
        from bs4 import BeautifulSoup
        
        parser = ProfileParser()
        html = """
        <li class="pvs-list__paged-list-item">
            <div class="display-flex align-items-center">
                <span aria-hidden="true">AWS Certification</span>
            </div>
            <span class="t-14 t-normal">
                <span aria-hidden="true">Amazon</span>
            </span>
        </li>
        """
        soup = BeautifulSoup(html, 'lxml')
        item = soup.find('li')
        
        result = parser._extract_single_certification(item)
        assert result is not None
        assert result['name'] == 'AWS Certification'
        assert result['issuer'] == 'Amazon'

    def test_extract_single_language(self):
        """Test _extract_single_language method."""
        from bs4 import BeautifulSoup
        
        parser = ProfileParser()
        html = """
        <li class="pvs-list__paged-list-item">
            <div class="display-flex align-items-center">
                <span aria-hidden="true">Spanish</span>
            </div>
            <span class="t-14 t-normal t-black--light">
                <span aria-hidden="true">Native or bilingual proficiency</span>
            </span>
        </li>
        """
        soup = BeautifulSoup(html, 'lxml')
        item = soup.find('li')
        
        result = parser._extract_single_language(item)
        assert result is not None
        assert result['name'] == 'Spanish'
        assert 'proficiency' in result

    def test_extract_single_volunteer(self):
        """Test _extract_single_volunteer method."""
        from bs4 import BeautifulSoup
        
        parser = ProfileParser()
        html = """
        <li class="pvs-list__paged-list-item">
            <div class="display-flex align-items-center">
                <span aria-hidden="true">Volunteer Teacher</span>
            </div>
            <span class="t-14 t-normal">
                <span aria-hidden="true">Local School</span>
            </span>
        </li>
        """
        soup = BeautifulSoup(html, 'lxml')
        item = soup.find('li')
        
        result = parser._extract_single_volunteer(item)
        assert result is not None
        assert result['role'] == 'Volunteer Teacher'
        assert result['organization'] == 'Local School'
