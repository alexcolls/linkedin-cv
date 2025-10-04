"""Image processing utilities for profile pictures."""
import base64
from io import BytesIO
from typing import Optional

import requests
from PIL import Image


class ImageProcessor:
    """Processes and optimizes profile pictures for PDF embedding."""

    def __init__(self, max_size: int = 400, quality: int = 85):
        """Initialize the image processor.

        Args:
            max_size: Maximum dimension (width/height) in pixels
            quality: JPEG quality (1-100)
        """
        self.max_size = max_size
        self.quality = quality

    def process(self, image_url: str) -> str:
        """Download, process, and convert image to base64 data URI.

        Args:
            image_url: URL of the profile picture

        Returns:
            Data URI string for HTML embedding

        Raises:
            Exception: If image processing fails
        """
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Open and process image
            image = Image.open(BytesIO(response.content))

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

            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=self.quality, optimize=True)
            img_data = base64.b64encode(buffered.getvalue()).decode()

            # Return data URI
            return f"data:image/jpeg;base64,{img_data}"

        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}")

    def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible.

        Args:
            url: Image URL to validate

        Returns:
            True if URL is accessible, False otherwise
        """
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False
