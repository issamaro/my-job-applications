---
slug: onboarding-rewrite
date: 2026-05-04
ceremony_level: L
phase: 4-ship
artifact: RETROSPECTIVE
---

# Retrospective — Onboarding Rewrite

## What surprised

- **Plan-reviewer ran four adversarial passes before VERIFIED.** Two majors (M-1 cancel-paths-fall-through-to-Done-banner, M-2 double-dot symlink display) and three minors (R-MIN-1/2/3) only surfaced under repeated adversarial pressure. The first pass gave a CLEAN verdict for the cancel-path coverage; the third pass caught that the legacy Done footer at L177–L194 of the old setup.sh would still print "Setup complete" on cancel paths because the cancel branch returned from the function but the script kept executing. Lesson: the second adversarial pass on the SAME plan still finds real defects — the value of the gate compounds.

- **Bash trap-with-`return`-from-function actually works on bash 3.2.57.** The plan placed an `INT` trap that calls `return 0` from inside the orchestrator function, expecting the cancel path to short-circuit before the atomic-commit boundary. Confirmed working on the host's bash 3.2.57 (same as deployment target). The watch was real — earlier sketches that used `$(read_helper)` would have hidden `read -r` from the parent's INT trap because subshell stdin captures the signal.

- **`grep -c` under `set -e` is a footgun.** `find_var_count` originally looked like a one-liner `grep -c '^export VAR=' rc`, but `grep -c` returns exit code 1 when count is zero, which kills the script under `set -e`. Switched to awk-with-`n+0`-coercion so the function always exits 0. This was caught at plan time, not build time — good plan hygiene.

- **macOS `readlink` doesn't have `-f`.** Single-hop `readlink` returns the literal symlink target, which can be relative (e.g., `dotfiles/zshrc` from a Stow setup). Without resolving relative-to-`dirname` of the link path, the atomic `mv` would write a phantom file inside setup.sh's cwd. The fix in `read_rc_path` is six lines, but the failure mode is silent — write succeeds in a wrong location, user never sees the warning.

## What was harder than expected

- **The 17-helper function ladder.** Lean-code's verb-prefix + ≤3-words-after-verb + one-job-per-function rules forced naming each shell-rc operation explicitly. Initial sketch had `read_var_name_for_provider` (4 words after verb — violates rule). Renamed to `read_provider_var`. The rule pays off in setup.sh now reading like a sequence of verbs, but the compliance pass took a non-trivial fraction of plan time.

- **Mode-preservation contract.** Plan-reviewer rev 3 caught that the naive `printf > tmp; mv tmp rc` widens permissions: the temp inherits the user's umask (typically 0644), and `mv` propagates the temp's mode to the destination — so a user with `chmod 600 ~/.zshrc` would silently end up world-readable on every `setup.sh` run. This is a real privacy regression because the rc now contains `*_API_KEY` values. Fix is umask 077 floor + `stat` (BSD `-f` then GNU `-c` fallback) to preserve the original mode. Three lines of code, but the failure mode would not have been caught by any automated test in scope.

- **Cancel-path stdout discipline.** The contract that cancel paths must NOT print "Setup complete" required deleting the legacy script-bottom Done block AND moving the success banner inside `update_provider_and_key`'s success branch only. M-1 in plan-reviewer rev 3. A regression check is now in CHECKLIST L132.

## What the next similar feature should do differently

- **Run plan-reviewer at least twice before declaring VERIFIED.** Even when pass 1 is CLEAN. The compounding-defect-detection observation above suggests a "two clean passes, not one" rule for L/XL features. Cheap relative to the cost of shipping a cancel-path or mode-widening regression.

- **Validate bash idioms against the deployment target's shell version, not the latest.** macOS ships bash 3.2 by default. The plan explicitly avoided `${var^^}`, `declare -A`, and other 4+-isms. Without that gate, build-phase debugging would have been painful. For future shell features: state the target version in the plan's "Library / runtime research" section even when no library is used.

- **Test create_rc_content on its own before the full script runs.** During build I extracted the function via `awk` and ran it against four scenarios (2a fresh, 2b switch, 2c keep, 2f duplicate-collapse) before running the script end-to-end. Caught one cosmetic blank-line accumulation issue immediately. Worth doing for any function that performs file content surgery.

## Anything to add to project-checks.md

There is no project-level `project-checks.md` at repo root in this project. If/when one is created, two items earned by this feature:

1. **Shell-rc edits go through atomic temp-file + mv with mode preservation.** Never `sed -i ''` (BSD-only AND partial-write risk) and never bare `>>` (no rollback). Pattern: in-memory transform → tmp at `${target}.tmp.$$` → `chmod` to original mode → `mv`. EXIT trap removes the pid-suffixed temp on every exit path.

2. **Function names in shell scripts follow lean-code's 9-verb whitelist.** `read, write, create, delete, update, find, check, parse, render`. Three-words-after-verb max. Existing `step`/`ok`/`warn`/`fail` palette helpers are grandfathered (renaming would create churn outside any feature's scope), but no new helper should be added with those names or with `setup_X`, `print_X`, `do_X`, `handle_X`, etc.

## v6 workflow notes

- **Two parallel adversarial gates (analysis-reviewer, plan-reviewer) earned their keep.** Both surfaced real issues that the build phase would otherwise have hit. Recommend keeping them at full ceremony for L+ features.

- **Skipping parallel docs-researcher dispatch was correct.** Zero new dependencies; no library version-sensitivity. The plan's explicit "skipped (with rationale)" section was useful as evidence for the plan-reviewer.

- **Manual inspector checklist ran 10 items.** Four (the static doc checks I-1, I-2, I-3, I-10) were verifiable by grep + skim during build. Six (the runtime/interactive items I-4 through I-9) are deferred to fresh-VM smoke validation. The deferred-smoke pattern works for shell-script + docs features where the cost of fresh-machine setup is high — but it means "build pass" is provisional until the VM run lands. Acceptable for a solo project.
