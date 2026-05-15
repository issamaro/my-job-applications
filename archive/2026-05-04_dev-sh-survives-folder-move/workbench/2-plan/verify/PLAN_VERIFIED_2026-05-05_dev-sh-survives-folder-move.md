# PLAN_VERIFIED — dev.sh survives a moved project folder

- **feature:** dev-sh-survives-folder-move
- **date:** 2026-05-05
- **status:** VERIFIED
- **reviewer:** plan-reviewer
- **inputs_reviewed:**
  - `backlog/refined/dev-sh-survives-folder-move.md` (acts as FEATURE_SPEC, ceremony S — analyze skipped)
  - `workbench-v6/2-plan/design/IMPL_PLAN_2026-05-05_dev-sh-survives-folder-move.md`
  - `workbench-v6/2-plan/research/uv-venv-relocation.md`
  - CHECKLIST not yet generated (parallel agent in flight) — coverage check deferred per caller instruction.
  - No UX_DESIGN (no UI surface).

---

## 1. Requirement traceability

The refined spec lists five success criteria (treated as Must-Have requirements). No Should-Have list.

| # | Requirement | Covered by | Status |
|---|---|---|---|
| 1 | After `mv`, `./dev.sh` exits 0 and backend returns 200 with no manual intervention beyond `cd`. | Plan §"Approach chosen — B" (line 19–21): `uv run python -m uvicorn` resolves through still-valid `.venv/bin/python` symlink, never touches broken shim. Backed by library notes Q2 + verified symlink target points outside project. | covered |
| 2 | `dev.sh` does not unconditionally rebuild the venv. | Plan §"Why not A or C" (line 24–25) explicitly rejects unconditional rebuild; final `dev.sh` keeps existing `uv sync --quiet` line and only swaps the launch verb. | covered |
| 3 | If recreation is triggered, single human-readable line explains it. | Vacuously satisfied — approach B never triggers recreation. The conditional ("If recreation is triggered…") is unreachable in B. The plan correctly notes recovery is a manual `rm -rf .venv && uv sync` inside README §6, not an automated path. | covered (vacuously) |
| 4 | README §6 has an entry titled `uvicorn: command not found` or `Failed to spawn: uvicorn`. | Plan §2, line 65: title includes both: ``Failed to spawn: uvicorn` (or `uvicorn: command not found`)``. | covered |
| 5 | Existing pytest suite still passes. | Plan §"Test plan" line 102: existing `uv run pytest` must remain green. No app-level change is made, so regression risk is low. | covered |

No must-have is missing. No deferred requirements.

---

## 2. File-path verification

| Reference | Type | Exists | Status |
|---|---|---|---|
| `dev.sh` line 67: `uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 &` | modify | `test -f` PASS; `grep -n` confirms exact match at line 67. | OK |
| `README.md` lines 85–86 (existing entry: ``**`uvicorn: command not found` after I moved the project folder.**``) | modify | `test -f` PASS; lines 85–86 verified verbatim against the plan's "Before" block. | OK |
| `README.md` line 167: `uv run uvicorn main:app --reload` | modify | `test -f` PASS; `grep -n` confirms exact match at line 167. | OK |
| `.venv/bin/uvicorn` (referenced by manual test only — not modified by the plan) | inspect-only | Verified shim exists; shebang line 2 contains absolute path baked at venv-creation. | OK |
| `.venv/bin/python` symlink (load-bearing for the fix) | inspect-only | Verified `lrwxr-xr-x` symlink → `/Users/aissacasa/.local/share/uv/python/cpython-3.13.9-macos-aarch64-none/bin/python3.13` (target is OUTSIDE the project, survives `mv`). | OK |
| `.venv/pyvenv.cfg` `home =` line | inspect-only | Verified `home = /Users/aissacasa/.local/share/uv/python/cpython-3.13.9-macos-aarch64-none/bin` (outside project). uv version pinned `uv = 0.9.8` matches plan claim. | OK |

No hallucinated file paths. No hallucinated symbols (the plan modifies one shell command in two files; no code symbols referenced).

---

## 3. Library-pattern verification

| Pattern | Documented in | Status |
|---|---|---|
| `uv run python -m <module>` to bypass console-script shims | `uv-venv-relocation.md` Q2 (line 28–50): explicit answer "Yes, with high confidence" — `uv run` locates `.venv/bin/python` (interpreter binary, not a shim) then `python -m` resolves via `sys.path`, never touching the shim. The `--module`/`-m` flag is documented at docs.astral.sh/uv/reference/cli (cited line 46–47). | OK |
| Recovery path `rm -rf .venv && uv sync` in README | `uv-venv-relocation.md` Q3 (line 52–66): documented two-step is `uv venv && uv sync`, equivalent because `uv sync` recreates an absent venv. The README phrasing is consistent. | OK |
| `uv sync` runs early in `dev.sh` to catch pruned interpreter | `uv-venv-relocation.md` Q1 (line 11–25): `uv sync` does NOT repair shims, but it WILL surface a missing/pruned interpreter loudly (`Q4` row 1: `uv python find` succeeds only if `.venv/bin/python` resolves). Plan's claim (line 30: "if Python is missing, `uv sync` errors loudly") is consistent. | OK |

No deprecated APIs used. No undocumented patterns.

Note on a flagged research uncertainty: line 118 of the library notes says "Whether `uv run` re-resolves `.venv/bin/python` via the real binary or via a shim is not explicitly stated in the docs. Empirical testing on a moved project is advisable before shipping." The plan addresses this by including a manual smoke test (Test plan steps 1–4) that validates the launch path with a deliberately-broken shim. This is acceptable empirical coverage, but see §6 for one caveat about the simulation fidelity.

---

## 4. Checklist coverage

CHECKLIST file not present at review time:
`workbench-v6/2-plan/checklist/CHECKLIST_2026-05-05_dev-sh-survives-folder-move.md` did not exist when this review ran. The caller noted this is acceptable (parallel checklist-builder still in flight).

| Plan file/section | Expected checklist items | Status |
|---|---|---|
| `dev.sh` line 67 swap | one verification item ("dev.sh line 67 reads `uv run python -m uvicorn …`") | DEFERRED — checklist not generated yet |
| README §6 entry replacement (lines 85–86) | one verification item (title contains "Failed to spawn" or "command not found"; body references `python -m uvicorn`; manual recovery `rm -rf .venv && uv sync` present) | DEFERRED |
| README "Manual setup → Run" line 167 swap | one verification item | DEFERRED |
| Manual regression test | one inspector checklist item per plan step 1–4 | DEFERRED |

This row is DEFERRED, not ISSUE — the caller authorised independent review when the checklist isn't ready. Reviewer should re-run §4 once the checklist lands.

---

## 5. Risks and ambiguities

| # | Finding | Location | Severity |
|---|---|---|---|
| 1 | Manual test does not simulate a true `mv` — it edits the uvicorn shim shebang only. The python symlink and `pyvenv.cfg` `home =` are not touched in the test. The reviewer confirmed those targets are absolute paths outside the project (so they DO survive a real `mv`), making the partial simulation behaviourally equivalent for this specific fix. But anyone running this test should know it covers the broken-shim mechanism only, not a full filesystem relocation. The plan should call this out as a known limitation. | IMPL_PLAN line 105–107 ("Edit `.venv/bin/uvicorn`'s shebang…") | MINOR |
| 2 | `PROJECT_CHECKS.md` line 156 contains `uvicorn main:app --reload &` after `source .venv/bin/activate`. Both the activate script (verified: VIRTUAL_ENV is hardcoded absolute on line 81) and the bare `uvicorn` resolution through `$PATH` would break post-`mv`. The plan does not touch this file. The refined spec scope-IN says "and/or `setup.sh`" and "manual-setup path in README" — `PROJECT_CHECKS.md` is not explicitly named. Reasonable to defer, but a future contributor copy-pasting from there reintroduces the bug. Worth a one-line acknowledgement in the plan's risk table. | not in plan; PROJECT_CHECKS.md:155–156 | MINOR |
| 3 | Plan §"Risks" row 2 ("User on uv < 0.4 where `uv run python -m` semantics differ") cites mitigation "repo pins `uv = 0.9.8` via `pyvenv.cfg`". Verified pinning is real, but `pyvenv.cfg` is a record of the venv-builder version, NOT a constraint on the user's installed `uv`. If a user has uv 0.3 installed system-wide and runs `uv sync`, it will sync against this venv but `uv run` semantics are whatever uv 0.3 provides. The mitigation chain is `setup.sh` → `brew install uv` (latest), which is sufficient for new installs but not for users who installed uv before this feature. Probability is genuinely very low (uv 0.4 is from 2024) and the symptom would be obvious. Not a blocker; just an inaccurate citation of `pyvenv.cfg` as a version pin. | IMPL_PLAN line 97 | MINOR |
| 4 | The `--reload` watcher behaviour under `python -m uvicorn` vs. console-script `uvicorn` is asserted equivalent (plan line 96) but not verified. The plan adds a manual smoke-check ("confirm `--reload` still picks up file edits") in inspect, which is the right place to verify. No issue. | IMPL_PLAN line 96 | MINOR (already mitigated) |

No BLOCKER. No MAJOR. Four MINOR findings, all of which are signal-level rather than gating.

The plan does not contain any vague terms ("appropriate"/"robust"/"as needed"/"etc."), unbounded loops, or unspecified error handling. Database/concurrency concerns N/A (shell launcher only).

---

## 6. What I almost flagged but didn't

These are spots where I pushed on the plan and decided it was OK, but they're the weakest seams an attacker would probe.

1. **The "rare" qualifier in the README §6 entry.** Plan line 66 says: "If you still see this error (rare — usually means the uv-managed Python was uninstalled separately)…" This is unverified — there could be other failure modes (Time Machine restore that breaks the symlink chain, brew uninstalling Python and cleaning the cache, FUSE/cloud-storage filesystems that don't preserve symlinks correctly). I almost flagged this as MAJOR for being speculative, but in practice the user-facing recovery (`rm -rf .venv && uv sync`) is correct for ALL of those failure modes, so the qualifier is harmless even if incomplete. Calling it "rare" is editorial; the recipe is sound.

2. **Heredoc-style nested code fences inside the README "After" block.** The plan's "After" markdown (IMPL_PLAN lines 64–73) has triple-backtick fences inside an outer triple-backtick demonstration block. When typed verbatim into the README, this nests one code block inside the troubleshooting entry — markdown handles this fine, but if the implementing agent copy-pastes the OUTER fence by mistake, the README will have an extra orphan ` ``` `. Low-likelihood typo risk; the implementer just needs to recognise the outer fence is illustrative. Not a structural issue with the plan.

