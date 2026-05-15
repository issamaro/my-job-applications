feature: restyle-profile-editor
date: 2026-05-13
status: VERIFIED
reviewer: plan-reviewer
inputs_reviewed:
  - workbench/1-analyze/spec/FEATURE_SPEC_2026-05-13_restyle-profile-editor.md
  - workbench/1-analyze/ux/UX_DESIGN_2026-05-13_restyle-profile-editor.md
  - workbench/2-plan/design/IMPL_PLAN_2026-05-13_restyle-profile-editor.md
  - workbench/2-plan/checks/CHECKLIST_2026-05-13_restyle-profile-editor.md
  - workbench/2-plan/research/SVELTE5_NOTES_2026-05-13_restyle-profile-editor.md
  - workbench/2-plan/research/SVELTE5_BINDABLE_NOTES_2026-05-13_restyle-profile-editor.md
  - workbench/2-plan/PLAN_VERIFIED_2026-05-13_restyle-profile-editor.md (prior review, now overwritten)

---

## 0. Re-review scope — targeted MN fixes

The previous review (status: ISSUES, 6 MINOR findings) recorded MN-A through MN-F. The user chose "Edit plan" for the three load-bearing MNs: MN-B (cropperjs CHECKLIST claim), MN-C (showAddForm vs showForm naming), and MN-E (visual-style assertions in test_user_initials_circle). MN-A, MN-D, and MN-F were intentionally left untouched.

This re-review re-reads every artifact from scratch (not relying on prior-pass observations), confirms the three targeted fixes, and re-runs all five verification passes.

---

## 0a. Targeted-fix verification

### MN-B (cropperjs CHECKLIST line ~24) — FIXED

CHECKLIST.md line 24 now reads (verbatim):

> `cropperjs ^2.0.0` present in `package.json` dependencies (pre-existing entry in `package.json:11`; **currently unused by any code path** — `grep -rn cropperjs src/ public/ rollup.config.js` returns zero matches, PhotoUpload uses native `FileReader` not cropperjs). This checklist item is a sanity-check that the entry wasn't accidentally removed; do NOT use this as evidence that cropperjs is wired in. Verify: `npm list cropperjs` → source: `package.json:11` — pre-existing dependency, unused

Independent verification:
- `grep -rn cropperjs src/ public/ rollup.config.js` returns zero matches (confirmed via Bash).
- `grep -n FileReader src/components/PhotoUpload.svelte` → `80: const reader = new FileReader();`
- `head -20 src/components/PhotoUpload.svelte` imports only `uploadPhoto`, `deletePhoto`, `ConfirmDialog`, `Toast` — no cropperjs import.
- `grep -n cropperjs package.json` → `11: "cropperjs": "^2.0.0"` — entry exists at the claimed line.

The MN-B factual claim is now accurate. The false "used by an upstream PhotoUpload code path" wording is replaced with "currently unused by any code path" plus explicit grep evidence and the FileReader citation. Status: RESOLVED.

### MN-C (IMPL_PLAN line ~541, CHECKLIST line ~122) — FIXED

IMPL_PLAN line 541 now reads:
> **Inline `{#if showForm && !editingId}` block** (~lines 309-428) — the "Add new" form rendered when the user clicks the add-experience action.

CHECKLIST line 122 also uses `{#if showForm && !editingId}`.

Independent verification:
- WorkExperience.svelte:10 → `let showForm = $state(false);` — variable name is `showForm`.
- WorkExperience.svelte:309 → `{#if showForm && !editingId}` — exact match for the IMPL_PLAN's condition string.
- No `showAddForm` references remain in IMPL_PLAN.md (grep returns zero).

The IMPL_PLAN and CHECKLIST now exactly match the source code's actual variable name and condition. Status: RESOLVED.

### MN-E (IMPL_PLAN ~lines 1029-1078, CHECKLIST line ~167) — FIXED

