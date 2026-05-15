# IMPL_PLAN — restyle-resume-preview

Date: 2026-05-13
Ceremony: M (full)
Slice: 4 of 9 — editorial redesign initiative
References:
- `workbench/1-analyze/spec/FEATURE_SPEC_2026-05-13_restyle-resume-preview.md`
- `workbench/1-analyze/ux/UX_DESIGN_2026-05-13_restyle-resume-preview.md`
- `workbench/2-plan/research/SVELTE5_BINDABLE_NOTES_2026-05-13_restyle-resume-preview.md`
- `workbench/2-plan/research/SVELTE5_NOTES_2026-05-13_restyle-resume-preview.md`
- `design-bundle/project/screen-resume.jsx`
- Slice 3 baseline: `archive/2026-05-13_restyle-profile-editor/`

## Architecture summary

Rebuild the chrome around the Resume preview screen using editorial primitives
shipped by slices 1–3. Five source files are edited, one is rewritten in place,
one is deleted. **Three protected zones** are NOT edited under any
circumstance: `templates/resume_base.css`, the four
`templates/resume_*.html` files, and the inner `<div class="pdf-preview
template-…">` markup plus inline `<style>` block inside
`src/components/PdfPreview.svelte`. PDF byte-identity (Must-have 12) is the
hard gate; every other change in this plan is subordinate to it.

