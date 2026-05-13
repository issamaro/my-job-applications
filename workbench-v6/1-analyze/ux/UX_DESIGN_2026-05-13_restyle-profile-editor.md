# UX_DESIGN — restyle-profile-editor

Date: 2026-05-13
Source: `design-bundle/project/screen-profile.jsx` (slice 3 reference)
Persona: job-seeking professional, desktop, English

## Screens & states

### Screen 1 — Profile editor (primary)

The entire profile editing surface, rendered when `activeTab === 'profile'`.
Below the Topbar (which is 64px tall, already styled by slice 2). The editor
fills the rest of the viewport with `padding: 36px 0` vertical and a centred
940px column.

**Layout:**

```
┌──────────────────────────────────────────────────────────────────┐
│ Topbar (slice 2)                                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│        ┌────────────────────────────────────────────────────┐     │
│        │  WORKSPACE · PROFILE                  [Import JSON]│     │
│        │  Your *source of truth*.                            │     │
│        │  The single profile every tailored CV draws from.   │     │
│        │                                                      │     │
│        │  ─── № 01 Identity ───────────────────────────────  │     │
│        │  ┌────┐  Full name           Email                  │     │
│        │  │ IM │  Phone               Location               │     │
│        │  └────┘  LinkedIn                                   │     │
│        │                                                      │     │
│        │  ─── № 02 Summary ────────────────────────────────  │     │
│        │  [textarea ─────────────────────────────]            │     │
│        │                                                      │     │
│        │  ─── № 03 Experience  3 ──────────────────────────  │     │
│        │  Mar 2023  Staff Eng · Acme                  [Edit] │     │
│        │  — — — — — — — — — — — — — — — — — — — — — — — —   │     │
│        │  Present   Lisbon · Built …                          │     │
│        │  ─── add row separator ─────                         │     │
│        │  [+ Add experience]                                  │     │
│        │                                                      │     │
│        │  ─── № 04 Education  1 ───────────────────────────  │     │
│        │  2018  MSc CS · Univ. of …                  [Edit]  │     │
│        │  [+ Add education]                                   │     │
│        │                                                      │     │
│        │  ─── № 05 Skills  12 ─────────────────────────────  │     │
│        │  ( Python )( FastAPI )( SQL )( Svelte )( + add )    │     │
│        │  [Add skills (comma-separated) ] [Add]               │     │
│        │                                                      │     │
│        │  ─── № 06 Languages  3 ───────────────────────────  │     │
│        │  ┌ English C2     C2 ┐  ┌ French B2     B2 ┐         │     │
│        │  └───────────────────┘  └──────────────────┘         │     │
│        │  ┌ Spanish A2    A2 ┐                                │     │
│        │  └──────────────────┘                                │     │
│        │  [+ Add language]                                    │     │
│        │                                                      │     │
│        │  ─── № 07 Projects  2 ────────────────────────────  │     │
│        │  Project Alpha · Svelte, Python · ↗ link    [Edit]  │     │
│        │  ─── row separator ───                               │     │
│        │  Project Beta · …                            [Edit] │     │
│        │  [+ Add project]                                     │     │
│        └────────────────────────────────────────────────────┘     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Token references (all from `src/styles/global.css`):**

- Page background: `var(--paper)`
- Column max-width: `940px` (matches design `screen-profile.jsx` line 9)
- Column padding: `0 36px`
- Vertical padding: `var(--d-pad)` = 36px
- Section spacing: 36px between sections (matches design line 61, `gap: 36`)
- Header eyebrow: `.eyebrow` class (mono, uppercase, tracked)
- Header display title: `.display` class (Instrument Serif, 44px, line-height 1.05)
- Italic accent: `.serif-italic` class (Instrument Serif italic)
- Section number eyebrow: `.eyebrow.num` (mono, uppercase)
- Section title: `.display` 26px
- Section count: `.num` 12px in `var(--ink-3)`
- Body text: 13px Inter Tight, `var(--ink)` or `var(--ink-2)` for de-emphasis
- Field labels: `.eyebrow` (mono, 10px, uppercase)
- Inputs: `.input` (paper background, rule border, ink text)
- Buttons: `.btn`, `.btn-primary`, `.btn-ghost` primitives

### State: empty

(User has not yet entered any profile data; all sections render their
empty-state forms.)

- **Identity:** avatar circle shows the placeholder text `??` (two ASCII
  question marks, per Resolved Decision 3 in FEATURE_SPEC). Inputs are
  empty; `Full name *` / `Email *` show required markers.
- **Summary:** empty `.textarea` primitive, no placeholder copy added
  (the existing textarea has no placeholder today — preserved).
- **Experience:** section body shows existing `.empty-state` text
  `"No work experience added yet."` (preserved verbatim). The
  `[+ Add experience]` button is below it.
- **Education / Languages / Projects:** same pattern, existing
  empty-state copy preserved verbatim:
  `"No education added yet."`, `"No languages added yet."`,
  `"No projects added yet."`.
- **Skills:** the legacy `<div class="empty-state">No skills added yet.</div>`
  is dropped. The pill cluster ALWAYS renders the dashed `+ add` pill
  (matches `screen-profile.jsx:154-162`), so the zero-skill state shows
  a single dashed pill instead of an empty-state text. The add-skill
  input + Add button remain below the cluster.
- **Page heading + sub-line:** always present regardless of data state.

### State: loading

Each child component manages its own loading skeleton today (`<div
class="skeleton" style="height: 60px;">`). Preserved verbatim. The page
header (eyebrow + display heading + Import JSON button) renders
immediately; the section bodies show skeletons until each fetch resolves.

Acceptable visual: skeleton blocks inside each section body, sized
roughly to the eventual content (60px for a typical row). The section
headers themselves are not skeleton'd — they're static labels.

### State: success (steady)

The state described in the layout above — populated rows in each section,
edit affordances visible, add buttons at the bottom of each list.

After a save, a `Saved` text indicator (`var(--positive)` color, fade-out
after 2s) appears at the bottom of the affected section (existing
behaviour preserved).

### State: error

- **Field-level (validation):** as today — red border on input
  (`var(--negative)`), red error message below. Inputs adopt `.input` so
  the red treatment continues to work via the existing `.error` selector
  (already coloured by `--color-error` which aliases to `--negative`).
- **Network-level (save fails):** existing `<div class="form-error">`
  block renders inside the affected section with the existing copy
  ("Could not save. Please try again."). The `.form-error` block already
  uses `oklch(0.58 0.22 27 / ...)` so no change needed.
- **Network-level (load fails):** existing `.form-error` "Could not load
  profile. Please refresh." copy preserved.

## A11y

- **Document outline:** the page heading is `<h1>` (the
  `Your source of truth.` display title); each section title is `<h2>`
  inside the `EditorialSection` primitive. The eyebrow `№ NN` is visually
  decorative and renders as a sibling `<span>` next to the `<h2>` inside
  a flex row (NOT as a child of the `<h2>`), so a screen reader reading
  the outline hears seven `<h2>` section names without `№ 01`, `№ 02`,
  etc. noise prepended. The count number (when present) is also a
  sibling `<span>`, not part of the heading.
- **Required fields:** `aria-required="true"` and the `.required` label
  decorator (preserves the existing `*` marker via `:after`).
- **Error association:** `aria-describedby` links input to error-message
  id, as today.
- **Drag-to-reorder (Languages):** the existing `draggable="true"` HTML5
  approach is kept. Caveat: it is not keyboard-accessible today (no
  pointerless reorder path); the refined item explicitly preserves
  existing behaviour, so this slice does NOT add keyboard reorder.
  A new note will be filed for a future a11y slice.
- **Decorative avatar:** `aria-hidden="true"` on the `.topbar-user`
  circle (already set). The Identity avatar is also `aria-hidden="true"`
  because the user's full name is rendered as a labelled field directly
  beside it.
- **Focus rings:** existing `:focus` outline via `--color-primary`
  (→ `--accent`) is preserved on `.btn`, `.input`, `.edit-btn`, etc.
- **Color contrast:** spot-check using the existing tokens — `var(--ink)`
  on `var(--paper)` is ~17:1, `var(--ink-3)` on `var(--paper)` is ~5:1,
  both AA-safe. `var(--negative)` (`#dc2626`) on `var(--paper)` is ~5:1
  for error text. No new tokens introduced.

