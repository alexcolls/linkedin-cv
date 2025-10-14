#!/bin/bash
# LinkedIn Profile HTML Export and PDF Generation Helper
# This script guides you through exporting your LinkedIn profile and generating a PDF

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source common functions
source "$SCRIPT_DIR/common.sh"

# Change to project root
cd "$PROJECT_ROOT"

# Load .env if exists to get PROFILE_URL
PROFILE_URL=""
if load_env ".env"; then
    PROFILE_URL="${PROFILE_URL:-}"
fi

# If no profile URL in .env, ask for it
if [ -z "$PROFILE_URL" ]; then
    print_header "📋 LinkedIn CV Generator - HTML Export Helper"
    echo -e "${YELLOW}No PROFILE_URL found in .env file.${NC}"
    echo ""
    read -p "$(echo -e ${CYAN}Enter your LinkedIn profile URL: ${NC})" PROFILE_URL
    PROFILE_URL=$(echo "$PROFILE_URL" | xargs)  # Trim whitespace
fi

print_header "📋 LinkedIn CV Generator - HTML Export Helper" "Step-by-step guide to export your LinkedIn profile"

echo -e "${CYAN}${BOLD}STEP 1: Export Your LinkedIn Profile HTML${NC}"
echo ""
echo "  1. Open your browser and go to:"
echo -e "     ${BLUE}$PROFILE_URL${NC}"
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
echo -e "     ${BLUE}$PROJECT_ROOT/linkedin-profile.html${NC}"
echo ""
echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
read -p "$(echo -e ${CYAN}Press ENTER when you've saved the HTML file \(or Ctrl+C to cancel\)...${NC})" 
echo ""

# Check if file exists
if [ ! -f "linkedin-profile.html" ]; then
    print_error "linkedin-profile.html not found in current directory"
    echo ""
    print_info "Please save the HTML file as: $PROJECT_ROOT/linkedin-profile.html"
    print_info "Then run this script again."
    exit 1
fi

# Check file size
FILE_SIZE=$(wc -c < linkedin-profile.html)
if [ "$FILE_SIZE" -lt 10000 ]; then
    print_warning "HTML file seems very small (${FILE_SIZE} bytes)"
    print_warning "This might indicate the file doesn't contain your full profile."
    echo ""
    if ! confirm "Continue anyway?"; then
        print_info "Cancelled."
        exit 0
    fi
fi

print_success "Found linkedin-profile.html (${FILE_SIZE} bytes)"
echo ""
echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
print_step "STEP 2: Generating Professional PDF CV..."
echo ""

# Generate PDF
poetry run python -m src.cli --html-file linkedin-profile.html -o output

echo ""
echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
print_success "Done! Your professional PDF CV is ready!"
echo ""
echo -e "${CYAN}To view your CV:${NC}"
echo -e "  ${BLUE}xdg-open output/*.pdf${NC}"
echo ""
echo -e "${CYAN}To list all generated CVs:${NC}"
echo -e "  ${BLUE}ls -lh output/*.pdf${NC}"
echo ""
echo -e "${GREEN}${BOLD}✨ Ready to send to any company! ✨${NC}"
echo ""
