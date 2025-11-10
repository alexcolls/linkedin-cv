"""Tests for HTML exporter."""
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.exceptions import PDFGenerationError
from src.exporters.html_exporter import HTMLExporter
from src.pdf.template_manager import ColorScheme


@pytest.fixture
def sample_profile_data():
    """Create sample profile data."""
    return {
        'name': 'John Doe',
        'headline': 'Software Engineer',
        'about': 'Experienced developer',
        'experience': [
            {
                'title': 'Senior Engineer',
                'company': 'Tech Corp',
                'duration': '2020-Present',
                'description': 'Built amazing things'
            }
        ],
        'education': [
            {
                'school': 'University',
                'degree': 'BS Computer Science',
                'year': '2018'
            }
        ],
        'skills': ['Python', 'JavaScript', 'Docker']
    }


@pytest.fixture
def html_exporter():
    """Create HTML exporter instance."""
    return HTMLExporter(theme="modern")


def test_html_exporter_init():
    """Test HTML exporter initialization."""
    color_scheme = ColorScheme(
        primary="#ff0000",
        secondary="#00ff00",
        accent="#0000ff",
        text_primary="#000000",
        text_secondary="#333333",
        text_muted="#666666",
        background="#ffffff",
        background_light="#f9f9f9",
        border="#cccccc"
    )
    exporter = HTMLExporter(
        theme="executive",
        color_scheme=color_scheme,
        custom_colors={"primary": "#ffffff"}
    )
    
    assert exporter.theme == "executive"
    assert exporter.color_scheme is not None
    assert exporter.custom_colors == {"primary": "#ffffff"}
    assert exporter.template_manager is not None


def test_html_exporter_default_theme():
    """Test HTML exporter with default theme."""
    exporter = HTMLExporter()
    assert exporter.theme == "modern"
    assert exporter.color_scheme is None
    assert exporter.custom_colors is None


@patch('src.exporters.html_exporter.Path.exists')
@patch('src.exporters.html_exporter.Path.mkdir')
@patch('builtins.open', new_callable=mock_open)
def test_export_success(mock_file, mock_mkdir, mock_exists, html_exporter, sample_profile_data, tmp_path):
    """Test successful HTML export."""
    mock_exists.return_value = True
    
    # Mock template manager
    with patch.object(html_exporter.template_manager, 'validate_theme', return_value=True), \
         patch.object(html_exporter.template_manager, 'render_template') as mock_render, \
         patch('builtins.open', mock_open(read_data="body { color: black; }")) as mock_css:
        
        mock_render.return_value = "<html><head></head><body>Test CV</body></html>"
        
        output_path = tmp_path / "cv.html"
        html_exporter.export(sample_profile_data, str(output_path))
        
        # Verify template was rendered
        mock_render.assert_called_once_with(
            theme="modern",
            profile_data=sample_profile_data,
            color_scheme=None,
            custom_colors=None
        )


def test_export_invalid_theme(html_exporter, sample_profile_data, tmp_path):
    """Test export with invalid theme."""
    html_exporter.theme = "nonexistent"
    
    with patch.object(html_exporter.template_manager, 'validate_theme', return_value=False), \
         patch.object(html_exporter.template_manager, 'get_available_themes', return_value=['modern', 'executive']):
        
        output_path = tmp_path / "cv.html"
        
        with pytest.raises(PDFGenerationError, match="Invalid theme"):
            html_exporter.export(sample_profile_data, str(output_path))


@patch('src.exporters.html_exporter.Path.mkdir')
@patch('builtins.open', new_callable=mock_open)
def test_export_creates_output_directory(mock_file, mock_mkdir, html_exporter, sample_profile_data, tmp_path):
    """Test that export creates output directory."""
    with patch.object(html_exporter.template_manager, 'validate_theme', return_value=True), \
         patch.object(html_exporter.template_manager, 'render_template', return_value="<html></html>"), \
         patch('src.exporters.html_exporter.Path.exists', return_value=False):
        
        output_path = tmp_path / "subdir" / "cv.html"
        html_exporter.export(sample_profile_data, str(output_path))
        
        # Verify mkdir was called with parents=True
        assert mock_mkdir.called


