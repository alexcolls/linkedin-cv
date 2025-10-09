#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🖨️ LinkedIn CV Generator - Test Runner
# ═══════════════════════════════════════════════════════════════

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source common functions
source "$SCRIPT_DIR/common.sh"

# Change to project root
cd "$PROJECT_ROOT"

# Check if verbose mode
VERBOSE=""
if [[ "$1" == "-v" ]] || [[ "$1" == "--verbose" ]]; then
    VERBOSE="-v"
fi

print_header "🧪 LinkedIn CV Generator - Test Suite"

# Check dependencies
if ! check_poetry; then
    print_error "Poetry not found. Please run: ./run.sh and select option 4 (Install)"
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
