# PLAN_VERIFIED — setup-detects-existing-api-key

- **feature**: setup-detects-existing-api-key
- **date**: 2026-05-05
- **status**: ISSUES
- **reviewer**: plan-reviewer
- **inputs_reviewed**:
  - workbench-v6/1-analyze/spec/FEATURE_SPEC_2026-05-05_setup-detects-existing-api-key.md
  - workbench-v6/2-plan/design/IMPL_PLAN_2026-05-05_setup-detects-existing-api-key.md
  - workbench-v6/1-analyze/ux/UX_DESIGN_2026-05-05_setup-detects-existing-api-key.md
  - setup.sh (lines 1-466)
  - tests/test_llm_factory.py (line 1, header style reference)
  - pyproject.toml
- **inputs_skipped**:
  - workbench-v6/2-plan/checklist/CHECKLIST_2026-05-05_setup-detects-existing-api-key.md — directory empty, checklist-builder running in parallel; per caller instructions, skipped.

## 1. Requirement traceability

Source: FEATURE_SPEC "Must-have behavior" 1-6 + 8 BDD scenarios.

| requirement | covered_by | status |
|---|---|---|
| MH1: route to keep/replace/cancel when key in env OR any candidate file | IMPL_PLAN §B `find_existing_key`, §D `update_provider_and_key` (rewrite of lines 419-434) | covered |
| MH2: preflight reports per-row source (path / live env only / not set) | IMPL_PLAN §C (`find_var_with_source`, `render_source_label`, three rows + write target line) | covered |
| MH3: keep/replace/cancel menu mentions source | IMPL_PLAN §E (`read_key_action` rewrite with combined label, lines 332-342) | covered |
| MH4: warning when source ≠ rc_target on replace | IMPL_PLAN §D (`render_replace_warning`, lines 268-288) and §F call site (line 371) | covered with caveat (see Issue I-2 — symlinked rc_target false-positive) |
| MH5: no regression in fresh / .zshrc / mismatch / duplicate paths | IMPL_PLAN §C duplicate block kept per-rc_target; mismatch warn rewritten to use `find_var_with_source` (lines 230-243); test cases in `TestFindExistingKey`, `TestPreflightSummary` cover scenarios 2/3/7/8 | covered |
| MH6: actual missed file recorded in change log | IMPL_PLAN §Verification step 1 (`grep -l ANTHROPIC_API_KEY ~/.zshenv …`) — but no explicit instruction to write the result into the change log artifact | partial / vague (see Issue I-3) |
| Scenario 1 — key in `~/.zshenv` only | IMPL_PLAN §B + §C + test `test_key_in_zshenv_only` + `test_preflight_shows_zshenv_source` | covered |
| Scenario 2 — fresh install | test `test_no_key_anywhere` | covered |
| Scenario 3 — key in `~/.zshrc` (regression) | test `test_key_in_zshrc` | covered |
| Scenario 4 — live env only | test `test_key_in_env_only` + `test_preflight_live_env_only` | covered |
| Scenario 5 — replace + cross-file warning | test `TestReplaceWarning::test_warns_when_source_differs` | covered |
| Scenario 6 — `.zshenv` AND `.zshrc` precedence | test `test_zshenv_precedes_zshrc` | covered |
| Scenario 7 — mismatch warning regression | IMPL_PLAN §C rewrite + test `test_preflight_mismatch` | covered |
| Scenario 8 — duplicate-line collapse | test `test_preflight_duplicate_warning` | covered |

No traceability gaps that block. MH6 is partial — see Issue I-3.

## 2. File-path verification (anti-hallucination)

