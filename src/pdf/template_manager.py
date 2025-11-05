"""Template manager for handling multiple PDF themes.

This module provides functionality to manage and render different CV templates
with customizable themes and color schemes.
"""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateTheme(str, Enum):
    """Available template themes."""
    
    MODERN = "modern"
    CREATIVE = "creative"
    EXECUTIVE = "executive"
    CLASSIC = "classic"  # Original LinkedIn-style template


@dataclass
class ColorScheme:
    """Color scheme configuration for templates."""
    
    primary: str
    secondary: str
    accent: str
    text_primary: str
    text_secondary: str
    text_muted: str
    background: str
    background_light: str
    border: str
    
    @classmethod
    def default_modern(cls) -> "ColorScheme":
        """Modern Professional color scheme - deep blues and soft grays."""
        return cls(
            primary="#2563eb",  # Deep blue
            secondary="#60a5fa",  # Light blue
            accent="#f59e0b",  # Gold
            text_primary="#111827",  # Almost black
            text_secondary="#4b5563",  # Dark gray
            text_muted="#9ca3af",  # Light gray
            background="#ffffff",  # White
            background_light="#f9fafb",  # Off-white
            border="#e5e7eb",  # Border gray
        )
    
    @classmethod
    def default_creative(cls) -> "ColorScheme":
        """Creative Bold color scheme - vibrant colors."""
        return cls(
            primary="#7c3aed",  # Purple
            secondary="#ec4899",  # Pink
            accent="#10b981",  # Green
            text_primary="#18181b",  # Near black
            text_secondary="#52525b",  # Zinc gray
            text_muted="#a1a1aa",  # Light zinc
            background="#ffffff",  # White
            background_light="#fafafa",  # Off-white
            border="#d4d4d8",  # Border zinc
        )
    
    @classmethod
    def default_executive(cls) -> "ColorScheme":
        """Executive Elegant color scheme - navy and burgundy."""
        return cls(
            primary="#1e3a8a",  # Navy blue
            secondary="#881337",  # Burgundy
            accent="#b45309",  # Gold/bronze
            text_primary="#1c1917",  # Stone black
            text_secondary="#57534e",  # Stone gray
            text_muted="#a8a29e",  # Light stone
            background="#ffffff",  # White
            background_light="#fafaf9",  # Cream
            border="#e7e5e4",  # Stone border
        )
    
    @classmethod
    def default_classic(cls) -> "ColorScheme":
        """Classic LinkedIn-style color scheme."""
        return cls(
            primary="#0a66c2",  # LinkedIn blue
            secondary="#70b5f9",  # Light blue
            accent="#057642",  # Green
            text_primary="#000000",  # Black
            text_secondary="#666666",  # Gray
            text_muted="#999999",  # Light gray
            background="#ffffff",  # White
            background_light="#f8f9fa",  # Off-white
            border="#e0e0e0",  # Border gray
        )
    
    def to_css_vars(self) -> Dict[str, str]:
        """Convert color scheme to CSS custom properties."""
        return {
            "--primary-color": self.primary,
            "--secondary-color": self.secondary,
            "--accent-color": self.accent,
            "--text-primary": self.text_primary,
            "--text-secondary": self.text_secondary,
            "--text-muted": self.text_muted,
            "--background-white": self.background,
            "--background-light": self.background_light,
            "--border-color": self.border,
        }


class TemplateManager:
    """Manager for handling CV templates."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize template manager.
        
        Args:
            templates_dir: Path to templates directory (optional)
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        
        self.templates_dir = templates_dir
        self._setup_jinja_env()
    
    def _setup_jinja_env(self) -> None:
        """Setup Jinja2 environment."""
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Add custom filters
        self.env.filters["css_vars"] = self._css_vars_filter
    
    def _css_vars_filter(self, color_scheme: ColorScheme) -> str:
        """Convert color scheme to CSS variable declarations."""
        vars_dict = color_scheme.to_css_vars()
        css_lines = [f"    {key}: {value};" for key, value in vars_dict.items()]
        return "\n".join(css_lines)
    
    def get_available_themes(self) -> List[str]:
        """Get list of available template themes.
        
        Returns:
            List of theme names
        """
        return [theme.value for theme in TemplateTheme]
    
    def get_theme_path(self, theme: str) -> Path:
        """Get path to theme directory.
        
        Args:
            theme: Theme name
            
        Returns:
            Path to theme directory
        """
        return self.templates_dir / theme
    
    def get_default_colors(self, theme: str) -> ColorScheme:
        """Get default color scheme for a theme.
        
        Args:
            theme: Theme name
            
        Returns:
            Default color scheme for the theme
        """
        theme_enum = TemplateTheme(theme)
        
        if theme_enum == TemplateTheme.MODERN:
            return ColorScheme.default_modern()
        elif theme_enum == TemplateTheme.CREATIVE:
            return ColorScheme.default_creative()
        elif theme_enum == TemplateTheme.EXECUTIVE:
            return ColorScheme.default_executive()
        else:  # CLASSIC
            return ColorScheme.default_classic()
    
    def render_template(
        self,
        theme: str,
        profile_data: Dict[str, Any],
        color_scheme: Optional[ColorScheme] = None,
        custom_colors: Optional[Dict[str, str]] = None,
    ) -> str:
        """Render CV template with profile data.
        
        Args:
            theme: Theme name
            profile_data: Profile data dictionary
            color_scheme: Custom color scheme (optional)
            custom_colors: Custom color overrides (optional)
            
        Returns:
            Rendered HTML string
        """
        # Get default colors if not provided
        if color_scheme is None:
            color_scheme = self.get_default_colors(theme)
        
        # Apply custom color overrides
        if custom_colors:
            for key, value in custom_colors.items():
                if hasattr(color_scheme, key):
                    setattr(color_scheme, key, value)
        
        # Load template
        template_path = f"{theme}/cv_template.html"
        template = self.env.get_template(template_path)
        
        # Prepare context
        context = {
            **profile_data,
            "colors": color_scheme,
            "theme": theme,
        }
        
        # Render template
        return template.render(context)
    
    def validate_theme(self, theme: str) -> bool:
        """Validate if a theme exists.
        
        Args:
            theme: Theme name
            
        Returns:
            True if theme is valid
        """
        try:
            TemplateTheme(theme)
            theme_dir = self.get_theme_path(theme)
            template_file = theme_dir / "cv_template.html"
            return template_file.exists()
        except (ValueError, FileNotFoundError):
            return False
