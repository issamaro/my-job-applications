# UX_DESIGN — restyle-resume-preview

Date: 2026-05-13
Ceremony: M (full)
Slice: 4 of 9 — editorial redesign initiative

Source references:
- Design: `design-bundle/project/screen-resume.jsx`
- Tokens: `src/styles/global.css` (slice 1), `design-bundle/project/tokens.css`
- Prior art: `archive-v6/2026-05-13_restyle-profile-editor/1-analyze/ux/`

## Screens covered

One screen — the Resume preview screen rendered by
`src/components/ResumeView.svelte` and reached via `activeTab === 'resume'`
in `src/App.svelte`. The screen has two view modes (`Edit` / `Preview`)
which share the same chrome (page header + JobAnalysis + 3-col layout +
left rail) and swap only the content of the center pane.

## Overall page layout (success state)

```
┌──────────────────────────────────────────────────────────────────────┐
│ Topbar (slice 2, unchanged)                                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  .container.container-wide  (max-width: none; padding: 0)             │
│                                                                        │
│  ┌── Page header chrome ───────────────────────────────────────────┐  │
│  │ ← Back to Input           RESUME · FOR JOB             Regenerate│  │
│  │                  ── Senior Engineer · Linear ──                  │  │
│  │                  Generated May 10, 2026   [Match 87%]            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌── JobAnalysis card (.card) ────────────────────────────────────┐  │
│  │ JOB · REQUIREMENTS                                       Hide  │  │
│  │ ── Required skills ──                                          │  │
│  │ [Python ✓] [FastAPI ✓] [Kubernetes ✗] [GraphQL ✗]              │  │
│  │ ── Preferred skills ──                                         │  │
│  │ [Rust ✓] [WASM ✗]                                              │  │
│  │ Experience: 5+ yrs       [Match ✓]                             │  │
│  │ Education: BSc CS or higher    [Match ✓]                       │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌── 3-column area (flex row, gap: var(--d-gap)) ────────────────┐    │
│  │ ┌──────────────┐  ┌──────────────────────────────────────────┐│    │
│  │ │ Left rail    │  │ Center pane                              ││    │
│  │ │ (240px)      │  │ [Edit | Preview] tab toggle              ││    │
│  │ │              │  │                                          ││    │
│  │ │ TEMPLATES·04 │  │ {Edit-mode pane OR Preview-mode pane}    ││    │
│  │ │ ┌──────────┐ │  │                                          ││    │
│  │ │ │[mini]    │ │  │                                          ││    │
│  │ │ │Classic   │ │  │                                          ││    │
│  │ │ │● active  │ │  │                                          ││    │
│  │ │ └──────────┘ │  │                                          ││    │
│  │ │ ┌──────────┐ │  │                                          ││    │
│  │ │ │Modern    │ │  │                                          ││    │
│  │ │ └──────────┘ │  │                                          ││    │
│  │ │ Brussels …   │  │                                          ││    │
│  │ │ EU Classic … │  │                                          ││    │
│  │ │              │  │                                          ││    │
│  │ │ ── soft ──   │  │                                          ││    │
│  │ │ LANGUAGE     │  │                                          ││    │
│  │ │ [EN] (solid) │  │                                          ││    │
│  │ │              │  │                                          ││    │
│  │ │ ── soft ──   │  │                                          ││    │
│  │ │ SECTIONS     │  │                                          ││    │
│  │ │ ☐ Identity   │  │                                          ││    │
│  │ │ ☐ Summary    │  │                                          ││    │
│  │ │ ☑ Experience │  │                                          ││    │
│  │ │ ☑ Education  │  │                                          ││    │
│  │ │ ☑ Skills     │  │                                          ││    │
│  │ │ ☑ Languages  │  │                                          ││    │
│  │ │ ☐ Projects   │  │                                          ││    │
│  │ └──────────────┘  └──────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

## State 1 — Success / populated (Preview mode)

**Trigger:** user opens a saved resume, `resumeData !== null`, all sections
have entries, `editMode === 'preview'`, no in-flight `downloadPdf`.

**Visual hierarchy (top to bottom):**

1. **Page header chrome** (full container-wide width)
   - **Row 1 (flex, justify-between, align-center, margin-bottom 8px):**
     - Left: `.btn-ghost` containing `← Back to Input` (12px,
       `var(--ink-2)`, no underline).
     - Right: `.btn` containing `Regenerate` (13px, `var(--ink)`,
       paper background, rule border).
   - **Row 2 (flex column, align-center, gap 4px):**
     - `<span class="eyebrow" style="font-size: 11px;">RESUME ·
       FOR JOB</span>` (uppercase, mono, tracked 0.12em,
       `var(--ink-3)`).
     - `<h1 class="display" style="font-size: 32px; line-height:
       1.15; margin: 0;">Senior Engineer · Linear</h1>` (Instrument
       Serif, `var(--ink)`, single page-level heading).
     - Sub-line (flex row, gap 12px, baseline): `Generated May 10,
       2026` (12px, `var(--ink-3)`) and `<span class="pill
       pill-positive">Match 87%</span>`.

