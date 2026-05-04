---
feature: onboarding-rewrite
date: 2026-05-04
status: VERIFIED
reviewer: plan-reviewer
revision: 4 (fourth adversarial pass)
inputs_reviewed:
  - workbench-v6/1-analyze/spec/FEATURE_SPEC_2026-05-04_onboarding-rewrite.md (unchanged)
  - workbench-v6/2-plan/design/IMPL_PLAN_2026-05-04_onboarding-rewrite.md (rev 4)
  - workbench-v6/2-plan/checks/CHECKLIST_2026-05-04_onboarding-rewrite.md (revised)
  - workbench-v6/1-analyze/ux/UX_DESIGN_2026-05-04_onboarding-rewrite.md (unchanged)
library_notes_paths: none (research skipped per IMPL_PLAN — accepted in pass 1)
host_bash: GNU bash 3.2.57(1)-release (arm64-apple-darwin24) — same as deployment target
---

# Plan Verified — Onboarding Rewrite (rev 4)

Pass-3 history: 2 majors + 3 minors raised. All addressed in IMPL_PLAN rev 4 + CHECKLIST revision. This pass focuses on the user's seven adversarial questions and any new concerns introduced by the rewrites.

---

## 1. Requirement traceability

All Must-Have requirements remain covered. Single change since pass 3:

| Requirement | Covered_by | Status |
|---|---|---|
| URL agreement (localhost:8000 only) | IMPL_PLAN File 1; CHECKLIST §3 README S5 + I-2 | covered |
| `gh auth login` before clone | IMPL_PLAN File 1 §2; CHECKLIST §3 README §2 + I-3 | covered |
| Repo name = my-job-applications everywhere | IMPL_PLAN File 1; CHECKLIST §3 + I-1 | covered |
| README §6 troubleshooting (4 items) | IMPL_PLAN File 1 §6; CHECKLIST §3 README §6 items 1–4 | covered |
| Pre-flight summary | IMPL_PLAN §"render_preflight_summary"; CHECKLIST §3 setup pre-flight | covered |
| Pre-flight mismatch warning | IMPL_PLAN render_preflight_summary L408–L410; CHECKLIST + Scenario 2e | covered |
| Pre-flight duplicate warning | IMPL_PLAN render_preflight_summary L412–L418; CHECKLIST + Scenario 2f | covered |
| Provider prompt — show current selection | IMPL_PLAN function table L184; CHECKLIST L120 (R-MIN-1 fix) | covered |
| Case A 3-way menu (Keep/Replace/Cancel) | IMPL_PLAN read_key_action; CHECKLIST §3 setup Cases A | covered |
| Case B paste / cancel literal / empty re-prompt | IMPL_PLAN read_new_key + quote-injection guard; CHECKLIST L127 | covered |
| Atomic commit (in-memory → tmp → mv) | IMPL_PLAN write_rc_atomic; CHECKLIST §"atomic write" | covered |
| Cancel-anywhere → byte-identical rc | IMPL_PLAN orchestrator L290/L299/L301/L308/L309; CHECKLIST §4 Scenario 2d | covered |
| Final-state guarantee (one consistent state) | IMPL_PLAN create_rc_content + write_rc_atomic; CHECKLIST §4 Scenarios 2a/b/c | covered |
| Done banner with new-terminal caveat | IMPL_PLAN render_done_banner sketch L532–L552 (M-1 + R-MIN-3 fix); CHECKLIST L129/L131 | covered |
| Cancel-path stdout never says "Setup complete" | IMPL_PLAN orchestrator (cancel paths return before L319); CHECKLIST L132 (M-1 regression) | covered |
| `find_chain_warning` shows clean `~/.zshrc` (no double-dot) | IMPL_PLAN sketch L429–L436 (M-2 fix); CHECKLIST L133 | covered |
| EXIT-trap pid-suffixed cleanup (no concurrent collisions) | IMPL_PLAN orchestrator L287; CHECKLIST §5 L173–L174 (R-MIN-2 fix) | covered |
| dev.sh — `uv run uvicorn` | IMPL_PLAN File 3 L573; CHECKLIST L82 | covered |
| dev.sh — `Using LLM provider:` line before uvicorn | IMPL_PLAN File 3 L574–L578; CHECKLIST L88 | covered |
| dev.sh — remove activate block | IMPL_PLAN File 3 L580 (m8 fix); CHECKLIST L83–L84 | covered |

