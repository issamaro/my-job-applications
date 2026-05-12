---
feature: topbar-shell
date: 2026-05-11
status: ISSUES
reviewer: plan-reviewer
ceremony_level: S
inputs_reviewed:
  - backlog/refined/topbar-shell.md
  - workbench-v6/2-plan/design/IMPL_PLAN_2026-05-11_topbar-shell.md
  - workbench-v6/2-plan/checks/CHECKLIST_2026-05-11_topbar-shell.md
  - design-bundle/project/shell.jsx (design source)
  - src/App.svelte
  - src/styles/global.css
  - src/components/TabNav.svelte
  - src/components/ResumeGenerator.svelte
  - tests/test_design_tokens.py
  - public/index.html
  - package.json, .python-version
---

# Plan verification — topbar-shell

## 1. Requirement traceability — refined "Scope IN" vs IMPL_PLAN

| Refined "Scope IN" bullet | Covered by | Status |
|---|---|---|
| Build Svelte `Topbar` from `shell.jsx` (small sigil + wordmark + nav + search pill + initials) | IMPL_PLAN §3.1 (create `Topbar.svelte`) | covered |
| Nav exposes 6 slots in order: dashboard, pipeline, jobs, profile, tailor, interview | IMPL_PLAN §3.1 slots table + §4 mapping | covered |
| Click-behavior for the four no-screen slots decided during /v6-feature analyze | IMPL_PLAN §1 (Q0.2 decision: render disabled / non-clickable) | covered |
| Wire `Topbar` as persistent shell in `App.svelte` above every page body | IMPL_PLAN §3.2 (modify App.svelte; Topbar rendered outside `.container`) | covered |
| Retire `TabNav.svelte` OR absorb into Topbar | IMPL_PLAN §3.4 (delete `TabNav.svelte`) | covered |
| Drive active link from existing `activeTab` state | IMPL_PLAN §3.1 props + `$derived` activeSlotId | covered |
| Active treatment: ink color + 1px ink underline | IMPL_PLAN §3.1 "Slot active state" + §5 | covered |
| Legacy `activeTab` mapping: `'profile'` → profile slot, `'resume'` → tailor slot | IMPL_PLAN §4 decision table | covered |
| Light-only, topbar-only — no `[data-layout]`, no sidebar, no mobile drawer | IMPL_PLAN §1 closing line | covered |

| Refined success criterion | Covered by | Status |
|---|---|---|
| Topbar renders top of every page, replaces old `<header>`+`TabNav` | §3.2 changes 1–3 + §8 test 1, 2 | covered |
| Profile slot renders Profile, tailor slot renders Resume Generator | §3.2 change 4 + §8 test 5 | covered |
| Active nav link visually distinct (ink + underline) | §3.1 + §8 test 3 | covered |
| 64px tall, paper bg, 1px rule bottom, etc. | §3.1 "Styles" block + checklist 3.1 row "Topbar height 64px..." | covered |
| No sidebar element, no `[data-layout]`/`[data-theme]` selectors | §1 + scope OUT | covered (asserted by absence; no explicit test) |

| Refined BDD scenario | Mapped checklist item | Status |
|---|---|---|
| Click "Tailor CV" from Profile → Resume Generator renders + Tailor CV gets active treatment | CHECKLIST §4 `test_click_tailor_routes` (line 89) | covered |
| Inspect shell on any page → only nav surface is the editorial Topbar (no sidebar, no legacy TabNav block) | CHECKLIST §4 `test_no_legacy_tab_nav` + `test_topbar_renders_at_top` (lines 85–86) | covered |

All "Scope IN" bullets and both BDD scenarios trace to either a plan step or a test.

## 2. File-path verification

