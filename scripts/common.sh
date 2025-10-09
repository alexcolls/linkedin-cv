#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🖨️ LinkedIn CV Generator - Common Functions
# ═══════════════════════════════════════════════════════════════
# Shared functions and utilities used across all scripts

# ═══════════════════════════════════════════════════════════════
# Color Definitions
# ═══════════════════════════════════════════════════════════════

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'      # No Color
BOLD='\033[1m'
DIM='\033[2m'

# ═══════════════════════════════════════════════════════════════
# Print Functions
# ═══════════════════════════════════════════════════════════════

print_header() {
    local title="$1"
    local subtitle="${2:-}"
    
    echo -e "${CYAN}${BOLD}"
    echo "================================================================"
    echo "  $title"
    if [ -n "$subtitle" ]; then
        echo "  $subtitle"
    fi
    echo "================================================================"
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

print_dim() {
    echo -e "${DIM}$1${NC}"
}

# ═══════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════

get_project_root() {
    # Get the absolute path to the project root
    cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}

check_command() {
    command -v "$1" >/dev/null 2>&1
}

check_poetry() {
    if check_command poetry; then
        return 0
    else
        return 1
    fi
}

check_dependencies() {
    if ! check_poetry; then
        print_error "Poetry not found"
        return 1
    fi
    
    if ! poetry env info &> /dev/null; then
        print_error "Poetry environment not initialized"
        return 1
    fi
    
    if ! poetry run python -c "import rich" &> /dev/null 2>&1; then
        print_error "Dependencies not installed"
        return 1
    fi
    
    return 0
}

load_env() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ "$key" =~ ^[[:space:]]*# ]] && continue
            [[ -z "$key" ]] && continue
            
            # Remove quotes from value
            value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
            
            # Export the variable
            export "$key=$value"
        done < "$env_file"
        return 0
    fi
    return 1
}

press_any_key() {
    echo ""
    read -n 1 -s -r -p "$(echo -e ${DIM}Press any key to continue...${NC})"
    echo ""
}

confirm() {
    local prompt="$1"
    local default="${2:-n}"
    
    if [ "$default" = "y" ]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi
    
    read -p "$(echo -e ${CYAN}$prompt${NC})" response
    response=${response:-$default}
    
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}
