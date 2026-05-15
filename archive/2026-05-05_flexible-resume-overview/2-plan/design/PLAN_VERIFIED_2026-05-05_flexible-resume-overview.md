feature: flexible-resume-overview
date: 2026-05-05
status: ISSUES
reviewer: plan-reviewer
inputs_reviewed:
  - workbench/1-analyze/spec/FEATURE_SPEC_2026-05-05_flexible-resume-overview.md
  - workbench/1-analyze/ux/UX_DESIGN_2026-05-05_flexible-resume-overview.md
  - workbench/2-plan/design/IMPL_PLAN_2026-05-05_flexible-resume-overview.md
  - workbench/2-plan/checklist/CHECKLIST_2026-05-05_flexible-resume-overview.md
  - src/components/ResumeView.svelte
  - src/components/ResumeSection.svelte
  - src/components/PdfPreview.svelte
  - src/components/SavedJobItem.svelte
  - src/components/ProfileEditor.svelte
  - src/components/Toast.svelte
  - tests/test_resumes.py
  - tests/conftest.py
  - routes/resumes.py
  - services/resume_generator.py
  - schemas.py
  - package.json

---

## 1. Traceability table — Must-Have requirements

| Requirement | Covered by | Status |
|---|---|---|
| MH-1 — Summary inline-edit | IMPL_PLAN F1.1 (state vars), F1.2 (`startEditSummary`/`cancelEditSummary`/`writeSummaryEdit`), F1.4 (markup), F1.6 (CSS) | covered |
| MH-2 — Skills per-item exclude / include | IMPL_PLAN F1.1 (`savingSkillIndex`), F1.2 (`updateSkillInclusion`), F1.5 (markup with active + available groups) | covered |
| MH-3 — Skills per-item rename | IMPL_PLAN F1.1 (`editingSkillIndex`, `skillDraft`), F1.2 (`startEditSkill`/`cancelEditSkill`/`writeSkillRename`), F1.5 | covered |
| MH-4 — Persistence + PDF preview parity | IMPL_PLAN F1.2 (every save calls `updateResume`), F3 (PdfPreview already filters on `included`) | covered |
| MH-5 — Regeneration is non-destructive | IMPL_PLAN "Out-of-plan items" + spec note that regenerate already creates a new row | covered (no work needed) |
| MH-6 — Section-wide skills toggle deterministic | IMPL_PLAN F1.3 | covered |

All Must-Haves traced.

---

## 2. File-path verification

