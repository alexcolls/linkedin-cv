"""Tests for PDF generator."""
from pathlib import Path

import pytest

from src.pdf.generator import PDFGenerator


def test_pdf_generator_initialization():
    """Test PDFGenerator initialization."""
    generator = PDFGenerator()
    assert generator.template_path is None
    assert generator.templates_dir.name == "templates"


def test_pdf_generator_with_custom_template():
    """Test PDFGenerator with custom template path."""
    generator = PDFGenerator(template_path="/path/to/template.html")
    assert generator.template_path == "/path/to/template.html"


def test_templates_directory_exists():
    """Test that templates directory exists."""
    generator = PDFGenerator()
    assert generator.templates_dir.exists()


def test_template_files_exist():
    """Test that required template files exist."""
    generator = PDFGenerator()
    html_template = generator.templates_dir / "cv_template.html"
    css_file = generator.templates_dir / "style.css"

    assert html_template.exists(), "cv_template.html should exist"
    assert css_file.exists(), "style.css should exist"


def test_validate_template_with_valid_template():
    """Test template validation with valid template."""
    generator = PDFGenerator()
    template_path = generator.templates_dir / "cv_template.html"
    assert generator.validate_template(str(template_path))


def test_validate_template_with_invalid_path():
    """Test template validation with invalid path."""
    generator = PDFGenerator()
    assert not generator.validate_template("/nonexistent/template.html")
