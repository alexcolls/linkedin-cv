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
    print_header "🖨️ LinkedIn CV Generator - Main Menu" "Professional CV generation from LinkedIn profiles"
    
    echo -e "${CYAN}${BOLD}📋 Main Operations:${NC}"
    echo -e "  ${BOLD}1)${NC} 🚀 Generate CV (from URL or .env)"
    echo -e "  ${BOLD}2)${NC} 🔐 Login to LinkedIn (save session)"
    echo -e "  ${BOLD}3)${NC} 🍪 Extract cookies from Chrome"
    echo ""
    echo -e "${CYAN}${BOLD}🔧 Setup & Testing:${NC}"
    echo -e "  ${BOLD}4)${NC} ⚙️  Run installation/setup"
    echo -e "  ${BOLD}5)${NC} 🧪 Run tests"
    echo -e "  ${BOLD}6)${NC} 📊 View test coverage"
    echo ""
    echo -e "${CYAN}${BOLD}📚 Documentation:${NC}"
    echo -e "  ${BOLD}7)${NC} 📖 View documentation"
    echo -e "  ${BOLD}8)${NC} 🔍 Quick help"
    echo ""
    echo -e "  ${BOLD}9)${NC} ❌ Exit"
    echo ""
}

generate_cv_from_url() {
    print_header "🚀 Generate CV from LinkedIn URL"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 3 (Installation) first."
        press_any_key
        return 1
    fi
    
    # Run the CLI (it will handle .env and interactive prompts)
    poetry run python -m src.cli
    
    press_any_key
}

login_to_linkedin() {
    print_header "🔐 Login to LinkedIn"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 4 (Installation) first."
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
    
    poetry run python -m src.cli --login
    
    press_any_key
}

extract_cookies() {
    print_header "🍪 Extract Cookies from Chrome"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 4 (Installation) first."
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
    echo -e "  ${BOLD}1.${NC} Run installation (option 4)"
    echo -e "  ${BOLD}2.${NC} Log in to LinkedIn (option 2)"
    echo -e "  ${BOLD}3.${NC} Generate your CV (option 1)"
    echo ""
    
    echo -e "${CYAN}${BOLD}Command Line Usage:${NC}"
    echo -e "  ${GREEN}./run.sh${NC}                          # Interactive menu"
    echo -e "  ${GREEN}./run.sh username${NC}                # Generate CV directly"
    echo -e "  ${GREEN}./run.sh --login${NC}                 # Login directly"
    echo -e "  ${GREEN}./run.sh --help${NC}                  # Show CLI help"
    echo ""
    
    echo -e "${CYAN}${BOLD}Examples:${NC}"
    echo -e "  ${GREEN}./run.sh alex-colls-outumuro${NC}    # Generate CV for username"
    echo -e "  ${GREEN}./run.sh --no-headless${NC}           # Run with visible browser"
    echo -e "  ${GREEN}./run.sh --debug${NC}                 # Run with debug output"
    echo ""
    
    echo -e "${CYAN}${BOLD}Authentication:${NC}"
    echo -e "  • First time: Use option 2 to log in"
    echo -e "  • Session lasts ~30 days"
    echo -e "  • Stored in: ~/.linkedin_session.json"
    echo -e "  • Alternative: Use option 3 to extract from Chrome"
    echo ""
    
    echo -e "${CYAN}${BOLD}Troubleshooting:${NC}"
    echo -e "  • Content masked (*****)? → Log in first (option 2)"
    echo -e "  • Chrome locked? → Try option 3 to extract cookies"
    echo -e "  • Tests failing? → Run option 4 to reinstall"
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
            print_info "Please run: ./run.sh and select option 4 (Installation)"
            exit 1
        fi
        
        # Run CLI with provided arguments
        poetry run python -m src.cli "$@"
        exit 0
    fi
    
    # Interactive menu loop
    while true; do
        show_menu
        
        read -p "$(echo -e ${CYAN}Enter your choice [1-9]: ${NC})" choice
        echo ""
        
        case $choice in
            1)
                generate_cv_from_url
                ;;
            2)
                login_to_linkedin
                ;;
            3)
                extract_cookies
                ;;
            4)
                run_installation
                ;;
            5)
                run_tests
                ;;
            6)
                view_coverage
                ;;
            7)
                view_documentation
                ;;
            8)
                show_quick_help
                ;;
            9)
                echo -e "${GREEN}Thank you for using LinkedIn CV Generator! 👋${NC}"
                echo ""
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 1-9."
                sleep 2
                ;;
        esac
    done
}

main "$@"