| Reference | Type | Exists | Status |
|---|---|---|---|
| `src/components/ResumeView.svelte` | modify | yes | OK |
| `src/components/ResumeView.svelte:57-68` (state group) | locator | partial | MINOR — state group is actually 57-61; lines 63-68 are unrelated state vars (`editMode`, `selectedTemplate`, `isExporting`, `toastMessage`, `toastType`, `draggedIndex`). Citation is loose but not hallucinated. |
| `src/components/ResumeView.svelte:121` (`cancelEdit`) | locator | yes | OK |
| `src/components/ResumeView.svelte:123` (`toggleSection`) | locator | yes | OK |
| `src/components/ResumeView.svelte:129-133` (skills branch) | locator | yes | OK |
| `src/components/ResumeView.svelte:124-128, 134-148` (other branches) | locator | yes | OK |
| `src/components/ResumeView.svelte:175-180` (reorder error pattern) | locator | partial | MINOR — actual try/catch spans 173-181 (close brace at 181). Plan's `175-180` is the body, off by one but not wrong. |
| `src/components/ResumeView.svelte:178-181` (reorder revert) | locator | yes | OK |
| `src/components/ResumeView.svelte:277-295` (personal-info card) | locator | yes | OK (block actually 278-294 inclusive) |
| `src/components/ResumeView.svelte:291` (`{#if resumeData.summary}`) | locator | yes | OK |
| `src/components/ResumeView.svelte:291-293` (summary block) | locator | yes | OK |
| `src/components/ResumeView.svelte:322-333` (work-experience inline edit) | locator | yes | OK |
| `src/components/ResumeView.svelte:328` (`disabled={saving}`) | locator | yes | OK |
| `src/components/ResumeView.svelte:343-345` (`savedId === exp.id`) | locator | yes | OK |
| `src/components/ResumeView.svelte:354-368` (skills section) | locator | yes | OK |
| `src/components/ResumeView.svelte:432` (Toast) | locator | yes | OK |
| `src/components/ResumeView.svelte:705-719` (`.skill-tag` CSS) | locator | yes | OK |
| `src/components/ResumeView.svelte:608` (`.inline-edit textarea`) | locator | yes | OK |
| `src/components/ResumeSection.svelte` | no-change | yes | OK |
| `src/components/PdfPreview.svelte` | no-change | yes | OK |
| `src/components/PdfPreview.svelte:56-58` (`includedSkills` filter) | locator | yes | OK |
| `src/components/PdfPreview.svelte:137` (`{skill.name}`) | locator | yes | OK |
| `src/components/PdfPreview.svelte:204` (`{skill.name}`) | locator | yes | OK |
| `src/components/PdfPreview.svelte:222, 246, 268` (summarySection render) | locator | yes | OK |
| `tests/test_resumes.py:163` (`test_update_resume`) | modify | yes | OK |
| `routes/resumes.py:59-64` (PUT endpoint) | no-change | yes | OK |
| `services/resume_generator.py:137-167` (`update_resume`) | no-change | yes | OK |
| `schemas.py:240` (`ResumeSkill`) | no-change | yes | OK (`name: str` + `matched: bool` + `included: bool = True`) |
| `package.json:14` (`svelte: ^5.0.0`) | locator | yes | OK |

No hallucinated file paths. No hallucinated symbols. Two minor line-range imprecisions noted.

---

## 3. Library-pattern verification

Single library: Svelte 5 (`^5.0.0`). The plan invokes the orchestrator carve-out for `libraries ≤ 1`. Per-pattern verification below.

| Pattern | Source / docs | Status |
|---|---|---|
| `$state(value)` | Used at `ResumeView.svelte:57,60,61` etc. — established | OK |
| `$state(null)` for refs | Used at `ProfileEditor.svelte:12-18`, `ResumeGenerator.svelte:207`, `ImportModal.svelte:234` etc. | OK |
| `$effect(() => { … })` | Used at `ResumeView.svelte:70-74`, `SavedJobItem.svelte:22-26` | OK |
| `bind:this={ref}` | Used at `ProfileEditor.svelte:34,53,57,61,65,69`, `ImportModal.svelte:234,256,262`, `ConfirmDialog.svelte:30` | OK |
| `bind:value` | Used at `ResumeView.svelte:324`, `SavedJobItem.svelte:122` | OK |
| `class:foo={expr}` | Used at `ResumeView.svelte:239,249,307,362` | OK |
| `onclick={handler}` (Svelte 5 lowercase event attrs) | Used throughout `ResumeView.svelte` and others | OK |
| `{#each arr as item, index}` | Used at `ResumeView.svelte:304,390` | OK |
| `{@render snippet(args)}` | Used at `PdfPreview.svelte:222,246,268` | OK |
| `field-sizing: content` (CSS) | Modern Chromium 123+, Safari TP. Plan provides `@supports not` fallback at fixed 160px. | OK (with documented fallback) |
| `autofocus` attribute on `<input>` | Used at `SavedJobItem.svelte:127` with `<!-- svelte-ignore a11y_autofocus -->` | **NOT used** by plan despite being the established codebase convention — see Risk-1 below |

