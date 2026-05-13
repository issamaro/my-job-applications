# FEATURE_SPEC — restyle-resume-preview

Date: 2026-05-13
Ceremony: M (full)
Slice: 4 of 9 — editorial redesign initiative

## Persona

**Primary:** the job-seeking professional who maintains MyCV as their single
source-of-truth profile and generates tailored CVs against saved jobs. After
generation, they open the Resume preview to review the LLM's output, tweak
the included sections, optionally rename a few skills, switch templates to
preview a different layout, and download the PDF. Desktop, English locale,
multiple resumes generated against multiple saved jobs. Same persona as
slices 2 and 3.

## Core pain point

Slices 1–3 shipped editorial primitives (`--ink*` / `--paper*` / `.eyebrow`
/ `.display` / `.card` / `.btn*` / `.pill*`), the editorial Topbar, and the
restyled Profile editor. The Resume preview screen now visually clashes
against the rest of the app: native `<select>` template picker, scattered
inline `[ON]/[OFF]` section toggles, terracotta-era badges
(`.match-score`, `.language-badge`), legacy `--color-border` greys, view-
mode tabs with underline-on-active. This slice lands the Resume preview on
editorial primitives — matching `design-bundle/project/screen-resume.jsx`
visually — without changing what the LLM produces, what weasyprint exports,
or what the existing toggle/edit/drag handlers do.

## Solution (one paragraph)

Restyle `ResumeView.svelte`, `TemplateSelector.svelte`,
`ResumeSection.svelte`, `JobAnalysis.svelte`, and the chrome wrapping
`PdfPreview.svelte` to the editorial primitives shipped by slices 1–3.
Introduce a 240px left rail (Templates · Language · Sections) and a
centered A4-ratio page preview on a `--paper-3` backdrop with a soft drop
shadow. Replace the inline `<select>` template picker with vertical
`TemplateCard`s, replace each section's inline `[ON]/[OFF]` toggle with a
centralised left-rail checkbox list, replace the `.match-score` badge with
a `.pill-positive` / `.pill-warn` / `.pill-accent` chip keyed to the score
band. **The PDF render path** (`templates/resume_base.css` + the four HTML
templates fed to weasyprint) **and the inner `<div class="pdf-preview
template-…">` markup and its inline `<style>` block stay byte-identical.**
PDF byte-identity is the hard gate.

## Must-have list

1. **`App.svelte` container-wide extension.** Extend
   `src/App.svelte:26` from
   `class:container-wide={activeTab === 'profile'}` to
   `class:container-wide={activeTab === 'profile' || activeTab === 'resume'}`.
   The existing `.container-wide` rule in `src/styles/global.css:181-184`
   resolves to `max-width: none; padding: 0` (i.e., the wide container
   removes both the 800px cap and the section padding of the default
   `.container`). This is the exact same opt-out slice 3 used for the
   profile editor. The 800px default cap can't seat a 240px rail plus a
   600px A4 page preview plus gaps; removing the cap lets the resume
   page span the viewport.

2. **Header chrome (full-width inside `.resume-preview`).** Replaces the
   current `.preview-header` and `.preview-title` blocks. Layout: a single
   row containing a left-aligned `← Back to Input` button restyled as
   `.btn-ghost` (no underlined text-link), a centered editorial title
   block, and a right-aligned `Regenerate` button restyled as `.btn`.
   The centered title block is two rows: an
   `.eyebrow`-classed `<span>` reading `RESUME · FOR JOB` (font-family
   JetBrains Mono, uppercase, tracked >= 0.10em, `var(--ink-3)`), then a
   serif `<h1 class="display">` (Instrument Serif, ~32–36px,
   `var(--ink)`) carrying `{job_title} · {company_name}`. The page
   heading is `<h1>` (singular page-level heading) so the document
   outline below (`EditorialSection` blocks rendering `<h2>` per slice 3
   — verified at `src/components/EditorialSection.svelte:11`) cleanly
   nests as section-level headings. A sub-line below the heading shows
   `Generated {formatted_date}` (12px, `var(--ink-3)`) and — if
   `resume.match_score` is non-null — a `.pill` chip to the right of
   the sub-line carrying `Match {Math.round(score)}%` with the variant
   keyed by score band:
   - `score >= 80` → `.pill-positive`
   - `60 <= score < 80` → `.pill-warn`
   - `score < 60` → `.pill-accent`
   The legacy classes `.back-link`, `.match-score`, `.preview-title`,
   `.preview-date`, `.language-badge`, `.score-high`, `.score-medium`,
   `.score-low` are dropped along with their `<style>` blocks. Existing
   `onBack` and `onRegenerate` props keep their callsites.

3. **3-column layout (header below, 2 visible columns).** Below the
   header chrome and the `JobAnalysis` card (Must-have 4), the page
   renders a flex row: a 240px left rail (Must-have 5) on the left and
   a flex-1 center pane (Must-have 7) on the right. **The right context
   aside from the design source is OUT** (deferred to slice 6/7). The
   row uses `gap: var(--d-gap)` for horizontal separation. On viewports
   below the 1024px breakpoint the rail wraps above the pane
   (single-column stack) — no media-query-driven hiding, just
   `flex-wrap: wrap` with `min-width: 240px` on the rail and
   `min-width: 0` on the pane.

4. **`JobAnalysis.svelte` restyle in place.** Same DOM position (above
   the 3-col area, after the page header chrome), same data, same
   collapse behaviour. Visual rebuild:
   - Outer wrapper: `.card` primitive (padding `var(--d-pad)`, `1px
     solid var(--rule)`, `background: var(--paper)`).
   - Header row: `.eyebrow` `JOB · REQUIREMENTS` on the left,
     `.btn-ghost` collapse toggle on the right with copy `Hide` /
     `Show` (the `[+]`/`[-]` ASCII glyph is dropped).
   - Required/Preferred skills sub-headers: `.eyebrow` (mono, tracked).
   - Skill chips: `.pill` primitive. Matched → `.pill-positive`,
     unmatched → `.pill-warn` (NOT `.pill-negative` — unmatched is a
     soft signal, not an error). The trailing `✓` / `✗` glyph is kept
     for screen-reader-independent recognition.
   - Experience / education inline lines: `var(--ink-2)` 13px label +
     `.pill-positive` / `.pill-warn` chip carrying the
     `Required: 5+ yrs` and a `✓` or `✗` glyph.
   The legacy classes `.requirements-card`, `.requirements-header`,
   `.collapse-toggle`, `.requirement-section`, `.requirement-inline`,
   `.match-indicator`, `.skill-tag.matched`, `.skill-tag.unmatched` are
   dropped along with their `<style>` blocks. All `--color-border`,
   `--color-primary-rgb`, `--color-text-rgb`, `--color-success`,
   `--color-error*` references in JobAnalysis.svelte are gone.