| Reference | Type | Exists | Status |
|---|---|---|---|
| `src/components/Topbar.svelte` | CREATE | n/a (parent `src/components/` exists) | OK |
| `src/components/TabNav.svelte` | DELETE | yes | OK |
| `src/App.svelte` | MODIFY | yes | OK |
| `src/styles/global.css` | MODIFY | yes | OK |
| `tests/test_topbar_shell.py` | CREATE | n/a (parent `tests/` exists, sibling `test_design_tokens.py` exists) | OK |
| `tests/test_design_tokens.py` | regression guard, READ | yes | OK |
| `design-bundle/project/shell.jsx` | design reference, READ | yes | OK |
| `public/index.html` | mentioned in §7 risk 5 | yes | OK |
| `src/components/ResumeGenerator.svelte:125` | unmodified, asserted in §7 risk 1 | yes; line 125 contains `window.dispatchEvent(new CustomEvent('switchTab', { detail: 'profile' }));` | OK |

No hallucinated paths.

## 3. Line-number verification

| Plan reference | Actual content | Status |
|---|---|---|
| `shell.jsx` lines 8–16 (MyCVLogo) | lines 8–16 = `function MyCVLogo({ size = 22 }) { ... }` | match |
| `shell.jsx` lines 102–108 (slot order dashboard...interview) | lines 102–107 = exactly those 6 entries (`]` on 108) | match |
| `shell.jsx` lines 109–155 (markup structure) | lines 109–155 = the JSX `return (...)` of `Topbar` | match |
| `shell.jsx` lines 110–115 (topbar styles) | lines 110–115 = `height: 64`, `padding: '0 32px'`, `borderBottom`, `background: 'var(--paper)'`, `display: 'flex'`, `gap: 36` | match |
| `shell.jsx` lines 122–129 (active state) | lines 122–129 = the active slot `<div>` styles inc. `borderBottom: '1px solid var(--ink)'`, `marginBottom: -1` | match |
| `shell.jsx` lines 135–146 (search pill) | lines 135–146 = search pill JSX with `padding: '6px 10px'`, `var(--paper-2)`, `var(--rule)`, `var(--r-sm)`, `minWidth: 200`, `⌘K` span | match |
| `shell.jsx` lines 147–152 (user-initials circle) | lines 147–152 = `30×30`, `borderRadius: '50%'`, `var(--ink)`, `var(--paper)`, italic Instrument Serif `LM` | match |
| `App.svelte` lines 21–32 (Before block) | lines 21 (`<div class="container">`) to 32 (`</div>`) | match |
| `App.svelte` lines 12–18 (`$effect` listening for `switchTab`) | lines 12–18 = the `$effect` with `addEventListener('switchTab', …)` | match |
| `global.css` line 152 (`body { padding: var(--spacing-section); }`) | line 152 = `padding: var(--spacing-section);` inside `body {…}` | match |
| `global.css` line 180–185 (legacy `.header` class) | line 180 = `.header {`, line 185 = `}` closing brace | match |
| `global.css` line 113 (`.num` tabular-num) | line 113 = `.num {` opening the rule | match |
| `ResumeGenerator.svelte:125` (`switchTab` dispatch) | line 125 = `window.dispatchEvent(new CustomEvent('switchTab', { detail: 'profile' }));` | match |

All line numbers verified.

## 4. Library-pattern verification (Svelte 5 runes)

| Pattern | Documented / proven in | Status |
|---|---|---|
| `$state` | used in `ImportModal.svelte:6+`, `Education.svelte:5+`, plus many others | real |
| `$props` | `ImportModal.svelte:4`, `LanguageSelector.svelte:2`, `JobAnalysis.svelte:2`, etc. | real |
| `$effect` | `ImportModal.svelte:214`, `Education.svelte:26`, plus `App.svelte:12` | real |
| `$derived` | `JobInput.svelte:14`, `SavedJobItem.svelte:16`, `PdfPreview.svelte:43+` | real |
| `{#snippet}` | `ResumeView.svelte:485+`, `PdfPreview.svelte:70+` | real (mentioned as optional in §3.1) |

No hallucinated APIs. No new dependencies. CHECKLIST §1/§2 correctly marked `n/a`.

## 5. Checklist coverage

