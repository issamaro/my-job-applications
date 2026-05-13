# FEATURE_SPEC — restyle-profile-editor

Date: 2026-05-13
Ceremony: M (full)
Slice: 3 of 9 — editorial redesign initiative

## Persona

**Primary:** the job-seeking professional who maintains MyCV as their single
source-of-truth profile and generates tailored CVs against it. They open the
profile editor weekly to add a recent role, refresh the summary, or fix a typo
before applying. Desktop, two-monitor setup, English locale, has photo +
multiple experiences + multiple skills + ≥1 language.

## Core pain point

The editorial Topbar shipped in slice 2 sits above a legacy editor. The
cognitive jolt between the two visual languages — Topbar in JetBrains Mono /
Instrument Serif over `--paper`, editor in legacy 14px Inter forms framed by
`--color-border` greys — undermines the credibility of the redesign and makes
the source-of-truth screen feel less trustworthy than the chrome.

## Solution (one paragraph)

Restyle the profile editor and its seven child components to the editorial
primitives shipped by slices 1–2 — matching `design-bundle/project/screen-profile.jsx`
visually — without touching schema, API, or save/validate behaviour. Every
field still saves, every error still surfaces, every drag-reorder still
persists; only the surface changes. Close slice 2's compromise #1 by wiring
the Topbar's initials circle to the active profile's `full_name`.

## Must-have list

1. **Editorial page frame.** ProfileEditor renders a centred column
   (`max-width: 940px`, padding `0 36px`) inside a `<main>` with
   `padding: var(--d-pad) 0`. A header block shows an `eyebrow`
   (`Workspace · profile`), a serif `.display` heading (`Your <em>source of
   truth</em>.`) at 44px, a short sub-line (`The single profile every tailored
   CV draws from. Edit once, ship anywhere.`), and the existing `Import JSON`
   button right-aligned. The action-row wrapper holding `Import JSON` keeps
   the existing `.profile-header` class so existing playwright tests
   (`test_disabled_slots_inert`, `test_search_pill_content`,
   `test_keyboard_activates_slot`) still find it. The `<Toast>` element
   remains a direct child of `ProfileEditor`'s root template (same
   parent as `.profile-header` and `<ImportModal>` — verifiable at
   `src/components/ProfileEditor.svelte:46`); it is NOT moved inside
   the new editorial-column wrapper, because Toast is a viewport-level
   overlay whose stacking should not be constrained by the centred
   column's transform context.

2. **Seven numbered editorial sections.** A new extracted component
   `src/components/EditorialSection.svelte` renders the section header
   pattern: a 14-pixel-bottom-margin row containing an `eyebrow`-classed
   `<span>` reading `№ {NN}`, then an `<h2 class="display">` (26px) with
   the section title, then an optional `.num`-classed count `<span>`
   (12px, `var(--ink-3)`). The eyebrow sits inside the row, not inside
   the `<h2>`, so the document outline still has a single `<h1>` (page
   heading) and seven `<h2>`s (one per section). Section body is a
   default `{@render children()}` slot. Sections in order: Identity
   (01), Summary (02), Experience (03, count), Education (04, count),
   Skills (05, count), Languages (06, count), Projects (07, count). No
   collapsible behaviour — the legacy `Section.svelte`'s
   click-to-collapse is dropped; every section is permanently expanded.

3. **Identity card.** Two-column layout: a 96px circular avatar slot on the
   left (background `var(--ink)`, color `var(--paper)`, font
   `var(--font-display)` italic 40px) wrapping the existing `PhotoUpload`
   component, and on the right a 1fr-1fr CSS grid (12px gap) of
   `.eyebrow`-labelled fields. The grid contains **five** fields, in
   source order: Full name, Email, Phone, Location, LinkedIn. The design
   reference (`screen-profile.jsx:73-78`) renders a sixth field
   `Headline / title` mapped to `u.title` — this slice deliberately omits
   it because adding `title` would be a schema change (see Non-goals).
   Inputs use the `.input` primitive. Validation messages preserved
   verbatim (required markers, "Invalid email address"). Summary field
   moves to its own section (see point 4).

4. **Summary section.** Renders the existing `summary` field as a
   `.textarea`-primitive control inside `EditorialSection № 02 Summary`.
   No AI-rewrite button, no word/character counter (per Scope OUT). The
   textarea reads/writes through the shared profile store
   `src/lib/profileStore.svelte.js` (see Must-have 10) — same data path
   as Identity. Blur triggers a 500ms-debounced `store.save()` that
   internally calls `updateUser`. The Identity card and the Summary
   section both subscribe to the same store state; both render `Saved`
   indicator on success.