2. **JobAnalysis card** (`.card`, full container-wide width,
   padding `var(--d-pad)`, margin `var(--d-gap) 0`)
   - Header row: `.eyebrow` `JOB · REQUIREMENTS` left, `.btn-ghost`
     `Hide` right.
   - Required skills sub-header `.eyebrow` 12px `var(--ink-3)`.
   - Skill pills: each chip is `.pill` with variant
     `.pill-positive` (matched) or `.pill-warn` (unmatched). Glyph
     `✓` or `✗` appears in the chip text.
   - Same pattern for Preferred skills.
   - Experience and Education inline rows: `var(--ink-2)` label +
     `.pill-positive` or `.pill-warn` chip.

3. **3-column area** (flex row, gap `var(--d-gap)`)
   - **Left rail** (`<aside class="resume-rail">`, 240px,
     `border-right: 1px solid var(--rule)`, padding-right
     `var(--d-pad)`)
     - **Templates group:** `.eyebrow` `Templates · 04` (10px, mono,
       tracked, `var(--ink-3)`), then four `TemplateCard` buttons
       stacked vertically with `gap: 12px`. Each card: 10px padding,
       `var(--card)` background when active else `var(--paper-2)`,
       `1px solid var(--ink)` when active else `1px solid
       var(--rule)`, `var(--r-sm)` radius. Mini preview (90px tall)
       + name row + sub. Active marker `● active` right-aligned in
       the name row, `var(--accent)` 10px mono.
     - `<hr class="rule-soft" style="margin: 20px 0;">`
     - **Language group:** `.eyebrow` `Language`, then one
       `.pill.pill-solid` chip showing `resume.language.toUpperCase()`
       (`EN`/`FR`/`NL`), `cursor: default`, `aria-label`.
     - `<hr class="rule-soft" style="margin: 20px 0;">`
     - **Sections group:** `.eyebrow` `Sections`, then seven rows
       each a `<button type="button" class="rail-section-row">`. Row
       layout: 8px gap flex row, 14×14 checkbox glyph (`background:
       var(--ink)` filled when included, `transparent` with `1px
       solid var(--rule)` when excluded), 12px label
       (`var(--ink)` when checked, `var(--ink-3)` when unchecked,
       `var(--ink-4)` when disabled). Identity + Summary rows are
       `aria-disabled="true"`, no click handler, faint label.
   - **Center pane** (`<div class="resume-pane">`, flex 1, min-width 0)
     - **Tab toggle** (top of pane, margin-bottom `var(--d-gap)`):
       `<div class="resume-tabs" role="tablist">` containing two
       buttons. Active button styled `.btn` (paper-on-ink),
       inactive `.btn-ghost`. Both 12px font-size, 6px-12px padding.
     - **Preview-mode content** (this state):
       - Outer wrapper `<div class="resume-pane-preview">`:
         `background: var(--paper-3)`, padding 28px, flex column,
         align-center, gap 16px.
       - Page-meta eyebrow row (flex baseline, gap 12px):
         `<span class="eyebrow num">A4 · 210 × 297</span>` +
         `<span style="color: var(--ink-3); font-size: 11px;">1 / 1
         page</span>`.
       - Page surface `<div class="resume-page">`: width 600px,
         min-height 848px, `background: white`, drop-shadow stack
         (`0 1px 0 rgba(0,0,0,0.04), 0 24px 48px -16px
         rgba(0,0,0,0.18)`). Inside: `<PdfPreview {resumeData}
         template={selectedTemplate} language={...}/>` — inner
         `<div class="pdf-preview template-…">` markup byte-
         identical to pre-slice.
       - Action row (flex, gap 10px, justify-center):
         `<button class="btn btn-primary">Download PDF</button>`.

