#!/usr/bin/env python3
"""Profile performance of CV generation workflow."""
import asyncio
import cProfile
import io
import pstats
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pdf.generator import PDFGenerator
from src.scraper.linkedin_scraper import LinkedInScraper
from src.scraper.parser import ProfileParser
from src.utils.image_processor import ImageProcessor
from src.utils.qr_generator import QRGenerator


class PerformanceProfiler:
    """Profile performance of CV generation components."""

    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}

    async def profile_scraping(self, profile_url: str) -> tuple:
        """Profile the scraping phase."""
        print("🔍 Profiling scraping...")
        
        profiler = cProfile.Profile()
        scraper = LinkedInScraper(headless=True, debug=False)
        
        start_time = time.time()
        profiler.enable()
        
        html_content = await scraper.scrape_profile(profile_url)
        
        profiler.disable()
        elapsed = time.time() - start_time
        
        self.results['scraping'] = {
            'elapsed': elapsed,
            'profiler': profiler,
            'size': len(html_content) if html_content else 0
        }
        
        print(f"   ⏱️  Scraping took {elapsed:.2f}s ({len(html_content):,} bytes)")
        
        return html_content

    def profile_parsing(self, html_content: str) -> dict:
        """Profile the parsing phase."""
        print("📋 Profiling parsing...")
        
        profiler = cProfile.Profile()
        parser = ProfileParser(debug=False)
        
        start_time = time.time()
        profiler.enable()
        
        profile_data = parser.parse(html_content)
        
        profiler.disable()
        elapsed = time.time() - start_time
        
        self.results['parsing'] = {
            'elapsed': elapsed,
            'profiler': profiler,
            'sections': len(profile_data.get('sections', [])),
            'experience': len(profile_data.get('experience', [])),
            'education': len(profile_data.get('education', [])),
            'skills': len(profile_data.get('skills', []))
        }
        
        print(f"   ⏱️  Parsing took {elapsed:.2f}s")
        print(f"       • Sections: {self.results['parsing']['sections']}")
        print(f"       • Experience: {self.results['parsing']['experience']}")
        print(f"       • Education: {self.results['parsing']['education']}")
        print(f"       • Skills: {self.results['parsing']['skills']}")
        
        return profile_data

    def profile_image_processing(self, image_url: str) -> str:
        """Profile image processing."""
        if not image_url:
            return None
            
        print("🖼️  Profiling image processing...")
        
        profiler = cProfile.Profile()
        processor = ImageProcessor()
        
        start_time = time.time()
        profiler.enable()
        
        try:
            image_data = processor.process(image_url)
        except Exception as e:
            print(f"   ⚠️  Image processing failed: {e}")
            image_data = None
        
        profiler.disable()
        elapsed = time.time() - start_time
        
        self.results['image_processing'] = {
            'elapsed': elapsed,
            'profiler': profiler,
            'success': image_data is not None
        }
        
        print(f"   ⏱️  Image processing took {elapsed:.2f}s")
        
        return image_data

    def profile_qr_generation(self, url: str) -> str:
        """Profile QR code generation."""
        print("📱 Profiling QR code generation...")
        
        profiler = cProfile.Profile()
        qr_gen = QRGenerator(box_size=10, border=1)
        
        start_time = time.time()
        profiler.enable()
        
        qr_data = qr_gen.generate(url)
        
        profiler.disable()
        elapsed = time.time() - start_time
        
        self.results['qr_generation'] = {
            'elapsed': elapsed,
            'profiler': profiler,
            'size': len(qr_data) if qr_data else 0
        }
        
        print(f"   ⏱️  QR generation took {elapsed:.2f}s")
        
        return qr_data

    def profile_pdf_generation(self, profile_data: dict, output_path: Path, theme: str = "modern"):
        """Profile PDF generation."""
        print(f"📄 Profiling PDF generation ({theme} theme)...")
        
        profiler = cProfile.Profile()
        generator = PDFGenerator(theme=theme)
        
        start_time = time.time()
        profiler.enable()
        
        pdf_path = generator.generate(profile_data, output_path)
        
        profiler.disable()
        elapsed = time.time() - start_time
        
        file_size = pdf_path.stat().st_size if pdf_path.exists() else 0
        
        self.results['pdf_generation'] = {
            'elapsed': elapsed,
            'profiler': profiler,
            'size': file_size,
            'theme': theme
        }
        
        print(f"   ⏱️  PDF generation took {elapsed:.2f}s ({file_size:,} bytes)")
        
        return pdf_path

    def print_summary(self):
        """Print performance summary."""
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 70)
        
        total_time = sum(r['elapsed'] for r in self.results.values())
        
        print(f"\n⏱️  Total Time: {total_time:.2f}s\n")
        
        # Sort by elapsed time
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['elapsed'],
            reverse=True
        )
        
        for phase, data in sorted_results:
            percentage = (data['elapsed'] / total_time) * 100
            bar_length = int(percentage / 2)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            
            print(f"{phase:.<25} {data['elapsed']:>6.2f}s  [{bar}] {percentage:>5.1f}%")
        
        print("\n" + "=" * 70)
        
        # Target check
        if total_time < 10:
            print(f"✅ Target achieved! Total time {total_time:.2f}s < 10s")
        else:
            print(f"⚠️  Target not met. Total time {total_time:.2f}s > 10s")
            print(f"   Need to optimize: {total_time - 10:.2f}s")

    def print_detailed_stats(self, phase: str, top_n: int = 10):
        """Print detailed profiling stats for a phase."""
        if phase not in self.results:
            print(f"No profiling data for {phase}")
            return
        
        print(f"\n{'=' * 70}")
        print(f"📊 TOP {top_n} FUNCTIONS IN {phase.upper()}")
        print("=" * 70)
        
        s = io.StringIO()
        profiler = self.results[phase]['profiler']
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(top_n)
        
        print(s.getvalue())

    def save_profile(self, phase: str, output_file: Path):
        """Save profiling data to file."""
        if phase not in self.results:
            print(f"No profiling data for {phase}")
            return
        
        profiler = self.results[phase]['profiler']
        profiler.dump_stats(str(output_file))
        print(f"💾 Saved {phase} profile to {output_file}")


