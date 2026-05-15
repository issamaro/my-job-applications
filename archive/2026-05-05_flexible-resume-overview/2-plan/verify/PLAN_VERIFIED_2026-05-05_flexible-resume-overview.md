feature: flexible-resume-overview
date: 2026-05-05
status: VERIFIED
reviewer: plan-reviewer
inputs_reviewed:
- /Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/workbench/1-analyze/spec/FEATURE_SPEC_2026-05-05_flexible-resume-overview.md
- /Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/workbench/1-analyze/ux/UX_DESIGN_2026-05-05_flexible-resume-overview.md
- /Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/workbench/2-plan/design/IMPL_PLAN_2026-05-05_flexible-resume-overview.md
- /Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/workbench/2-plan/checklist/CHECKLIST_2026-05-05_flexible-resume-overview.md
note: rebuilt CHECKLIST re-review after the prior ISSUES verdict. The previous round flagged five MAJOR drifts between IMPL_PLAN and CHECKLIST (stale `$effect`/`bind:this` requirement, seven-vars-not-five, two stale "invariant comment" entries, conftest-vs-decorator misclassification of `mock_llm`). All five drifts are now resolved in the rebuilt CHECKLIST.

---

## 1. Traceability table (Must-have requirements)

| Requirement | Covered by IMPL_PLAN | Covered by CHECKLIST | Status |
|---|---|---|---|
| MH-1 — Summary inline-edit | F1.1 (state), F1.2 (`startEditSummary`/`cancelEditSummary`/`writeSummaryEdit`), F1.4 (markup) | Sec.2 ($state, bind:value, sentinel `__summary__`, 2000ms), Sec.3 Region A six items A.1–A.6, Sec.5 (a11y, readSummaryKey, aria-live) | covered |
| MH-2 — Skills per-item exclude/include | F1.1 (`savingSkillIndex`), F1.2 (`updateSkillInclusion`), F1.5 (active + available groups, stable-array iteration), UX B.7 ordering rule | Sec.2 (`{#each}` over stable array, class:saving-skill), Sec.3 Region B (B.1, B.2, B.6), Sec.5 aria-labels for ✎ × + | covered |
| MH-3 — Skills per-item rename | F1.1 (`editingSkillIndex`/`skillDraft`), F1.2 (`startEditSkill`/`cancelEditSkill`/`writeSkillRename`), F1.5 (rename inline UI) | Sec.2 (bind:value={skillDraft}), Sec.3 Region B (B.3 rename input + ✓ ×), Sec.5 (rename input aria-label, readSkillKey Enter/Esc) | covered |
| MH-4 — Persistence + PDF preview parity | F3 (PdfPreview unchanged — already filters `included !== false`), F1.2 functions all `await updateResume()` | Sec.4 (3 backend round-trip tests), Sec.7 PdfPreview zero-diff gate | covered |
| MH-5 — Regeneration is non-destructive | F5 (regen INSERT path at `services/resume_generator.py:84-102` untouched) | Sec.7 zero-diff gates on `services/resume_generator.py`, `schemas.py`, `database.py` | covered |
| MH-6 — Section toggle deterministic | F1.3 (`anyExcluded` two-state rule + async try/catch + revert + toast) | Sec.2 (`anyExcluded` rule, async, try/catch w/ revert, `previous` snapshot via JSON.parse/stringify) | covered |

All six Must-Have items traced. No Should-Have tier in spec. No deferred. BDD scenarios S1–S12 all reachable through plan + checklist.

---

## 2. File-path verification