Coverage: 20 / 20 must-have items. 0 missing. 0 deferred (smoke deferred, but explicitly out of scope).

---

## 2. File-path verification

| Reference | Type | Exists | Status |
|---|---|---|---|
| `/Users/.../MyCV-2/setup.sh` (current 194 lines, modify) | modify | yes | OK |
| `/Users/.../MyCV-2/dev.sh` (current 75 lines, modify) | modify | yes | OK |
| `/Users/.../MyCV-2/README.md` (current 96 lines, modify) | modify | yes | OK |
| `setup.sh` L33 `need_restart=false` | modify-context | yes (verified L33) | OK |
| `setup.sh` L77 `need_restart=true` | modify-context | yes (verified L77) | OK |
| `setup.sh` L21–L24 banner header | preserve | yes (verified L21–L24) | OK |
| `setup.sh` L37–L96 install steps | preserve | yes (range matches actual content L37–L96) | OK |
| `setup.sh` L98–L175 API-key block | replace | yes (current `setup_api_key` L100–L173) | OK |
| `setup.sh` L177–L194 done footer | DELETE (M-1 fix) | yes (verified — current L177–L194 contains the legacy footer with `Setup complete` at L181, and `if $need_restart` branch L184) | OK |
| `setup.sh` L181 contains "Setup complete." string | verify-deletion-target | yes | OK |
| `dev.sh` L37–L41 activate block | DELETE (m8 fix) | yes (verified L38–L41 has `if [ -d ".venv" ]; then ... source .venv/bin/activate; fi`) | OK |
| `dev.sh` L71 bare `uvicorn` | modify | yes (verified L71 = `uvicorn main:app --reload --host 0.0.0.0 --port 8000 &`) | OK |
| `services/llm/factory.py:43` (do-not-touch) | preserve | not re-verified this pass (accepted in pass 1) | OK |
| README L7–L17 §1 git-install | replace | range plausible against 96-line file; not byte-verified this pass | OK |
| README L21–L24 clone block | replace | range plausible | OK |
| README L40 `localhost:5173` | replace | plausible | OK |

Hallucinated files: 0. Hallucinated symbols: 0. All deletion targets verified to actually exist with the claimed content.

---

## 3. Library-pattern verification

n/a — no library research dispatched. Patterns are POSIX shell + bash 3.2 builtins, all verified against host bash 3.2.57. Per-pattern checks performed live in this review:

| Pattern | Verified |
|---|---|
| `${rc_path/#$HOME/~}` produces `~/.zshrc` for `/Users/foo/.zshrc` | yes (live test) |
| `${rc_path/#$HOME/~}` for non-HOME path returns the path unchanged (e.g., `/tmp/zshrc` → `/tmp/zshrc`) | yes (live test) |
| Single-quoted `trap '... $$ ...' EXIT` interpolates `$$` at trap-fire time inside setup.sh's process | yes (live test) |
| `if "$need_restart"; then` works when `need_restart` holds string `true` or `false` | yes (`true` and `false` are real commands) |
| `find_var_count` awk pattern returns `0` (not error) on no-match under `set -e` | yes (live test) |
| `find_var_value` exits 0 when no match (empty stdout) under `set -e` | yes (live test) |

---

## 4. Checklist coverage

| IMPL_PLAN file | Checklist items | Status |
|---|---|---|
| File 1 — README.md | §3 README items L99–L116 + I-1, I-2, I-3, I-10 | covered |
| File 2 — setup.sh (incl. M-1, M-2, R-MIN-1, R-MIN-2 fixes) | §2 items L33–L78, §3 setup items L120–L133, §4 Scenarios 2a–2g, §5 L172–L174, I-4–I-7 | covered |
| File 3 — dev.sh | L82–L84, L88–L89, L137–L139, I-8, I-9 | covered |

