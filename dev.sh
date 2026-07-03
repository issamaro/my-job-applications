#!/bin/bash
# MyCV — Develop
# Scope: Run the Svelte watch build and the auto-reloading FastAPI backend together.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PLAYWRIGHT_BROWSERS_PATH=0

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       MyCV Development Server            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"

cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait 2>/dev/null
    echo -e "${GREEN}Servers stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo -e "${BLUE}Syncing Python dependencies...${NC}"
uv sync --quiet 2>/dev/null || uv sync

if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}Killing existing process on port 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

echo -e "${GREEN}Starting Svelte build watcher...${NC}"
bun run dev &
FRONTEND_PID=$!

echo -e "${GREEN}Starting FastAPI backend...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}App running at: ${YELLOW}http://localhost:8000${NC}"
echo -e "${GREEN}API docs at:    ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

wait