3. **`uv run python -m uvicorn` lockfile-staleness behaviour.** `dev.sh` already does `uv sync` first (line 39) and then `uv run python -m uvicorn` will run another implicit lockfile check (per uv docs: "Before each execution, uv run ensures that your lockfile is synchronized with pyproject.toml"). That's two consecutive sync checks per dev.sh invocation. Not a bug, not a regression vs. the current `uv run uvicorn` which has the same double-check, but a missed efficiency opportunity (`--no-sync` on the second call). Out of scope per the spec's latency-budget criterion #2 (steady-state has not regressed), so not flagged. If anyone ever asks "why is dev.sh slow to start" this is the line to look at.

---

## 7. Final verdict

**VERIFIED** — no BLOCKER, no MAJOR. Four MINOR findings (test simulation fidelity caveat, PROJECT_CHECKS.md scope question, inaccurate `pyvenv.cfg` version-pin claim, `--reload` not pre-verified). All MINORs are acknowledgement-quality, not gating. The plan can proceed to /v5-build.

The traceability is clean (5/5 must-have requirements covered), file paths and symbols are real (no hallucinations), library patterns are documented, and risk reasoning is sound. The choice of approach B over A or C is well-justified against criterion #2 specifically, which was the failure mode of the prior onboarding-rewrite attempt.