def test_export_template_rendering_error(html_exporter, sample_profile_data, tmp_path):
    """Test handling of template rendering errors."""
    with patch.object(html_exporter.template_manager, 'validate_theme', return_value=True), \
         patch.object(html_exporter.template_manager, 'render_template', side_effect=Exception("Render failed")):
        
        output_path = tmp_path / "cv.html"
        
        with pytest.raises(PDFGenerationError, match="Failed to export HTML"):
            html_exporter.export(sample_profile_data, str(output_path))


def test_create_standalone_html_with_style_tags():
    """Test creating standalone HTML when style tags exist."""
    exporter = HTMLExporter()
    
    html_content = """<html>
<head>
    <style>
        body { margin: 0; }
    </style>
</head>
<body>Test</body>
</html>"""
    
    css_content = "p { color: blue; }"
    
    result = exporter._create_standalone_html(html_content, css_content)
    
    assert css_content in result
    assert "body { margin: 0; }" in result


def test_create_standalone_html_with_head_no_style():
    """Test creating standalone HTML with head but no style tags."""
    exporter = HTMLExporter()
    
    html_content = """<html>
<head>
    <title>CV</title>
</head>
<body>Test</body>
</html>"""
    
    css_content = "body { padding: 0; }"
    
    result = exporter._create_standalone_html(html_content, css_content)
    
    assert "<style>" in result
    assert css_content in result
    assert "</style>" in result


def test_create_standalone_html_no_head():
    """Test creating standalone HTML when no head tag exists."""
    exporter = HTMLExporter()
    
    html_content = "<div>Test Content</div>"
    css_content = "div { font-size: 14px; }"
    
    result = exporter._create_standalone_html(html_content, css_content)
    
    assert "<!DOCTYPE html>" in result
    assert "<html lang=\"en\">" in result
    assert "<head>" in result
    assert css_content in result
    assert html_content in result


def test_create_standalone_html_empty_css():
    """Test creating standalone HTML with empty CSS."""
    exporter = HTMLExporter()
    
    html_content = """<html>
<head></head>
<body>Test</body>
</html>"""
    
    css_content = ""
    
    result = exporter._create_standalone_html(html_content, css_content)
    
    assert "<html>" in result
    assert "Test" in result


@patch('src.exporters.html_exporter.Path.mkdir')
@patch('src.exporters.html_exporter.Path.exists')
@patch('builtins.open', new_callable=mock_open, read_data="body { background: white; }")
def test_export_with_assets_success(mock_file, mock_exists, mock_mkdir, html_exporter, sample_profile_data, tmp_path):
    """Test export with separate CSS file."""
    mock_exists.return_value = True
    
    with patch.object(html_exporter.template_manager, 'validate_theme', return_value=True), \
         patch.object(html_exporter.template_manager, 'render_template') as mock_render:
        
        mock_render.return_value = "<html><head><style>old css</style></head><body>Test</body></html>"
        
        result = html_exporter.export_with_assets(
            sample_profile_data,
            str(tmp_path),
            filename="test.html"
        )
        
        assert result is not None
        assert "test.html" in result


def test_export_with_assets_invalid_theme(html_exporter, sample_profile_data, tmp_path):
    """Test export with assets when theme is invalid."""
    html_exporter.theme = "invalid"
    
    with patch.object(html_exporter.template_manager, 'validate_theme', return_value=False), \
         patch.object(html_exporter.template_manager, 'get_available_themes', return_value=['modern']):
        
        with pytest.raises(PDFGenerationError, match="Invalid theme"):
            html_exporter.export_with_assets(sample_profile_data, str(tmp_path))


def test_export_with_assets_no_css_file(html_exporter, sample_profile_data, tmp_path):
    """Test export with assets when CSS file doesn't exist."""
    with patch.object(html_exporter.template_manager, 'validate_theme', return_value=True), \
         patch.object(html_exporter.template_manager, 'render_template', return_value="<html></html>"), \
         patch('src.exporters.html_exporter.Path.exists', return_value=False), \
         patch('src.exporters.html_exporter.Path.mkdir'), \
         patch('builtins.open', mock_open()):
        
        result = html_exporter.export_with_assets(sample_profile_data, str(tmp_path))
        assert result is not None


