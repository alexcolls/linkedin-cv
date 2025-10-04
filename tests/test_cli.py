"""Tests for CLI interface."""
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from src.cli import main


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "LinkedIn profile URL" in result.output
    assert "--output-dir" in result.output
    assert "--template" in result.output


def test_cli_missing_url(runner):
    """Test CLI without required URL argument."""
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert "Missing argument" in result.output or "Error" in result.output


def test_cli_invalid_url(runner):
    """Test CLI with invalid URL."""
    with patch("src.cli.generate_cv", new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = ValueError("Invalid LinkedIn profile URL")

        result = runner.invoke(main, ["https://invalid-url.com"])
        assert result.exit_code != 0


def test_cli_with_output_dir(runner, tmp_path):
    """Test CLI with custom output directory."""
    output_dir = tmp_path / "custom_output"

    with patch("src.cli.generate_cv", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = None

        result = runner.invoke(
            main,
            [
                "https://www.linkedin.com/in/johndoe/",
                "--output-dir",
                str(output_dir),
            ],
        )

        # Output directory should be created
        assert output_dir.exists()


def test_cli_with_template(runner, tmp_path):
    """Test CLI with custom template."""
    template_file = tmp_path / "custom_template.html"
    template_file.write_text("<html><body>{{ name }}</body></html>")

    with patch("src.cli.generate_cv", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = None

        result = runner.invoke(
            main,
            [
                "https://www.linkedin.com/in/johndoe/",
                "--template",
                str(template_file),
            ],
        )

        # Should not error
        assert result.exit_code == 0


def test_cli_debug_mode(runner):
    """Test CLI with debug flag."""
    with patch("src.cli.generate_cv", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = None

        result = runner.invoke(
            main,
            ["https://www.linkedin.com/in/johndoe/", "--debug"],
        )

        assert result.exit_code == 0


def test_cli_no_headless_mode(runner):
    """Test CLI with --no-headless flag."""
    with patch("src.cli.generate_cv", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = None

        result = runner.invoke(
            main,
            ["https://www.linkedin.com/in/johndoe/", "--no-headless"],
        )

        assert result.exit_code == 0


def test_cli_keyboard_interrupt(runner):
    """Test CLI handles keyboard interrupt gracefully."""
    with patch("src.cli.generate_cv", new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = KeyboardInterrupt()

        result = runner.invoke(main, ["https://www.linkedin.com/in/johndoe/"])

        # Should exit cleanly
        assert result.exit_code == 0
        assert "cancelled" in result.output.lower() or "interrupt" in result.output.lower()
