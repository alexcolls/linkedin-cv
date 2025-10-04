#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🖨️ LinkedIn CV Generator - Easy Installer
# ═══════════════════════════════════════════════════════════════

set -e  # Exit on any error

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           🖨️  LinkedIn CV Generator Installer                  ║"
    echo "║      Generate Beautiful PDFs from LinkedIn Profiles            ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_step() {
    echo -e "\n${MAGENTA}${BOLD}▶ $1${NC}"
}

# ═══════════════════════════════════════════════════════════════
# System Detection
# ═══════════════════════════════════════════════════════════════

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            PACKAGE_MANAGER="apt"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            PACKAGE_MANAGER="yum"
        else
            OS="linux"
            PACKAGE_MANAGER="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    else
        OS="unknown"
        PACKAGE_MANAGER="unknown"
    fi
}

# ═══════════════════════════════════════════════════════════════
# Dependency Checking
# ═══════════════════════════════════════════════════════════════

check_command() {
    command -v "$1" >/dev/null 2>&1
}

check_python() {
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            print_success "Python $PYTHON_VERSION detected"
            return 0
        else
            print_warning "Python $PYTHON_VERSION found, need Python 3.9+"
            return 1
        fi
    else
        print_warning "Python 3 not found"
        return 1
    fi
}

check_poetry() {
    if check_command poetry; then
        print_success "Poetry detected"
        return 0
    else
        print_warning "Poetry not found"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════
# Installation Functions
# ═══════════════════════════════════════════════════════════════

install_python() {
    print_step "Installing Python 3.9+"
    
    case $OS in
        debian)
            print_info "Installing Python using apt..."
            sudo apt update
            sudo apt install -y python3 python3-venv python3-pip
            ;;
        macos)
            if ! check_command brew; then
                print_info "Installing Homebrew first..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            print_info "Installing Python using brew..."
            brew install python@3.9
            ;;
        *)
            print_error "Automatic Python installation not supported"
            print_info "Install Python 3.9+ from: https://www.python.org/downloads/"
            exit 1
            ;;
    esac
}

install_poetry() {
    print_step "Installing Poetry"
    
    if check_command poetry; then
        print_success "Poetry already installed"
        return 0
    fi
    
    print_info "Downloading Poetry installer..."
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add to PATH
    export PATH="$HOME/.local/bin:$PATH"
    
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_RC="$HOME/.zshrc"
    else
        SHELL_RC="$HOME/.bashrc"
    fi
    
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$SHELL_RC"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    fi
    
    if check_command poetry; then
        print_success "Poetry installed!"
    else
        print_error "Poetry installation failed"
        exit 1
    fi
}

install_system_deps() {
    print_step "Installing system dependencies for WeasyPrint"
    
    case $OS in
        debian)
            print_info "Installing Cairo, Pango, and GDK-PixBuf..."
            sudo apt install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
                libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
            ;;
        macos)
            print_info "Installing dependencies with Homebrew..."
            brew install cairo pango gdk-pixbuf libffi
            ;;
        *)
            print_warning "Please install Cairo and Pango manually"
            ;;
    esac
    
    print_success "System dependencies installed"
}

install_dependencies() {
    print_step "Installing Python dependencies"
    
    print_info "This may take 2-5 minutes... ☕"
    poetry install
    
    print_success "Dependencies installed"
}

install_playwright() {
    print_step "Installing Playwright browsers"
    
    print_info "Downloading Chromium browser..."
    poetry run playwright install chromium
    
    print_success "Playwright browser installed"
}

setup_directories() {
    print_step "Setting up directories"
    
    mkdir -p output
    
    print_success "Directories created"
}

setup_pre_commit() {
    print_step "Setting up pre-commit hooks"
    
    poetry run pre-commit install || print_warning "Pre-commit setup skipped"
    
    print_success "Pre-commit hooks configured"
}

# ═══════════════════════════════════════════════════════════════
# Main Installation Flow
# ═══════════════════════════════════════════════════════════════

main() {
    print_header
    
    print_step "Detecting system"
    detect_os
    print_info "OS: $OS"
    print_info "Package Manager: $PACKAGE_MANAGER"
    
    # Check Python
    if ! check_python; then
        install_python
    fi
    
    # Check Poetry
    if ! check_poetry; then
        install_poetry
    fi
    
    # Install system dependencies
    install_system_deps
    
    # Install Python dependencies
    install_dependencies
    
    # Install Playwright
    install_playwright
    
    # Setup directories
    setup_directories
    
    # Setup pre-commit
    setup_pre_commit
    
    # Success message
    echo ""
    echo -e "${GREEN}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║               ✓ Installation Complete!                        ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}${BOLD}Quick Start:${NC}"
    echo -e "  ${BLUE}./run.sh https://www.linkedin.com/in/your-username/${NC}"
    echo ""
    echo -e "${CYAN}${BOLD}Or use Poetry directly:${NC}"
    echo -e "  ${BLUE}poetry run python -m src.cli https://www.linkedin.com/in/your-username/${NC}"
    echo ""
    echo -e "${CYAN}${BOLD}Run tests:${NC}"
    echo -e "  ${BLUE}./test.sh${NC}"
    echo ""
}

main "$@"