## State 2 — Success / populated (Edit mode)

**Trigger:** same as State 1 but `editMode === 'edit'`.

**Difference from State 1:** the center pane below the tab toggle is the
edit-mode pane (Identity card + numbered editorial sections), not the
paper-3 backdrop with the A4 page.

**Edit-mode pane layout:**

1. **Identity card** — wrapped in `<EditorialSection number="01"
   title="Identity">`. Body: a two-row block — line 1 is the full
   name (16px semibold, `var(--ink)`); lines 2 and 3 are contact
   lines (12px, `var(--ink-3)`, `email · phone` on line 2,
   `location · linkedin` on line 3 when present). No inline edit
   affordance — personal_info is read-only in this view today; the
   restyle preserves that. The legacy `.personal-info-preview`,
   `.contact-line` classes are dropped.

2. **EditorialSection blocks** (re-using slice 3's
   `EditorialSection.svelte`, in this order):
   - `№ 02 Summary` — separate section, NOT inside the Identity
     card. Body holds the existing summary editor flow: if
     `editingSummary === true`, render a `.textarea`-primitive
     control bound to `summaryDraft` with Save / Cancel
     `.btn-ghost` buttons; else render the summary text (13px,
     `var(--ink)`, `line-height: 1.5`) followed by an `Edit`
     `.btn-ghost` link (11px). The empty case (no summary text)
     renders an `Add summary` `.btn-ghost` only. All existing
     keybinds preserved (Cmd/Ctrl+Enter to save, Esc to cancel).
     The legacy `.summary-edit`, `.summary-footer`,
     `.summary-add-btn` classes are dropped.
   - `№ 03 Experience` — count = `resumeData.work_experiences.length`.
     Work timeline: 3-column grid per row (`110px 1fr auto`, gap
     18px, padding `12px 0`). Left rail: mono dates
     (`formatWorkDate(start_date)`, em-dash `var(--ink-4)`,
     `formatWorkDate(end_date)` or `Present`). Middle: drag handle
     `⋮⋮` + `{title} · {company}` semibold 14px (company in
     `var(--ink-3)` weight 400) + `var(--ink-2)` 13px description.
     If `editingId === exp.id`, inline textarea + Save/Cancel
     buttons replace the description. Right: `.btn-ghost` `Edit` /
     `Save` indicator.
   - `№ 04 Education` — count =
     `resumeData.education.length`. 3-column grid (`70px 1fr auto`).
     Mono year, degree+field+institution middle, `.btn-ghost` Edit
     right.
   - `№ 05 Skills` — count =
     `resumeData.skills.length`. Pill cluster: each skill is
     `.pill`; matched skills carry `.pill-positive`; the existing
     rename/exclude affordances live inside the chip. Available
     skills row below (dashed `.pill` for one-click add). All inline
     editing behaviour preserved verbatim.
   - `№ 06 Languages` — count =
     `resumeData.languages.length`. 2-column grid of language cards
     (name + level + CEFR code) matching slice 3 pattern.
   - `№ 07 Projects` — count =
     `resumeData.projects.length`. 2-column grid (`1fr auto`).

## State 3 — Initial load / `resumeData === null`

**Trigger:** the user navigates to `activeTab === 'resume'`, the
`ResumeGenerator` parent has just rendered `<ResumeView resume={…}/>`,
but `ResumeView`'s `$effect` to populate `resumeData` from `resume.resume`
hasn't run yet (one tick).

**Visual:** the page header chrome and JobAnalysis card render fine
(they read from `resume.*` props, not `resumeData`). The 3-col area
renders the left rail (Templates + Language + Sections show a
"loading" empty state) and the center pane shows an inline skeleton.

