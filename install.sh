#!/usr/bin/env bash
#
# LinkedIn CV - Installation Script
#
# This script provides two installation modes:
# 1. System Installation: Installs globally with 'linkedin-cv' command
# 2. Development Installation: Installs with Poetry for local testing
#
# Usage: ./install.sh [--system|--dev|--both] [--dry-run]
#

# Note: We don't use 'set -e' to allow graceful error handling

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Installation markers
SYSTEM_MARKER="$SCRIPT_DIR/.system-installed"
DEV_MARKER="$SCRIPT_DIR/.dev-installed"

# Print functions
print_header() {
    echo -e "\n${CYAN}================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================================${NC}\n"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Banner
print_header "LinkedIn CV - Installation"
echo -e "  📄 Generate professional PDF CVs from LinkedIn profiles"
echo -e "  🚀 Powered by Playwright & WeasyPrint\n"

# Check for existing installations
HAS_SYSTEM=false
HAS_DEV=false

if [[ -f "$SYSTEM_MARKER" ]]; then
    HAS_SYSTEM=true
    print_success "System installation detected"
    print_info "LinkedIn CV is installed globally as 'linkedin-cv'"
fi

if [[ -f "$DEV_MARKER" ]]; then
    HAS_DEV=true
    print_success "Development installation detected"
    print_info "LinkedIn CV is installed locally with Poetry"
fi

# Show current status
if [[ "$HAS_SYSTEM" == true ]] || [[ "$HAS_DEV" == true ]]; then
    echo ""
    print_info "Current installations:"
    if [[ "$HAS_SYSTEM" == true ]]; then
        echo -e "  ${GREEN}✓${NC} System (linkedin-cv)"
    fi
    if [[ "$HAS_DEV" == true ]]; then
        echo -e "  ${GREEN}✓${NC} Development (./run.sh)"
    fi
    echo ""
fi

# Parse arguments
INSTALL_MODE=""
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --system) INSTALL_MODE="system"; shift ;;
        --dev) INSTALL_MODE="dev"; shift ;;
        --both) INSTALL_MODE="both"; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        *) ;;
    esac
done

if [[ "$DRY_RUN" == true ]]; then
    print_warning "DRY RUN MODE - No actual installation will be performed"
    echo ""
fi

# Ask installation mode if not specified
if [[ -z "$INSTALL_MODE" ]] && [[ "$DRY_RUN" == false ]]; then
    print_header "Installation Mode Selection"
    echo -e "${CYAN}Choose installation type:${NC}\n"
    echo -e "  ${GREEN}1)${NC} ${BOLD}System Installation${NC} (Recommended)"
    echo -e "     • Installs globally with 'linkedin-cv' command"
    echo -e "     • Available system-wide"
    echo -e "     • Easier to use\n"
    echo -e "  ${GREEN}2)${NC} ${BOLD}Development Installation${NC}"
    echo -e "     • Installs locally with Poetry"
    echo -e "     • For testing and development"
    echo -e "     • Run with './run.sh'\n"
    echo -e "  ${GREEN}3)${NC} ${BOLD}Both System + Development${NC}"
    echo -e "     • Installs both modes"
    echo -e "     • Best of both worlds\n"
    
    while true; do
        read -p "$(echo -e ${MAGENTA}Enter choice [1/2/3]: ${NC})" choice
        case $choice in
            1 ) INSTALL_MODE="system"; break;;
            2 ) INSTALL_MODE="dev"; break;;
            3 ) INSTALL_MODE="both"; break;;
            * ) print_error "Invalid choice. Please enter 1, 2, or 3.";;
        esac
    done
elif [[ -z "$INSTALL_MODE" ]] && [[ "$DRY_RUN" == true ]]; then
    # Default to system mode for dry run
    INSTALL_MODE="system"
    print_info "Dry run: using system installation mode"
fi

# Check Python Installation
print_header "Step 1: Checking Python Installation"

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
        
        print_success "Python found: $PYTHON_VERSION"
        
        if [[ "$PYTHON_MAJOR" -ge 3 ]] && [[ "$PYTHON_MINOR" -ge 9 ]]; then
            print_success "Python version is compatible (>= 3.9)"
            return 0
        else
            print_error "Python version must be >= 3.9"
            print_info "Current version: $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

if ! check_python; then
    print_info "Installing Python 3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
    if check_python; then
        print_success "Python 3 installed"
    else
        print_error "Failed to install Python 3"
        exit 1
    fi
fi