5. **Left rail — `.resume-rail` (240px, three groups).** A flex-column
   `<aside>` with `width: 240px`, `flex-shrink: 0`, `padding: 0
   var(--d-pad) 0 0`, separated from the center pane by `1px solid
   var(--rule)` on the right edge (mirrors the design source). Three
   groups, each preceded by an `.eyebrow` header and separated by
   `<hr class="rule-soft">`:

   **5a. Templates · 04** — vertical stack of four `TemplateCard`
   components (Must-have 6) bound to `selectedTemplate` from
   `ResumeView`. `<TemplateSelector>` is rewritten (NOT deleted): its
   `<script>` keeps the same `templates` array of four IDs (`classic`,
   `modern`, `brussels`, `eu_classic`) and the `bind:selected`
   `$bindable` contract; its template body and `<style>` are replaced
   with the vertical `TemplateCard` stack.

   **5b. Language** — read-only `.pill` chip showing
   `resume.language.toUpperCase()` (`EN` / `FR` / `NL`). NOT a button
   group, NOT interactive — generation locked the language. The pill
   carries the variant `.pill-solid` (`var(--ink)` background,
   `var(--paper)` color) so it's visually distinct from clickable
   pills. Tooltip / `aria-label` `Resume language: English` (or French
   / Dutch / locked) for screen readers.

   **5c. Sections** — a `<div>` of seven checkbox rows, one per
   section: Identity, Summary, Experience, Education, Skills,
   Languages, Projects. Each row is a 14px-icon checkbox (CSS-only:
   14×14, `border-radius: 2px`, `background: var(--ink)` when checked,
   `transparent` when unchecked, `1px solid var(--rule)` border) + a
   12px label (`var(--ink)` when checked, `var(--ink-3)` when
   unchecked). The row is a `<button type="button">` so it's keyboard-
   focusable; pressing space/enter fires the same `toggleSection()`
   handler in `ResumeView.svelte:276` that the inline `[ON]/[OFF]`
   button fires today. Mapping from row label to `toggleSection(key)`:
   - `Identity` → no-op (the identity card cannot be toggled off in
     the current schema; row is rendered but `disabled` with
     `var(--ink-4)` text and no checkbox click handler — see Decision 3)
   - `Summary` → no-op (same; resume summary is always rendered when
     non-empty; row is rendered `disabled` — see Decision 3)
   - `Experience` → `toggleSection('work')`
   - `Education` → `toggleSection('education')`
   - `Skills` → `toggleSection('skills')`
   - `Languages` → `toggleSection('languages')`
   - `Projects` → `toggleSection('projects')`
   The `included` boolean for each row is derived the same way the
   existing `ResumeSection` `included` prop is derived (e.g.
   `resumeData.work_experiences?.[0]?.included !== false`,
   `resumeData.projects?.[0]?.included === true`, etc.). Toggling
   updates `resumeData` reactively and the PdfPreview re-renders
   (existing flow).

6. **`TemplateCard` (vertical card primitive).** Per
   `design-bundle/project/screen-resume.jsx:200`. Rendered inside
   `TemplateSelector.svelte` (one per template). Layout:
   - Outer `<button type="button">` with `padding: 12px` (round to a
     4px-grid value; the design source uses 10px, but the editorial
     density tokens land on 4px increments — pick 12px so the card
     sits on the same vertical rhythm as `.card` and `.pill`),
     `background: var(--card)` when active else `var(--paper-2)`,
     `border: 1px solid var(--ink)` when active else `1px solid
     var(--rule)`, `border-radius: var(--r-sm)`, full-width.
   - Mini preview (top, 90px tall): a stylised CSS-only sketch of the
     page — centered name band, sub-line rule, body rules — using
     `var(--ink)` and `var(--ink-3)` / `var(--rule-soft)` for the
     strokes. Same shape for every template (the mini preview is
     decorative; recognisability comes from the name + sub).
   - Name row (12px semibold) + sub (`var(--ink-3)`, 10px) describing
     the template:
     - `classic` → `Classic` / `Serif · centered`
     - `modern` → `Modern` / `Sans · accent rule`
     - `brussels` → `Brussels` / `Two-column · photo`
     - `eu_classic` → `EU Classic` / `Serif · header bar`
   - Active marker: `<span class="num">` reading `● active`
     (`color: var(--accent)`, 10px), right-aligned in the name row,
     visible only when `template.id === selected`.
   - Click → `selected = template.id` (via `bind:selected` from
     `ResumeView`).
   - `aria-pressed` reflects active state.

7. **Center pane — view-mode toggle + content.** Top of the pane is a
   horizontal pair of buttons that visually reads as a segmented
   control (no new primitive added — composition uses existing `.btn`
   / `.btn-ghost`):
   - Two `<button type="button">` elements: `Edit` and `Preview`,
     placed in a flex row with `gap: 4px` and an outer wrapper
     `padding: 4px`. The active button uses `.btn` (paper-on-ink
     filled), the inactive uses `.btn-ghost`. Both buttons carry
     `font-size: 12px` and `padding: 6px 12px` (vertical 6px,
     horizontal 12px — both on the 4px grid).
   - `role="tablist"` on the wrapper with `aria-label="View mode"`,
     `role="tab"` on each button, `aria-selected={editMode === 'edit'}`
     / `aria-selected={editMode === 'preview'}` on the active /
     inactive buttons respectively. `tabindex` on the inactive tab is
     `-1` per the ARIA APG tab pattern, on the active tab it is `0`.
   - The legacy `.view-mode-btn` / underline-on-active styling is
     dropped.

   Below the toggle, content switches by `editMode`:
   - **Preview mode** (Must-have 8) — page-meta eyebrow, A4 surface,
     action row.
   - **Edit mode** (Must-have 9) — the existing editor restyled with
     editorial primitives.