| Reference | Type | Verified | Status |
|---|---|---|---|
| `src/components/ResumeView.svelte` | modify | yes | ok |
| `src/components/ResumeView.svelte` state vars `editingId`/`editValue`/`saving`/`savedId` | symbol | yes — actual lines 58-61 (plan said "around 57-68") | ok |
| `src/components/ResumeView.svelte:100-116` `saveEdit` | symbol | yes — `async function saveEdit(expIndex)` at 100, closes 116 | ok |
| `src/components/ResumeView.svelte:108-110` savedId setTimeout 2000ms | symbol | yes — `setTimeout(() => savedId = null, 2000)` at line 110 | ok |
| `src/components/ResumeView.svelte:118-121` `cancelEdit` | symbol | yes — function defined 118-121 | ok |
| `src/components/ResumeView.svelte:123` `toggleSection` | symbol | yes — `function toggleSection(section)` at line 123 | ok |
| `src/components/ResumeView.svelte:129-133` skills branch | landmark | yes — `else if (section === 'skills')` at 129, `skills[0]?.included` at 132 | ok |
| `src/components/ResumeView.svelte:174-181` reorder toast pattern | landmark | yes — `writeReorderedOrder` try/catch with revert + toast at 168-184 | ok |
| `src/components/ResumeView.svelte:277-295` personal-info card | landmark | yes — card spans 277-295 with `{#if resumeData.summary}` at line 291, `<p class="summary">` at 292 | ok |
| `src/components/ResumeView.svelte:354-368` skills section | landmark | yes — `<ResumeSection title={labels.skills}` at 354; `{#each resumeData.skills as skill}` at 361 | ok |
| `src/components/ResumeView.svelte:705-719` `.skill-tag` CSS block | landmark | yes — block confirmed at lines 705-719 | ok |
| `src/components/SavedJobItem.svelte:118-128` autofocus pattern | symbol | yes — `<!-- svelte-ignore a11y_autofocus -->` at line 119, `autofocus` at line 127 | ok |
| `src/components/Toast.svelte:12` 3000ms duration | symbol | yes — line 12 contains `}, 3000);` (the setTimeout duration arg) | ok |
| `src/components/PdfPreview.svelte:56-58` `includedSkills` derived | symbol | yes — `let includedSkills = $derived((resumeData?.skills \|\| []).filter(skill => skill.included !== false));` confirmed at lines 56-58 | ok |
| `src/components/PdfPreview.svelte` | nochange | yes (file exists; zero-diff gate in CHECKLIST Sec.7) | ok |
| `src/components/ResumeSection.svelte` | nochange | yes (file exists; zero-diff gate in CHECKLIST Sec.7) | ok |
| `tests/test_resumes.py:162-163` `@patch` + `mock_llm` parameter | symbol | yes — line 162 `@patch("services.resume_generator.llm_service.analyze_and_generate")`, line 163 `def test_update_resume(mock_llm, client):` | ok |
| `tests/conftest.py:26-29` `client` fixture | symbol | yes — `@pytest.fixture` + `def client():` at lines 25-28 (CHECKLIST cites 26-29; ~1 line drift, body matches) | ok |
| `services/resume_generator.py:84-102` per-generation INSERT | symbol | yes — INSERT block confirmed at lines 89-105 (~3-line drift, semantics correct) | ok |
| `services/resume_generator.py:137-167` `update_resume` round-trip | symbol | yes — function present 137-167 | ok |
| `routes/resumes.py:59-64` PUT endpoint | symbol | yes — `@router.put("/{resume_id}", response_model=GeneratedResumeResponse)` at line 59, `async def update_resume(...)` at 60 | ok |
| `schemas.py:240` `ResumeSkill` | symbol | yes — `class ResumeSkill(BaseModel):` at 240, `name: str` at 241, `included: bool = True` at 243 | ok |
| `database.py` | nochange | yes (file exists; zero-diff gate) | ok |
| `package.json:14` svelte ^5.0.0 | dep ref | yes — line 14 `"svelte": "^5.0.0",` confirmed | ok |
| `pyproject.toml` | dep ref | yes | ok |
| `.python-version` | env ref | yes | ok |
| `services/pdf_subprocess.py` (CHECKLIST Sec.6 line 123, transcribed verbatim from PROJECT_CHECKS.md) | inherited stale ref | NO — file does not exist; actual is `services/pdf_generator.py`. PROJECT_CHECKS.md line 212 itself references the missing file. | inherited (see Risk findings) |

No hallucinated source files. No hallucinated symbols. Line drift on long-lived anchors is ≤3 lines; all semantic anchors verified by name and shape.

---

## 3. Library-pattern verification

Single library: Svelte 5 (`^5.0.0`). Plan invokes the orchestrator's research-skip carve-out for `libraries ≤ 1` plus established same-file precedent. All patterns used are already exercised in `ResumeView.svelte` or `SavedJobItem.svelte`.

| Pattern | Documented in | Status |
|---|---|---|
| `$state(...)` reactive vars | `ResumeView.svelte:58-66` | ok |
| `$effect(...)` for Toast (NOT used in new code) | `Toast.svelte:6` and `ResumeView.svelte:69-73` | ok — plan deliberately avoids `$effect` for autofocus per R-Plan-3 |
| `$derived(...)` | `ResumeView.svelte:53`, `PdfPreview.svelte:53-69` | ok |
| `bind:value` on textarea/input | `ResumeView.svelte:324`, `SavedJobItem.svelte:122` | ok |
| `<!-- svelte-ignore a11y_autofocus -->` + `autofocus` | `SavedJobItem.svelte:119,127` | ok |
| `class:foo={cond}` dynamic class | `ResumeView.svelte:308 class:dragging`, `:361 class:matched` | ok |
| `{#each ... as item, index}` over stable array | `ResumeView.svelte:303,361` | ok |
| `{#if cond}{:else}{/if}` | `ResumeView.svelte:321,341` | ok |
| `onclick={() => fn(args)}` and `onkeydown={fn}` Svelte 5 attribute style | `ResumeView.svelte:328,331,340`, `SavedJobItem.svelte:122` | ok |
| Toast component (3000ms hard-coded duration; no prop) | `Toast.svelte:12` | ok |
| `field-sizing: content` CSS with `@supports not` fallback | NEW; F1.6 declares both | ok — fallback documented and gated in CHECKLIST Sec.2 |

