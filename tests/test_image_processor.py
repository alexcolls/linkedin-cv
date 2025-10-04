"""Tests for image processor."""
import pytest

from src.utils.image_processor import ImageProcessor


def test_image_processor_initialization():
    """Test ImageProcessor initialization."""
    processor = ImageProcessor(max_size=500, quality=90)
    assert processor.max_size == 500
    assert processor.quality == 90


def test_image_processor_default_values():
    """Test ImageProcessor default values."""
    processor = ImageProcessor()
    assert processor.max_size == 400
    assert processor.quality == 85


def test_validate_url_invalid():
    """Test URL validation with invalid URL."""
    processor = ImageProcessor()
    assert not processor.validate_url("https://invalid-url-that-does-not-exist.example.com/image.jpg")


def test_process_raises_on_invalid_url():
    """Test that process raises exception on invalid URL."""
    processor = ImageProcessor()
    with pytest.raises(Exception):
        processor.process("https://invalid-url-that-does-not-exist.example.com/image.jpg")