8. **Preview-mode pane (page on paper-3 backdrop).** Per
   `design-bundle/project/screen-resume.jsx:59-131`. The pane has:
   - Outer wrapper: `background: var(--paper-3)`, padding
     `var(--d-gap)` (28px from the editorial density tokens — same
     value the design source uses), `display: flex`,
     `flex-direction: column`, `align-items: center`, `gap: 16px`.
   - Page-meta eyebrow row (baseline-aligned, gap 12px):
     `<span class="eyebrow num">A4 · 210 × 297</span>` then
     `<span style="color: var(--ink-3); font-size: 11px;">1 / 1 page</span>`.
     The byte-count from the design source (`612 KB`) is OUT for this
     slice — we don't know the PDF size without generating it, and
     generating-on-mount is a perf regression. The `1 / 1 page` text
     is a hard-coded placeholder since the screen preview is a single
     div, not a paginated PDF. Documented as Compromise #1 (see
     "Known compromises" below).
   - Page surface: a 600px-wide, 848px-tall (A4 ratio 1:1.414) div
     with `background: white`, `box-shadow: 0 1px 0 rgba(0,0,0,0.04),
     0 24px 48px -16px rgba(0,0,0,0.18)`. The page surface CONTAINS
     `<PdfPreview {resumeData} template={selectedTemplate}
     language={...}/>` exactly as today — the inner `<div
     class="pdf-preview template-…">` markup and its inline `<style>`
     block stay byte-identical. The page surface scrolls internally
     if PdfPreview overflows; the outer pane scrolls vertically.
   - Action row (below the page, baseline-aligned, gap 10px):
     `<button class="btn btn-primary">Download PDF</button>`, then
     `<button class="btn">Regenerate</button>` — wait, Regenerate is
     in the page header (Must-have 2). Action row therefore only has
     **Download PDF**. The legacy `.download-btn` class is dropped.

9. **Edit-mode pane (editor restyled).** The existing edit-mode
   content (Identity, Summary, Experience, Skills, Education,
   Languages, Projects) keeps every behaviour (inline edit, summary
   draft, skill curation, drag-reorder, project list) and re-uses the
   `EditorialSection` component shipped by slice 3 for section
   headers. Specifically:
   - **Section headers** swap from raw `<ResumeSection>` calls to
     `<EditorialSection number="03" title="Experience" count={…}>` —
     same numbering pattern as slice 3 profile editor (01 Identity,
     02 Summary, 03 Experience, 04 Education, 05 Skills, 06 Languages,
     07 Projects). The existing `ResumeSection.svelte` is **deleted**
     (single consumer is `ResumeView.svelte`, verified by grep — see
     Risks). Section toggles move to the left-rail Sections group
     (Must-have 5c); the inline `[ON]/[OFF]` button is gone.
   - **Identity card** renders an `EditorialSection № 01 Identity`
     wrapper around a two-row block: line 1 is the full-name semibold
     16px (`var(--ink)`), lines 2 and 3 are contact lines (12px
     `var(--ink-3)`, `email · phone` on line 2, `location · linkedin`
     on line 3). No inline edit affordance here — personal_info is
     read-only in the resume edit view today; this slice preserves
     that.
   - **Summary** lives in its own `EditorialSection № 02 Summary`
     block (NOT inside the Identity card), matching slice 3 exactly.
     The section body is a single `.textarea`-primitive editor (when
     `editingSummary === true`) or the rendered summary text + an
     `Edit` `.btn-ghost` link (when `editingSummary === false`). All
     existing keybinds (Cmd/Ctrl+Enter to save, Esc to cancel) and
     state flow (`summaryDraft`, `writeSummaryEdit`, `savedId ===
     '__summary__'` indicator) preserved verbatim.
   - **Experience timeline** restyled per slice 3 pattern: 3-column
     grid (`110px 1fr auto`) with mono dates left, title+company+
     description middle, `.btn-ghost` Edit right. Drag handle on
     hover (`⋮⋮`, `var(--ink-3)`) preserved with the same
     ondragstart/over/end/drop wiring. `.work-list` / `.work-item` /
     `.work-header` / `.work-dates` / `.work-description` /
     `.work-footer` / `.match-reasons` / `.inline-edit` /
     `.edit-actions` legacy styles dropped; new styles use editorial
     tokens.
   - **Skills cluster** restyled per slice 3 pattern: `.pill` chips
     for saved skills (variant: matched → `.pill-positive`,
     not-matched → `.pill` default), plus a separator and an
     available-skills row of `.pill` chips with dashed border
     (`border-style: dashed`) for one-click add. The inline rename
     edit affordance (Enter to save, Esc to cancel, `field-sizing:
     content` input) is preserved verbatim, restyled to inherit
     editorial typography. `.skill-tag` / `.skill-action` /
     `.available-skills-header` / `.all-excluded-note` /
     `.empty-note` legacy styles dropped.
   - **Education list** restyled per slice 3 pattern: 3-column grid
     (`70px 1fr auto`), mono year left, degree + institution middle,
     `.btn-ghost` Edit right. Existing edit form preserved.
   - **Languages list** restyled per slice 3 pattern: 2-column grid
     of language cards. The existing comma-separated line render is
     replaced with the slice-3 card grid; data binding to
     `resumeData.languages` unchanged.
   - **Projects rows** restyled per slice 3 pattern: 2-column grid
     (`1fr auto`), name + technologies + description middle,
     `.btn-ghost` Edit right.

10. **Token sweep (component-wide).** Inside `ResumeView.svelte`,
    `TemplateSelector.svelte`, `ResumeSection.svelte` (before
    deletion), `JobAnalysis.svelte`, and the `PdfPreview` wrapper
    chrome (NOT the inner `<style>` block), **zero matches** of:
    - `--color-border`, `--color-primary`, `--color-primary-rgb`,
      `--color-text-rgb`, `--color-success`, `--color-success-rgb`,
      `--color-error`, `--color-error-rgb`
    - `--spacing-grid`, `--spacing-section`, `--spacing-field`
    - Hard-coded greys (`#e0e0e0`, `#999`, `#ccc`, `#333`, etc.) —
      EXCEPT inside the `PdfPreview` inner inline `<style>` block,
      which is OUT of scope.
    All borders → `var(--rule)` / `var(--rule-soft)`. All ink levels
    → `var(--ink)` / `var(--ink-2)` / `var(--ink-3)` / `var(--ink-4)`.
    All accent overlays → `var(--accent-soft)` or `var(--accent)`. All
    spacing → `var(--d-pad)` / `var(--d-gap)` / `var(--d-row)` / 4px
    increments.

11. **Behaviour preservation (hard gate).** Every existing user flow
    works after the restyle, with no functional change:
    - Template select → screen preview re-renders (CSS variable
      `selectedTemplate` flows through to PdfPreview).
    - Download PDF → existing `downloadPdf(resume.id, template,
      language)` call fires; the produced PDF is byte-identical to
      pre-slice for the same `(template, language, included sections)`
      combination.
    - Section toggle (from left rail) → fires `toggleSection(key)`
      with the same key strings (`work`, `skills`, `education`,
      `projects`, `languages`); persistence, optimistic update, error
      revert, toast behaviour all preserved.
    - Edit mode: inline summary edit (Esc / Cmd+Enter), inline skill
      rename (Enter / Esc / `field-sizing: content`), skill exclude/
      include, profile-skill add, work drag-reorder, work description
      edit — all behaviour preserved.
    - Regenerate → fires `onRegenerate` prop callback (existing).
    - Back → fires `onBack` prop callback (existing).
    - Match score → renders with the same numeric value, just in a
      pill instead of a coloured-text badge.

