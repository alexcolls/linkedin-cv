"""Image processing utilities for profile pictures."""
import base64
from io import BytesIO
from typing import Optional

import aiohttp
from PIL import Image

from src.utils.cache import get_image_cache


class ImageProcessor:
    """Processes and optimizes profile pictures for PDF embedding."""

    def __init__(self, max_size: int = 400, quality: int = 85, use_cache: bool = True):
        """Initialize the image processor.

        Args:
            max_size: Maximum dimension (width/height) in pixels
            quality: JPEG quality (1-100)
            use_cache: Enable image caching (default: True)
        """
        self.max_size = max_size
        self.quality = quality
        self.use_cache = use_cache
        self.cache = get_image_cache() if use_cache else None

    async def process(self, image_url: str) -> str:
        """Download, process, and convert image to base64 data URI.

        Args:
            image_url: URL of the profile picture

        Returns:
            Data URI string for HTML embedding

        Raises:
            Exception: If image processing fails
        """
        # Check cache first
        if self.use_cache and self.cache:
            cache_key = f"{image_url}::{self.max_size}::{self.quality}"
            cached_data = self.cache.get(cache_key, extension="img")
            if cached_data:
                # Cache hit - return cached data URI
                img_data = base64.b64encode(cached_data).decode()
                return f"data:image/jpeg;base64,{img_data}"
        
        try:
            # Download image asynchronously
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    content = await response.read()

            # Open and process image
            image = Image.open(BytesIO(content))

            # Convert to RGB if necessary
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = background

            # Resize if necessary
            if max(image.size) > self.max_size:
                image.thumbnail((self.max_size, self.max_size), Image.Resampling.LANCZOS)

            # Convert to JPEG bytes
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=self.quality, optimize=True)
            jpeg_bytes = buffered.getvalue()
            
            # Cache the processed image
            if self.use_cache and self.cache:
                cache_key = f"{image_url}::{self.max_size}::{self.quality}"
                self.cache.set(cache_key, jpeg_bytes, extension="img")
            
            # Convert to base64 and return data URI
            img_data = base64.b64encode(jpeg_bytes).decode()
            return f"data:image/jpeg;base64,{img_data}"

        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}")

    async def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible.

        Args:
            url: Image URL to validate

        Returns:
            True if URL is accessible, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False
