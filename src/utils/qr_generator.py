"""QR code generator for LinkedIn profiles."""
import base64
from io import BytesIO
from typing import Optional

import qrcode
from PIL import Image


class QRGenerator:
    """Generate QR codes for LinkedIn profile URLs."""
    
    def __init__(self, version: int = 1, box_size: int = 10, border: int = 2):
        """Initialize QR code generator.
        
        Args:
            version: QR code version (1-40), controls size
            box_size: Size of each box in pixels
            border: Border size in boxes
        """
        self.version = version
        self.box_size = box_size
        self.border = border
    
    def generate(self, profile_url: str, fill_color: str = "black", back_color: str = "white") -> Optional[str]:
        """Generate QR code as base64 data URI.
        
        Args:
            profile_url: LinkedIn profile URL
            fill_color: QR code fill color (default: black)
            back_color: QR code background color (default: white)
            
        Returns:
            Base64 data URI string for embedding in HTML/PDF, or None on error
        """
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=self.version,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=self.box_size,
                border=self.border,
            )
            
            # Add data
            qr.add_data(profile_url)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # Convert to base64 data URI
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
    
    def generate_with_logo(
        self, 
        profile_url: str, 
        logo_path: Optional[str] = None,
        fill_color: str = "black",
        back_color: str = "white"
    ) -> Optional[str]:
        """Generate QR code with optional logo in center.
        
        Args:
            profile_url: LinkedIn profile URL
            logo_path: Path to logo image file
            fill_color: QR code fill color
            back_color: QR code background color
            
        Returns:
            Base64 data URI string, or None on error
        """
        try:
            # Generate basic QR code
            qr = qrcode.QRCode(
                version=self.version,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo
                box_size=self.box_size,
                border=self.border,
            )
            
            qr.add_data(profile_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGB')
            
            # Add logo if provided
            if logo_path:
                try:
                    logo = Image.open(logo_path)
                    
                    # Calculate logo size (max 30% of QR code)
                    qr_width, qr_height = img.size
                    logo_size = min(qr_width, qr_height) // 3
                    
                    # Resize logo
                    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
                    
                    # Calculate position (center)
                    logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                    
                    # Paste logo
                    img.paste(logo, logo_pos)
                except Exception as e:
                    print(f"Warning: Could not add logo: {e}")
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            print(f"Error generating QR code with logo: {e}")
            return None
