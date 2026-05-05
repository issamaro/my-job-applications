#!/bin/bash
# MyCV — Setup
# Scope: Install dependencies and write LLM provider + API key into the user's shell-rc atomically.

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

need_restart=false

create_dependencies() {
    cd "$SCRIPT_DIR"

    export PLAYWRIGHT_BROWSERS_PATH=0

    echo ""
    echo -e "${BOLD}MyCV — Setup${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    need_restart=false

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
        need_restart=true
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
}

find_current_shell() {
    if [[ -n "$SHELL" ]]; then
        case "$(basename "$SHELL")" in
            zsh)  printf 'zsh';  return ;;
            bash) printf 'bash'; return ;;
        esac
    fi
    case "$(ps -p $PPID -o comm= 2>/dev/null)" in
        *zsh)  printf 'zsh' ;;
        *bash) printf 'bash' ;;
        *)     printf 'zsh' ;;
    esac
}

find_rc_candidates() {
    local shell_name="$1"
    case "$shell_name" in
        zsh)
            printf '%s\n' "$HOME/.zshenv" "$HOME/.zprofile" "$HOME/.zshrc" "$HOME/.profile"
            ;;
        bash)
            printf '%s\n' "$HOME/.bash_profile" "$HOME/.bashrc" "$HOME/.profile"
            ;;
        *)
            printf '%s\n' "$HOME/.${shell_name}rc"
            ;;
    esac
}

