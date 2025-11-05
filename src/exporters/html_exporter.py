"""HTML export functionality for standalone CV generation."""
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Template

from src.exceptions import PDFGenerationError
from src.pdf.template_manager import ColorScheme, TemplateManager


class HTMLExporter:
    """Export CV as standalone HTML file with embedded CSS."""

    def __init__(
        self,
        theme: str = "modern",
        color_scheme: Optional[ColorScheme] = None,
        custom_colors: Optional[Dict[str, str]] = None,
    ):
        """Initialize HTML exporter.

        Args:
            theme: Template theme to use (default: "modern")
            color_scheme: Custom color scheme (optional)
            custom_colors: Custom color overrides (optional)
        """
        self.theme = theme
        self.color_scheme = color_scheme
        self.custom_colors = custom_colors
        self.templates_dir = Path(__file__).parent.parent / "pdf" / "templates"
        self.template_manager = TemplateManager(self.templates_dir)

    def export(self, profile_data: Dict[str, Any], output_path: str) -> None:
        """Export CV as standalone HTML file.

        Args:
            profile_data: Dictionary containing profile information
            output_path: Path where HTML should be saved

        Raises:
            PDFGenerationError: If HTML export fails
        """
        try:
            # Validate theme
            if not self.template_manager.validate_theme(self.theme):
                raise PDFGenerationError(
                    f"Invalid theme: '{self.theme}'. "
                    f"Available themes: {', '.join(self.template_manager.get_available_themes())}"
                )

            # Get the HTML template
            html_content = self.template_manager.render_template(
                theme=self.theme,
                profile_data=profile_data,
                color_scheme=self.color_scheme,
                custom_colors=self.custom_colors,
            )

            # Load theme-specific CSS
            css_path = self.templates_dir / self.theme / "style.css"
            if css_path.exists():
                with open(css_path, "r", encoding="utf-8") as f:
                    css_content = f.read()
            else:
                css_content = ""

            # Create standalone HTML with embedded CSS
            standalone_html = self._create_standalone_html(html_content, css_content)

            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(standalone_html)

        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(
                f"Failed to export HTML: {str(e)}",
                context={"output_path": output_path, "theme": self.theme},
            )

    def _create_standalone_html(self, html_content: str, css_content: str) -> str:
        """Create standalone HTML with embedded CSS.

        Args:
            html_content: HTML body content
            css_content: CSS stylesheet content

        Returns:
            Complete standalone HTML document
        """
        # Extract body content from template HTML
        # The templates are complete HTML documents, so we need to embed CSS in <head>
        if "<style>" in html_content or "</style>" in html_content:
            # Template already has style tags, just ensure CSS is included
            if css_content and css_content not in html_content:
                # Insert CSS before closing </style> tag
                html_content = html_content.replace(
                    "</style>", f"\n{css_content}\n</style>", 1
                )
        elif "<head>" in html_content:
            # Insert CSS in head section
            style_block = f"<style>\n{css_content}\n</style>"
            html_content = html_content.replace(
                "</head>", f"{style_block}\n</head>", 1
            )
        else:
            # Wrap in complete HTML document
            template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV - LinkedIn Profile</title>
    <style>
{css_content}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            return template

        return html_content

    def export_with_assets(
        self,
        profile_data: Dict[str, Any],
        output_dir: str,
        filename: str = "cv.html"
    ) -> str:
        """Export CV as HTML with separate CSS file.

        Args:
            profile_data: Dictionary containing profile information
            output_dir: Directory where files should be saved
            filename: HTML filename (default: cv.html)

        Returns:
            Path to the generated HTML file

        Raises:
            PDFGenerationError: If export fails
        """
        try:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Validate theme
            if not self.template_manager.validate_theme(self.theme):
                raise PDFGenerationError(
                    f"Invalid theme: '{self.theme}'. "
                    f"Available themes: {', '.join(self.template_manager.get_available_themes())}"
                )

            # Get the HTML template
            html_content = self.template_manager.render_template(
                theme=self.theme,
                profile_data=profile_data,
                color_scheme=self.color_scheme,
                custom_colors=self.custom_colors,
            )

            # Create CSS directory
            css_dir = output_path / "css"
            css_dir.mkdir(exist_ok=True)

            # Copy CSS file
            css_source = self.templates_dir / self.theme / "style.css"
            if css_source.exists():
                css_dest = css_dir / f"{self.theme}.css"
                with open(css_source, "r", encoding="utf-8") as f:
                    css_content = f.read()
                with open(css_dest, "w", encoding="utf-8") as f:
                    f.write(css_content)

                # Update HTML to link to external CSS
                html_content = self._link_external_css(
                    html_content,
                    f"css/{self.theme}.css"
                )

            # Write HTML file
            html_file = output_path / filename
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            return str(html_file)

        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(
                f"Failed to export HTML with assets: {str(e)}",
                context={"output_dir": output_dir, "theme": self.theme},
            )

    def _link_external_css(self, html_content: str, css_path: str) -> str:
        """Update HTML to link to external CSS file.

        Args:
            html_content: HTML content
            css_path: Path to CSS file (relative to HTML)

        Returns:
            Updated HTML content
        """
        # Remove embedded CSS if present
        import re
        html_content = re.sub(
            r'<style>.*?</style>',
            f'<link rel="stylesheet" href="{css_path}">',
            html_content,
            flags=re.DOTALL,
            count=1
        )

        # If no <style> tag, add <link> in <head>
        if '<link rel="stylesheet"' not in html_content:
            html_content = html_content.replace(
                '</head>',
                f'    <link rel="stylesheet" href="{css_path}">\n</head>',
                1
            )

        return html_content