Layout reform: `App.svelte` opts the resume tab into `.container-wide` (slice 3
precedent for profile). `ResumeView.svelte` becomes a three-zone composition —
page-header chrome + JobAnalysis card + flex row with a 240px left rail and a
flex-1 center pane. The left rail centralises Templates (vertical `TemplateCard`
stack), Language (read-only pill), and Sections (checkbox list that replaces
each section's inline `[ON]/[OFF]` toggle). The center pane keeps the Edit /
Preview tab toggle, restyled as a paper-on-ink segmented control with the ARIA
APG tab semantics from Scenario 15b. Preview mode wraps `<PdfPreview/>` in a
white A4-ratio surface on a paper-3 backdrop. Edit mode replaces every
`ResumeSection` call with a slice-3 `EditorialSection`, swaps legacy `.skill-
tag` / `.work-item` / `.preview-*` classes for editorial primitives, and
preserves every inline-edit behaviour (summary draft, skill rename, skill
exclude/include, profile-skill add, work drag-reorder, work description edit)
verbatim.

Two side-effects ride along: `TemplateSelector.svelte` is rewritten (NOT
deleted — the import contract and `bind:selected` `$bindable` interaction stay)
to render four vertical `TemplateCard` buttons; `ResumeSection.svelte` is
deleted (single consumer); `JobAnalysis.svelte` is restyled in place;
`Topbar.svelte`'s unused `store` import is dropped (slice 3 carryover).

No new libraries. Svelte 5 runes (`$state`, `$props`, `$bindable`, `$effect`,
`$derived`) only. Tab pattern follows W3C ARIA APG (`role="tablist"`,
`role="tab"`, `aria-selected`, `tabindex` flip).

## Files to MODIFY

### 1. `src/App.svelte` — extend `.container-wide` to resume tab (1 line)

**Lean-code header:** already present (slice 2 wrote it). Scope line stays.

**Edit at line 26:**

```diff
- <div class="container" class:container-wide={activeTab === 'profile'}>
+ <div class="container" class:container-wide={activeTab === 'profile' || activeTab === 'resume'}>
```

**Why:** the existing 800px `.container` cap can't seat a 240px rail + 28px
gap + 600px A4 page surface + container-edge padding (~900px minimum useful
width). `.container-wide` resolves to `max-width: none; padding: 0` per
`src/styles/global.css:181-184`. Slice 3 used the same opt-out for profile.

**Maps to:** FEATURE_SPEC Must-have 1, Scenario 4b.

### 2. `src/components/Topbar.svelte` — drop unused `store` import (1 line)

**Edit at line 5:**

```diff
- import { store, readInitials, readProfile } from '../lib/profileStore.svelte.js';
+ import { readInitials, readProfile } from '../lib/profileStore.svelte.js';
```

**Pre-edit verification:** `grep -nE "\bstore\b" src/components/Topbar.svelte`
returns exactly one match (line 5, the import). If a second match appears
(future-proofing not done in this slice), leave the import alone and note in
retro.

**Maps to:** FEATURE_SPEC Must-have 14, Scenario 17.

### 3. `src/components/TemplateSelector.svelte` — rewrite body, keep contract

**Lean-code header:** add at top (file currently has no header):

```svelte
<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Vertical stack of TemplateCard buttons bound to the resume's selected template. -->
```

**Script section:** keep the four-template array, keep `$bindable`. Extend
each template with a `sub` string for the secondary label:

```svelte
<script>
  let { selected = $bindable('classic') } = $props();

  const templates = [
    { id: 'classic',    name: 'Classic',    sub: 'Serif · centered' },
    { id: 'modern',     name: 'Modern',     sub: 'Sans · accent rule' },
    { id: 'brussels',   name: 'Brussels',   sub: 'Two-column · photo' },
    { id: 'eu_classic', name: 'EU Classic', sub: 'Serif · header bar' }
  ];

  function updateSelected(id) {
    selected = id;
  }
</script>
```

**Template body:** replace the `<select>` with a vertical stack of four
`<button class="template-card">` elements. Each carries `aria-pressed` and
fires `updateSelected(template.id)` on click. Inside each button: a
CSS-rendered mini preview block (`<div class="template-card-mini">` — three
horizontal rule strokes in `var(--ink)` and `var(--rule-soft)`, decorative),
a flex row with name (12px semibold) on the left and an `<span class="num">●
active</span>` marker on the right when active, then a sub-line in
`var(--ink-3)` at 10px. Outer wrapper: a flex column with `gap: 12px`. No
group eyebrow — the rail consumer (`ResumeView`) renders the
`Templates · 04` eyebrow above this component.

**Style block:** drop all legacy classes (`.template-selector`,
`.template-label`, `.template-dropdown` and any colour hex literals). Replace
with `.template-card`, `.template-card-mini`, `.template-card-name`,
`.template-card-sub`, `.template-card-active` rules. All values pulled from
editorial tokens (`var(--paper-2)`, `var(--card)`, `var(--ink)`,
`var(--rule)`, `var(--ink-3)`, `var(--accent)`, `var(--r-sm)`). Active card:
`background: var(--card)`, `border: 1px solid var(--ink)`. Inactive:
`background: var(--paper-2)`, `border: 1px solid var(--rule)`. Padding 12px
to keep the 4px grid (the design source uses 10px; 12px lands on rhythm with
`.card` and `.pill`).

**Lean-code function names:** only `updateSelected` (verb prefix, ≤3 words
after verb). The component body is a pure render — no other functions.

**Maps to:** Must-haves 5a, 6; Scenarios 5, 6.

### 4. `src/components/JobAnalysis.svelte` — restyle in place

**Lean-code header:** add at top.

```svelte
<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Job requirements card — skill match pills and inline experience/education rows. -->
```

**Script section:** unchanged. `let { jobAnalysis = null } = $props()`, `let
collapsed = $state(false)`. The existing `{#if jobAnalysis}` guard at line 7
stays — drives Scenario 16c (null guard).

**Template body:** rebuild around `.card` primitive. Outer wrapper becomes
`<div class="card resume-job-analysis">`. Header row: an `.eyebrow` span
reading `JOB · REQUIREMENTS` on the left, a `<button class="btn-ghost">`
reading `{collapsed ? 'Show' : 'Hide'}` on the right with
`aria-expanded={!collapsed}`. Required/Preferred skill sub-headers swap
`<h4>` to `<span class="eyebrow">` (drops the `<h4>` from the document
outline — UX a11y note 1 keeps the page outline clean: one `<h1>` + seven
`<h2>`). Skill chip wrappers: `<span class="pill {skill.matched ? 'pill-
positive' : 'pill-warn'}">{skill.name} {skill.matched ? '✓' : '✗'}</span>`.
Experience/education inline rows: `<div class="resume-job-analysis-inline">`
with a `var(--ink-2)` label span + a `.pill.pill-positive` or `.pill.pill-
warn` chip carrying the `✓` / `✗` glyph.

**Style block:** drop every legacy class (`.requirements-card`,
`.requirements-header`, `.requirements-content`, `.requirement-section`,
`.requirement-inline`, `.collapse-toggle`, `.skill-tags`, `.skill-tag`,
`.skill-tag.matched`, `.skill-tag.unmatched`, `.match-indicator`). Replace
with `.resume-job-analysis` (small layout offsets only; `.card` does the
heavy lifting), `.resume-job-analysis-inline` (flex row, gap 8px,
align-items baseline). Zero references to `--color-border`,
`--color-primary-rgb`, `--color-text-rgb`, `--color-success`,
`--color-success-rgb`, `--color-error`, `--color-error-rgb`. All margins
swap to `var(--d-pad)`, `var(--d-gap)`, `var(--d-row)`, or 4px increments.

**Maps to:** Must-have 4, Scenarios 16b, 16c.

### 5. `src/components/ResumeView.svelte` — big restyle (1046 → ~850 LoC est.)

This is the load-bearing change. The script section keeps every existing
state variable and handler. The template is rebuilt zone-by-zone. The style
block is replaced wholesale.

**Lean-code header:** add at top.

```svelte
<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Resume preview screen — editorial chrome, left rail, Edit/Preview pane. -->
```

**Script changes (additive, non-breaking):**

5a. Drop the `JobAnalysis`-line `ResumeSection` import:

```diff
-  import ResumeSection from './ResumeSection.svelte';
+  import EditorialSection from './EditorialSection.svelte';
```

5b. Rename helpers to lean-code verbs and reduce the band logic to one
function:

```diff
-  function getScoreClass(score) {
-    if (score >= 80) return 'score-high';
-    if (score >= 60) return 'score-medium';
-    return 'score-low';
-  }
+  function findMatchPillVariant(score) {
+    if (score == null) return null;
+    if (score >= 80) return 'pill-positive';
+    if (score >= 60) return 'pill-warn';
+    return 'pill-accent';
+  }
+
+  function findMatchAriaLabel(score) {
+    if (score == null) return null;
+    if (score >= 80) return `Match score: ${Math.round(score)} percent, strong fit`;
+    if (score >= 60) return `Match score: ${Math.round(score)} percent, moderate fit`;
+    return `Match score: ${Math.round(score)} percent, weak fit`;
+  }
+
+  const languageLockedLabels = {
+    en: 'Resume language: English (locked)',
+    fr: 'Resume language: French (locked)',
+    nl: 'Resume language: Dutch (locked)'
+  };
+
+  let sectionRows = $derived.by(() => {
+    if (!resumeData) return [];
+    const work = resumeData.work_experiences?.[0]?.included !== false;
+    const skills = !resumeData.skills?.every(s => s.included === false);
+    const edu = resumeData.education?.[0]?.included !== false;
+    const langs = resumeData.languages?.[0]?.included !== false;
+    const projs = resumeData.projects?.[0]?.included === true;
+    return [
+      { key: null,         label: 'Identity',   included: true,   disabled: true  },
+      { key: null,         label: 'Summary',    included: true,   disabled: true  },
+      { key: 'work',       label: 'Experience', included: work,   disabled: false },
+      { key: 'education',  label: 'Education',  included: edu,    disabled: false },
+      { key: 'skills',     label: 'Skills',     included: skills, disabled: false },
+      { key: 'languages',  label: 'Languages',  included: langs,  disabled: false },
+      { key: 'projects',   label: 'Projects',   included: projs,  disabled: false }
+    ];
+  });
+
+  function readSectionAriaLabel(row) {
+    if (row.disabled) return `${row.label} — always shown`;
+    return `${row.label} — ${row.included ? 'included' : 'excluded'}`;
+  }
+
+  function updateSectionFromRail(row) {
+    if (row.disabled || !row.key) return;
+    toggleSection(row.key);
+  }
```

`getScoreClass` is deleted (single old caller line 372). All new helpers use
the lean-code verb-prefix conventions (`find*`, `read*`, `update*`).

5c. Preserve every existing handler verbatim: `toggleSection`,
`writeSummaryEdit`, `writeSkillRename`, `updateSkillInclusion`,
`createSkillFromProfile`, `updateDraggedIndex`, `updateOrderOnHover`,
`writeReorderedOrder`, `deleteDraggedIndex`, `handleDownloadPdf`,
`readSummaryKey`, `readSkillKey`, `startEdit`, `saveEdit`, `cancelEdit`,
`startEditSummary`, `cancelEditSummary`, `startEditSkill`, `cancelEditSkill`,
`readProfileSkills`. Same names (already lean-code compliant for verb
prefixes — `handleDownloadPdf` violates "no handle"; rename to
`writeDownloadedPdf`). See risk-5 below.

Actually: `handleDownloadPdf` IS in the forbidden-pattern table (handleX).
Rename to `writeDownloadedPdf` (the operation writes a PDF to the user's
download folder). Update its single callsite. Risk-5 below tracks the
contract.

**Template changes (full restructure):**

5d. **Top-level wrapper** `<div class="resume-preview">` stays. The
existing `<hr>` between header and JobAnalysis goes away (the editorial
pattern uses `.card` boundaries, not horizontal rules). The single inner
`<hr>` before the Edit/Preview toggle also goes away.

5e. **Page header chrome** replaces lines 367–385. New structure:

```svelte
<header class="resume-page-header">
  <button class="btn-ghost" type="button" onclick={onBack} aria-label="Back to job input">
    ← Back to Input
  </button>
  <div class="resume-page-title">
    <span class="eyebrow">RESUME · FOR JOB</span>
    <h1 class="display">{resume.job_title || 'Untitled'} · {resume.company_name || 'Unknown'}</h1>
    <div class="resume-page-meta">
      <span>Generated {formatDate(resume.created_at)}</span>
      {#if resume.match_score != null}
        <span class="pill {findMatchPillVariant(resume.match_score)}" aria-label={findMatchAriaLabel(resume.match_score)}>
          Match {Math.round(resume.match_score)}%
        </span>
      {/if}
    </div>
  </div>
  <button class="btn" type="button" onclick={onRegenerate}>Regenerate</button>
</header>
```

The `.resume-page-meta` row holds `Generated {date}` and the match pill side
by side, baseline-aligned, gap 12px. The pill is omitted when
`match_score == null` (Scenario 3).

5f. **JobAnalysis card** keeps the existing position (just below the
header) and the existing `<JobAnalysis jobAnalysis={resume.job_analysis}/>`
invocation. No wrapper added — the component now renders its own
`.card`-classed div internally (modification 4).

5g. **3-column area** replaces lines 393–432 and lines 433–656 (the entire
view-mode container + edit/preview content + bottom action row). New
structure:

```svelte
<div class="resume-3col">
  <aside class="resume-rail" aria-label="Resume controls">
    <div class="resume-rail-group">
      <span class="eyebrow">Templates · 04</span>
      <TemplateSelector bind:selected={selectedTemplate} />
    </div>

    <hr class="rule-soft" />

    <div class="resume-rail-group">
      <span class="eyebrow">Language</span>
      <span
        class="pill pill-solid"
        aria-label={languageLockedLabels[resume?.language || 'en']}
      >{(resume?.language || 'en').toUpperCase()}</span>
    </div>

    <hr class="rule-soft" />

    <div class="resume-rail-group">
      <span class="eyebrow">Sections</span>
      <div class="resume-rail-sections">
        {#each sectionRows as row (row.label)}
          <button
            type="button"
            class="rail-section-row"
            class:disabled={row.disabled}
            class:included={row.included && !row.disabled}
            aria-pressed={row.disabled ? undefined : row.included}
            aria-disabled={row.disabled ? 'true' : undefined}
            aria-label={readSectionAriaLabel(row)}
            tabindex={row.disabled ? -1 : 0}
            onclick={() => updateSectionFromRail(row)}
          >
            <span class="rail-section-checkbox" aria-hidden="true"></span>
            <span class="rail-section-label">{row.label}</span>
          </button>
        {/each}
      </div>
    </div>
  </aside>

  <div class="resume-pane">
    <div class="resume-tabs" role="tablist" aria-label="View mode">
      <button
        type="button"
        class:btn={editMode === 'edit'}
        class:btn-ghost={editMode !== 'edit'}
        role="tab"
        aria-selected={editMode === 'edit'}
        tabindex={editMode === 'edit' ? 0 : -1}
        onclick={() => editMode = 'edit'}
      >Edit</button>
      <button
        type="button"
        class:btn={editMode === 'preview'}
        class:btn-ghost={editMode !== 'preview'}
        role="tab"
        aria-selected={editMode === 'preview'}
        tabindex={editMode === 'preview' ? 0 : -1}
        onclick={() => editMode = 'preview'}
      >Preview</button>
    </div>

    {#if editMode === 'preview'}
      <!-- preview-mode pane (5h below) -->
    {:else}
      <!-- edit-mode pane (5i below) -->
    {/if}
  </div>
</div>
```

5h. **Preview-mode pane** (replaces the legacy `.preview-controls` block):

```svelte
<div class="resume-pane-preview">
  <div class="resume-page-meta-eyebrow">
    <span class="eyebrow num">A4 · 210 × 297</span>
    <span class="resume-page-count">1 / 1 page</span>
  </div>
  <div class="resume-page">
    <PdfPreview {resumeData} template={selectedTemplate} language={resume?.language || 'en'} />
  </div>
  <div class="resume-pane-actions">
    <button
      type="button"
      class="btn btn-primary"
      onclick={writeDownloadedPdf}
      disabled={isExporting}
      aria-live="polite"
    >
      {isExporting ? 'Generating…' : 'Download PDF'}
    </button>
  </div>
</div>
```

Page-meta eyebrow has zero behaviour; `.resume-page-count` is the static `1 /
1 page` text with `font-size: 11px; color: var(--ink-3)`. The `<PdfPreview/>`
call is byte-identical to today — same props order, same names. The page
surface (`<div class="resume-page">`) is 600px × 848px with white background
and the two-shadow stack.

5i. **Edit-mode pane** rebuilds the entire content. Identity card +
six numbered editorial sections.

```svelte
<div class="resume-pane-edit">
  {#if resumeData}
    {#if resumeData.personal_info}
      <EditorialSection number="01" title="Identity">
        {#snippet children()}
          <div class="resume-identity">
            <p class="resume-identity-name">{resumeData.personal_info.full_name}</p>
            <p class="resume-identity-contact">
              {resumeData.personal_info.email}
              {#if resumeData.personal_info.phone} · {resumeData.personal_info.phone}{/if}
            </p>
            {#if resumeData.personal_info.location || resumeData.personal_info.linkedin_url}
              <p class="resume-identity-contact">
                {resumeData.personal_info.location || ''}
                {#if resumeData.personal_info.linkedin_url} · {resumeData.personal_info.linkedin_url}{/if}
              </p>
            {/if}
          </div>
        {/snippet}
      </EditorialSection>
    {/if}

    <EditorialSection number="02" title="Summary">
      {#snippet children()}
        <!-- existing summary edit flow, restyled -->
      {/snippet}
    </EditorialSection>

    <EditorialSection number="03" title="Experience" count={resumeData.work_experiences?.length ?? 0}>
      {#snippet children()}
        <!-- existing work-list, restyled to 3-col grid -->
      {/snippet}
    </EditorialSection>

    <EditorialSection number="04" title="Education" count={resumeData.education?.length ?? 0}>
      {#snippet children()}
        <!-- existing education list, restyled to 3-col grid -->
      {/snippet}
    </EditorialSection>

    <EditorialSection number="05" title="Skills" count={resumeData.skills?.length ?? 0}>
      {#snippet children()}
        <!-- existing skills cluster, restyled to .pill chips -->
      {/snippet}
    </EditorialSection>

    {#if resumeData.languages?.length > 0}
      <EditorialSection number="06" title="Languages" count={resumeData.languages.length}>
        {#snippet children()}
          <!-- existing languages list, restyled to 2-col card grid -->
        {/snippet}
      </EditorialSection>
    {/if}

    <EditorialSection number="07" title="Projects" count={resumeData.projects?.length ?? 0}>
      {#snippet children()}
        <!-- existing projects list, restyled to 2-col grid -->
      {/snippet}
    </EditorialSection>
  {:else}
    <p class="resume-loading-note">Loading resume…</p>
  {/if}
</div>
```

Inside each `{#snippet children()}`:

- **Summary (02):** mirror lines 450–476, replacing `.summary-edit`,
  `.summary-footer`, `.summary-add-btn`, `.summary` classes with editorial
  primitives. Textarea uses `.textarea` from `global.css:381`. Edit / Cancel
  buttons use `.btn-ghost`. Saved indicator stays. Empty `Add summary`
  becomes `.btn-ghost`. All keybinds preserved (`readSummaryKey`).
  Excluded-section banner: when the Summary row in the rail were togglable
  (it isn't — `disabled: true` per Decision 3), the section-excluded
  paragraph would render. Since Summary is always-shown, no banner.

- **Experience (03):** rebuild around the existing
  `{#each resumeData.work_experiences as exp, index}` loop. Each row is a 3-
  column CSS grid (`grid-template-columns: 110px 1fr auto`, gap 18px,
  padding `12px 0`, border-bottom `var(--rule-soft)`). Left cell: a span of
  mono dates `<span class="num resume-work-dates">{formatWorkDate(start)} —
  {formatWorkDate(end)}</span>`. Middle cell: title row (drag-handle ⋮⋮ in
  `var(--ink-3)` + `<span>{exp.title} · {exp.company}</span>` semibold 14px)
  + description (`var(--ink-2)` 13px, `white-space: pre-wrap`). Right cell:
  `<button class="btn-ghost">Edit</button>` (or, when `editingId === exp.id`,
  the existing textarea + Save / Cancel buttons). Match reasons line
  (existing `match_reasons`) renders as a small `.num` span in
  `var(--positive)` below the description (preserves the legacy meaning).
  Drag wiring (`ondragstart`, `ondragover`, `ondrop`, `ondragend`,
  `draggable={editingId !== exp.id}`) — all preserved verbatim.

- **Education (04):** mirror lines 602–606, rebuild as a 3-column grid
  (`grid-template-columns: 70px 1fr auto`, gap 18px). Left: mono year. Middle:
  `{edu.degree} {edu.field_of_study ? labels.in + ' ' + edu.field_of_study :
  ''} · {edu.institution}`. Right: existing edit affordance if any (the
  current Svelte source has none — Edit button preserved as
  display-only; the legacy renders a single `<p>` per education row, with
  no edit button. Plan: do NOT add an Edit button; keep the existing
  display-only pattern. Risk-1 below).

- **Skills (05):** rebuild the chip cluster. Each included skill is a
  `<span class="pill skill-chip" class:pill-positive={skill.matched}
  class:saving-skill={savingSkillIndex === index}>`. Inside the chip: the
  name span, the existing rename pencil button (`onclick=startEditSkill`),
  the existing exclude × button (`onclick=updateSkillInclusion(index,
  false)`). When `editingSkillIndex === index`, the rename input replaces
  the name span with the existing keybind wiring (`readSkillKey`,
  `field-sizing: content`). Available skills (excluded + profile skills)
  rendered below the chip cluster as a row of `<span class="pill skill-
  chip-available">` with dashed border (`border-style: dashed`) and an `+`
  add button. The `Available skills` header label becomes
  `<span class="eyebrow">{labels.availableSkills}</span>`. All-excluded
  note stays (legacy copy), restyled.

- **Languages (06):** rebuild the languages list as a 2-column CSS grid
  (`grid-template-columns: 1fr 1fr`, gap 12px). Each language card:
  `<div class="resume-language-card">` with a 14px `var(--ink)` semibold
  name span and a 12px `var(--ink-3)` level span. No edit affordance
  (legacy has none; preserve display-only). Container hidden when
  `languages.length === 0`.

- **Projects (07):** rebuild the projects loop as a 2-column grid
  (`grid-template-columns: 1fr auto`, gap 8px, padding `12px 0`,
  border-bottom `var(--rule-soft)`). Each row: middle cell with name
  (semibold 14px), description (`var(--ink-2)` 13px), tech (`var(--ink-3)`
  11px). Right cell: no edit affordance preserved from legacy. Empty
  `<p class="resume-empty">No projects.</p>` (12px `var(--ink-3)` italic).

5j. **Section-excluded banner (Edit mode):** when an editable row in the
rail is `included === false`, the corresponding `EditorialSection` body
prepends:

```svelte
{#if !rowIncluded}
  <p class="resume-section-excluded">Hidden from resume — re-check {sectionLabel} in the left rail to include.</p>
{/if}
```

Implementation: pass the row's `included` state into each snippet via a
locally-bound variable (e.g., `{@const expIncluded = sectionRows.find(r =>
r.key === 'work')?.included}`), then guard the banner inside the snippet
above the content rows. The banner has `color: var(--ink-3)`, italic,
12px, margin-bottom `var(--d-row)`. The section number and title in the
EditorialSection header are dimmed (`color: var(--ink-3)`) when the
section is excluded — pass `dim={!included}` as a new prop to
`EditorialSection`. **CAVEAT:** `EditorialSection.svelte` does not
currently expose a `dim` prop (slice 3 shipped without one). Reading the
slice 3 source (`src/components/EditorialSection.svelte`), there are
only 4 props. **Resolution: do NOT add the prop.** Dim the section
header from the consumer side via a CSS sibling rule — wrap each
excluded EditorialSection in a `<div class="resume-section-wrapper
section-dimmed">…</div>` and target `.section-dimmed
.editorial-section-title, .section-dimmed .editorial-section-header
.eyebrow.num { color: var(--ink-3); }` inside `ResumeView`'s `<style>`.
This avoids cross-slice contamination of slice 3's component. **No edit
to EditorialSection.svelte in this slice.**

5k. **Bottom action row** (legacy lines 651–656) is GONE — the Regenerate
button moves into the page header chrome (Must-have 2) and Download PDF
moves into the preview pane (Must-have 8).

5l. **Toast** (line 659) is unchanged — same `<Toast bind:message=…/>`
invocation at the bottom of the template.

**Style block (full replacement):**

Drop every class definition in the existing `<style>` block (lines 661–
1046). Replace with a single editorial style block that defines:

- `.resume-preview` — top-level container, `padding: var(--d-pad)` (so the
  layout doesn't sit flush against the viewport edges given
  `.container-wide` has `padding: 0`).
- `.resume-page-header` — flex row, justify-between, align-items center,
  gap 16px, padding-bottom `var(--d-gap)`. `.resume-page-title` — flex
  column, align-items center, gap 4px. `.resume-page-meta` — flex row,
  baseline, gap 12px.
- `.resume-job-analysis` styles already live in `JobAnalysis.svelte`
  (modification 4).
- `.resume-3col` — flex row, gap `var(--d-gap)`, flex-wrap wrap. (Wraps
  below the rail + pane minimum width per Must-have 3.)
- `.resume-rail` — width 240px, flex-shrink 0, min-width 240px,
  padding-right `var(--d-pad)`, border-right `1px solid var(--rule)`,
  display flex, flex-direction column, gap 0 (groups self-space).
- `.resume-rail-group` — display flex, flex-direction column, gap 10px,
  padding `12px 0`.
- `.resume-rail-sections` — flex column, gap 6px.
- `.rail-section-row` — display flex, align-items center, gap 8px,
  padding `4px 0`, background transparent, border none, font inherit,
  text-align left, cursor pointer.
- `.rail-section-checkbox` — 14×14, border-radius 2px, border 1px solid
  `var(--rule)`, background transparent (default). `.rail-section-row.
  included .rail-section-checkbox` — background `var(--ink)`, border-color
  `var(--ink)`. `.rail-section-row.disabled` — `cursor: default; color:
  var(--ink-4)`; `.rail-section-row.disabled .rail-section-checkbox` —
  border-color `var(--rule-soft)`.
- `.rail-section-label` — font-size 12px, color `var(--ink)` (default).
  `.rail-section-row:not(.included):not(.disabled) .rail-section-label` —
  color `var(--ink-3)`. `.rail-section-row.disabled .rail-section-label`
  — color `var(--ink-4)`.
- `.resume-pane` — flex 1, min-width 0, display flex, flex-direction
  column, gap `var(--d-gap)`.
- `.resume-tabs` — flex row, gap 4px, padding 4px, align-self flex-start.
- `.resume-pane-preview` — background `var(--paper-3)`, padding 28px, flex
  column, align-items center, gap 16px.
- `.resume-page-meta-eyebrow` — flex row, baseline, gap 12px.
- `.resume-page-count` — font-size 11px, color `var(--ink-3)`.
- `.resume-page` — width 600px, min-height 848px, background white,
  box-shadow `0 1px 0 rgba(0,0,0,0.04), 0 24px 48px -16px rgba(0,0,0,
  0.18)`, overflow auto.
- `.resume-pane-actions` — flex row, gap 10px, justify-content center.
- `.resume-pane-edit` — flex column, gap `var(--d-row)`.
- `.resume-section-wrapper` — wrapper around each EditorialSection (no
  border, just for the dim-by-class hook).
- `.section-dimmed .editorial-section-title` — color `var(--ink-3)`.
- `.section-dimmed .editorial-section-header .num` — color
  `var(--ink-3)`.
- `.resume-section-excluded` — color `var(--ink-3)`, font-size 12px,
  font-style italic, margin-bottom `var(--d-row)`.
- `.resume-identity` — flex column, gap 4px.
- `.resume-identity-name` — font-size 16px, font-weight 600, color
  `var(--ink)`, margin 0.
- `.resume-identity-contact` — font-size 12px, color `var(--ink-3)`,
  margin 0.
- `.resume-work-list` — flex column.
- `.resume-work-row` — display grid, grid-template-columns `110px 1fr
  auto`, gap 18px, padding `12px 0`, border-bottom `1px solid
  var(--rule-soft)`. `.resume-work-row:last-child { border-bottom: 0; }`
- `.resume-work-dates` — color `var(--ink-3)`, align-self start.
- `.resume-work-handle` — color `var(--ink-3)`, cursor grab, user-select
  none. `.resume-work-handle:active { cursor: grabbing; }`
- `.resume-work-title` — font-weight 600, font-size 14px, color
  `var(--ink)`.
- `.resume-work-company` — font-weight 400, color `var(--ink-3)`.
- `.resume-work-description` — font-size 13px, color `var(--ink-2)`,
  white-space pre-wrap, margin `8px 0 0`.
- `.resume-work-match` — font-size 11px, color `var(--positive)`, margin
  `4px 0 0`.
- `.resume-skills-cluster` — flex row, flex-wrap wrap, gap 8px.
- `.skill-chip` — extends `.pill`; gap 6px.
- `.skill-chip-available` — extends `.pill`; border-style dashed.
- `.skill-action` — background none, border none, cursor pointer, padding
  `0 2px`, font-size 10px, opacity 0.6, color inherit, font-family
  inherit. `:hover { opacity: 1; }`.
- `.skill-chip-input` — min-width 100px, max-width 300px, field-sizing
  content, font-size 11px, font-family inherit, padding `0 4px`, border
  none, background transparent.
- `.resume-education-list` — flex column.
- `.resume-education-row` — display grid, grid-template-columns `70px 1fr
  auto`, gap 18px, padding `12px 0`, border-bottom `1px solid
  var(--rule-soft)`.
- `.resume-languages-grid` — display grid, grid-template-columns
  `1fr 1fr`, gap 12px.
- `.resume-language-card` — padding 12px, background `var(--paper-2)`,
  border `1px solid var(--rule)`, border-radius `var(--r-sm)`.
- `.resume-language-name` — font-weight 600, color `var(--ink)`,
  font-size 14px.
- `.resume-language-level` — color `var(--ink-3)`, font-size 12px.
- `.resume-projects-list` — flex column.
- `.resume-project-row` — display grid, grid-template-columns `1fr auto`,
  gap 8px, padding `12px 0`, border-bottom `1px solid var(--rule-soft)`.
- `.resume-project-name` — font-weight 600, color `var(--ink)`, font-size
  14px, margin 0.
- `.resume-project-description` — color `var(--ink-2)`, font-size 13px,
  margin `4px 0 0`.
- `.resume-project-tech` — color `var(--ink-3)`, font-size 11px, margin
  `4px 0 0`.
- `.resume-loading-note` — color `var(--ink-3)`, font-size 13px,
  text-align center, font-style italic.
- `.resume-empty` — color `var(--ink-3)`, font-size 12px, font-style
  italic, margin 0.
- `.saving-skill` — opacity 0.5, pointer-events none.
- `.dragging` — opacity 0.5, background `var(--paper-2)`.
- `:focus-visible` for all interactive elements (buttons, inputs) —
  outline `2px solid var(--accent)`, outline-offset `2px`. Single rule:
  `.resume-preview button:focus-visible, .resume-preview
  input:focus-visible, .resume-preview textarea:focus-visible`.

**Zero references** in the new style block to: `--color-border`,
`--color-primary`, `--color-primary-rgb`, `--color-text-rgb`,
`--color-success`, `--color-success-rgb`, `--color-error`,
`--color-error-rgb`, `--spacing-grid`, `--spacing-section`,
`--spacing-field`, or any of the hard-coded greys (`#999`, `#ccc`, `#333`,
`#e0e0e0`, `#f0f0f0`, `#cc6600`).

**Maps to:** Must-haves 2, 3, 5, 7, 8, 9, 10, 11; Scenarios 1, 2, 3, 4,
4b, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15b, 16.

## Files to DELETE

### `src/components/ResumeSection.svelte`

**Verified consumer count:** 1 (`src/components/ResumeView.svelte`,
lines 480, 537, 597, 610, 625). After modification 5 removes every
`<ResumeSection>` callsite in `ResumeView.svelte` and the `import` at
line 3, `ResumeSection.svelte` has zero consumers.

**Deletion command:** `git rm src/components/ResumeSection.svelte`.

**Re-verification step (in build phase):** before running `git rm`,
`grep -rn "ResumeSection" src/ tests/` returns zero matches.

**Maps to:** FEATURE_SPEC Resolved decision 4, Must-have 9.

## Tests

**No new tests written in this slice.** The behaviour preservation gate
(Must-haves 11, 12) and the visual restyle scenarios (Must-haves 1–10) are
verified by:

1. **Existing tests pass without modification.** Run `pytest tests/` after
   the build. Particular attention: `tests/test_pdf_export.py`,
   `tests/test_pdf_api.py`, `tests/test_pdf_language.py`,
   `tests/test_resumes.py`, `tests/test_resume_*.py`,
   `tests/test_skills.py`, `tests/test_users.py`,
   `tests/test_work_experiences.py`, `tests/test_topbar_shell.py`,
   `tests/test_profile_editor_restyle.py`. **Zero modifications to test
   files** — if a test fails, the production code is wrong, not the
   test.

2. **`bun run build` succeeds with zero Svelte / Rollup errors.** No
   `svelte-ignore` comments added without justification (per slice 3
   retro).

3. **Manual inspection** (Phase 3 inspector agent dispatch). Bullets
   below.

### Manual inspection bullets (for Phase 3 `inspector` agent)

**These bullets MUST be promoted 1:1 to CHECKLIST checkboxes (MN-A — slice 3
carryover, FEATURE_SPEC Must-have 13).** The `checklist-builder` agent is
explicitly instructed to mirror them; the `plan-reviewer` agent verifies
the mapping.

The inspector should automate every bullet via Playwright where possible
(per user-level memory: computed-style assertions and DOM grep belong to
Playwright; only behavioural judgment belongs to the human). The list is
written in inspect-checkbox phrasing.

I-1. **Page header chrome.** `← Back to Input` is a `.btn-ghost` button
     (computed `background: transparent`, no underline on hover). Center
     block has eyebrow `RESUME · FOR JOB` (computed font-family contains
     "JetBrains Mono", `text-transform: uppercase`, `letter-spacing >=
     0.10em`) and an `<h1 class="display">` with the page title (computed
     font-family contains "Instrument Serif"). Right has `Regenerate` as
     `.btn`. Below the title, `Generated {date}` sits next to a `.pill.
     pill-positive` chip when `match_score >= 80`.

I-2. **Match pill bands.** With `score >= 80`, the pill class is `pill-
     positive`. With `60 <= score < 80`, `pill-warn`. With `score < 60`,
     `pill-accent`. With `score == null`, no pill renders.

I-3. **Three-column shape.** `.resume-3col` exists with two visible
     children: `.resume-rail` (computed width 240px, flex-shrink 0) and
     `.resume-pane` (computed flex `1 1 0%`).

I-4. **Container-wide on resume tab.** `<div class="container">` has the
     `container-wide` class when `activeTab === 'resume'` (verified by
     `classList.contains('container-wide') === true`). The class is
     absent on other tabs.

I-5. **Templates rail group.** Eyebrow reads `Templates · 04`. Four
     `<button class="template-card">` elements render in order:
     Classic, Modern, Brussels, EU Classic. The active card has
     `aria-pressed="true"` and computed `border-color` matching
     `var(--ink)` (or its OKLCH equivalent).

I-6. **Template switch wiring.** Clicking Modern flips `aria-pressed` on
     Classic to `false` and on Modern to `true`. The `<PdfPreview>`
     inner `<div>` gains `class="pdf-preview template-modern"`.
     Subsequent Download PDF call hits `downloadPdf(resume.id, 'modern',
     resume.language)`.

I-7. **Language pill (locked).** Eyebrow `Language` followed by exactly
     one `.pill.pill-solid` chip carrying the resume's
     `language.toUpperCase()` text. The pill is NOT a `<button>`,
     has no onclick, `cursor: default`, and `aria-label` reads
     "Resume language: {Lang} (locked)".

I-8. **Sections rail.** Eyebrow `Sections` followed by seven
     `<button class="rail-section-row">` elements in order:
     Identity, Summary, Experience, Education, Skills, Languages,
     Projects. Identity and Summary have `aria-disabled="true"`,
     `tabindex="-1"`, `cursor: default` and the label colour is
     `var(--ink-4)` (computed OKLCH ≈ `oklch(0.70 0.025 265)`). The
     other five rows have `aria-pressed={true|false}` reflecting
     the section's `included` state. Clicking Projects flips
     `aria-pressed` AND triggers a `<PdfPreview>` re-render without
     projects (the `<div class="pdf-preview…">` inner content no
     longer has the projects block).

I-9. **Preview pane backdrop and page surface.** When `editMode ===
     'preview'`, `.resume-pane-preview` has computed `background-color`
     resolving to `var(--paper-3)`. Below the page-meta eyebrow, the
     `.resume-page` div has computed `width: 600px`, `min-height: 848px`,
     `background-color: rgb(255 255 255)`, and `box-shadow` containing
     the substring `24px 48px -16px` (substring match to avoid browser-
     format flake).

I-10. **PdfPreview content unchanged.** The inner `<div
      class="pdf-preview template-classic">` (or matching template) is
      byte-identical to a pre-slice snapshot. Captured by running
      `bun run build && bun run dev`, opening a saved resume, and
      diffing the rendered `outerHTML` of the first matching
      `.pdf-preview` element against the pre-slice baseline. (For
      automation: Playwright `page.locator('.pdf-preview').first
      .innerHTML()` should match the baseline exactly.)

I-11. **Tab pattern ARIA.** `.resume-tabs` carries `role="tablist"`,
      `aria-label="View mode"`. Each button has `role="tab"`,
      `aria-selected={true|false}`, `tabindex={0|-1}`. After clicking
      Preview: `aria-selected`/`tabindex` flip; Edit becomes
      `aria-selected="false"`, `tabindex="-1"`.

I-12. **Edit-mode shape.** With `editMode === 'edit'` and a populated
      resume, the pane renders one Identity card (no EditorialSection
      header — wait, per Must-have 9 the identity card IS wrapped in
      `<EditorialSection number="01" title="Identity">`. CONFIRM: there
      are seven EditorialSection blocks (01–07) — Identity, Summary,
      Experience, Education, Skills, Languages, Projects). Document
      outline: one `<h1>` + exactly seven `<h2>` headings from the
      EditorialSection blocks (per Must-have 9 and the document-outline
      success-criteria checkbox).

I-13. **JobAnalysis restyle.** Eyebrow reads `JOB · REQUIREMENTS` (NOT
      "Job Requirements" in title case). Collapse toggle is a `.btn-
      ghost` button with text `Hide` (or `Show` after collapse). Each
      required-skill chip is `.pill.pill-positive` (matched) or
      `.pill.pill-warn` (unmatched). Experience and education inline
      rows pair an `var(--ink-2)` label with a `.pill-positive` or
      `.pill-warn` chip. No `.requirements-*` legacy classes appear in
      the rendered DOM.

I-14. **Inline-edit affordances preserved.** Round-trip in Edit mode:

      I-14a. Click Edit on the Summary section, type ` X`, press
             Cmd+Enter → API PATCH/PUT fires, summary persists, `Saved`
             indicator surfaces.
      I-14b. Click rename pencil on a skill chip, type new name,
             press Enter → API call fires, chip text updates, no toast
             error.
      I-14c. Click exclude × on a skill chip → skill moves to
             "Available skills" row below, included flag flips.
      I-14d. Drag a work experience row from position 2 to position 1
             → order persists after the drop event; `Order saved` toast
             surfaces.
      I-14e. Click Edit on a work description, type text, click Save →
             description persists; `Saved` indicator surfaces.

I-15. **Section toggle from rail (Preview mode).** From Preview mode,
      click the Projects row in the rail → row's `aria-pressed` flips
      to `false`, `.rail-section-checkbox` background changes from
      `var(--ink)` to transparent, `<PdfPreview>` re-renders without
      the projects block. The legacy `[ON]/[OFF]` toggle does not
      appear in the DOM anywhere.

I-16. **Section toggle from rail (Edit mode).** From Edit mode, with
      the Projects row currently included, click it → the
      `EditorialSection № 07 Projects` block in the center pane gets
      the `.section-dimmed` wrapper class, its header and number turn
      `var(--ink-3)`, and a `<p class="resume-section-excluded">`
      banner appears at the TOP of the section body reading "Hidden
      from resume — re-check Projects in the left rail to include."
      Project rows still render below the banner.

I-17. **Legacy class grep.** Run the grep in Scenario 15 against
      `src/components/ResumeView.svelte`,
      `src/components/TemplateSelector.svelte`,
      `src/components/JobAnalysis.svelte`, and the OUTER chrome of
      `src/components/PdfPreview.svelte`. **Exactly zero matches**
      outside the protected inner `<div class="pdf-preview template-
      …">` markup and `<style>` block.

I-18. **Legacy token grep.** Run the grep in Scenario 16 — zero
      matches outside the protected PDF zone.

I-19. **Topbar import cleanup.** `grep -n "\bstore\b"
      src/components/Topbar.svelte` returns zero matches. `bun run
      build` succeeds.

I-20. **PDF byte-identity (the load-bearing gate).** Capture pre-
      slice baseline PDFs for one representative resume:
      `(classic, en), (modern, en), (brussels, en), (eu_classic, en),
       (classic, fr), …, (eu_classic, nl)` = 12 PDFs. After this slice,
      download the 12 PDFs again from the same resume. Diff
      byte-by-byte (`cmp pre.pdf post.pdf`). Zero bytes differ.
      Implementation: capture baselines BEFORE editing any source
      file. Store under `workbench/3-build/pdf-baselines/`.

I-21. **`pytest tests/` zero regressions.** Particular attention to
      the PDF suite. Zero test files modified.

I-22. **Focus-visible outline.** Tab through every interactive
      element in the rendered page. Each focused element shows a `2px
      solid var(--accent)` outline with 2px offset. No element shows
      the legacy `--color-primary` outline.

I-23. **Empty / loading states.** Open a resume immediately on
      first mount (before `$effect` populates `resumeData`): the
      center pane shows `<p class="resume-loading-note">Loading
      resume…</p>` in `var(--ink-3)` italic. The page header chrome
      and JobAnalysis card render normally (they read from
      `resume.*`, not `resumeData`).

I-24. **Document outline.** Open browser devtools accessibility tree
      → one `<h1>` (page title), seven `<h2>` headings from the
      EditorialSection blocks. Zero `<h3>` or `<h4>` from the
      restyled components. (The PdfPreview inner `<div>` is OUT of
      scope and may carry its own template-specific `<h*>` — those
      are inside the protected zone.)

The 24 bullets above are EXACTLY the set that must appear as `[ ]`
checkboxes in CHECKLIST.

## Library patterns to use (cite SVELTE5_NOTES)

- **`$bindable` for `selected` in TemplateSelector.** Pattern Q1 in
  `workbench/2-plan/research/SVELTE5_BINDABLE_NOTES_2026-05-13_restyle-
  resume-preview.md`. Parent: `<TemplateSelector bind:selected=
  {selectedTemplate}/>`. Child: `let { selected = $bindable('classic') } =
  $props();`. **Same pattern slice 3 used; no deviation.**

- **`$state` for ResumeView state.** Already in place (lines 60–86). No
  change to declarations.

- **`$derived.by(() => …)` for derived state.** Used for `labels`
  (already there) and added for `sectionRows`. Cite Q3 in
  `SVELTE5_NOTES_2026-05-13_restyle-resume-preview.md`.

- **`$effect` for side effects.** Already used at lines 87, 101. No
  change to effect declarations.

- **`{#snippet children()}` for EditorialSection consumption.** Same
  pattern slice 3 uses for ProfileEditor sections. The `EditorialSection`
  component renders `{@render children()}` at line 17, exactly as slice 3
  ships.

- **ARIA APG tab pattern (W3C, not a library).** `role="tablist"` on the
  wrapper with `aria-label`, `role="tab"` on each button,
  `aria-selected={…}` mirroring the active state, `tabindex={0 | -1}`
  with active = 0 and inactive = -1. Source:
  <https://www.w3.org/WAI/ARIA/apg/patterns/tabs/>. Left/Right-arrow
  keyboard navigation between tabs NOT implemented (preserved-legacy
  limitation per UX a11y note 9).

## Risks

R-1. **Education / project edit affordance.** The current
     `ResumeView.svelte` source renders Education and Projects as
     display-only (no edit buttons). UX_DESIGN says "`.btn-ghost` Edit
     right" for Education and "`.btn-ghost` Edit right" for Projects in
     the slice-3-pattern grid. **Decision:** keep display-only (preserve
     current behaviour, no new affordance). Pull the "Edit" right-column
     description from the spec since it doesn't exist in the legacy and
     this slice is chrome-only. Surface in retro if anyone expects it.

R-2. **`sectionRows` derived state and `toggleSection` key mapping.**
     The current `toggleSection(section)` accepts five keys: `work`,
     `skills`, `education`, `projects`, `languages`. The rail Sections
     group renders seven rows; Identity and Summary have
     `disabled: true` and don't call `toggleSection` (Decision 3).
     The mapping in `sectionRows` is:
     `Identity → key: null`, `Summary → key: null`,
     `Experience → key: 'work'`, `Education → key: 'education'`,
     `Skills → key: 'skills'`, `Languages → key: 'languages'`,
     `Projects → key: 'projects'`. Note that **`Experience` maps to
     `'work'`**, not `'experience'` — the existing handler keys on
     `work`. `updateSectionFromRail(row)` guards `row.disabled || !row.
     key` first, then delegates to `toggleSection(row.key)`.

R-3. **`projects[0]?.included === true` is the correct test for
     "Projects included".** Note the strict `=== true` (current code line
     627); the projects opt-IN default per the existing schema is
     `false`-equivalent unless explicitly enabled. The `sectionRows`
     derivation matches: `const projs = resumeData.projects?.[0]?.
     included === true`. Don't accidentally weaken to `!== false` —
     projects is opt-IN per legacy semantics. The CHECKLIST checkbox
     covering Section 8 toggle verifies this.

R-4. **PDF byte-identity break (the highest-priority risk).** The
     restyle MUST NOT edit `templates/resume_base.css`, the four
     `templates/resume_*.html` files, or the inner `<div class="pdf-
     preview template-…">` markup and inline `<style>` block in
     `src/components/PdfPreview.svelte`. Build-phase mitigation:
     before-and-after `sha256sum` of these files. **The CHECKLIST has
     an explicit checkbox for "no diff in protected files" — verified
     by `git diff --stat templates/ src/components/PdfPreview.svelte`
     showing zero lines changed.**

R-5. **`writeDownloadedPdf` rename.** `handleDownloadPdf` violates
     the forbidden-pattern table (handle* prefix). Rename and update
     the single callsite. The function literally writes a PDF to the
     user's local Downloads folder via `downloadPdf` (lib/api.js).
     `write*` is the correct verb per CLAUDE.md. Single callsite is
     line 423 (`onclick={handleDownloadPdf}`). One rename + one
     callsite swap.

R-6. **EditorialSection `dim` prop NOT added.** Slice 3's component
     stays as shipped (40 LoC, four props). The dimmed-header rendering
     for excluded sections is achieved via a sibling `.section-dimmed`
     class on the `.resume-section-wrapper` that contains the
     `<EditorialSection>` invocation, with CSS rules inside
     `ResumeView`'s `<style>` block targeting
     `.section-dimmed .editorial-section-title` and `.section-dimmed
     .editorial-section-header .num`. This crosses Svelte's component-
     scope boundary on purpose (CSS specificity, not Svelte scoping —
     these target classes from the child component's compiled CSS). If
     Svelte's CSS scoping prevents reaching the child's classes, fall
     back to passing a `dim` prop into `EditorialSection.svelte` —
     **CAVEAT**: that requires editing slice 3's component, which
     should be a last-resort change. Build phase: implement with
     `:global()` selectors or `>>>` legacy combinator; verify by
     inspecting computed styles before committing.

R-7. **Drag-handle aria-label.** Existing source emits a
     `<span class="drag-handle" aria-label="Drag to reorder">`. The
     restyle keeps the drag handle as an `<span>` (not a button), so
     it can't take keyboard focus — that matches the legacy
     limitation. UX a11y note 9 acknowledges this. No new keyboard-
     accessible drag pattern is introduced.

R-8. **`getScoreClass` removal.** Single old caller is the
     `<span class="match-score {getScoreClass(resume.match_score)}">`
     in the legacy template (line 372). Removing the function and the
     callsite together is safe; no other consumer.

R-9. **`labels.availableSkills` copy.** Currently English in the FR
     and NL translation maps (lines 39, 49 — `availableSkills:
     'Available skills'`). The restyle does NOT fix the translation
     gap (out of scope — same string in every locale today). Surface
     in retro as a slice 5+ candidate.

R-10. **`store` import in Topbar — confirm before deleting.** Run the
      grep `grep -nE "\bstore\b" src/components/Topbar.svelte` AGAIN
      immediately before the edit. If a second match appears (e.g.,
      between writing this plan and running build), abort the edit
      and surface in retro.

R-11. **Empty-data `sectionRows` race.** `resumeData` is null on
      first mount; `sectionRows` derives to `[]` and the rail's
      Sections group renders nothing. UX_DESIGN State 3 calls for a
      7-row skeleton in the indeterminate state. **Decision:** the
      State 3 skeleton is a fallback against a slow Svelte 5 effect;
      in practice the `$effect` populating `resumeData` runs in the
      same microtask as the first render. Ship with the empty `[]`
      → no rows render for that one microtask. If users complain,
      add the indeterminate skeleton in a follow-up. Note in retro.

R-12. **Edit-mode summary section: the rail Summary row is disabled,
      so the Summary EditorialSection block NEVER shows the
      excluded-banner.** Confirmed: Summary's `key: null` AND
      `disabled: true`; `updateSectionFromRail` guards on both and
      no-ops. The Summary section block always renders.

R-13. **JobAnalysis `<h3>` vs `<span class="eyebrow">`.** The legacy
      uses `<h3>Job Requirements</h3>` inside the header row. The
      restyle drops the `<h3>` entirely — header is just an `.eyebrow`
      span. This removes one `<h3>` from the document outline (UX a11y
      note 1 supports this — no `<h3>` from restyled components).
      Sub-headers `Required Skills` / `Preferred Skills` swap from
      `<h4>` to `<span class="eyebrow">` — same heading-strip rationale.

R-14. **`labels.workExperience` etc. translations.** The existing
      `labels` map (lines 11–58) holds the EditorialSection titles for
      Experience / Skills / Education / Languages / Projects in three
      languages. The restyle keeps the same `labels.*` references for
      each EditorialSection's `title` prop. The Identity and Summary
      titles are NOT in the labels map — hardcode `"Identity"` and
      `"Summary"` in English for now; surface in retro as a
      translation-gap candidate.

R-15. **`bun run dev` HMR + Svelte 5 props.** The restyle is large
      enough that Vite/Rollup HMR may behave unpredictably on the
      first save. Verify by hard-refreshing the dev server before
      running `pytest`. If HMR shows stale state, restart `bun run
      dev`. Surface a `note-capturer` artifact if observed.

## Build & verify steps

1. **PDF baseline capture (FIRST).** Before any source edit, run
   `bun run build && bun run dev` (or use the existing dev server).
   Pick one representative saved resume, generate and download all 12
   `(template, language)` PDFs. Save under `workbench/3-build/pdf-
   baselines/` named `{template}_{language}.pdf`. **If this step
   fails (no saved resume to test against), STOP — surface via Q3 or
   note-capturer; do not proceed.**

2. **Lean-code header on every modified Svelte file.** Confirm each of
   the five MODIFY targets begins with the two-line header per
   CLAUDE.md.

3. **Modifications in this order** (least-risky → most-risky):
   - 3.1. `src/App.svelte` (1-line diff).
   - 3.2. `src/components/Topbar.svelte` (1-line import).
   - 3.3. `src/components/JobAnalysis.svelte` (small file, isolated
          consumer).
   - 3.4. `src/components/TemplateSelector.svelte` (rewrite body,
          keep contract).
   - 3.5. `src/components/ResumeView.svelte` (the big one).
   - 3.6. `git rm src/components/ResumeSection.svelte`.

4. **`bun run build`** between major edits. Tolerate zero compile
   errors. Tolerate zero new Svelte warnings (`svelte-ignore` only
   for the existing `a11y_autofocus` cases on textarea / input,
   preserved verbatim from legacy).

5. **`pytest tests/`** AFTER all edits. Zero regressions, zero
   modifications to test files.

6. **PDF byte-identity verification.** Re-download all 12 PDFs;
   `cmp` byte-by-byte against the baselines from step 1. **Zero
   bytes differ.** If ANY byte differs, STOP and surface — this is
   the hard gate.

7. **Legacy class / token grep.** Run Scenarios 15 and 16 greps.
   Expect zero matches outside the protected PDF zone.

8. **Inspector dispatch.** Phase 3 step 4 invokes `inspector` with
   the 24-bullet manual checklist payload (above).

9. **Retro + change-logger + git-closer** per Phase 4.

## Out-of-scope re-affirmed

- **PDF render path** (`templates/resume_base.css`, four template HTMLs).
- **Inner `<div class="pdf-preview template-…">` markup and inline
  `<style>` block** in `PdfPreview.svelte`.
- **Render-path unification** (shared CSS or iframe srcdoc).
- **`src/lib/resumeStore.svelte.js`** changes.
- **Live preview-language toggle** (EN / FR / NL button group).
- **Right-side context aside** (job sigil, MatchDonut, Stats grid).
- **Inline editor behaviour changes** (only chrome restyle).
- **Schema, API, mobile, dark theme, sidebar nav, live tweaks,
  AI augmentations.**
- **Translation gaps** in `labels` map (out per slice scope).