12. **PDF byte-identity (hard gate).** The downloaded PDF for every
    template (`classic`, `modern`, `brussels`, `eu_classic`) and
    every language (`en`, `fr`, `nl`) is byte-identical to a
    pre-slice baseline PDF generated with the same inputs.
    Specifically:
    - `templates/resume_base.css` is NOT edited.
    - `templates/resume_classic.html`, `templates/resume_modern.html`,
      `templates/resume_brussels.html`, `templates/resume_eu_classic.html`
      are NOT edited.
    - The inner `<div class="pdf-preview template-…">` markup and the
      inline `<style>` block in `src/components/PdfPreview.svelte`
      are NOT edited.
    - `tests/test_pdf_export.py`, `tests/test_pdf_api.py`,
      `tests/test_pdf_language.py`, `tests/test_resumes.py`, and
      every `tests/test_resume_*.py` continue to pass with zero
      modifications.

13. **Slice 3 carryover · CHECKLIST promotion (MN-A).** Slice 3's
    retro flagged that Inspector-style manual-inspection bullets
    appeared in IMPL_PLAN but were never promoted to CHECKLIST
    checkboxes — meaning inspect-time the bullets had no place to
    tick. For this slice, IMPL_PLAN's "Manual inspection items"
    section MUST be mirrored 1:1 as explicit `[ ]` checkboxes in
    CHECKLIST. The `checklist-builder` agent receives an explicit
    instruction (in its dispatch prompt) to do this promotion, and
    `plan-reviewer` checks the 1:1 mapping as a verify item. Failure
    surfaces an ISSUES gate.

14. **Slice 3 carryover · Topbar unused import sweep.** Slice 3's
    IMPL_PLAN line 202 kept the `store` named import in
    `src/components/Topbar.svelte` verbatim, even though it was no
    longer used after the wiring landed via `$effect`. This slice
    drops the unused import IF a grep over Topbar.svelte confirms
    `store` is still unused inside the script + template. If the
    grep returns any use, leave the import alone and note in retro.

## BDD scenarios

**Scenario 1 — Editorial header chrome.**
- **Given** a saved resume with `job_title: "Senior Engineer"`,
  `company_name: "Linear"`, `match_score: 87`, `created_at: "2026-05-10"`,
- **When** the user navigates to `activeTab === 'resume'` and opens the
  resume,
- **Then** the page header chrome renders a left-aligned `← Back to
  Input` button styled as `.btn-ghost` (no underlined text-link
  appearance, no `.back-link` class in the DOM),
- **And** the center title block shows an `.eyebrow`-classed span
  reading `RESUME · FOR JOB` (computed font-family contains
  `JetBrains Mono`, `text-transform: uppercase`, `letter-spacing >=
  0.10em`),
- **And** below the eyebrow an `<h1 class="display">` reads
  `Senior Engineer · Linear` (computed font-family contains
  `Instrument Serif`),
- **And** a right-aligned `Regenerate` button is styled as `.btn`,
- **And** a sub-line below the heading reads
  `Generated May 10, 2026` followed by a `.pill.pill-positive` chip
  reading `Match 87%`,
- **And** the legacy classes `.back-link`, `.match-score`,
  `.preview-title`, `.preview-date`, `.language-badge` are absent
  from the rendered DOM.

**Scenario 2 — Match pill variant keyed to score.**
- **Given** the same resume but with `match_score: 65`,
- **When** the page renders,
- **Then** the match pill renders as `.pill.pill-warn` (not
  `.pill-positive`, not `.pill-accent`),
- **When** the resume changes to `match_score: 40`,
- **Then** the match pill renders as `.pill.pill-accent`.

**Scenario 3 — Match pill absent when score is null.**
- **Given** a resume with `match_score: null`,
- **When** the page renders,
- **Then** no `.pill` element appears inside the page header chrome
  (the sub-line shows only `Generated {date}` with no trailing chip).

**Scenario 4 — Three-column layout shape.**
- **Given** a saved resume opens in `ResumeView` on a desktop
  viewport (≥1024px),
- **When** the page renders,
- **Then** the layout below the header chrome and JobAnalysis card is
  a flex row containing exactly two children: a `<aside
  class="resume-rail">` with computed `width: 240px` and
  `flex-shrink: 0` on the left, and a `<div class="resume-pane">`
  with computed `flex` expanding to `1 1 0%` (the shorthand
  expansion of `flex: 1`) on the right,
- **And** the rail's right edge has computed
  `border-right: 1px solid var(--rule)` (or equivalent
  `border-right-color: oklch(0.85 0.02 260)`).

**Scenario 4b — container-wide class toggles on resume tab.**
- **Given** the App.svelte renders with `activeTab === 'profile'`,
- **When** the user switches to `activeTab === 'resume'`,
- **Then** the `<div class="container">` element gains the
  `container-wide` class (verified by `classList.contains
  ('container-wide') === true`),
- **And** when the user switches back to `activeTab === 'profile'`,
  the class is still present (slice 3 preserves it for profile),
- **And** when the user switches to any other tab (e.g.
  `interview`), the class is absent.

**Scenario 5 — Left rail Templates group.**
- **Given** the page renders with `selectedTemplate === 'classic'`,
- **When** the Templates group is inspected,
- **Then** the group has an `.eyebrow` header reading `Templates · 04`
  followed by four `TemplateCard` buttons in order: Classic, Modern,
  Brussels, EU Classic,
- **And** the Classic card has `aria-pressed="true"` and computed
  `border-color` matching `var(--ink)`,
- **And** the Classic card's name row contains an `<span class="num">`
  reading `● active`,
- **And** the other three cards have `aria-pressed="false"` and
  computed `border-color` matching `var(--rule)`.

**Scenario 6 — Template switch via TemplateCard.**
- **Given** the page is rendered with Classic active,
- **When** the user clicks the Modern `TemplateCard`,
- **Then** Modern becomes active (`aria-pressed="true"`, `● active`
  marker visible) and Classic deactivates,
- **And** the `selectedTemplate` state in `ResumeView` becomes
  `'modern'`,
- **And** the `<PdfPreview>` inside the preview pane re-renders with
  `template="modern"` (the inner `<div>` gains `class="pdf-preview
  template-modern"`),
- **When** the user clicks Download PDF,
- **Then** `downloadPdf(resume.id, 'modern', resume.language)` fires
  and the produced PDF is byte-identical to a pre-slice baseline PDF
  generated for the same `(resume.id, 'modern', language)`.

**Scenario 7 — Left rail Language pill (locked).**
- **Given** a saved resume with `language: "fr"`,
- **When** the Language group renders,
- **Then** the group has an `.eyebrow` reading `Language` and a
  single `.pill.pill-solid` chip reading `FR`,