read_rc_path() {
    local shell_name="$1"
    local rc_path="$HOME/.${shell_name}rc"
    local rc_target

    if [[ -L "$rc_path" ]]; then
        rc_target="$(readlink "$rc_path")"
        if [[ "$rc_target" != /* ]]; then
            rc_target="$(dirname "$rc_path")/$rc_target"
        fi
    else
        rc_target="$rc_path"
    fi

    printf '%s' "$rc_target"
}

find_chain_warning() {
    local rc_path="$1"
    local rc_target="$2"
    if [[ -L "$rc_target" ]]; then
        warn "Note: ${rc_path/#$HOME/~} resolves through a symlink chain; only the first hop ($rc_target) will be written."
        warn "      If you use a managed dotfiles repo, verify the result manually after setup."
    fi
}

read_rc_content() {
    local rc_target="$1"
    if [[ -f "$rc_target" ]]; then
        cat "$rc_target"
    else
        printf ''
    fi
}

find_var_count() {
    local rc_content="$1"
    local var_name="$2"
    printf '%s\n' "$rc_content" \
        | awk -v vn="$var_name" '$0 ~ "^export " vn "=" { n++ } END { print n+0 }'
}

find_var_value() {
    local rc_content="$1"
    local var_name="$2"
    printf '%s\n' "$rc_content" \
        | awk -v vn="$var_name" '
            $0 ~ "^export " vn "=\"" {
                line = $0
            }
            END {
                if (line == "") exit
                sub("^export " vn "=\"", "", line)
                sub("\"$", "", line)
                print line
            }
          '
}

find_key_in_files() {
    local var_name="$1"
    local shell_name="$2"
    local candidate file_content count value
    while IFS= read -r candidate; do
        [[ -z "$candidate" ]] && continue
        file_content="$(read_rc_content "$candidate")"
        count="$(find_var_count "$file_content" "$var_name")"
        if (( count > 0 )); then
            value="$(find_var_value "$file_content" "$var_name")"
            if [[ -n "$value" ]]; then
                printf '%s\t%s' "$candidate" "$value"
                return 0
            fi
        fi
    done < <(find_rc_candidates "$shell_name")
    return 1
}

find_key_in_environment() {
    local var_name="$1"
    local value="${!var_name}"
    if [[ -n "$value" ]]; then
        printf '%s' "$value"
    fi
}

find_var_with_source() {
    local var_name="$1"
    local shell_name="$2"
    local hit env_value
    VAR_VALUE=""
    VAR_SOURCE=""
    hit="$(find_key_in_files "$var_name" "$shell_name" 2>/dev/null || true)"
    if [[ -n "$hit" ]]; then
        VAR_SOURCE="${hit%%$'\t'*}"
        VAR_VALUE="${hit#*$'\t'}"
        return 0
    fi
    env_value="$(find_key_in_environment "$var_name")"
    if [[ -n "$env_value" ]]; then
        VAR_VALUE="$env_value"
        VAR_SOURCE="live env only"
    fi
}

find_existing_key() {
    local provider="$1"
    local shell_name="$2"
    local key_var
    key_var="$(read_provider_var "$provider")"
    find_var_with_source "$key_var" "$shell_name"
    EXISTING_KEY="$VAR_VALUE"
    EXISTING_KEY_SOURCE="$VAR_SOURCE"
}

render_source_label() {
    local source="$1"
    if [[ -z "$source" ]]; then
        printf ''
    elif [[ "$source" == "live env only" ]]; then
        printf '(live env only)'
    else
        printf '(from %s)' "${source/#$HOME/~}"
    fi
}

read_provider_var() {
    local provider="$1"
    case "$provider" in
        gemini) printf 'GEMINI_API_KEY' ;;
        *)      printf 'ANTHROPIC_API_KEY' ;;
    esac
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

render_existence_for_key() {
    local key_value="$1"
    if [[ -z "$key_value" ]]; then
        printf 'not set'
    else
        printf 'set %s' "$(render_key_suffix "$key_value")"
    fi
}

check_provider_mismatch() {
    local rc_content="$1"
    local provider="$2"
    local key_var
    key_var="$(read_provider_var "$provider")"
    local count
    count="$(find_var_count "$rc_content" "$key_var")"
    if (( count > 0 )); then
        return 0
    fi
    return 1
}

render_preflight_summary() {
    local rc_content="$1"
    local rc_path="$2"
    local rc_target="$3"
    local shell_name="$4"

    find_var_with_source "LLM_PROVIDER" "$shell_name"
    local provider_value="$VAR_VALUE"
    local provider_source="$VAR_SOURCE"

    find_var_with_source "ANTHROPIC_API_KEY" "$shell_name"
    local anthropic_value="$VAR_VALUE"
    local anthropic_source="$VAR_SOURCE"

    find_var_with_source "GEMINI_API_KEY" "$shell_name"
    local gemini_value="$VAR_VALUE"
    local gemini_source="$VAR_SOURCE"

    echo ""
    echo -e "${BOLD}Detected configuration:${NC}"
    printf '  LLM_PROVIDER:        %-20s%s\n' "${provider_value:-not set}" "$(render_source_label "$provider_source")"
    printf '  ANTHROPIC_API_KEY:   %-20s%s\n' "$(render_existence_for_key "$anthropic_value")" "$(render_source_label "$anthropic_source")"
    printf '  GEMINI_API_KEY:      %-20s%s\n' "$(render_existence_for_key "$gemini_value")" "$(render_source_label "$gemini_source")"

    printf '\n  Write target: %s\n' "${rc_target/#$HOME/~}"

    find_chain_warning "$rc_path" "$rc_target"

    if [[ -n "$provider_value" ]]; then
        local provider_key_var
        provider_key_var="$(read_provider_var "$provider_value")"
        find_var_with_source "$provider_key_var" "$shell_name"
        if [[ -z "$VAR_VALUE" ]]; then
            local provider_upper
            provider_upper="$(printf '%s' "$provider_value" | tr '[:lower:]' '[:upper:]')"
            warn "Mismatch: LLM_PROVIDER says $provider_value but no ${provider_upper}_API_KEY found. Setup will fix this."
        fi
    fi

    local var n
    for var in LLM_PROVIDER ANTHROPIC_API_KEY GEMINI_API_KEY; do
        n="$(find_var_count "$rc_content" "$var")"
        if (( n > 1 )); then
            warn "Found $n duplicate $var lines — will collapse to one on save."
        fi
    done
}

read_provider_choice() {
    local rc_content="$1"
    local current_provider
    current_provider="$(find_var_value "$rc_content" "LLM_PROVIDER")"

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
    local existing_source="$3"
    local combined
    if [[ "$existing_source" == "live env only" ]]; then
        combined="(from live env only, ends in …${existing_key: -4})"
    elif [[ -n "$existing_source" ]]; then
        combined="(from ${existing_source/#$HOME/~}, ends in …${existing_key: -4})"
    else
        combined="$(render_key_suffix "$existing_key")"
    fi
    echo ""
    echo "You already have a $key_var $combined."
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

render_replace_warning() {
    local source="$1"
    local rc_target="$2"
    local key_var="$3"
    if [[ -z "$source" ]] || [[ "$source" == "live env only" ]]; then
        return 0
    fi
    if [[ "$source" == "$rc_target" ]]; then
        return 0
    fi
    if [[ -e "$source" ]] && [[ -e "$rc_target" ]] && [[ "$source" -ef "$rc_target" ]]; then
        return 0
    fi
    warn "Existing key is exported from ${source/#$HOME/~}. New key will be written to ${rc_target/#$HOME/~}."
    warn "  You may end up with two \`export $key_var\` lines across files."
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
        if [[ "$answer" == *'"'* || "$answer" == *\\* ]]; then
            warn "Key contains \" or \\ which would break shell-rc parsing. Paste a different key, or type 'cancel'."
            continue
        fi
        NEW_KEY="$answer"
        return 0
    done
}

create_rc_content() {
    local rc_content="$1"
    local provider="$2"
    local key_value="$3"
    local key_var
    key_var="$(read_provider_var "$provider")"

    local filtered
    filtered="$(printf '%s\n' "$rc_content" \
        | awk -v vp="LLM_PROVIDER" -v vk="$key_var" '
            $0 ~ "^export " vp "=" { next }
            $0 ~ "^export " vk "=" { next }
            { print }
          ')"

    local kept_key_line=""
    if [[ -z "$key_value" ]]; then
        kept_key_line="$(printf '%s\n' "$rc_content" \
            | awk -v vk="$key_var" '$0 ~ "^export " vk "=" { line = $0 } END { print line }')"
    fi

    if [[ -n "$filtered" ]]; then
        printf '%s\n' "$filtered"
    fi
    printf 'export LLM_PROVIDER="%s"\n' "$provider"
    if [[ -n "$key_value" ]]; then
        printf 'export %s="%s"\n' "$key_var" "$key_value"
    elif [[ -n "$kept_key_line" ]]; then
        printf '%s\n' "$kept_key_line"
    fi
}

write_rc_atomic() {
    local new_content="$1"
    local rc_target="$2"
    local tmp="${rc_target}.tmp.$$"

    local prev_umask
    prev_umask="$(umask)"
    umask 077
    if ! printf '%s' "$new_content" > "$tmp" 2>/dev/null; then
        umask "$prev_umask"
        rm -f "$tmp" 2>/dev/null
        return 1
    fi
    umask "$prev_umask"

    if [[ -e "$rc_target" ]]; then
        local original_mode
        original_mode="$(stat -f '%Lp' "$rc_target" 2>/dev/null || stat -c '%a' "$rc_target" 2>/dev/null || true)"
        if [[ -n "$original_mode" ]]; then
            chmod "$original_mode" "$tmp" 2>/dev/null || true
        fi
    fi

    if ! mv "$tmp" "$rc_target" 2>/dev/null; then
        rm -f "$tmp" 2>/dev/null
        return 1
    fi
    return 0
}

write_session_vars() {
    local provider="$1"
    local key_value="$2"
    export LLM_PROVIDER="$provider"
    if [[ -n "$key_value" ]]; then
        local key_var
        key_var="$(read_provider_var "$provider")"
        export "$key_var=$key_value"
    fi
}

render_done_banner() {
    local need_restart="$1"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}${BOLD}✓ Setup complete.${NC}"
    echo ""
    if "$need_restart"; then
        warn "Open a new terminal window, then run:"
        echo ""
        echo -e "    ${BOLD}./dev.sh${NC}"
    else
        echo "Run the app with:"
        echo ""
        echo -e "    ${BOLD}./dev.sh${NC}"
        echo ""
        echo "If you want to use a different terminal, open a new one OR"
        echo "run \`source ~/.zshrc\` first, then ./dev.sh."
    fi
    echo ""
}

render_cancel_message() {
    echo ""
    echo "Setup cancelled. No changes made."
}

update_provider_and_key() {
    local rc_path="$1"
    local rc_target="$2"
    local rc_content="$3"
    local shell_name="$4"

    local cancel_requested=false
    PROVIDER_CHOICE=""
    KEY_ACTION=""
    NEW_KEY=""

    trap 'cancel_requested=true; render_cancel_message; trap - INT; return 0' INT
    trap 'rm -f "${rc_target}.tmp.$$" 2>/dev/null' EXIT

    read_provider_choice "$rc_content"
    if $cancel_requested; then return 0; fi

    local key_var
    key_var="$(read_provider_var "$PROVIDER_CHOICE")"

    find_existing_key "$PROVIDER_CHOICE" "$shell_name"
    local existing_key="$EXISTING_KEY"
    local existing_source="$EXISTING_KEY_SOURCE"

    if [[ -n "$existing_key" ]]; then
        read_key_action "$key_var" "$existing_key" "$existing_source"
        if $cancel_requested; then return 0; fi
        case "$KEY_ACTION" in
            cancel)  render_cancel_message; trap - INT; return 0 ;;
            keep)    NEW_KEY="" ;;
            replace)
                render_replace_warning "$existing_source" "$rc_target" "$key_var"
                read_new_key "$PROVIDER_CHOICE"
                ;;
        esac
    else
        read_new_key "$PROVIDER_CHOICE"
    fi
    if $cancel_requested; then return 0; fi
    if [[ "$KEY_ACTION" == "cancel" ]]; then
        render_cancel_message
        trap - INT
        return 0
    fi

    trap - INT

    local new_content
    new_content="$(create_rc_content "$rc_content" "$PROVIDER_CHOICE" "$NEW_KEY")"
    if ! write_rc_atomic "$new_content" "$rc_target"; then
        fail "Failed to write $rc_target (disk full? permissions?). Original is unchanged."
    fi

    if [[ "$KEY_ACTION" == "keep" ]]; then
        ok "Kept existing $key_var."
    fi

    write_session_vars "$PROVIDER_CHOICE" "$NEW_KEY"
    render_done_banner "$need_restart"

    return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    create_dependencies
    shell_name="$(find_current_shell)"
    rc_path="$HOME/.${shell_name}rc"
    rc_target="$(read_rc_path "$shell_name")"
    rc_content="$(read_rc_content "$rc_target")"

    render_preflight_summary "$rc_content" "$rc_path" "$rc_target" "$shell_name"
    update_provider_and_key "$rc_path" "$rc_target" "$rc_content" "$shell_name"
fi
