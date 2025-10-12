#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🖨️ LinkedIn CV Generator - Single Entry Point
# 
# This is the ONLY script you need to run!
# - Interactive menu for easy access
# - CLI passthrough for advanced users  
# - All features in one place
# ═══════════════════════════════════════════════════════════════

set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Source common functions
source "$SCRIPT_DIR/scripts/common.sh"

# Change to project root
cd "$PROJECT_ROOT"

# ═══════════════════════════════════════════════════════════════
# Menu Functions
# ═══════════════════════════════════════════════════════════════

show_menu() {
    clear
    
    # Display the ASCII banner from assets
    if [ -f "$PROJECT_ROOT/assets/banner.txt" ]; then
        echo -e "${CYAN}${BOLD}"
        cat "$PROJECT_ROOT/assets/banner.txt"
        echo -e "${NC}"
    fi
    
    echo -e "${DIM}Transform your LinkedIn profile into a professional CV${NC}"
    echo ""
    
    echo -e "${CYAN}${BOLD}📋 Main Workflow (in order):${NC}"
    echo -e "  ${BOLD}1)${NC} 🌐 Extract HTML from LinkedIn profile"
    echo -e "  ${BOLD}2)${NC} 📊 Extract JSON data from HTML"
    echo -e "  ${BOLD}3)${NC} 📄 Generate CV PDF from JSON"
    echo ""
    echo -e "${CYAN}${BOLD}🔐 Authentication:${NC}"
    echo -e "  ${BOLD}4)${NC} 🔐 Login to LinkedIn (save session)"
    echo -e "  ${BOLD}5)${NC} 🍪 Extract cookies from Chrome"
    echo ""
    echo -e "${CYAN}${BOLD}🔧 Setup & Testing:${NC}"
    echo -e "  ${BOLD}6)${NC} ⚙️ Run installation/setup"
    echo -e "  ${BOLD}7)${NC} 🧪 Run tests"
    echo -e "  ${BOLD}8)${NC} 📊 View test coverage"
    echo ""
    echo -e "${CYAN}${BOLD}📚 Documentation:${NC}"
    echo -e "  ${BOLD}9)${NC} 📖 View documentation"
    echo -e "  ${BOLD}h)${NC} 🔍 Quick help"
    echo ""
    echo -e "  ${BOLD}0)${NC} ❌ Exit"
    echo ""
}

extract_html() {
    print_header "🌐 Extract HTML from LinkedIn Profile"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 6 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}This will scrape all LinkedIn profile sections:${NC}"
    echo -e "${CYAN}  • Main profile page${NC}"
    echo -e "${CYAN}  • Experience details${NC}"
    echo -e "${CYAN}  • Education details${NC}"
    echo -e "${CYAN}  • Skills, Certifications, Projects, etc.${NC}"
    echo ""
    echo -e "${CYAN}HTML files will be saved in: output/<username>/html/${NC}"
    echo ""
    
    # Get profile URL or username
    echo -e "${CYAN}Enter LinkedIn profile URL or username: ${NC}"
    read profile_input
    
    if [ -z "$profile_input" ]; then
        print_error "No profile provided"
        press_any_key
        return 1
    fi
    
    echo ""
    echo -e "${YELLOW}⏳ Extracting HTML from all sections...${NC}"
    
    # Run the scraper with HTML extraction
    poetry run python -m src.cli "$profile_input" --extract-html --no-banner
    
    press_any_key
}

