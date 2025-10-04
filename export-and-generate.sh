#!/bin/bash
# LinkedIn Profile HTML Export and PDF Generation Helper
# This script guides you through exporting your LinkedIn profile and generating a PDF

set -e

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║       LinkedIn CV Generator - HTML Export & PDF Creation             ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 This script will help you generate your LinkedIn PDF CV"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "STEP 1: Export Your LinkedIn Profile HTML"
echo ""
echo "  1. Open your browser and go to:"
echo "     https://www.linkedin.com/in/alexcollsoutumuro/"
echo ""
echo "  2. Make sure you're LOGGED IN to LinkedIn"
echo ""
echo "  3. Press F12 to open Developer Tools"
echo ""
echo "  4. In the Elements/Inspector tab:"
echo "     - Find the <html> tag at the very top"
echo "     - Right-click on it"
echo "     - Select 'Copy' → 'Copy outerHTML'"
echo ""
echo "  5. Paste the HTML into a text editor and save as:"
echo "     /home/quantium/labs/linkedin-cv/linkedin-profile.html"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press ENTER when you've saved the HTML file (or Ctrl+C to cancel)..."
echo ""

# Check if file exists
if [ ! -f "linkedin-profile.html" ]; then
    echo "❌ Error: linkedin-profile.html not found in current directory"
    echo ""
    echo "Please save the HTML file as: /home/quantium/labs/linkedin-cv/linkedin-profile.html"
    echo "Then run this script again."
    exit 1
fi

# Check file size
FILE_SIZE=$(wc -c < linkedin-profile.html)
if [ "$FILE_SIZE" -lt 10000 ]; then
    echo "⚠️  Warning: HTML file seems very small (${FILE_SIZE} bytes)"
    echo "   This might indicate the file doesn't contain your full profile."
    echo ""
    read -p "Continue anyway? (y/N): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo "✅ Found linkedin-profile.html (${FILE_SIZE} bytes)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "STEP 2: Generating PDF..."
echo ""

# Generate PDF
poetry run python -m src.cli --html-file linkedin-profile.html -o . --debug

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Done! Your PDF should be in the current directory."
echo ""
echo "To view the PDF:"
echo "  xdg-open alexcollsoutumuro_*.pdf"
echo ""
echo "To view all generated PDFs:"
echo "  ls -lh *.pdf"
echo ""
