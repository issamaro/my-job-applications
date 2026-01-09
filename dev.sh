#!/bin/bash

# MyCV Development Server
# Runs FastAPI backend + Svelte frontend concurrently

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       MyCV Development Server            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo -e "${YELLOW}Copy .env.example to .env and configure your API keys${NC}"
    exit 1
fi

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait 2>/dev/null
    echo -e "${GREEN}Servers stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Activate Python virtual environment if exists
if [ -d ".venv" ]; then
    echo -e "${GREEN}Activating Python virtual environment...${NC}"
    source .venv/bin/activate
fi

# Sync Python dependencies with uv
echo -e "${BLUE}Syncing Python dependencies...${NC}"
uv sync --quiet 2>/dev/null || uv sync

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing npm dependencies...${NC}"
    npm install
fi

# Start Rollup/Svelte watcher in background (CSS is bundled automatically)
echo -e "${GREEN}Starting Svelte build watcher...${NC}"
npm run dev &
FRONTEND_PID=$!

# Give frontend a moment to start
sleep 2

# Kill any existing process on port 8000
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}Killing existing process on port 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Start FastAPI backend
echo -e "${GREEN}Starting FastAPI backend...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}App running at: ${YELLOW}http://localhost:8000${NC}"
echo -e "${GREEN}API docs at:    ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for all background processes
wait
