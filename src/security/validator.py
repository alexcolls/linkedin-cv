"""Input validation and sanitization for security."""
import re
from pathlib import Path
from typing import Optional, Dict
from urllib.parse import urlparse

from src.exceptions import ValidationError


class SecurityValidator:
    """Validate and sanitize inputs for security."""

    # LinkedIn URL patterns
    LINKEDIN_URL_PATTERN = re.compile(
        r'^https?://(www\.)?linkedin\.com/in/[\w\-\u0100-\uFFFF]+/?(\?.*)?$',
        re.IGNORECASE
    )

    # Safe filename characters (including unicode)
    SAFE_FILENAME_PATTERN = re.compile(r'^[\w\-\.]+$', re.UNICODE)

    # Hex color pattern
    HEX_COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')

    # Maximum lengths
    MAX_URL_LENGTH = 2048
    MAX_FILENAME_LENGTH = 255
    MAX_PATH_LENGTH = 4096
    MAX_USERNAME_LENGTH = 100

    # Dangerous path components
    DANGEROUS_PATH_COMPONENTS = {
        '..',
        '~',
        '/etc',
        '/root',
        '/sys',
        '/proc',
        '/dev',
    }

    @classmethod
    def validate_linkedin_url(cls, url: str) -> str:
        """Validate LinkedIn profile URL.

        Args:
            url: URL to validate

        Returns:
            Validated URL

        Raises:
            ValidationError: If URL is invalid
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL must be a non-empty string", field="url")

        url = url.strip()

        # Check length
        if len(url) > cls.MAX_URL_LENGTH:
            raise ValidationError(
                f"URL exceeds maximum length of {cls.MAX_URL_LENGTH}",
                field="url"
            )

        # Check for null bytes
        if '\x00' in url:
            raise ValidationError("URL contains null bytes", field="url")

        # Check pattern
        if not cls.LINKEDIN_URL_PATTERN.match(url):
            raise ValidationError(
                "Invalid LinkedIn profile URL format",
                field="url"
            )

        # Parse and validate
        try:
            parsed = urlparse(url)
            
            # Must be HTTPS or HTTP
            if parsed.scheme not in ['http', 'https']:
                raise ValidationError(
                    "URL must use HTTP or HTTPS protocol",
                    field="url"
                )

            # Must be linkedin.com domain
            if 'linkedin.com' not in parsed.netloc.lower():
                raise ValidationError(
                    "URL must be from linkedin.com domain",
                    field="url"
                )

            return url

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Invalid URL format: {str(e)}", field="url")

    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """Sanitize URL by removing potentially dangerous components.

        Args:
            url: URL to sanitize

        Returns:
            Sanitized URL
        """
        url = url.strip()
        
        # Remove fragment identifiers
        if '#' in url:
            url = url.split('#')[0]

        return url

    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """Validate filename for security.

        Args:
            filename: Filename to validate

        Returns:
            Validated filename

        Raises:
            ValidationError: If filename is invalid
        """
        if not filename or not isinstance(filename, str):
            raise ValidationError("Filename must be a non-empty string", field="filename")

        filename = filename.strip()

        # Check length
        if len(filename) > cls.MAX_FILENAME_LENGTH:
            raise ValidationError(
                f"Filename exceeds maximum length of {cls.MAX_FILENAME_LENGTH}",
                field="filename"
            )

        # Check for null bytes
        if '\x00' in filename:
            raise ValidationError("Filename contains null bytes", field="filename")

        # Check for path separators
        if '/' in filename or '\\' in filename:
            raise ValidationError(
                "Filename cannot contain path separators",
                field="filename"
            )

        # Check for dangerous components
        if filename in ['.', '..']:
            raise ValidationError(
                f"Filename uses dangerous component: {filename}",
                field="filename"
            )

        # Check for reserved names (Windows)
        reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                   'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                   'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
        
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved:
            raise ValidationError(
                f"Filename uses reserved name: {name_without_ext}",
                field="filename"
            )

        return filename

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename by removing unsafe characters.

        Args:
            filename: Filename to sanitize

        Returns:
            Sanitized filename

        Raises:
            ValidationError: If filename is completely invalid
        """
        if not filename:
            raise ValidationError("Filename cannot be empty", field="filename")

        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')

        # Remove null bytes
        filename = filename.replace('\x00', '')

        # Keep only safe characters
        filename = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in filename)

        # Remove leading/trailing dots and underscores
        filename = filename.strip('._')

        # Ensure not empty after sanitization
        if not filename:
            raise ValidationError(
                "Filename becomes empty after sanitization",
                field="filename"
            )

        # Truncate if too long
        if len(filename) > cls.MAX_FILENAME_LENGTH:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            max_name_len = cls.MAX_FILENAME_LENGTH - len(ext) - 1 if ext else cls.MAX_FILENAME_LENGTH
            filename = name[:max_name_len] + ('.' + ext if ext else '')

        return filename

    @classmethod
    def validate_path(cls, path: str) -> str:
        """Validate file path for security.

        Args:
            path: Path to validate

        Returns:
            Validated path

        Raises:
            ValidationError: If path is invalid
        """
        if not path or not isinstance(path, str):
            raise ValidationError("Path must be a non-empty string", field="path")

        path = path.strip()

        # Check length
        if len(path) > cls.MAX_PATH_LENGTH:
            raise ValidationError(
                f"Path exceeds maximum length of {cls.MAX_PATH_LENGTH}",
                field="path"
            )

        # Check for null bytes
        if '\x00' in path:
            raise ValidationError("Path contains null bytes", field="path")

        # Check for excessive path traversal (too many ..)
        path_parts = path.replace('\\', '/').split('/')
        traversal_count = sum(1 for part in path_parts if part == '..')
        if traversal_count > 3:
            raise ValidationError(
                "Path contains excessive traversal attempts",
                field="path"
            )

        # Check for dangerous absolute paths
        path_lower = path.lower()
        dangerous_absolute = ['/etc', '/root', '/sys', '/proc', '/dev']
        if any(path_lower.startswith(d) for d in dangerous_absolute):
            raise ValidationError(
                f"Path attempts to access dangerous system directory",
                field="path"
            )

        return path

    @classmethod
    def sanitize_path(cls, path: str) -> str:
        """Sanitize path by stripping whitespace.

        Args:
            path: Path to sanitize

        Returns:
            Sanitized path
        """
        return path.strip()

    @classmethod
    def validate_hex_color(cls, color: str) -> str:
        """Validate hex color code.

        Args:
            color: Color code to validate

        Returns:
            Validated color code (lowercase)

        Raises:
            ValidationError: If color is invalid
        """
        if not color or not isinstance(color, str):
            raise ValidationError("Color must be a non-empty string", field="color")

        color = color.strip()

        if not cls.HEX_COLOR_PATTERN.match(color):
            raise ValidationError(
                "Invalid hex color format (expected #RRGGBB)",
                field="color"
            )

        return color.lower()

    @classmethod
    def sanitize_hex_color(cls, color: str) -> str:
        """Sanitize hex color code.

        Args:
            color: Color code to sanitize

        Returns:
            Sanitized color code (lowercase)

        Raises:
            ValidationError: If color is invalid
        """
        if not color:
            raise ValidationError("Color cannot be empty", field="color")

        color = color.strip()

        # Add # if missing
        if not color.startswith('#'):
            color = '#' + color

        # Convert to lowercase
        color = color.lower()

        # Validate
        if not cls.HEX_COLOR_PATTERN.match(color):
            raise ValidationError(
                "Invalid hex color format (expected #RRGGBB)",
                field="color"
            )

        return color

    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate LinkedIn username.

        Args:
            username: Username to validate

        Returns:
            Validated username

        Raises:
            ValidationError: If username is invalid
        """
        if not username or not isinstance(username, str):
            raise ValidationError("Username must be a non-empty string", field="username")

        username = username.strip()

        # Check length
        if len(username) > cls.MAX_USERNAME_LENGTH:
            raise ValidationError(
                f"Username exceeds maximum length of {cls.MAX_USERNAME_LENGTH}",
                field="username"
            )

        # Check for null bytes
        if '\x00' in username:
            raise ValidationError("Username contains null bytes", field="username")

        # Check for path separators
        if '/' in username or '\\' in username:
            raise ValidationError(
                "Username cannot contain path separators",
                field="username"
            )

        # Check for dangerous components
        if username in ['.', '..']:
            raise ValidationError(
                f"Username uses dangerous component: {username}",
                field="username"
            )

        return username

    @classmethod
    def sanitize_username(cls, username: str) -> str:
        """Sanitize LinkedIn username.

        Args:
            username: Username to sanitize

        Returns:
            Sanitized username (lowercase)

        Raises:
            ValidationError: If username is invalid
        """
        if not username:
            raise ValidationError("Username cannot be empty", field="username")

        # Remove whitespace and convert to lowercase
        username = username.strip().lower()

        # Replace spaces and special characters with underscore
        username = re.sub(r'[^\w\-]', '_', username)

        # Remove multiple consecutive underscores
        username = re.sub(r'_+', '_', username)

        # Strip leading/trailing underscores
        username = username.strip('_')

        # Truncate if too long
        if len(username) > cls.MAX_USERNAME_LENGTH:
            username = username[:cls.MAX_USERNAME_LENGTH]

        # Ensure not empty after sanitization
        if not username:
            raise ValidationError(
                "Username becomes empty after sanitization",
                field="username"
            )

        return username

    @classmethod
    def validate_all_inputs(
        cls,
        url: Optional[str] = None,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        color_primary: Optional[str] = None,
        color_accent: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Dict[str, str]:
        """Validate all inputs at once.

        Args:
            url: LinkedIn profile URL
            filename: Output filename
            path: Output directory path
            color_primary: Primary color
            color_accent: Accent color
            username: LinkedIn username

        Returns:
            Dictionary of validated values

        Raises:
            ValidationError: If any input is invalid
        """
        results = {}
        errors = []

        # Validate URL
        if url:
            try:
                results['url'] = cls.validate_linkedin_url(url)
            except ValidationError as e:
                errors.append(f"URL: {str(e)}")

        # Validate filename
        if filename:
            try:
                results['filename'] = cls.validate_filename(filename)
            except ValidationError as e:
                errors.append(f"Filename: {str(e)}")

        # Validate path
        if path:
            try:
                results['path'] = cls.validate_path(path)
            except ValidationError as e:
                errors.append(f"Path: {str(e)}")

        # Validate colors
        if color_primary:
            try:
                results['color_primary'] = cls.validate_hex_color(color_primary)
            except ValidationError as e:
                errors.append(f"Primary color: {str(e)}")

        if color_accent:
            try:
                results['color_accent'] = cls.validate_hex_color(color_accent)
            except ValidationError as e:
                errors.append(f"Accent color: {str(e)}")

        # Validate username
        if username:
            try:
                results['username'] = cls.validate_username(username)
            except ValidationError as e:
                errors.append(f"Username: {str(e)}")

        # If there were any errors, raise combined error
        if errors:
            raise ValidationError(
                f"Multiple validation errors: {'; '.join(errors)}",
                field="multiple"
            )

        return results
