"""Tests for configuration module."""
import os
import tempfile
from pathlib import Path

import pytest

from src.config import Config, get_config, reset_config
from src.exceptions import ValidationError


class TestConfig:
    """Test configuration loading and validation."""
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_config()
        # Clean up any environment variables we set
        for key in ["OUTPUT_DIR", "LOG_LEVEL", "HEADLESS", "BROWSER_TIMEOUT", "SCROLL_PAUSE", "ENCRYPTION_KEY"]:
            if key in os.environ:
                del os.environ[key]
    
    def test_default_config(self):
        """Test configuration with default values."""
        config = Config()
        
        assert config.get("output_dir") == Path("./output")
        assert config.get("log_level") == "INFO"
        assert config.get("headless") is True
        assert config.get("browser_timeout") == 30
        assert config.get("page_load_timeout") == 60
        assert config.get("scroll_pause") == 1.5
        assert config.get("max_scroll_attempts") == 10
    
    def test_load_from_env(self):
        """Test loading configuration from environment variables."""
        os.environ["OUTPUT_DIR"] = "/tmp/test_output"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["HEADLESS"] = "false"
        os.environ["BROWSER_TIMEOUT"] = "60"
        
        config = Config()
        
        assert config.get("output_dir") == Path("/tmp/test_output")
        assert config.get("log_level") == "DEBUG"
        assert config.get("headless") is False
        assert config.get("browser_timeout") == 60
    
    def test_load_from_env_file(self):
        """Test loading configuration from .env file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("OUTPUT_DIR=/tmp/env_test\n")
            f.write("LOG_LEVEL=WARNING\n")
            f.write("HEADLESS=false\n")
            env_file = f.name
        
        try:
            config = Config(env_file=env_file)
            assert config.get("output_dir") == Path("/tmp/env_test")
            assert config.get("log_level") == "WARNING"
            assert config.get("headless") is False
        finally:
            os.unlink(env_file)
    
    def test_invalid_log_level(self):
        """Test validation error for invalid log level."""
        os.environ["LOG_LEVEL"] = "INVALID"
        
        with pytest.raises(ValidationError) as exc_info:
            Config()
        
        assert "Invalid log level" in str(exc_info.value)
        assert "LOG_LEVEL" in str(exc_info.value)
    
    def test_invalid_int(self):
        """Test validation error for invalid integer."""
        os.environ["BROWSER_TIMEOUT"] = "not_a_number"
        
        with pytest.raises(ValidationError) as exc_info:
            Config()
        
        assert "Invalid integer value" in str(exc_info.value)
        assert "BROWSER_TIMEOUT" in str(exc_info.value)
    
    def test_invalid_float(self):
        """Test validation error for invalid float."""
        os.environ["SCROLL_PAUSE"] = "invalid"
        
        with pytest.raises(ValidationError) as exc_info:
            Config()
        
        assert "Invalid float value" in str(exc_info.value)
        assert "SCROLL_PAUSE" in str(exc_info.value)
    
    def test_bool_parsing(self):
        """Test various boolean value representations."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
        ]
        
        for value, expected in test_cases:
            os.environ["HEADLESS"] = value
            config = Config()
            assert config.get("headless") == expected, f"Failed for value: {value}"
            reset_config()
    
    def test_path_expansion(self):
        """Test path expansion (e.g., ~)."""
        os.environ["OUTPUT_DIR"] = "~/test_output"
        config = Config()
        
        output_dir = config.get("output_dir")
        assert isinstance(output_dir, Path)
        assert str(output_dir).startswith(str(Path.home()))
    
    def test_dict_access(self):
        """Test dictionary-style access to configuration."""
        config = Config()
        
        # Test __getitem__
        assert config["log_level"] == "INFO"
        
        # Test KeyError for non-existent key
        with pytest.raises(KeyError):
            _ = config["non_existent_key"]
    
    def test_validate_profile_url(self):
        """Test profile URL validation."""
        config = Config()
        
        # Valid URLs
        assert config.validate_profile_url("https://www.linkedin.com/in/username/")
        assert config.validate_profile_url("http://linkedin.com/in/test")
        
        # Invalid URLs
        with pytest.raises(ValidationError) as exc_info:
            config.validate_profile_url("linkedin.com/in/username")
        assert "must include protocol" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            config.validate_profile_url("https://example.com/profile")
        assert "must be a LinkedIn profile" in str(exc_info.value)
    
    def test_create_output_dir(self):
        """Test output directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_output"
            os.environ["OUTPUT_DIR"] = str(test_dir)
            
            config = Config()
            result = config.create_output_dir()
            
            assert result.exists()
            assert result.is_dir()
            assert result == test_dir
    
    def test_to_dict(self):
        """Test exporting configuration as dictionary."""
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "output_dir" in config_dict
        assert "log_level" in config_dict
        assert "headless" in config_dict
    
    def test_repr(self):
        """Test string representation of configuration."""
        config = Config()
        repr_str = repr(config)
        
        assert "Config" in repr_str
        assert "output_dir" in repr_str
    
    def test_repr_hides_sensitive_data(self):
        """Test that sensitive data is hidden in repr."""
        os.environ["ENCRYPTION_KEY"] = "secret_key_12345"
        config = Config()
        repr_str = repr(config)
        
        assert "secret_key_12345" not in repr_str
        assert "***" in repr_str
    
    def test_get_with_default(self):
        """Test get method with default value."""
        config = Config()
        
        # Existing key
        assert config.get("log_level") == "INFO"
        
        # Non-existent key with default
        assert config.get("non_existent", "default_value") == "default_value"
        
        # Non-existent key without default
        assert config.get("non_existent") is None


class TestGlobalConfig:
    """Test global configuration instance management."""
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_config()
    
    def test_get_config_singleton(self):
        """Test that get_config returns same instance."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_reset_config(self):
        """Test resetting global configuration."""
        config1 = get_config()
        reset_config()
        config2 = get_config()
        
        assert config1 is not config2
    
    def test_get_config_with_env_file(self):
        """Test get_config with custom env file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("LOG_LEVEL=DEBUG\n")
            env_file = f.name
        
        try:
            reset_config()
            config = get_config(env_file=env_file)
            assert config.get("log_level") == "DEBUG"
        finally:
            os.unlink(env_file)


class TestConfigIntegration:
    """Integration tests for configuration."""
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_config()
        for key in ["OUTPUT_DIR", "LOG_LEVEL", "LINKEDIN_PROFILE_URL"]:
            if key in os.environ:
                del os.environ[key]
    
    def test_complete_workflow(self):
        """Test complete configuration workflow."""
        # Set up environment
        os.environ["OUTPUT_DIR"] = "/tmp/linkedin_cv"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["LINKEDIN_PROFILE_URL"] = "https://www.linkedin.com/in/testuser/"
        
        # Create config
        config = get_config()
        
        # Validate configuration
        assert config.get("output_dir") == Path("/tmp/linkedin_cv")
        assert config.get("log_level") == "DEBUG"
        assert config.get("profile_url") == "https://www.linkedin.com/in/testuser/"
        
        # Validate URL
        profile_url = config.get("profile_url")
        if profile_url:
            assert config.validate_profile_url(profile_url)
        
        # Export to dict
        config_dict = config.to_dict()
        assert len(config_dict) > 0