| reference | type | exists | status |
|---|---|---|---|
| `setup.sh` | modify | yes (466 lines) | OK |
| `setup.sh:5` (`set -e`) | modify-context | yes | OK |
| `setup.sh:14` (`SCRIPT_DIR=…`) | modify-context | yes | OK |
| `setup.sh:17` (`export PLAYWRIGHT_BROWSERS_PATH=0`) | modify-context | yes | OK |
| `setup.sh:19-78` (install block to wrap into `install_dependencies`) | modify | yes | OK |
| `setup.sh:29` (`need_restart=false`) | modify | yes | OK |
| `setup.sh:80-86` (`find_current_shell`) | modify-context | yes | OK |
| `setup.sh:88-103` (`read_rc_path`) | modify-context | yes | OK |
| `setup.sh:105-112` (`find_chain_warning`) | reuse | yes | OK |
| `setup.sh:114-121` (`read_rc_content`) | reuse | yes | OK |
| `setup.sh:123-128` (`find_var_count`) | reuse | yes | OK |
| `setup.sh:130-145` (`find_var_value`) | reuse | yes | OK |
| `setup.sh:147-153` (`read_provider_var`) | reuse | yes | OK |
| `setup.sh:155-165` (`render_key_suffix`) | reuse | yes | OK |
| `setup.sh:167-174` (`render_existence_for_key`) | reuse | yes | OK |
| `setup.sh:176-187` (`check_provider_mismatch`) | replaced/superseded by `find_var_with_source` callers | yes | OK |
| `setup.sh:189-220` (`render_preflight_summary`) | modify | yes (lines 189-220 confirmed) | OK |
| `setup.sh:200-204` (current preflight rows) | UX-design-reference | yes (lines 200-203 confirmed; UX cites 200-204 for the 3 rows + heading) | OK |
| `setup.sh:255-271` (`read_key_action` lines per plan §E) | modify | yes | OK |
| `setup.sh:259` (the hardcoded `~/.zshrc` line) | modify | yes (literal `"You already have a $key_var in ~/.zshrc $(render_key_suffix …)"` confirmed) | OK |
| `setup.sh:283` (paste prompt) | reuse | yes | OK |
| `setup.sh:304-334` (`create_rc_content`) | analysis-only | yes | OK |
| `setup.sh:320-322` (`kept_key_line`) | analysis-only | yes (lines 319-323 confirmed) | OK |
| `setup.sh:336-364` (`write_rc_atomic`) | reuse | yes | OK |
| `setup.sh:413` (INT trap) | reuse | yes | OK |
| `setup.sh:414` (EXIT trap) | reuse | yes | OK |
| `setup.sh:419-434` (existing key vs new key fork) | modify | yes (lines 419-431 confirmed; line 434 ends the if/else) | OK |
| `setup.sh:455` (`render_done_banner "$need_restart"`) | reuse | yes | OK |
| `setup.sh:460-466` (bottom main block) | modify (wrap in `run_setup_main`) | yes | OK |
| `tests/test_setup_detection.py` | create | parent dir `tests/` exists | OK |
| `tests/test_llm_factory.py:1` (header style) | analysis-only | yes (`"""Tests for the LLM provider factory."""`) | OK |
| `pyproject.toml:18` (`pytest>=8.0.0`) | reference | yes (line 18 = `"pytest>=8.0.0",`) | OK |

No hallucinated file references. Every line number, function name, and snippet citation in the plan resolves to real code.

## 3. Library-pattern verification

User's note: "no library notes — only bash + pytest, in-project already." Verified live:

| pattern | documented_in | status |
|---|---|---|
| `${!var}` indirection | bash 3.2.57 (system) — confirmed via `bash --version` + smoke test | OK |
| `printf '%s\t%s'` + `${var%%$'\t'*}` / `${var#*$'\t'}` | bash 3.2 ANSI-C quoting — smoke-tested, splits correctly | OK |
| `< <(producer)` process substitution under `set -e` | bash 3.2 — smoke-tested with `gen() { printf "a\nb\nc\n"; }; while …; done < <(gen)` | OK |
| `${path/#$HOME/~}` parameter expansion | already used in setup.sh:200 | OK |
| `[[ "${BASH_SOURCE[0]}" == "${0}" ]]` source-vs-execute guard | standard bash idiom; confirmed `setup.sh:14` already uses `${BASH_SOURCE[0]}` | OK |
| `subprocess.run(env=…)` env replacement (NOT inheritance) | Python stdlib — confirmed semantics | OK |
| `pytest tmp_path` + `monkeypatch` | pyproject.toml dev group has `pytest>=8.0.0`; existing `tests/test_llm_factory.py` uses pytest | OK |
| `${var: -4}` negative-substring expansion | bash 3.2 — smoke-tested; works | OK |
| `awk` in restricted PATH | `/usr/bin/awk` exists; smoke-tested under `env -i HOME=… PATH=/usr/bin:/bin` | OK |