# Check and Install Poetry
print_header "Step 2: Checking Poetry Installation"

if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version | cut -d' ' -f3 | tr -d ')')
    print_success "Poetry found: $POETRY_VERSION"
else
    print_warning "Poetry not found"
    print_info "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    
    if command -v poetry &> /dev/null; then
        print_success "Poetry installed successfully"
    else
        print_error "Poetry installation failed"
        exit 1
    fi
fi

# Ensure Poetry is in PATH
if ! command -v poetry &> /dev/null; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install System Dependencies
print_header "Step 3: Installing System Dependencies"

# Check for rsync (needed for system installation)
if [[ "$INSTALL_MODE" == "system" ]] || [[ "$INSTALL_MODE" == "both" ]]; then
    if ! command -v rsync &> /dev/null; then
        print_warning "rsync not found, installing..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y -qq rsync 2>/dev/null || print_error "Failed to install rsync"
        fi
        if command -v rsync &> /dev/null; then
            print_success "rsync installed"
        else
            print_error "rsync is required for system installation"
            print_info "Please install rsync: sudo apt-get install rsync"
            exit 1
        fi
    fi
fi

print_step "Installing WeasyPrint and Playwright dependencies..."

if command -v apt-get &> /dev/null; then
    print_info "Updating package lists..."
    sudo apt-get update -qq 2>/dev/null || print_warning "Could not update package lists"
    
    # WeasyPrint dependencies - install individually to handle missing packages
    PACKAGES=(
        "libpango-1.0-0"
        "libpangocairo-1.0-0"
        "libgdk-pixbuf-2.0-0"  # Correct package name (with hyphens)
        "libffi-dev"
        "libcairo2"
        "libcairo2-dev"
        "shared-mime-info"
        "libpangoft2-1.0-0"  # Additional dependency
        "fonts-dejavu-core"  # Font support
    )
    
    FAILED_PACKAGES=()
    for pkg in "${PACKAGES[@]}"; do
        if dpkg -l | grep -q "^ii  $pkg"; then
            print_info "$pkg already installed"
        else
            if sudo apt-get install -y -qq "$pkg" 2>/dev/null; then
                print_success "Installed $pkg"
            else
                print_warning "Could not install $pkg (may not be needed)"
                FAILED_PACKAGES+=("$pkg")
            fi
        fi
    done
    
    if [ ${#FAILED_PACKAGES[@]} -eq 0 ]; then
        print_success "All system dependencies installed"
    else
        print_warning "Some packages could not be installed: ${FAILED_PACKAGES[*]}"
        print_info "This may not affect functionality"
    fi
fi

# MODE-SPECIFIC INSTALLATION

if [[ "$INSTALL_MODE" == "system" ]] || [[ "$INSTALL_MODE" == "both" ]]; then
    print_header "System Installation"
    
    print_step "Installing LinkedIn CV globally..."
    
    # Configure Poetry
    poetry config virtualenvs.create true --local
    poetry config virtualenvs.in-project false --local
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    if poetry install --no-interaction --quiet 2>&1 | tee /tmp/poetry-install.log | grep -q "error\|Error\|ERROR"; then
        print_error "Failed to install Python dependencies"
        print_info "Check /tmp/poetry-install.log for details"
        exit 1
    fi
    print_success "Python dependencies installed"
    
    # Create wrapper script in user's local bin
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
    
    WRAPPER_SCRIPT="$BIN_DIR/linkedin-cv"
    
    cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/usr/bin/env bash
# LinkedIn CV - System wrapper script
PROJECT_DIR="$HOME/.linkedin-cv-installation"

if [[ -d "$PROJECT_DIR" ]]; then
    # Preserve the user's working directory
    export LINKEDIN_CV_CWD="$(pwd)"
    cd "$PROJECT_DIR"
    exec poetry run python -m src.cli "$@"
else
    echo "Error: LinkedIn CV installation not found at $PROJECT_DIR"
    exit 1
fi
EOF
    
    chmod +x "$WRAPPER_SCRIPT"
    
    # Copy project to installation directory
    INSTALL_DIR="$HOME/.linkedin-cv-installation"
    print_info "Installing to $INSTALL_DIR..."
    
    mkdir -p "$INSTALL_DIR"
    rsync -a --exclude='.git' --exclude='__pycache__' --exclude='.venv' --exclude='data' \
        --exclude='output' --exclude='.pytest_cache' \
        "$SCRIPT_DIR/" "$INSTALL_DIR/"
    
    # Install dependencies in the installation directory
    print_info "Installing dependencies in installation directory..."
    cd "$INSTALL_DIR"
    poetry config virtualenvs.create true --local
    poetry config virtualenvs.in-project false --local
    
    if ! poetry install --no-interaction 2>&1 | tee /tmp/poetry-install-system.log; then
        print_error "Failed to install Python dependencies"
        print_info "Check /tmp/poetry-install-system.log for details"
        cd "$SCRIPT_DIR"
        exit 1
    fi
    print_success "Python dependencies installed"
    
    # Install Playwright browsers
    print_info "Installing Playwright browsers (this may take a few minutes)..."
    if ! poetry run playwright install chromium --with-deps 2>&1 | tee /tmp/playwright-install.log; then
        print_warning "Playwright browser installation had issues"
        print_info "You may need to run: playwright install chromium --with-deps"
    else
        print_success "Playwright browsers installed"
    fi
    
    cd "$SCRIPT_DIR"
    
    # Create marker
    touch "$SYSTEM_MARKER"
    echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$SYSTEM_MARKER"
    
    touch "$INSTALL_DIR/.system-installed"
    echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$INSTALL_DIR/.system-installed"
    
    print_success "System installation complete!"
    echo ""
    print_info "Command available: ${GREEN}linkedin-cv${NC}"
    print_info "Installation directory: $INSTALL_DIR"
    echo ""
fi

if [[ "$INSTALL_MODE" == "dev" ]] || [[ "$INSTALL_MODE" == "both" ]]; then
    print_header "Development Installation"
    
    print_step "Installing LinkedIn CV for development..."
    
    # Configure Poetry
    poetry config virtualenvs.create true --local
    poetry config virtualenvs.in-project false --local
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    if ! poetry install --no-interaction 2>&1 | tee /tmp/poetry-install-dev.log; then
        print_error "Failed to install Python dependencies"
        print_info "Check /tmp/poetry-install-dev.log for details"
        exit 1
    fi
    print_success "Python dependencies installed"
    
    # Install Playwright browsers
    print_info "Installing Playwright browsers (this may take a few minutes)..."
    if ! poetry run playwright install chromium --with-deps 2>&1 | tee /tmp/playwright-install-dev.log; then
        print_warning "Playwright browser installation had issues"
        print_info "You may need to run: poetry run playwright install chromium --with-deps"
    else
        print_success "Playwright browsers installed"
    fi
    
    # Create .env if not exists
    if [[ ! -f ".env" ]]; then
        cp .env.sample .env
        print_success "Created .env file"
        print_warning "Remember to edit .env with your configuration!"
    fi
    
    # Create marker
    touch "$DEV_MARKER"
    echo "$(date '+%Y-%m-%d %H:%M:%S')" > "$DEV_MARKER"
    
    print_success "Development installation complete!"
    echo ""
    print_info "Run with: ${GREEN}./run.sh${NC}"
    echo ""
fi

# Completion
print_header "Installation Complete! 🎉"

if [[ "$INSTALL_MODE" == "system" ]]; then
    echo -e "${GREEN}✓ System installation successful${NC}\n"
    echo -e "${CYAN}Quick Start:${NC}"
    echo -e "  ${YELLOW}linkedin-cv --help${NC}  # See available options"
    echo -e "  ${YELLOW}linkedin-cv https://linkedin.com/in/username${NC}  # Generate CV\n"
elif [[ "$INSTALL_MODE" == "dev" ]]; then
    echo -e "${GREEN}✓ Development installation successful${NC}\n"
    echo -e "${CYAN}Quick Start:${NC}"
    echo -e "  ${YELLOW}./run.sh --help${NC}  # Run the CLI\n"
    echo -e "${CYAN}Configure:${NC}"
    echo -e "  ${YELLOW}nano .env${NC}  # Edit configuration\n"
elif [[ "$INSTALL_MODE" == "both" ]]; then
    echo -e "${GREEN}✓ Both installations successful${NC}\n"
    echo -e "${CYAN}Quick Start:${NC}"
    echo -e "  ${YELLOW}linkedin-cv${NC}  # System command (anywhere)"
    echo -e "  ${YELLOW}./run.sh${NC}     # Development mode\n"
fi

echo -e "${CYAN}Uninstall:${NC}"
echo -e "  ${YELLOW}./uninstall.sh${NC}\n"

echo -e "${CYAN}Documentation:${NC} See README.md\n"

exit 0