| IMPL_PLAN section | Checklist items covering it | Status |
|---|---|---|
| §3.1 CREATE `Topbar.svelte` | CHECKLIST §3.1 (17 items: file exists, header, props, slots array, $derived, click handler, aria-disabled, markup, button, nav aria-label, MyCVLogo, height, active CSS, disabled CSS, search pill CSS, user-circle CSS, no-hex) | covered |
| §3.2 MODIFY `App.svelte` | CHECKLIST §3.2 (6 items: import swap, handler rename, Topbar outside container, old header gone, if-blocks unchanged, $effect unchanged) | covered |
| §3.3 MODIFY `global.css` | CHECKLIST §3.3 (3 items: body padding 0, .container gains padding, legacy .header kept) | covered |
| §3.4 DELETE `TabNav.svelte` | CHECKLIST §3.4 (2 items: file gone, grep returns nothing) | covered |
| §5 a11y bullets | CHECKLIST §5 (5 items: `<header>` element, `<nav aria-label="Primary">`, Tab focus order, Enter/Space activate, search/circle decorative) | covered |
| §7 risk 1 (switchTab survives) | CHECKLIST §3.2 line 65 + §4 indirect via test_click_tailor_routes | covered |
| §7 risk 3 (design-tokens regression) | CHECKLIST §4 line 90 | covered |
| §8 test plan (5 tests + regression) | CHECKLIST §4 (8 items) | covered |
| Lean-code header on new test file | CHECKLIST §4 last item (line 91) | covered |

No orphan checks. No uncovered plan sections.

## 6. Risks, ambiguities, and lean-code findings

### MAJOR

- **M1 — `handleSwitchTab` rename gap (App.svelte:13).** §3.2 change 2 renames `handleTabChange → updateActiveTab`. §3.2 change 5 says "the `$effect` that listens for the `switchTab` window event stays". But that `$effect` contains an inner function literally named `handleSwitchTab` (App.svelte:13), and CLAUDE.md explicitly forbids the `handle*` verb. After the slice, the file still violates lean-code. CHECKLIST has no item flagging this. Either (a) the plan should explicitly rename the inner function (e.g., `updateActiveTabFromEvent`) or (b) acknowledge it as a deliberate carry-over compromise. Currently it does neither — a future lean-code sweep will catch this and reopen the file. Location: IMPL_PLAN §3.2 change 5 + CHECKLIST §3.2 line 65–66.

- **M2 — Active-treatment test assertion is fragile against OKLCH (`test_active_slot_treatment`).** §8 test 3 asserts the Profile slot has "computed `color: rgb(...)` matching `--ink`". Browsers serialize `oklch(0.16 0.04 265)` to a specific (and not always stable across Chromium versions) `rgb(…)` triplet. The existing `test_design_tokens.py:72–73` already hard-codes `rgb(244, 241, 236)` / `rgb(26, 24, 20)` against OKLCH tokens — that hard-coded pair was authored when the tokens were paper/ink browns, not the current cobalt OKLCH. After the slice-1 reskin (`91a798e feat(styles): reskin design tokens from editorial to electric cobalt`) those RGB triplets likely no longer match the cobalt-era tokens; the regression guard in CHECKLIST line 90 ("test_design_tokens.py still passes") may already be red before the slice starts. Plan §7 risk 3 acknowledges OKLCH brittleness in the abstract but does not pin down the actual assertion strategy for slice-2's new test, nor verify the slice-1 test still passes today. Location: IMPL_PLAN §8 test 3 + §7 risk 3.

### MINOR

- **m1 — "preloaded" overstates `public/index.html` (§7 risk 5).** Risk 5 says "`Instrument Serif` is already preloaded via `public/index.html`". `public/index.html` uses `preconnect` to `fonts.googleapis.com` and a regular `<link rel="stylesheet">` for the Google Fonts CSS; there is no `<link rel="preload">`. The font does load and is available, so the conclusion ("no new font subset needed") is correct — just mis-stated. Cosmetic.

