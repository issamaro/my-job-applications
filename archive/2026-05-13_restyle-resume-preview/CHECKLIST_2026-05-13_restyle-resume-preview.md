<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Verification checklist for slice 4 of the editorial redesign initiative — restyle-resume-preview. -->

feature: restyle-resume-preview
date: 2026-05-13
total_checkboxes: 144
derived_from: IMPL_PLAN_2026-05-13_restyle-resume-preview.md, FEATURE_SPEC_2026-05-13_restyle-resume-preview.md, UX_DESIGN_2026-05-13_restyle-resume-preview.md, SVELTE5_BINDABLE_NOTES_2026-05-13_restyle-resume-preview.md, SVELTE5_NOTES_2026-05-13_restyle-resume-preview.md

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` (verify: `cat .python-version`)  → source: IMPL_PLAN "Tests" section — `pytest tests/` is the test runner; `.python-version` found at repo root
- [ ] Virtual environment created and activated (verify: `which python` resolves to the project venv, not system Python)  → source: IMPL_PLAN "Build & verify steps" step 5 — `pytest tests/` implied local env
- [ ] Svelte `^5.0.0` present in `package.json` (verify: `npm list svelte` or `bun pm ls`)  → source: SVELTE5_NOTES "Version compatibility" — "Svelte 5 ships universal reactivity via runes"
- [ ] `bun` runtime available (verify: `bun --version` exits 0)  → source: IMPL_PLAN "Build & verify steps" steps 1 and 4 — `bun run build`, `bun run dev`

---

## Section 1 — Dependencies

- [ ] `svelte ^5.0.0` present in `package.json` (verify: `bun pm ls | grep svelte`)  → source: IMPL_PLAN "Library patterns to use" — "No new libraries. Svelte 5 runes only"
- [ ] `rollup ^4.0.0` present in `package.json` (verify: `bun pm ls | grep rollup`)  → source: IMPL_PLAN "Build & verify steps" step 4 — "zero Svelte / Rollup errors"
- [ ] `rollup-plugin-svelte ^7.2.0` present in `package.json` (verify: `bun pm ls | grep rollup-plugin-svelte`)  → source: IMPL_PLAN "Build & verify steps" step 4 — Svelte/Rollup build pipeline
- [ ] No new library entries added to `package.json` by this slice (verify: `git diff package.json` shows zero lines changed)  → source: IMPL_PLAN "Architecture summary" — "No new libraries"

---

## Section 2 — Syntax (Svelte 5 patterns)

- [ ] `$bindable('classic')` used in `TemplateSelector.svelte` script section (verify: `grep -n '\$bindable' src/components/TemplateSelector.svelte`)  → source: IMPL_PLAN "Library patterns to use" — "$bindable for `selected` in TemplateSelector. Pattern Q1"; SVELTE5_BINDABLE_NOTES "Q1 — $bindable() as a child-exposed prop"
- [ ] Parent `<TemplateSelector bind:selected={selectedTemplate}/>` syntax used in `ResumeView.svelte` (verify: `grep -n 'bind:selected' src/components/ResumeView.svelte`)  → source: IMPL_PLAN "Library patterns to use" — "Parent: `<TemplateSelector bind:selected={selectedTemplate}/>`"; SVELTE5_BINDABLE_NOTES "Q1"
- [ ] `$derived.by(() => …)` used for `sectionRows` in `ResumeView.svelte` (verify: `grep -n '\$derived\.by' src/components/ResumeView.svelte`)  → source: IMPL_PLAN "Library patterns to use" — "`$derived.by(() => …)` for derived state. Cite Q3 in SVELTE5_NOTES"
- [ ] `{#snippet children()}` + `{@render children()}` pattern used for all seven `EditorialSection` blocks in `ResumeView.svelte` (verify: `grep -c 'snippet children' src/components/ResumeView.svelte` returns 7)  → source: IMPL_PLAN "Library patterns to use" — "`{#snippet children()}` for EditorialSection consumption"
- [ ] `role="tablist"` on the `.resume-tabs` wrapper and `role="tab"` on each button in `ResumeView.svelte` (verify: `grep -n 'role="tablist"' src/components/ResumeView.svelte`)  → source: IMPL_PLAN "Library patterns to use" — "ARIA APG tab pattern"; FEATURE_SPEC Must-have 7 / Scenario 15b
- [ ] `aria-selected={editMode === '…'}` and `tabindex={editMode === '…' ? 0 : -1}` present on each tab button in `ResumeView.svelte` (verify: `grep -n 'aria-selected' src/components/ResumeView.svelte`)  → source: IMPL_PLAN "Library patterns to use" — "active = 0 and inactive = -1"
- [ ] `updateSelected` is the only function declared in `TemplateSelector.svelte` (verify: `grep -nE 'function ' src/components/TemplateSelector.svelte` returns exactly one match)  → source: IMPL_PLAN §3 — "only `updateSelected` (verb prefix, ≤3 words after verb). The component body is a pure render — no other functions"

---

## Section 3 — UX

### 3a. Page header chrome (UX State 1, Row 1 + Row 2)

- [ ] `← Back to Input` renders as `.btn-ghost` button (NOT a text-link; no `.back-link` class in DOM) at left of header  → source: UX_DESIGN "State 1 — Page header chrome Row 1" — "`.btn-ghost` containing `← Back to Input`"; FEATURE_SPEC Must-have 2
- [ ] `Regenerate` renders as `.btn` button at right of header  → source: UX_DESIGN "State 1 — Page header chrome Row 1" — "`.btn` containing `Regenerate`"; FEATURE_SPEC Must-have 2
- [ ] `.eyebrow` span reads `RESUME · FOR JOB` (uppercase, JetBrains Mono, tracked ≥ 0.10em, `var(--ink-3)`)  → source: UX_DESIGN "State 1 — Row 2" — "`<span class="eyebrow">RESUME · FOR JOB</span>`"; FEATURE_SPEC Must-have 2
- [ ] `<h1 class="display">` carries `{job_title} · {company_name}` (Instrument Serif, `var(--ink)`, singular page-level heading)  → source: UX_DESIGN "State 1 — Row 2" — "`<h1 class="display" …>Senior Engineer · Linear</h1>`"
- [ ] Sub-line shows `Generated {formatted_date}` (12px, `var(--ink-3)`) in a flex row with gap 12px baseline  → source: UX_DESIGN "State 1 — Row 2 Sub-line"
- [ ] Match pill shows `Match {round(score)}%` as `.pill.pill-positive` when `score >= 80`  → source: FEATURE_SPEC Must-have 2 — "score >= 80 → .pill-positive"
- [ ] Match pill shows `.pill.pill-warn` when `60 <= score < 80`  → source: FEATURE_SPEC Must-have 2 — "60 <= score < 80 → .pill-warn"
- [ ] Match pill shows `.pill.pill-accent` when `score < 60`  → source: FEATURE_SPEC Must-have 2 — "score < 60 → .pill-accent"
- [ ] No pill renders when `match_score === null` (sub-line shows only the date)  → source: FEATURE_SPEC Scenario 3; UX_DESIGN State 4 — "Match score null: no pill rendered"

### 3b. JobAnalysis card

- [ ] Card outer wrapper is `.card` primitive (NOT legacy `.requirements-card`)  → source: UX_DESIGN "State 1 — JobAnalysis card" — "`.card`"; FEATURE_SPEC Must-have 4
- [ ] Header row has `.eyebrow` reading `JOB · REQUIREMENTS` (NOT title-case) and a `.btn-ghost` collapse toggle with text `Hide` / `Show`  → source: UX_DESIGN "State 1 — JobAnalysis" — "`.eyebrow` `JOB · REQUIREMENTS`"; FEATURE_SPEC Must-have 4 / Scenario 16b
- [ ] Each skill chip is `.pill.pill-positive` (matched) or `.pill.pill-warn` (unmatched); `✓` / `✗` glyph inside chip text  → source: UX_DESIGN "State 1 — Skill pills"; FEATURE_SPEC Must-have 4
- [ ] Experience/Education inline rows: `var(--ink-2)` label + `.pill-positive` or `.pill-warn` chip  → source: UX_DESIGN "State 1 — Experience and Education inline rows"; FEATURE_SPEC Must-have 4
- [ ] `{#if jobAnalysis}` guard preserved — card absent when `job_analysis === null`  → source: FEATURE_SPEC Scenario 16c; UX_DESIGN State 4 — "job_analysis null: JobAnalysis card not rendered"

### 3c. 3-column layout and left rail

- [ ] `.resume-3col` is a flex row with `gap: var(--d-gap)` and `flex-wrap: wrap`  → source: FEATURE_SPEC Must-have 3; UX_DESIGN "3-column area"
- [ ] `<aside class="resume-rail">` has computed width 240px, `flex-shrink: 0`, `border-right: 1px solid var(--rule)`  → source: FEATURE_SPEC Must-have 5; UX_DESIGN "Left rail" — "240px, border-right: 1px solid var(--rule)"
- [ ] Templates group eyebrow reads `Templates · 04`; four `<button class="template-card">` render in order: Classic, Modern, Brussels, EU Classic  → source: UX_DESIGN "Templates group"; FEATURE_SPEC Must-have 5a / Scenario 5
- [ ] Each TemplateCard carries `aria-pressed`; active card has `background: var(--card)` and `border: 1px solid var(--ink)`; inactive card has `background: var(--paper-2)` and `border: 1px solid var(--rule)`  → source: FEATURE_SPEC Must-have 6; UX_DESIGN "Templates group"
- [ ] Language group eyebrow reads `Language`; one `.pill.pill-solid` chip shows `resume.language.toUpperCase()` and is NOT a `<button>` (no onclick, `cursor: default`)  → source: FEATURE_SPEC Must-have 5b; UX_DESIGN "Language group"; Scenario 7
- [ ] Language pill carries `aria-label="Resume language: {Language} (locked)"`  → source: UX_DESIGN a11y note 6; FEATURE_SPEC Scenario 7
- [ ] Sections group eyebrow reads `Sections`; seven `<button class="rail-section-row">` render in order: Identity, Summary, Experience, Education, Skills, Languages, Projects  → source: FEATURE_SPEC Must-have 5c; UX_DESIGN "Sections group"
- [ ] Identity and Summary rows have `aria-disabled="true"`, `tabindex="-1"`, `cursor: default`, label color `var(--ink-4)`, and clicking them is a no-op  → source: FEATURE_SPEC Must-have 5c — "Identity → no-op, disabled"; UX_DESIGN a11y note 5
- [ ] Each enabled Sections row has `aria-pressed={included}` reflecting its included state; clicking Projects fires `toggleSection('projects')`  → source: FEATURE_SPEC Scenario 8; UX_DESIGN a11y note 4

### 3d. Preview-mode pane

- [ ] `.resume-pane-preview` has `background: var(--paper-3)`, padding 28px, flex column, align-items center, gap 16px  → source: FEATURE_SPEC Must-have 8; UX_DESIGN "Preview-mode content"
- [ ] Page-meta eyebrow row: `<span class="eyebrow num">A4 · 210 × 297</span>` + `<span>1 / 1 page</span>` (11px, `var(--ink-3)`)  → source: FEATURE_SPEC Must-have 8; UX_DESIGN "Page-meta eyebrow row"
- [ ] `.resume-page` div: width 600px, min-height 848px, `background: white`, `box-shadow` containing `24px 48px -16px`  → source: FEATURE_SPEC Must-have 8 / Scenario 9; UX_DESIGN "Page surface"
- [ ] Action row below page surface: only `<button class="btn btn-primary">Download PDF</button>` (Regenerate is in header, NOT repeated here)  → source: FEATURE_SPEC Must-have 8 — "Action row therefore only has Download PDF"

### 3e. Edit-mode pane

- [ ] Seven `EditorialSection` blocks render in order: 01 Identity, 02 Summary, 03 Experience, 04 Education, 05 Skills, 06 Languages, 07 Projects  → source: FEATURE_SPEC Must-have 9 / Scenario 10; UX_DESIGN "State 2 — Edit-mode pane"
- [ ] `Loading resume…` paragraph (`<p class="resume-loading-note">`) renders in center pane when `resumeData === null` (italic, `var(--ink-3)`)  → source: FEATURE_SPEC Scenario 16c — null guard; UX_DESIGN State 3 — "Loading resume…"
- [ ] Section-excluded banner (`<p class="resume-section-excluded">Hidden from resume — re-check {Section} in the left rail to include.</p>`) appears at TOP of section body when `included === false`  → source: IMPL_PLAN §5j; FEATURE_SPEC Scenario 11; UX_DESIGN "Section toggled off" copy row

### 3f. Focus / accessibility

- [ ] `:focus-visible` outline is `2px solid var(--accent)` with 2px offset on all interactive elements inside `.resume-preview` (verify: `grep -n 'focus-visible' src/components/ResumeView.svelte`)  → source: UX_DESIGN a11y note 10; FEATURE_SPEC Scenario 10 (document outline)
- [ ] Language pill is NOT in the tab order (`tabindex` not set or absent; no keyboard activation)  → source: UX_DESIGN "Keyboard navigation map" — "Language pill — NOT focusable"

---

## Section 4 — Tests

- [ ] `pytest tests/` passes with zero regressions after all edits (verify: `pytest tests/` exit code 0)  → source: IMPL_PLAN "Tests" step 2; FEATURE_SPEC Scenario 18
- [ ] `tests/test_pdf_export.py` passes without modification  → source: IMPL_PLAN "Tests" — "Particular attention: tests/test_pdf_export.py"
- [ ] `tests/test_pdf_api.py` passes without modification  → source: IMPL_PLAN "Tests" — "tests/test_pdf_api.py"
- [ ] `tests/test_pdf_language.py` passes without modification  → source: IMPL_PLAN "Tests" — "tests/test_pdf_language.py"
- [ ] `tests/test_resumes.py` and all `tests/test_resume_*.py` pass without modification  → source: IMPL_PLAN "Tests" — "tests/test_resumes.py, tests/test_resume_*.py"
- [ ] `tests/test_skills.py` passes without modification  → source: IMPL_PLAN "Tests" — "tests/test_skills.py"
- [ ] `tests/test_users.py` passes without modification  → source: IMPL_PLAN "Tests" — "tests/test_users.py"
- [ ] `tests/test_work_experiences.py` passes without modification  → source: IMPL_PLAN "Tests" — "tests/test_work_experiences.py"
- [ ] `tests/test_topbar_shell.py` passes without modification  → source: IMPL_PLAN "Tests" — "tests/test_topbar_shell.py"
- [ ] `tests/test_profile_editor_restyle.py` passes without modification  → source: IMPL_PLAN "Tests" — "tests/test_profile_editor_restyle.py"
- [ ] Zero test files are modified by this slice (verify: `git diff --name-only tests/` shows no output)  → source: IMPL_PLAN "Tests" — "Zero modifications to test files"

---

## Section 5 — Accessibility (from UX_DESIGN)

- [ ] Keyboard Tab order follows the documented sequence: Back → Regenerate → JobAnalysis toggle → Edit tab → Preview tab → TemplateCards (4) → Sections rows (7) → center-pane affordances → Download PDF (verify by manual tab traversal or Playwright `page.keyboard.press('Tab')` loop)  → source: UX_DESIGN a11y note 8 and Keyboard navigation map
- [ ] Space/Enter on a TemplateCard activates it (verify: Playwright keyboard.press on Classic card)  → source: UX_DESIGN a11y note 9 — "TemplateCard: Space/Enter activates select"
- [ ] Space/Enter on an enabled Sections row fires `toggleSection(key)` (verify: Playwright keyboard.press on Experience row)  → source: UX_DESIGN a11y note 9 — "Sections checkbox row: Space/Enter toggles section"
- [ ] Space/Enter on Identity or Summary row is a no-op (`toggleSection` NOT called)  → source: UX_DESIGN a11y note 9; FEATURE_SPEC Scenario 8 — "Space/Enter on those rows is a no-op"
- [ ] `Cmd/Ctrl+Enter` on summary textarea fires `writeSummaryEdit` (verify: Playwright keyboard.press in summary edit mode)  → source: UX_DESIGN a11y note 9 — "Cmd/Ctrl+Enter on summary textarea → writeSummaryEdit"
- [ ] `Esc` on summary textarea fires `cancelEditSummary`; `Esc` on rename input fires `cancelEditSkill`  → source: UX_DESIGN a11y note 9; FEATURE_SPEC Scenario 12
- [ ] Match pill carries `aria-label="Match score: {N} percent, strong fit"` (≥80), "moderate fit" (60–79), or "weak fit" (<60)  → source: UX_DESIGN a11y note 7; IMPL_PLAN §5b — `findMatchAriaLabel`
- [ ] All text color / background pairings use only editorial tokens (`var(--ink)` / `var(--paper)`, etc.); no `--color-*` or hard-coded hex greys remain (verify: `grep -rn '#[0-9a-fA-F]\{3,6\}\|--color-' src/components/ResumeView.svelte src/components/TemplateSelector.svelte src/components/JobAnalysis.svelte` returns zero matches outside protected zone)  → source: UX_DESIGN "Visual tokens used"; FEATURE_SPEC Must-have 10 / Scenario 16

---

## Section 6 — Project-specific

n/a — no project-checks.md found (searched root and `.claude/` directory)

---

## Pre-flight (Section P)

- [ ] **PDF baseline capture (FIRST — before any source edit).** Run `bun run build && bun run dev`, pick one saved resume, download all 12 `(template, language)` PDFs, save to `workbench/3-build/pdf-baselines/` named `{template}_{language}.pdf`. If no saved resume exists, STOP and surface before proceeding.  → source: IMPL_PLAN "Build & verify steps" step 1
- [ ] **Working tree clean before edits begin.** `git status` shows no uncommitted changes to `src/`, `templates/`, or `tests/` before the first edit.  → source: IMPL_PLAN "Build & verify steps" step 3 — ordered edit sequence

---

## File-by-file edits (Section F)

### F1. `src/App.svelte` — extend `.container-wide` to resume tab

- [ ] Line 26 diff applied: `class:container-wide={activeTab === 'profile' || activeTab === 'resume'}` (verify: `grep -n 'container-wide' src/App.svelte` shows the `|| activeTab === 'resume'` clause)  → source: IMPL_PLAN §1; FEATURE_SPEC Must-have 1
- [ ] No other lines in `App.svelte` are changed (verify: `git diff src/App.svelte | grep '^[+-]' | grep -v '^---\|^+++' | wc -l` equals 2)  → source: IMPL_PLAN §1 — "1 line"
- [ ] `bun run build` succeeds with zero errors after this change  → source: IMPL_PLAN "Build & verify steps" step 4

### F2. `src/components/Topbar.svelte` — drop unused `store` import

- [ ] Pre-edit grep: `grep -nE "\bstore\b" src/components/Topbar.svelte` returns exactly one match (line 5, the import only); if a second match appears, do NOT proceed with the edit  → source: IMPL_PLAN §2 — "Pre-edit verification"
- [ ] Post-edit: `grep -n "\bstore\b" src/components/Topbar.svelte` returns zero matches  → source: IMPL_PLAN §2; FEATURE_SPEC Must-have 14 / Scenario 17
- [ ] `bun run build` succeeds with zero errors after this change  → source: IMPL_PLAN §2 — "bun run build succeeds"

### F3. `src/components/TemplateSelector.svelte` — rewrite body, keep contract

- [ ] Two-line lean-code header added at top: `<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->` + `<!-- Scope: Vertical stack of TemplateCard buttons bound to the resume's selected template. -->`  → source: IMPL_PLAN §3 "Lean-code header"
- [ ] `let { selected = $bindable('classic') } = $props();` present in script section  → source: IMPL_PLAN §3; FEATURE_SPEC Decision 5
- [ ] Four-template array with `id`, `name`, `sub` properties present (`classic`, `modern`, `brussels`, `eu_classic`)  → source: IMPL_PLAN §3; FEATURE_SPEC Must-have 5a
- [ ] `updateSelected(id)` is the sole function; sets `selected = id` on click  → source: IMPL_PLAN §3 — "only `updateSelected`"
- [ ] Each `<button class="template-card">` carries `aria-pressed` and fires `updateSelected(template.id)` on click  → source: IMPL_PLAN §3; FEATURE_SPEC Must-have 6
- [ ] All legacy classes (`.template-selector`, `.template-label`, `.template-dropdown`) and colour hex literals absent from the new style block  → source: IMPL_PLAN §3 — "drop all legacy classes"
- [ ] Active card: `background: var(--card)`, `border: 1px solid var(--ink)`. Inactive card: `background: var(--paper-2)`, `border: 1px solid var(--rule)`.  → source: IMPL_PLAN §3; FEATURE_SPEC Must-have 6
- [ ] `bun run build` succeeds with zero errors after this change  → source: IMPL_PLAN "Build & verify steps" step 4

### F4. `src/components/JobAnalysis.svelte` — restyle in place

- [ ] Two-line lean-code header added at top  → source: IMPL_PLAN §4 "Lean-code header"
- [ ] Script section unchanged: `let { jobAnalysis = null } = $props()`, `let collapsed = $state(false)`, `{#if jobAnalysis}` guard at line 7 preserved  → source: IMPL_PLAN §4; FEATURE_SPEC Scenario 16c
- [ ] Outer wrapper is `<div class="card resume-job-analysis">` (NOT `.requirements-card`)  → source: IMPL_PLAN §4; FEATURE_SPEC Must-have 4
- [ ] Header row: `.eyebrow` span with `JOB · REQUIREMENTS`, `<button class="btn-ghost">` collapse toggle with copy `{collapsed ? 'Show' : 'Hide'}` and `aria-expanded={!collapsed}`  → source: IMPL_PLAN §4; FEATURE_SPEC Must-have 4
- [ ] Required/Preferred skill sub-headers are `<span class="eyebrow">` (NOT `<h4>`)  → source: IMPL_PLAN §4; FEATURE_SPEC Must-have 4
- [ ] Zero references to `--color-border`, `--color-primary-rgb`, `--color-text-rgb`, `--color-success`, `--color-success-rgb`, `--color-error`, `--color-error-rgb` in the style block (verify: `grep -n 'color-' src/components/JobAnalysis.svelte` returns zero matches)  → source: IMPL_PLAN §4; FEATURE_SPEC Must-have 10
- [ ] `bun run build` succeeds with zero errors after this change  → source: IMPL_PLAN "Build & verify steps" step 4

### F5. `src/components/ResumeView.svelte` — big restyle

- [ ] Two-line lean-code header added at top  → source: IMPL_PLAN §5 "Lean-code header"
- [ ] 5a: `import ResumeSection` replaced with `import EditorialSection` (verify: `grep -n 'ResumeSection' src/components/ResumeView.svelte` returns zero matches)  → source: IMPL_PLAN §5a; FEATURE_SPEC Must-have 9
- [ ] 5b: `getScoreClass` removed; `findMatchPillVariant`, `findMatchAriaLabel`, `languageLockedLabels`, `sectionRows` ($derived.by), `readSectionAriaLabel`, `updateSectionFromRail` added (verify: `grep -n 'findMatchPillVariant\|findMatchAriaLabel\|sectionRows\|readSectionAriaLabel\|updateSectionFromRail' src/components/ResumeView.svelte` returns at least one match each; `grep -n 'getScoreClass' src/components/ResumeView.svelte` returns zero)  → source: IMPL_PLAN §5b
- [ ] 5c: `handleDownloadPdf` renamed to `writeDownloadedPdf`; single callsite updated to `onclick={writeDownloadedPdf}` (verify: `grep -n 'handleDownloadPdf' src/components/ResumeView.svelte` returns zero; `grep -n 'writeDownloadedPdf' src/components/ResumeView.svelte` returns two matches — declaration + callsite)  → source: IMPL_PLAN §5c / Risk R-5; FEATURE_SPEC Must-have 11
- [ ] 5d: Both `<hr>` separators in the old header/JobAnalysis area removed  → source: IMPL_PLAN §5d
- [ ] 5e: `<header class="resume-page-header">` structure present: Back button (`.btn-ghost`), title block (`.eyebrow` + `<h1 class="display">` + `.resume-page-meta`), Regenerate button (`.btn`)  → source: IMPL_PLAN §5e; FEATURE_SPEC Must-have 2
- [ ] 5f: `<JobAnalysis jobAnalysis={resume.job_analysis}/>` invocation unchanged in position and prop name  → source: IMPL_PLAN §5f
- [ ] 5g: `.resume-3col` wrapper with `.resume-rail` aside and `.resume-pane` div present; `<TemplateSelector bind:selected={selectedTemplate}/>` inside the rail  → source: IMPL_PLAN §5g; FEATURE_SPEC Must-have 3
- [ ] 5h: Preview-mode pane: `.resume-pane-preview` > page-meta eyebrow row > `.resume-page` (600px × 848px) > `<PdfPreview {resumeData} template={selectedTemplate} language={resume?.language || 'en'} />` > action row with Download PDF button calling `writeDownloadedPdf`  → source: IMPL_PLAN §5h; FEATURE_SPEC Must-have 8
- [ ] 5i: Edit-mode pane: seven `EditorialSection` blocks (01–07) using `{#snippet children()}` pattern; `{:else}<p class="resume-loading-note">Loading resume…</p>` when `resumeData` is falsy  → source: IMPL_PLAN §5i; FEATURE_SPEC Must-have 9
- [ ] 5j: Section-excluded banner present inside each editable EditorialSection body: `{#if !rowIncluded}<p class="resume-section-excluded">Hidden from resume — re-check {sectionLabel} in the left rail to include.</p>{/if}`  → source: IMPL_PLAN §5j; FEATURE_SPEC Scenario 11
- [ ] 5k: Bottom action row (legacy lines 651–656) removed — no Regenerate/Download at the bottom of the page  → source: IMPL_PLAN §5k; FEATURE_SPEC Must-have 2 / Must-have 8
- [ ] 5l: `<Toast bind:message=…/>` invocation unchanged at the bottom of the template  → source: IMPL_PLAN §5l
- [ ] New style block contains zero references to `--color-border`, `--color-primary`, `--color-primary-rgb`, `--color-text-rgb`, `--color-success`, `--color-success-rgb`, `--color-error`, `--color-error-rgb`, `--spacing-grid`, `--spacing-section`, `--spacing-field`, `#999`, `#ccc`, `#333`, `#e0e0e0`, `#f0f0f0`, `#cc6600` (verify: `grep -nE '(--color-|--spacing-|#999|#ccc|#333|#e0e0e0|#f0f0f0|#cc6600)' src/components/ResumeView.svelte` returns zero matches)  → source: IMPL_PLAN §5 "Zero references"; FEATURE_SPEC Must-have 10
- [ ] `.section-dimmed .editorial-section-title` and `.section-dimmed .editorial-section-header .num` rules present in `ResumeView` style block (CSS cross-scope via `:global()` or equivalent)  → source: IMPL_PLAN §5j / Risk R-6; FEATURE_SPEC Scenario 11
- [ ] `bun run build` succeeds with zero Svelte/Rollup errors after this change  → source: IMPL_PLAN "Build & verify steps" step 4

### F6. `src/components/ResumeSection.svelte` — delete

- [ ] Pre-deletion grep confirms zero consumers: `grep -rn "ResumeSection" src/ tests/` returns zero matches (after F5 is complete)  → source: IMPL_PLAN "Files to DELETE"; FEATURE_SPEC Decision 4
- [ ] `git rm src/components/ResumeSection.svelte` executed successfully  → source: IMPL_PLAN "Files to DELETE"
- [ ] `bun run build` succeeds after deletion  → source: IMPL_PLAN "Build & verify steps" step 4

---

## Automated verification (Section A)

- [ ] `bun run build` succeeds with zero Svelte compile errors and zero Rollup errors after all six file-by-file edits are complete  → source: IMPL_PLAN "Build & verify steps" step 4
- [ ] `pytest tests/` exits with code 0 (zero regressions) after all edits  → source: IMPL_PLAN "Build & verify steps" step 5; FEATURE_SPEC Scenario 18
- [ ] **Legacy class grep — zero matches outside protected zone:** `grep -nE '(\.back-link|\.view-mode-btn|\.download-btn|\.match-score|\.language-badge|\.toggle-btn|\.template-dropdown|\.template-label|\.template-selector|\.preview-title|\.preview-date|\.preview-header|\.view-mode-container|\.view-mode-toggle|\.preview-controls|\.section-title-btn|\.collapse-toggle|\.resume-section|\.resume-section-header|\.resume-section-content|\.section-hidden|\.requirements-card|\.requirements-header|\.requirement-section|\.requirement-inline|\.match-indicator|\.work-list|\.work-item|\.work-header|\.work-number|\.work-title|\.work-dates|\.work-description|\.work-footer|\.match-reasons|\.inline-edit|\.skill-tag|\.skill-action|\.available-skills-header|\.all-excluded-note|\.empty-note)' src/components/ResumeView.svelte src/components/TemplateSelector.svelte src/components/JobAnalysis.svelte src/components/PdfPreview.svelte` returns zero matches outside the inner `.pdf-preview template-…` div and its inline `<style>` block  → source: FEATURE_SPEC Scenario 15; IMPL_PLAN "Build & verify steps" step 7
- [ ] **Legacy token grep — zero matches outside protected zone:** `grep -nE '(--color-border|--color-primary|--color-primary-rgb|--color-text-rgb|--color-success|--color-success-rgb|--color-error|--color-error-rgb|--spacing-grid|--spacing-section|--spacing-field)' src/components/ResumeView.svelte src/components/TemplateSelector.svelte src/components/JobAnalysis.svelte src/components/PdfPreview.svelte` returns zero matches outside the protected PDF zone  → source: FEATURE_SPEC Scenario 16; IMPL_PLAN "Build & verify steps" step 7
- [ ] **Topbar store-import grep — zero matches:** `grep -nE "\bstore\b" src/components/Topbar.svelte` returns zero matches after the edit  → source: IMPL_PLAN §2; FEATURE_SPEC Scenario 17
- [ ] **Protected files untouched:** `git diff --stat templates/ src/components/PdfPreview.svelte` shows zero lines changed  → source: IMPL_PLAN Risk R-4; FEATURE_SPEC Must-have 12
- [ ] **PDF byte-identity for all 12 combinations:** for each `(template, language)` in `{classic, modern, brussels, eu_classic} × {en, fr, nl}`, run `cmp workbench/3-build/pdf-baselines/{template}_{language}.pdf <post-slice download>` — zero bytes differ for all 12 pairs  → source: IMPL_PLAN "Build & verify steps" step 6; FEATURE_SPEC Must-have 12 / Scenario 14

---

## Manual inspection (Section I — I-1 through I-24)

**MN-A carryover gate:** every bullet below is promoted verbatim from IMPL_PLAN "Manual inspection bullets". The Inspector agent and Q4 prompt feed off this list. The plan-reviewer agent verifies the 1:1 mapping.

- [ ] **I-1. Page header chrome.** `← Back to Input` is a `.btn-ghost` button (computed `background: transparent`, no underline on hover). Center block has eyebrow `RESUME · FOR JOB` (computed font-family contains "JetBrains Mono", `text-transform: uppercase`, `letter-spacing >= 0.10em`) and an `<h1 class="display">` with the page title (computed font-family contains "Instrument Serif"). Right has `Regenerate` as `.btn`. Below the title, `Generated {date}` sits next to a `.pill.pill-positive` chip when `match_score >= 80`.  → source: IMPL_PLAN "Manual inspection bullets" I-1

- [ ] **I-2. Match pill bands.** With `score >= 80`, the pill class is `pill-positive`. With `60 <= score < 80`, `pill-warn`. With `score < 60`, `pill-accent`. With `score == null`, no pill renders.  → source: IMPL_PLAN "Manual inspection bullets" I-2

- [ ] **I-3. Three-column shape.** `.resume-3col` exists with two visible children: `.resume-rail` (computed width 240px, flex-shrink 0) and `.resume-pane` (computed flex `1 1 0%`).  → source: IMPL_PLAN "Manual inspection bullets" I-3

- [ ] **I-4. Container-wide on resume tab.** `<div class="container">` has the `container-wide` class when `activeTab === 'resume'` (verified by `classList.contains('container-wide') === true`). The class is absent on other tabs.  → source: IMPL_PLAN "Manual inspection bullets" I-4

- [ ] **I-5. Templates rail group.** Eyebrow reads `Templates · 04`. Four `<button class="template-card">` elements render in order: Classic, Modern, Brussels, EU Classic. The active card has `aria-pressed="true"` and computed `border-color` matching `var(--ink)` (or its OKLCH equivalent).  → source: IMPL_PLAN "Manual inspection bullets" I-5

- [ ] **I-6. Template switch wiring.** Clicking Modern flips `aria-pressed` on Classic to `false` and on Modern to `true`. The `<PdfPreview>` inner `<div>` gains `class="pdf-preview template-modern"`. Subsequent Download PDF call hits `downloadPdf(resume.id, 'modern', resume.language)`.  → source: IMPL_PLAN "Manual inspection bullets" I-6

- [ ] **I-7. Language pill (locked).** Eyebrow `Language` followed by exactly one `.pill.pill-solid` chip carrying the resume's `language.toUpperCase()` text. The pill is NOT a `<button>`, has no onclick, `cursor: default`, and `aria-label` reads "Resume language: {Lang} (locked)".  → source: IMPL_PLAN "Manual inspection bullets" I-7

- [ ] **I-8. Sections rail.** Eyebrow `Sections` followed by seven `<button class="rail-section-row">` elements in order: Identity, Summary, Experience, Education, Skills, Languages, Projects. Identity and Summary have `aria-disabled="true"`, `tabindex="-1"`, `cursor: default` and the label colour is `var(--ink-4)` (computed OKLCH ≈ `oklch(0.70 0.025 265)`). The other five rows have `aria-pressed={true|false}` reflecting the section's `included` state. Clicking Projects flips `aria-pressed` AND triggers a `<PdfPreview>` re-render without projects (the `<div class="pdf-preview…">` inner content no longer has the projects block).  → source: IMPL_PLAN "Manual inspection bullets" I-8

- [ ] **I-9. Preview pane backdrop and page surface.** When `editMode === 'preview'`, `.resume-pane-preview` has computed `background-color` resolving to `var(--paper-3)`. Below the page-meta eyebrow, the `.resume-page` div has computed `width: 600px`, `min-height: 848px`, `background-color: rgb(255 255 255)`, and `box-shadow` containing the substring `24px 48px -16px` (substring match to avoid browser-format flake).  → source: IMPL_PLAN "Manual inspection bullets" I-9

- [ ] **I-10. PdfPreview content unchanged.** The inner `<div class="pdf-preview template-classic">` (or matching template) is byte-identical to a pre-slice snapshot. Captured by running `bun run build && bun run dev`, opening a saved resume, and diffing the rendered `outerHTML` of the first matching `.pdf-preview` element against the pre-slice baseline. (For automation: Playwright `page.locator('.pdf-preview').first().innerHTML()` should match the baseline exactly.)  → source: IMPL_PLAN "Manual inspection bullets" I-10

- [ ] **I-11. Tab pattern ARIA.** `.resume-tabs` carries `role="tablist"`, `aria-label="View mode"`. Each button has `role="tab"`, `aria-selected={true|false}`, `tabindex={0|-1}`. After clicking Preview: `aria-selected`/`tabindex` flip; Edit becomes `aria-selected="false"`, `tabindex="-1"`.  → source: IMPL_PLAN "Manual inspection bullets" I-11

- [ ] **I-12. Edit-mode shape.** With `editMode === 'edit'` and a populated resume, the pane renders seven EditorialSection blocks (01–07) — Identity, Summary, Experience, Education, Skills, Languages, Projects. Document outline: one `<h1>` + exactly seven `<h2>` headings from the EditorialSection blocks (per Must-have 9 and the document-outline success-criteria checkbox).  → source: IMPL_PLAN "Manual inspection bullets" I-12

- [ ] **I-13. JobAnalysis restyle.** Eyebrow reads `JOB · REQUIREMENTS` (NOT "Job Requirements" in title case). Collapse toggle is a `.btn-ghost` button with text `Hide` (or `Show` after collapse). Each required-skill chip is `.pill.pill-positive` (matched) or `.pill.pill-warn` (unmatched). Experience and education inline rows pair an `var(--ink-2)` label with a `.pill-positive` or `.pill-warn` chip. No `.requirements-*` legacy classes appear in the rendered DOM.  → source: IMPL_PLAN "Manual inspection bullets" I-13

- [ ] **I-14. Inline-edit affordances preserved.** Round-trip in Edit mode: (I-14a) Click Edit on the Summary section, type ` X`, press Cmd+Enter → API PATCH/PUT fires, summary persists, `Saved` indicator surfaces. (I-14b) Click rename pencil on a skill chip, type new name, press Enter → API call fires, chip text updates, no toast error. (I-14c) Click exclude × on a skill chip → skill moves to "Available skills" row below, included flag flips. (I-14d) Drag a work experience row from position 2 to position 1 → order persists after the drop event; `Order saved` toast surfaces. (I-14e) Click Edit on a work description, type text, click Save → description persists; `Saved` indicator surfaces.  → source: IMPL_PLAN "Manual inspection bullets" I-14

- [ ] **I-15. Section toggle from rail (Preview mode).** From Preview mode, click the Projects row in the rail → row's `aria-pressed` flips to `false`, `.rail-section-checkbox` background changes from `var(--ink)` to transparent, `<PdfPreview>` re-renders without the projects block. The legacy `[ON]/[OFF]` toggle does not appear in the DOM anywhere.  → source: IMPL_PLAN "Manual inspection bullets" I-15

- [ ] **I-16. Section toggle from rail (Edit mode).** From Edit mode, with the Projects row currently included, click it → the `EditorialSection № 07 Projects` block in the center pane gets the `.section-dimmed` wrapper class, its header and number turn `var(--ink-3)`, and a `<p class="resume-section-excluded">` banner appears at the TOP of the section body reading "Hidden from resume — re-check Projects in the left rail to include." Project rows still render below the banner.  → source: IMPL_PLAN "Manual inspection bullets" I-16

- [ ] **I-17. Legacy class grep.** Run the grep in Scenario 15 against `src/components/ResumeView.svelte`, `src/components/TemplateSelector.svelte`, `src/components/JobAnalysis.svelte`, and the OUTER chrome of `src/components/PdfPreview.svelte`. Exactly zero matches outside the protected inner `<div class="pdf-preview template-…">` markup and `<style>` block.  → source: IMPL_PLAN "Manual inspection bullets" I-17

- [ ] **I-18. Legacy token grep.** Run the grep in Scenario 16 — zero matches outside the protected PDF zone.  → source: IMPL_PLAN "Manual inspection bullets" I-18

- [ ] **I-19. Topbar import cleanup.** `grep -n "\bstore\b" src/components/Topbar.svelte` returns zero matches. `bun run build` succeeds.  → source: IMPL_PLAN "Manual inspection bullets" I-19

- [ ] **I-20. PDF byte-identity (the load-bearing gate).** Capture pre-slice baseline PDFs for one representative resume: `(classic, en), (modern, en), (brussels, en), (eu_classic, en), (classic, fr), …, (eu_classic, nl)` = 12 PDFs. After this slice, download the 12 PDFs again from the same resume. Diff byte-by-byte (`cmp pre.pdf post.pdf`). Zero bytes differ. Implementation: capture baselines BEFORE editing any source file. Store under `workbench/3-build/pdf-baselines/`.  → source: IMPL_PLAN "Manual inspection bullets" I-20

- [ ] **I-21. `pytest tests/` zero regressions.** Particular attention to the PDF suite. Zero test files modified.  → source: IMPL_PLAN "Manual inspection bullets" I-21

- [ ] **I-22. Focus-visible outline.** Tab through every interactive element in the rendered page. Each focused element shows a `2px solid var(--accent)` outline with 2px offset. No element shows the legacy `--color-primary` outline.  → source: IMPL_PLAN "Manual inspection bullets" I-22

- [ ] **I-23. Empty / loading states.** Open a resume immediately on first mount (before `$effect` populates `resumeData`): the center pane shows `<p class="resume-loading-note">Loading resume…</p>` in `var(--ink-3)` italic. The page header chrome and JobAnalysis card render normally (they read from `resume.*`, not `resumeData`).  → source: IMPL_PLAN "Manual inspection bullets" I-23

- [ ] **I-24. Document outline.** Open browser devtools accessibility tree → one `<h1>` (page title), seven `<h2>` headings from the EditorialSection blocks. Zero `<h3>` or `<h4>` from the restyled components. (The PdfPreview inner `<div>` is OUT of scope and may carry its own template-specific `<h*>` — those are inside the protected zone.)  → source: IMPL_PLAN "Manual inspection bullets" I-24

---

## Lean-code self-check (Section L)

- [ ] Every new or renamed function in all modified files starts with one of the nine permitted verbs: `read`, `write`, `create`, `delete`, `update`, `find`, `check`, `parse`, `render` (verify: `grep -nE 'function [a-z]' src/components/ResumeView.svelte src/components/TemplateSelector.svelte src/components/JobAnalysis.svelte` — every match must start with one of the nine verbs)  → source: CLAUDE.md "Function naming" — "Permitted verbs"
- [ ] No function name contains `handle`, `process`, `manage`, or `do` (verify: `grep -nE 'function (handle|process|manage|do)[A-Z]' src/components/ResumeView.svelte src/components/TemplateSelector.svelte src/components/JobAnalysis.svelte` returns zero matches)  → source: CLAUDE.md "Forbidden patterns" — "`handleX`, `processX`, `manageX`, `doX` — hides the actual operation"; IMPL_PLAN Risk R-5 — `handleDownloadPdf` renamed to `writeDownloadedPdf`
- [ ] No abbreviations in any function or variable name in the modified files (verify: `grep -nE '\b(cfg|ctx|req|res|opts|params|fn|cb|evt|btn|msg|err)\b' src/components/ResumeView.svelte src/components/TemplateSelector.svelte src/components/JobAnalysis.svelte` returns zero matches)  → source: CLAUDE.md "Forbidden patterns" — "cfg, ctx, req, res, opts, params"
- [ ] Each modified Svelte file begins with exactly the two-line lean-code header comment and zero other comments in the file body (verify: `grep -c '<!--' src/components/TemplateSelector.svelte` equals 2; same for `JobAnalysis.svelte`; for `ResumeView.svelte` equals 2 plus any `svelte-ignore` lines that existed in legacy)  → source: CLAUDE.md "Comments" — "Every file begins with exactly two comment lines … After the header: ZERO comments"
- [ ] No inline `<!-- comments -->` added inside the template body of any modified file beyond the two-line header (existing `svelte-ignore` comments for `a11y_autofocus` preserved verbatim, no new ones added without justification)  → source: IMPL_PLAN "Build & verify steps" step 4 — "no new svelte-ignore comments added without justification"
