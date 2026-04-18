#!/bin/bash

# MyCV Setup
# Installs all dependencies needed to run the app.
# Safe to run multiple times.

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${BOLD}MyCV — Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ── Helpers ──────────────────────────────────────────────────────────────────

step() { echo -e "${BLUE}▸${NC} $1"; }
ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

need_restart=false

# ── Homebrew ─────────────────────────────────────────────────────────────────

if ! command -v brew &>/dev/null; then
    step "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add brew to PATH for Apple Silicon
    if [[ -f /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    ok "Homebrew installed"
else
    ok "Homebrew"
fi

# ── uv (Python manager) ───────────────────────────────────────────────────────

if ! command -v uv &>/dev/null || [[ "$(which uv)" != "/opt/homebrew/bin/uv" ]]; then
    step "Installing uv via Homebrew..."
    # Remove curl-installed version if present
    if [[ -f "$HOME/.local/bin/uv" ]]; then
        warn "Removing curl-installed uv in favour of brew version..."
        rm -f "$HOME/.local/bin/uv" "$HOME/.local/bin/uvx"
    fi
    brew install uv
    ok "uv installed"
else
    ok "uv"
fi

# ── Python 3.13 ───────────────────────────────────────────────────────────────

step "Installing Python 3.13..."
uv python install 3.13 --quiet
ok "Python 3.13"

# ── bun (Node.js runtime + package manager) ────────────────────────────────────

if ! command -v bun &>/dev/null; then
    step "Installing bun via Homebrew..."
    brew install oven-sh/bun/bun
    ok "bun installed"
    need_restart=true
else
    ok "bun"
fi

# ── Python dependencies ───────────────────────────────────────────────────────

step "Installing Python dependencies..."
uv sync --quiet
ok "Python dependencies"

# ── Node dependencies ─────────────────────────────────────────────────────────

step "Installing Node dependencies..."
bun install --silent
ok "Node dependencies"

# ── .env ─────────────────────────────────────────────────────────────────────

if [[ ! -f ".env" ]]; then
    if [[ ! -f ".env.example" ]]; then
        fail ".env.example is missing — run setup.sh from a full git clone of the repo."
    fi
    echo ""
    warn "No .env file found. Creating one now."
    echo "You'll need API keys to use the AI features."
    echo ""
    cp .env.example .env
    warn ".env created from .env.example — open it and fill in your API keys."
else
    ok ".env"
fi

# ── Done ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}Setup complete.${NC}"
echo ""

if $need_restart; then
    warn "Open a new terminal window, then run:"
    echo ""
    echo -e "    ${BOLD}./dev.sh${NC}"
else
    echo -e "Start the app with:"
    echo ""
    echo -e "    ${BOLD}./dev.sh${NC}"
fi

echo ""
