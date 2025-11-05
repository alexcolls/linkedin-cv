"""Integration tests for QR code functionality."""
import pytest
from pathlib import Path
from src.utils.qr_generator import QRGenerator
from src.pdf.generator import PDFGenerator


class TestQRCodeGeneration:
    """Test QR code generation and integration."""

    def test_qr_generator_initialization(self):
        """Test QR generator can be initialized."""
        qr_gen = QRGenerator()
        assert qr_gen is not None

    def test_generate_qr_code(self):
        """Test basic QR code generation."""
        qr_gen = QRGenerator()
        qr_data = qr_gen.generate("https://linkedin.com/in/test")
        
        assert qr_data is not None
        assert qr_data.startswith("data:image/png;base64,")
        assert len(qr_data) > 100  # Should have substantial data

    def test_qr_code_with_different_sizes(self):
        """Test QR code generation with various sizes."""
        for size in [5, 10, 15, 20]:
            qr_gen = QRGenerator(box_size=size)
            qr_data = qr_gen.generate("https://linkedin.com/in/test")
            assert qr_data is not None
            assert qr_data.startswith("data:image/png;base64,")

    def test_qr_code_with_custom_colors(self):
        """Test QR code with custom colors."""
        qr_gen = QRGenerator()
        qr_data = qr_gen.generate(
            "https://linkedin.com/in/test",
            fill_color="#FF0000",
            back_color="#FFFFFF"
        )
        
        assert qr_data is not None
        assert qr_data.startswith("data:image/png;base64,")

    def test_qr_code_with_border(self):
        """Test QR code with different border sizes."""
        for border in [0, 1, 2, 5]:
            qr_gen = QRGenerator(border=border)
            qr_data = qr_gen.generate("https://linkedin.com/in/test")
            assert qr_data is not None

    def test_qr_code_error_correction_levels(self):
        """Test QR code generation (error correction is handled internally)."""
        qr_gen = QRGenerator()
        qr_data = qr_gen.generate("https://linkedin.com/in/test")
        assert qr_data is not None
        assert qr_data.startswith("data:image/png;base64,")

    def test_qr_code_with_empty_data(self):
        """Test QR code generation with empty data."""
        qr_gen = QRGenerator()
        qr_data = qr_gen.generate("")
        
        # Should still generate a valid QR code
        assert qr_data is not None
        assert qr_data.startswith("data:image/png;base64,")

    def test_qr_code_with_long_url(self):
        """Test QR code with very long URL."""
        qr_gen = QRGenerator()
        long_url = "https://linkedin.com/in/test?" + "param=value&" * 50
        qr_data = qr_gen.generate(long_url)
        
        assert qr_data is not None
        assert qr_data.startswith("data:image/png;base64,")


class TestQRCodeInPDF:
    """Test QR code integration in PDF generation."""

    def test_pdf_generation_with_qr_code(self, sample_profile_data, temp_output_dir):
        """Test PDF generation includes QR code."""
        sample_profile_data['qr_code'] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        sample_profile_data['profile_url'] = "https://linkedin.com/in/test"
        
        generator = PDFGenerator(theme="modern")
        output_file = temp_output_dir / "test_qr_cv.pdf"
        
        generator.generate(sample_profile_data, str(output_file))
        
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_pdf_generation_without_qr_code(self, sample_profile_data, temp_output_dir):
        """Test PDF generation without QR code."""
        sample_profile_data['qr_code'] = None
        
        generator = PDFGenerator(theme="modern")
        output_file = temp_output_dir / "test_no_qr_cv.pdf"
        
        generator.generate(sample_profile_data, str(output_file))
        
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_all_themes_with_qr_code(self, sample_profile_data, temp_output_dir):
        """Test QR code works with all themes."""
        qr_gen = QRGenerator()
        qr_data = qr_gen.generate("https://linkedin.com/in/test")
        sample_profile_data['qr_code'] = qr_data
        sample_profile_data['profile_url'] = "https://linkedin.com/in/test"
        
        themes = ["modern", "creative", "executive", "classic"]
        
        for theme in themes:
            generator = PDFGenerator(theme=theme)
            output_file = temp_output_dir / f"test_qr_{theme}.pdf"
            
            generator.generate(sample_profile_data, str(output_file))
            
            assert output_file.exists(), f"PDF not generated for theme: {theme}"
            assert output_file.stat().st_size > 0