extract_json() {
    print_header "📊 Extract JSON Data from HTML"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 6 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}This will parse HTML files and extract structured JSON data.${NC}"
    echo -e "${CYAN}Make sure you've run option 1 (Extract HTML) first!${NC}"
    echo ""
    
    # List available HTML directories
    if [ -d "output" ]; then
        echo -e "${CYAN}${BOLD}Available profiles:${NC}"
        for profile_dir in output/*/; do
            if [ -d "$profile_dir" ]; then
                username=$(basename "$profile_dir")
                echo -e "  • $username"
            fi
        done
        echo ""
    fi
    
    # Get username
    echo -e "${CYAN}Enter username (or press Enter to extract from URL): ${NC}"
    read username_input
    
    if [ -z "$username_input" ]; then
        # Get profile URL
        echo -e "${CYAN}Enter LinkedIn profile URL: ${NC}"
        read profile_input
        
        if [ -z "$profile_input" ]; then
            print_error "No username or URL provided"
            press_any_key
            return 1
        fi
        
        # Extract username from URL
        username_input=$(echo "$profile_input" | sed 's|.*linkedin.com/in/||' | sed 's|/||g')
    fi
    
    echo ""
    echo -e "${YELLOW}⏳ Parsing HTML and extracting JSON data...${NC}"
    
    # Run the parser
    poetry run python -m src.cli --parse-html "$username_input" --no-banner
    
    press_any_key
}

generate_cv_pdf() {
    print_header "📄 Generate CV PDF from JSON"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 6 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}This will generate a professional PDF CV from JSON data.${NC}"
    echo -e "${CYAN}Make sure you've run option 2 (Extract JSON) first!${NC}"
    echo ""
    
    # List available JSON files
    if [ -d "output" ]; then
        echo -e "${CYAN}${BOLD}Available profiles:${NC}"
        for profile_dir in output/*/; do
            if [ -d "$profile_dir" ] && [ -f "$profile_dir/profile_data.json" ]; then
                username=$(basename "$profile_dir")
                echo -e "  • $username"
            fi
        done
        echo ""
    fi
    
    # Get username
    echo -e "${CYAN}Enter username: ${NC}"
    read username_input
    
    if [ -z "$username_input" ]; then
        print_error "No username provided"
        press_any_key
        return 1
    fi
    
    # Check if JSON exists
    json_file="output/$username_input/profile_data.json"
    if [ ! -f "$json_file" ]; then
        print_error "JSON file not found: $json_file"
        print_info "Please run option 2 (Extract JSON) first."
        press_any_key
        return 1
    fi
    
    echo ""
    echo -e "${YELLOW}⏳ Generating PDF CV...${NC}"
    
    # Run the PDF generator
    poetry run python -m src.cli --generate-pdf "$username_input" --no-banner
    
    press_any_key
}


login_to_linkedin() {
    print_header "🔐 Login to LinkedIn"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 6 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}This will open a browser for you to log in to LinkedIn.${NC}"
    echo -e "${CYAN}Your session will be saved for future use (~30 days).${NC}"
    echo ""
    echo -e "${YELLOW}Important: Use your real LinkedIn credentials.${NC}"
    echo -e "${YELLOW}Your credentials are NOT stored - only cookies.${NC}"
    echo ""
    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
    
    poetry run python -m src.cli --login --no-banner
    
    press_any_key
}

extract_cookies() {
    print_header "🍪 Extract Cookies from Chrome"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 6 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}This will extract LinkedIn cookies from your running Chrome.${NC}"
    echo -e "${CYAN}Make sure you're logged in to LinkedIn in Chrome!${NC}"
    echo ""
    echo -e "${YELLOW}Note: If Chrome is locked, this may fail.${NC}"
    echo -e "${YELLOW}Try closing Chrome first if you get errors.${NC}"
    echo ""
    read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
    
    poetry run python scripts/extract_cookies.py
    
    press_any_key
}


run_installation() {
    print_header "⚙️ Installation & Setup"
    # Run the installation script
    bash "$SCRIPT_DIR/scripts/install.sh"
    press_any_key
}

run_tests() {
    print_header "🧪 Running Test Suite"
    
    if ! check_poetry; then
        print_error "Poetry not found. Please run option 4 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}Run tests in verbose mode? [y/N]:${NC} "
    read -n 1 verbose
    echo ""
    
    if [[ "$verbose" =~ ^[Yy]$ ]]; then
        bash "$SCRIPT_DIR/scripts/test.sh" -v
    else
        bash "$SCRIPT_DIR/scripts/test.sh"
    fi
    
    press_any_key
}

view_coverage() {
    print_header "📊 Test Coverage Report"
    
    if ! check_poetry; then
        print_error "Poetry not found. Please run option 4 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}Generating coverage report...${NC}"
    poetry run pytest tests/ --cov=src --cov-report=term --cov-report=html -q
    
    echo ""
    echo -e "${GREEN}✓ Coverage report generated!${NC}"
    echo ""
    
    if [ -d "htmlcov" ]; then
        echo -e "${CYAN}Open HTML coverage report in browser? [Y/n]:${NC} "
        read -n 1 open_report
        echo ""
        
        if [[ ! "$open_report" =~ ^[Nn]$ ]]; then
            if command -v xdg-open &> /dev/null; then
                xdg-open htmlcov/index.html
            elif command -v open &> /dev/null; then
                open htmlcov/index.html
            else
                print_info "HTML report available at: htmlcov/index.html"
            fi
        fi
    fi
    
    press_any_key
}

