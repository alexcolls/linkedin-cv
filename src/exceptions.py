"""Custom exceptions for LinkedIn CV Generator."""


class LinkedInCVError(Exception):
    """Base exception for LinkedIn CV Generator."""
    
    def __init__(self, message: str, troubleshooting_hint: str = None):
        """Initialize exception with message and optional troubleshooting hint.
        
        Args:
            message: Error message
            troubleshooting_hint: Optional hint to help users resolve the issue
        """
        self.message = message
        self.troubleshooting_hint = troubleshooting_hint
        super().__init__(self.message)
    
    def __str__(self):
        """String representation with troubleshooting hint if available."""
        if self.troubleshooting_hint:
            return f"{self.message}\n\n💡 Troubleshooting: {self.troubleshooting_hint}"
        return self.message


class LinkedInAuthError(LinkedInCVError):
    """Exception raised for LinkedIn authentication errors."""
    
    def __init__(self, message: str = "LinkedIn authentication required"):
        """Initialize authentication error.
        
        Args:
            message: Error message
        """
        troubleshooting = (
            "To fix this:\n"
            "  1. Run: ./run.sh → option 4 (Login to LinkedIn)\n"
            "  2. Or run: ./run.sh → option 5 (Extract cookies from Chrome)\n"
            "  3. Then try again\n"
            "\n"
            "See docs/AUTHENTICATION_GUIDE.md for detailed instructions."
        )
        super().__init__(message, troubleshooting)


class ParsingError(LinkedInCVError):
    """Exception raised when parsing LinkedIn profile HTML fails."""
    
    def __init__(self, message: str, section: str = None):
        """Initialize parsing error.
        
        Args:
            message: Error message
            section: Optional section name where parsing failed
        """
        if section:
            full_message = f"Failed to parse {section} section: {message}"
        else:
            full_message = f"Parsing error: {message}"
        
        troubleshooting = (
            "This usually happens when:\n"
            "  • LinkedIn changed their HTML structure\n"
            "  • The profile HTML is incomplete or malformed\n"
            "  • You're not authenticated (some sections require login)\n"
            "\n"
            "Try:\n"
            "  1. Make sure you're logged in to LinkedIn\n"
            "  2. Use option 3 to extract fresh HTML\n"
            "  3. Check docs/TROUBLESHOOTING_EMPTY_DATA.md"
        )
        super().__init__(full_message, troubleshooting)


class ScrapingError(LinkedInCVError):
    """Exception raised when scraping LinkedIn profile fails."""
    
    def __init__(self, message: str, url: str = None):
        """Initialize scraping error.
        
        Args:
            message: Error message
            url: Optional URL that failed to scrape
        """
        if url:
            full_message = f"Failed to scrape {url}: {message}"
        else:
            full_message = f"Scraping error: {message}"
        
        troubleshooting = (
            "Common causes:\n"
            "  • Network connection issues\n"
            "  • LinkedIn rate limiting (too many requests)\n"
            "  • Invalid profile URL\n"
            "  • Browser automation blocked\n"
            "\n"
            "Try:\n"
            "  1. Check your internet connection\n"
            "  2. Wait a few minutes and try again\n"
            "  3. Verify the profile URL is correct\n"
            "  4. Try using --html-file with manually saved HTML"
        )
        super().__init__(full_message, troubleshooting)


class PDFGenerationError(LinkedInCVError):
    """Exception raised when PDF generation fails."""
    
    def __init__(self, message: str):
        """Initialize PDF generation error.
        
        Args:
            message: Error message
        """
        troubleshooting = (
            "PDF generation issues are often caused by:\n"
            "  • Missing or invalid profile data\n"
            "  • Template rendering errors\n"
            "  • WeasyPrint installation issues\n"
            "\n"
            "Try:\n"
            "  1. Check that profile data was extracted correctly\n"
            "  2. Verify WeasyPrint is installed: poetry run pip list | grep -i weasyprint\n"
            "  3. Try regenerating with --debug flag for more details"
        )
        super().__init__(f"PDF generation failed: {message}", troubleshooting)


class ConfigurationError(LinkedInCVError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, config_key: str = None):
        """Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Optional configuration key that caused the error
        """
        if config_key:
            full_message = f"Configuration error for '{config_key}': {message}"
        else:
            full_message = f"Configuration error: {message}"
        
        troubleshooting = (
            "Check your configuration:\n"
            "  1. Make sure .env file exists (copy from .env.sample)\n"
            "  2. Verify all required values are set\n"
            "  3. Check for typos in configuration keys\n"
            "  4. See .env.sample for valid configuration options"
        )
        super().__init__(full_message, troubleshooting)


class SessionError(LinkedInCVError):
    """Exception raised for session management errors."""
    
    def __init__(self, message: str):
        """Initialize session error.
        
        Args:
            message: Error message
        """
        troubleshooting = (
            "Session issues can be resolved by:\n"
            "  1. Deleting old session: rm -rf .session/\n"
            "  2. Re-authenticating: ./run.sh → option 4\n"
            "  3. Making sure Chrome is closed when extracting cookies\n"
            "  4. Checking .session/ directory permissions"
        )
        super().__init__(f"Session error: {message}", troubleshooting)


class ValidationError(LinkedInCVError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: str = None):
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Optional field name that failed validation
        """
        if field:
            full_message = f"Validation error for '{field}': {message}"
        else:
            full_message = f"Validation error: {message}"
        
        super().__init__(full_message, "Check that all required fields have valid values")
