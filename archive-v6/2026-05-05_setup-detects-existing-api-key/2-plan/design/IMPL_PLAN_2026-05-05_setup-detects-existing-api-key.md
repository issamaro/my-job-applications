# IMPL_PLAN — setup-detects-existing-api-key

- **Date:** 2026-05-05
- **Slug:** setup-detects-existing-api-key
- **Ceremony:** M
- **References:** FEATURE_SPEC_2026-05-05_setup-detects-existing-api-key.md, UX_DESIGN_2026-05-05_setup-detects-existing-api-key.md

## Summary

Expand `setup.sh` detection to scan a fixed list of login-shell files plus the live process environment, surface the source in the preflight summary and the keep/replace/cancel menu, and warn before a cross-file replace. Make `setup.sh` source-able so a new pytest module can drive its helpers under temp `HOME` layouts. No third-party libraries added.

## Libraries / patterns in use

- **bash builtins** — `${VAR}`, `${!VAR}` for indirect read, `printf '%s\n'`, parameter expansion `${path/#$HOME/~}` for tilde rendering, `[[ -n $x ]]` guards. All POSIX-extended bash, already used throughout `setup.sh`.
- **awk** — existing `find_var_count` / `find_var_value` regexes (`^export VAR="…"`) reused unchanged. No regex broadening.
- **pytest** (`>=8.0.0`, dev group, `pyproject.toml:18`) — `tmp_path`, `monkeypatch`, `subprocess.run`. Existing testpath `tests/`. `asyncio_mode = "auto"` is irrelevant for sync tests; subprocess tests stay sync.
- **subprocess** (stdlib) — invoke `bash -c 'source setup.sh; <call>'` with `env=` and `cwd=` controlled per case.

No `bats`, `shunit2`, or other shell-test framework introduced — keeps the dev-deps surface minimal.

## File-by-file plan

### `setup.sh` (modify)

Lean-code rules apply throughout: verb-prefixed names (`find_*`, `read_*`, `render_*`, `update_*`, `write_*`, `check_*`); no abbreviations; no inline comments beyond the existing two-line file header.

#### A. Wrap install block (light refactor for testability)

- **Lines 14-78** — wrap the install-time-only logic (the `cd "$SCRIPT_DIR"` on line 15, the `export PLAYWRIGHT_BROWSERS_PATH=0` on line 17, the banner echos on lines 19-22, and the brew/uv/python/bun/uv-sync/playwright/bun-install blocks on lines 31-78, plus `need_restart=false` on line 29) into one function. Lean-code verb: `create` ("bring into existence" — installs create the runtime environment on the host).

  ```bash
  create_dependencies() {
      cd "$SCRIPT_DIR"
      export PLAYWRIGHT_BROWSERS_PATH=0

      echo ""
      echo -e "${BOLD}MyCV — Setup${NC}"
      …  # current lines 20-78 verbatim, including need_restart=false
  }
  ```

  Preserve `need_restart` as a script-global since `update_provider_and_key` reads it (line 455). Initialize `need_restart=false` at file scope (above any function definition) so sourcing the script for tests gives a sane default; the install block still re-assigns it inside `create_dependencies`.

  Keep `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` (line 14) at file scope — it's a pure variable assignment and tests can read it.