No deprecated APIs. No undocumented patterns.

---

## 4. Checklist coverage

| IMPL_PLAN element | Checklist items | Status |
|---|---|---|
| F1.1 (5 new `$state` vars) | Sec.2 lines 29 ($state used), 30 (exactly five named: `editingSummary`, `summaryDraft`, `editingSkillIndex`, `skillDraft`, `savingSkillIndex` — no more, no fewer), 31 (no `$effect`), 32 (no `bind:this` or ref vars) | covered — drift fixed |
| F1.2 (8 new functions) | Sec.2 lines 34 (bind summary), 35 (bind skill), 44 (sentinel `__summary__`), 45 (savedId 2000ms), 46 (Toast 3000ms); Sec.3 A.6, B.4, B.5; Sec.5 readSummaryKey, readSkillKey, all aria-labels | covered |
| F1.3 (toggleSection skills branch) | Sec.2 line 36 (async), 37 (anyExcluded rule, NOT old `skills[0]?.included`), 38 (try/catch with `Could not save skills. Try again.` toast), 39 (`previous = JSON.parse(JSON.stringify(...))`) | covered — drift fixed |
| F1.4 (summary markup) | Sec.3 Region A all six items A.1–A.6 with state combinations explicit, Sec.5 (Edit button focusable, readSummaryKey keys Cmd/Ctrl+Enter and Esc, aria-live=polite) | covered |
| F1.5 (skills markup) | Sec.2 line 40 (`{#each}` over stable array filtered by `{#if}` — NOT `.filter()` sublist); Sec.3 Region B B.1, B.2, B.3, B.6, B.6 empty-skills, .all-excluded-note copy verbatim; Sec.5 four aria-labels | covered |
| F1.6 (CSS) | Sec.2 lines 42 (.skill-tag.saving-skill), 43 (@supports not field-sizing fallback at 160px); Sec.3 lines 73, 74 (.skill-tag.excluded, .available-skills-header); Sec.5 line 109 :focus outline | covered |
| F1.5 zero-comments rule | Sec.2 line 47 (zero inline comments — only `<!-- svelte-ignore a11y_autofocus -->` compiler directive allowed) | covered — drift fixed (no more "invariant comment present above {#each}" requirement) |
| F2 (3 new pytest tests) | Sec.4 lines 83 (skill_excluded), 84 (skill_renamed), 85 (summary_empty), 86 (`client` fixture from conftest), 87 (`mock_llm` from `@patch` decorator NOT conftest), 88 (existing suite stays green) | covered — drift fixed (mock_llm fixture-vs-decorator distinction now correct) |
| F3 (PdfPreview no change) | Sec.7 zero-diff gate item | covered |
| F4 (ResumeSection no change) | Sec.7 zero-diff gate item | covered |
| F5 (backend no change) | Sec.7 four zero-diff gate items | covered |
| sectionTranslations `availableSkills` | Sec.3 line 75 | covered |
| `bun run build` + bundle size | Sec.4 lines 92, 93, 94 | covered |
| PROJECT_CHECKS Sec.6 transcribed checks | Sec.6 lines 117-124 (8 items) | covered |

No checklist orphans. Every item traces back to IMPL_PLAN, FEATURE_SPEC, UX_DESIGN, or PROJECT_CHECKS.md.

---

## 5. Risks and ambiguities

### BLOCKER findings
None.

### MAJOR findings
None. The five MAJOR drifts from the prior review are all resolved:
1. ~~Stale `$effect`/`bind:this` requirement~~ → CHECKLIST Sec.2 lines 31-33 explicitly forbid both.
2. ~~Seven vars instead of five~~ → CHECKLIST Sec.2 line 30 names exactly five.
3. ~~Stale "invariant comment above {#each}" requirement~~ → CHECKLIST Sec.2 line 47 mandates ZERO inline comments.
4. ~~Stale "invariant comment above skills branch"~~ → same line 47 covers both sites.
5. ~~`mock_llm` misclassified as conftest fixture~~ → CHECKLIST Sec.4 line 87 explicitly states "mock_llm is NOT a conftest fixture, it is the patch decorator's injected object".

### MINOR findings