- **And** the pill is NOT a button (no `<button>` element, no
  `onclick` handler, no cursor pointer on hover),
- **And** the pill carries `aria-label="Resume language: French
  (locked)"` (or equivalent) for screen readers.

**Scenario 8 — Left rail Sections checkbox toggles.**
- **Given** a saved resume with all sections `included`, including
  `projects: [{included: true}, ...]`,
- **When** the Sections group renders,
- **Then** the group has an `.eyebrow` reading `Sections` and seven
  rows in order: Identity, Summary, Experience, Education, Skills,
  Languages, Projects,
- **And** each row is a `<button type="button">` with computed
  `display` of flex/grid (a 14×14 checkbox glyph + label),
- **And** Identity and Summary rows are rendered `disabled`:
  `aria-disabled="true"`, label `color: var(--ink-4)` (computed
  resolves to the slice-1 OKLCH `oklch(0.70 0.025 265)` or equivalent
  `rgba` triplet), `cursor: default`, no `onclick` handler attached,
  and Space/Enter on those rows is a no-op (`toggleSection` is not
  called),
- **And** the other five rows are enabled and reflect their
  `included` state — checkbox filled with `var(--ink)` background
  when included, transparent with `var(--rule)` border when excluded,
- **When** the user clicks the Projects row,
- **Then** `toggleSection('projects')` fires, every
  `resumeData.projects[i].included` flips, the `<PdfPreview>` re-
  renders without projects, and the Projects checkbox visual flips
  to unchecked,
- **And** the legacy `.toggle-btn` (the `[ON]/[OFF]` button on
  `ResumeSection` headers) does NOT appear anywhere in the rendered
  DOM.

**Scenario 9 — Preview pane shape (paper-3 backdrop + A4 page).**
- **Given** the user is in Preview mode (`editMode === 'preview'`),
- **When** the center pane renders,
- **Then** the pane has computed `background-color` matching
  `var(--paper-3)` (or equivalent `oklch(0.90 0.02 260)`),
- **And** the pane's first child is a row of two `.eyebrow`-classed
  spans: `A4 · 210 × 297` (`<span class="eyebrow num">`) and
  `1 / 1 page` (`<span>` 11px `var(--ink-3)`),
- **And** the pane's second child is a `.resume-page` div with
  computed `width: 600px`, `min-height: 848px`, `background-color:
  rgb(255 255 255)` (white), and `box-shadow` containing the design
  source's two-shadow stack (`0 1px 0 rgba(0,0,0,0.04), 0 24px 48px
  -16px rgba(0,0,0,0.18)`),
- **And** the `.resume-page` div contains the `<PdfPreview>` whose
  inner `<div class="pdf-preview template-…">` markup is byte-
  identical to pre-slice (verified by diffing the rendered HTML
  fragment of just that `<div>` against a pre-slice snapshot).

**Scenario 10 — Edit mode shape (numbered editorial sections).**
- **Given** the user is in Edit mode (`editMode === 'edit'`),
- **When** the center pane renders for a resume with non-empty
  `summary`, `work_experiences`, `skills`, `education`, `languages`,
  `projects`,
- **Then** the pane renders an Identity card (full-name semibold,
  contact lines `var(--ink-3)`) at top,
- **And** below it six `EditorialSection` blocks in order: `№ 02
  Summary`, `№ 03 Experience`, `№ 04 Education`, `№ 05 Skills`, `№
  06 Languages`, `№ 07 Projects`,
- **And** sections 03–07 display a count next to the title (`.num`
  classed 12px `var(--ink-3)`),
- **And** the legacy `ResumeSection` component is NOT rendered (no
  element with class `.resume-section`, no `[ON]/[OFF]` toggle
  button, no `[+]/[-]` collapse glyph).

**Scenario 11 — Section toggle (from rail) flips Edit-mode visibility.**
- **Given** the user is in Edit mode and the Projects section
  contains one project,
- **When** the user clicks the Projects row in the left rail's
  Sections group (which currently shows `included: true`),
- **Then** `toggleSection('projects')` fires and every
  `resumeData.projects[i].included` flips to `false`,
- **And** the Projects `EditorialSection` block in the center pane
  re-renders with its header dimmed (`color: var(--ink-3)` on both
  the section number and the title) and a paragraph
  `<p class="section-excluded">Hidden from resume — re-check
  Projects in the left rail to include.</p>` (12px, `var(--ink-3)`,
  italic) inserted at the top of the section body BEFORE the project
  rows. Project rows still render below (preserving slice 3 pattern
  — content not hidden, just marked excluded).

**Scenario 12 — Inline edit preserved (summary).**
- **Given** the user is in Edit mode and the Summary section is
  visible,
- **When** the user clicks Edit, types ` More text.`, and presses
  Cmd+Enter,
- **Then** `writeSummaryEdit()` fires, `PUT /api/resumes/{id}` is
  called with the new `summary`, the textarea closes, and the
  `Saved` indicator appears for 2 seconds — same as today.

**Scenario 13 — Inline skill rename preserved.**
- **Given** the user is in Edit mode and a skill `"Python"` is in
  `resumeData.skills`,
- **When** the user clicks the rename pencil on the Python pill,
  changes the input to `Python 3.12`, and presses Enter,
- **Then** `writeSkillRename(index)` fires, `PUT /api/resumes/{id}`
  is called with `resumeData.skills[index].name === "Python 3.12"`,
  the input closes, and a success toast appears — same as today.

**Scenario 14 — PDF byte-identity across templates and languages.**
- **Given** a saved resume with `language: "en"`,
- **When** the user clicks Download PDF for each of the four
  templates (Classic, Modern, Brussels, EU Classic) one at a time,
- **Then** each produced PDF is byte-identical to a pre-slice
  baseline PDF generated for the same `(resume_id, template, "en")`
  combination,
- **When** the test is repeated for `language: "fr"` and
  `language: "nl"`,
- **Then** all 12 produced PDFs (4 templates × 3 languages) are
  byte-identical to pre-slice baselines.

**Scenario 15 — Legacy classes absent (grep over restyled files).**
- **Given** the build succeeds,
- **When** running `grep -nE
  '(\.back-link|\.view-mode-btn|\.download-btn|\.match-score|\.language-badge|\.toggle-btn|\.template-dropdown|\.template-label|\.template-selector|\.preview-title|\.preview-date|\.preview-header|\.view-mode-container|\.view-mode-toggle|\.preview-controls|\.section-title-btn|\.collapse-toggle|\.resume-section|\.resume-section-header|\.resume-section-content|\.section-hidden|\.requirements-card|\.requirements-header|\.requirement-section|\.requirement-inline|\.match-indicator|\.work-list|\.work-item|\.work-header|\.work-number|\.work-title|\.work-dates|\.work-description|\.work-footer|\.match-reasons|\.inline-edit|\.skill-tag|\.skill-action|\.available-skills-header|\.all-excluded-note|\.empty-note)'
  src/components/ResumeView.svelte src/components/TemplateSelector.svelte
  src/components/JobAnalysis.svelte src/components/PdfPreview.svelte`,
- **Then** the only matches are inside the inner `<div
  class="pdf-preview template-…">` markup and the inline `<style>`
  block in `PdfPreview.svelte` (which are OUT of scope), and the
  remaining classes from the legacy list are absent from
  ResumeView/TemplateSelector/JobAnalysis source files.

**Scenario 16 — Legacy color tokens absent.**
- **Given** a grep over `ResumeView.svelte`, `TemplateSelector.svelte`,
  `JobAnalysis.svelte`, and the OUTER chrome of `PdfPreview.svelte`
  (anything outside the inner `<div class="pdf-preview template-…">`
  markup and its inline `<style>` block),
- **When** scanning for `--color-border`, `--color-primary`,
  `--color-primary-rgb`, `--color-text-rgb`, `--color-success`,
  `--color-success-rgb`, `--color-error`, `--color-error-rgb`,
  `--spacing-grid`, `--spacing-section`, `--spacing-field`,
- **Then** zero matches are found inside any `<style>` block or
  inline `style="..."` attribute outside the protected PDF zone.

**Scenario 15b — View-mode tab ARIA wiring.**
- **Given** the page renders with `editMode === 'edit'` (default),
- **When** the view-mode toggle is inspected,
- **Then** the wrapper has `role="tablist"` and
  `aria-label="View mode"` (preserved from legacy),
- **And** the `Edit` button has `role="tab"`,
  `aria-selected="true"`, `tabindex="0"`,
- **And** the `Preview` button has `role="tab"`,
  `aria-selected="false"`, `tabindex="-1"`,
- **When** the user clicks `Preview`,
- **Then** `editMode` becomes `'preview'`,
- **And** the ARIA roles flip: `Preview` gets `aria-selected="true"`,
  `tabindex="0"`; `Edit` gets `aria-selected="false"`, `tabindex="-1"`,
- **And** keyboard Tab from the `Templates · 04` last card lands on
  the active tab (one tab-stop for the tablist per the ARIA APG tab
  pattern).

**Scenario 16b — JobAnalysis restyle (pills + collapse copy).**
- **Given** a saved resume with `job_analysis` populated:
  `required_skills: [{name: "Python", matched: true},
                     {name: "Kubernetes", matched: false}]`,
  `preferred_skills: [{name: "Rust", matched: true}]`,
  `experience_years: {required: 5, matched: true}`,
  `education: {required: "BSc CS", matched: false}`,
- **When** the page renders with the JobAnalysis card expanded
  (default state on mount),
- **Then** the card has an `.eyebrow` header reading
  `JOB · REQUIREMENTS` (NOT `Job Requirements`, NOT `Required
  Skills` in title-case),
- **And** the collapse toggle on the right is a `.btn-ghost` button
  with text content `Hide` (NOT `[+]` or `[-]` ASCII glyph),
- **And** Required-skills sub-header is an `.eyebrow` (not a raw
  `<h4>`),
- **And** the Python chip is rendered as `<span class="pill
  pill-positive">` containing the text `Python ✓`,