5. **Experience timeline.** Each row is a 3-column grid (`110px 1fr auto`,
   gap 18px, padding `16px 0`): left rail mono dates using the existing
   `formatDate()` helper in `WorkExperience.svelte:142` — top line
   `formatDate(start_date)`, middle line a `var(--ink-4)` em-dash, bottom
   line `Present` (when `is_current`) or `formatDate(end_date)`. Middle
   shows `{title} · {company}` (semibold 14px, company in `var(--ink-3)`
   weight 400) then a `var(--ink-3)` 12px location line then a
   `var(--ink-2)` 13px description (line-height 1.55). Right column an
   `.btn-ghost` Edit action (padding `4px 8px`, font-size 11px). Rows
   separated by `1px solid var(--rule-soft)` (no separator above the
   first row). Add-experience rendered as a `.btn` with a leading
   `+` Unicode glyph (no SVG dependency needed). The existing
   edit form (modal-less inline form replacing the row) is preserved;
   only its inputs adopt the `.input` / `.textarea` primitives.

6. **Education list.** 3-column grid (`70px 1fr auto`): mono year, then
   `{degree}{ field_of_study?}` semibold 13px + `{institution}` `ink-3`
   sub-line, then `.btn-ghost` Edit. Rows separated by `--rule-soft`. Add
   action is a `.btn` button. Existing edit form retained.

7. **Skills cluster.** Saved skills render as `.pill` chips
   (`background: var(--paper-2)`, `border: 1px solid var(--rule-soft)`,
   `border-radius: var(--r-sm)`, font-size 12px, padding `5px 10px`,
   gap 6px) with a per-pill remove affordance (the existing `×` button
   restyled to inherit `var(--ink-3)`, hover `var(--negative)`). The
   pill cluster ALWAYS includes a final dashed `.pill` reading `+ add`
   (background `transparent`, `border: 1px dashed var(--rule)`, color
   `var(--ink-3)`) — present whether saved-skill count is 0, 1, or N.
   Clicking the dashed pill focuses the add-skill input below. The
   add-skill input uses the `.input` primitive plus a `.btn-primary` Add
   button. The legacy `<div class="empty-state">No skills added yet.</div>`
   is dropped — the always-visible dashed pill replaces it.

8. **Languages grid.** Two-column grid (`1fr 1fr`, gap 8px) of language cards:
   `padding: 10px 14px`, `background: var(--paper-2)`,
   `border: 1px solid var(--rule-soft)`, `border-radius: var(--r-sm)`. Each
   card shows the language name (semibold 13px) and full level label
   (`ink-3` 11px) aligned left, with the CEFR code (mono 11px) right-aligned.
   Drag-to-reorder behaviour preserved verbatim. Existing edit form
   (inline name + level select) retained, restyled to use `.input` and the
   native select with `.input`-matching styling.

9. **Projects rows.** Same row pattern as Experience but without a date rail:
   2-column grid (`1fr auto`) — middle shows `{name}` semibold + technologies
   + URL link in the `ink-3` sub-line + `ink-2` description below; right is
   `.btn-ghost` Edit. Add-project action is a `.btn`. Existing edit form
   retained.

