#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🖨️ LinkedIn CV Generator - Quick Run Script
# ═══════════════════════════════════════════════════════════════

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🖨️  LinkedIn CV Generator${NC}\n"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}Poetry not found. Running installer...${NC}\n"
    chmod +x install.sh
    ./install.sh
    exit 0
fi

# Check if dependencies are installed
if ! poetry env info &> /dev/null || ! poetry run python -c "import rich" &> /dev/null 2>&1; then
    echo -e "${YELLOW}Dependencies not installed. Running installer...${NC}\n"
    chmod +x install.sh
    ./install.sh
    exit 0
fi

# Run the program
echo -e "${GREEN}Starting LinkedIn CV Generator...${NC}\n"
poetry run python -m src.cli "$@"