- **And** the Kubernetes chip is rendered as `<span class="pill
  pill-warn">` (NOT `.pill-negative`) containing `Kubernetes ✗`,
- **And** the Rust chip is `<span class="pill pill-positive">Rust ✓`,
- **And** the experience line shows
  `Experience: 5+ yrs` text followed by a `.pill.pill-positive`
  chip reading `✓` (or `Match ✓`),
- **And** the education line shows `Education: BSc CS` text
  followed by a `.pill.pill-warn` chip reading `✗`,
- **When** the user clicks the `Hide` toggle,
- **Then** the card body collapses (the existing `collapsed` state
  flips), the body content is hidden, and the toggle text flips to
  `Show`,
- **And** the legacy classes `.requirements-card`,
  `.requirements-header`, `.requirements-content`,
  `.requirement-section`, `.requirement-inline`,
  `.collapse-toggle`, `.match-indicator`, `.skill-tag.matched`,
  `.skill-tag.unmatched` are absent from the rendered DOM of the
  JobAnalysis component.

**Scenario 16c — JobAnalysis empty / null state.**
- **Given** a resume with `job_analysis: null` (LLM produced no
  analysis, or analysis failed),
- **When** the page renders,
- **Then** no JobAnalysis card is rendered at all — the existing
  `{#if jobAnalysis}` guard at `JobAnalysis.svelte:7` is preserved.
- **Given** a resume with `job_analysis: {}` (truthy but empty),
- **When** the page renders,
- **Then** the JobAnalysis card renders with the eyebrow header
  and the collapse toggle, but the body contains no skill chip
  clusters and no experience/education inline rows (each section
  guarded by `{#if jobAnalysis.X?.length > 0}` or
  `{#if jobAnalysis.X}` is preserved).

**Scenario 17 — Topbar unused store import dropped.**
- **Given** the current `src/components/Topbar.svelte` source after
  slice 3,
- **When** running `grep -n 'store' src/components/Topbar.svelte`
  before the slice,
- **Then** if `store` is imported but never referenced outside the
  import statement (no `store.*`, no `{store.foo}` interpolation),
- **And** the slice drops the import,
- **Then** post-slice the import is gone and the build still
  succeeds (`bun run build`).

**Scenario 18 — Existing tests pass.**
- **Given** the build succeeds (`bun run build`),
- **When** `pytest tests/` runs,
- **Then** every test passes without modification, with particular
  attention to: `tests/test_pdf_export.py`, `tests/test_pdf_api.py`,
  `tests/test_pdf_language.py`, `tests/test_resumes.py`,
  `tests/test_resume_*.py`, `tests/test_skills.py`,
  `tests/test_users.py`, `tests/test_work_experiences.py`,
  `tests/test_topbar_shell.py`, `tests/test_profile_editor_restyle.py`.

## Success criteria (verifiable)

- [ ] **Visual match.** Side-by-side screenshot of the rebuilt Resume
      preview screen and `design-bundle/project/screen-resume.jsx`
      shows the same 240px left rail with three groups (Templates ·
      Language · Sections), centered A4 page on paper-3 backdrop with
      soft drop shadow, page-meta eyebrow above, action button below.
      Right context aside intentionally absent (OUT for this slice).