## Keyboard navigation map

Tab order (top to bottom, left to right within rows):

1. Topbar Profile slot (active)
2. Topbar Tailor CV slot
3. Topbar search pill (existing behaviour — focusable but inert click)
4. Topbar user circle — `aria-hidden="true"` so skipped
5. `Import JSON` button (page header)
6. Identity: PhotoUpload trigger
7. Identity: Full name input
8. Identity: Email input
9. Identity: Phone input
10. Identity: Location input
11. Identity: LinkedIn input
12. Summary: textarea
13. Experience rows: each `[Edit]` button in source order
14. Experience: `[+ Add experience]` button
15. Education rows: each `[Edit]`
16. Education: `[+ Add education]`
17. Skills: each `×` remove button in source order
18. Skills: add-skill input → Add button
19. Languages rows: each row is draggable (no Tab focus today — preserve)
20. Languages: each row `[Edit]` button
21. Languages: `[+ Add language]`
22. Projects: each row `[Edit]`
23. Projects: `[+ Add project]`

When editing a row inline (the existing pattern), Tab order moves into
the form (Company → Title → Location → Start → End → checkbox →
description → Save → Cancel → Delete) and stays focused inside the form
until Cancel/Save/Delete is pressed.

`Enter` / `Space` activate `<button>` elements as normal.

