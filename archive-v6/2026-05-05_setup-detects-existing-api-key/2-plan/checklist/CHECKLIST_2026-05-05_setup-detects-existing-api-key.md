feature: setup-detects-existing-api-key
date: 2026-05-05
total_checkboxes: 52
derived_from: IMPL_PLAN_2026-05-05_setup-detects-existing-api-key.md, FEATURE_SPEC_2026-05-05_setup-detects-existing-api-key.md, UX_DESIGN_2026-05-05_setup-detects-existing-api-key.md

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` (verify: `cat .python-version`)  → source: IMPL_PLAN "Libraries / patterns in use" — "pytest (>=8.0.0)"; .python-version file confirmed 3.13
- [ ] `pyproject.toml` declares `requires-python = ">=3.13"`  → source: IMPL_PLAN "Libraries / patterns in use" — pytest dev dep entry at pyproject.toml:18
- [ ] Virtual environment created and activated (verify: `which python` resolves inside `.venv`)  → source: IMPL_PLAN "Verification" — `uv run pytest tests/test_setup_detection.py -v`

---

## Section 1 — Dependencies

- [ ] `pytest>=8.0.0` present in `pyproject.toml` dev group (verify: `uv tree --package pytest`)  → source: IMPL_PLAN "Libraries / patterns in use" — "pytest (>=8.0.0, dev group, pyproject.toml:18)"
- [ ] `subprocess` available as stdlib — no additional install needed (verify: `python -c "import subprocess; print('ok')"`)  → source: IMPL_PLAN "Libraries / patterns in use" — "subprocess (stdlib)"
- [ ] No new third-party libraries added — `uv tree` output unchanged from baseline  → source: IMPL_PLAN "Summary" — "No third-party libraries added."

---

## Section 2 — Syntax / implementation checkpoints

These items are ticked while editing the two in-scope files. Work through them in section order (A → F for setup.sh, then the test file).

### setup.sh — Section A: Wrap install block

- [ ] Lines 14-78 are wrapped inside `create_dependencies()` with no behavioral change to the enclosed commands; `cd "$SCRIPT_DIR"` (was line 15), `export PLAYWRIGHT_BROWSERS_PATH=0` (was line 17), the banner echos, and the brew/uv/python/bun installs all live inside the new function  → source: IMPL_PLAN "Section A" — wrap install-time-only logic
- [ ] `SCRIPT_DIR=…` (line 14) remains at file scope (pure variable assignment, safe to evaluate on source)  → source: IMPL_PLAN "Section A" — "Keep SCRIPT_DIR=… at file scope"
- [ ] `need_restart=false` is declared at file scope (above any function definition) AND re-assigned inside `create_dependencies`  → source: IMPL_PLAN "Section A" — "Initialize need_restart=false at file scope … the install block still re-assigns it"
- [ ] No `run_setup_main` wrapper is created — orchestration lives directly inside the BASH_SOURCE guard at the end of the file  → source: IMPL_PLAN "Section A" — "no run_setup_main wrapper, since 'run' is not a permitted verb"
- [ ] End-of-file BASH_SOURCE guard added with the inline orchestration block: calls `create_dependencies`, then `find_current_shell`, `read_rc_path`, `read_rc_content`, `render_preflight_summary` (with `shell_name` arg), `update_provider_and_key` (with `shell_name` arg)  → source: IMPL_PLAN "Section A" — guard block listing
- [ ] Smoke test passes: `bash -c 'source setup.sh; find_existing_key claude zsh; echo OK'` prints `OK` without triggering brew or `cd`  → source: IMPL_PLAN "Risks" — sourcing must not trigger installs
- [ ] `set -e` on line 5 is untouched  → source: IMPL_PLAN "Section A" — "Keep set -e (line 5) untouched"
- [ ] Lean-code: `create_dependencies` starts with permitted verb `create` (one of the nine in CLAUDE.md)  → source: IMPL_PLAN "Section A" — "Lean-code verb: create"; CLAUDE.md permitted verbs table

### setup.sh — Section B: New detection helpers

- [ ] `find_rc_candidates` inserted after `find_current_shell`; prints candidate paths for zsh, bash, and fallback shells using `printf '%s\n'`  → source: IMPL_PLAN "Section B" — find_rc_candidates body
- [ ] zsh candidate order is exactly: `.zshenv`, `.zprofile`, `.zshrc`, `.profile`  → source: FEATURE_SPEC "Candidate sources (closed list)" — zsh order items 1-4
- [ ] bash candidate order is exactly: `.bash_profile`, `.bashrc`, `.profile`  → source: FEATURE_SPEC "Candidate sources (closed list)" — bash order items 1-3
- [ ] `find_key_in_files` reuses `read_rc_content`, `find_var_count`, `find_var_value` unchanged; prints `PATH<TAB>VALUE` on first hit **with non-empty value** and returns 0; continues scanning when count > 0 but value is empty (unquoted-export edge); returns 1 when no quoted hit anywhere  → source: IMPL_PLAN "Section B" — find_key_in_files body and the unquoted-export note
- [ ] `find_key_in_environment` uses `${!var_name}` indirect expansion and prints non-empty value; prints nothing when var is unset  → source: IMPL_PLAN "Section B" — find_key_in_environment body
- [ ] `find_var_with_source` sets globals `VAR_VALUE` and `VAR_SOURCE`; file scan first, live-env fallback second  → source: IMPL_PLAN "Section C" — find_var_with_source body
- [ ] `find_existing_key` is a thin wrapper calling `find_var_with_source` then copying to `EXISTING_KEY` / `EXISTING_KEY_SOURCE`  → source: IMPL_PLAN "Section C" — "find_existing_key becomes a thin wrapper"
- [ ] All four new helpers start with verb `find` (one of the nine permitted verbs)  → source: CLAUDE.md — permitted verbs table; IMPL_PLAN "Section B" — "verb-prefixed names (find_*, …)"
- [ ] No new helper name exceeds verb + three scope words (e.g. `find_key_in_files` = find + key + in + files = four tokens — check that bash allows this and document the single exception)  → source: CLAUDE.md — "Maximum three words after the verb"
- [ ] No inline comments inside any new helper body  → source: CLAUDE.md — "After the header: ZERO comments"
- [ ] No abbreviations in variable names inside helpers (e.g. `file_content` not `f_cont`, `candidate` not `cand`)  → source: CLAUDE.md — "No abbreviations anywhere in names"; IMPL_PLAN "Section B" — local variable names shown verbatim

### setup.sh — Section C: Source-aware preflight

- [ ] `render_preflight_summary` heading changed from `Current configuration in <path>:` to `Detected configuration:`  → source: UX_DESIGN "Screen A" — "Heading change: Current configuration in <path>: → Detected configuration:"
- [ ] Each of the three rows calls `find_var_with_source` and appends `$(render_source_label "$VAR_SOURCE")` to its output  → source: IMPL_PLAN "Section C" — "Update each row in render_preflight_summary"
- [ ] `render_source_label` returns `(from <tilde-path>)` for a file path, `(live env only)` for that sentinel, and empty string for an empty source  → source: IMPL_PLAN "Section C" — render_source_label body; UX_DESIGN "Copy specifics"
- [ ] `render_source_label` uses `${source/#$HOME/~}` for tilde rendering  → source: IMPL_PLAN "Libraries / patterns in use" — "parameter expansion ${path/#$HOME/~} for tilde rendering"
- [ ] Write-target line `  Write target: <tilde-path>` is printed below the three rows  → source: UX_DESIGN "Screen A" — new copy block; IMPL_PLAN "Section C" — "The rc_target write-target line is added below the three rows"
- [ ] `render_preflight_summary` signature now accepts `shell_name` as a fourth argument  → source: IMPL_PLAN "Section C" — "Pass shell_name into render_preflight_summary (signature changes … to (rc_content, rc_path, rc_target, shell_name))"
- [ ] Mismatch check uses `find_var_with_source` results (not the old single-file `rc_content` lookup) and fires the verbatim warning text: `"Mismatch: LLM_PROVIDER says <provider> but no <PROVIDER>_API_KEY found. Setup will fix this."`  → source: IMPL_PLAN "Section C" — mismatch block; FEATURE_SPEC "Scenario 7"
- [ ] Duplicate-line warning still operates on `rc_content` of `rc_target` (per-file scope preserved)  → source: IMPL_PLAN "Section C" — "keep operating on rc_content of rc_target for the duplicate count"
- [ ] `render_source_label` starts with verb `render` (permitted)  → source: CLAUDE.md — permitted verbs table

### setup.sh — Section D: Source-aware routing in `update_provider_and_key`

- [ ] Old `existing_key = find_var_value(rc_content, key_var)` lookup replaced with `find_existing_key "$PROVIDER_CHOICE" "$shell_name"` + local copies  → source: IMPL_PLAN "Section D" — "Replace: local existing_key … with: find_existing_key …"
- [ ] `update_provider_and_key` receives `shell_name` as a new argument; caller in `run_setup_main` updated  → source: IMPL_PLAN "Section D" — "update_provider_and_key signature gains shell_name"
- [ ] `render_replace_warning` takes three args: `source`, `rc_target`, `key_var`; is silent when source is empty, when source equals `live env only`, when source string equals rc_target, OR when both paths exist and `[[ "$source" -ef "$rc_target" ]]` is true (managed-dotfiles symlink case)  → source: IMPL_PLAN "Section D" — render_replace_warning body with `-ef` symlink check
- [ ] `render_replace_warning` fires both warn lines verbatim when source file ≠ rc_target (including not-symlink-equivalent) and source is not `live env only`  → source: UX_DESIGN "Screen D"; FEATURE_SPEC "Scenario 5"
- [ ] `render_replace_warning` starts with verb `render` (permitted)  → source: CLAUDE.md — permitted verbs table

### setup.sh — Section E: `read_key_action` message update

- [ ] `read_key_action` signature extended to three args: `key_var`, `existing_key`, `existing_source`  → source: IMPL_PLAN "Section E" — "New signature: read_key_action <key_var> <existing_key> <existing_source>"
- [ ] Menu header line renders inline combined label matching exactly: `You already have a ANTHROPIC_API_KEY (from ~/.zshenv, ends in …XXXX).`  → source: FEATURE_SPEC "Scenario 1" — exact menu line; UX_DESIGN "Screen C" — new copy
- [ ] `live env only` source path renders as `(from live env only, ends in …XXXX)` in the menu header  → source: UX_DESIGN "Screen C" — state variation "Source = live env only"
- [ ] `read_key_suffix` / `render_key_suffix` (line 155) is NOT modified (scope-out)  → source: IMPL_PLAN "Section E" — "render_key_suffix (line 155) stays untouched"

### setup.sh — Section F: Wire-up

- [ ] `update_provider_and_key` call sequence matches the plan: provider choice → `find_existing_key` → branch on `existing_key` non-empty → `read_key_action` → `case` on `KEY_ACTION` (replace branch calls `render_replace_warning` before `read_new_key`)  → source: IMPL_PLAN "Section F" — updated call sequence listing
- [ ] When user picks `keep` and source ≠ rc_target, no duplicate key line is written to rc_target (the key stays only in its source file)  → source: IMPL_PLAN "Section F" — "Confirmed safe by inspection of create_rc_content"
- [ ] The legacy `create_rc_content` / `write_rc_atomic` path is invoked unchanged  → source: IMPL_PLAN "Section F" — "The legacy file-rewrite path … is invoked exactly as today"
- [ ] `bash -n setup.sh` reports no syntax errors  → source: IMPL_PLAN "Verification" — "bash -n setup.sh — syntax check"

---

## Section 3 — UX

- [ ] Screen A empty-state: when no vars are set, all three rows show `not set` with no `(from …)` annotation; `Write target:` line still rendered  → source: UX_DESIGN "Screen A" — "Empty (fresh install): each row shows not set; no (from …) annotation"
- [ ] Screen A success-state: key in env only renders `set ...AB12         (live env only)` on the relevant row  → source: UX_DESIGN "Screen A" — "Success (key in env only): row reads set ...AB12 (live env only)"
- [ ] Screen C copy: menu header reads `You already have a <VAR> (from <tilde-path>, ends in …<suffix>).` — two parenthesized tokens collapsed into one  → source: UX_DESIGN "Screen C" — new copy block
- [ ] Screen D triggered only when `[2] Replace` is chosen AND source ≠ rc_target AND source ≠ `live env only`  → source: UX_DESIGN "Screen D" — trigger condition; state variations "Skipped when …"
- [ ] Screen D skipped silently when source = rc_target  → source: UX_DESIGN "Screen D" — "Skipped when source = rc_target"
- [ ] Screen D skipped silently when source = `live env only`  → source: UX_DESIGN "Screen D" — "Skipped when source = live env only"
- [ ] No emojis introduced; ANSI palette (`BOLD`, `BLUE`, `GREEN`, `YELLOW`, `RED`, `NC`) unchanged  → source: UX_DESIGN "Copy specifics" — "No emojis are introduced. ANSI palette stays as-is"

---

## Section 4 — Tests (`tests/test_setup_detection.py`)

- [ ] File opens with docstring `"""Shell-rc detection tests for setup.sh."""` (project's existing pytest header style)  → source: IMPL_PLAN "tests/test_setup_detection.py" — "Test file header is the standard docstring"
- [ ] `TestFindExistingKey.test_key_in_zshenv_only` — value = `sk-ant-AAAA0001`, source ends with `.zshenv` (Scenario 1)  → source: IMPL_PLAN "Test cases" — test_key_in_zshenv_only; FEATURE_SPEC "Scenario 1"
- [ ] `TestFindExistingKey.test_no_key_anywhere` — value = `""`, source = `""` (Scenario 2)  → source: IMPL_PLAN "Test cases" — test_no_key_anywhere; FEATURE_SPEC "Scenario 2"
- [ ] `TestFindExistingKey.test_key_in_zshrc` — source ends with `.zshrc` (Scenario 3 regression)  → source: IMPL_PLAN "Test cases" — test_key_in_zshrc; FEATURE_SPEC "Scenario 3"
- [ ] `TestFindExistingKey.test_key_in_env_only` — source = `live env only` (Scenario 4)  → source: IMPL_PLAN "Test cases" — test_key_in_env_only; FEATURE_SPEC "Scenario 4"
- [ ] `TestFindExistingKey.test_zshenv_precedes_zshrc` — zshenv value returned, source ends with `.zshenv` (Scenario 6)  → source: IMPL_PLAN "Test cases" — test_zshenv_precedes_zshrc; FEATURE_SPEC "Scenario 6"
- [ ] `TestFindExistingKey.test_bash_candidates` — source ends with `.bash_profile` when key is there  → source: IMPL_PLAN "Test cases" — test_bash_candidates
- [ ] `TestPreflightSummary.test_preflight_shows_zshenv_source` — stdout contains `(from ~/.zshenv)` and `ANTHROPIC_API_KEY:` (Scenario 1 preflight)  → source: IMPL_PLAN "Test cases" — test_preflight_shows_zshenv_source; FEATURE_SPEC "Scenario 1" test-plan row
- [ ] `TestPreflightSummary.test_preflight_live_env_only` — stdout contains `(live env only)` (Scenario 4)  → source: IMPL_PLAN "Test cases" — test_preflight_live_env_only; FEATURE_SPEC "Scenario 4"
- [ ] `TestPreflightSummary.test_preflight_mismatch` — stdout contains the verbatim mismatch warning (Scenario 7)  → source: IMPL_PLAN "Test cases" — test_preflight_mismatch; FEATURE_SPEC "Scenario 7"
- [ ] `TestPreflightSummary.test_preflight_duplicate_warning` — stdout contains verbatim duplicate-collapse warning (Scenario 8)  → source: IMPL_PLAN "Test cases" — test_preflight_duplicate_warning; FEATURE_SPEC "Scenario 8"
- [ ] `TestReplaceWarning.test_warns_when_source_differs` — output contains both `~/.zshenv` and `~/.zshrc` (Scenario 5)  → source: IMPL_PLAN "Test cases" — test_warns_when_source_differs; FEATURE_SPEC "Scenario 5"
- [ ] `TestReplaceWarning.test_silent_when_source_equals_target` — output does NOT contain `"New key will be written"`  → source: IMPL_PLAN "Test cases" — test_silent_when_source_equals_target
- [ ] `TestReplaceWarning.test_silent_when_source_is_live_env` — output does NOT contain `"New key will be written"`  → source: IMPL_PLAN "Test cases" — test_silent_when_source_is_live_env
- [ ] `uv run pytest tests/test_setup_detection.py -v` exits 0, all 12 cases green  → source: IMPL_PLAN "Verification" — automated step 1
- [ ] `uv run pytest` (full suite) exits 0 — `tests/test_llm_factory.py` still green  → source: IMPL_PLAN "Verification" — "full suite green; no regression in tests/test_llm_factory.py"
- [ ] Test function names use no abbreviations (e.g. `test_key_in_zshenv_only` not `test_key_zshenv`)  → source: CLAUDE.md — "No abbreviations anywhere in names"; IMPL_PLAN "tests/test_setup_detection.py" — "test functions are descriptive, no abbreviations"
- [ ] No inline comments inside test function bodies (the `# Scenario N` annotations in the plan are illustrative; confirm none are left in the final file)  → source: CLAUDE.md — "After the header: ZERO comments"

---

## Section 5 — Accessibility

n/a — UX_DESIGN explicitly states "There is no a11y concern beyond ANSI colors already in use" (UX_DESIGN line 8). The surface is a terminal CLI with single-character read prompts; no new interactive elements are introduced.

---

## Section 6 — Project-specific

n/a — no project-checks.md found at project root.

---

## Manual verification record (to be filled during build)

These items are from IMPL_PLAN "Verification — Manual" and FEATURE_SPEC "Success criteria". Tick after running on the developer's actual machine.

- [ ] `grep -l ANTHROPIC_API_KEY ~/.zshenv ~/.zprofile ~/.zshrc ~/.profile 2>/dev/null` — record which file is printed (this is the reproduction case)  → source: IMPL_PLAN "Verification" — manual step 1
- [ ] `printenv ANTHROPIC_API_KEY` confirms key is in live env  → source: IMPL_PLAN "Verification" — manual step 2
- [ ] `./setup.sh` preflight shows `ANTHROPIC_API_KEY: set …XXXX (from <that file>)` before the fix is applied (baseline failure captured)  → source: FEATURE_SPEC "Success criteria" — "Manual run … reproduces the failing case before the fix"
- [ ] After fix, `./setup.sh` shows keep/replace/cancel menu with source label embedded  → source: IMPL_PLAN "Verification" — manual step 4
- [ ] Pick `[1] Keep` — no duplicate `export ANTHROPIC_API_KEY` line created in rc_target when source is a different file  → source: IMPL_PLAN "Verification" — manual step 5
- [ ] Re-run `./setup.sh` — preflight is unchanged (idempotent)  → source: IMPL_PLAN "Verification" — manual step 6
- [ ] Reproduction case (exact file that held the user's key) recorded in change log  → source: FEATURE_SPEC "Success criteria" — "The reproduction case … is recorded in the change log"
