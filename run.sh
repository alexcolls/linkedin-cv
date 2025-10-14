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
source "$SCRIPT_DIR/src/scripts/common.sh"

# Change to project root
cd "$PROJECT_ROOT"

# ═══════════════════════════════════════════════════════════════
# Menu Functions
# ═══════════════════════════════════════════════════════════════

show_menu() {
    clear
    
    # Display the ASCII banner from assets
    if [ -f "$PROJECT_ROOT/src/assets/banner.txt" ]; then
        echo -e "${CYAN}${BOLD}"
        cat "$PROJECT_ROOT/src/assets/banner.txt"
        echo -e "${NC}"
    fi
    
    echo -e "${DIM}Transform your LinkedIn profile into a professional CV${NC}"
    echo ""
    
    echo -e "${CYAN}${BOLD}📋 Main Workflow:${NC}"
    echo -e "  ${BOLD}1)${NC} 📄 Generate CV PDF ${DIM}${NC}"
    echo -e "  ${BOLD}2)${NC} 📊 Extract JSON data ${DIM}${NC}"
    echo -e "  ${BOLD}3)${NC} 🌐 Extract HTML from profile ${DIM}${NC}"
    echo ""
    echo -e "${CYAN}${BOLD}🔐 Authentication (For extracting full data):${NC}"
    echo -e "  ${BOLD}4)${NC} 🔐 Pre-login to LinkedIn (manual setup)"
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

generate_cv_pdf() {
    print_header "📄 Generate CV PDF"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 6 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}This will generate a professional PDF CV from your LinkedIn profile.${NC}"
    echo -e "${CYAN}The process will:${NC}"
    echo -e "${CYAN}  1. Check authentication ${NC}"
    echo -e "${CYAN}  2. Scrape all LinkedIn profile sections${NC}"
    echo -e "${CYAN}  3. Parse and extract data${NC}"
    echo -e "${CYAN}  4. Generate professional PDF CV${NC}"
    echo ""
    
    # Run the CLI (it will handle .env and interactive prompts)
    poetry run python -m src.cli --no-banner
    
    press_any_key
}

extract_json() {
    print_header "📊 Extract JSON Data"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 6 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}This will export the LinkedIn profile data to a JSON file.${NC}"
    echo -e "${CYAN}No PDF will be generated - only raw data extraction.${NC}"
    echo -e "${CYAN}Output will be saved in: output/<username>/profile_data.json${NC}"
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
    echo -e "${YELLOW}⏳ Extracting profile data...${NC}"
    
    # Run the CLI with JSON export flag
    poetry run python -m src.cli "$profile_input" --json --no-banner
    
    # Try to find the generated JSON file
    # Extract username from input
    username=$(echo "$profile_input" | sed 's|.*linkedin.com/in/||' | sed 's|/||g')
    json_file="output/$username/profile_data.json"
    
    if [ -f "$json_file" ]; then
        echo ""
        echo -e "${GREEN}✅ Profile data exported to: $json_file${NC}"
        echo ""
        echo -e "${CYAN}View the JSON file? [Y/n]: ${NC}"
        read -n 1 view_json
        echo ""
        
        if [[ ! "$view_json" =~ ^[Nn]$ ]]; then
            if command -v jq &> /dev/null; then
                jq . "$json_file" | less
            else
                less "$json_file"
            fi
        fi
    else
        # Fallback: check if it was saved with default username
        json_file="output/linkedin-profile/profile_data.json"
        if [ -f "$json_file" ]; then
            echo ""
            echo -e "${GREEN}✅ Profile data exported to: $json_file${NC}"
            echo -e "${YELLOW}Note: Username couldn't be extracted, using default directory${NC}"
        fi
    fi
    
    press_any_key
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
    
    poetry run python src/utils/extract_cookies.py
    
    press_any_key
}


run_installation() {
    print_header "⚙️ Installation & Setup"
    # Run the installation script
    bash "$SCRIPT_DIR/src/scripts/install.sh"
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
        bash "$SCRIPT_DIR/src/scripts/test.sh" -v
    else
        bash "$SCRIPT_DIR/src/scripts/test.sh"
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
    echo -e "  ${BOLD}2.${NC} Generate your CV (option 1)"
    echo -e "  ${DIM}→ Login happens automatically if needed!${NC}"
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
    echo -e "  • 🆕 NEW: Auto-login on first run!"
    echo -e "  • No need to pre-authenticate"
    echo -e "  • Session saved automatically (~30 days)"
    echo -e "  • Stored in: .session/linkedin_session.json"
    echo -e "  • Manual setup: Use option 4 if preferred"
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
                generate_cv_pdf
                ;;
            2)
                extract_json
                ;;
            3)
                extract_html
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
