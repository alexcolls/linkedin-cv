"""Tests for template manager and theme system."""
import pytest
from pathlib import Path

from src.pdf.template_manager import ColorScheme, TemplateManager, TemplateTheme


class TestColorScheme:
    """Test ColorScheme dataclass."""
    
    def test_default_modern(self):
        """Test Modern color scheme defaults."""
        scheme = ColorScheme.default_modern()
        assert scheme.primary == "#2563eb"
        assert scheme.accent == "#f59e0b"
        assert scheme.background == "#ffffff"
    
    def test_default_creative(self):
        """Test Creative color scheme defaults."""
        scheme = ColorScheme.default_creative()
        assert scheme.primary == "#7c3aed"
        assert scheme.secondary == "#ec4899"
        assert scheme.accent == "#10b981"
    
    def test_default_executive(self):
        """Test Executive color scheme defaults."""
        scheme = ColorScheme.default_executive()
        assert scheme.primary == "#1e3a8a"
        assert scheme.secondary == "#881337"
        assert scheme.accent == "#b45309"
    
    def test_default_classic(self):
        """Test Classic color scheme defaults."""
        scheme = ColorScheme.default_classic()
        assert scheme.primary == "#0a66c2"
        assert scheme.secondary == "#70b5f9"
        assert scheme.accent == "#057642"
    
    def test_to_css_vars(self):
        """Test conversion to CSS variables."""
        scheme = ColorScheme.default_modern()
        css_vars = scheme.to_css_vars()
        
        assert "--primary-color" in css_vars
        assert css_vars["--primary-color"] == "#2563eb"
        assert "--accent-color" in css_vars
        assert len(css_vars) == 9  # All color properties


class TestTemplateTheme:
    """Test TemplateTheme enum."""
    
    def test_theme_values(self):
        """Test theme enum values."""
        assert TemplateTheme.MODERN == "modern"
        assert TemplateTheme.CREATIVE == "creative"
        assert TemplateTheme.EXECUTIVE == "executive"
        assert TemplateTheme.CLASSIC == "classic"
    
    def test_all_themes_defined(self):
        """Test all expected themes are defined."""
        themes = list(TemplateTheme)
        assert len(themes) == 4
        assert TemplateTheme.MODERN in themes