No hallucinated APIs. The plan's bash idioms are all bash-3.2-compatible.

## 4. Checklist coverage

CHECKLIST not yet present (running in parallel — caller instruction: skip if missing).

## 5. Risks and ambiguities

### BLOCKER — none

### MAJOR

**M-1 — Symlinked `rc_target` causes false-positive replace warning.**
Location: IMPL_PLAN §D, lines 268-276 (`render_replace_warning`).
`read_rc_path` (setup.sh:88-103) resolves a symlinked `~/.zshrc` to its target (e.g. `/Users/me/dotfiles/zshrc`). But `find_rc_candidates` (plan §B, lines 79-83) emits literal `$HOME/.zshrc`. So when the user has a managed-dotfiles symlinked rc, `existing_source="/Users/me/.zshrc"` while `rc_target="/Users/me/dotfiles/zshrc"`. The check `[[ "$source" == "$rc_target" ]]` is false → warning fires saying "Existing key is exported from ~/.zshrc. New key will be written to ~/dotfiles/zshrc" — even though they're the same file. The existing `find_chain_warning` already fires for the symlink, but the new replace warning misleads the user into thinking the existing key won't be overwritten when it will. Fix needed: resolve the source the same way `read_rc_path` does, or compare via `realpath`/`readlink`-equivalent. Plan acknowledges symlink in Risks ("Symlinked candidate file") only for content-reading, not for this equality check.

### MINOR

**m-1 — Unquoted-export edge produces "not set (from ~/.zshenv)" preflight wording.**
Location: IMPL_PLAN §C (preflight rows) + scope-OUT.
When a candidate file has `export ANTHROPIC_API_KEY=sk-ant-…` (unquoted), `find_var_count` returns 1 but `find_var_value` returns empty (its regex requires `="`). `find_key_in_files` therefore prints `path<TAB>` (empty value), `find_var_with_source` sets `VAR_SOURCE=path` but `VAR_VALUE=""`, and the preflight row shows `ANTHROPIC_API_KEY:   not set         (from ~/.zshenv)` — which is semantically incoherent. Spec lists unquoted forms as out-of-scope, but the preflight wording in this edge will confuse the user, not fail safe. Easy fix: in the preflight key rows, only render the source label when `VAR_VALUE` is non-empty.

**m-2 — Two snippets for `render_replace_warning` may confuse the implementer.**
Location: IMPL_PLAN §D, lines 267-288.
The plan presents two function definitions in sequence: the first (lines 268-276) uses `$key_var` in the body without declaring it locally; the second (lines 282-288) adds `local key_var="$3"` but elides the body with `…`. A literal copy-paste of the first snippet would leave `$key_var` unbound (likely empty under default expansion). The intent is clearly the second; making it explicit ("use this combined definition") would prevent confusion.

**m-3 — Cross-file duplicate detection is silently scope-narrowed.**
Location: IMPL_PLAN §C, line 226.
The plan keeps the duplicate-line warning per-rc_target. FEATURE_SPEC Scenario 6 has the key in BOTH `.zshenv` and `.zshrc` (different values) — this is two single-file-with-one-line states, not a duplicate, so no warning fires. Behavior is correct, but a user with the key actually duplicated across files won't get a heads-up that two files will have stale state after they pick `keep`. Acceptable per scope but unflagged.