No deprecated APIs. Critical observation: the plan's R-Plan-3 mitigation reaches for `bind:this` + `$effect` to focus, but the codebase already has a simpler precedent (`SavedJobItem.svelte`) using the native `autofocus` attribute on a conditionally mounted input. Plan deviates from established convention without justification beyond the unsubstantiated assertion that `autofocus` "is unreliable in Svelte 5."

---

## 4. Checklist coverage

| Plan file / change | Checklist items | Status |
|---|---|---|
| F1.1 — five new `$state` vars + 2 ref vars | Section 2 (`$state`, `bind:this`), Section 4 ("F1.1 verified") | covered |
| F1.2 — eight new functions | Section 4 ("F1.2 verified") | covered (lists nine names; matches IMPL_PLAN total of 7 declared + 2 key handlers) |
| F1.3 — `toggleSection('skills')` rewrite | Section 2 (`async`), Section 3 (B.0), Section 4 ("F1.3 verified" x2) | covered |
| F1.4 — summary markup three-branch | Section 3 (A.1–A.6), Section 4 ("F1.4 verified") | covered |
| F1.5 — skills markup active + available + all-excluded | Section 3 (B.1–B.6), Section 4 ("F1.5 verified") | covered |
| F1.6 — new CSS rules | Section 4 ("F1.6 verified" lists every selector) | covered |
| F2 — three new pytest tests | Section 4 (each test named explicitly) | covered |
| F3 — `PdfPreview.svelte` no change | Section 7 ("F3") | covered |
| F4 — `ResumeSection.svelte` no change | Section 7 ("F4") | covered |
| F5 — backend no change | Section 7 ("F5" rows for routes, generator, schemas, database) | covered |

No orphan checks identified. All checklist items trace to a plan file or to an explicit FEATURE_SPEC requirement.

---

## 5. Risks and ambiguities (findings)

### MAJOR-1 — Autofocus pattern deviates from established codebase convention
Location: `IMPL_PLAN:170-172` (R-Plan-3) + checklist Section 2 line about `bind:this` and `$effect` for focus
Severity: **MAJOR**

The plan's R-Plan-3 asserts: "`autofocus` on conditionally rendered inputs is unreliable in Svelte 5." It introduces `summaryTextareaRef` + `skillRenameRef` state vars + `bind:this` + a `$effect` block that calls `.focus()` on transition. But `src/components/SavedJobItem.svelte:118-128` already implements the analogous pattern (input revealed under `{#if editing}` with `autofocus` attribute and `<!-- svelte-ignore a11y_autofocus -->`):

```
{#if editing}
  <!-- svelte-ignore a11y_autofocus -->
  <input … autofocus />
```

The plan provides no evidence that this established pattern fails for the new feature. UX_DESIGN B.8 says "Edit input is autofocused on open" — the codebase precedent is to use the HTML `autofocus` attribute, not a `$effect` shim. Cost: two extra state vars, two `bind:this` directives, one `$effect` block, and a divergence from how other components in this codebase handle the same concern. Either the plan should mirror `SavedJobItem.svelte`, or it should justify why the new feature requires a different approach.

This matches the second of the two specific traps the reviewer was asked to look for: the plan does NOT mirror the established `{#if …}` mount + `autofocus` attribute pattern.

### MAJOR-2 — `mock_llm` is a `@patch` decorator, not a `conftest.py` fixture
Location: `IMPL_PLAN:149` ("Use the existing `mock_llm` and `client` fixtures from `tests/conftest.py`")
Severity: **MAJOR**

Verified `tests/conftest.py` (full file read, 30 lines): only `client` and the autouse `setup_test_db` are defined. `mock_llm` is the result of `@patch("services.resume_generator.llm_service.analyze_and_generate")` decorating the test (see `tests/test_resumes.py:162`). Calling it a "fixture from `conftest.py`" misleads the build phase: a developer reading the plan literally will look in `conftest.py`, not find `mock_llm`, and may invent a new fixture rather than apply the `@patch` decorator. The plan should state: "wrap each new test with `@patch('services.resume_generator.llm_service.analyze_and_generate')` and accept `mock_llm` as the first arg, mirroring `test_update_resume` at line 162."