10. **Topbar initials wiring.** `Topbar.svelte`'s `<div class="topbar-user">`
    no longer renders the hard-coded `LM`. Initials are derived from
    `profile.full_name` via a pure helper `parseInitials(fullName)`:
    - Trim, split on whitespace, drop empty tokens.
    - Zero tokens → return `??` (the chosen placeholder).
    - One token → return its first character, uppercased.
    - Two-or-more tokens → return first character of first token + first
      character of last token, both uppercased.
    The helper lives in `src/lib/profileStore.svelte.js` (so it can be
    unit-tested independently of the DOM).
    **Data source: shared profile store.** A new module
    `src/lib/profileStore.svelte.js` exports a Svelte 5 runes-based
    singleton with the following shape:
    ```js
    profile = $state({ full_name: '', email: '', phone: '', location: '',
                       linkedin_url: '', summary: '', photo: null });
    loaded = $state(false);
    error = $state(null);
    saving = $state(false);
    saved = $state(false);
    async function load() { ... call getUser() ... }
    async function save() { ... call updateUser(profile) ... }
    function initials() { return parseInitials(profile.full_name); }
    ```
    `Topbar.svelte` imports the store and calls `store.load()` on its
    own first mount, then renders `<div class="topbar-user">{store.initials()}
    </div>`. `UserProfile.svelte` is refactored to read/write through
    the same store instead of owning its own `data` state — so a save
    via the Identity card automatically updates the Topbar circle via
    Svelte 5 reactivity, no event bus required. The Summary section
    (Must-have 4) also subscribes to the same store. The store survives
    tab switches (singleton lives at module scope).
    **`store.load()` is idempotent and concurrency-safe.** Both Topbar
    and UserProfile call it defensively in their own `$effect` on mount.
    The store maintains a module-level `inFlightLoad` promise — if a
    load is already running, subsequent callers `await` the same
    promise rather than firing another `getUser()`. If `store.loaded`
    is already `true`, callers short-circuit and return immediately.
    Net effect: exactly one `getUser()` request fires per page session.

11. **Legacy color sweep.** No occurrences of `--color-border`,
    `--color-primary-rgb`, `--color-text-rgb`, or hard-coded `#e0e0e0`
    remain inside the seven listed component files
    (`ProfileEditor.svelte`, `UserProfile.svelte`,
    `WorkExperience.svelte`, `Education.svelte`, `Skills.svelte`,
    `Languages.svelte`, `Projects.svelte`). All borders flow from
    `var(--rule)` / `var(--rule-soft)`; all tinted backgrounds from
    `var(--paper-2)`; all accent overlays from `var(--accent-soft)` or
    `oklch(from var(--accent) l c h / alpha)`. `Section.svelte` is not
    in this list because it is being deleted in this slice (verified
    single consumer is `ProfileEditor.svelte:2`).

12. **Behaviour preservation.** Every field still saves and round-trips
    (identity fields, summary, photo, work experience full schema, education
    full schema, skills, languages with drag order, projects full schema).
    Every existing validation error still surfaces against the new input
    styling. The import-from-JSON path through `ImportModal` is untouched.
    The `Toast` success affordance after import still fires.

13. **UserProfile loading + error render contract.** After the refactor,
    `UserProfile.svelte` no longer owns the loading skeleton or the
    error banner via its own local state. Instead it renders bound to
    the shared store:
    - `store.loaded === false` AND `store.error === null` → render the
      existing 3-row `.skeleton` block (preserve the markup at
      `UserProfile.svelte:80-84` verbatim, just point the conditional at
      `store.loaded` instead of the local `loading` variable).
    - `store.error !== null` → render the existing
      `<div class="form-error">{store.error}</div>` block. The error
      copy `"Could not load profile. Please refresh."` is preserved
      verbatim and is set by the store's `load()` catch handler.
    - `store.loaded === true` AND `store.error === null` → render the
      Identity layout (avatar + 5-field grid).
    The Summary section (Must-have 4) and Topbar (Must-have 10) do
    NOT render skeletons or error UI of their own. Topbar's
    `.topbar-user` shows `??` while `store.loaded === false` (the same
    rendering as empty `full_name`) — there is no separate loading
    glyph. Summary section shows an empty `.textarea` until
    `store.loaded === true`. The page header (eyebrow + display
    heading + Import JSON) is independent of profile load state and
    renders immediately on mount.

## BDD scenarios

**Scenario 1 — Editorial page frame.**
- **Given** a profile with `full_name: "Issa Maro"` and at least one work
  experience, education, skill, language, and project,
- **When** the user opens the profile editor on a desktop viewport,
- **Then** the page renders a centred 940px column with an eyebrow
  `Workspace · profile` (font-family JetBrains Mono, uppercase, tracked
  0.12em), a serif display heading `Your source of truth.` (font-family
  Instrument Serif, 44px, with "source of truth" italicised),
- **And** seven numbered editorial sections appear in order: `№ 01 Identity`,
  `№ 02 Summary`, `№ 03 Experience`, `№ 04 Education`, `№ 05 Skills`,
  `№ 06 Languages`, `№ 07 Projects`,
- **And** sections 03–07 display a count next to the title (mono numerals).

**Scenario 2 — Identity edit + validation preserved.**
- **Given** the profile editor is open and the Identity card is visible,
- **When** the user types `not-an-email` into the Email field and blurs,
- **Then** the field shows the existing red border (now coloured by
  `var(--negative)`), an `.error-message` reading `Invalid email address`
  appears below the field,