- **End of file** — replace the lines 460-466 main flow with a `BASH_SOURCE` guard that orchestrates inline (no `run_setup_main` wrapper, since "run" is not a permitted verb in CLAUDE.md and lean-code's reference layout puts orchestration at module level):

  ```bash
  if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
      create_dependencies
      shell_name="$(find_current_shell)"
      rc_path="$HOME/.${shell_name}rc"
      rc_target="$(read_rc_path "$shell_name")"
      rc_content="$(read_rc_content "$rc_target")"
      render_preflight_summary "$rc_content" "$rc_path" "$rc_target" "$shell_name"
      update_provider_and_key "$rc_path" "$rc_target" "$rc_content" "$shell_name"
  fi
  ```

  When the file is sourced, only the function definitions and the `need_restart=false` default are evaluated — no installs, no `cd`, no preflight.

- Keep `set -e` (line 5) untouched at file scope (sourcing imports the flag, but tests run helpers under `bash -c` subshells so the flag stops at subshell exit). Keep ANSI color globals untouched. Keep helper glyphs (`step`, `ok`, `warn`, `fail`).

#### B. New detection helpers

Insert after `find_current_shell` (after current line 86):

- `find_rc_candidates` — print newline-separated paths in the closed order from FEATURE_SPEC.

  ```bash
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
  ```

- `find_key_in_files` — given a var name and shell name, scan candidates in order; on first hit **with a non-empty quoted value**, print `PATH<TAB>VALUE` and return. Continue scanning on count > 0 but empty value (unquoted-export edge — current `find_var_value` regex requires `="`; that limitation is out of scope for this fix, but we must not produce a `not set (from <file>)` row in the preflight). Reuses `read_rc_content`, `find_var_count`, `find_var_value` unchanged.

  ```bash
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
  ```

- `find_key_in_environment` — print `${!var_name}` if non-empty.

  ```bash
  find_key_in_environment() {
      local var_name="$1"
      local value="${!var_name}"
      if [[ -n "$value" ]]; then
          printf '%s' "$value"
      fi
  }
  ```

- `find_existing_key` — set globals `EXISTING_KEY` and `EXISTING_KEY_SOURCE`. File scan first; live-env fallback second.

  ```bash
  find_existing_key() {
      local provider="$1"
      local shell_name="$2"
      local key_var hit env_value
      key_var="$(read_provider_var "$provider")"

      EXISTING_KEY=""
      EXISTING_KEY_SOURCE=""

      hit="$(find_key_in_files "$key_var" "$shell_name" 2>/dev/null || true)"
      if [[ -n "$hit" ]]; then
          EXISTING_KEY_SOURCE="${hit%%$'\t'*}"
          EXISTING_KEY="${hit#*$'\t'}"
          return 0
      fi

      env_value="$(find_key_in_environment "$key_var")"
      if [[ -n "$env_value" ]]; then
          EXISTING_KEY="$env_value"
          EXISTING_KEY_SOURCE="live env only"
      fi
  }
  ```

  Lean-code self-check: `find_*` verb, three-word scope, no abbreviations, single job (locate one key + its source), one global pair set, no inline comments.

#### C. Source-aware preflight (`render_preflight_summary` modify)

Lines 189-220 today render into one rc_target with three rows. New version:

- Heading: `Detected configuration:` (no longer "Current configuration in <path>").
- Each row resolves its own source by calling `find_existing_key` per provider key (and a sibling `find_provider_in_files` for `LLM_PROVIDER`, OR — simpler — extend `find_existing_key` to be reusable for any var).

  Cleaner: introduce `find_var_with_source` that mirrors `find_existing_key` but takes `var_name` + `shell_name` instead of `provider`. Then `find_existing_key` becomes a thin wrapper for the API in `update_provider_and_key`. Both are single-job. Three callers (`LLM_PROVIDER`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) each set their own `value` + `source` locals.

  Implementation sketch:

  ```bash
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
      local provider="$1" shell_name="$2"
      local key_var
      key_var="$(read_provider_var "$provider")"
      find_var_with_source "$key_var" "$shell_name"
      EXISTING_KEY="$VAR_VALUE"
      EXISTING_KEY_SOURCE="$VAR_SOURCE"
  }
  ```

- New helper `render_source_label` — turn an absolute source path into a tilde-rendered label, or pass `live env only` through, or empty string when nothing was detected (caller decides not to render the parens).

  ```bash
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
  ```

- Update each row in `render_preflight_summary`. The exact three-call sequence (each call clobbers the `VAR_VALUE` / `VAR_SOURCE` globals, so capture into locals immediately):

  ```bash
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
  ```

  The `%-20s` width column for the value preserves the current alignment; one space then the source label or empty. `render_existence_for_key` (existing, line 167) already returns `not set` or `set (ends in …XXXX)` so the row text matches UX Screen A.

- The rc_target write-target line is added below the three rows:

  ```bash
  printf '\n  Write target: %s\n' "${rc_target/#$HOME/~}"
  ```

- The `find_chain_warning` call on line 205 stays in place.

- The mismatch warning block (lines 207-211) and duplicate-line warning block (lines 213-219) remain. Their inputs change: instead of operating on a single `rc_content`, they need to know whether the var lives in any candidate file. Cleanest: keep operating on `rc_content` of `rc_target` for the duplicate count (a duplicate IS a per-file phenomenon; the warning is "I will collapse to one on save" which implies a write to rc_target, so per-file scope is correct). The mismatch check (`check_provider_mismatch`) is also per-file today. After this fix it should look at the union: if `LLM_PROVIDER` exists somewhere AND the corresponding key var exists nowhere (no file, no env), warn. Switch `check_provider_mismatch` callers to use the new `find_var_with_source` results.

  Concretely:

  ```bash
  find_var_with_source "LLM_PROVIDER" "$shell_name"
  local provider_value="$VAR_VALUE"
  if [[ -n "$provider_value" ]]; then
      local key_var
      key_var="$(read_provider_var "$provider_value")"
      find_var_with_source "$key_var" "$shell_name"
      if [[ -z "$VAR_VALUE" ]]; then
          local provider_upper
          provider_upper="$(printf '%s' "$provider_value" | tr '[:lower:]' '[:upper:]')"
          warn "Mismatch: LLM_PROVIDER says $provider_value but no ${provider_upper}_API_KEY found. Setup will fix this."
      fi
  fi
  ```

  This preserves the verbatim warning text required by Scenario 7.

- Pass `shell_name` into `render_preflight_summary` (signature changes from `(rc_content, rc_path, rc_target)` to `(rc_content, rc_path, rc_target, shell_name)`). Update the only caller in `run_setup_main`.

#### D. Source-aware routing in `update_provider_and_key`

Modify lines 419-434:

- Replace:
  ```bash
  local existing_key
  existing_key="$(find_var_value "$rc_content" "$key_var")"
  ```
  with:
  ```bash
  find_existing_key "$PROVIDER_CHOICE" "$shell_name"
  local existing_key="$EXISTING_KEY"
  local existing_source="$EXISTING_KEY_SOURCE"
  ```
- Pass `existing_source` into `read_key_action` so the menu copy can render it.
- After `replace` is chosen, call a new `render_replace_warning "$existing_source" "$rc_target" "$key_var"` that fires the warn lines from UX Screen D when the source is a file *physically different* from rc_target. Skip silently when (a) source is empty, (b) source equals `live env only`, (c) source string equals rc_target, OR (d) source and rc_target both exist on disk and refer to the same inode (managed-dotfiles symlink case — `read_rc_path` on setup.sh:88-103 resolves rc_target through symlinks; `find_rc_candidates` does not, so a literal string compare alone misses the case where `~/.zshrc` is a symlink to `~/dotfiles/zshrc`).

  ```bash
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
  ```

  `[[ a -ef b ]]` (bash 3.2+) returns true when both paths resolve to the same device + inode. The `-e` guards keep the test honest when one of the paths doesn't exist on disk (rc_target may be created later by `write_rc_atomic`).

- `update_provider_and_key` signature gains `shell_name` so it can reach `find_existing_key`. Update the call in `run_setup_main`.

#### E. `read_key_action` message update

Modify lines 255-271. New signature: `read_key_action <key_var> <existing_key> <existing_source>`. Replace the hardcoded `~/.zshrc` with a source-aware label:

```bash
read_key_action() {
    local key_var="$1"
    local existing_key="$2"
    local existing_source="$3"
    local source_label
    source_label="$(render_source_label "$existing_source")"
    echo ""
    if [[ -n "$source_label" ]]; then
        echo "You already have a $key_var $source_label, $(render_key_suffix "$existing_key")."
    else
        echo "You already have a $key_var, $(render_key_suffix "$existing_key")."
    fi
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
```

Note: `render_source_label` returns `(from ~/.zshenv)` not `from ~/.zshenv`; the line therefore reads `You already have a ANTHROPIC_API_KEY (from ~/.zshenv), (ends in …AB12).` That's two parenthesized groups which is awkward. Adjust by removing the comma between source and suffix and integrating the suffix into the label assembly:

```bash
echo "You already have a $key_var (from ${existing_source/#$HOME/~}, ends in …${existing_key: -4})."
```

But that re-implements `render_key_suffix`. Cleaner: render a single combined label inline in `read_key_action`:

```bash
local suffix
suffix="$(render_key_suffix "$existing_key")"  # returns "(ends in …AB12)" or "(empty / suspicious — will replace)"
local combined
if [[ "$existing_source" == "live env only" ]]; then
    combined="(from live env only, ends in …${existing_key: -4})"
elif [[ -n "$existing_source" ]]; then
    combined="(from ${existing_source/#$HOME/~}, ends in …${existing_key: -4})"
else
    combined="$suffix"
fi
echo "You already have a $key_var $combined."
```

This matches the FEATURE_SPEC Scenario 1 exact line: `You already have a ANTHROPIC_API_KEY (from ~/.zshenv, ends in …XXXX).` and the UX Screen C copy. The `render_key_suffix` empty/suspicious branch (line 159) is only hit when `existing_key` is empty — in our routing that path doesn't reach `read_key_action` because we only enter it when `[[ -n "$existing_key" ]]`. So the simpler inline `${existing_key: -4}` suffices for the live cases, with a defensive fallback to `render_key_suffix` only when source is empty (shouldn't happen but is safe).