**Empty-state copy:**
- Sections checkboxes: render the 7 rows with `aria-disabled="true"`
  and checkbox glyph in the indeterminate state (a 2px-thick
  `var(--rule)` horizontal bar instead of a fill/empty).
- Center pane (Edit mode): `<p class="loading-note">Loading
  resume…</p>` (`var(--ink-3)`, 13px, centered).
- Center pane (Preview mode): the paper-3 backdrop renders, the
  page surface renders empty white, the page-meta eyebrow renders
  with no byte count.

**Realistic likelihood:** very brief (one Svelte microtask). In
practice users will not see this state long. The skeleton is a
fallback against a slow Svelte 5 effect.

## State 4 — Empty data sub-states (rare)

**Resume with no work_experiences** (e.g., student CV the LLM didn't
populate):
- The Experience section in Edit mode renders the count `0` and a
  small note `<p class="empty-note">No experiences added.</p>` (13px,
  `var(--ink-3)`, italic). The PdfPreview's Experience section
  renders empty per its existing logic.
- The left rail Sections checkbox for Experience renders
  enabled but with a faint label since toggling a 0-entry section is
  cosmetically pointless. **Decision: keep enabled, no special-case
  — toggling a 0-entry section is harmless.**

**Resume with no skills / no education / no projects / no languages:**
Same pattern. Empty count, empty-note inside the editor section,
checkbox stays enabled.

**Resume with `match_score === null` or `match_score === undefined`:**
The match pill is absent from the page header (Scenario 3). No
fallback copy. The score reading is silent rather than `Match —`.

**Resume with `language` missing:** Defaults to `en` per the existing
`resume.language || 'en'` pattern. The Language group's pill shows
`EN`.

**Resume with `job_analysis === null`:** The JobAnalysis card is not
rendered at all (the existing `{#if jobAnalysis}` guard at
`JobAnalysis.svelte:7` is preserved). The 3-col area starts
immediately below the page header chrome with no gap from the
missing card. No empty-state copy surfaces.

**Resume with `job_analysis === {}` (truthy but empty):** The
JobAnalysis card renders the eyebrow header and the `Hide` /
`Show` toggle, but the body contains no skill-chip clusters and no
inline experience/education rows (each interior section guarded by
`{#if jobAnalysis.X?.length > 0}` or `{#if jobAnalysis.X}` is
preserved). The card visually reads as "empty job analysis".

## State 5 — Saving / loading sub-states

**Inline edit save in flight (`saving === true`):**
- The Save button's label flips to `Saving…` per existing flow.
- The button's appearance: `.btn-primary` with `opacity: 0.6,
  cursor: not-allowed`.

**Skill rename / skill exclusion / skill add in flight
(`savingSkillIndex !== null` or `savingProfileSkillName !== null`):**
- The affected skill pill renders with `opacity: 0.5, pointer-events:
  none` (preserved from legacy `.saving-skill` class, now applied
  via class binding on the `.pill` chip).

**Download PDF in flight (`isExporting === true`):**
- The `Download PDF` button label flips to `Generating…` per
  existing flow. `aria-live="polite"` preserved.
- Button styling: `.btn-primary` with `opacity: 0.6, cursor:
  not-allowed`.

## State 6 — Error sub-states

**Save error (any inline-edit save fails):**
- Toast component renders with `type="error"` and the message:
  - Summary save: `"Could not save summary. Try again."`
  - Skill save / rename / inclusion / add: `"Could not save skills.
    Try again."`
  - Work description save: console.error only (no toast — preserved
    from legacy).
  - Drag reorder save: `"Could not save order. Reverting."`
- The Toast component is rendered by `<Toast>` at the bottom of
  `ResumeView`'s template, unchanged in placement.
- The local `resumeData` is reverted to the last known good state
  (existing pattern).

**Download PDF error:**
- Toast: `type="error"`, message either
  `"Could not generate PDF. Please try again."` or
  `"PDF download failed: {error.message}"` (preserved from legacy
  catch handler in `handleDownloadPdf`).
- The center pane keeps the Preview mode chrome; only the toast
  surfaces the error.

**Network / API loss (e.g., `updateResume` rejects with no message):**
- Same pattern — Toast in `error` type with a generic message.