- [ ] **Typography.** Computed style of the page header `.display`
      is Instrument Serif (or fallback `serif`); computed style of
      every `.eyebrow` element on the screen is JetBrains Mono (or
      fallback `monospace`) with `text-transform: uppercase` and
      `letter-spacing >= 0.10em`.
- [ ] **Match pill variant correct.** With `score >= 80`,
      `.pill-positive` renders; with `60 <= score < 80`,
      `.pill-warn`; with `score < 60`, `.pill-accent`. With null
      score, no pill renders.
- [ ] **Template switch works.** Clicking a non-active TemplateCard
      activates it (visual + `aria-pressed`), updates the screen
      preview's inner `pdf-preview template-…` class, and a
      subsequent Download PDF produces the matching template's PDF
      byte-identical to baseline.
- [ ] **Section toggle works from rail.** Clicking a left-rail
      Sections row fires `toggleSection(key)`, updates `resumeData`,
      re-renders the screen preview, and the legacy
      `[ON]/[OFF]` inline button is absent from the DOM.
- [ ] **Behaviour preservation.** Round-trip an edit in each of the
      six editorial sections (Identity is display-only — touch
      Summary text, Experience description, Education year, Skill
      rename, Language reorder, Project name); each change persists
      after page reload.
- [ ] **PDF byte-identity.** For each `(template, language)`
      combination (12 total), the downloaded PDF diffs zero bytes
      against a pre-slice baseline. `tests/test_pdf_*.py` returns
      zero regressions.
- [ ] **Legacy class sweep.** The grep in Scenario 15 returns zero
      matches outside the protected PDF zone.
- [ ] **Legacy token sweep.** The grep in Scenario 16 returns zero
      matches outside the protected PDF zone.
- [ ] **CHECKLIST promotion (MN-A).** The CHECKLIST file produced
      by `checklist-builder` mirrors every "Manual inspection"
      bullet from IMPL_PLAN as an explicit `[ ]` checkbox. The
      `plan-reviewer` agent verifies this 1:1 mapping.
- [ ] **Topbar import cleanup.** If the pre-slice grep over
      Topbar.svelte showed `store` imported-but-unused, the post-
      slice file has the import removed. Build still succeeds.
- [ ] **JobAnalysis restyle verifiable.** Required-skill chips are
      `.pill.pill-positive` (matched) / `.pill.pill-warn`
      (unmatched). Eyebrow header reads `JOB · REQUIREMENTS`.
      Collapse toggle is text `Hide` / `Show` on a `.btn-ghost`
      button. No `[+]` / `[-]` glyph remains. (Scenario 16b.)
- [ ] **Document outline clean.** Page renders one `<h1
      class="display">` (page heading) and exactly seven `<h2>`
      headings (EditorialSection blocks). Zero `<h3>` from the
      restyled components in Edit mode.

## Resolved decisions (no open questions remain)

1. **Right context aside (job sigil, MatchDonut, Stats, Suggested-
   next) — OUT.** Explicit per refined item; deferred to slice 6
   (tailor-cv-screen) or slice 7 (dashboard-screen). The match-
   summary (JobAnalysis card) stays in the main flow above the 3-col
   area as a card.

2. **Match-score representation — pill.** A `.pill` chip with
   `.pill-positive` / `.pill-warn` / `.pill-accent` variant keyed to
   the score band. Bands: `>= 80` → positive, `60–79` → warn, `< 60`
   → accent. Single pill, no donut. (Donut is reserved for the
   right-context-aside in slice 6/7.)

3. **Sections — Identity and Summary rendered but disabled.** Per
   refined item the Sections checkbox list shows seven rows
   (Identity, Summary, Experience, Education, Skills, Languages,
   Projects). The current `toggleSection()` handler only supports
   five keys (`work`, `skills`, `education`, `projects`,
   `languages`). Identity is a structural always-on header; Summary
   is editable but cannot be toggled off in the schema (there's no
   `included` flag on summary, just empty-vs-non-empty text). Rather
   than adding schema fields (OUT) or pretending these rows are
   togglable, render them visibly **disabled**: faint `var(--ink-4)`
   label, no checkbox click handler, `aria-disabled="true"`, with a
   tooltip explaining "Always shown when present". This keeps the
   design-source's seven-row list visible without lying about
   functionality.

4. **`ResumeSection.svelte` — delete.** Single consumer is
   `src/components/ResumeView.svelte` (verified by grep before
   writing this spec). After this slice, the consumer uses
   `EditorialSection.svelte` from slice 3 instead. If the grep
   during plan phase finds an unknown caller, the file stays put
   (only the import in `ResumeView` is removed).

5. **`TemplateSelector.svelte` — rewrite, not delete.** Keep the
   file (preserves the import contract `import TemplateSelector
   from './TemplateSelector.svelte'` and the `bind:selected` /
   `$bindable` interaction) but replace its body with the vertical
   `TemplateCard` stack. The four template IDs stay
   (`classic` / `modern` / `brussels` / `eu_classic`).

6. **Edit-mode + rail Sections coexistence.** The left rail Sections
   group is visible in both Edit and Preview modes. In Edit mode it
   acts as a global toggle that fires `toggleSection()` against
   `resumeData`; the section's `EditorialSection` block in the
   center pane either renders normally (when included) or renders a
   muted excluded-state hint. In Preview mode the same toggles drive
   the `<PdfPreview>` re-render (existing flow).

7. **Excluded-section visual in Edit mode.** When a section is
   `included === false`, its `EditorialSection` block in the center
   pane renders the header dimmed (`var(--ink-3)` instead of
   `var(--ink)` on both the section number and the title) and a
   small explanatory paragraph at the TOP of the section body
   BEFORE the existing content rows:
   `<p class="section-excluded">Hidden from resume — re-check
   {SectionName} in the left rail to include.</p>` (12px,
   `var(--ink-3)`, italic). The body content rows (work items,
   skills cluster, education list, etc.) still render below the
   paragraph so the editor never hides content — only marks it as
   "excluded from the next PDF". This preserves the slice 3 pattern
   and avoids the legacy `ResumeSection`'s "Section hidden from
   resume" copy living inside a fully-collapsed section body. The
   `EditorialSection.svelte` component does NOT need any new prop:
   the dimmed-header rendering and the section-excluded paragraph
   are added inside the consumer (`ResumeView.svelte`), keeping
   `EditorialSection` reusable for slice 3 and slice 4 unchanged.

8. **Summary placement.** Resolved → **own editorial section**.
   Summary lives in `EditorialSection № 02 Summary`, NOT inside the
   Identity card. Matches slice 3 conventions exactly. Scenario 10
   asserts this layout.