def test_export_with_assets_rendering_error(html_exporter, sample_profile_data, tmp_path):
    """Test export with assets when rendering fails."""
    with patch.object(html_exporter.template_manager, 'validate_theme', return_value=True), \
         patch.object(html_exporter.template_manager, 'render_template', side_effect=Exception("Render error")):
        
        with pytest.raises(PDFGenerationError, match="Failed to export HTML with assets"):
            html_exporter.export_with_assets(sample_profile_data, str(tmp_path))


def test_link_external_css_with_style_tag():
    """Test linking external CSS when style tag exists."""
    exporter = HTMLExporter()
    
    html_content = """<html>
<head>
    <style>
        body { margin: 0; }
    </style>
</head>
<body>Test</body>
</html>"""
    
    result = exporter._link_external_css(html_content, "css/style.css")
    
    assert '<link rel="stylesheet" href="css/style.css">' in result
    assert "<style>" not in result


def test_link_external_css_no_style_tag():
    """Test linking external CSS when no style tag exists."""
    exporter = HTMLExporter()
    
    html_content = """<html>
<head>
    <title>CV</title>
</head>
<body>Test</body>
</html>"""
    
    result = exporter._link_external_css(html_content, "css/theme.css")
    
    assert '<link rel="stylesheet" href="css/theme.css">' in result
    assert result.count('<link rel="stylesheet"') == 1


def test_link_external_css_multiple_style_tags():
    """Test linking external CSS with multiple style tags."""
    exporter = HTMLExporter()
    
    html_content = """<html>
<head>
    <style>body { margin: 0; }</style>
    <style>p { padding: 0; }</style>
</head>
<body>Test</body>
</html>"""
    
    result = exporter._link_external_css(html_content, "css/main.css")
    
    # Only first style tag should be replaced
    assert result.count('<link rel="stylesheet"') >= 1


def test_export_with_custom_colors(sample_profile_data, tmp_path):
    """Test export with custom color overrides."""
    custom_colors = {"primary": "#ff5733", "accent": "#33ff57"}
    exporter = HTMLExporter(theme="modern", custom_colors=custom_colors)
    
    with patch.object(exporter.template_manager, 'validate_theme', return_value=True), \
         patch.object(exporter.template_manager, 'render_template') as mock_render, \
         patch('src.exporters.html_exporter.Path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data="css")):
        
        mock_render.return_value = "<html></html>"
        
        output_path = tmp_path / "cv.html"
        exporter.export(sample_profile_data, str(output_path))
        
        # Verify custom colors were passed
        call_args = mock_render.call_args
        assert call_args[1]['custom_colors'] == custom_colors


def test_export_with_color_scheme(sample_profile_data, tmp_path):
    """Test export with custom color scheme."""
    color_scheme = ColorScheme(
        primary="#111111",
        secondary="#222222",
        accent="#333333",
        text_primary="#000000",
        text_secondary="#555555",
        text_muted="#888888",
        background="#ffffff",
        background_light="#fafafa",
        border="#dddddd"
    )
    exporter = HTMLExporter(theme="executive", color_scheme=color_scheme)
    
    with patch.object(exporter.template_manager, 'validate_theme', return_value=True), \
         patch.object(exporter.template_manager, 'render_template') as mock_render, \
         patch('src.exporters.html_exporter.Path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data="css")):
        
        mock_render.return_value = "<html></html>"
        
        output_path = tmp_path / "cv.html"
        exporter.export(sample_profile_data, str(output_path))
        
        # Verify color scheme was passed
        call_args = mock_render.call_args
        assert call_args[1]['color_scheme'] == color_scheme


def test_export_all_themes(sample_profile_data, tmp_path):
    """Test export with all available themes."""
    themes = ["modern", "creative", "executive", "classic"]
    
    for theme in themes:
        exporter = HTMLExporter(theme=theme)
        
        with patch.object(exporter.template_manager, 'validate_theme', return_value=True), \
             patch.object(exporter.template_manager, 'render_template', return_value="<html></html>"), \
             patch('src.exporters.html_exporter.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="css")):
            
            output_path = tmp_path / f"cv_{theme}.html"
            exporter.export(sample_profile_data, str(output_path))
            
            # Should complete without errors
            assert True


def test_templates_dir_path():
    """Test that templates directory path is correctly set."""
    exporter = HTMLExporter()
    
    assert exporter.templates_dir is not None
    assert "templates" in str(exporter.templates_dir)
    assert exporter.templates_dir.parts[-2:] == ('pdf', 'templates')