Per the scope-OUT on the rewrite path: `render_key_suffix` (line 155) stays untouched. The new logic is inline in `read_key_action`.

#### F. Wire-up: `update_provider_and_key` adjustments

Updated call sequence (line 416 onward):

```bash
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
```

The legacy file-rewrite path (`create_rc_content`, `write_rc_atomic`) is invoked exactly as today. No behavioral change there. The only divergence: when the user picks `keep` and the source file is not rc_target, `kept_key_line` (line 320-322) is computed from `rc_content` of rc_target, not from the source file. If source is `~/.zshenv`, rc_target is `~/.zshrc`, and the user picks `keep`, then `kept_key_line` is empty (no matching line in rc_target) and `create_rc_content` writes `LLM_PROVIDER` to rc_target without re-emitting the key. This is correct: the key already lives in `~/.zshenv`, will be loaded by interactive shells via the normal zsh load order, and we should NOT duplicate it in `~/.zshrc`.

Confirmed safe by inspection of `create_rc_content` (lines 304-334): when `key_value` is empty AND no kept_key_line is found in rc_target's content, the new content has only the `LLM_PROVIDER` line and the existing rc_target content (with old `LLM_PROVIDER` and any old key line filtered out). The key stays where it lives.

### `tests/test_setup_detection.py` (new)