### MAJOR-3 — Async asymmetry in `toggleSection` is partly understated
Location: `IMPL_PLAN:60-68` (F1.3 final shape)
Severity: **MAJOR**

The plan states `toggleSection` "becomes async" and that "Svelte handlers accept async functions." Trace through the existing wiring:
- `ResumeView.svelte:300,357,373,386,401` — every section wraps the call in an arrow: `onToggle={() => toggleSection('work')}` (and similar).
- `ResumeSection.svelte:2` destructures `onToggle`; line 24 wires `onclick={onToggle}`. So Svelte calls the arrow, which calls `toggleSection(...)`. Both arrow and `onclick` discard the return value.

After the change:
- The function declaration becomes `async function toggleSection(section)`. Promise rejection from the new `await updateResume(...)` is caught by an internal try/catch as the plan states ("with the same revert-on-error shape as `writeSkillRename`"). This is fine.
- BUT the plan's wording is loose: an `async` function returns a Promise on **every** branch, not "only for the skills branch." The other branches now return `Promise<undefined>` — harmless because callers discard, but the framing "becomes async only for the skills branch" is incorrect.
- The bigger concern: the plan needs to confirm explicitly that the new internal try/catch covers ALL exception sources inside the new skills branch (network error AND any sync error in the `.map(...)` step), and that the catch reverts `resumeData` from `resume.resume` exactly as `writeSkillRename` does. The plan delegates to "same shape as `writeSkillRename`" but does not write out the actual code, so the build phase has to infer it. Document the exact try/catch shape in F1.3, including the toast message ("`Could not toggle skills. Reverting.`" or similar — the plan currently doesn't pick a copy string for this case).

This trap was the first one the reviewer was asked about. The async asymmetry **does not break `ResumeSection.svelte`** because callers discard the return — but the plan's exception-handling plan is under-specified, and the toast copy for the section-toggle failure case is missing from UX_DESIGN entirely.

### MINOR-1 — UX_DESIGN B.4 claims a 2000ms toast; actual `Toast.svelte` uses 3000ms
Location: `UX_DESIGN:142` ("a single 2000ms 'Saved' message"); `src/components/Toast.svelte:9` (`setTimeout(..., 3000)`)
Severity: **MINOR**

The shared `Toast` component hardcodes a 3000ms display. The UX_DESIGN B.4 spec text says 2000ms, which doesn't match the code. The IMPL_PLAN reuses the existing `toastMessage` / `toastType` mechanism without changing the timer. Net effect: the toast will display for 3 seconds, contradicting the UX spec. Either accept the existing 3s and update the spec, or change the Toast component (not in current plan scope). Build phase will need to pick.

### MINOR-2 — Comment-policy carve-out is asserted but not documented in CLAUDE.md
Location: `IMPL_PLAN:124,66` ("non-obvious why" + invariant comments); UX_DESIGN B.7 (also asserts the carve-out)
Severity: **MINOR**

CLAUDE.md states: "After the header: ZERO comments. No inline comments. No docstrings. … If code needs a comment, fix the name or structure instead." The plan adds two inline comments anyway:
1. F1.3 — "Document this difference in a one-line invariant comment in the file (qualifies as a 'non-obvious why' comment per CLAUDE.md)."
2. F1.5 — "skills array order is the LLM original order; never reorder, never splice. UX B.7 / spec R7."

CLAUDE.md does NOT explicitly carve out a "non-obvious why" exception. The plan invokes a carve-out that the project's lean-code rules don't grant. This may be the plan author's interpretation of CLAUDE.md's principle "fix the name or structure instead" — but the file structure already constrains the invariant only by convention, not by the type system, so a comment is the only available enforcement. Build phase decision: either add the comments and accept the deviation, or rename functions / structure code to make the invariant self-evident.

### MINOR-3 — Lean-code function-naming rationalization is fragile
Location: `IMPL_PLAN:49,79` (verb-table self-defense for `start*` and `read*` over `handle*`)
Severity: **MINOR**

The plan justifies `startEditSummary` / `cancelEditSummary` etc. as "symmetric with the local convention." But CLAUDE.md's table only permits nine verbs: `read, write, create, delete, update, find, check, parse, render`. `start` and `cancel` are neither. The plan also claims `readSummaryKey` reads "the key and dispatches" — that's a strained reading of `read`, and the local precedent in this same codebase is `handleKeydown` (`SavedJobItem.svelte:56`), which the verb table forbids. The plan accepts the inconsistency for `start*` / `cancel*` and partly forces compliance for the keydown handlers. Result: an inconsistent verb-table compliance level inside one component. Minor; build phase can keep it or normalize.

### MINOR-4 — S10/S11 persistence claim adds an `await` to `toggleSection` for skills only
Location: `IMPL_PLAN:66` (F1.3) + `FEATURE_SPEC` S10/S11
Severity: **MINOR**

The plan acknowledges this as R-Plan-6. The asymmetry is real: clicking the section toggle for `work`/`education`/`languages`/`projects` does NOT persist (the existing convention is local-state-only, persisted on the next per-item save), but for `skills` it WILL persist. A user toggling `work` and `skills` in adjacent clicks gets two different persistence behaviors. The plan accepts this; the spec accepts this. Documented and load-bearing — flagged as MINOR for visibility, not as a blocker.

---

## What I almost flagged but didn't

These are the three weakest spots that survived scrutiny:

1. **Plan F1.5 specifies `aria-label="Rename skill {name}"` on both the rename button (when in display state) AND on the `<input>` (when in editing state).** Two different elements with overlapping accessible names — a screen reader could announce both depending on focus order. I did not flag this because it's documented in UX_DESIGN B.8 + concrete-copy table and the build phase can disambiguate (e.g., change input's label to `"Skill name"`). But it's a small a11y smell.

