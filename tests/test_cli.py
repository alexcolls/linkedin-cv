"""Tests for CLI module."""
import pytest
from click.testing import CliRunner
from src.cli import main, normalize_profile_url


class TestCLI:
    """Test suite for CLI functions."""

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'LinkedIn profile URL' in result.output or 'PROFILE_URL' in result.output

    def test_normalize_profile_url_full(self):
        """Test URL normalization with full URL."""
        url = "https://www.linkedin.com/in/john-doe/"
        result = normalize_profile_url(url)
        assert result == "https://www.linkedin.com/in/john-doe"

    def test_normalize_profile_url_username_only(self):
        """Test URL normalization with username only."""
        username = "john-doe"
        result = normalize_profile_url(username)
        assert result == "https://www.linkedin.com/in/john-doe/"

    def test_normalize_profile_url_removes_trailing_slash(self):
        """Test URL normalization removes trailing slash."""
        url = "https://www.linkedin.com/in/john-doe/"
        result = normalize_profile_url(url)
        assert not result.endswith('/')

    def test_normalize_profile_url_with_at_symbol(self):
        """Test URL normalization with @ symbol."""
        username = "@john-doe"
        result = normalize_profile_url(username)
        assert '@' not in result
        assert "john-doe" in result

    def test_normalize_profile_url_partial(self):
        """Test URL normalization with partial URL."""
        url = "linkedin.com/in/john-doe"
        result = normalize_profile_url(url)
        assert result.startswith("https://")

    def test_cli_version_exists(self):
        """Test that CLI module can be imported."""
        from src import cli
        assert cli is not None

    def test_cli_main_function_exists(self):
        """Test that main function exists."""
        assert callable(main)

    def test_cli_no_banner_flag(self):
        """Test CLI with --no-banner flag."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help', '--no-banner'])
        
        # Should execute without error
        assert result.exit_code == 0


class TestCLIEdgeCases:
    """Test edge cases for CLI."""

    def test_normalize_empty_string(self):
        """Test normalization with empty string."""
        result = normalize_profile_url("")
        assert result == "https://www.linkedin.com/in//"

    def test_normalize_whitespace(self):
        """Test normalization with whitespace."""
        result = normalize_profile_url("  john-doe  ")
        assert result.strip() == "https://www.linkedin.com/in/john-doe/"

    def test_normalize_complex_username(self):
        """Test normalization with complex username."""
        username = "john-doe-123"
        result = normalize_profile_url(username)
        assert "john-doe-123" in result


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_cli_with_invalid_option(self):
        """Test CLI with invalid option."""
        runner = CliRunner()
        result = runner.invoke(main, ['--invalid-option'])
        
        # Should show error
        assert result.exit_code != 0

    def test_cli_debug_flag(self):
        """Test CLI with debug flag."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help', '--debug'])
        
        # Should execute
        assert result.exit_code == 0

    def test_cli_json_export_flag_exists(self):
        """Test that --json flag exists."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        # Help should mention JSON option
        assert '--json' in result.output or 'json' in result.output.lower()
