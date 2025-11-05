"""Tests for security validator module."""
import pytest
from src.security.validator import SecurityValidator
from src.exceptions import ValidationError


class TestSecurityValidator:
    """Test SecurityValidator class."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return SecurityValidator()

    # LinkedIn URL validation tests
    def test_validate_valid_linkedin_urls(self, validator):
        """Test validation of valid LinkedIn URLs."""
        valid_urls = [
            "https://www.linkedin.com/in/username/",
            "https://linkedin.com/in/username/",
            "https://www.linkedin.com/in/user-name/",
            "https://www.linkedin.com/in/user_name123/",
            "https://www.linkedin.com/in/username",
        ]
        for url in valid_urls:
            result = validator.validate_linkedin_url(url)
            assert result == url, f"Failed to validate {url}"

    def test_validate_invalid_linkedin_urls(self, validator):
        """Test validation rejects invalid LinkedIn URLs."""
        invalid_urls = [
            "http://example.com",
            "https://facebook.com/in/username/",
            "https://www.linkedin.com/company/test/",
            "https://www.linkedin.com/pub/test/",
            "javascript:alert('xss')",
            "file:///etc/passwd",
            "../../../etc/passwd",
        ]
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                validator.validate_linkedin_url(url)
        
        # Test null byte URL separately (different error message)
        with pytest.raises(ValidationError, match="null bytes"):
            validator.validate_linkedin_url("https://www.linkedin.com/in/\x00username/")

    def test_validate_linkedin_url_too_long(self, validator):
        """Test URL length validation."""
        long_url = "https://www.linkedin.com/in/" + "a" * 3000
        with pytest.raises(ValidationError, match="URL exceeds maximum length"):
            validator.validate_linkedin_url(long_url)

    def test_sanitize_linkedin_url(self, validator):
        """Test URL sanitization."""
        url = "  https://www.linkedin.com/in/username/  "
        result = validator.sanitize_url(url)
        assert result == "https://www.linkedin.com/in/username/"

    # Filename validation tests
    def test_validate_valid_filenames(self, validator):
        """Test validation of valid filenames."""
        valid_names = [
            "document.pdf",
            "file_name.txt",
            "my-file-123.json",
            "test.tar.gz",
        ]
        for name in valid_names:
            result = validator.validate_filename(name)
            assert result == name, f"Failed to validate {name}"

    def test_validate_invalid_filenames(self, validator):
        """Test validation rejects invalid filenames."""
        invalid_names = [
            "file\x00.txt",  # null byte
            "../../../etc/passwd",  # path traversal
            "file/name.txt",  # path separator
            "file\\name.txt",  # backslash
            "CON",  # reserved name (Windows)
            "PRN.txt",  # reserved name (Windows)
            "..",  # dangerous component
        ]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                validator.validate_filename(name)

    def test_validate_filename_too_long(self, validator):
        """Test filename length validation."""
        long_name = "a" * 300 + ".txt"
        with pytest.raises(ValidationError, match="Filename exceeds maximum length"):
            validator.validate_filename(long_name)

    def test_sanitize_filename(self, validator):
        """Test filename sanitization."""
        result = validator.sanitize_filename("unsafe<>:\"|?*chars")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "?" not in result

    # Path validation tests
    def test_validate_valid_paths(self, validator):
        """Test validation of valid paths."""
        valid_paths = [
            "/home/user/document.pdf",
            "/var/log/app.log",
            "./output/file.txt",
            "../data/test.json",
            "C:\\Users\\test\\file.txt",  # Windows path
        ]
        for path in valid_paths:
            result = validator.validate_path(path)
            assert result == path, f"Failed to validate {path}"

    def test_validate_invalid_paths(self, validator):
        """Test validation rejects invalid paths."""
        invalid_paths = [
            "/path/with\x00nullbyte",  # null bytes
            "/etc/passwd",  # dangerous absolute path
            "/root/secret",  # dangerous absolute path
        ]
        for path in invalid_paths:
            with pytest.raises(ValidationError):
                validator.validate_path(path)
        
        # Test excessive traversal (more than 3 ..)
        with pytest.raises(ValidationError, match="excessive traversal"):
            validator.validate_path("/path/../../../../sensitive/file")

    def test_validate_path_too_long(self, validator):
        """Test path length validation."""
        # Create a path that's actually longer than MAX_PATH_LENGTH (4096)
        long_path = "/" + "a" * 5000
        with pytest.raises(ValidationError, match="Path exceeds maximum length"):
            validator.validate_path(long_path)

    def test_sanitize_path(self, validator):
        """Test path sanitization."""
        result = validator.sanitize_path("  /path/to/file.txt  ")
        assert result == "/path/to/file.txt"

    # Hex color validation tests
    def test_validate_valid_hex_colors(self, validator):
        """Test validation of valid hex colors."""
        valid_colors = [
            "#000000",
            "#FFFFFF",
            "#123abc",
            "#ABC123",
            "#f5f5f5",
        ]
        for color in valid_colors:
            result = validator.validate_hex_color(color)
            assert result == color.lower(), f"Failed to validate {color}"

    def test_validate_invalid_hex_colors(self, validator):
        """Test validation rejects invalid hex colors."""
        invalid_colors = [
            "000000",  # missing #
            "#00000",  # too short
            "#0000000",  # too long
            "#GGGGGG",  # invalid characters
            "rgb(0,0,0)",  # wrong format
            "#12 34 56",  # spaces
        ]
        for color in invalid_colors:
            with pytest.raises(ValidationError, match="Invalid hex color format"):
                validator.validate_hex_color(color)

    def test_sanitize_hex_color(self, validator):
        """Test hex color sanitization."""
        result = validator.sanitize_hex_color("  #ABC123  ")
        assert result == "#abc123"

    # Username validation tests
    def test_validate_valid_usernames(self, validator):
        """Test validation of valid usernames."""
        valid_usernames = [
            "john_doe",
            "user-123",
            "user.name",
            "test",
        ]
        for username in valid_usernames:
            result = validator.validate_username(username)
            assert result == username, f"Failed to validate {username}"

    def test_validate_invalid_usernames(self, validator):
        """Test validation rejects invalid usernames."""
        invalid_usernames = [
            "user\x00name",  # null byte
            "../admin",  # path traversal
            "user/name",  # path separator
            "a" * 150,  # too long
        ]
        for username in invalid_usernames:
            with pytest.raises(ValidationError):
                validator.validate_username(username)

    def test_sanitize_username(self, validator):
        """Test username sanitization."""
        result = validator.sanitize_username("  User Name!@#  ")
        assert result == "user_name"
        assert result.islower()
        assert " " not in result

    # validate_all_inputs tests
    def test_validate_all_inputs_valid(self, validator):
        """Test validate_all_inputs with all valid inputs."""
        result = validator.validate_all_inputs(
            url="https://www.linkedin.com/in/test/",
            filename="output.pdf",
            path="/home/user/output",
            color_primary="#2563eb",
            color_accent="#f59e0b",
            username="testuser",
        )
        assert result["url"] == "https://www.linkedin.com/in/test/"
        assert result["filename"] == "output.pdf"
        assert result["path"] == "/home/user/output"
        assert result["color_primary"] == "#2563eb"
        assert result["color_accent"] == "#f59e0b"
        assert result["username"] == "testuser"

    def test_validate_all_inputs_with_invalid(self, validator):
        """Test validate_all_inputs with some invalid inputs."""
        with pytest.raises(ValidationError, match="Multiple validation errors"):
            validator.validate_all_inputs(
                url="https://facebook.com/user",
                filename="file\x00.txt",
                color_primary="#GGGGGG",
            )

    def test_validate_all_inputs_empty(self, validator):
        """Test validate_all_inputs with no inputs."""
        result = validator.validate_all_inputs()
        assert result == {}

    def test_validate_all_inputs_partial(self, validator):
        """Test validate_all_inputs with partial inputs."""
        result = validator.validate_all_inputs(
            url="https://www.linkedin.com/in/test/",
            color_primary="#123456",
        )
        assert result["url"] == "https://www.linkedin.com/in/test/"
        assert result["color_primary"] == "#123456"
        assert "filename" not in result
        assert "path" not in result

    # Edge cases
    def test_unicode_handling(self, validator):
        """Test handling of unicode characters."""
        # Unicode in URL should be accepted
        url = "https://www.linkedin.com/in/名前/"
        result = validator.validate_linkedin_url(url)
        assert result == url

        # Unicode in filename
        filename = "résumé.pdf"
        result = validator.validate_filename(filename)
        assert result == filename

    def test_special_characters_in_linkedin_url(self, validator):
        """Test special characters in LinkedIn URLs."""
        valid_urls = [
            "https://www.linkedin.com/in/user-name/",
            "https://www.linkedin.com/in/user_name/",
        ]
        for url in valid_urls:
            result = validator.validate_linkedin_url(url)
            assert result == url
        
        # Dot is not allowed in LinkedIn usernames
        with pytest.raises(ValidationError):
            validator.validate_linkedin_url("https://www.linkedin.com/in/user.name/")

    def test_empty_string_validation(self, validator):
        """Test validation of empty strings."""
        with pytest.raises(ValidationError):
            validator.validate_linkedin_url("")
        
        with pytest.raises(ValidationError):
            validator.validate_filename("")
        
        with pytest.raises(ValidationError):
            validator.validate_hex_color("")