- **m2 — "free to remove later if the design-tokens test still passes" (§3.3).** Unbounded `if` clause with no exit criterion or owner. The handover compromise §6 row 4 records the carry-over more cleanly; the §3.3 sentence is redundant and adds ambiguity. Cosmetic.

- **m3 — `test_disabled_slots_inert` exit assertion ("clicking one does not change the visible page") is observable but weak.** With `pointer-events: none`, the click event never fires; the test could just assert that the element matches `:where([pointer-events="none"])` or is `aria-disabled="true"`. The "page does not change" assertion is a positive consequence but won't distinguish between "click was swallowed" vs "click was processed but the slot mapped to null". Plan §3.1 click-handler section combines `pointer-events: none` with an `&& onTabChange(slot.tab)` short-circuit — the redundancy is good defense, but the test should assert the property that matters (the slot is not focusable + not clickable), not the page-level side effect.

- **m4 — No `class:active` predicate in CHECKLIST.** The `$derived` `activeSlotId` is checked (CHECKLIST §3.1 line 44) but no checklist item asserts that `class:active={slot.id === activeSlotId}` is the actual binding in markup. IMPL_PLAN §3.1 markup snippet shows `class:active class:disabled` without naming the predicate. A faulty wiring (e.g., `class:active={slot.tab === activeTab}`) would still pass the existing checks but would mis-fire for slots where `tab === null && activeTab === null` (impossible here but defensive). Borderline pedantic given S ceremony — flagging for completeness.

### Lean-code compliance of planned new code

| Rule | Status in plan |
|---|---|
| Two-line file header (`// Lean Code …` + `// Scope: …`) on `Topbar.svelte` | CHECKLIST §3.1 line 41 — covered |
| Two-line file header on `tests/test_topbar_shell.py` | CHECKLIST §4 line 91 — covered |
| No `handle*` verb in new component code | Plan §3.2 change 2 renames `handleTabChange → updateActiveTab`; click handler is inline arrow (no named function); CHECKLIST §3.1 line 45 + §3.2 line 61 enforce — covered |
| No abbreviations | `activeSlotId`, `updateActiveTab`, `slots` — all spelled out. OK |
| Permitted verbs only | `update` (App.svelte handler), test verbs (`test_*` Python convention, fine — `check_*` would be the lean form, but Python test discovery requires `test_*` prefix; this is a project-wide carve-out, see existing `tests/test_design_tokens.py`). OK |
| No comments beyond header | §3.1 makes no commitment about absence of inline comments; CHECKLIST §3.1 line 41 says "no inline comments anywhere in the file" — covered |
| Click-handler inline arrow vs named function | §3.1 uses inline arrow — CLAUDE.md "scope-defines-size" satisfied. OK |
| `MyCVLogo` lives in the same file (avoid extracted-fragment) | §3.1 explicitly inline. OK |

But: M1 above — the surviving `handleSwitchTab` inside the kept `$effect` is a lean-code violation that the plan inherits without acknowledgement.

## 7. Scope-drift check