- **And** no `PUT /api/users` request is fired (verified by intercept or
  network log),
- **When** the user fixes the email to `me@example.com` and blurs again,
- **Then** the error disappears, the request fires, and the `Saved`
  indicator briefly appears.

**Scenario 2b — Identity 5-field grid shape.**
- **Given** the profile editor is open and `store.loaded === true`,
- **When** the Identity card renders,
- **Then** the card is a flex row with a 96px circular avatar slot on
  the left (verified by computed `width: 96px`, `height: 96px`,
  `border-radius: 50%`),
- **And** to the right of the avatar is a CSS grid with computed
  `grid-template-columns: repeat(2, minmax(0, 1fr))` (or equivalent
  `1fr 1fr`) and `gap: 12px`,
- **And** the grid contains exactly five `.form-row`-level cells in
  this DOM source order: `Full name`, `Email`, `Phone`, `Location`,
  `LinkedIn`,
- **And** no cell exists with an `.eyebrow` label of `Headline`,
  `Title`, or `Headline / title` (the deliberate omission, see
  Must-have 3).

**Scenario 3 — Skills cluster (populated).**
- **Given** the profile has skills `[Python, FastAPI, SQL]`,
- **When** the page renders,
- **Then** the Skills section shows three `.pill` chips (paper-2 background,
  rule-soft border, 12px text), each with a `×` remove affordance,
- **And** the cluster's last child is a dashed `+ add` `.pill`
  (`border-style: dashed`, `color: var(--ink-3)`),
- **When** the user types `Svelte, Rust` into the add input and clicks Add,
- **Then** after the request returns the cluster contains five solid
  `.pill` chips plus the trailing dashed `+ add` pill (the existing
  `createSkills` flow re-loads in alphabetical order), and the input
  clears.

**Scenario 3b — Skills cluster (zero state).**
- **Given** the profile has zero saved skills,
- **When** the page renders,
- **Then** the Skills section's cluster contains exactly one `.pill`
  element — the dashed `+ add` pill (`border-style: dashed`),
- **And** no `.empty-state`-classed element exists inside the Skills
  section (legacy "No skills added yet." copy is gone),
- **When** the user clicks the dashed pill,
- **Then** focus moves to the add-skill input below the cluster.

**Scenario 4 — Languages drag preserved.**
- **Given** the profile has languages `[English C2, French B2, Spanish A2]`
  in that order,
- **When** the user drags Spanish above English,
- **Then** the visual order updates in real time, the
  `PUT /api/languages/reorder` request fires with the new `display_order`
  values, and on reload the order persists.

**Scenario 5 — Experience timeline shape.**
- **Given** the profile has one work experience with
  `start_date: "2023-03"`, `end_date: null`, `is_current: true`,
- **When** the Experience section renders,
- **Then** the row shows three columns: mono date rail `Mar 2023 / — /
  Present` on the left, `{title} · {company}` semibold + location +
  description in the middle, and a `.btn-ghost` `Edit` button on the right,
- **And** the row above and below are separated by `1px solid
  var(--rule-soft)`.

**Scenario 6 — Topbar initials wired (set).**
- **Given** the active profile has `full_name: "Issa Maro"`,
- **When** the Topbar mounts (page load or screen switch back to profile)
  and `profileStore.load()` resolves,
- **Then** the `.topbar-user` circle text equals `IM`,
- **When** the user changes the Identity card's Name field to
  `Ada Lovelace`, blurs the input, the existing 500ms blur-debounce
  elapses, and the resulting `updateUser` request returns successfully,
- **Then** the `.topbar-user` circle text equals `AL` without any
  additional polling, event listener, or manual refresh — Svelte 5
  reactivity propagates the store mutation synchronously to the Topbar
  on the next microtask after `store.save()` resolves.

**Scenario 7 — Topbar initials wired (empty).**
- **Given** the active profile has `full_name: ""` (or no profile row),
- **When** the Topbar mounts and `profileStore.load()` resolves,
- **Then** the `.topbar-user` circle text equals exactly `??`
  (two ASCII question marks — chosen placeholder),
- **And** the circle preserves its 30×30 dimensions, `var(--ink)`
  background, `var(--paper)` color, and `Instrument Serif` italic font.