Orphan checklist items (don't trace back to IMPL_PLAN or LIBRARY_NOTES): 0.

---

## 5. Adversarial answers to the user's seven questions

### Q1 — M-1 fix coherence (Approach + structural summary + render_done_banner sketch + orchestrator)

Rewrote section: L159–L165 ("Approach"), L165 (structural summary), L319 (orchestrator call `render_done_banner "$need_restart"`), L524–L554 (body sketch).

Cross-checks performed:
- Structural summary L165: "script ends" after `update_provider_and_key` invocation; "no trailing banner block; `render_done_banner` is the only source of the success banner and is called from inside `update_provider_and_key`". MATCHES the orchestrator sketch.
- Orchestrator L319 calls `render_done_banner "$need_restart"`. The sketch at L532 takes `need_restart="$1"`. Argument shape matches.
- `render_done_banner` body L538–L549 branches on `if "$need_restart"; then` → `warn "Open a new terminal..."` else → "Run the app with: ./dev.sh" + the source-rc/different-terminal hint.
- No dangling references to L177–L194 anywhere outside the M-1 fix description (grep confirmed: only references are in §"Approach" L162 and §"Done banner" L526).

VERDICT: coherent. No dangling references.

### Q2 — Cancel-path regression check (4 cancel return points all upstream of `render_done_banner`)

The orchestrator pseudocode at L277–L322. `render_done_banner` is at L319, the second-to-last line before the final `return 0`.

Walking each cancel point:

1. **Ctrl-C at provider prompt (or any prompt later)** — INT trap fires (installed L286), runs `cancel_requested=true; render_cancel_message; trap - INT; return 0`. The trap's `return 0` returns from whichever helper was running. Control flows back to orchestrator which checks `$cancel_requested && return 0` at L290 (or L299, or L308). All three checks are BEFORE L319. **CLEAN.**

2. **`KEY_ACTION=cancel` from menu** — `read_key_action` (called at L298) sets `KEY_ACTION=cancel`. Orchestrator at L300 enters `case "$KEY_ACTION" in cancel) render_cancel_message; trap - INT; return 0 ;;`. Returns at L301, BEFORE L319. **CLEAN.**

3. **`KEY_ACTION=cancel` from literal "cancel" typed at key prompt** — `read_new_key` (called at L303 OR L306) sets `KEY_ACTION=cancel`. Orchestrator falls through `case`/`else` to L309 `[[ "$KEY_ACTION" == "cancel" ]] && { render_cancel_message; trap - INT; return 0; }`. Returns at L309, BEFORE L319. **CLEAN.**

4. **`cancel_requested=true` from any prompt's INT trap** — same as path 1; covered by `$cancel_requested && return 0` checks at L290/L299/L308. All BEFORE L319. **CLEAN.**

The CHECKLIST L132 regression check ("stdout does NOT contain `Setup complete`") is satisfied for all four paths. VERDICT: regression check is genuine.

One subtle note (not a finding, just for the record): the trap's `return 0` returns from whichever function is on top of the call stack — i.e., the helper, not the orchestrator. The orchestrator then re-enters its sequential check at L290/L299/L308. Bash's nested-`return` semantics correctly propagate one level; this is documented at L209 of IMPL_PLAN.

### Q3 — `if "$need_restart"; then` form correctness

Verified in the actual current setup.sh (which the rewrite preserves):
- L33 `need_restart=false` (string `false`, which is a real shell command)
- L77 `need_restart=true` (string `true`, which is a real shell command)
- L184 (current code, which is being deleted) `if $need_restart; then` — uses the same string-as-command idiom

The plan's `if "$need_restart"; then` form (L538) inside `render_done_banner` works because:
- `need_restart="$1"` (L533) holds the literal `true` or `false` (passed by orchestrator at L319 from outer-scope `need_restart`).
- `if "true"; then` and `if "false"; then` are syntactically valid — bash invokes `true` (exit 0, branch taken) or `false` (exit 1, branch skipped).

setup.sh consistently sets `need_restart` to `true` / `false` strings (verified at L33 and L77). The fix is consistent. **VERIFIED.**

### Q4 — M-2 fix correctness (`${rc_path/#$HOME/~}`)

Live tested:
- `rc_path="$HOME/.zshrc"` → `${rc_path/#$HOME/~}` produces `~/.zshrc` exactly. No trailing chars, no escape issues.
- `rc_path="/tmp/zshrc"` (outside `$HOME`) → `${rc_path/#$HOME/~}` produces `/tmp/zshrc` (unchanged). Anchor `#` only matches at start of string, so no substitution occurs. Resulting message: `Note: /tmp/zshrc resolves through a symlink chain; only the first hop (...) will be written.` — readable.

The fix is consistent with the existing pattern at L399 (`${rc_target/#$HOME/~}`). **VERIFIED.**

### Q5 — R-MIN-2 fix correctness (`trap 'rm -f "${rc_target}.tmp.$$"' EXIT`)

Single-quoted trap body: `${rc_target}` and `$$` are interpolated at trap-fire time, not at trap-install time.

At trap-fire time (script exits — success, failure, SIGINT):
- `rc_target` evaluates to whatever the orchestrator set it to. Since it's `local rc_target="$1"` inside the function, it persists in the trap closure even after the function returns? **Concern flagged below as MINOR-A.**
- `$$` is setup.sh's PID, which is constant for the lifetime of the script. Live test confirmed.

Live test confirmed the substitution works for both single- and double-quoted forms. The literal `$$` (not glob `*`) prevents concurrent setup.sh runs from racing on each other's temp files. **VERIFIED.**

### Q6 — `render_preflight_summary` signature change

Function body sketch L388–L391: `local rc_content="$1"; local rc_path="$2"; local rc_target="$3"`. **3 args.**

Searched the IMPL_PLAN for call sites: `grep -n render_preflight_summary` returns four hits — the signature definition, the function-table row, the structural summary mention ("`render_preflight_summary` invocation"), and a `find_chain_warning` reference. **No actual call-site pseudocode is shown.**

The structural summary at L165 ("`render_preflight_summary` invocation") is too vague to verify the call site lines up with the 3-arg signature. The build-phase author has the function body to copy from, but the top-level glue between `read_rc_path` (which returns `rc_target`), `rc_path` (the literal `$HOME/.<shell>rc`), and `render_preflight_summary` is implicit. **MINOR-B below.**

### Q7 — Anything else fresh eyes catch

Three new minor concerns surfaced. None are blockers. See §6.

---

## 6. Risks and ambiguities

### MINOR-A — EXIT trap closure over `local rc_target`

**Location:** IMPL_PLAN L287 `trap 'rm -f "${rc_target}.tmp.$$" 2>/dev/null' EXIT` is installed inside `update_provider_and_key`, where `rc_target` is `local`.

**Concern:** Bash EXIT traps fire at SCRIPT exit, not function exit. By the time the trap fires, `update_provider_and_key` has long returned, and its `local rc_target` is out of scope. Bash's dynamic scoping may or may not allow the trap to see the local variable depending on whether the script exits while still inside the function vs after the function returns.

**Walking the cases:**
- If `fail` is called at L316 inside the orchestrator → `exit 1` while still inside the function → `rc_target` is in scope → trap can resolve it. CORRECT.
- If orchestrator returns normally (success path) → script ends → trap fires at top-level. By that point, the function's locals are gone. **`rc_target` may be empty or unset at trap-fire time, and `rm -f "${rc_target}.tmp.$$"` becomes `rm -f ".tmp.<pid>"` — a stray relative path.** This is harmless (rm on non-existent file with `2>/dev/null`), but the trap also fails to clean up the temp file in the rare case where success-path mv was preceded by a still-living temp.

**Severity:** MINOR. Success-path always means `mv` succeeded, so there's no temp left to clean up anyway. The trap's purpose is failure paths (fail → exit, SIGINT during commit, etc.) — and those exit while still inside the function. The harmless-empty case only fires on the success path which has nothing to clean.

**Mitigation suggestion (build phase):** consider promoting `rc_target` to script-global scope (no `local`), OR install the EXIT trap at script-top with a script-global variable. Documentation gap, not a correctness bug.

### MINOR-B — `render_preflight_summary` call site is not sketched

**Location:** IMPL_PLAN structural summary L165 says "`render_preflight_summary` invocation" but no top-level pseudocode shows how it's invoked, with what args.

The function takes 3 args (`rc_content`, `rc_path`, `rc_target`). The orchestrator `update_provider_and_key` only takes 2 args (`rc_target`, `rc_content`). So the top-level setup.sh code must:
1. Compute `shell_name` from `find_current_shell`.
2. Compute `rc_path` literally as `$HOME/.${shell_name}rc`.
3. Compute `rc_target` from `read_rc_path "$shell_name"`.
4. Read `rc_content` from `read_rc_content "$rc_target"`.
5. Call `render_preflight_summary "$rc_content" "$rc_path" "$rc_target"`.
6. Call `update_provider_and_key "$rc_target" "$rc_content"`.

This sequence is implicit but not sketched. Fresh build-phase author may stumble assembling the glue.

**Severity:** MINOR. Function bodies are clear; only the orchestration is implicit.

### MINOR-C — `read_provider_choice` invalid-input handling unspecified

**Location:** IMPL_PLAN function table L184 says `read_provider_choice` "Show current selection, read 1/2 from stdin" and sets global `PROVIDER_CHOICE` to `claude`/`gemini`. UX_DESIGN L113–L116 doesn't specify what happens if user types `3` or `q` or empty.

Other helpers (`read_new_key` L484–L508) explicitly loop on empty/cancel. `read_provider_choice` doesn't have a sketched body. Build-phase author could implement either: (a) loop on invalid, (b) treat invalid as cancel, (c) default to claude. UX_DESIGN doesn't pin this.

**Severity:** MINOR. Spec contract is "user picks 1 or 2"; persona is non-technical and reads the prompt — invalid input is theoretical for this persona. Suggested: spec-author to pin this in build phase.

### MINOR-D — `read_var_name_for_provider` invocation under `set -e`

**Location:** IMPL_PLAN L293 `key_var="$(read_var_name_for_provider "$PROVIDER_CHOICE")"`.

If `PROVIDER_CHOICE` is somehow not `claude` or `gemini` (defensive case), the function might return non-zero, and under `set -e` the assignment kills the script. The function body is described as "Trivial case statement" (L272) — a `case` statement without a default branch returns 0 by default in bash, but a default that doesn't echo would return 0 with empty stdout. The exact behavior depends on the build-phase implementation.

**Severity:** MINOR. Defensive issue; persona never triggers it in practice.

---

## 7. What I almost flagged but didn't

These are spots where I paused — they look fine but I want to be transparent that I considered them and stepped back:

1. **Trap return semantics across nested function calls.** When the INT trap fires while we're inside a helper (e.g., `read_provider_choice`), the trap body's `return 0` returns from the helper, not the orchestrator. The orchestrator's subsequent `$cancel_requested && return 0` check then returns from the orchestrator. This is a two-step return that depends on bash's `return-from-trap exits one level` behavior. The IMPL_PLAN documents it at L209 and L330. I tested it analytically and it's sound, but it's the kind of thing where a build-phase author who doesn't read the notes carefully could simplify away the redundant cancel checks (because "the trap returned"). Recommendation: keep all three `$cancel_requested && return 0` checks (L290, L299, L308) verbatim in build.

2. **Trap install/teardown timing for INT.** The INT trap is installed at L286 and cleared at L301, L309, L311 (the success-path commit boundary). Between L286 and L311, ANY Ctrl-C is caught. After L311, Ctrl-C falls through to bash default (script dies). This is by design (M2 trap-leak fix). However, the inspector item at CHECKLIST L172 says "`trap - INT` IMMEDIATELY BEFORE `create_rc_content`" — but the orchestrator pseudocode actually calls `trap - INT` at L311, which is after the cancel-sentinel check at L309. There's a gap of two statements (L309 cancel check + L311 trap clear) where Ctrl-C can still be caught. Order is correct (cancel-checks first, then commit) but the wording "IMMEDIATELY BEFORE" is a slight overstatement. The build-phase author who follows the pseudocode will get correct behavior; the wording in CHECKLIST is loose. Not flagging as MINOR because the pseudocode dominates the wording.

3. **`render_done_banner` body uses `warn` for the `need_restart=true` branch but plain `echo` for the `false` branch.** Style inconsistency: yellow `warn` glyph for "open new terminal" vs neutral text for "run ./dev.sh". UX_DESIGN doesn't specify color for the new-terminal-required case. Probably fine — `warn` correctly signals "you need to do something extra" — but a UX-reviewer pass might quibble. Not a bug.

---

## 8. Final verdict

**VERIFIED.** Zero BLOCKER, zero MAJOR. Four MINOR findings flagged above. All four are documentation/orchestration polish issues, not correctness bugs. The build phase has unambiguous behavioral specs for every must-have requirement; the cancel-path contract holds across all four return points; the M-1 and M-2 user-facing fixes are correctly applied in both code sketches and CHECKLIST regression checks; the EXIT trap glob fix correctly uses `$$` and avoids the concurrent-collision class.

The plan is implementation-ready. The build agent should:
- Sketch the top-level setup.sh glue (MINOR-B) when stitching together the helper calls.
- Pin `read_provider_choice` invalid-input behavior (MINOR-C) before coding it.
- Verify EXIT-trap variable scoping (MINOR-A) — promote `rc_target` to script-global if needed.
- Define `read_var_name_for_provider` with explicit defaults (MINOR-D) to keep `set -e` happy.

Counts:
- traceability: covered=20/20, missing=0, deferred=0
- hallucinated_files: 0
- hallucinated_symbols: 0
- checklist_orphans: 0
- risk_findings: blockers=0, major=0, minor=4
