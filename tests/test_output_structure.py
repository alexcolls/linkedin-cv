#!/usr/bin/env python3
"""
Test script to verify the output directory structure.
"""

import json
from pathlib import Path
from datetime import datetime

def test_output_structure():
    """Test the output structure for different usernames."""
    
    test_cases = [
        "alex-colls-outumuro",
        "https://www.linkedin.com/in/alex-colls-outumuro/",
        "john-doe",
        "https://linkedin.com/in/jane-smith",
    ]
    
    print("Testing output structure:")
    print("=" * 50)
    
    for test_input in test_cases:
        print(f"\nInput: {test_input}")
        
        # Extract username
        import re
        username = test_input
        if 'linkedin.com' in test_input:
            match = re.search(r'linkedin\.com/in/([^/]+)', test_input)
            if match:
                username = match.group(1)
        else:
            username = test_input.strip('/').split('/')[-1]
        
        print(f"  Extracted username: {username}")
        
        # Expected paths
        output_dir = Path(f"output/{username}")
        json_path = output_dir / "profile_data.json"
        
        # Example PDF with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = output_dir / f"cv_{timestamp}.pdf"
        
        print(f"  Output directory: {output_dir}")
        print(f"  JSON path: {json_path}")
        print(f"  PDF path: {pdf_path}")
        
        # Check if alex's directory exists
        if username == "alex-colls-outumuro":
            if output_dir.exists():
                print(f"  ✅ Directory exists!")
                if json_path.exists():
                    print(f"  ✅ JSON file exists!")
                    # Show file size
                    size = json_path.stat().st_size
                    print(f"     Size: {size:,} bytes")
                else:
                    print(f"  ❌ JSON file not found")
                
                # Check for any PDFs
                pdfs = list(output_dir.glob("*.pdf"))
                if pdfs:
                    print(f"  📄 Found {len(pdfs)} PDF(s):")
                    for pdf in pdfs:
                        print(f"     - {pdf.name}")
                else:
                    print(f"  ℹ️ No PDFs found")
            else:
                print(f"  ❌ Directory doesn't exist")

if __name__ == "__main__":
    test_output_structure()
    
    # Show current output structure
    print("\n" + "=" * 50)
    print("Current output directory structure:")
    output_path = Path("output")
    if output_path.exists():
        for user_dir in output_path.iterdir():
            if user_dir.is_dir():
                print(f"\n📁 {user_dir}/")
                for file in user_dir.iterdir():
                    print(f"  📄 {file.name} ({file.stat().st_size:,} bytes)")
    else:
        print("No output directory found")