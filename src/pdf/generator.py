"""PDF generation using WeasyPrint and Jinja2 templates."""
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, Template
from weasyprint import HTML, CSS

from src.exceptions import PDFGenerationError


class PDFGenerator:
    """Generates professional PDF CVs from profile data."""

    def __init__(self, template_path: Optional[str] = None):
        """Initialize the PDF generator.

        Args:
            template_path: Path to custom HTML template (optional)
        """
        self.template_path = template_path
        self.templates_dir = Path(__file__).parent / "templates"

        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
        )

    def generate(self, profile_data: Dict[str, Any], output_path: str) -> None:
        """Generate professional PDF CV from profile data.

        Args:
            profile_data: Dictionary containing profile information
            output_path: Path where PDF should be saved

        Raises:
            Exception: If PDF generation fails
        """
        try:
            # Load template
            if self.template_path:
                with open(self.template_path, "r", encoding="utf-8") as f:
                    template = Template(f.read())
            else:
                template = self.env.get_template("cv_template.html")

            # Render HTML with profile data
            html_content = template.render(**profile_data)

            # Load CSS
            css_path = self.templates_dir / "style.css"

            # Generate PDF using WeasyPrint
            html_doc = HTML(string=html_content)
            
            if css_path.exists():
                css_doc = CSS(filename=str(css_path))
                html_doc.write_pdf(output_path, stylesheets=[css_doc])
            else:
                html_doc.write_pdf(output_path)

        except Exception as e:
            raise PDFGenerationError(str(e))

    def validate_template(self, template_path: str) -> bool:
        """Validate if template file is valid HTML.

        Args:
            template_path: Path to template file

        Returns:
            True if template is valid, False otherwise
        """
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                Template(f.read())
            return True
        except:
            return False
