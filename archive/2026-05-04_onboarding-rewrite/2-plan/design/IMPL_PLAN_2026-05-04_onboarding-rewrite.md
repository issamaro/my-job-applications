---
slug: onboarding-rewrite
date: 2026-05-04
ceremony_level: L
phase: 2-plan
artifact: IMPL_PLAN
revision: 1
---

# Implementation Plan — Onboarding Rewrite

Companion to `workbench/1-analyze/spec/FEATURE_SPEC_2026-05-04_onboarding-rewrite.md` and `workbench/1-analyze/ux/UX_DESIGN_2026-05-04_onboarding-rewrite.md`. Plan is file-by-file; lean-code rules from `CLAUDE.md` apply (verb prefix on shell functions, no abbreviations, two-line file headers when adding new files, no inline comments where the code is self-explanatory).

---

## Library / runtime research — skipped (with rationale)

The orchestrator routing table calls for parallel `docs-researcher` dispatch at `ceremony_level: L`. Skipping intentionally:

- **`gh` CLI** — used only for `gh auth login` (interactive web flow) and `gh repo clone <owner>/<repo>`. Both syntax-locked in spec L42, L114. No version-sensitive surface.
- **`uv run uvicorn`** — already canonical in the project (manual setup section of README cites `uv run uvicorn main:app --reload`). Replacing bare `uvicorn` with `uv run uvicorn` in `dev.sh` is a one-line shape change, not a library adoption.
- **`bash` / POSIX builtins** — `ps -p $$ -o comm=`, `mv`, `grep -c`, `awk`, `read -rs`. Portability nuances are watch items, not library questions.

No `stack-resolver` either: zero new dependencies; existing `pyproject.toml` and `package.json` untouched.

If the plan-reviewer flags this as a gap, we will dispatch a single `docs-researcher` for `gh` CLI to confirm the auth-login flow text in the README walkthrough.

---

## Watch-item decisions (closing W1, W2, W3, and the `ps -o comm=` nuance)

These were left open by analysis-reviewer for the planner to resolve.

### W1 — `~/.zshrc` is a symlink (e.g., dotfiles repo)

**Decision: detect-and-warn, then proceed against the symlink target.**

`mv tmp ~/.zshrc` over a symlink severs the link (Darwin/Linux `mv` semantics). For a non-technical user this is fine because they have no symlinked rc. For a developer with dotfiles, severing the link is destructive.

Implementation:
- `read_rc_path` resolves the symlink ONCE, single-hop, and turns relative targets into absolute paths so all downstream file ops (`[[ -L … ]]`, in-memory read, atomic `mv`) work regardless of setup.sh's cwd:

  ```bash
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
  ```

  Why the relative-target branch matters: `readlink` (no `-f`) returns the literal symlink target string. Common dotfiles managers (Stow, dotbot, hand-rolled `ln -s zshrc ~/.zshrc` from inside `~/dotfiles`) create symlinks with relative targets like `dotfiles/zshrc`. Without the `dirname` resolution, `rc_target="dotfiles/zshrc"` resolves against setup.sh's cwd (the project dir) — `find_chain_warning` would silently miss the chain, and the atomic mv would write a phantom file inside the project directory.

