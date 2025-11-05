"""PDF generation using WeasyPrint and Jinja2 templates."""
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Template
from weasyprint import HTML, CSS

from src.exceptions import PDFGenerationError
from src.pdf.template_manager import ColorScheme, TemplateManager


class PDFGenerator:
    """Generates professional PDF CVs from profile data."""

    def __init__(
        self,
        template_path: Optional[str] = None,
        theme: str = "modern",
        color_scheme: Optional[ColorScheme] = None,
        custom_colors: Optional[Dict[str, str]] = None,
    ):
        """Initialize the PDF generator.

        Args:
            template_path: Path to custom HTML template (optional)
            theme: Template theme to use (default: "modern")
            color_scheme: Custom color scheme (optional)
            custom_colors: Custom color overrides (optional)
        """
        self.template_path = template_path
        self.theme = theme
        self.color_scheme = color_scheme
        self.custom_colors = custom_colors
        self.templates_dir = Path(__file__).parent / "templates"
        self.template_manager = TemplateManager(self.templates_dir)

    def generate(self, profile_data: Dict[str, Any], output_path: str) -> None:
        """Generate professional PDF CV from profile data.

        Args:
            profile_data: Dictionary containing profile information
            output_path: Path where PDF should be saved

        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            # Use custom template if provided
            if self.template_path:
                with open(self.template_path, "r", encoding="utf-8") as f:
                    template = Template(f.read())
                html_content = template.render(**profile_data)
                
                # For custom templates, use default CSS from classic theme
                css_path = self.templates_dir / "classic" / "style.css"
            else:
                # Validate theme
                if not self.template_manager.validate_theme(self.theme):
                    raise PDFGenerationError(
                        f"Invalid theme: '{self.theme}'. "
                        f"Available themes: {', '.join(self.template_manager.get_available_themes())}"
                    )
                
                # Render using template manager
                html_content = self.template_manager.render_template(
                    theme=self.theme,
                    profile_data=profile_data,
                    color_scheme=self.color_scheme,
                    custom_colors=self.custom_colors,
                )
                
                # Load theme-specific CSS
                css_path = self.templates_dir / self.theme / "style.css"

            # Generate PDF using WeasyPrint
            html_doc = HTML(string=html_content)
            
            if css_path.exists():
                css_doc = CSS(filename=str(css_path))
                html_doc.write_pdf(output_path, stylesheets=[css_doc])
            else:
                html_doc.write_pdf(output_path)

        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(
                f"Failed to generate PDF: {str(e)}",
                context={"output_path": output_path, "theme": self.theme},
            )

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
