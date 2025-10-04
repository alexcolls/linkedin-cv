#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🖨️ LinkedIn CV Generator - Test Runner
# ═══════════════════════════════════════════════════════════════

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║          🧪 LinkedIn CV Generator - Test Suite                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

print_step() {
    echo -e "${BLUE}${BOLD}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if verbose mode
VERBOSE=""
if [[ "$1" == "-v" ]] || [[ "$1" == "--verbose" ]]; then
    VERBOSE="-v"
fi

print_header

# Check dependencies
if ! command -v poetry &> /dev/null; then
    print_error "Poetry not found. Please run ./install.sh first"
    exit 1
fi

# Run pytest with coverage
print_step "Running tests with coverage"
if poetry run pytest $VERBOSE tests/ --cov=src --cov-report=term-missing --cov-report=html; then
    print_success "All tests passed!"
else
    print_error "Tests failed"
    exit 1
fi

echo ""

# Run code quality checks
print_step "Running code quality checks"

# Black
echo -n "  Checking code formatting (black)... "
if poetry run black --check src/ tests/ > /dev/null 2>&1; then
    print_success "Passed"
else
    print_error "Failed - run: poetry run black src/ tests/"
fi

# isort
echo -n "  Checking import sorting (isort)... "
if poetry run isort --check-only src/ tests/ > /dev/null 2>&1; then
    print_success "Passed"
else
    print_error "Failed - run: poetry run isort src/ tests/"
fi

# Flake8
echo -n "  Linting code (flake8)... "
if poetry run flake8 src/ tests/ > /dev/null 2>&1; then
    print_success "Passed"
else
    print_error "Failed - check flake8 output"
fi

# MyPy
echo -n "  Type checking (mypy)... "
if poetry run mypy src/ > /dev/null 2>&1; then
    print_success "Passed"
else
    echo -e "${YELLOW}Warnings (check mypy output)${NC}"
fi

echo ""
echo -e "${GREEN}${BOLD}✓ Test suite completed!${NC}"
echo ""
echo -e "${CYAN}Coverage report generated: ${BOLD}htmlcov/index.html${NC}"