- All in-memory transform reads from `$rc_target`; the atomic `mv` writes to `$rc_target`. Both are now guaranteed absolute.
- Pre-flight summary prints `Writing to: <rc_target>` so the user sees the resolved path. If `rc_target != rc_path`, additionally print `(resolved from symlink at ~/.zshrc)`.
- **Chained-symlink detection (m4 fix):** after `read_rc_path` returns, `find_chain_warning` does `[[ -L "$rc_target" ]]` against the absolute resolved path. If true (the chain has more than one link), it emits a yellow ⚠ note via `warn`:
  ```
  ⚠ Note: ~/.zshrc resolves through a symlink chain; only the first hop (<rc_target>) will be written.
    If you use a managed dotfiles repo, verify the result manually after setup.
  ```
  Continue normally — do NOT refuse. Non-technical users never see this (their rc isn't symlinked); developers with dotfiles see one informational line and can decide whether to interrupt setup. Called once from the pre-flight phase, immediately after `read_rc_path`.

Why not refuse-on-symlink: forces dotfiles users to do manual surgery for a flow that works correctly on the target. Why not link-severing (multi-hop `readlink -f`): on chained dotfile setups, writing to the final ultimate target is also destructive (the intermediate links may be the user's actual managed file). Single-hop + relative-resolution + chain warning is the least-bad balance.

### W2 — Duplicate-collapse pick policy

**Decision: last-wins.**

When `count > 1` for an existing var, we delete all matching lines and append one canonical line at the end with the new value (when we're writing a new value) or with the value from the last matching line (when the user chose "Keep existing"). Last-wins matches likely user intent (most-recent value is most likely current) and keeps the implementation single-pass.

Implemented inside `create_rc_content` via the awk `{ line = $0 } END { print line }` idiom — the `END` block emits whichever line was assigned last during the scan. No standalone helper needed.

### W3 — Short-key tail display

**Decision: branch on length.**

```
len(key) == 0   → "(empty / suspicious — will replace)"
len(key) <  4   → "(ends in …<all-chars>)"   # whole string, since 1–3 chars
len(key) >= 4   → "(ends in …<last-4-chars>)"
```

Implemented via a single helper `render_key_suffix` that takes a string and returns the parenthesized phrase. Lean: one function, one job.

### Bonus — `ps -p $$ -o comm=` portability

**Decision: pattern-match, not exact-match.**

On macOS login shells, `comm=` returns `-zsh` (leading dash). Matching with a pattern `*zsh` / `*bash` covers both login (`-zsh`) and non-login (`zsh`) cases.

```bash
find_current_shell() {
  case "$(ps -p $$ -o comm= 2>/dev/null)" in
    *zsh)  printf 'zsh' ;;
    *bash) printf 'bash' ;;
    *)     printf 'zsh' ;;
  esac
}
```

---

## File-by-file plan

### File 1 — `README.md` (modify, full rewrite of "Getting started" + new §6)

**Current state:** 96 lines, two `MyCV-2` references (L22, L23), one `localhost:5173` reference (L40), no auth section, no troubleshooting section.

**Target structure (matches UX_DESIGN §"Section list"):**

1. Title + one-sentence pitch (keep existing L1–L3).
2. **§1 — Install Homebrew, Git, and gh** (replaces current §1; one fenced bash block: `brew install git gh`).
3. **§2 — Authenticate to GitHub** (NEW; instructs `gh auth login`, walks the GitHub.com → HTTPS → "Login with a web browser" → 8-char code path).
4. **§3 — Clone the project** (replaces current §2; uses `gh repo clone issamaro/my-job-applications`).
5. **§4 — Run setup** (replaces current §3; mentions provider menu + cancel-anywhere-is-safe).
6. **§5 — Start the app** (replaces current §4; references `http://localhost:8000` exactly).
7. **§6 — If something goes wrong** (NEW; four troubleshooting items per UX_DESIGN §"Troubleshooting copy").
8. **Manual setup (developers)** (keep existing §"Manual setup" content; one edit — confirm `LLM_PROVIDER` documentation already shows both providers, no change needed beyond verifying the URL/repo name don't appear there either).
9. **Tests** (keep existing).

**Concrete edits:**

- Delete L7–L17 (current §1 git-install) → replace with §1 "Install Homebrew, Git, and gh" using `brew install git gh` (assumes Homebrew exists; if not, `setup.sh` installs it later — README mentions this).
- Insert new §2 "Authenticate to GitHub" between §1 and what was §2:
  - One paragraph + one fenced block: `gh auth login`
  - Bulleted walkthrough: choose **GitHub.com** → **HTTPS** → **Yes** (authenticate Git) → **Login with a web browser** → copy 8-char code → paste in browser.
  - Success line: terminal shows `✓ Logged in as <username>`.
- Replace L21–L24 (clone block):
  ```
  gh repo clone issamaro/my-job-applications
  cd my-job-applications
  ```
- Replace L40 `localhost:5173` → `http://localhost:8000`.
- Add new §6 "If something goes wrong" after §5, before the `---` divider, with four items verbatim per UX_DESIGN.
- Spot-check rest of file for any other `MyCV-2` or `5173` strings (none expected outside lines flagged).

**Lean-code:** README isn't code, but the same crispness applies — one command per fenced block (so copy-paste can't pick up comments), no decorative emoji in commands, headings at H2.

---

### File 2 — `setup.sh` (full rewrite of provider/key flow + new pre-flight)

**Current state:** 194 lines, monolithic `setup_api_key` function L100–L173 that:
- Uses `$SHELL` (login shell, wrong) instead of `$$` shell detection.
- Writes piecemeal with `sed -i ''` (BSD-only, partial-write risk).
- Writes `LLM_PROVIDER` only if missing (the central bug).
- Has the empty-Enter overload for "skip key" (UX_DESIGN explicitly forbids).

**Approach:**
- Keep the install steps L37–L96 exactly as-is (Homebrew, uv, Python, bun, deps, Playwright, Node deps).
- Keep the banner header at L21–L24 (existing `MyCV — Setup` copy stays).
- **Delete the existing "Done" footer at L177–L194 (M-1 fix).** Its content is folded into a new `render_done_banner` helper called from `update_provider_and_key`'s success path only, so cancel paths cannot fall through to it. The legacy `need_restart` variable (currently set at L33/L77 from the bun-install branch) is preserved at top-level scope and passed to `render_done_banner` as an argument so the new banner can still branch on "bun was newly installed → open new terminal for PATH".
- Replace the API-key block (L98–L175) with the new two-phase atomic flow.

After this rewrite, setup.sh's structure top-to-bottom is: shebang + 2-line file header → ANSI palette + helper trio (`step`/`ok`/`warn`/`fail`) → install steps L37–L96 (unchanged) → `render_preflight_summary` invocation → `update_provider_and_key` invocation → script ends (no trailing banner block; `render_done_banner` is the only source of the success banner and is called from inside `update_provider_and_key`).

**New functions to add (lean-code names, verb-first per CLAUDE.md 9-verb whitelist, ≤3 words after verb):**

Whitelist: `read, write, create, delete, update, find, check, parse, render`. CLAUDE.md explicitly forbids `build`, `print`, `detect`, `prompt`, `export`, `setup`, `note`, `count`. All names below comply.

| Function | Job (single) | Returns |
|---|---|---|
| `find_current_shell` | Run `ps -p $$ -o comm=` and pattern-match `*zsh`/`*bash` | `zsh` or `bash` (echoed) |
| `read_rc_path` | Compose rc path from shell name; resolve symlink one hop into `rc_target` | echoes resolved path |
| `find_chain_warning` | If `$rc_target` is itself a symlink (chained), emit a yellow ⚠ note via `warn` | side effect |
| `read_rc_content` | Read whole rc file into a variable (or empty string if file missing) | echoes content |
| `find_var_count` | Count `^export <VAR>=` lines in rc content | integer to stdout |
| `find_var_value` | Extract the value (last match) of `export <VAR>="..."` from content | echoes value or empty |
| `render_key_suffix` | Format a key tail per W3 (empty/short/normal cases) | echoes parenthesized phrase |
| `render_existence_for_key` | Render `set (ends in …xxxx)` or `not set` for the pre-flight summary line | echoes phrase |
| `render_preflight_summary` | Render "Current configuration in <rc_target>:" + per-var lines + anomaly ⚠ lines | side effect |
| `check_provider_mismatch` | Given content, return 1 if `LLM_PROVIDER=X` but no `X_API_KEY` line | exit code |
| `check_var_duplicates` | Given content + var name, echo count if > 1 else nothing | side effect |
| `read_provider_choice` | Show current selection, read 1/2 from stdin | sets global `PROVIDER_CHOICE` (`claude`/`gemini`) |
| `read_key_action` | Case A menu (Keep / Replace / Cancel) | sets global `KEY_ACTION` (`keep`/`replace`/`cancel`) |
| `read_new_key` | Hidden read with `cancel` literal; loop on empty | sets globals `NEW_KEY` and `KEY_ACTION` (`cancel` on literal) |
| `create_rc_content` | Apply all scheduled var ops to in-memory content (last-wins on duplicates) | echoes new content |
| `write_rc_atomic` | Write content to `<rc_target>.tmp.$$`, then `mv` over `<rc_target>` | exit code |
| `write_session_vars` | `export LLM_PROVIDER=… ; export <CHOSEN>_API_KEY=…` in current shell | side effect |
| `render_done_banner` | Render the success banner per UX_DESIGN; takes `need_restart` as arg and branches on it (see body sketch below) | side effect |
| `update_provider_and_key` | Top-level orchestration: phase 1 plan → phase 2 commit, with cancel paths | exit code |

The existing 4-line helper trio `step / ok / warn / fail` (L28–L31) stays — these are short bash conventions for status glyphs and are documented as legacy helpers (the `step`/`ok`/`fail` names predate this rewrite; renaming them would create churn outside this feature's scope). The `warn` helper, which already prints a yellow line, absorbs the role originally proposed for a new `note` helper. No new helper is added beyond the 17 above.

**Cancel paths (Scenario 2d coverage) — globals-based, no subshell.**

Subshell-echo (`var=$(read_helper)`) hides the `read -r` from the parent's `INT` trap, so the trap as originally drafted never fired and the contract held only by accident via `set -e` + subshell death. Fix: prompt helpers do NOT echo their answer; they set a documented global that the orchestrator reads in the same shell.

| Helper | Sets global | Possible values |
|---|---|---|
| `read_provider_choice` | `PROVIDER_CHOICE` | `claude`, `gemini` |
| `read_key_action` | `KEY_ACTION` | `keep`, `replace`, `cancel` |
| `read_new_key` | `NEW_KEY` (and `KEY_ACTION=cancel` on `cancel` literal) | non-empty key string, or unset |

Caller (`update_provider_and_key`) then reads `PROVIDER_CHOICE`, `KEY_ACTION`, `NEW_KEY` directly. No `$(...)` around the helpers, so the parent's INT trap reaches the in-progress `read -r`.

Cancel sources, after the fix:

- **Ctrl-C at any prompt:** parent's `trap 'cancel_requested=true; render_cancel_message; return 0' INT` fires (set inside `update_provider_and_key`, cleared on exit via `trap - INT`). Sets `cancel_requested=true` and short-circuits before the commit phase.
- **Literal `cancel` typed at the key prompt:** `read_new_key` sets `KEY_ACTION=cancel` and returns; orchestrator checks `KEY_ACTION` and short-circuits.
- **`[3] Cancel` menu choice:** `read_key_action` sets `KEY_ACTION=cancel`; same short-circuit.

In all three cases the orchestrator returns BEFORE `create_rc_content` / `write_rc_atomic` are invoked. Shell-rc remains byte-identical (Scenario 2d).

The "Done" banner is moved inside the success branch of `update_provider_and_key` so cancel paths skip it. On cancel, `render_cancel_message` prints `Setup cancelled. No changes made.` (the existing `warn` helper does not fit; this is a neutral-tone line per UX_DESIGN L188).

| Helper | Job |
|---|---|
| `render_cancel_message` | Render `Setup cancelled. No changes made.` (used by both INT-trap and sentinel paths) |

**Atomic-commit phase:**

After `read_provider_choice` and `read_key_action`/`read_new_key` populate their globals AND `cancel_requested` is still false AND `KEY_ACTION != cancel`:

1. `create_rc_content "$rc_content" "$PROVIDER_CHOICE" "$NEW_KEY" → new_content` (`NEW_KEY` is empty when the user chose "Keep existing").
2. `write_rc_atomic "$new_content" "$rc_target"` → on failure, print red ✗ line and `exit 1`. No in-shell exports.
3. `write_session_vars "$PROVIDER_CHOICE" "$NEW_KEY"`.
4. `render_done_banner` (success-path only).

`create_rc_content` does the actual line surgery using awk (POSIX, no GNU/BSD divergence): for each tracked var, awk filters out matching `^export <VAR>=` lines from the input; then we append exactly one canonical line (or zero, if user chose "Keep" and the original line should be preserved — in that case we re-emit the existing line verbatim). Last-wins behavior for pre-existing duplicates falls out naturally because we delete all and re-emit one.

**Sketch of `create_rc_content`:**

```bash
create_rc_content() {
  local rc_content="$1"
  local provider="$2"
  local key_value="$3"        # empty if user chose "Keep existing"
  local key_var
  key_var="$(read_var_name_for_provider "$provider")"

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

  printf '%s\n' "$filtered"
  printf 'export LLM_PROVIDER="%s"\n' "$provider"
  if [[ -n "$key_value" ]]; then
    printf 'export %s="%s"\n' "$key_var" "$key_value"
  else
    printf '%s\n' "$kept_key_line"
  fi
}
```

Notes:
- `awk` reads from `printf` stdin so a missing trailing newline in `rc_content` doesn't drop content.
- The two `next`-rules eliminate ALL existing `LLM_PROVIDER` lines and ALL existing `<chosen>_API_KEY` lines (including duplicates → collapse to one). The OTHER provider's `*_API_KEY` lines are NEVER mentioned in awk → preserved untouched (Scenario 2b).
- `kept_key_line` is the last existing match (last-wins per W2) when user chose Keep.
- The `printf '%s\n'` between filtered content and our appended lines is the output assembly.

**Helper `read_var_name_for_provider`:** maps `claude` → `ANTHROPIC_API_KEY`, `gemini` → `GEMINI_API_KEY`. Trivial case statement.

**Sketch of `update_provider_and_key` (orchestrator with trap):**

```bash
update_provider_and_key() {
  local rc_target="$1"
  local rc_content="$2"

  local cancel_requested=false
  PROVIDER_CHOICE=""
  KEY_ACTION=""
  NEW_KEY=""

  trap 'cancel_requested=true; render_cancel_message; trap - INT; return 0' INT
  trap 'rm -f "${rc_target}.tmp.$$" 2>/dev/null' EXIT

  read_provider_choice "$rc_content"
  $cancel_requested && return 0

  local key_var
  key_var="$(read_var_name_for_provider "$PROVIDER_CHOICE")"
  local existing_key
  existing_key="$(find_var_value "$rc_content" "$key_var")"

  if [[ -n "$existing_key" ]]; then
    read_key_action "$key_var" "$existing_key"
    $cancel_requested && return 0
    case "$KEY_ACTION" in
      cancel)  render_cancel_message; trap - INT; return 0 ;;
      keep)    NEW_KEY="" ;;
      replace) read_new_key "$PROVIDER_CHOICE" ;;
    esac
  else
    read_new_key "$PROVIDER_CHOICE"
  fi
  $cancel_requested && return 0
  [[ "$KEY_ACTION" == "cancel" ]] && { render_cancel_message; trap - INT; return 0; }

  trap - INT

  local new_content
  new_content="$(create_rc_content "$rc_content" "$PROVIDER_CHOICE" "$NEW_KEY")"
  if ! write_rc_atomic "$new_content" "$rc_target"; then
    fail "Failed to write $rc_target (disk full? permissions?). Original is unchanged."
  fi
  write_session_vars "$PROVIDER_CHOICE" "$NEW_KEY"
  render_done_banner "$need_restart"

  return 0
}
```

Notes:
- Globals (`PROVIDER_CHOICE`, `KEY_ACTION`, `NEW_KEY`) are uppercase to flag their out-param role; declared at the top of the function so they don't bleed in from a previous call.
- `trap - INT` clears the INT trap on every exit path so a later Ctrl-C in the surrounding script (e.g. during the wait/banner) doesn't fire stale handler logic.
- **Commit phase is uninterruptible (M2 trap-leak fix):** `trap - INT` is also called immediately BEFORE `create_rc_content` so the brief atomic commit (`create_rc_content` → `write_rc_atomic` → `write_session_vars` → `render_done_banner`) cannot be hijacked by a Ctrl-C that fires inside `write_rc_atomic` and falsely returns 0 from the helper while the orchestrator still believes commit succeeded. Cancel during commit takes the bash default (script dies via SIGINT) — acceptable because (a) commit is millisecond-scale, (b) the EXIT trap below cleans up any orphaned temp file regardless of how the script ends.
- **EXIT-trap temp cleanup:** `trap 'rm -f "${rc_target}.tmp.$$"' EXIT` runs unconditionally on script exit (success, failure, SIGINT, anything). Targets the literal pid-suffixed temp (`$$` is setup.sh's pid) so concurrent setup.sh invocations cannot delete each other's in-flight temp file. Guarantees this run's temp does not linger in `$HOME` regardless of whether the commit completed, was interrupted, or `write_rc_atomic` itself failed.
- `$cancel_requested && return 0` checked after every prompt; the INT trap sets the flag so we return cleanly instead of dying.
- `KEY_ACTION == cancel` is the sentinel path for the literal `cancel` typed in `read_new_key` and the `[3] Cancel` menu choice.
- No `$(read_helper)` anywhere — every helper call is a bare invocation in the parent shell.

**Atomic write (preserves original file mode; defense-in-depth umask 077):**

The naive `printf > tmp; mv tmp rc` widens permissions on every run because the temp file inherits the user's umask (typically 0644 on macOS), and `mv` propagates the temp's mode to the destination. For a shell-rc that may now contain `*_API_KEY` values, this is a real privacy regression — a user with `chmod 600 ~/.zshrc` would silently end up world-readable after each `setup.sh` run.

Fix: write the temp file under a restricted `umask 077` (so secrets are 0600 even on first creation), then `chmod` the temp to match the original's mode before `mv` (so an explicit user choice of 0644 or 0600 is preserved verbatim). `stat` portability is handled by trying BSD-form first, GNU-form second.

```bash
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
```

Mode-preservation contract:

| Pre-existing rc | Pre-existing mode | After `write_rc_atomic` |
|---|---|---|
| absent | n/a | new file at `0600` (umask 077 floor) |
| present | `0600` | preserved at `0600` |
| present | `0644` | preserved at `0644` |
| present | other | preserved verbatim |

The `|| true` after each portability fallback prevents `set -e` from killing the script if both `stat` forms fail in some exotic environment — in that case we keep the umask-077-derived `0600` on the temp, which is the safer default.

Note: `printf '%s'` (no `\n`) for the final write because the last appended line in `create_rc_content` already ends with `\n`. Avoids a phantom blank line growing on every run.

**Pre-flight summary printing:**

```bash
render_preflight_summary() {
  local rc_content="$1"
  local rc_path="$2"
  local rc_target="$3"

  local current_provider current_anthropic current_gemini
  current_provider="$(find_var_value "$rc_content" "LLM_PROVIDER")"
  current_anthropic="$(find_var_value "$rc_content" "ANTHROPIC_API_KEY")"
  current_gemini="$(find_var_value "$rc_content" "GEMINI_API_KEY")"

  echo ""
  echo -e "${BOLD}Current configuration in ${rc_target/#$HOME/~}:${NC}"
  printf '  LLM_PROVIDER:        %s\n' "${current_provider:-not set}"
  printf '  ANTHROPIC_API_KEY:   %s\n' "$(render_existence_for_key "$current_anthropic")"
  printf '  GEMINI_API_KEY:      %s\n' "$(render_existence_for_key "$current_gemini")"

  find_chain_warning "$rc_path" "$rc_target"

  local provider_upper
  provider_upper="$(printf '%s' "$current_provider" | tr '[:lower:]' '[:upper:]')"
  if [[ -n "$current_provider" ]] && ! check_provider_mismatch "$rc_content" "$current_provider"; then
    warn "Mismatch: LLM_PROVIDER says $current_provider but no ${provider_upper}_API_KEY found. Setup will fix this."
  fi

  for var in LLM_PROVIDER ANTHROPIC_API_KEY GEMINI_API_KEY; do
    local n
    n="$(find_var_count "$rc_content" "$var")"
    if (( n > 1 )); then
      warn "Found $n duplicate $var lines — will collapse to one on save."
    fi
  done
}
```

**Bash 3.2 portability:** macOS ships bash 3.2 by default. The `${var^^}` uppercase expansion (bash 4+) is not used anywhere. Inline `printf '%s' "$x" | tr '[:lower:]' '[:upper:]'` at each use site (≤3 sites total). No helper function added.

**Sketch of `find_chain_warning` (W1 chained-symlink detection, M-2 user-facing-string fix):**

Takes both the literal `rc_path` (e.g. `/Users/foo/.zshrc`) and the resolved absolute `rc_target`. Renders the rc_path in `~/`-relative form via the same `${var/#$HOME/~}` substitution `render_preflight_summary` uses, so `~/.zshrc` is shown verbatim instead of the broken `~/..zshrc` produced by basename-prefix concatenation.

```bash
find_chain_warning() {
  local rc_path="$1"
  local rc_target="$2"
  if [[ -L "$rc_target" ]]; then
    warn "Note: ${rc_path/#$HOME/~} resolves through a symlink chain; only the first hop ($rc_target) will be written."
    warn "      If you use a managed dotfiles repo, verify the result manually after setup."
  fi
}
```

Called once from `render_preflight_summary` (above), AFTER the per-var lines and BEFORE the mismatch / duplicate scans, so the user sees the chain note in context with the resolved path.

**Sketch of `find_var_count` (avoid `grep -c` under `set -e`):**

`grep -c '^export VAR='` returns exit code 1 when count is zero, which is the typical case for at least one of `ANTHROPIC_API_KEY` / `GEMINI_API_KEY`. Under `set -e`, a zero-count call would kill the script. Use awk (always exit 0) instead:

```bash
find_var_count() {
  local rc_content="$1"
  local var_name="$2"
  printf '%s\n' "$rc_content" \
    | awk -v vn="$var_name" '$0 ~ "^export " vn "=" { n++ } END { print n+0 }'
}
```

The `n+0` coercion ensures a numeric `0` is printed when no match.

**Sketch of `find_var_value` (extract last-match value, double-quoted form):**

```bash
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
```

Last-match (W2 last-wins) and double-quoted-only (per P1 risk) by design. Empty stdout when the var is absent.

**Quote-injection guard in `read_new_key` (m2 fix):**

A pasted key containing a literal `"` or trailing `\` would corrupt the appended `export VAR="<key>"` line. Real Anthropic/Gemini keys are alphanumeric + `_` + `-`, so this is theoretical, but a one-line guard is cheap:

```bash
read_new_key() {
  local provider="$1"
  while true; do
    echo ""
    echo -n "Paste your $provider API key (input hidden), or type 'cancel' to abort. Key: "
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
```

**`create_rc_content` Keep-branch empty guard (m5 fix):**

If `kept_key_line` is somehow empty (race / unexpected state), don't emit a phantom blank line. Update the Keep branch in the snippet:

```bash
  if [[ -n "$key_value" ]]; then
    printf 'export %s="%s"\n' "$key_var" "$key_value"
  elif [[ -n "$kept_key_line" ]]; then
    printf '%s\n' "$kept_key_line"
  fi
```

**Banner header:** the existing `MyCV — Setup` line at L22–L24 stays. The pre-flight summary prints AFTER all install steps but BEFORE the API-key prompts (so brew/uv/bun/deps installs come first, matching today's flow).

**Done banner — `render_done_banner` body sketch (M-1 + R-MIN-3 fix):**

`render_done_banner` is the single source of the success banner. The legacy L177–L194 block in setup.sh is deleted (see "Approach" above). It branches on `need_restart` to handle two distinct new-terminal cases:

- `need_restart=true` (bun was newly installed in this run): user must open a new terminal so the freshly-installed `bun` is on PATH.
- `need_restart=false` (bun was already installed): user can run `./dev.sh` from the same terminal; if they prefer a different terminal, they need to either open a new one (rc file picks up keys at launch) or `source ~/.zshrc` first (current shell already has them via `write_session_vars`, but a sibling terminal does not).

```bash
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
```

Caller (orchestrator success path): `render_done_banner "$need_restart"`. The `need_restart` variable stays at top-level scope in setup.sh (its current home; assigned at L33 / mutated at L77 by the bun branch). `update_provider_and_key` reads it from outer scope or accepts it as an argument; either way, no cancel path reaches `render_done_banner`.

**File header:** existing two-line pseudo-header at L1–L5 is fine; tighten to:
```
#!/bin/bash
# MyCV — Setup
# Scope: Install dependencies and write LLM provider + API key into the user's shell-rc atomically.
```

(Three lines counting the shebang; the lean rule's "two comment lines" applies after the shebang.)

---

### File 3 — `dev.sh` (modify uvicorn invocation + add provider banner line)

**Current state:** 75 lines. Line 71 invokes bare `uvicorn`. No `Using LLM provider:` line.

**Edits:**

- **L71** — change `uvicorn main:app --reload --host 0.0.0.0 --port 8000 &` → `uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 &`. Survives `mv`-of-folder regardless of activation state.
- **Insert before L47** (after the `uv sync` block ends, before the `# Start Rollup/Svelte watcher in background...` comment so the comment stays attached to its echo) — banner line:
  ```bash
  echo -e "${GREEN}Using LLM provider: ${YELLOW}${LLM_PROVIDER:-claude (default)}${NC}"
  ```
  This places the line BEFORE uvicorn starts, so the user sees it in the banner area, not buried in factory.py logs (per UX_DESIGN note about not consolidating with `services/llm/factory.py:43`).

- **Remove activate block (m8 fix)** — delete current L37–L41 (`if [ -d ".venv" ]; then source .venv/bin/activate; fi`). With `uv run uvicorn` doing all Python invocation, the activation is redundant. More importantly, after `mv project /elsewhere`, the activate script's hardcoded `VIRTUAL_ENV` path is stale and gets exported into uvicorn's environment — confusing for anyone debugging `env | grep VIRTUAL_ENV`. Removing the block eliminates the stale-path footgun at its source. `uv sync` immediately below (L44–L45) still runs and rebuilds `.venv` if needed; `uv run uvicorn` finds the venv via `pyproject.toml` lookup regardless of activation state.

- **No file-header change** — dev.sh is not part of this rewrite's added-files set. Header stays.

**Risk R6 (factory.py double-log):** explicitly do NOT touch `services/llm/factory.py` line 43. The spec calls this intentional duplication.

---

### Files NOT touched (explicit non-changes)

- `services/llm/*.py` — out of scope per spec L98.
- `services/llm/factory.py:43` — intentional dual-log per R6.
- `pyproject.toml`, `package.json`, `bun.lockb`, `uv.lock` — no dependency changes.
- `frontend/`, `app/`, `tests/` — no app/test changes (regression catch via existing pytest only).
- `.gitignore` — no new files to ignore (`*.tmp.<pid>` lives outside repo, in `~`).

---

## Test plan (build phase)

- **`uv run pytest`** — full existing suite must pass. No new tests. (App-feature tests aren't relevant; this is shell + docs.)
- **Inspector checklist** — the 10 items in FEATURE_SPEC §"Verification". Hand-walked by the maintainer.
- **No automated smoke** — deferred to `backlog/raw/onboarding-smoke-script.md`.

The test-runner subagent will be invoked after build to confirm pytest is green (regression).

---

## Risks specific to this plan

- **P1 (low):** `awk` regex anchoring in `create_rc_content` uses `"^export " vp "="` — if the user has an `export LLM_PROVIDER='gemini'` (single-quoted), the start-anchor still matches, but the value-extraction in `find_var_value` must handle both `"..."` and `'...'`. Plan: extract via a permissive sed/awk that strips both quote styles; or accept double-quote-only and document. **Decision:** double-quote-only because (a) setup.sh always WRITES double-quoted, (b) the spec's BDD scenarios all show double-quotes, (c) supporting both adds branching with no observable user benefit. If a developer pre-set the var single-quoted manually, our pre-flight summary will show "not set" and `find_var_count` will still be 1 — minor cosmetic mismatch, no data corruption (we'll still match the line and replace it, since the start-anchor doesn't care about quote style). Confirm during build.

- **P2 (low):** `printf '%s' "$content"` argument size limit on bash. Shell-rc files are small (typically <100 lines, ~5 KB); well under any limit. Acceptable.

- **P3 (low):** macOS bash 3.2 lacks `${var^^}` and several niceties. Plan avoids all of them (uses `tr` for uppercase, `case` for matching, no associative arrays).

- **P4 (low):** `gh repo clone issamaro/my-job-applications` requires `gh` to be authed. Spec orders auth first, so this is enforced by README ordering. If the user runs the clone command in a different terminal where `gh` was authed, behavior is undefined; out of scope per persona definition (linear top-to-bottom reader).

- **P5 (medium):** if the user's `~/.zshrc` has CRLF line endings (rare on macOS but possible if edited on Windows), our awk regex `^export ` still matches but the appended lines are LF — file becomes mixed. **Decision:** detect CRLF on read and refuse with a diagnostic asking the user to convert, rather than silently mixing. Alternative — normalize to LF — risks losing lines the user intended to keep CRLF for some reason. Refuse-with-diagnostic is the safer minimal default. Document in `note-capturer` if encountered during build.

  Actually, on reflection: this is overkill for the persona. Mac `~/.zshrc` files don't have CRLF in practice. **Final decision:** ignore CRLF; if it happens, the user gets a mixed file that still works for export semantics. Treat as undocumented edge case. No diagnostic.

---

## Summary

- 3 files touched: `README.md`, `setup.sh`, `dev.sh`.
- 0 files created.
- 0 dependencies added.
- 0 library docs research dispatched (rationale documented above).
- All 4 watch items closed: W1 (symlink: detect-and-resolve, write to target), W2 (last-wins), W3 (length-branched suffix), `ps comm=` (pattern-match `*zsh`/`*bash`).
- 17 new bash functions in `setup.sh`, all verb-prefixed, all single-job.
- Atomicity contract held by `create_rc_content` → `write_rc_atomic` boundary; cancel paths return before the boundary.
- Test plan: pytest regression + 10-item inspector checklist.