**Empty resume edge case (`resume === undefined` or null when
`ResumeView` renders):**
- This is a parent-component contract violation (ResumeGenerator
  should not render `<ResumeView/>` without a `resume`). Out of
  scope for this slice; if it happens, the page header chrome
  shows `Untitled · Unknown` (preserved from existing
  `resume.job_title || 'Untitled'` pattern).

## Accessibility notes

1. **Semantic outline.** The Resume preview's page heading is an
   `<h1 class="display">` (carrying `{job_title} · {company_name}`).
   `EditorialSection` blocks render `<h2 class="display
   editorial-section-title">` per slice 3 (verified at
   `src/components/EditorialSection.svelte:11`), giving the page a
   single `<h1>` followed by seven `<h2>` section headings. The
   Topbar does not render any `<h*>` element (verified — slice 2
   uses `<header>` semantics only), so there is no h1/h2 collision
   with topbar landmarks.

2. **`aria-pressed` on TemplateCard.** Each `TemplateCard` button
   carries `aria-pressed={template.id === selected}`.

3. **`aria-selected` on view-mode tabs.** The Edit/Preview tab
   buttons carry `role="tab"` and `aria-selected={editMode === '…'}`.
   The wrapper carries `role="tablist"` and `aria-label="View mode"`
   (preserved from legacy).

4. **`aria-pressed` on Sections checkbox rows.** Each rail-section-row
   button carries `aria-pressed={included}` so screen readers
   announce "Experience, pressed" / "not pressed".

5. **`aria-disabled` on Identity/Summary Sections rows.** Those two
   rows are visually disabled and announce as
   `Identity, dimmed, not interactive` via `aria-disabled="true"`
   and `tabindex="-1"` (NOT removed from tab order entirely — the
   row remains a button to maintain DOM stability).

6. **Language pill `aria-label`.** The locked language pill carries
   `aria-label="Resume language: English (locked)"` (or French /
   Dutch).

7. **Match pill `aria-label`.** The match pill carries
   `aria-label="Match score: 87 percent, strong fit"` (or "moderate
   fit" / "weak fit" per band).

8. **Focus order.** Tab key order top-to-bottom, left-to-right:
   - `← Back` button
   - `Regenerate` button
   - JobAnalysis `Hide`/`Show` toggle
   - JobAnalysis skill chips (if focusable — currently `<span>`s,
     NOT focusable; preserved)
   - Tab toggle: `Edit` then `Preview`
   - Left rail: TemplateCard buttons (Classic → EU Classic), then
     Sections rows (Identity → Projects)
   - Center pane: edit affordances (textareas, buttons, drag handles)
   - Action row: `Download PDF`
   - (Toast is `aria-live="polite"`, not in tab order)

9. **Keyboard activation.**
   - TemplateCard: Space/Enter activates select.
   - Sections checkbox row: Space/Enter toggles section.
   - Tab buttons: Space/Enter switches view mode. Left/Right arrow
     navigation between tabs is NOT implemented (preserved from
     legacy — could be a follow-up).
   - Inline summary edit: Esc cancels, Cmd+Enter saves (preserved).
   - Inline skill rename: Esc cancels, Enter saves (preserved).
   - Drag-reorder: keyboard alternative NOT implemented (legacy
     limitation, out of scope here).

10. **Focus-visible outline.** Every interactive element receives a
    `:focus-visible` outline of `2px solid var(--accent)` with `2px`
    offset. This closes slice 1's compromise #2 (`:focus-visible`
    not defined) for the Resume preview screen. Specifically applies
    to: `.btn`, `.btn-ghost`, `.btn-primary`, `.pill` (only when
    interactive), TemplateCard, rail-section-row, JobAnalysis toggle,
    tab buttons, all inputs/textareas.

11. **Color contrast.** All text colors checked against background
    colors in the rendered design:
    - `var(--ink)` on `var(--paper)` — slice 1 verified > 7:1.
    - `var(--ink-2)` on `var(--paper)` — slice 1 verified > 4.5:1.
    - `var(--ink-3)` on `var(--paper)` — slice 1 verified > 3:1 for
      11+px text (caption tier).
    - `var(--ink-4)` (disabled labels) on `var(--paper)` — > 3:1
      via slice 1 token; explicitly NOT used for non-disabled body
      text.
    - `.pill-positive`, `.pill-warn`, `.pill-accent` text on their
      soft backgrounds — slice 1 verified > 4.5:1 in cobalt re-skin.
    - `var(--accent)` text on `var(--paper)` — > 4.5:1 (cobalt
      `oklch(0.56 0.24 265)` on white).

