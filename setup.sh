#!/bin/bash
# MyCV — Setup
# Scope: Install dependencies and write the LLM provider + API key into a project-local .env.

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

step() { echo -e "${BLUE}▸${NC} $1"; }
ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

create_dependencies() {
    cd "$SCRIPT_DIR"

    export PLAYWRIGHT_BROWSERS_PATH=0

    echo ""
    echo -e "${BOLD}MyCV — Setup${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    if ! command -v brew &>/dev/null; then
        step "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        ok "Homebrew installed"
    else
        ok "Homebrew"
    fi

    if ! command -v uv &>/dev/null || [[ "$(which uv)" != "/opt/homebrew/bin/uv" ]]; then
        step "Installing uv via Homebrew..."
        if [[ -f "$HOME/.local/bin/uv" ]]; then
            warn "Removing curl-installed uv in favour of brew version..."
            rm -f "$HOME/.local/bin/uv" "$HOME/.local/bin/uvx"
        fi
        brew install uv
        ok "uv installed"
    else
        ok "uv"
    fi

    step "Installing Python 3.13..."
    uv python install 3.13 --quiet
    ok "Python 3.13"

    if ! command -v bun &>/dev/null; then
        step "Installing bun via Homebrew..."
        brew install oven-sh/bun/bun
        ok "bun installed"
    else
        ok "bun"
    fi

    step "Installing Python dependencies..."
    uv sync --quiet
    ok "Python dependencies"

    step "Installing Playwright browser..."
    uv run playwright install chromium 2>/dev/null
    ok "Playwright Chromium"

    step "Installing Node dependencies..."
    bun install --silent
    ok "Node dependencies"

    step "Building frontend bundle..."
    bun run build
    ok "Frontend bundle"
}

read_provider_var() {
    local provider="$1"
    case "$provider" in
        gemini) printf 'GEMINI_API_KEY' ;;
        *)      printf 'ANTHROPIC_API_KEY' ;;
    esac
}

read_env_value() {
    local content="$1"
    local var_name="$2"
    printf '%s\n' "$content" | awk -v vk="$var_name" '
        $0 ~ "^" vk "=" { line = $0; sub("^" vk "=", "", line) }
        END { print line }
    '
}

find_key_in_environment() {
    local var_name="$1"
    local value="${!var_name}"
    if [[ -n "$value" ]]; then
        printf '%s' "$value"
    fi
}

read_key_from_pass() {
    local provider="$1"
    local anthropic_entry="anthropic/api-key"
    local gemini_entry="gemini/api-key"

    local entry
    case "$provider" in
        gemini) entry="$gemini_entry" ;;
        *)      entry="$anthropic_entry" ;;
    esac

    if ! command -v pass &>/dev/null; then
        return 0
    fi
    pass show "$entry" 2>/dev/null | head -n1
}

render_key_suffix() {
    local key_value="$1"
    local len=${#key_value}
    if (( len == 0 )); then
        printf '(empty / suspicious — will replace)'
    elif (( len < 4 )); then
        printf '(ends in …%s)' "$key_value"
    else
        printf '(ends in …%s)' "${key_value: -4}"
    fi
}

read_provider_choice() {
    local existing="$1"
    local current_provider
    current_provider="$(read_env_value "$existing" "LLM_PROVIDER")"

    echo ""
    echo -e "${BOLD}AI provider setup${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "MyCV uses an AI model to tailor your CV."
    echo "You need a free API key from one of these providers:"
    echo ""

    local claude_label="Claude"
    local gemini_label="Gemini"
    if [[ "$current_provider" == "claude" ]]; then
        claude_label="Claude  (currently selected)"
    elif [[ "$current_provider" == "gemini" ]]; then
        gemini_label="Gemini  (currently selected)"
    fi

    echo -e "  ${BOLD}[1] $claude_label${NC}  — https://console.anthropic.com/settings/keys"
    echo -e "  ${BOLD}[2] $gemini_label${NC}     — https://aistudio.google.com/app/apikey"
    echo ""
    echo -n "Which provider? [1/2]: "
    local answer
    read -r answer
    case "$answer" in
        2) PROVIDER_CHOICE="gemini" ;;
        *) PROVIDER_CHOICE="claude" ;;
    esac
}

read_key_action() {
    local key_var="$1"
    local existing_key="$2"
    echo ""
    echo "You already have a $key_var in .env $(render_key_suffix "$existing_key")."
    echo "  [1] Keep the existing key"
    echo "  [2] Replace it with a new key"
    echo "  [3] Cancel setup"
    echo -n "Choice [1/2/3]: "
    local answer
    read -r answer
    case "$answer" in
        2) KEY_ACTION="replace" ;;
        3) KEY_ACTION="cancel" ;;
        *) KEY_ACTION="keep" ;;
    esac
}

read_new_key() {
    local provider="$1"
    local label
    case "$provider" in
        gemini) label="Gemini" ;;
        *)      label="Claude" ;;
    esac
    local answer
    while true; do
        echo ""
        echo -n "Paste your $label API key (input hidden), or type 'cancel' to abort. Key: "
        read -rs answer
        echo ""
        if [[ "$answer" == "cancel" ]]; then
            KEY_ACTION="cancel"
            NEW_KEY=""
            return 0
        fi
        if [[ -z "$answer" ]]; then
            warn "No key entered. Paste a key, or type 'cancel' to abort."
            continue
        fi
        if [[ "$answer" == *'"'* || "$answer" == *\\* || "$answer" == *'#'* || "$answer" == *[[:space:]]* ]]; then
            warn "Key contains a quote, backslash, #, or whitespace, which would break .env parsing. Paste a different key, or type 'cancel'."
            continue
        fi
        NEW_KEY="$answer"
        return 0
    done
}

