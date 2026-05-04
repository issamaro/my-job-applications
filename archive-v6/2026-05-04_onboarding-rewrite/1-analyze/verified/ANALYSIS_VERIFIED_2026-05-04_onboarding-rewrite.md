---
slug: onboarding-rewrite
date: 2026-05-04
ceremony_level: L
phase: 1-analyze
artifact: ANALYSIS_VERIFIED
status: VERIFIED
revision: 3 (final)
reviewer: analysis-reviewer (Opus)
---

# Analysis Verified — onboarding-rewrite (revision 3, final)

**Status: VERIFIED** — clean enough to graduate to plan phase.

- All 4 prior MAJORs from revision 2 (N1 shell detection, N2 sed-pattern semantics, N3 partial-write/sed portability, N4 smoke.sh capture) closed by design changes in revision 3.
- Prior MINOR (N5 symmetric provider scenario) closed by Scenario 2g parameterization.
- Prior watch (N6 factory.py double-log) preserved as R6 in spec — correct disposition.
- 0 BLOCKER, 0 MAJOR, 0 new MINOR.
- 3 watch items recorded for plan-phase design questions.

---

## Resolution audit (revision 2 MAJORs → revision 3 fixes)

| ID | Prior issue | Resolution |
|---|---|---|
| N1 | `$SHELL` writes to wrong rc file (login vs interactive) | Spec L29: detect via `ps -p $$ -o comm=` |
| N2 | sed-replace pattern coverage unspecified | Spec L80-86: explicit `^export <VAR>=` start-anchored, comment/indent excluded; in-memory transform; duplicate-collapse policy |
| N3 | Partial-write + BSD/GNU sed | Spec "Atomicity" L33: in-memory transform → tmp → atomic mv. No `sed -i` anywhere |
| N4 | smoke.sh capture mechanism not specified | Spec "Out of scope" L104: smoke.sh deferred to follow-up backlog item; build-gate is manual inspector checklist (Spec L211-225) |
| N5 | Scenario 2e covered Gemini direction only | Scenario 2g now parameterized over P ∈ {claude, gemini} |
| N6 | factory.py:43 already prints "Using LLM provider:" | Spec R6 + UX L233-235: documented as intentional duplication, do not consolidate |

---

## Verified observations

**Atomic two-phase pattern closes prior partial-write concerns (N3):** Yes. Phase 1 read-only/decisions-only + Phase 2 in-memory transform → tmp → atomic mv → in-shell exports eliminates all three N3 failure modes. Contract observable via Scenario 2d (cancel anywhere → byte-identical rc).

**Inspector checklist sufficient as build gate:** Yes. All 8 smoke.sh observable checks have inspector counterparts (gh installed/auth, working dir name, LLM_PROVIDER + matching key, `uv run uvicorn --version`, dev.sh boot, HTTP 200, no command-not-found, `Using LLM provider:` line). Cost is human time; defensible as first-iteration gate.

**Scenarios 2a–2g all testable:** Yes. Each has concrete Given (specific rc state) + single When (specific user action) + observable Then (rc bytes / current-shell env / dev.sh stdout/stderr / HTTP status).

**Three-way alignment (refined.md / FEATURE_SPEC / deferred file):** Confirmed.

**No new ambiguities from pre-flight summary or explicit menu UX:** Pre-flight format example, anomaly warning text, and existing-key tail display are spelled out exactly enough.

**Duplicate-collapse "MAY choose either deterministically" tight enough at L:** "Exactly one remains" is the binary observable contract. "Deterministically" rules out random/race picks. Watch W2 records the policy decision for plan phase.

---

## Watch items for plan/build phase

These are NOT analysis blockers — they're design questions the planner should resolve before code lands.

### W1 — `~/.zshrc` symlink case

If the user has `~/.zshrc` as a symlink to a dotfiles repo, atomic `mv` over the symlink severs the link (replaces with a regular file at `~/.zshrc`). Out of the non-technical-friend persona scope, but a developer running setup.sh on a dotfiles-managed machine could lose their dotfiles linkage.