12. **Screen-reader hints for the page-meta eyebrow.** The
    `A4 · 210 × 297` and `1 / 1 page` text is decorative metadata;
    `aria-hidden="true"` would silence it but might surprise users
    who navigate by landmark. Decision: leave audible (no
    `aria-hidden`).

## Keyboard navigation map

```
Tab order:
  1.  ← Back to Input (header chrome)
  2.  Regenerate (header chrome)
  3.  JobAnalysis Hide/Show (when expanded)
  4.  Edit tab
  5.  Preview tab
  6–9.   TemplateCards (Classic, Modern, Brussels, EU Classic)
  10. Language pill — NOT focusable (cursor: default, no tabindex)
  11–17. Sections rows (Identity → Projects). Identity/Summary
         tab-stop receives focus but Space/Enter does nothing
         (aria-disabled).
  18+. Center pane content (Edit mode: every inline editor; Preview
        mode: Download PDF only).

Activation:
  - Space/Enter on TemplateCard → bind:selected
  - Space/Enter on Sections row → toggleSection(key) (skipped on
    Identity/Summary)
  - Space/Enter on tab → editMode = 'edit'|'preview'
  - Enter on rename input → writeSkillRename
  - Esc on rename input → cancelEditSkill
  - Cmd/Ctrl+Enter on summary textarea → writeSummaryEdit
  - Esc on summary textarea → cancelEditSummary
```

## Empty / loading / error state copy summary

| State | Copy | Location |
|-------|------|---------|
| Loading resume (≤1 tick) | `Loading resume…` | center pane, italic, var(--ink-3) |
| No work_experiences | `No experiences added.` | inside `№ 03 Experience` body |
| No skills | `No skills.` (legacy `.empty-note` copy preserved) | inside `№ 05 Skills` body |
| No projects | `No projects.` | inside `№ 07 Projects` body |
| No languages | (section hidden — preserved from legacy `{#if resumeData.languages?.length > 0}` guard) | n/a |
| Match score null | (no pill rendered) | n/a |
| `job_analysis` null | (JobAnalysis card not rendered) | n/a |
| `job_analysis` empty `{}` | eyebrow + toggle only, no body sections | JobAnalysis card |
| Section toggled off (Edit mode) | `Hidden from resume — re-check {Section} in the left rail to include.` | inside affected `EditorialSection` body, before content |
| Save error — summary | `Could not save summary. Try again.` | Toast bottom |
| Save error — skills | `Could not save skills. Try again.` | Toast bottom |
| Save error — drag order | `Could not save order. Reverting.` | Toast bottom |
| Save success — generic | `Saved` | Toast bottom |
| Save success — drag order | `Order saved` | Toast bottom |
| Save success — PDF | `PDF downloaded` | Toast bottom |
| Download error | `Could not generate PDF. Please try again.` (or `PDF download failed: {msg}`) | Toast bottom |
| Saving inline edit | `Saving…` | button label, opacity 0.6 |
| Generating PDF | `Generating…` | Download PDF button label |

## Visual tokens used (from `src/styles/global.css`)

- **Backgrounds:** `--paper`, `--paper-2` (raised), `--paper-3`
  (preview backdrop), `--card`.
- **Text:** `--ink`, `--ink-2`, `--ink-3`, `--ink-4`.
- **Borders:** `--rule`, `--rule-soft`.
- **Accents:** `--accent` (cobalt), `--accent-soft`.
- **Status:** `--positive`, `--positive-soft`, `--warn`, `--warn-soft`,
  `--negative`, `--negative-soft`.
- **Radii:** `--r-sm`.
- **Spacing:** `--d-pad`, `--d-gap`, `--d-row`.
- **Fonts:** `--font-display` (Instrument Serif), `--font-mono`
  (JetBrains Mono).

Zero references to legacy tokens (`--color-*`, `--spacing-*`).