2. **Plan asserts `editingSkillIndex = $state(null)` then `editingSkillIndex === index` for branch matching.** Strict equality is correct for `null !== 0` (so index 0 won't accidentally match the null state). I verified `=== null` versus `=== 0` would NOT collide because the comparison is to `index` (a non-null number). But this is a class of bug Svelte 5 does NOT protect against, and the plan does not call out the choice. Easy to break on a future refactor that swaps `null` for `-1`.

3. **The plan's `writeSkillRename` revert path is `resumeData = JSON.parse(JSON.stringify(resume.resume))`, but `resume.resume` is the ORIGINAL LLM-generated content from when the resume was first loaded.** If the user has already done another successful edit since load (say, excluded a skill), then renamed a skill and the rename fails, the revert restores the LLM content — losing the previously persistent exclusion locally until next reload. The mirror at `ResumeView.svelte:178-181` has the same property and is tolerated, but the plan inherits it without flagging. I did not flag this because it matches existing behavior, but if a build-phase bug is going to surface here, this is where.

---

## Final verdict

**ISSUES**

Three MAJOR findings (autofocus pattern deviation, `mock_llm` documentation error, under-specified async error handling for the section toggle) plus four MINOR findings. The plan should be tightened on at minimum these points before /v5-build:

- Decide and document: mirror `SavedJobItem.svelte` autofocus pattern, OR justify why a `$effect` shim is required for the summary textarea / skill rename input.
- Fix the test source documentation: `mock_llm` is a `@patch` decorator, not a `conftest.py` fixture.
- Specify the explicit try/catch shape and toast copy for the new async path inside `toggleSection('skills')`.

No hallucinated file paths. No hallucinated symbols. No deprecated library APIs. The plan's structure and traceability are otherwise sound.