| Plan adds | Refined asked for? | Verdict |
|---|---|---|
| Q0.2 decision: four no-screen slots render disabled + non-clickable | Refined says "decided during /v6-feature analyze"; the plan records the decision | in-scope |
| Q0.3 decision: drop the separate `Sigil` mark, use only `MyCVLogo` | Refined says "small sigil mark on the left, 'MyCV' wordmark in Instrument Serif" — i.e. it asked for BOTH a sigil AND the wordmark | minor drift — plan drops half of the requested left-side layout. The refined doc reads as "sigil + wordmark"; the plan reduces to "wordmark only". This is a design decision (Q0.3) but it is a SCOPE REDUCTION versus the refined doc, not a faithful port. Worth confirming with the user before /v6-build. (Flagged but not raised to MAJOR because the refined doc has `confidence: some-unknowns` and slice 1 didn't ship a sigil to consume.) |
| Rename `handleTabChange → updateActiveTab` | Lean-code reflex, not in refined | in-scope (style enforcement) |
| Body padding flip body→.container | Required to make the topbar span full width — implicit in "renders above every page body" | in-scope |
| Keep legacy `.header` CSS class | Not asked for either way | in-scope (deferred work) |
| Search pill is decorative (no `⌘K` palette) | Refined did not ask for working ⌘K | in-scope (§6 compromise 2 records) |
| User-initials hardcoded `LM` | Refined says "user-initials circle" — content unspecified; mock value is fine | in-scope (§6 compromise 1 records) |

Net: one minor scope-drift on the sigil (plan reduces visual scope vs refined doc). Not a blocker for S ceremony but should be acknowledged before build.

## 8. Risk and ambiguity sweep — vague terms

Grepped for "appropriate", "robust", "as needed", "etc.", "and so on", "iterate until", "keep adjusting" across the plan and checklist.

- No instances of "appropriate / robust / as needed / iterate until / keep adjusting" found.
- "etc." not found.
- "if any default-font-size cascade interacts" (§7 risk 3) — speculative phrasing but bounded by the test-suite re-run requirement. Acceptable.
- "free to remove later if the design-tokens test still passes" (§3.3) — see m2.
- "(or absorb its tab-switch contract into the new `Topbar` nav)" (refined Scope IN, not plan) — refined-level ambiguity, resolved by the plan's choice to delete.

Database schema, race conditions, error handling, migration strategy — N/A for this slice (UI shell, no persistence, no concurrent state).

## 9. What I almost flagged but didn't

These are spots that *looked* sketchy on first pass but verification cleared them — recording so the next reviewer can spot-check:

1. **The `tests/test_design_tokens.py:72-73` assertion `rgb(244, 241, 236)` looks misaligned with the cobalt OKLCH tokens (`oklch(0.97 0.01 260)`).** I considered raising this as a BLOCKER because CHECKLIST line 90 promises the test "still passes". But: I cannot run the test (constraint). The mismatch may reflect a) chromium's OKLCH-to-sRGB conversion producing exactly those values for the current tokens, or b) the test being broken before this slice started, in which case it's slice-1 debt, not slice-2's. Recorded as M2 instead of BLOCKER because the diagnosis is "test may already be red", which is the parent's call to resolve.

2. **The plan's "no other consumer exists — verified by `grep -rn TabNav src/`" claim (§3.4).** I verified independently: `grep -rn TabNav src/` returns only `src/App.svelte:2` (import) and `src/App.svelte:24` (usage). The plan's grep is honest. Did not flag.

3. **The `<button>` vs `<div>` swap (§3.1) vs shell.jsx using `<div cursor:pointer>`.** I almost flagged this as a divergence from "pixel intent of shell.jsx" (refined success criterion). But the plan explicitly justifies the swap: "Svelte/native semantics need a real button so the BDD scenario 'clicks Tailor CV' maps to a clickable element with keyboard support." That is a correct accessibility upgrade, not a regression. The visual outcome (text styled like a label, with a bottom-border on active) is preserved via scoped CSS. Did not flag.

## 10. Final verdict

**Status: ISSUES.** Two MAJOR findings (M1: lean-code violation surviving in App.svelte:13; M2: `test_active_slot_treatment` fragility against OKLCH + possible pre-existing red regression guard) and a scope-reduction note on the missing Sigil mark vs refined doc. The plan is otherwise tight, well-traced, line-numbers verified, no hallucinated paths, lean-code compliant for new code. After the parent addresses M1 (decide: rename or accept-with-note), M2 (decide assertion strategy + verify slice-1 test currently passes), and the Sigil scope reduction (confirm Q0.3 decision is the user's intent), /v6-build can proceed.

---

```
status: ISSUES
artifact: /Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/workbench-v6/2-plan/PLAN_VERIFIED_2026-05-11_topbar-shell.md
traceability: covered=9/9 must-have-bullets, missing=0, deferred=0
hallucinated_files: 0
hallucinated_symbols: 0
checklist_orphans: 0
risk_findings: blockers=0, major=2, minor=4
top_issue: handleSwitchTab survives the rename in App.svelte:13 — lean-code violation the plan does not address
```
