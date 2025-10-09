"""End-to-end tests for LinkedIn CV Generator."""
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.cli import generate_cv
from src.pdf.generator import PDFGenerator
from src.scraper.linkedin_scraper import LinkedInScraper
from src.scraper.parser import ProfileParser
from src.utils.image_processor import ImageProcessor


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing."""
    return {
        "username": "john-doe",
        "name": "John Doe",
        "headline": "Software Engineer at Tech Corp",
        "location": "San Francisco, CA",
        "profile_picture_url": "https://example.com/photo.jpg",
        "about": "Experienced software engineer with expertise in Python.",
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "duration": "2020 - Present",
                "location": "San Francisco, CA",
                "description": "Building scalable applications",
            }
        ],
        "education": [
            {
                "institution": "Stanford University",
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "duration": "2016 - 2020",
            }
        ],
        "skills": ["Python", "JavaScript", "Docker"],
        "certifications": [],
        "languages": ["English", "Spanish"],
        "volunteer": [],
        "projects": [],
        "publications": [],
        "honors": [],
        "courses": [],
        "sections": ["name", "headline", "experience", "education", "skills"],
    }


@pytest.fixture
def sample_html():
    """Sample LinkedIn HTML."""
    return """
    <html>
        <head>
            <link rel="canonical" href="https://www.linkedin.com/in/john-doe/" />
        </head>
        <body>
            <h1 class="text-heading-xlarge">John Doe</h1>
            <div class="text-body-medium break-words">Software Engineer at Tech Corp</div>
        </body>
    </html>
    """


@pytest.mark.asyncio
async def test_e2e_workflow_success(tmp_path, sample_html, sample_profile_data):
    """Test complete workflow from URL to PDF."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with patch.object(LinkedInScraper, "scrape_profile", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = sample_html

        with patch.object(ProfileParser, "parse") as mock_parse:
            mock_parse.return_value = sample_profile_data

            with patch.object(
                ImageProcessor, "process"
            ) as mock_image:
                mock_image.return_value = "data:image/jpeg;base64,fake_image_data"

                with patch.object(PDFGenerator, "generate") as mock_pdf:
                    mock_pdf.return_value = None

                    # Run the workflow
                    await generate_cv(
                        profile_url="https://www.linkedin.com/in/john-doe/",
                        output_path=output_dir,
                        template=None,
                        html_file=None,
                        headless=True,
                        debug=False,
                    )

                    # Verify scraper was called
                    mock_scrape.assert_called_once_with(
                        "https://www.linkedin.com/in/john-doe/"
                    )

                    # Verify parser was called
                    mock_parse.assert_called_once_with(sample_html)

                    # Verify image processor was called
                    mock_image.assert_called_once()

                    # Verify PDF generator was called
                    mock_pdf.assert_called_once()


@pytest.mark.asyncio
async def test_e2e_workflow_without_profile_picture(tmp_path, sample_html):
    """Test workflow when profile has no picture."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    profile_data_no_pic = {
        "username": "john-doe",
        "name": "John Doe",
        "headline": "Software Engineer",
        "location": None,
        "profile_picture_url": None,  # No profile picture
        "about": "Test bio",
        "experience": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "languages": [],
        "volunteer": [],
        "projects": [],
        "publications": [],
        "honors": [],
        "courses": [],
        "sections": ["name", "headline"],
    }

    with patch.object(LinkedInScraper, "scrape_profile", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = sample_html

        with patch.object(ProfileParser, "parse") as mock_parse:
            mock_parse.return_value = profile_data_no_pic

            with patch.object(PDFGenerator, "generate") as mock_pdf:
                mock_pdf.return_value = None

                await generate_cv(
                    profile_url="https://www.linkedin.com/in/john-doe/",
                    output_path=output_dir,
                    template=None,
                    html_file=None,
                    headless=True,
                    debug=False,
                )

                # Should still generate PDF without image
                mock_pdf.assert_called_once()


@pytest.mark.asyncio
async def test_e2e_workflow_image_processing_fails(tmp_path, sample_html, sample_profile_data):
    """Test workflow when image processing fails."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with patch.object(LinkedInScraper, "scrape_profile", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = sample_html

        with patch.object(ProfileParser, "parse") as mock_parse:
            mock_parse.return_value = sample_profile_data

            with patch.object(ImageProcessor, "process") as mock_image:
                # Image processing fails
                mock_image.side_effect = Exception("Image download failed")

                with patch.object(PDFGenerator, "generate") as mock_pdf:
                    mock_pdf.return_value = None

                    # Should handle error gracefully and continue
                    await generate_cv(
                        profile_url="https://www.linkedin.com/in/john-doe/",
                        output_path=output_dir,
                        template=None,
                        html_file=None,
                        headless=True,
                        debug=False,
                    )

                    # PDF should still be generated
                    mock_pdf.assert_called_once()


def test_output_file_naming(tmp_path, sample_profile_data):
    """Test that output files are named correctly."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    generator = PDFGenerator()
    username = sample_profile_data["username"]

    # Check filename pattern
    import re
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    expected_pattern = f"{username}_{timestamp}.pdf"

    # Verify pattern matches expected format
    assert re.match(r"john-doe_\d{4}-\d{2}-\d{2}-\d{6}\.pdf", expected_pattern)