Pytest module — sync (no asyncio markers needed), uses `tmp_path`, `monkeypatch`, `subprocess.run`.

#### Helper at top of file

```python
"""Shell-rc detection tests for setup.sh."""

import subprocess
from pathlib import Path

import pytest

SETUP_SH = Path(__file__).resolve().parent.parent / "setup.sh"


def run_detection(home, env_overrides, shell, provider):
    """Run find_existing_key under a controlled HOME + env, return (value, source)."""
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin", **env_overrides}
    cmd = (
        f'source "{SETUP_SH}" >/dev/null 2>&1; '
        f'find_existing_key "{provider}" "{shell}"; '
        f'printf "%s\\n%s\\n" "$EXISTING_KEY" "$EXISTING_KEY_SOURCE"'
    )
    result = subprocess.run(
        ["bash", "-c", cmd],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"bash exited {result.returncode}: {result.stderr}"
    lines = result.stdout.split("\n")
    return lines[0], lines[1]


def run_preflight(home, env_overrides, shell):
    """Run render_preflight_summary, return stdout."""
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin", **env_overrides}
    rc_target = f"$HOME/.{shell}rc"
    cmd = (
        f'source "{SETUP_SH}" >/dev/null 2>&1; '
        f'rc_target="{rc_target}"; rc_target="${{rc_target/#\\$HOME/$HOME}}"; '
        f'rc_content="$(read_rc_content "$rc_target")"; '
        f'render_preflight_summary "$rc_content" "$HOME/.{shell}rc" "$rc_target" "{shell}"'
    )
    result = subprocess.run(
        ["bash", "-c", cmd],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"bash exited {result.returncode}: {result.stderr}"
    return result.stdout
```

#### Test cases (mapping to FEATURE_SPEC scenarios)

