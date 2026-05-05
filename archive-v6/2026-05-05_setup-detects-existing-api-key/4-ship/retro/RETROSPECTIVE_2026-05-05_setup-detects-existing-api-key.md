# RETROSPECTIVE — setup-detects-existing-api-key

- **Date:** 2026-05-05
- **Slug:** setup-detects-existing-api-key
- **Ceremony:** M

## What surprised me

- The bug had two stacked root causes, not one. The backlog hypothesized H1 (`setup.sh` reads only one rc file), and the fix targeted H1. Manual verification surfaced H3 simultaneously: `find_current_shell` always returned `bash` because `ps -p $$` inspects the script's own bash process (per `#!/bin/bash` shebang), not the user's interactive shell. Without the H3 fix, the H1 fix alone would still write to `~/.bashrc` for a zsh user. **The original `find_current_shell` had been broken since the file was authored**; nobody noticed because the failure mode (writing to the wrong rc file) was silent and the user's previous setup happened to also have `~/.bashrc` configured. This was caught only by the manual verification step asking the user to confirm `Write target: ~/.zshrc`.

- Lean-code's nine-verb list does not include `install`, `run`, or `setup` — the obvious names for a top-level script's main flow. The plan-reviewer caught this mid-plan; the resolution was (a) rename `install_dependencies` → `create_dependencies` and (b) drop `run_setup_main` and inline the orchestration directly inside the BASH_SOURCE guard. Lean-code's reference layout puts orchestration at module level for exactly this reason.

- Subprocess-driven shell tests are surprisingly clean. `subprocess.run(["bash", "-c", cmd], env=…)` plus `tmp_path` gave us 21 hermetic tests with no third-party dependency. The pattern reads well, runs in <1s, and the env-replacement semantics of `subprocess.run` makes leakage from the parent shell impossible.

## What was harder than expected

- Designing `find_var_with_source` to keep the lean-code "one job per function" rule while sharing implementation with `find_existing_key`. The compromise — `find_existing_key` is a thin wrapper that copies `VAR_VALUE` / `VAR_SOURCE` into provider-specific `EXISTING_KEY` / `EXISTING_KEY_SOURCE` globals — feels slightly redundant but avoids passing context flags between callers (which lean-code forbids).

- The symlink-equivalence check in `render_replace_warning`. Without `[[ a -ef b ]]`, a managed-dotfiles user (where `~/.zshrc` is a symlink to `~/dotfiles/zshrc`) would have gotten a misleading "exported from ~/.zshrc / written to ~/dotfiles/zshrc" warning. The plan-reviewer flagged this as MAJOR; I almost shipped without it.

- Wrapping the install block while keeping `need_restart` reachable from `update_provider_and_key` (which runs *after* `create_dependencies`, in the BASH_SOURCE guard's orchestration block). The script-global initialization at file scope (`need_restart=false`) plus a re-assignment inside `create_dependencies` covers both source-for-tests and run-for-real cases.

## What the next similar feature should do differently

1. **For shell-script bugs, manually invoke the script under the failing condition during the analyze phase**, not just during inspect. Had I run `./setup.sh` once during analyze, I would have caught the bash-vs-zsh write-target mismatch before writing the spec, instead of patching the spec mid-build. The backlog's H1-H4 hypotheses were a useful list, but a single live reproduction would have ranked H3 alongside H1 from the start.

2. **Add a one-line "what shell are we?" sanity check to any future shell-script feature spec**. The check is `echo "shell=$SHELL ps=$(ps -p $$ -o comm=) ppid=$(ps -p $PPID -o comm=)"`. It surfaces shebang-vs-login-shell drift in seconds.

3. **When wrapping legacy code in functions, run `bash -n` immediately after each Edit**. I caught the orphaned `ok "Node dependencies"` line only by reading the file post-edit. `bash -n` after each section would have flagged misplacements faster.

4. **Default to subprocess-driven tests for any shell helpers**, not just integration paths. `tests/test_setup_detection.py` could have been written before the implementation as TDD; the boilerplate cost is small and the hermetic isolation is worth it.

## What to add to project-checks

- **Pre-flight `find_current_shell` smoke test**: any feature that touches shell-rc detection should add a test asserting that `find_current_shell` returns `zsh` when `$SHELL=/bin/zsh`. The original bug went undetected for the lifetime of `setup.sh`; pinning this in tests prevents regression.

- **`bash -n setup.sh`** as a CI gate. Cheap, catches the orphaned-line-after-function-close class of mistake instantly. Could be added to a future `pre-commit` or `make check` target.

- **Lean-code verb-suffix scanner** (low priority): a simple grep to flag any function whose name doesn't start with one of the nine permitted verbs. The `install_dependencies` rename was caught manually by the checklist-builder; an automated check would close that gap.

## Risks deferred to backlog

- **Unquoted export forms** (`export ANTHROPIC_API_KEY=value` without quotes) are still not detected by `find_var_value`. Live-env fallback covers most user cases, but a future feature should expand the awk regex.

- **Sourced-helper / LaunchAgent / `~/.config/...` snippets**: only detected indirectly via live env. If a user exports the key in a snippet sourced *after* setup.sh's own shell starts, detection misses it. Out of scope for this feature; tracked here.

- **Cross-file duplicate exports**: if `~/.zshenv` AND `~/.zshrc` both export `ANTHROPIC_API_KEY`, the duplicate-line warning currently only fires when both lines are in the *same* file (the rc_target). Cross-file duplicates pass silently. Acceptable trade-off for the "collapse to one on save" semantics, which is per-file by definition.
