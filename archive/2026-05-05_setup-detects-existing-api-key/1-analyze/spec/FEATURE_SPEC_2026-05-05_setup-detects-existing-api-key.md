# FEATURE_SPEC — setup-detects-existing-api-key

- **Date:** 2026-05-05
- **Slug:** setup-detects-existing-api-key
- **Ceremony:** M
- **Persona:** Returning developer who exports `ANTHROPIC_API_KEY` in a login-shell file (`~/.zshenv`, `~/.zprofile`, etc.) and expects `setup.sh` to pick it up without re-prompting.
- **Pain:** `setup.sh` re-prompts for a key that is already exported in the user's environment, which feels broken and risks the user pasting a duplicate or stale key.

## Problem statement

Today, `setup.sh:461-465` reads exactly one rc file — `$HOME/.${shell_name}rc` (e.g. `~/.zshrc` or `~/.bashrc`) — and feeds its contents to `find_var_value`. The live shell environment is never consulted, and other login-shell files (`~/.zshenv`, `~/.zprofile`, `~/.bash_profile`, `~/.profile`) are never read. So a user whose `ANTHROPIC_API_KEY` is exported from any of those — common when a user puts secrets in `~/.zshenv` so they reach non-interactive shells — falls through to `read_new_key` and is asked to paste a key they already have.

## Candidate sources (closed list)

The fix scans, in this exact order, and stops at first hit:

For zsh:
1. `~/.zshenv`
2. `~/.zprofile`
3. `~/.zshrc`
4. `~/.profile`

For bash:
1. `~/.bash_profile`
2. `~/.bashrc`
3. `~/.profile`

If none of the listed files contain the export, the live process environment is consulted as a final fallback (`live env only` source label).

Sources NOT scanned by file inspection: arbitrary sourced helpers, `~/.config/...` shell snippets, LaunchAgents, `setenv` forms, unquoted `export VAR=value` (existing regex limitation). These are covered indirectly by the live-env fallback whenever they have already been loaded into the running shell.

## Root-cause hypotheses (to confirm during build)

H1 (likely) — Key is exported from a file `setup.sh` does not read (most likely `~/.zshenv` or `~/.zprofile`).
H2 — `find_var_value` regex misses a valid `export` form (e.g. unquoted assignment, leading whitespace, `setenv`). Lower likelihood; no existing test covers `find_var_value` (the pytest suite only covers Python runtime reads of `os.environ`).
H3 — `find_current_shell` resolves to a different shell than the one the user runs. Lower likelihood — `ps -p $$ -o comm=` is correct for the script's own process.
H4 — `read_rc_path` resolves a different file than expected (symlink chain). `find_chain_warning` already surfaces this case.