```python
class TestFindExistingKey:
    def test_key_in_zshenv_only(self, tmp_path):
        # Scenario 1
        (tmp_path / ".zshenv").write_text('export ANTHROPIC_API_KEY="sk-ant-AAAA0001"\n')
        value, source = run_detection(tmp_path, {"ANTHROPIC_API_KEY": "sk-ant-AAAA0001"}, "zsh", "claude")
        assert value == "sk-ant-AAAA0001"
        assert source.endswith(".zshenv")

    def test_no_key_anywhere(self, tmp_path):
        # Scenario 2
        value, source = run_detection(tmp_path, {}, "zsh", "claude")
        assert value == ""
        assert source == ""

    def test_key_in_zshrc(self, tmp_path):
        # Scenario 3 (regression)
        (tmp_path / ".zshrc").write_text('export ANTHROPIC_API_KEY="sk-ant-BBBB0002"\n')
        value, source = run_detection(tmp_path, {}, "zsh", "claude")
        assert value == "sk-ant-BBBB0002"
        assert source.endswith(".zshrc")

    def test_key_in_env_only(self, tmp_path):
        # Scenario 4
        value, source = run_detection(tmp_path, {"ANTHROPIC_API_KEY": "sk-ant-CCCC0003"}, "zsh", "claude")
        assert value == "sk-ant-CCCC0003"
        assert source == "live env only"

    def test_zshenv_precedes_zshrc(self, tmp_path):
        # Scenario 6
        (tmp_path / ".zshenv").write_text('export ANTHROPIC_API_KEY="sk-ant-EEEE0001"\n')
        (tmp_path / ".zshrc").write_text('export ANTHROPIC_API_KEY="sk-ant-FFFF0002"\n')
        value, source = run_detection(tmp_path, {}, "zsh", "claude")
        assert value == "sk-ant-EEEE0001"
        assert source.endswith(".zshenv")

    def test_bash_candidates(self, tmp_path):
        (tmp_path / ".bash_profile").write_text('export ANTHROPIC_API_KEY="sk-ant-DDDD0004"\n')
        value, source = run_detection(tmp_path, {}, "bash", "claude")
        assert value == "sk-ant-DDDD0004"
        assert source.endswith(".bash_profile")
```

For Scenarios 5 (replace warning), 7 (mismatch), and 8 (duplicate), use a focused subprocess that runs `render_preflight_summary` or `render_replace_warning` standalone:

```python
class TestPreflightSummary:
    def test_preflight_shows_zshenv_source(self, tmp_path):
        # Scenario 1 preflight half
        (tmp_path / ".zshenv").write_text('export ANTHROPIC_API_KEY="sk-ant-AAAA0001"\n')
        out = run_preflight(tmp_path, {"ANTHROPIC_API_KEY": "sk-ant-AAAA0001"}, "zsh")
        assert "(from ~/.zshenv)" in out
        assert "ANTHROPIC_API_KEY:" in out

    def test_preflight_live_env_only(self, tmp_path):
        out = run_preflight(tmp_path, {"ANTHROPIC_API_KEY": "sk-ant-CCCC0003"}, "zsh")
        assert "(live env only)" in out

    def test_preflight_mismatch(self, tmp_path):
        # Scenario 7
        (tmp_path / ".zshrc").write_text('export LLM_PROVIDER="gemini"\n')
        out = run_preflight(tmp_path, {}, "zsh")
        assert "Mismatch: LLM_PROVIDER says gemini but no GEMINI_API_KEY found. Setup will fix this." in out

    def test_preflight_duplicate_warning(self, tmp_path):
        # Scenario 8
        (tmp_path / ".zshrc").write_text(
            'export ANTHROPIC_API_KEY="sk-ant-1111"\n'
            'export ANTHROPIC_API_KEY="sk-ant-2222"\n'
        )
        out = run_preflight(tmp_path, {}, "zsh")
        assert "Found 2 duplicate ANTHROPIC_API_KEY lines — will collapse to one on save." in out


class TestReplaceWarning:
    def test_warns_when_source_differs(self, tmp_path):
        # Scenario 5
        cmd = (
            f'source "{SETUP_SH}" >/dev/null 2>&1; '
            f'render_replace_warning "$HOME/.zshenv" "$HOME/.zshrc" "ANTHROPIC_API_KEY"'
        )
        result = subprocess.run(
            ["bash", "-c", cmd],
            env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = result.stdout + result.stderr
        assert "~/.zshenv" in out
        assert "~/.zshrc" in out

    def test_silent_when_source_equals_target(self, tmp_path):
        cmd = (
            f'source "{SETUP_SH}" >/dev/null 2>&1; '
            f'render_replace_warning "$HOME/.zshrc" "$HOME/.zshrc" "ANTHROPIC_API_KEY"'
        )
        result = subprocess.run(
            ["bash", "-c", cmd],
            env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = result.stdout + result.stderr
        assert "New key will be written" not in out

    def test_silent_when_source_is_live_env(self, tmp_path):
        cmd = (
            f'source "{SETUP_SH}" >/dev/null 2>&1; '
            f'render_replace_warning "live env only" "$HOME/.zshrc" "ANTHROPIC_API_KEY"'
        )
        result = subprocess.run(
            ["bash", "-c", cmd],
            env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = result.stdout + result.stderr
        assert "New key will be written" not in out
```