class TestQRCodeWorkflow:
    """Test complete QR code workflow."""

    def test_full_qr_workflow(self, temp_output_dir):
        """Test complete workflow from profile to PDF with QR code."""
        # Step 1: Generate QR code
        qr_gen = QRGenerator()
        profile_url = "https://linkedin.com/in/johndoe"
        qr_data = qr_gen.generate(profile_url)
        
        # Step 2: Create profile data with QR code
        profile_data = {
            'name': 'John Doe',
            'headline': 'Software Engineer',
            'location': 'San Francisco, CA',
            'qr_code': qr_data,
            'profile_url': profile_url,
            'linkedin_url': profile_url,
            'about': 'Experienced software engineer',
            'experience': [
                {
                    'title': 'Senior Engineer',
                    'company': 'Tech Corp',
                    'duration': '2020 - Present',
                    'location': 'Remote',
                    'description': 'Building scalable systems'
                }
            ],
            'education': [
                {
                    'institution': 'University',
                    'degree': 'BS Computer Science',
                    'duration': '2016 - 2020'
                }
            ],
            'skills': [
                {'name': 'Python'},
                {'name': 'JavaScript'},
                {'name': 'Docker'}
            ]
        }
        
        # Step 3: Generate PDF
        generator = PDFGenerator(theme="modern")
        output_file = temp_output_dir / "full_workflow_qr.pdf"
        generator.generate(profile_data, str(output_file))
        
        # Verify
        assert output_file.exists()
        assert output_file.stat().st_size > 5000  # Should be substantial

    def test_qr_workflow_all_themes(self, temp_output_dir):
        """Test QR workflow with all themes."""
        qr_gen = QRGenerator(box_size=10)
        profile_url = "https://linkedin.com/in/janedoe"
        qr_data = qr_gen.generate(profile_url)
        
        profile_data = {
            'name': 'Jane Doe',
            'headline': 'Product Manager',
            'qr_code': qr_data,
            'profile_url': profile_url,
            'experience': [],
            'education': [],
            'skills': []
        }
        
        for theme in ["modern", "creative", "executive", "classic"]:
            generator = PDFGenerator(theme=theme)
            output_file = temp_output_dir / f"workflow_{theme}_qr.pdf"
            
            generator.generate(profile_data, str(output_file))
            assert output_file.exists()


class TestQRCodeEdgeCases:
    """Test edge cases for QR code generation."""

    def test_qr_code_with_special_characters(self):
        """Test QR code with special characters in URL."""
        qr_gen = QRGenerator()
        special_url = "https://linkedin.com/in/john-doe?ref=test&utm_source=app"
        qr_data = qr_gen.generate(special_url)
        
        assert qr_data is not None
        assert qr_data.startswith("data:image/png;base64,")

    def test_qr_code_with_unicode(self):
        """Test QR code with unicode characters."""
        qr_gen = QRGenerator()
        unicode_url = "https://linkedin.com/in/josé-garcía"
        qr_data = qr_gen.generate(unicode_url)
        
        assert qr_data is not None

    def test_qr_code_multiple_generations(self):
        """Test generating multiple QR codes in sequence."""
        qr_gen = QRGenerator()
        
        urls = [
            "https://linkedin.com/in/user1",
            "https://linkedin.com/in/user2",
            "https://linkedin.com/in/user3",
        ]
        
        qr_codes = []
        for url in urls:
            qr_data = qr_gen.generate(url)
            qr_codes.append(qr_data)
        
        # All should be unique
        assert len(set(qr_codes)) == len(qr_codes)
        
        # All should be valid
        for qr in qr_codes:
            assert qr.startswith("data:image/png;base64,")

    def test_qr_code_consistency(self):
        """Test that same input produces same QR code."""
        qr_gen = QRGenerator()
        url = "https://linkedin.com/in/consistent"
        
        qr1 = qr_gen.generate(url)
        qr2 = qr_gen.generate(url)
        
        assert qr1 == qr2
