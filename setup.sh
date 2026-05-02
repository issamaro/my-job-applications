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

export PLAYWRIGHT_BROWSERS_PATH=0

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

step "Installing Playwright browser..."
uv run playwright install chromium 2>/dev/null
ok "Playwright Chromium"

# ── Node dependencies ─────────────────────────────────────────────────────────

step "Installing Node dependencies..."
bun install --silent
ok "Node dependencies"

# ── API key ───────────────────────────────────────────────────────────────────

setup_api_key() {
    local shell_config="$HOME/.zshrc"
    [[ "$SHELL" == */bash ]] && shell_config="$HOME/.bashrc"

    echo ""
    echo -e "${BOLD}AI provider setup${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "MyCV uses an AI model to tailor your CV."
    echo "You need a free API key from one of these providers:"
    echo ""
    echo -e "  ${BOLD}1) Anthropic (Claude)${NC}  — https://console.anthropic.com/settings/keys"
    echo -e "  ${BOLD}2) Google (Gemini)${NC}     — https://aistudio.google.com/app/apikey"
    echo ""
    echo -n "Which provider? [1/2]: "
    read -r provider_choice

    local var_name
    local provider_label
    if [[ "$provider_choice" == "2" ]]; then
        var_name="GEMINI_API_KEY"
        provider_label="Google Gemini"
    else
        var_name="ANTHROPIC_API_KEY"
        provider_label="Anthropic Claude"
    fi

    if [[ -n "${!var_name}" ]]; then
        ok "$var_name already set — skipping"
        return
    fi

    echo ""
    echo "Open the link above, create an account if needed, and generate a key."
    echo "Paste it here (input is hidden):"
    echo ""
    echo -n "  $var_name: "
    read -rs api_key
    echo ""

    if [[ -z "$api_key" ]]; then
        warn "No key entered — skipping. Set $var_name manually before running the app."
        return
    fi

    local export_line="export $var_name=\"$api_key\""

    if grep -q "^export $var_name=" "$shell_config" 2>/dev/null; then
        sed -i '' "s|^export $var_name=.*|$export_line|" "$shell_config"
        ok "$var_name updated in $shell_config"
    else
        echo "" >> "$shell_config"
        echo "$export_line" >> "$shell_config"
        ok "$var_name saved to $shell_config"
    fi

    export "$var_name=$api_key"

    if [[ "$provider_choice" != "2" ]]; then
        local llm_line='export LLM_PROVIDER="claude"'
        if ! grep -q "^export LLM_PROVIDER=" "$shell_config" 2>/dev/null; then
            echo "$llm_line" >> "$shell_config"
        fi
        export LLM_PROVIDER="claude"
    else
        local llm_line='export LLM_PROVIDER="gemini"'
        if ! grep -q "^export LLM_PROVIDER=" "$shell_config" 2>/dev/null; then
            echo "$llm_line" >> "$shell_config"
        fi
        export LLM_PROVIDER="gemini"
    fi

    ok "$provider_label configured"
}

setup_api_key

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
