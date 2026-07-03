#!/bin/bash
# MyCV — Run
# Scope: Build the frontend once if missing and serve the app as a single local process.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PLAYWRIGHT_BROWSERS_PATH=0

echo -e "${BLUE}Syncing Python dependencies...${NC}"
uv sync --quiet 2>/dev/null || uv sync

if [[ ! -f public/build/bundle.js ]]; then
    echo -e "${BLUE}Building frontend bundle...${NC}"
    bun run build
fi

if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}Killing existing process on port 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}App running at: ${YELLOW}http://127.0.0.1:8000${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop.${NC}"
echo ""

uv run python -m uvicorn main:app --host 127.0.0.1 --port 8000
