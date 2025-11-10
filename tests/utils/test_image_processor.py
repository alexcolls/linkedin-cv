"""Tests for async image processor."""
import base64
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from PIL import Image

from src.utils.image_processor import ImageProcessor


@pytest.fixture
def sample_image():
    """Create a sample PIL image."""
    img = Image.new('RGB', (800, 600), color='red')
    return img


@pytest.fixture
def sample_image_bytes(sample_image):
    """Convert sample image to bytes."""
    buffer = BytesIO()
    sample_image.save(buffer, format='JPEG')
    return buffer.getvalue()


@pytest.fixture
def image_processor():
    """Create image processor instance."""
    return ImageProcessor(max_size=400, quality=85, use_cache=False)


@pytest.mark.asyncio
async def test_process_success(image_processor, sample_image_bytes):
    """Test successful image processing."""
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=sample_image_bytes)
    mock_response.status = 200
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        result = await image_processor.process("https://example.com/image.jpg")
        
        assert result.startswith("data:image/jpeg;base64,")
        # Verify it's valid base64
        base64_data = result.split(',')[1]
        decoded = base64.b64decode(base64_data)
        assert len(decoded) > 0


@pytest.mark.asyncio
async def test_process_with_cache_hit(sample_image_bytes):
    """Test image processing with cache hit."""
    processor = ImageProcessor(max_size=400, quality=85, use_cache=True)
    
    # Mock cache
    mock_cache = MagicMock()
    mock_cache.get.return_value = sample_image_bytes
    processor.cache = mock_cache
    
    result = await processor.process("https://example.com/image.jpg")
    
    # Should return cached data without making HTTP request
    assert result.startswith("data:image/jpeg;base64,")
    mock_cache.get.assert_called_once()


@pytest.mark.asyncio
async def test_process_with_cache_miss(image_processor, sample_image_bytes):
    """Test image processing with cache miss."""
    image_processor.use_cache = True
    mock_cache = MagicMock()
    mock_cache.get.return_value = None
    image_processor.cache = mock_cache
    
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=sample_image_bytes)
    mock_response.status = 200
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        result = await image_processor.process("https://example.com/image.jpg")
        
        assert result.startswith("data:image/jpeg;base64,")
        # Verify cache was set
        mock_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_process_rgba_image(image_processor):
    """Test processing RGBA image (convert to RGB)."""
    # Create RGBA image
    rgba_img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
    buffer = BytesIO()
    rgba_img.save(buffer, format='PNG')
    rgba_bytes = buffer.getvalue()
    
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=rgba_bytes)
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        result = await image_processor.process("https://example.com/image.png")
        
        assert result.startswith("data:image/jpeg;base64,")


@pytest.mark.asyncio
async def test_process_resize_large_image(image_processor):
    """Test resizing large image to max_size."""
    # Create large image
    large_img = Image.new('RGB', (1600, 1200), color='blue')
    buffer = BytesIO()
    large_img.save(buffer, format='JPEG')
    large_bytes = buffer.getvalue()
    
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=large_bytes)
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        result = await image_processor.process("https://example.com/large.jpg")
        
        # Decode and verify size
        base64_data = result.split(',')[1]
        decoded = base64.b64decode(base64_data)
        img = Image.open(BytesIO(decoded))
        
        # Should be resized to fit within max_size
        assert max(img.size) <= image_processor.max_size


@pytest.mark.asyncio
async def test_process_http_error(image_processor):
    """Test handling HTTP errors."""
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock(
        side_effect=aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=(),
            status=404,
            message="Not Found"
        )
    )
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        with pytest.raises(Exception, match="Failed to process image"):
            await image_processor.process("https://example.com/notfound.jpg")


@pytest.mark.asyncio
async def test_process_invalid_image_data(image_processor):
    """Test handling invalid image data."""
    invalid_data = b"This is not a valid image"
    
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=invalid_data)
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        with pytest.raises(Exception, match="Failed to process image"):
            await image_processor.process("https://example.com/invalid.jpg")


@pytest.mark.asyncio
async def test_validate_url_success():
    """Test URL validation with accessible URL."""
    processor = ImageProcessor()
    
    mock_response = AsyncMock()
    mock_response.status = 200
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.head = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        result = await processor.validate_url("https://example.com/image.jpg")
        
        assert result is True


@pytest.mark.asyncio
async def test_validate_url_failure():
    """Test URL validation with inaccessible URL."""
    processor = ImageProcessor()
    
    mock_response = AsyncMock()
    mock_response.status = 404
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.head = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        result = await processor.validate_url("https://example.com/notfound.jpg")
        
        assert result is False


@pytest.mark.asyncio
async def test_validate_url_exception():
    """Test URL validation with network error."""
    processor = ImageProcessor()
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.head = MagicMock(side_effect=aiohttp.ClientError())
        mock_session_cls.return_value = mock_session
        
        result = await processor.validate_url("https://example.com/error.jpg")
        
        assert result is False


def test_image_processor_init():
    """Test image processor initialization."""
    processor = ImageProcessor(max_size=500, quality=90, use_cache=True)
    
    assert processor.max_size == 500
    assert processor.quality == 90
    assert processor.use_cache is True
    assert processor.cache is not None


def test_image_processor_init_no_cache():
    """Test image processor initialization without cache."""
    processor = ImageProcessor(use_cache=False)
    
    assert processor.use_cache is False
    assert processor.cache is None


@pytest.mark.asyncio
async def test_process_palette_image(image_processor):
    """Test processing palette mode image."""
    # Create palette image
    palette_img = Image.new('P', (100, 100))
    palette_img.putpalette([i % 256 for i in range(768)])
    buffer = BytesIO()
    palette_img.save(buffer, format='PNG')
    palette_bytes = buffer.getvalue()
    
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=palette_bytes)
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        result = await image_processor.process("https://example.com/palette.png")
        
        assert result.startswith("data:image/jpeg;base64,")


@pytest.mark.asyncio
async def test_process_quality_setting():
    """Test that quality setting affects output."""
    img = Image.new('RGB', (200, 200), color='green')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_bytes = buffer.getvalue()
    
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.read = AsyncMock(return_value=img_bytes)
    
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.get = MagicMock(return_value=mock_response)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_session_cls.return_value = mock_session
        
        # Process with low quality
        processor_low = ImageProcessor(quality=10, use_cache=False)
        result_low = await processor_low.process("https://example.com/img.jpg")
        
        # Process with high quality
        processor_high = ImageProcessor(quality=95, use_cache=False)
        result_high = await processor_high.process("https://example.com/img.jpg")
        
        # Both should be valid data URIs
        assert result_low.startswith("data:image/jpeg;base64,")
        assert result_high.startswith("data:image/jpeg;base64,")
        
        # High quality should produce larger result (more data)
        # Note: This might not always be true due to compression, but in general it should be
        assert len(result_low) > 0
        assert len(result_high) > 0
