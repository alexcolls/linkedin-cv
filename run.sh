#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🖨️ LinkedIn CV Generator - Interactive Main Menu
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
    print_header "🖨️  LinkedIn CV Generator - Main Menu" "Professional CV generation from LinkedIn profiles"
    
    echo -e "${CYAN}Please select an option:${NC}"
    echo ""
    echo -e "  ${BOLD}1)${NC} 🚀 Generate CV (from URL or .env)"
    echo -e "  ${BOLD}2)${NC} 📂 Generate CV (from saved HTML file)"
    echo -e "  ${BOLD}3)${NC} 📋 Export LinkedIn HTML manually (step-by-step guide)"
    echo -e "  ${BOLD}4)${NC} ⚙️  Run installation/setup"
    echo -e "  ${BOLD}5)${NC} 🧪 Run tests"
    echo -e "  ${BOLD}6)${NC} 📖 View documentation"
    echo -e "  ${BOLD}7)${NC} ❌ Exit"
    echo ""
}

generate_cv_from_url() {
    print_header "🚀 Generate CV from LinkedIn URL"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 4 (Installation) first."
        press_any_key
        return 1
    fi
    
    # Run the CLI (it will handle .env and interactive prompts)
    poetry run python -m src.cli
    
    press_any_key
}

generate_cv_from_html() {
    print_header "📂 Generate CV from Saved HTML File"
    
    # Check dependencies first
    if ! check_dependencies; then
        print_error "Dependencies not installed properly."
        print_info "Please run option 4 (Installation) first."
        press_any_key
        return 1
    fi
    
    echo -e "${CYAN}Enter the path to your LinkedIn HTML file:${NC}"
    read -e -p "Path: " html_file
    
    if [ -z "$html_file" ]; then
        print_error "No file path provided."
        press_any_key
        return 1
    fi
    
    if [ ! -f "$html_file" ]; then
        print_error "File not found: $html_file"
        press_any_key
        return 1
    fi
    
    echo ""
    print_step "Generating CV from HTML file..."
    poetry run python -m src.cli --html-file "$html_file"
    
    press_any_key
}

export_helper() {
    # Run the export helper script
    bash "$SCRIPT_DIR/scripts/export-helper.sh"
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

view_documentation() {
    print_header "📖 Documentation"
    
    echo -e "${CYAN}${BOLD}Available Documentation:${NC}"
    echo ""
    echo -e "  ${BOLD}1.${NC} README.md - Full project documentation"
    echo -e "  ${BOLD}2.${NC} CHANGELOG.md - Version history and changes"
    echo -e "  ${BOLD}3.${NC} docs/ - Additional documentation files"
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
        
        read -p "$(echo -e ${CYAN}Enter your choice [1-7]: ${NC})" choice
        echo ""
        
        case $choice in
            1)
                generate_cv_from_url
                ;;
            2)
                generate_cv_from_html
                ;;
            3)
                export_helper
                ;;
            4)
                run_installation
                ;;
            5)
                run_tests
                ;;
            6)
                view_documentation
                ;;
            7)
                echo -e "${GREEN}Thank you for using LinkedIn CV Generator! 👋${NC}"
                echo ""
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 1-7."
                sleep 2
                ;;
        esac
    done
}

main "$@"