IMPL_PLAN lines 1029-1068 show the replacement `test_user_initials_circle`. Verified line-by-line:
- `wait_for_function` gate present at lines 1037-1039 (asserts textContent === 'IM' before evaluating style).
- All 8 visual-style assertions preserved at lines 1061-1068:
  - `assert user["text"] == "IM"` (line 1061 — text expectation updated from `LM`)
  - `assert user["width"] == "30px"` (1062)
  - `assert user["height"] == "30px"` (1063)
  - `assert user["borderRadius"] == "50%"` (1064)
  - `assert user["background"] == "oklch(0.16 0.04 265)"` (1065)
  - `assert user["color"] == "oklch(0.97 0.01 260)"` (1066)
  - `assert "Instrument Serif" in user["fontFamily"]` (1067)
  - `assert user["fontStyle"] == "italic"` (1068)

Cross-referenced against the existing `tests/test_topbar_shell.py:358-365` — the eight original assertions are identical in shape; only the text expectation changes (`LM` → `IM`).

CHECKLIST.md line 167 now contains an explicit checkbox:
> `test_user_initials_circle` **preserves** the original visual-style assertions (MN-E fix): `width == "30px"`, `height == "30px"`, `borderRadius == "50%"`, `background == "oklch(0.16 0.04 265)"`, `color == "oklch(0.97 0.01 260)"`, `"Instrument Serif" in fontFamily`, `fontStyle == "italic"` — the rewrite changes only the text expectation, not the visual contract

The checklist item lists all seven non-text assertions verbatim and is explicit about the MN-E origin. Status: RESOLVED.

---

## 1. Requirement traceability

| Requirement (FEATURE_SPEC) | Covered by (IMPL_PLAN) | Status |
|---|---|---|
| MH 1 — Editorial page frame | File 6 (ProfileEditor template + scoped styles) | covered |
| MH 2 — Seven numbered editorial sections | File 2 (EditorialSection) + File 6 (seven usages) | covered |
| MH 3 — Identity card (5 fields, 96px avatar) | File 4 (UserProfile rewrite) | covered |
| MH 4 — Summary section (textarea + 500ms blur) | File 6 change 4 + File 1 `writeProfile` | covered |
| MH 5 — Experience timeline | File 7 (both blocks restyled per MN2/MN-C fix) | covered |
| MH 6 — Education list | File 8 | covered |
| MH 7 — Skills cluster (pills + dashed add) | File 9 | covered |
| MH 8 — Languages grid + drag | File 10 | covered |
| MH 9 — Projects rows | File 11 | covered |
| MH 10 — Topbar initials wiring + shared store | File 1 + File 3 + File 4 + File 6 | covered |
| MH 11 — Legacy color sweep | Files 4, 6-11 + test_no_legacy_color_tokens | covered |
| MH 12 — Behaviour preservation | Files 4, 7-11 ("preserved verbatim" notes) | covered |
| MH 13 — UserProfile loading + error render contract | File 4 change 3 | covered |
| BDD 1 (page frame) | File 6 + test `test_editorial_page_frame` | covered |
| BDD 2 (email validation preserved) | File 4 + manual inspection (implicit) | covered |
| BDD 2b (Identity 5-field grid) | File 4 + test `test_identity_grid_shape` | covered |
| BDD 3/3b (skills cluster + zero state) | File 9 + test `test_skills_zero_state` | covered |
| BDD 4 (Languages drag preserved) | File 10 + MI-4 manual bullet | covered (manual) |
| BDD 5 (Experience timeline shape) | File 7 + MI-5 manual bullet | covered (manual) |
| BDD 6 (Topbar initials wired on Name change) | File 1 + File 3 reactivity + MI-6 manual bullet | covered (manual) |
| BDD 7 (Topbar empty → `??`) | File 1 `parseInitials("")` + test | covered |
| BDD 7b (initials edge cases) | File 1 + test `test_initials_helper_edge_cases` | covered |
| BDD 8 (legacy tokens absent) | test `test_no_legacy_color_tokens_in_components` | covered |
| BDD 9 (existing tests pass) | tests/test_topbar_shell.py modification (MN-E fix) + meta | covered |
| BDD 10/11/12 (round-trips) | MI-10/11/12 manual bullets in IMPL_PLAN | covered (manual) |

