"""Tests for PDFGenerator class."""
import pytest
from pathlib import Path
from src.pdf.generator import PDFGenerator


class TestPDFGenerator:
    """Test suite for PDFGenerator."""

    def test_generator_initialization(self):
        """Test generator can be initialized."""
        generator = PDFGenerator()
        assert generator is not None
        assert generator.template_path is None

    def test_generator_with_custom_template(self, tmp_path):
        """Test generator with custom template path."""
        template_file = tmp_path / "custom_template.html"
        template_file.write_text("<html><body>{{ name }}</body></html>")
        
        generator = PDFGenerator(template_path=str(template_file))
        assert generator.template_path == str(template_file)

    def test_generate_pdf(self, sample_profile_data, temp_output_dir):
        """Test PDF generation from profile data."""
        generator = PDFGenerator()
        output_file = temp_output_dir / "test_cv.pdf"
        
        # Generate PDF
        generator.generate(sample_profile_data, str(output_file))
        
        # Check file was created
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_generate_pdf_with_image_data(self, sample_profile_data, temp_output_dir):
        """Test PDF generation with profile image."""
        # Add base64 image data
        sample_profile_data['profile_image_data'] = 'data:image/jpeg;base64,/9j/4AAQSkZJRg=='
        
        generator = PDFGenerator()
        output_file = temp_output_dir / "test_cv_with_image.pdf"
        
        generator.generate(sample_profile_data, str(output_file))
        
        assert output_file.exists()

    def test_generate_pdf_missing_data(self, temp_output_dir):
        """Test PDF generation with minimal data."""
        minimal_data = {
            'name': 'Test User',
            'headline': 'Test Headline'
        }
        
        generator = PDFGenerator()
        output_file = temp_output_dir / "test_cv_minimal.pdf"
        
        # Should not raise exception
        generator.generate(minimal_data, str(output_file))
        assert output_file.exists()

    def test_validate_template_valid(self, tmp_path):
        """Test template validation with valid template."""
        template_file = tmp_path / "valid_template.html"
        template_file.write_text("<html><body>{{ name }}</body></html>")
        
        generator = PDFGenerator()
        assert generator.validate_template(str(template_file)) is True

    def test_validate_template_invalid(self, tmp_path):
        """Test template validation with invalid template."""
        template_file = tmp_path / "invalid_template.html"
        template_file.write_text("{{ invalid }}")
        
        generator = PDFGenerator()
        # Should handle gracefully
        result = generator.validate_template(str(template_file))
        assert isinstance(result, bool)

    def test_templates_directory_exists(self):
        """Test that templates directory exists."""
        generator = PDFGenerator()
        assert generator.templates_dir.exists()
        assert generator.templates_dir.is_dir()

    def test_default_template_exists(self):
        """Test that default CV template exists."""
        generator = PDFGenerator()
        template_file = generator.templates_dir / "cv_template.html"
        assert template_file.exists()

    def test_default_css_exists(self):
        """Test that default CSS file exists."""
        generator = PDFGenerator()
        css_file = generator.templates_dir / "style.css"
        assert css_file.exists()


class TestPDFGeneratorEdgeCases:
    """Test edge cases for PDF generation."""

    def test_generate_with_empty_sections(self, temp_output_dir):
        """Test PDF with empty sections doesn't crash."""
        data = {
            'name': 'Test User',
            'experience': [],
            'education': [],
            'skills': []
        }
        
        generator = PDFGenerator()
        output_file = temp_output_dir / "test_empty_sections.pdf"
        
        generator.generate(data, str(output_file))
        assert output_file.exists()

    def test_generate_with_long_text(self, temp_output_dir):
        """Test PDF with very long text content."""
        data = {
            'name': 'Test User',
            'about': 'Lorem ipsum ' * 1000  # Very long text
        }
        
        generator = PDFGenerator()
        output_file = temp_output_dir / "test_long_text.pdf"
        
        generator.generate(data, str(output_file))
        assert output_file.exists()

    def test_generate_with_special_characters(self, temp_output_dir):
        """Test PDF with special characters."""
        data = {
            'name': 'Tëst Üsér',
            'headline': 'Sénior Développeur',
            'location': 'São Paulo, Brasil'
        }
        
        generator = PDFGenerator()
        output_file = temp_output_dir / "test_special_chars.pdf"
        
        generator.generate(data, str(output_file))
        assert output_file.exists()