class TestTemplateManager:
    """Test TemplateManager class."""
    
    def test_init_default_path(self):
        """Test initialization with default templates path."""
        manager = TemplateManager()
        assert manager.templates_dir.exists()
        assert manager.templates_dir.name == "templates"
    
    def test_init_custom_path(self, tmp_path):
        """Test initialization with custom templates path."""
        custom_path = tmp_path / "custom_templates"
        custom_path.mkdir()
        manager = TemplateManager(custom_path)
        assert manager.templates_dir == custom_path
    
    def test_get_available_themes(self):
        """Test getting list of available themes."""
        manager = TemplateManager()
        themes = manager.get_available_themes()
        
        assert isinstance(themes, list)
        assert len(themes) == 4
        assert "modern" in themes
        assert "creative" in themes
        assert "executive" in themes
        assert "classic" in themes
    
    def test_get_theme_path(self):
        """Test getting path to theme directory."""
        manager = TemplateManager()
        theme_path = manager.get_theme_path("modern")
        
        assert isinstance(theme_path, Path)
        assert theme_path.name == "modern"
        assert "templates" in str(theme_path)
    
    def test_get_default_colors(self):
        """Test getting default colors for each theme."""
        manager = TemplateManager()
        
        # Test each theme
        modern = manager.get_default_colors("modern")
        assert isinstance(modern, ColorScheme)
        assert modern.primary == "#2563eb"
        
        creative = manager.get_default_colors("creative")
        assert creative.primary == "#7c3aed"
        
        executive = manager.get_default_colors("executive")
        assert executive.primary == "#1e3a8a"
        
        classic = manager.get_default_colors("classic")
        assert classic.primary == "#0a66c2"
    
    def test_validate_theme_valid(self):
        """Test validation of valid themes."""
        manager = TemplateManager()
        
        assert manager.validate_theme("modern") is True
        assert manager.validate_theme("creative") is True
        assert manager.validate_theme("executive") is True
        assert manager.validate_theme("classic") is True
    
    def test_validate_theme_invalid(self):
        """Test validation of invalid themes."""
        manager = TemplateManager()
        
        assert manager.validate_theme("nonexistent") is False
        assert manager.validate_theme("invalid") is False
        assert manager.validate_theme("") is False
    
    def test_render_template_basic(self):
        """Test basic template rendering."""
        manager = TemplateManager()
        profile_data = {
            "name": "John Doe",
            "headline": "Software Engineer",
            "location": "San Francisco",
        }
        
        html = manager.render_template("modern", profile_data)
        
        assert isinstance(html, str)
        assert "John Doe" in html
        assert "Software Engineer" in html
        assert "San Francisco" in html
    
    def test_render_template_with_custom_colors(self):
        """Test rendering with custom color overrides."""
        manager = TemplateManager()
        profile_data = {"name": "Jane Smith"}
        custom_colors = {"primary": "#ff0000", "accent": "#00ff00"}
        
        html = manager.render_template(
            "modern",
            profile_data,
            custom_colors=custom_colors
        )
        
        assert isinstance(html, str)
        assert "Jane Smith" in html
    
    def test_render_template_with_color_scheme(self):
        """Test rendering with custom ColorScheme."""
        manager = TemplateManager()
        profile_data = {"name": "Bob Johnson"}
        custom_scheme = ColorScheme(
            primary="#123456",
            secondary="#234567",
            accent="#345678",
            text_primary="#000000",
            text_secondary="#333333",
            text_muted="#666666",
            background="#ffffff",
            background_light="#f5f5f5",
            border="#dddddd"
        )
        
        html = manager.render_template(
            "modern",
            profile_data,
            color_scheme=custom_scheme
        )
        
        assert isinstance(html, str)
        assert "Bob Johnson" in html
    
    def test_render_all_themes(self):
        """Test that all themes can be rendered."""
        manager = TemplateManager()
        profile_data = {
            "name": "Test User",
            "headline": "Test Headline",
        }
        
        for theme in manager.get_available_themes():
            html = manager.render_template(theme, profile_data)
            assert isinstance(html, str)
            assert len(html) > 0
            assert "Test User" in html


class TestTemplateManagerIntegration:
    """Integration tests for template manager."""
    
    def test_full_profile_rendering(self):
        """Test rendering with complete profile data."""
        manager = TemplateManager()
        profile_data = {
            "name": "John Doe",
            "headline": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "about": "Experienced software engineer...",
            "experience": [
                {
                    "title": "Senior Engineer",
                    "company": "Tech Corp",
                    "duration": "2020 - Present",
                    "description": "Led development team...",
                    "skills": ["Python", "AWS", "Docker"]
                }
            ],
            "education": [
                {
                    "institution": "University",
                    "degree": "BS Computer Science",
                    "duration": "2016 - 2020"
                }
            ],
            "skills": [
                {"name": "Python", "endorsements": 50},
                {"name": "JavaScript", "endorsements": 30}
            ]
        }
        
        for theme in ["modern", "creative", "executive", "classic"]:
            html = manager.render_template(theme, profile_data)
            
            # Verify content is present
            assert "John Doe" in html
            assert "Senior Software Engineer" in html
            assert "Tech Corp" in html
            assert "University" in html
            assert "Python" in html
    
    def test_theme_specific_features(self):
        """Test that theme-specific features are rendered."""
        manager = TemplateManager()
        profile_data = {
            "name": "Test User",
            "skills": [{"name": "Skill1"}, {"name": "Skill2"}]
        }
        
        # Modern should have skills section
        modern_html = manager.render_template("modern", profile_data)
        assert "skill-list" in modern_html or "Top Skills" in modern_html
        
        # Creative should have skill badges
        creative_html = manager.render_template("creative", profile_data)
        assert "skill-badge" in creative_html or "Top Skills" in creative_html