All 13 Must-haves covered; all BDD scenarios mapped.

---

## 2. File-path verification

| Reference | Type | Exists | Status |
|---|---|---|---|
| `src/lib/profileStore.svelte.js` | create | parent `src/lib/` exists | OK |
| `src/components/EditorialSection.svelte` | create | parent `src/components/` exists | OK |
| `src/components/Topbar.svelte` (lines 4-17 script, 51 user circle) | modify | yes | OK |
| `src/components/UserProfile.svelte` (1-77 / 79-170 / 172-189) | modify | yes | OK |
| `src/components/PhotoUpload.svelte` ($bindable verification only) | read-verify | yes; line 6 confirms `photo = $bindable(null)` | OK |
| `src/components/ProfileEditor.svelte` ("currently 78 lines") | modify | yes (78 lines) | OK |
| `src/components/WorkExperience.svelte` (lines 150-432, both blocks: `{#each}` ~165-307 and `{#if showForm && !editingId}` ~309-428) | modify | yes (432 lines); line 10 declares `let showForm = $state(false);`, line 309 = `{#if showForm && !editingId}` | OK — MN-C fix verified |
| `src/components/Education.svelte` (lines 142-247, #e0e0e0 line 251) | modify | yes (337 lines) | OK |
| `src/components/Skills.svelte` (template 77-129, style 131-167) | modify | yes (167 lines) | OK |
| `src/components/Languages.svelte` (rendered 175-258, #e0e0e0 line 261, style 315-341) | modify | yes (341 lines) | OK |
| `src/components/Projects.svelte` (rendered 138-217, #e0e0e0 line 220) | modify | yes (275 lines) | OK |
| `src/App.svelte` (lines 25-32) | modify | yes | OK |
| `src/styles/global.css` (add `.container-wide`) | modify | yes | OK |
| `src/components/Section.svelte` | delete | yes; single consumer `ProfileEditor.svelte:2` | OK |
| `tests/test_topbar_shell.py:334` (`test_user_initials_circle`) | modify | yes; existing visual-style assertions confirmed at 359-365 | OK |
| `tests/test_profile_editor_restyle.py` | create | parent `tests/` exists | OK |
| `src/lib/api.js` (`getUser`, `updateUser`) | read-verify | both exported | OK |
| `src/components/WorkExperience.svelte:142` (`formatDate()`) | read-verify | line 142 defines `function formatDate(date)` | OK |
| `tests/test_design_tokens.py` (regression check) | read-verify | yes; body-only computed style reads | OK |

**Zero hallucinated files. Zero hallucinated symbols.** The previously-flagged variable name mismatch (`showAddForm` → `showForm`) is resolved.

---

## 3. Library-pattern verification

| Pattern (cited by IMPL_PLAN) | Documented in research notes | Status |
|---|---|---|
| Module-scoped `export const store = $state({...})` | SVELTE5_NOTES Pattern 1 (canonical) | OK |
| Cross-component reactivity from store | SVELTE5_NOTES Pattern 2 | OK |
| `$effect(() => { void readProfile(); })` mount | SVELTE5_NOTES Pattern 3 | OK |
| In-flight promise coalescing via module-level `let _pending` | SVELTE5_NOTES Pattern 4 | OK |
| Deep mutation via Proxy | SVELTE5_NOTES Pattern 5 | OK |
| `{@render children()}` for section body | SVELTE5_NOTES Pattern 6 | OK |
| Playwright DOM-only assertions | SVELTE5_NOTES Pattern 7 | OK |
| `bind:value={store.profile.full_name}` | SVELTE5_NOTES Pattern 8 | OK |
| Child `$bindable()` count prop + parent `bind:count` + effect writeback | SVELTE5_NOTES Pattern 9 + SVELTE5_BINDABLE_NOTES Q1, Q3, Q5 | OK |
| Hazard: `effect_update_depth_exceeded` | SVELTE5_BINDABLE_NOTES Q2 + Q5 | OK |
| Hazard: `ownership_invalid_mutation` | SVELTE5_BINDABLE_NOTES Q1 pitfall + Q2 | OK |
| `bind:photo={store.profile.photo}` (PhotoUpload) | PhotoUpload.svelte:6 already declares `photo = $bindable(null)` | OK |

All cited patterns documented. M1/M2 research gap remains closed.

---

## 4. Checklist coverage

| IMPL_PLAN file | CHECKLIST items | Status |
|---|---|---|
| File 1 profileStore.svelte.js | Section 2 (Patterns 1, 3, 4, 5), Section 4 line 169 (no localStorage), Section 6 | covered |
| File 2 EditorialSection.svelte | Section 2 (Pattern 6), Section 5, Section 6 | covered |
| File 3 Topbar.svelte | Section 2 (Patterns 2, 3, 8) | covered |
| File 4 UserProfile.svelte | Section 3 (Identity), Section 5, Section 6 | covered |
| File 5 PhotoUpload.svelte (read-verify) | Section 2 line 77 | covered |
| File 6 ProfileEditor.svelte | Section 3, Section 5, Section 6 (Toast, container) | covered |
| File 7 WorkExperience.svelte | Section 3 (Experience) + line 122 (both-blocks-restyled, showForm condition matches source) | covered |
| File 8 Education.svelte | Section 3 (Education) | covered |
| File 9 Skills.svelte | Section 3 (Skills), Section 6 (designer sign-off) | covered |
| File 10 Languages.svelte | Section 3 (Languages) | covered |
| File 11 Projects.svelte | Section 3 (Projects) | covered |
| File 12 App.svelte | Section 6 lines 261-265 | covered |
| File 13 global.css | Section 6 line 263 | covered |
| File X Section.svelte deletion | Section 6 line 258 | covered |
| `tests/test_topbar_shell.py` modify | Section 4 lines 165-169 (with explicit MN-E visual-style checkbox at 167) | covered |
| `tests/test_profile_editor_restyle.py` add | Section 4 lines 173-185 | covered |
| Pattern 9 bindable + effect writeback | Section 2 lines 79-88 | covered |

Zero orphan checklist items found.

---

## 5. Risks and ambiguities

### BLOCKER findings

None.

### MAJOR findings

None.

### MINOR findings (untouched by this round per user direction)

**MN-A. Inspector checklist items live only in IMPL_PLAN, not promoted to CHECKLIST.md checkboxes.**
- Location: IMPL_PLAN lines 1219-1245 (MI-4 through MI-12).
- Impact: Phase 3 inspector agent reads IMPL_PLAN, not CHECKLIST, to know what to ask. Anchored in two places when one would suffice.
- Severity: MINOR.

**MN-D. `conftest.py` autouse fixture mutates `database.DATABASE` for Playwright tests.**
- Location: tests/conftest.py:8-19.
- Impact: Pre-existing tax; not slice-3 regression.
- Severity: MINOR.

**MN-F. Pattern 9 hazard guards are grep-based, not runtime-asserted.**
- Location: CHECKLIST lines 81-88.
- Impact: A future refactor that introduces a `count` read inside the effect would trigger `effect_update_depth_exceeded` at runtime; the CHECKLIST item catches it only via human/grep review.
- Severity: MINOR (acceptable for a checklist).

---

## 6. Scope drift check

- No schema changes proposed (no `title` field; matches Non-goals).
- No new profile attributes.
- `Section.svelte` deletion is legitimate per spec.
- `.container-wide` rule added to `global.css` is in-scope.
- localStorage test hook removed from production code; test now uses `page.route` interception.
- No new dependencies. cropperjs is pre-existing and confirmed unused.

---

## 7. What I almost flagged but didn't

These are the three weakest spots I scrutinized but did not promote to findings.

1. **`store.profile.summary` data path is split between File 4 (Identity rows) and File 6 (Summary textarea), both mutating the same `store.profile`.** IMPL_PLAN MH 13 spells out the load-state contract (Summary shows empty textarea until loaded), so the race is documented. But if the build agent introduces a `$derived` over `store.profile.summary`, it could trip on a `null`-before-load case that the contract assumes is `''`. I checked: File 1 line 56 initializes `summary: ''` (empty string, not null), so `$derived(store.profile.summary)` would yield `''` pre-load — safe. No bug, but a brittle invariant.

2. **The `import { store, writeProfile } from '../lib/profileStore.svelte.js';` named-import pattern.** File 1 exports `store`, `readInitials`, `parseInitials`, `readProfile`, `writeProfile` as siblings, not as methods on `store`. A build agent could mis-call `store.readProfile()` (which doesn't exist). I verified IMPL_PLAN consistently uses bare function calls (line 202 `import { store, readInitials, readProfile }`, line 208 `void readProfile();`, line 462 `void writeProfile();`). The CHECKLIST doesn't explicitly assert "imports are named, not method-call style", but the IMPL_PLAN examples are correct. A misread is possible but not encouraged by the plan.

3. **First-paint count flash for sections 03–07.** Pattern 9's `count = items.length` write happens inside `$effect`, which runs after the child mounts. On first paint, `count={0}` is passed via `bind:count`, then the child's effect fires and writes the real count, then the parent re-renders EditorialSection. SVELTE5_BINDABLE_NOTES Q5 confirms no loop. But the EditorialSection header momentarily shows `№ 03 Experience 0` before settling. Not a correctness bug — the eventual render is correct — but a designer doing visual QA might notice the flicker. The FEATURE_SPEC's Scenario 1 doesn't pin first-paint behaviour, so this is not a regression-from-spec.

---

## 8. Final verdict

**Status: VERIFIED** — 0 BLOCKER, 0 MAJOR. The three MN findings the user opted to fix (MN-B, MN-C, MN-E) are all resolved; independent verification confirms:
- MN-B: cropperjs CHECKLIST line now factually accurate (grep evidence + FileReader citation present).
- MN-C: IMPL_PLAN line 541 and CHECKLIST line 122 both use `{#if showForm && !editingId}`, matching `WorkExperience.svelte:309` exactly.
- MN-E: IMPL_PLAN lines 1029-1068 preserve all 8 visual-style assertions + add `wait_for_function` gate; CHECKLIST line 167 anchors the requirement with an explicit checkbox.

The three remaining untouched MINORs (MN-A, MN-D, MN-F) are all sub-blocker process annoyances:
- MN-A: inspector bullets exist in IMPL_PLAN but not promoted to CHECKLIST checkboxes.
- MN-D: pre-existing `conftest.py` autouse tax (not slice-3 regression).
- MN-F: Pattern 9 hazards verified via grep, not runtime-asserted.

None of these block a successful build. Per v6 verdict rules: a plan with no BLOCKER and no MAJOR is `VERIFIED`. The parent agent may proceed to `/v5-build` with confidence in the three load-bearing fixes.

If proceeding to build, the most load-bearing watch points are:
1. Build agent uses named imports (`import { store, readProfile, writeProfile, parseInitials, readInitials }`) — not method-call syntax on `store`.
2. The `count = items.length` write-only shape inside each child's `$effect` is preserved verbatim (no clever conditionals that would also read `count`).
3. The 8 visual-style assertions in `test_user_initials_circle` are pasted verbatim from the IMPL_PLAN code block — do not abridge.