## Copy register

Voice: spare, editorial, second-person. Headings use serifs; UI chrome
uses mono uppercase for eyebrows and Inter for buttons/body.

| Slot | Copy | Source |
|---|---|---|
| Page eyebrow | `Workspace · profile` | new |
| Page display title | `Your source of truth.` (with italic on `source of truth`) | new |
| Page sub-line | `The single profile every tailored CV draws from. Edit once, ship anywhere.` | new |
| Import action | `Import JSON` | preserved verbatim |
| Section 01 title | `Identity` | new |
| Section 02 title | `Summary` | new |
| Section 03 title | `Experience` | new |
| Section 04 title | `Education` | new |
| Section 05 title | `Skills` | new |
| Section 06 title | `Languages` | new |
| Section 07 title | `Projects` | new |
| Field labels | `Full name`, `Email`, `Phone`, `Location`, `LinkedIn`, `Summary` (rendered as eyebrows above each input) | new (re-cased) |
| Validation errors | `Required`, `Invalid email address`, `Invalid date`, `End date must be after start date` | preserved verbatim |
| Empty states | `No work experience added yet.`, `No education added yet.`, `No skills added yet.`, `No languages added yet.`, `No projects added yet.` | preserved verbatim |
| Save indicator | `Saved` | preserved verbatim |
| Add buttons | `+ Add experience`, `+ Add education`, `+ Add language`, `+ Add project` | re-cased from current `+ Add`; bare `Add` button on Skills retained |
| Delete confirm | `Delete this work experience?` etc. | preserved verbatim |

## Out-of-bounds (deferred to later slices)

- Section nav rail on left + Completeness widget — surface elements,
  excluded by Scope OUT.
- "Rewrite with AI" button + word/char counter — AI features, excluded.
- "Import from LinkedIn" / "Import from PDF" buttons — keep only
  "Import JSON".
- Headline / title field in Identity — schema change, excluded.
- Keyboard-accessible reorder for languages — a11y slice TBD.
- Mobile / responsive — not in scope until after slice 9.
- Dark mode — out for the entire initiative.