view_documentation() {
    print_header "📖 Documentation"
    
    echo -e "${CYAN}${BOLD}Available Documentation:${NC}"
    echo ""
    echo -e "  ${BOLD}1.${NC} README.md - Full project documentation"
    echo -e "  ${BOLD}2.${NC} CHANGELOG.md - Version history and changes"
    echo -e "  ${BOLD}3.${NC} docs/AUTHENTICATION_GUIDE.md - Authentication help"
    echo -e "  ${BOLD}4.${NC} docs/ - Additional documentation files"
    echo ""
    
    if [ -f "README.md" ]; then
        echo -e "${CYAN}Open README.md? [Y/n]:${NC} "
        read -n 1 open_readme
        echo ""
        
        if [[ ! "$open_readme" =~ ^[Nn]$ ]]; then
            if command -v less &> /dev/null; then
                less README.md
            elif command -v more &> /dev/null; then
                more README.md
            else
                cat README.md
                press_any_key
            fi
        fi
    else
        print_warning "README.md not found"
    fi
    
    echo ""
    echo -e "${CYAN}${BOLD}Quick Links:${NC}"
    echo -e "  ${BLUE}GitHub:${NC} https://github.com/alexcolls/linkedin-cv"
    echo -e "  ${BLUE}Issues:${NC} https://github.com/alexcolls/linkedin-cv/issues"
    echo -e "  ${BLUE}Auth Guide:${NC} docs/AUTHENTICATION_GUIDE.md"
    echo ""
    
    press_any_key
}

show_quick_help() {
    print_header "🔍 Quick Help"
    
    echo -e "${CYAN}${BOLD}Quick Start:${NC}"
    echo -e "  ${BOLD}1.${NC} Run installation (option 6)"
    echo -e "  ${BOLD}2.${NC} Log in to LinkedIn (option 4)"
    echo -e "  ${BOLD}3.${NC} Extract HTML (option 1)"
    echo -e "  ${BOLD}4.${NC} Extract JSON (option 2)"
    echo -e "  ${BOLD}5.${NC} Generate PDF (option 3)"
    echo ""
    
    echo -e "${CYAN}${BOLD}Command Line Usage:${NC}"
    echo -e "  ${GREEN}./run.sh${NC}                         # Interactive menu"
    echo -e "  ${GREEN}./run.sh username${NC}                # Generate CV directly"
    echo -e "  ${GREEN}./run.sh --login${NC}                 # Login directly"
    echo -e "  ${GREEN}./run.sh --help${NC}                  # Show CLI help"
    echo ""
    
    echo -e "${CYAN}${BOLD}Examples:${NC}"
    echo -e "  ${GREEN}./run.sh alex-colls-outumuro${NC}     # Generate CV for username"
    echo -e "  ${GREEN}./run.sh --no-headless${NC}           # Run with visible browser"
    echo -e "  ${GREEN}./run.sh --debug${NC}                 # Run with debug output"
    echo ""
    
    echo -e "${CYAN}${BOLD}Authentication:${NC}"
    echo -e "  • First time: Use option 4 to log in"
    echo -e "  • Session lasts ~30 days"
    echo -e "  • Stored in: ~/.linkedin_session.json"
    echo -e "  • Alternative: Use option 5 to extract from Chrome"
    echo ""
    
    echo -e "${CYAN}${BOLD}Troubleshooting:${NC}"
    echo -e "  • Content masked (*****)? → Log in first (option 4)"
    echo -e "  • Chrome locked? → Try option 5 to extract cookies"
    echo -e "  • Tests failing? → Run option 6 to reinstall"
    echo -e "  • More help: docs/AUTHENTICATION_GUIDE.md"
    echo ""
    
    press_any_key
}

# ═══════════════════════════════════════════════════════════════
# Main Loop
# ═══════════════════════════════════════════════════════════════

main() {
    # If arguments provided, run directly without menu
    if [ $# -gt 0 ]; then
        # Check dependencies
        if ! check_dependencies; then
            print_error "Dependencies not installed."
            print_info "Please run: ./run.sh and select option 6 (Installation)"
            exit 1
        fi
        
        # Run CLI with provided arguments
        poetry run python -m src.cli "$@"
        exit 0
    fi
    
    # Interactive menu loop
    while true; do
        show_menu
        
        read -p "$(echo -e ${CYAN}Enter your choice [0-9/h]: ${NC})" choice
        echo ""
        
        case $choice in
            1)
                extract_html
                ;;
            2)
                extract_json
                ;;
            3)
                generate_cv_pdf
                ;;
            4)
                login_to_linkedin
                ;;
            5)
                extract_cookies
                ;;
            6)
                run_installation
                ;;
            7)
                run_tests
                ;;
            8)
                view_coverage
                ;;
            9)
                view_documentation
                ;;
            h|H)
                show_quick_help
                ;;
            0)
                echo -e "${GREEN}Thank you for using LinkedIn CV Generator! 👋${NC}"
                echo ""
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 0-9 or h."
                sleep 2
                ;;
        esac
    done
}

main "$@"