- **CHECKLIST Sec.6 line 123 — Inherited stale `services/pdf_subprocess.py` reference.** File does not exist; actual is `services/pdf_generator.py` with no subprocess invocation. Item is in the "transcribed verbatim from PROJECT_CHECKS.md" section, so the staleness is inherited from PROJECT_CHECKS.md line 212. This feature does not modify PDF generation, so the gate is not load-bearing. Severity MINOR. Resolution path: a separate PROJECT_CHECKS.md cleanup task, out of scope here.
- **CHECKLIST Sec.6 line 120 — Inherited stale "test count remains ≥101" baseline.** Actual current test count is 231; PROJECT_CHECKS.md says 101. The check still works as a regression gate (231 + 3 ≥ 104), but the baseline figure is misleading. Severity MINOR.
- **IMPL_PLAN F1.1 line 27 wording — "Add five new `$state` vars" lead-in is now correct, but the file-by-file plan title at line 21 still says "Touch points" without indicating the count.** Cosmetic; not a bug. Severity MINOR.
- **IMPL_PLAN F1.4 line 99 reads as in-line deliberation.** The function name flips through three options (`handleSummaryKey` → `parseSummaryKey` → `readSummaryKey`) before settling. The CHECKLIST line 101 confirms `readSummaryKey` as the chosen name, so build phase is unambiguous. Severity MINOR (readability only).
- **Conftest `client` fixture line drift.** CHECKLIST Sec.4 line 86 cites "tests/conftest.py:26-29"; actual lines are 25-28 (the `@pytest.fixture` decorator is at 25, the function body at 26-28). One-line drift. Severity MINOR — anchor is unmistakable by name.
- **S8 (regen non-destructive) has no automated test.** F2 adds three tests but none exercises "edit resume A → regenerate creates B → A still has the edit". The behaviour is structural (separate INSERT row); the existing `test_get_resume_after_generation` covers the happy path. Adding `test_regenerate_does_not_overwrite_edits` would be ~30 lines and cheap. Severity MINOR — not blocking, but the only Must-Have without a direct automated regression catch.
- **`{#each resumeData.skills as skill, index}` loses keyed-update semantics.** Without `(skill.id ?? index)` as a keyed expression, Svelte's reconciler may rebuild DOM nodes on rename or include-toggle. `ResumeSkill` has no `id` field per `schemas.py:240`. Performance-only; correctness fine because filtering happens via `{#if}` not array splicing. Severity MINOR.

---

## What I almost flagged but didn't

1. **CHECKLIST Sec.2 line 44 sentinel string `'__summary__'`.** Almost flagged as fragile — what if work-experience IDs become strings later? Then I reread `saveEdit` at line 108 (`savedId = editingId;`) where `editingId` is set by `startEdit(id, …)` and `id` comes from `exp.id`, which is the SQLite primary key (numeric). String sentinel cannot collide with any numeric id. Plan calls this out. Not a real risk.

2. **`Toast.svelte:12` line citation.** Almost flagged as imprecise — the actual `setTimeout(..., 3000)` spans lines 9-13 with the literal `3000` on line 12. Verified the citation is technically correct (the `3000` literal IS on line 12). Off by zero. Did not flag.

3. **`sectionTranslations` `availableSkills` entry — which language keys?** Almost flagged: UX_DESIGN says "English value only"; the existing object has `en`/`fr`/`nl`. Builder must decide whether to add the key under all three (with English text in the fr/nl positions for now) or only under `en`. Reread the lookup code at line 53-54 — it falls back to `sectionTranslations.en` if a lang is missing the key, so either implementation works. Severity below the bar; not flagged.

---

## Final verdict

**VERIFIED.** All six Must-Have requirements trace into both IMPL_PLAN and CHECKLIST. All file paths and symbol references confirmed against the current codebase (line drift ≤3 lines on long-lived anchors; all symbol shapes and contracts intact). All 53 checklist items trace to a plan, spec, UX, or PROJECT_CHECKS source. No checklist orphans. The five MAJOR drifts called out in the prior ISSUES verdict are all resolved by the rebuilt CHECKLIST.

Seven MINOR findings, none blocking. Two are inherited stale wording from PROJECT_CHECKS.md (pdf_subprocess.py file missing; test count baseline outdated) and do not affect feature delivery.

Proceed to /v5-build.

---

## Return-value summary

```
status: VERIFIED
artifact: /Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/workbench/2-plan/verify/PLAN_VERIFIED_2026-05-05_flexible-resume-overview.md
traceability: covered=6/6, missing=0, deferred=0
hallucinated_files: 0
hallucinated_symbols: 0
checklist_orphans: 0
risk_findings: blockers=0, major=0, minor=7
top_issue: none — five prior MAJOR drifts all resolved; only inherited PROJECT_CHECKS.md staleness remains
```