**Plan-phase decision needed:** detect symlinks via `[ -L ~/.zshrc ]` and either (a) `readlink -f` to find the real target and write there, (b) refuse with a diagnostic asking the user to inline the symlink first, or (c) accept the link-severing as a documented dev edge case.

### W2 — Duplicate-collapse pick policy

Scenario 2f says "implementation MAY choose either deterministically" — first-wins or last-wins, both acceptable. Implementer should pick one and document in code.

**Plan-phase decision needed:** pick first-wins OR last-wins. Recommend last-wins (the most-recent value is more likely to be the user's current intent).

### W3 — Pre-flight summary tail truncation

UX shows existing keys as `(ends in …wXYZ)` (last 4 characters). If an existing key is shorter than 4 chars (corrupted by an earlier write), behavior is undefined.

**Plan-phase decision needed:** display logic for short keys. Suggest: print `(ends in …<all-chars>)` when len < 4, or `(empty / suspicious)` when len == 0.

### Bonus watch — `ps -p $$ -o comm=` portability nuance

On macOS, `comm=` returns the basename of the executable; for login shells, that's `-zsh` (with leading dash). Exact-match `zsh` would miss `-zsh`. Recommend pattern matching: `*zsh` / `*bash`. Plan-phase implementation detail, not an analysis finding.

---

## BDD scenarios — testability matrix (final)

| # | Scenario | Verdict |
|---|---|---|
| 1 | Auth before clone | testable |
| 2a | Fresh shell-rc + Gemini paste | testable |
| 2b | Re-run, preserve orphan, collapse provider | testable |
| 2c | Existing key, Keep | testable |
| 2d | Cancel anywhere → no writes | testable (3 cancel paths) |
| 2e | Pre-flight mismatch warning | testable |
| 2f | Pre-flight duplicate collapse | testable; W2 watch |
| 2g | Backend boots, parameterized over provider | testable |
| 3 | Portable launch after mv | testable |
| 4 | URL agreement | testable |
| 5 | Repo name consistency | testable |

11/11 testable. Prior Scenario 6 (smoke evidence) correctly excised in tandem with smoke.sh deferral.

---

## Vague-term sweep

Zero blocking vague terms. Acceptable hedges remaining:
- "may" in Scenario 2f — qualified by "deterministically".
- "shouldn't happen" / "Should NOT occur" — guard rails for treat-as-regression cases, not happy-path requirements.

---

## UX state coverage

| Surface | Empty | Loading | Success | Error |
|---|---|---|---|---|
| README per-section | ✓ | ✓ | ✓ | ✓ §6 troubleshooting |
| setup.sh | ✓ | ✓ | ✓ | ✓ atomic-write fail + cancel paths |
| dev.sh | ✓ | ✓ | ✓ | ✓ mismatch crash + port busy |

No missing states. All have concrete copy.

---

## Requirement traceability

| Refined Scope IN | Must-Have | Scenario | Inspector |
|---|---|---|---|
| Single source of truth for dev URL | ✓ | 4 | 2, 8 |
| Auth layer before clone | ✓ | 1 | 3 |
| Correct repo name | ✓ | 5 | 1 |
| Provider selection persists | ✓ | 2a–2g | 4–7 |
| Portable venv + entrypoints | ✓ | 3 | 9 |
| End-to-end verification | ✓ (deferred smoke noted) | (manual) | 1–10 |

6/6 covered.

---

## Final verdict

**VERIFIED.** Orchestrator may proceed to plan phase. The plan-phase agent should treat W1, W2, W3, and the `ps -o comm=` portability nuance as design questions to answer before code lands.

```
status: VERIFIED
bdd: testable=11/11, untestable=0
vague_terms: 0
ux_states_missing: 0
traceability: covered=6/6, missing=0
risk_findings: blockers=0, major=0, minor=0
watch_items: 3 (W1 symlink rc, W2 collapse policy, W3 short-key tail) + 1 bonus (ps comm portability)
```