The fix targets H1 directly (broader source set) and adds a live-env fallback that also catches H2 in practice (the user's shell already exported the key, so `${ANTHROPIC_API_KEY}` is set regardless of the export form). H2's regex is not expanded as part of this feature and is tracked separately. The build phase records which hypothesis actually triggered the user's report.

## Must-have behavior

1. When `ANTHROPIC_API_KEY` is set in the running shell environment OR present in any candidate login-shell file, `setup.sh` routes to `read_key_action` (keep / replace / cancel) — never `read_new_key`.
2. The preflight summary truthfully reports each provider key's source: an rc file path, `live env only`, or `not set`.
3. The keep / replace / cancel menu mentions where the existing key was found.
4. When the user picks `replace` and the source file is **not** the write target, a warning fires before the write so the user knows a new line will be added to a different file (legacy single-target write path is preserved per scope).
5. No regression in already-tested paths: fresh install (no key anywhere), key in `~/.zshrc`, mismatch between `LLM_PROVIDER` and key var, duplicate export lines.
6. The reproduction case (which file held the user's key) is captured in the change log and the manual-verification record.

## Out of scope

- Adding a third LLM provider.
- Refactoring `create_rc_content` / `write_rc_atomic` / the file-rewrite path.
- Windows / PowerShell support.
- Redesigning the interactive prompts or the menu layout (only message text is updated).
- Detecting unquoted `export VAR=value` forms (existing limitation; tracked separately).

## BDD scenarios

### Scenario 1 — key in a login file `setup.sh` previously missed (the failing case)

```
Given the user's shell is zsh
  And ANTHROPIC_API_KEY is exported from ~/.zshenv (and not from ~/.zshrc)
  And the live environment has ANTHROPIC_API_KEY set
When the user runs ./setup.sh and selects [1] Claude
Then the preflight shows "ANTHROPIC_API_KEY: set ...XXXX (from ~/.zshenv)"
  And the keep / replace / cancel menu prints the line
       "You already have a ANTHROPIC_API_KEY (from ~/.zshenv, ends in …XXXX)."
  And setup never shows the "Paste your Claude API key" prompt
```

### Scenario 2 — fresh install, no key anywhere

```
Given no ANTHROPIC_API_KEY in any login file
  And the live environment has no ANTHROPIC_API_KEY
When the user runs ./setup.sh and selects [1] Claude
Then the preflight shows "ANTHROPIC_API_KEY: not set"
  And setup prompts the user to paste a new key
```

### Scenario 3 — key in `~/.zshrc` (regression)

```
Given ANTHROPIC_API_KEY is exported from ~/.zshrc
When the user runs ./setup.sh and selects [1] Claude
Then the preflight shows "ANTHROPIC_API_KEY: set ...XXXX (from ~/.zshrc)"
  And setup shows the keep / replace / cancel menu
```

### Scenario 4 — key in live env only (untraceable source)

```
Given no ANTHROPIC_API_KEY in any candidate rc file
  And the live environment has ANTHROPIC_API_KEY set (e.g. from a sourced helper or LaunchAgent)
When the user runs ./setup.sh and selects [1] Claude
Then the preflight shows "ANTHROPIC_API_KEY: set ...XXXX (live env only)"
  And setup shows the keep / replace / cancel menu
```

### Scenario 5 — user picks `replace` and source ≠ write target

```
Given ANTHROPIC_API_KEY is exported from ~/.zshenv
  And rc_target is ~/.zshrc
When the user runs ./setup.sh, selects Claude, picks replace, and pastes a new key
Then setup warns "Existing key is exported from ~/.zshenv. New key will be written to ~/.zshrc."
  And setup writes the new key to ~/.zshrc
  And ~/.zshenv is left untouched
```

### Scenario 6 — key in `~/.zshenv` AND `~/.zshrc` (precedence is fixed)

```
Given ANTHROPIC_API_KEY is exported from both ~/.zshenv and ~/.zshrc with different values
When the user runs ./setup.sh
Then the preflight shows "ANTHROPIC_API_KEY: set ...<zshenv-suffix> (from ~/.zshenv)"
  And the keep / replace / cancel menu line names ~/.zshenv as the source
```

(`.zshenv` precedes `.zshrc` per the candidate order in the "Candidate sources" section.)

### Scenario 7 — provider mismatch regression

```
Given LLM_PROVIDER is exported as "gemini" from ~/.zshrc
  And no GEMINI_API_KEY is set anywhere (no rc file, no env)
When the user runs ./setup.sh
Then the preflight prints
       "Mismatch: LLM_PROVIDER says gemini but no GEMINI_API_KEY found. Setup will fix this."
  And the existing mismatch warning behavior is unchanged
```

### Scenario 8 — duplicate export lines regression

```
Given ~/.zshrc contains two `export ANTHROPIC_API_KEY="…"` lines
When the user runs ./setup.sh
Then the preflight prints
       "Found 2 duplicate ANTHROPIC_API_KEY lines — will collapse to one on save."
  And the keep / replace / cancel menu still appears
  And the existing collapse-on-save behavior is unchanged
```

## Success criteria

- New behavior — Scenarios 1, 4, 5, 6 pass automated tests.
- Regression coverage — Scenarios 2, 3, 7, 8 pass automated tests and confirm current behavior is unchanged.
- Manual run on the user's actual machine reproduces the failing case (Scenario 1) before the fix and shows the keep / replace / cancel menu after.
- The reproduction case (which exact file held the user's key) is recorded in the change log.
- `uv run pytest` is fully green.

## Test plan

All new tests live in a single file: `tests/test_setup_detection.py`. It subprocess-sources `setup.sh` (after the install block is wrapped in `install_dependencies`) under a temp `HOME`, exercises `find_existing_key` and `render_preflight_summary` directly, and asserts globals + stdout.

Mapping of scenarios to test cases:

| Scenario | Test asserts |
|---|---|
| 1 | `EXISTING_KEY` non-empty; `EXISTING_KEY_SOURCE` ends with `.zshenv`; preflight stdout contains `(from ~/.zshenv)`; menu line stdout contains `(from ~/.zshenv, ends in …<suffix>)`. |
| 2 | `EXISTING_KEY` empty; `EXISTING_KEY_SOURCE` empty; preflight stdout contains `not set`. |
| 3 | `EXISTING_KEY_SOURCE` ends with `.zshrc`; preflight stdout contains `(from ~/.zshrc)`. |
| 4 | `EXISTING_KEY` matches env value; `EXISTING_KEY_SOURCE` equals `live env only`; preflight stdout contains `(live env only)`. |
| 5 | Replace path executes; warning stdout contains both source path and rc_target path. |
| 6 | When key is in `.zshenv` AND `.zshrc`, `EXISTING_KEY_SOURCE` ends with `.zshenv` (precedence). |
| 7 | Existing mismatch warning still fires verbatim. |
| 8 | Existing duplicate-collapse warning still fires verbatim. |

Existing `tests/test_llm_factory.py` must remain green (no detection-layer change there).

## Open questions

- None blocking. The exact missed file on the user's machine is determined during build (manual verification step 1).