Lean-code rules (Python flavor): test functions are descriptive, no abbreviations. Test file header is the standard `"""..."""` docstring (Python tests already use that style — lean-code's two-line shell header is for shell scripts). The `# Lean Code` directive applies to project source; test scaffolding follows the project's existing pytest style (see `tests/test_llm_factory.py:1` `"""Tests for the LLM provider factory."""`).

## Risks

- **Sourcing setup.sh under `set -e`**: any non-zero return from a helper kills the test subprocess. Mitigation: `find_key_in_files` uses `count=$(find_var_count …)` which always returns; the inner `(( count > 0 ))` returns non-zero when count is 0, but it's not under `set -e` because it's the condition of an `if`. The `find_existing_key` wrapper traps `find_key_in_files` failure with `2>/dev/null || true`. Manual smoke: `bash -c 'set -e; source setup.sh; find_existing_key claude zsh; echo OK'` should print `OK`.

- **`${!var_name}` indirection under `set -u`**: not used today (`set -u` is not enabled), so safe. If a future change adds `set -u`, `${!var_name}` errors when var is unset; switch to `${!var_name:-}` defensively. Out of scope for this fix.

- **HOME tilde rendering**: `${path/#$HOME/~}` requires `$HOME` to be exported in the running shell, which it always is. Test subprocesses set `HOME=tmp_path` explicitly.

- **Bash `set -e` + subshell**: the `< <(find_rc_candidates)` process substitution returns non-zero only if `find_rc_candidates` itself fails — it doesn't, since it's plain `printf`. Safe.

- **Live-env false positive**: if the user has `ANTHROPIC_API_KEY` exported by their interactive shell at the moment they run setup.sh, but not in any rc file, the source label says `live env only`. That's correct and expected.

- **Symlinked candidate file**: `find_chain_warning` only fires for rc_target. If `~/.zshenv` is a symlink, we'll still read the resolved content via `cat`. No new warning needed (out of scope).

- **Test platform**: tests run `bash -c …`. macOS bash 3.2 supports the syntax used (`${!var}`, process substitution, `printf '%s\n'`). Also runs on Linux bash >= 4. CI compatibility unchanged.

## Verification

Automated:
- `uv run pytest tests/test_setup_detection.py -v` — all 12 cases green.
- `uv run pytest` — full suite green; no regression in `tests/test_llm_factory.py`.
- `bash -n setup.sh` — syntax check.

Manual (per FEATURE_SPEC success criteria, on the user's actual machine):
1. `grep -l ANTHROPIC_API_KEY ~/.zshenv ~/.zprofile ~/.zshrc ~/.profile 2>/dev/null` to identify the actual source file. **Record the result in the build's note-capturer output** so the change-logger can quote it in the eventual change log entry (satisfies FEATURE_SPEC must-have #6 and the success criterion "reproduction case is captured").
2. `printenv ANTHROPIC_API_KEY` to confirm it's in the live env.
3. `./setup.sh` — preflight prints `ANTHROPIC_API_KEY: set …XXXX (from <that file>)`.
4. Choose `[1] Claude` — keep/replace/cancel menu appears with the source label embedded.
5. Pick `[1] Keep` — setup completes, no duplicate `export ANTHROPIC_API_KEY` line is created in rc_target if the source was a different file.
6. Re-run `./setup.sh` — preflight is unchanged.