**Scenario 7b — Initials helper edge cases.**
- **Given** the helper `parseInitials(fullName)` from
  `src/lib/profileStore.svelte.js`,
- **Then** `parseInitials("Issa Maro")` returns `"IM"`,
- **And** `parseInitials("Ada")` returns `"A"`,
- **And** `parseInitials("  Ada   Byron  Lovelace ")` returns `"AL"`
  (whitespace trimmed, first + last token only),
- **And** `parseInitials("")` returns `"??"`,
- **And** `parseInitials("   ")` returns `"??"`.

**Scenario 8 — Legacy color tokens absent.**
- **Given** a grep over the seven listed component files,
- **When** scanning for `--color-border`, `--color-primary-rgb`,
  `--color-text-rgb`, or `#e0e0e0`,
- **Then** zero matches are found inside any `<style>` block or inline
  `style="..."` attribute.

**Scenario 9 — Existing tests pass.**
- **Given** the build succeeds (`bun run build`),
- **When** `pytest tests/` runs,
- **Then** all of the following pass without modification:
  `test_resumes.py`, `test_profile_import.py`, `test_education.py`,
  `test_languages.py`, `test_projects.py`, `test_photos.py`,
  `test_skills.py`, `test_users.py`, `test_work_experiences.py`,
  `test_topbar_shell.py` (with the single `test_user_initials_circle`
  case updated to assert wired behaviour rather than `"LM"`).

**Scenario 10 — Summary section shape + save.**
- **Given** the profile has `summary: "Builder of CV tools."`,
- **When** the editor opens and the page renders,
- **Then** the `№ 02 Summary` section contains a single `.textarea`
  primitive (not the legacy raw `<textarea>` selector) whose value is
  `Builder of CV tools.`,
- **When** the user appends ` Now restyling them.` and blurs,
- **Then** within 500ms+request-time a single `PUT /api/users` request
  fires with `summary: "Builder of CV tools. Now restyling them."`,
- **And** the response succeeds, the `Saved` indicator appears, and
  reloading the page shows the new summary persisted.

**Scenario 11 — Education row shape + edit preserved.**
- **Given** the profile has one education entry:
  `{degree: "MSc", field_of_study: "CS", institution: "Univ. of Lisbon",
   graduation_year: 2018, gpa: 3.8}`,
- **When** the editor opens,
- **Then** the `№ 04 Education` section renders the row as a 3-column
  grid (`70px 1fr auto`, gap 18px, padding `12px 0`): mono year `2018`
  in `var(--ink-3)` 12px on the left, `MSc CS` semibold 13px + line
  `Univ. of Lisbon` `var(--ink-3)` 12px in the middle, `.btn-ghost`
  Edit on the right,
- **When** the user clicks Edit, changes Year to `2019`, and clicks
  Save,
- **Then** a `PUT /api/education/{id}` request fires with
  `graduation_year: 2019`, the form closes, and the row re-renders with
  `2019` on the left rail.

**Scenario 12 — Projects row shape + link + edit preserved.**
- **Given** the profile has one project:
  `{name: "MyCV", technologies: "Svelte, Python, SQLite",
   url: "https://example.com/mycv", description: "Source-of-truth CV."}`,
- **When** the editor opens,
- **Then** the `№ 07 Projects` section renders the row as a 2-column
  grid (`1fr auto`, gap 18px, padding `12px 0`, separated from
  neighbours by `1px solid var(--rule-soft)`): name `MyCV` semibold +
  `Svelte, Python, SQLite · ` followed by an `<a target="_blank"
  rel="noopener">` to the URL in the `var(--ink-3)` sub-line, then a
  `var(--ink-2)` 13px description below; `.btn-ghost` Edit on the right,
- **When** the user clicks Edit and clears the URL field then clicks
  Save,
- **Then** a `PUT /api/projects/{id}` request fires with `url: null`,
  the form closes, and the row re-renders without the link anchor.

## Success criteria (verifiable)

- [ ] **Visual match.** Side-by-side screenshot of the rebuilt editor and
      `design-bundle/project/screen-profile.jsx` shows the same column
      width, header treatment, section numbering, Identity layout,
      Experience timeline shape, Skills pill cluster, Languages 2-column
      grid, and Projects row pattern.
- [ ] **Typography.** Computed style of the page heading is Instrument
      Serif; computed style of `.eyebrow` elements is JetBrains Mono with
      `text-transform: uppercase` and `letter-spacing >= 0.10em`.