**m-4 — `cd "$SCRIPT_DIR"` runs at source time, not flagged as test-side-effect.**
Location: setup.sh:14-15.
The `BASH_SOURCE` guard wraps `install_dependencies` and `run_setup_main`, but `SCRIPT_DIR=…; cd "$SCRIPT_DIR"; export PLAYWRIGHT_BROWSERS_PATH=0` (lines 14-17) runs unconditionally on `source`. The test subprocess will end up with cwd at the project root, not at `tmp_path`. None of the helpers under test depend on cwd, so it's harmless — but `subprocess.run(cwd=…)` should not be relied on if a future test does depend on it. Plan's Risks section doesn't mention this side effect.

**m-5 — MH6 ("record reproduction case in change log") has no concrete plan step.**
Location: IMPL_PLAN §Verification.
The plan's manual step 1 surfaces the file but does not say "write the result into the change log artifact" or name the artifact. The build phase will need to remember this on its own.

**m-6 — Vague phrase: "use `render_existence_for_key` (existing) plus the source label" without showing the assembled `printf`.**
Location: IMPL_PLAN §C, line 216.
The LLM_PROVIDER row is shown explicitly (line 213). The two key rows are described but not coded. The exact `printf` format string + ordering of `find_var_with_source` calls + which globals are saved into which locals between calls is left to the implementer. Three sequential `find_var_with_source` calls all share `VAR_VALUE`/`VAR_SOURCE`, so the implementer must save into locals after each — the plan implies this but doesn't show it.

## 6. What I almost flagged but didn't

**A. `find_existing_key` global propagation across command-substitution.**
The plan's helpers set globals (`VAR_VALUE`, `VAR_SOURCE`, `EXISTING_KEY`, `EXISTING_KEY_SOURCE`). I almost flagged that command-substitution wraps would discard the globals — bash subshells don't propagate variables to parent. Re-read: every call site in the plan invokes the helper directly (NOT inside `$(…)`), so globals do propagate. Verified by smoke test. Safe.

**B. `subprocess.run(env=…)` HOME bleed-through.**
I expected the test to inherit the developer's `ANTHROPIC_API_KEY` from the parent shell and contaminate `find_key_in_environment`. Re-checked: Python's `subprocess.run(env=dict)` REPLACES the env entirely — it does not inherit unless `dict(os.environ, **overrides)` is used. The plan's helper uses `{"HOME": …, "PATH": …, **env_overrides}` with no `os.environ` merge, so the developer's globals are excluded. Safe.

**C. `find_var_count` returning 0 + `(( count > 0 ))` under `set -e`.**
I expected `set -e` to abort the script when `(( 0 > 0 ))` returns non-zero. Re-checked: arithmetic evaluation as the condition of an `if`/`while`/`&&`/`||` is exempt from `set -e`. The plan uses `if (( count > 0 ))` — exempt. Safe. The plan's risks section does mention this exact mitigation, which I cross-checked.

## 7. Final verdict

**ISSUES**

One MAJOR (M-1, symlinked rc_target false-positive replace warning) plus six MINOR. The MAJOR should be addressed before /v5-build because a managed-dotfiles user (a real persona, since `find_chain_warning` exists specifically for them) will see a misleading warning that contradicts the actual write behavior. The MINORs can be folded into the build pass but should not be silently dropped.

---

## Return summary

```
status: ISSUES
artifact: /Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/workbench-v6/2-plan/review/PLAN_VERIFIED_2026-05-05_setup-detects-existing-api-key.md
traceability: covered=8/8 must-have (incl. 8 BDD), missing=0, deferred=0 (MH6 partial)
hallucinated_files: 0
hallucinated_symbols: 0
checklist_orphans: skipped (checklist not present)
risk_findings: blockers=0, major=1, minor=6
top_issue: render_replace_warning equality check is symlink-blind — managed-dotfiles users will get a misleading warning when source is `~/.zshrc` and rc_target is the resolved symlink target
```