async def main():
    """Main profiling workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Profile CV generation performance")
    parser.add_argument(
        "profile_url",
        nargs="?",
        default=None,
        help="LinkedIn profile URL to test with"
    )
    parser.add_argument(
        "--theme",
        default="modern",
        choices=["modern", "creative", "executive", "classic"],
        help="PDF theme to use (default: modern)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./output/profile_test"),
        help="Output directory for generated PDF"
    )
    parser.add_argument(
        "--detailed",
        nargs="?",
        const="all",
        help="Show detailed stats for phase (all, scraping, parsing, etc.)"
    )
    parser.add_argument(
        "--save-profiles",
        action="store_true",
        help="Save profiling data to files"
    )
    
    args = parser.parse_args()
    
    if not args.profile_url:
        # Use test HTML file if available
        test_html = project_root / "tests" / "fixtures" / "profile.html"
        if not test_html.exists():
            print("❌ Error: No profile URL provided and no test HTML found")
            print("Usage: python scripts/profile_performance.py <profile_url>")
            sys.exit(1)
        
        print(f"Using test HTML file: {test_html}")
        with open(test_html) as f:
            html_content = f.read()
        
        profiler = PerformanceProfiler()
        profile_data = profiler.profile_parsing(html_content)
    else:
        profile_url = args.profile_url
        print(f"🎯 Profiling CV generation for: {profile_url}")
        print()
        
        profiler = PerformanceProfiler()
        
        # Profile each phase
        html_content = await profiler.profile_scraping(profile_url)
        profile_data = profiler.profile_parsing(html_content)
        
        # Image processing
        if profile_data.get('profile_picture_url'):
            image_data = profiler.profile_image_processing(
                profile_data['profile_picture_url']
            )
            if image_data:
                profile_data['profile_image_data'] = image_data
        
        # QR code generation
        qr_data = profiler.profile_qr_generation(profile_url)
        profile_data['qr_code'] = qr_data
        profile_data['profile_url'] = profile_url
    
    # PDF generation
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_file = args.output_dir / "profile_test.pdf"
    profiler.profile_pdf_generation(profile_data, output_file, theme=args.theme)
    
    # Print summary
    profiler.print_summary()
    
    # Detailed stats if requested
    if args.detailed:
        phases = (
            list(profiler.results.keys())
            if args.detailed == "all"
            else [args.detailed]
        )
        
        for phase in phases:
            profiler.print_detailed_stats(phase, top_n=15)
    
    # Save profiles if requested
    if args.save_profiles:
        profile_dir = project_root / "performance_profiles"
        profile_dir.mkdir(exist_ok=True)
        
        for phase in profiler.results.keys():
            output_file = profile_dir / f"{phase}.prof"
            profiler.save_profile(phase, output_file)


if __name__ == "__main__":
    asyncio.run(main())