- [ ] **Initials wired.** With a known profile `full_name`, the
      `.topbar-user` text equals the derived initials; with an empty
      `full_name`, it equals the placeholder glyph.
- [ ] **Round-trip preserved.** A full manual or automated profile edit
      (touch one field in each of the seven sections, save, reload page)
      shows every change persisted.
- [ ] **Validation preserved.** Submitting an invalid email surfaces
      `Invalid email address`; submitting a work experience with
      end-before-start surfaces `End date must be after start date`.
- [ ] **Legacy tokens gone.** `grep -nE
      '(--color-border|--color-primary-rgb|--color-text-rgb|#e0e0e0)'
      src/components/{ProfileEditor,Section,UserProfile,WorkExperience,Education,Skills,Languages,Projects}.svelte`
      returns zero matches.
- [ ] **Tests pass.** `bun run build && pytest tests/` reports zero
      failures.
- [ ] **New tests.** `tests/test_topbar_shell.py::test_user_initials_circle`
      updated to assert wired behaviour. A new `tests/test_profile_editor_restyle.py`
      asserts: editorial heading present, seven numbered sections present,
      Identity 96px avatar present, Skills pill cluster, Languages 2-column
      grid, no legacy color tokens in computed background-color / border-color
      of the rendered sections.

## Resolved decisions (no open questions remain)

1. **Summary section data ownership.** Resolved → **shared profile
   store** (`src/lib/profileStore.svelte.js`). Both `UserProfile.svelte`
   and the Summary section read/write through the store. UserProfile no
   longer owns its own `data` state; it binds to `store.profile`. This
   is consistent with the Topbar wiring (decision 2 below) — one store,
   one source of truth.

2. **Topbar initials data source.** Resolved → **same shared profile
   store**. Topbar imports `store`, calls `store.load()` on first mount
   if `!store.loaded`, and renders `{store.initials()}`. Svelte 5
   reactivity propagates a `full_name` change to the Topbar without any
   event bus.

3. **Empty-name placeholder glyph.** Resolved → **`??`** (two ASCII
   question marks). Reads as "missing data", explicit, no ambiguity
   with "loading" or "muted". Tested by Scenario 7 and Scenario 7b.

4. **Section primitive — inline vs extracted.** Resolved → **extracted
   component** `src/components/EditorialSection.svelte`. Seven uses in
   one file is enough to justify, and the pattern will likely recur in
   slices 4 (resume preview), 5 (saved jobs), 7 (dashboard), 8 (kanban).

## Non-goals (reaffirmed from refined item)

- No schema changes (no Headline/title field, no new profile attributes).
- No data-layer changes (`src/lib/api.js`, FastAPI endpoints stay put).
- No import-flow rewrites (the ImportModal trigger restyles, but its
  internals don't).
- No AI features (no Rewrite-with-AI button, no word/char counter).
- No section-nav rail or Completeness widget on the left.
- No dark-mode, no mobile/responsive, no live tweaks panel, no sidebar.

## Dependencies & risk

- **Depends on:** slice 1 (editorial-design-system — tokens, primitives,
  fonts) and slice 2 (topbar-shell — `.topbar-user` slot exists with
  styling). Both shipped.
- **Risk — store double-load.** Topbar mounts in `App.svelte`,
  ProfileEditor mounts when `activeTab === 'profile'`. If both call
  `store.load()` unguarded, two `getUser()` requests fire on initial
  load. Mitigation: `store.load()` returns early when `loaded === true`
  AND coalesces concurrent calls via a module-level in-flight promise.
  Test in plan phase.
- **Risk — Section.svelte deletion.** Verified: `Section.svelte` is
  imported only by `src/components/ProfileEditor.svelte:2` (confirmed
  with grep during analysis). Safe to delete once
  `ProfileEditor.svelte` stops importing it. If the plan phase finds an
  unknown caller, leave the file alone and only remove the import.
- **Risk — Test brittleness.** Existing playwright tests depend on
  `.profile-header` class on the import-button wrapper. Keep it
  there (see Must-have 1).
- **Risk — Photo handling.** `UserProfile.svelte`'s `data.photo`
  currently flows through `PhotoUpload.svelte` via `bind:photo`.
  Moving to a store means rewriting that two-way binding to a
  store-getter + store-setter. Estimated complexity: low, but verify
  in plan phase via reading `PhotoUpload.svelte`.
