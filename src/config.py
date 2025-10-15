"""Centralized configuration management for LinkedIn CV Generator."""
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from dotenv import load_dotenv

from src.exceptions import ValidationError


class Config:
    """Configuration manager for the application.
    
    Handles loading configuration from environment variables and .env files,
    with validation and sensible defaults.
    """
    
    # Default values
    DEFAULT_OUTPUT_DIR = "./output"
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_TIMEOUT = 30
    DEFAULT_HEADLESS = True
    DEFAULT_PAGE_LOAD_TIMEOUT = 60
    DEFAULT_SCROLL_PAUSE = 1.5
    DEFAULT_MAX_SCROLL_ATTEMPTS = 10
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional, defaults to .env in project root)
        """
        self._config: Dict[str, Any] = {}
        self._load_env(env_file)
        self._load_config()
    
    def _load_env(self, env_file: Optional[str] = None) -> None:
        """Load environment variables from .env file.
        
        Args:
            env_file: Path to .env file
        """
        if env_file:
            env_path = Path(env_file)
            if env_path.exists():
                load_dotenv(env_path)
        else:
            # Try to find .env in project root
            project_root = Path(__file__).parent.parent
            env_path = project_root / ".env"
            if env_path.exists():
                load_dotenv(env_path)
    
    def _load_config(self) -> None:
        """Load all configuration values with validation."""
        self._config = {
            # Paths
            "output_dir": self._get_path("OUTPUT_DIR", self.DEFAULT_OUTPUT_DIR),
            "session_dir": self._get_path("SESSION_DIR", None),
            
            # Logging
            "log_level": self._get_log_level("LOG_LEVEL", self.DEFAULT_LOG_LEVEL),
            "log_file": self._get_path("LOG_FILE", None),
            
            # Browser settings
            "headless": self._get_bool("HEADLESS", self.DEFAULT_HEADLESS),
            "browser_timeout": self._get_int("BROWSER_TIMEOUT", self.DEFAULT_TIMEOUT),
            "page_load_timeout": self._get_int("PAGE_LOAD_TIMEOUT", self.DEFAULT_PAGE_LOAD_TIMEOUT),
            
            # Scraping settings
            "scroll_pause": self._get_float("SCROLL_PAUSE", self.DEFAULT_SCROLL_PAUSE),
            "max_scroll_attempts": self._get_int("MAX_SCROLL_ATTEMPTS", self.DEFAULT_MAX_SCROLL_ATTEMPTS),
            "user_agent": self._get_str("USER_AGENT", None),
            
            # LinkedIn profile
            "profile_url": self._get_str("LINKEDIN_PROFILE_URL", None),
            
            # PDF generation
            "template_path": self._get_path("TEMPLATE_PATH", None),
            
            # Security
            "encrypt_session": self._get_bool("ENCRYPT_SESSION", False),
            "encryption_key": self._get_str("ENCRYPTION_KEY", None),
        }
    
    def _get_str(self, key: str, default: Optional[str]) -> Optional[str]:
        """Get string value from environment.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            String value or default
        """
        value = os.getenv(key, default)
        return value if value else default
    
    def _get_int(self, key: str, default: int) -> int:
        """Get integer value from environment with validation.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Integer value or default
            
        Raises:
            ValidationError: If value is not a valid integer
        """
        value = os.getenv(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            raise ValidationError(
                f"Invalid integer value: '{value}'. Please provide a valid integer.",
                field=key
            )
    
    def _get_float(self, key: str, default: float) -> float:
        """Get float value from environment with validation.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Float value or default
            
        Raises:
            ValidationError: If value is not a valid float
        """
        value = os.getenv(key)
        if value is None:
            return default
        
        try:
            return float(value)
        except ValueError:
            raise ValidationError(
                f"Invalid float value: '{value}'. Please provide a valid number.",
                field=key
            )
    
    def _get_bool(self, key: str, default: bool) -> bool:
        """Get boolean value from environment.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Boolean value or default
        """
        value = os.getenv(key)
        if value is None:
            return default
        
        # Support various boolean representations
        return value.lower() in ("true", "1", "yes", "on")
    
    def _get_path(self, key: str, default: Optional[str]) -> Optional[Path]:
        """Get path value from environment.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Path object or None
        """
        value = os.getenv(key, default)
        if value is None:
            return None
        return Path(value).expanduser()
    
    def _get_log_level(self, key: str, default: str) -> str:
        """Get and validate log level from environment.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Valid log level string
            
        Raises:
            ValidationError: If log level is invalid
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        value = os.getenv(key, default).upper()
        
        if value not in valid_levels:
            raise ValidationError(
                f"Invalid log level: '{value}'. Valid options are: {', '.join(valid_levels)}",
                field=key
            )
        
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dict-like syntax.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
            
        Raises:
            KeyError: If key not found
        """
        return self._config[key]
    
    def validate_profile_url(self, url: str) -> bool:
        """Validate LinkedIn profile URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If URL is invalid
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                raise ValidationError(
                    f"URL must include protocol (http:// or https://). Example: https://www.linkedin.com/in/username/",
                    field="profile_url"
                )
            
            if "linkedin.com" not in parsed.netloc:
                raise ValidationError(
                    f"URL must be a LinkedIn profile. URL should contain 'linkedin.com'",
                    field="profile_url"
                )
            
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Invalid URL: {str(e)}. Please provide a valid LinkedIn profile URL.",
                field="profile_url"
            )
    
    def create_output_dir(self) -> Path:
        """Create output directory if it doesn't exist.
        
        Returns:
            Path to output directory
        """
        output_dir = self.get("output_dir")
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir
        return Path(self.DEFAULT_OUTPUT_DIR)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary.
        
        Returns:
            Dictionary of configuration values
        """
        return self._config.copy()
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        # Hide sensitive values
        safe_config = self._config.copy()
        if safe_config.get("encryption_key"):
            safe_config["encryption_key"] = "***"
        return f"Config({safe_config})"


# Create a global config instance
_config: Optional[Config] = None


def get_config(env_file: Optional[str] = None) -> Config:
    """Get or create global configuration instance.
    
    Args:
        env_file: Path to .env file (optional)
        
    Returns:
        Configuration instance
    """
    global _config
    if _config is None:
        _config = Config(env_file)
    return _config


def reset_config() -> None:
    """Reset global configuration instance (useful for testing)."""
    global _config
    _config = None
