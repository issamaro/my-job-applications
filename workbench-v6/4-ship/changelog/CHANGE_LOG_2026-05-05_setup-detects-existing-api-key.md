# CHANGE_LOG — setup-detects-existing-api-key

**Feature:** setup-detects-existing-api-key  
**Date:** 2026-05-05  
**Commit base:** HEAD  
**Total files:** 2  
**Total additions:** +437  
**Total deletions:** -72  

---

## Files by category

### Backend

| File | Change type | +lines | -lines |
|------|-------------|--------|--------|
| setup.sh | M | 215 | 72 |

**Details:**
- Wrapped install-time logic into `create_dependencies()` function for sourceability.
- Fixed `find_current_shell()`: replaced `ps -p $$` (always returns script's bash process per shebang) with `$SHELL` env var as primary signal and `ps -p $PPID` fallback, fixing cross-shell detection (e.g., zsh users were incorrectly targeted to `~/.bashrc`).
- Added 6 new detection helpers: `find_rc_candidates`, `find_key_in_files`, `find_key_in_environment`, `find_var_with_source`, `find_existing_key`, `render_source_label`.
- Updated `render_preflight_summary()` to accept `shell_name` parameter, detect API key source from all candidate rc files + live environment, and display source label (e.g., "(from ~/.zshenv)" or "(live env only)").
- Updated `read_key_action()` to accept `existing_source` parameter and render combined source+suffix label.
- Added `render_replace_warning()` to warn when replacing a key that exists in a different file, with symlink detection (`-ef` inode test).
- Updated `update_provider_and_key()` to use `find_existing_key()` for source-aware detection and pass `shell_name` through call chain.
- Added guard `if [[ "${BASH_SOURCE[0]}" == "${0}" ]]` around main orchestration to allow sourcing setup.sh for testing.

### Tests

| File | Change type | +lines | -lines |
|------|-------------|--------|--------|
| tests/test_setup_detection.py | A | 222 | — |

**Details:**
- New pytest module for shell-rc detection under controlled HOME + env.
- `TestFindCurrentShell`: 4 test cases (UNPLANNED, see drift section) verifying `find_current_shell()` reads `$SHELL` env var and falls back to `ps -p $PPID`, with support for unusual paths.
- `TestFindExistingKey`: 7 cases covering detection order (zshenv precedes zshrc), provider routing (claude vs gemini), live-env fallback, empty key.
- `TestPreflightSummary`: 5 cases verifying source-aware preflight display, mismatch warning, duplicate warning, heading change, write-target line.
- `TestReplaceWarning`: 4 cases verifying cross-file warning behavior, symlink detection, live-env silence.

---

## Scope drift

**Unplanned additions:**
- `TestFindCurrentShell` class (4 cases): not in IMPL_PLAN, added to pin regression discovered during manual verification. Root cause: `find_current_shell` always returned `bash` due to `ps -p $$` inspecting script's own process. Zsh users were routed to `~/.bashrc` instead of `~/.zshrc`.

**Omitted from plan:**
- None. All planned helpers, refactors, and test scenarios delivered.

**Drift assessment:** Low. The `TestFindCurrentShell` additions directly document and test the discovered root cause mentioned in user context. This is expected scope expansion for a regression-fix scenario.

---

## Sensitive-area changes

None. No auth secrets, database migrations, public API surface, or security config modified. Changes are setup-time shell helpers and test infrastructure.

---

## Reproduction notes

Per FEATURE_SPEC success criteria and manual verification:

- **Root cause (original hypothesis):** setup.sh did not scan login-shell rc files; only read rc_target. Fix addresses by scanning `~/.zshenv`, `~/.zprofile`, `~/.zshrc`, `~/.profile` (zsh) or `~/.bash_profile`, `~/.bashrc`, `~/.profile` (bash) in order, then falling back to live environment.
- **Root cause (discovered during manual verification):** `find_current_shell` used `ps -p $$`, which inspects the script's own bash process (per `#!/bin/bash` shebang), not the user's interactive shell. Caused zsh users' ANTHROPIC_API_KEY to be located in `~/.zshenv` (correct) but setup to target `~/.bashrc` (incorrect) for write. Fix: use `$SHELL` env var (always set by login shells) as primary signal, with `ps -p $PPID` fallback (replaces broken `ps -p $$`).
- **Manual verification result:** User's pre-existing ANTHROPIC_API_KEY exported from `~/.zshenv` (the file setup.sh originally did not read). Live env had the key. Preflight now displays `ANTHROPIC_API_KEY: set …XXXX (from ~/.zshenv)`, and keep/replace menu shows source label embedded.

---

## Suggested commit subject

fix: detect api key source from all rc files and fix shell detection

