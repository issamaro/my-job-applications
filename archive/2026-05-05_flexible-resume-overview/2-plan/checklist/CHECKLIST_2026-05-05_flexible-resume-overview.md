feature: flexible-resume-overview
date: 2026-05-05
total_checkboxes: 53
derived_from: IMPL_PLAN_2026-05-05_flexible-resume-overview.md, FEATURE_SPEC_2026-05-05_flexible-resume-overview.md, UX_DESIGN_2026-05-05_flexible-resume-overview.md, PROJECT_CHECKS.md

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` (verify: `cat .python-version`)  → source: IMPL_PLAN "Library posture"; PROJECT_CHECKS.md "Expected versions: Python 3.13"
- [ ] `pyproject.toml` declares `requires-python = ">=3.13"`  → source: PROJECT_CHECKS.md "Environment Setup"; pyproject.toml line 5
- [ ] `package.json` declares `"svelte": "^5.0.0"` in `devDependencies`  → source: IMPL_PLAN "Library posture — Single library: Svelte 5 (^5.0.0, per package.json:14)"
- [ ] Python virtual environment created and active: `.venv/bin/python --version` shows `3.13.x`  → source: PROJECT_CHECKS.md "Verify setup — Check Python version"

---

## Section 1 — Dependencies

- [ ] `svelte ^5.0.0` present in `package.json` devDependencies (verify: `bun pm ls | grep svelte`)  → source: IMPL_PLAN "Library posture — Single library: Svelte 5 (^5.0.0, per package.json:14)"
- [ ] `fastapi >=0.100.0` present in `pyproject.toml` (verify: `grep fastapi pyproject.toml`)  → source: PROJECT_CHECKS.md "Check dependencies — import fastapi"
- [ ] `pydantic >=2.0` present in `pyproject.toml`  → source: PROJECT_CHECKS.md "Check dependencies — import pydantic"
- [ ] `pytest >=8.0.0` present in `pyproject.toml` dev group  → source: PROJECT_CHECKS.md "Test Suite — python -m pytest -v"
- [ ] `httpx >=0.27.0` present in `pyproject.toml` dev group (required by test client)  → source: PROJECT_CHECKS.md; F2 uses `client` fixture from `tests/conftest.py:26-29`

---

## Section 2 — Syntax

- [ ] `$state` used (not `writable` or raw variables) for all five new reactive vars in `src/components/ResumeView.svelte` script block  → source: IMPL_PLAN F1.1 "Add five new $state vars"
- [ ] Exactly five new `$state` declarations present in `ResumeView.svelte` around lines 57-68: `editingSummary`, `summaryDraft`, `editingSkillIndex`, `skillDraft`, `savingSkillIndex` — no more, no fewer  → source: IMPL_PLAN F1.1 "EXACTLY FIVE new $state vars"; corrected-plan delta #2
- [ ] No `$effect` block present for autofocus in `ResumeView.svelte`  → source: IMPL_PLAN R-Plan-3; corrected-plan delta #1 "No $effect, no bind:this"
- [ ] No `bind:this` ref vars (`summaryTextareaRef`, `skillRenameRef`) present anywhere in `ResumeView.svelte`  → source: IMPL_PLAN R-Plan-3; corrected-plan delta #1
- [ ] Autofocus implemented via `{#if editing}<input … autofocus />` pattern with `<!-- svelte-ignore a11y_autofocus -->` on the line above — mirrors `src/components/SavedJobItem.svelte:118-128`  → source: IMPL_PLAN R-Plan-3; corrected-plan delta #1
- [ ] `bind:value={summaryDraft}` on the summary `<textarea>` (not `value={summaryDraft}`)  → source: IMPL_PLAN F1.4 "render a <textarea bind:value={summaryDraft}>"
- [ ] `bind:value={skillDraft}` on the skill rename `<input>` (not `value={skillDraft}`)  → source: IMPL_PLAN F1.5 markup `<input bind:value={skillDraft}`
- [ ] `toggleSection` function declared `async` in `ResumeView.svelte`  → source: IMPL_PLAN F1.3 "The function becomes async"; corrected-plan delta #4
- [ ] Skills branch of `toggleSection` uses `const anyExcluded = resumeData.skills.some(s => s.included === false)` then `resumeData.skills = resumeData.skills.map(s => ({ ...s, included: anyExcluded }))` — not the old `skills[0]?.included` pattern  → source: IMPL_PLAN F1.3 "deterministic two-state rule from MH-6"; FEATURE_SPEC MH-6
- [ ] Skills branch of `toggleSection` wraps the `await updateResume(resume.id, resumeData)` call in `try { … } catch (err) { resumeData.skills = previous; toastType = 'error'; toastMessage = 'Could not save skills. Try again.'; }`  → source: IMPL_PLAN F1.3 final shape; corrected-plan delta #4
- [ ] `previous` snapshot captured via `JSON.parse(JSON.stringify(resumeData.skills))` before the map in the skills branch of `toggleSection`  → source: IMPL_PLAN F1.3 final shape `const previous = JSON.parse(...)`
- [ ] `{#each resumeData.skills as skill, index}` iterates the full stable array, filtered by `{#if skill.included !== false}` inside — NOT via `.filter()` producing a sublist  → source: IMPL_PLAN F1.5 "Critical: the {#each} iterates over the stable array"; FEATURE_SPEC R7; UX_DESIGN B.7
- [ ] `class:saving-skill={savingSkillIndex === index}` applied to active skill chip `<span>` wrapper  → source: IMPL_PLAN F1.5 markup; UX_DESIGN B.4
- [ ] CSS rule `.skill-tag.saving-skill { opacity: 0.5; pointer-events: none; }` present in `ResumeView.svelte` style block  → source: IMPL_PLAN F1.6 ".skill-tag.saving-skill"
- [ ] CSS `@supports not (field-sizing: content)` fallback at 160px fixed present for `.skill-tag input`  → source: IMPL_PLAN F1.6 "R-Plan-2 fallback"; UX_DESIGN B.3
- [ ] `savedId === '__summary__'` sentinel used for the summary saved badge (not a numeric id that could collide with work-experience IDs)  → source: IMPL_PLAN F1.2 `writeSummaryEdit` — "sentinel string '__summary__' cannot collide with any work-experience id"
- [ ] `writeSummaryEdit` on success calls `setTimeout(() => savedId = null, 2000)` — 2000ms for the savedId badge, NOT a Toast duration  → source: IMPL_PLAN F1.2; IMPL_PLAN R-Plan-7; corrected-plan delta #6 ("2000ms is for the savedId badge, not the Toast")
- [ ] Toast component duration is 3000ms as defined in `Toast.svelte:12` — implementation does NOT pass a custom duration  → source: IMPL_PLAN R-Plan-7; UX_DESIGN B.4 "hard-coded 3000ms"; corrected-plan delta #6
- [ ] Zero inline comments in new code added to `ResumeView.svelte` (the `<!-- svelte-ignore a11y_autofocus -->` Svelte compiler directive is the only in-source markup allowed)  → source: CLAUDE.md "ZERO comments. No inline comments."; IMPL_PLAN F1.5 "Per CLAUDE.md ZERO comments — no inline comment will be added"; corrected-plan delta #3

---

## Section 3 — UX

### Region A — Summary

- [ ] Display state (A.1): `<p class="summary">` rendered with an `[Edit]` button (`class="edit-btn"`) when `editingSummary === false` and `resumeData.summary` is truthy  → source: UX_DESIGN A.1; IMPL_PLAN F1.4 "resumeData.summary is truthy"
- [ ] Empty-summary state (A.5): when `editingSummary === false` and `resumeData.summary` is falsy, no `<p class="summary">` rendered; `[Add summary]` button appears using `onclick={startEditSummary}`  → source: UX_DESIGN A.5; IMPL_PLAN F1.4; FEATURE_SPEC S9
- [ ] Editing state (A.2): `<textarea>` with `rows="4"` and `autofocus` rendered when `editingSummary === true`, followed by `[Save]` and `[Cancel]` buttons  → source: UX_DESIGN A.2; IMPL_PLAN F1.4
- [ ] Saving state (A.3): `[Save]` button disabled (`disabled={saving}`) while `saving === true`; `[Cancel]` also disabled  → source: UX_DESIGN A.3; IMPL_PLAN F1.4 "disabled while saving — mirror disabled={saving} at line 328"
- [ ] Saved state (A.4): saved indicator span visible when `savedId === '__summary__'`, using `aria-live="polite"`  → source: UX_DESIGN A.4 "aria-live=polite so screen readers announce Saved"; IMPL_PLAN F1.4; FEATURE_SPEC S1
- [ ] Error state (A.6): on API failure, Toast fires `"Could not save summary. Try again."` with `toastType = 'error'`; editor stays open  → source: UX_DESIGN A.6; IMPL_PLAN F1.2 `writeSummaryEdit` error branch

### Region B — Skills

- [ ] Active group (B.1): each skill chip in the `{#if skill.included !== false}` branch shows: name, `✓` if `skill.matched`, rename button `✎` (`aria-label="Rename skill {skill.name}"`), exclude button `×` (`aria-label="Exclude skill {skill.name}"`)  → source: UX_DESIGN B.1; IMPL_PLAN F1.5
- [ ] Editing chip (B.3): when `editingSkillIndex === index`, chip body replaced with `<input bind:value={skillDraft}>` with `aria-label="Rename skill {skill.name}"`, save button `✓` (`aria-label="Save skill name"`), cancel button `×` (`aria-label="Cancel rename"`)  → source: UX_DESIGN B.3; IMPL_PLAN F1.5
- [ ] Loading state (B.4): chip wrapper has `class:saving-skill={savingSkillIndex === index}` giving `opacity: 0.5; pointer-events: none` while PUT is in flight; dim removed on resolve  → source: UX_DESIGN B.4; IMPL_PLAN F1.5 + F1.6
- [ ] Success state (B.4): Toast fires `"Saved"` on successful skill mutation (exclude, re-include, rename) via `toastMessage / toastType` — no per-chip persistent indicator  → source: UX_DESIGN B.4 "no per-chip persistent indicator"; IMPL_PLAN F1.2 `updateSkillInclusion`
- [ ] Error state (B.5): Toast fires `"Could not save skills. Try again."` (red); `resumeData = JSON.parse(JSON.stringify(resume.resume))` reverts local state  → source: UX_DESIGN B.5; IMPL_PLAN F1.2 `writeSkillRename` / `updateSkillInclusion` error branch
- [ ] "Available skills" header (B.2): `<h4 class="available-skills-header">Available skills</h4>` shown only when `resumeData.skills.some(s => s.included === false)`  → source: UX_DESIGN B.2; IMPL_PLAN F1.5 "Available group (only if any excluded)"
- [ ] Available group chips (B.2): excluded skills rendered in `{#if skill.included === false}` branch with `class="skill-tag excluded"` and `+` button (`aria-label="Re-include skill {skill.name}"`)  → source: UX_DESIGN B.2; IMPL_PLAN F1.5
- [ ] All-excluded notice (B.6): `<p class="all-excluded-note">` with text `"All skills excluded — re-include one below, or use the section toggle."` shown when `resumeData.skills.every(s => s.included === false)`  → source: UX_DESIGN B.6 copy table; IMPL_PLAN F1.5; FEATURE_SPEC concrete-copy table
- [ ] Empty-skills state (B.6): when `resumeData.skills.length === 0`, skills section body renders `"No skills."` (no edit affordances)  → source: UX_DESIGN B.6 "No skills at all"
- [ ] CSS `.skill-tag.excluded { opacity: 0.5; }` present  → source: IMPL_PLAN F1.6 ".skill-tag.excluded"
- [ ] CSS `.available-skills-header` rule present with `font-size: 12px; text-transform: uppercase`  → source: IMPL_PLAN F1.6 ".available-skills-header"
- [ ] `sectionTranslations` object in `ResumeView.svelte` includes an `availableSkills` entry (English value only; structure for future translation)  → source: UX_DESIGN "Translations — Add an entry in sectionTranslations for availableSkills"

---

## Section 4 — Tests

### BDD scenario coverage (F2 — `tests/test_resumes.py`)

- [ ] `test_update_resume_skill_excluded` present in `tests/test_resumes.py`: POST generation → PUT with one skill `included: false` → GET asserts that skill still present with `included === False`  → source: IMPL_PLAN F2; FEATURE_SPEC S4
- [ ] `test_update_resume_skill_renamed` present in `tests/test_resumes.py`: POST generation → PUT with mutated skill `name` → GET asserts new name preserved, `matched` and `included` unchanged  → source: IMPL_PLAN F2; FEATURE_SPEC S6
- [ ] `test_update_resume_summary_empty` present in `tests/test_resumes.py`: PUT with `summary: ""` → GET returns `summary: ""` (not None, not prior value)  → source: IMPL_PLAN F2; FEATURE_SPEC S9
- [ ] Each new test uses the `client` fixture from `tests/conftest.py:26-29` (a TestClient conftest fixture)  → source: IMPL_PLAN F2 "Use the client fixture from tests/conftest.py (defined at conftest.py:26-29)"; corrected-plan delta #5
- [ ] Each new test is decorated with `@patch("services.resume_generator.llm_service.analyze_and_generate")` and receives `mock_llm` as its first parameter — `mock_llm` is NOT a conftest fixture, it is the patch decorator's injected object  → source: IMPL_PLAN F2 "pattern at tests/test_resumes.py:162-163"; corrected-plan delta #5
- [ ] Existing `pytest tests/` suite stays fully green (all pre-existing tests pass, no regressions)  → source: IMPL_PLAN "Test plan — Run existing pytest tests/ — must stay green"; PROJECT_CHECKS.md "Test Suite"

### Build verification

- [ ] `bun run build` succeeds (Rollup + Svelte compile, no syntax or reactivity errors)  → source: IMPL_PLAN "Test plan — Run bun run build"; PROJECT_CHECKS.md "Frontend Build"
- [ ] Build output files `public/build/bundle.js` and `public/build/global.css` exist after build  → source: PROJECT_CHECKS.md "Verify output files exist"
- [ ] Bundle size remains under 500KB (`wc -c public/build/bundle.js`)  → source: PROJECT_CHECKS.md "Health Indicators — Bundle size < 500KB"

---

## Section 5 — Accessibility

- [ ] Summary `[Edit]` / `[Add summary]` button is a `<button>` element (keyboard-focusable, `Enter` activates)  → source: UX_DESIGN A.7 "Edit button is keyboard-focusable; Enter opens the editor"
- [ ] Inside the summary textarea, `onkeydown` handler `readSummaryKey` fires: `Cmd/Ctrl+Enter` → `writeSummaryEdit()`; `Esc` → `cancelEditSummary()`  → source: UX_DESIGN A.7; IMPL_PLAN F1.4 "`readSummaryKey(e)`"
- [ ] Summary saved indicator span has `aria-live="polite"`  → source: UX_DESIGN A.7 "aria-live=polite so screen readers announce Saved"
- [ ] Skill rename input has `aria-label="Rename skill {skill.name}"`  → source: UX_DESIGN B.8; IMPL_PLAN F1.5 `aria-label="Rename skill {skill.name}"`
- [ ] Skill exclude button has `aria-label="Exclude skill {skill.name}"`  → source: UX_DESIGN B.8; IMPL_PLAN F1.5 `aria-label="Exclude skill {skill.name}"`
- [ ] Skill re-include button has `aria-label="Re-include skill {skill.name}"`  → source: UX_DESIGN B.8; IMPL_PLAN F1.5 `aria-label="Re-include skill {skill.name}"`
- [ ] Skill rename save button has `aria-label="Save skill name"`  → source: IMPL_PLAN F1.5 `aria-label="Save skill name"`
- [ ] Rename input `onkeydown` handler `readSkillKey` fires: `Enter` → `writeSkillRename(index)`; `Esc` → `cancelEditSkill()`  → source: IMPL_PLAN F1.5 "`readSkillKey` handles Enter → save, Esc → cancel"; UX_DESIGN B.3
- [ ] All skill action buttons (✎, ×, +) are `<button>` elements — not `<span>` with click handler  → source: UX_DESIGN B.8 "Each affordance is a <button>"
- [ ] `:focus` outline present on `.skill-tag .skill-action`: `outline: 2px solid var(--color-primary); outline-offset: 1px;`  → source: IMPL_PLAN F1.6 ":focus { outline: 2px solid var(--color-primary); outline-offset: 1px; }"

---

## Section 6 — Project-specific

Items transcribed verbatim from `PROJECT_CHECKS.md`:

- [ ] Backend imports clean: `python -c "from main import app; print('FastAPI app: OK')"` prints `FastAPI app: OK`  → source: PROJECT_CHECKS.md "Backend Health — Test app imports"
- [ ] Database initializes: `python -c "from database import init_db; init_db(); print('Database: OK')"` prints `Database: OK`  → source: PROJECT_CHECKS.md "Backend Health — Test database can initialize"
- [ ] All route modules import without error: `from routes import personal_info, work_experiences, education` and `from routes import skills, projects, resumes, job_descriptions`  → source: PROJECT_CHECKS.md "Backend Health — Test all routes import"
- [ ] `python -m pytest -v` passes; test count remains ≥101 (pre-existing baseline) plus the 3 new tests  → source: PROJECT_CHECKS.md "Test Suite — Expected output: All tests pass (101 as of 2026-01-04)" + IMPL_PLAN F2 adds 3
- [ ] `bun run build` produces `public/build/bundle.js`; "created public/build/bundle.js" message appears; circular dep warnings from Svelte internals are safe to ignore  → source: PROJECT_CHECKS.md "Frontend Build — Expected output"
- [ ] WeasyPrint importable: `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib python -c "from weasyprint import HTML; print('WeasyPrint: OK')"` prints `WeasyPrint: OK`  → source: PROJECT_CHECKS.md "PDF Generation — Check WeasyPrint can import"
- [ ] PDF generation uses subprocess pattern via `services/pdf_subprocess.py`; WeasyPrint is NOT imported directly in the uvicorn process  → source: PROJECT_CHECKS.md "Architecture Note: PDF generation uses a subprocess pattern"
- [ ] Stale test DB files (`test_*.db`) absent before test run (delete if present to avoid DB errors)  → source: PROJECT_CHECKS.md "Failure Troubleshooting — Tests fail with DB errors → Delete test_*.db files"

---

## Section 7 — Zero-change gate

The following files MUST have zero modifications relative to the pre-feature commit. Verify with `git diff HEAD -- <file>` returning empty.

### F3 — `src/components/PdfPreview.svelte`

- [ ] `src/components/PdfPreview.svelte` has zero diff: `git diff HEAD -- src/components/PdfPreview.svelte` is empty  → source: IMPL_PLAN F3 "No changes needed — includedSkills derived at lines 56-58 already filters on included !== false; renamed skills already render via {skill.name}; edited summaries already render via {@render summarySection(resumeData.summary)}"

### F4 — `src/components/ResumeSection.svelte`

- [ ] `src/components/ResumeSection.svelte` has zero diff: `git diff HEAD -- src/components/ResumeSection.svelte` is empty  → source: IMPL_PLAN F4 "onToggle callback wires through to toggleSection('skills') — that's the only relationship. Treating ResumeSection as opaque. No changes."

### F5 — Backend files

- [ ] `routes/resumes.py` has zero diff: `git diff HEAD -- routes/resumes.py` is empty  → source: IMPL_PLAN F5 "routes/resumes.py:59-64 PUT endpoint — accepts whole ResumeContent; no change"
- [ ] `services/resume_generator.py` has zero diff: `git diff HEAD -- services/resume_generator.py` is empty  → source: IMPL_PLAN F5 "services/resume_generator.py:137-167 — round-trips arbitrary ResumeContent; no change"
- [ ] `schemas.py` has zero diff: `git diff HEAD -- schemas.py` is empty  → source: IMPL_PLAN F5 "schemas.py:240 ResumeSkill — already has included: bool = True and name: str mutable; no change"
- [ ] `database.py` has zero diff: `git diff HEAD -- database.py` is empty  → source: IMPL_PLAN F5 "database.py — resume_content is a JSON blob; no migration"