9. **Page heading level.** Resolved → **`<h1 class="display">`** for
   the page heading inside the header chrome (Must-have 2).
   `EditorialSection` blocks stay at `<h2>` (slice 3 component,
   verified at `EditorialSection.svelte:11`). One `<h1>` for the
   page, seven `<h2>` for the sections.

10. **JobAnalysis collapse copy.** The legacy `[+]` / `[-]` ASCII
    glyph is replaced with text: `Hide` / `Show` (right-aligned
    `.btn-ghost` with `font-size: 11px`). Avoids an extra Unicode
    character class in the editorial fonts and reads better in
    screen readers.

11. **Page-meta byte-count — deferred.** The design source shows
    `1 / 1 page · 612 KB` as a static placeholder. Surfacing the
    real byte count would require either generating the PDF on
    mount (perf regression) or instrumenting the download path
    (out of scope for a chrome restyle). The slice ships
    `A4 · 210 × 297` + `1 / 1 page` only, with no byte-count copy.
    Tracked as Compromise #1 below.

12. **`1 / 1 page` accuracy.** The screen preview is a single
    scrollable HTML block, not paginated. Showing `1 / 1 page` is
    a white lie that matches the design source's framing. A
    truly-accurate page count would require running weasyprint on
    every render — out of scope. Tracked as Compromise #2 below.

## Non-goals (reaffirmed from refined item)

- **PDF render path** — `templates/resume_base.css` and the four HTML
  templates fed to weasyprint. PDF byte-identity is a hard gate.
- **`<div class="pdf-preview template-…">` inner markup and its inline
  `<style>` block** in `src/components/PdfPreview.svelte`.
- **Unification of the two render paths** (shared CSS / iframe srcdoc /
  server preview endpoint). Deferred to its own slice.
- **`src/lib/resumeStore.svelte.js`** — no cross-component store needed.
  Existing prop + local `$state` flow inside `ResumeView` /
  `ResumeGenerator` is sufficient.
- **Live preview-language toggle** (EN / FR / NL button group from
  the design). Generation locks the language; live switching needs a
  generation-side rethink. Deferred.
- **Right-side context aside** (job sigil, MatchDonut, Stats grid,
  Suggested-next cards). Deferred to slice 6/7.
- **In-document editing UX changes** — inline editor behaviour
  (textareas, skill rename keybinds, drag-reorder semantics) stays as
  today. Chrome-only restyle.
- **Schema or API changes.**
- **Mobile / responsive layouts.** Defer until after slice 9. (The
  `flex-wrap: wrap` behavior in Must-have 3 is a graceful-degradation
  fallback driven purely by intrinsic widths — not a media query, not
  a designed mobile experience. Below the 1024px breakpoint the rail
  wraps above the pane; styling, font sizes, and copy are unchanged.)
- **Dark theme, sidebar nav, live tweaks panel, AI-augmentation
  affordances.** All initiative-wide OUT.

## Known compromises (deferred deliberately)

1. **Page-meta byte count absent.** The design source's `· 612 KB`
   copy is dropped from this slice. Surfacing the real PDF byte
   count needs either eager generation (perf) or download-path
   instrumentation (scope). Action owner: a future slice that
   touches the PDF download flow.

2. **`1 / 1 page` is a hard-coded white lie.** The screen preview is
   a single scrollable HTML div, not paginated. Real page count
   requires weasyprint server-side rendering. Action owner: the
   future "unify the two render paths" slice (deferred from refined
   item).

3. **Pre-existing drift between screen preview and exported PDF.**
   The screen `PdfPreview` duplicates the PDF's CSS in an inline
   `<style>` block. This slice does NOT close that drift; it just
   restyles the framing around it. Action owner: a future "unify
   the two render paths" slice with its own byte-identity gate.

## Dependencies & risk

- **Depends on:** slice 1 (editorial-design-system — tokens,
  primitives, fonts), slice 2 (topbar-shell — `container-wide` class,
  topbar), slice 3 (restyle-profile-editor — `EditorialSection.svelte`
  reusable, slice-3-pattern editor restyles for Identity/Experience/
  Skills/Education/Languages/Projects). All three shipped.
- **Risk — PDF byte-identity break.** Highest-priority risk. If any
  edit accidentally touches `templates/resume_base.css` or the four
  HTML templates or the inner `PdfPreview` `<style>` block, the PDF
  diff fails. Mitigation: explicit IMPL_PLAN list of "do NOT edit"
  files; explicit CHECKLIST checkbox to grep-diff those files
  before final commit.
- **Risk — `ResumeSection.svelte` deletion.** Verified: the only
  consumer is `ResumeView.svelte` (`grep -rn "ResumeSection"
  src/`). Safe to delete once `ResumeView.svelte` stops importing
  it. Re-verify in plan phase.
- **Risk — Section toggle key mismatch.** The current
  `toggleSection(section)` handler accepts five keys: `work`,
  `skills`, `education`, `projects`, `languages`. The left-rail
  Sections list shows seven rows including Identity and Summary —
  those two are rendered disabled (Decision 3) and DON'T call
  toggleSection. Plan must spell out the row-to-key mapping table.
- **Risk — Existing inline edit affordances getting lost in restyle.**
  The Edit mode currently has rich inline editing: summary draft,
  skill rename (Enter/Esc/`field-sizing: content`), skill exclude/
  include, profile-skill add, work drag-reorder, work description
  textarea. None of this behaviour changes; the restyle only swaps
  CSS classes and tokens. Plan must include a regression checklist
  bullet for each affordance.
- **Risk — Match-score band thresholds.** Spec sets `>= 80`,
  `60–79`, `< 60`. The current `getScoreClass()` helper in
  `ResumeView.svelte:125-129` uses the same bands. The match-pill
  picker should re-use the existing function (rename to
  `findMatchPillVariant(score)` per lean-code) — don't duplicate
  the band logic. Plan must capture this.
- **Risk — `JobAnalysis.svelte` collapse state.** The current
  component starts expanded (`collapsed = false`). Plan must
  preserve that; just restyle the toggle button copy and
  affordance.
- **Risk — Wide-container width premise.** Verified during analyze
  review: `src/styles/global.css:181-184` defines `.container-wide`
  as `{ max-width: none; padding: 0; }` — i.e., it removes both the
  800px cap and the section padding from the default `.container`.
  The resume layout's minimum useful width is 240px rail +
  `var(--d-gap)` (28px) + 600px page surface +
  `var(--d-gap)` (28px) container-edge padding inside the pane =
  ~900px. The viewport-bounded layout fits comfortably on any
  desktop ≥1024px. Below 1024px the rail wraps via `flex-wrap:
  wrap` (Must-have 3). Plan-phase action: confirm the rail+pane
  flex row sits inside a container that supplies its own
  horizontal padding (since `.container-wide` drops padding to 0),
  so the layout doesn't run flush against the viewport edges.