create_env_content() {
    local existing="$1"
    local provider="$2"
    local key_value="$3"
    local key_var
    key_var="$(read_provider_var "$provider")"

    local filtered
    filtered="$(printf '%s\n' "$existing" \
        | awk -v vp="LLM_PROVIDER" -v vk="$key_var" '
            $0 ~ "^" vp "=" { next }
            $0 ~ "^" vk "=" { next }
            { print }
          ')"

    local kept_key=""
    if [[ -z "$key_value" ]]; then
        kept_key="$(read_env_value "$existing" "$key_var")"
    fi

    if [[ -n "$filtered" ]]; then
        printf '%s\n' "$filtered"
    fi
    printf 'LLM_PROVIDER=%s\n' "$provider"
    if [[ -n "$key_value" ]]; then
        printf '%s=%s\n' "$key_var" "$key_value"
    elif [[ -n "$kept_key" ]]; then
        printf '%s=%s\n' "$key_var" "$kept_key"
    fi
}

write_env_atomic() {
    local new_content="$1"
    local target="$2"
    local tmp="${target}.tmp.$$"

    local prev_umask
    prev_umask="$(umask)"
    umask 077
    if ! printf '%s' "$new_content" > "$tmp" 2>/dev/null; then
        umask "$prev_umask"
        rm -f "$tmp" 2>/dev/null
        return 1
    fi
    umask "$prev_umask"

    if [[ -e "$target" ]]; then
        local original_mode
        original_mode="$(stat -f '%Lp' "$target" 2>/dev/null || stat -c '%a' "$target" 2>/dev/null || true)"
        if [[ -n "$original_mode" ]]; then
            chmod "$original_mode" "$tmp" 2>/dev/null || true
        fi
    fi

    if ! mv "$tmp" "$target" 2>/dev/null; then
        rm -f "$tmp" 2>/dev/null
        return 1
    fi
    return 0
}

render_env_summary() {
    local provider="$1"
    local env_path="$2"
    local key_var
    key_var="$(read_provider_var "$provider")"
    local key_value
    key_value="$(read_env_value "$(cat "$env_path")" "$key_var")"

    echo ""
    echo -e "${BOLD}Configuration written to ./.env${NC}"
    printf '  LLM_PROVIDER:  %s\n' "$provider"
    if [[ -n "$key_value" ]]; then
        printf '  %s:  set %s\n' "$key_var" "$(render_key_suffix "$key_value")"
    else
        printf '  %s:  not set\n' "$key_var"
    fi
}

render_done_banner() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}${BOLD}✓ Setup complete.${NC}"
    echo ""
    echo -e "Use it:   ${BOLD}./run.sh${NC}   ·   Develop: ${BOLD}./dev.sh${NC}"
    echo ""
}

render_cancel_message() {
    echo ""
    echo "Setup cancelled. No changes made."
}

update_provider_and_key() {
    local env_path="$SCRIPT_DIR/.env"
    local example_path="$SCRIPT_DIR/.env.example"

    local existing_content=""
    if [[ -f "$env_path" ]]; then
        existing_content="$(cat "$env_path")"
    elif [[ -f "$example_path" ]]; then
        existing_content="$(cat "$example_path")"
    fi

    PROVIDER_CHOICE=""
    KEY_ACTION=""
    NEW_KEY=""
    local cancel_requested=false

    trap 'cancel_requested=true; render_cancel_message; trap - INT; return 0' INT
    trap 'rm -f "$SCRIPT_DIR/.env.tmp.$$" 2>/dev/null' EXIT

    read_provider_choice "$existing_content"
    if $cancel_requested; then return 0; fi

    local key_var
    key_var="$(read_provider_var "$PROVIDER_CHOICE")"

    local env_key
    env_key="$(find_key_in_environment "$key_var")"
    if [[ -n "$env_key" ]]; then
        trap - INT
        ok "$key_var already configured in your environment $(render_key_suffix "$env_key")."
        echo "Nothing to write — the app reads it live; a .env value would only be shadowed."
        render_done_banner
        return 0
    fi

    local pass_key
    pass_key="$(read_key_from_pass "$PROVIDER_CHOICE")"
    if [[ -n "$pass_key" ]]; then
        NEW_KEY="$pass_key"
        KEY_ACTION="replace"
        ok "Read $key_var from pass."
    else
        local existing_key
        existing_key="$(read_env_value "$existing_content" "$key_var")"
        if [[ -n "$existing_key" ]]; then
            read_key_action "$key_var" "$existing_key"
            if $cancel_requested; then return 0; fi
            case "$KEY_ACTION" in
                cancel)  render_cancel_message; trap - INT; return 0 ;;
                keep)    NEW_KEY="" ;;
                replace) read_new_key "$PROVIDER_CHOICE" ;;
            esac
        else
            read_new_key "$PROVIDER_CHOICE"
        fi
    fi
    if $cancel_requested; then return 0; fi
    if [[ "$KEY_ACTION" == "cancel" ]]; then
        render_cancel_message
        trap - INT
        return 0
    fi

    trap - INT

    local new_content
    new_content="$(create_env_content "$existing_content" "$PROVIDER_CHOICE" "$NEW_KEY")"
    if ! write_env_atomic "$new_content" "$env_path"; then
        fail "Failed to write $env_path (disk full? permissions?). Original is unchanged."
    fi

    if [[ "$KEY_ACTION" == "keep" ]]; then
        ok "Kept existing $key_var."
    fi

    render_env_summary "$PROVIDER_CHOICE" "$env_path"
    render_done_banner
    return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    create_dependencies
    update_provider_and_key
fi
