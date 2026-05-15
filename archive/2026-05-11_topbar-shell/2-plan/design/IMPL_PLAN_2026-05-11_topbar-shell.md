# IMPL_PLAN — topbar-shell

- **Slug:** topbar-shell
- **Date:** 2026-05-11
- **Ceremony:** S (light plan — no separate UX doc; UX folded inline)
- **Source of truth:** `backlog/refined/topbar-shell.md`
- **Design reference:** `design-bundle/project/shell.jsx` (the `Topbar` function and the `MyCVLogo` helper it uses)

## 1. Scope summary

Port the editorial `Topbar` from `shell.jsx` to a Svelte 5 component and mount it as
the persistent app shell in `App.svelte`. Retire `TabNav.svelte`. Keep the existing
`activeTab` + `switchTab` event contract; map the two existing screens
(`'profile'` → profile slot, `'resume'` → tailor slot). The four nav slots without
a screen (`dashboard`, `pipeline`, `jobs`, `interview`) render disabled and
non-clickable (decision Q0.2, 2026-05-11).

Logo mark = `MyCVLogo` only (wordmark with cobalt dot). No separate `Sigil` left
of the wordmark (decision Q0.3, 2026-05-11).

Light-only, desktop-only, no router, no mobile drawer.

## 2. Library notes

None. Svelte 5 runes (`$props`, `$state`, `$effect`) are already used throughout
`src/components/`. No new dependency is added.

## 3. Files — file-by-file plan

### 3.1 CREATE — `src/components/Topbar.svelte`

A single-file Svelte 5 component (~140 LOC including scoped styles). Header
follows lean-code rules (two-line file header, no inline comments, no abbreviations).

**Props:**

| Name | Type | Purpose |
|---|---|---|
| `activeTab` | `'profile' \| 'resume'` | Legacy active-tab value owned by `App.svelte`. |
| `onTabChange` | `(tab: string) => void` | Callback fired when an enabled slot is clicked. |

**Internal data — the slot table.** Hard-coded array in the script block:

```js
const slots = [
  { id: 'dashboard', label: 'Dashboard',     tab: null },
  { id: 'pipeline',  label: 'Pipeline',      tab: null },
  { id: 'jobs',      label: 'Saved jobs',    tab: null },
  { id: 'profile',   label: 'Profile',       tab: 'profile' },
  { id: 'tailor',    label: 'Tailor CV',     tab: 'resume' },
  { id: 'interview', label: 'Interview prep', tab: null },
];
```

Order matches `shell.jsx` line 102–108 (`dashboard, pipeline, jobs, profile, tailor, interview`).
A slot is enabled iff `tab` is non-null.

**Derived value — the active slot id.** A `$derived` expression:

```js
const activeSlotId = $derived(slots.find(s => s.tab === activeTab)?.id);
```

No verb-named helper function: the derivation is one line and reads as data.

**Click handling.** Inline arrow in markup: `onclick={() => slot.tab && onTabChange(slot.tab)}`.
For disabled slots (`tab: null`), the `&&` short-circuits — click is a no-op. Plus
`aria-disabled={slot.tab === null}` and `tabindex={slot.tab === null ? -1 : 0}`
to keep them out of keyboard focus order.

**Markup structure** (mirrors `shell.jsx` lines 109–155):

```
<header class="topbar">
  <div class="topbar-brand"><MyCVLogo/></div>
  <nav class="topbar-nav">
    {#each slots as slot}
      <button class="topbar-slot" class:active class:disabled .../>
    {/each}
  </nav>
  <div class="topbar-right">
    <div class="topbar-search">🔍 Find a job, resume… <kbd>⌘K</kbd></div>
    <div class="topbar-user">LM</div>
  </div>
</header>
```

Each slot is a `<button type="button">`, not a `<div>` — the JSX uses `<div>` with
`cursor: pointer`, but Svelte/native semantics need a real button so the BDD
scenario "clicks Tailor CV" maps to a clickable element with keyboard support.

**MyCVLogo (inline in the same file).** A small `{#snippet}` or a sub-component-free
local block: italic "my" + roman "CV" + cobalt dot positioned via `transform: translateY(-2px)`,
all using `var(--font-display)` and `var(--accent)` — pixel-for-pixel match of
shell.jsx lines 8–16.

**Styles.** Scoped `<style>` block. Token consumers only (no hardcoded hex). The
visual targets from shell.jsx lines 110–115:

- `height: 64px`
- `padding: 0 32px`
- `border-bottom: 1px solid var(--rule)`
- `background: var(--paper)`
- `display: flex; align-items: center; gap: 36px`

Slot active state (shell.jsx lines 122–129):

- `color: var(--ink)`, `font-weight: 500`, `border-bottom: 1px solid var(--ink)`,
  `margin-bottom: -1px` (the underline overlaps the header's bottom rule).

Slot disabled state:

- `color: var(--ink-4)`, `cursor: not-allowed`, `pointer-events: none`.

Search pill (shell.jsx lines 135–146): `padding: 6px 10px`, `background: var(--paper-2)`,
`border: 1px solid var(--rule)`, `border-radius: var(--r-sm)`, `min-width: 200px`.
The `⌘K` hint uses `class="num"` for the tabular-num mono treatment that
`global.css` line 113 already defines.

User-initials circle (shell.jsx lines 147–152): `30×30`, `border-radius: 50%`,
`background: var(--ink)`, `color: var(--paper)`, italic Instrument Serif `LM`.

### 3.2 MODIFY — `src/App.svelte`

**Before** (lines 21–32):

```svelte
<div class="container">
  <header class="header">
    <h1>MyCV</h1>
    <TabNav {activeTab} onTabChange={handleTabChange} />
  </header>
  {#if activeTab === 'profile'} <ProfileEditor /> {/if}
  {#if activeTab === 'resume'}  <ResumeGenerator /> {/if}
</div>
```

**After:**

```svelte
<Topbar {activeTab} onTabChange={updateActiveTab} />
<div class="container">
  {#if activeTab === 'profile'} <ProfileEditor /> {/if}
  {#if activeTab === 'resume'}  <ResumeGenerator /> {/if}
</div>
```

Changes:

1. Replace `import TabNav` with `import Topbar from './components/Topbar.svelte'`.
2. Rename `handleTabChange` → `updateActiveTab` (lean-code: `handle` is forbidden;
   `update` is the verb for "modify existing data"). Same body.
3. **Also rename the inner `handleSwitchTab` (line 13) → `updateTabFromEvent`.**
   That inner function is the listener bound inside the `$effect`, kept in scope
   so add/remove pair share the same reference. Lean-code: same rule — `handle`
   is forbidden; `update` matches its job (write to `activeTab` from the event's
   `detail`). Body unchanged.
4. Topbar renders **outside** `.container` so it spans full viewport width. The
   container keeps its centered max-width for the page body below.
5. The two existing `{#if activeTab === ...}` blocks stay unchanged.
6. The `$effect` that listens for the `switchTab` window event stays — that
   contract is consumed by `ResumeGenerator.svelte:125` and is not part of this slice.

### 3.3 MODIFY — `src/styles/global.css`

Two small adjustments so the topbar can span edge-to-edge:

1. `body { padding: var(--spacing-section); }` → `body { padding: 0; }` (line 152).
2. `.container { max-width: 800px; margin: 0 auto; }` →
   `.container { max-width: 800px; margin: 0 auto; padding: var(--spacing-section); }`.

Net effect: the topbar gets full width; existing page content below it keeps the
same horizontal padding it had before.

The legacy `.header` class (line 180–185) is now unused — leave it in place this
slice (slices 3–9 will trip over it if it's actually referenced elsewhere; cheap
to leave, free to remove later if the design-tokens test still passes).

### 3.4 MODIFY — `tests/test_design_tokens.py` (pre-existing red test, opportunistic fix)

The slice-1 OKLCH refactor (`refactor(styles): convert color tokens to oklch
color space`, commit `ffdc989`) broke this test: Chromium now serializes
`getComputedStyle(body).backgroundColor` as the literal string `oklch(0.97 0.01 260)`
rather than the resolved `rgb(244, 241, 236)` the test asserts. Confirmed red by
running `uv run pytest tests/test_design_tokens.py` on 2026-05-11 18:57 (current
HEAD `ffdc989`).

This is **not** my slice's concern in spec, but is fixed here so:
(a) the Phase 3 test run has a green baseline, and
(b) the slice-2 inspector verdict isn't muddied by a known-unrelated regression.

Changes (line 72–73):

- `assert styles["backgroundColor"] == "rgb(244, 241, 236)"` →
  `assert styles["backgroundColor"] == "oklch(0.97 0.01 260)"`
- `assert styles["color"] == "rgb(26, 24, 20)"` →
  `assert styles["color"] == "oklch(0.16 0.04 265)"`

Both target values are the literal `--paper` / `--ink` declarations in
`src/styles/global.css:15,20`. The header (line 1–2) and rest of the file stay
unchanged.

### 3.5 DELETE — `src/components/TabNav.svelte`

After App.svelte stops importing it, the file is dead. Delete it (lean-code:
"if you are certain that something is unused, you can delete it completely").
No other consumer exists — verified by `grep -rn TabNav src/` returning only the
two App.svelte references that this slice removes.

## 4. Active-tab ↔ slot mapping (decision table)

| Legacy `activeTab` | Slot id | Slot label | Renders |
|---|---|---|---|
| `'profile'` | `profile` | Profile | `<ProfileEditor />` |
| `'resume'` | `tailor` | Tailor CV | `<ResumeGenerator />` (placeholder until slice 6) |
| n/a (disabled) | `dashboard` | Dashboard | — (slice 7) |
| n/a (disabled) | `pipeline` | Pipeline | — (slice 8) |
| n/a (disabled) | `jobs` | Saved jobs | — (slice 5) |
| n/a (disabled) | `interview` | Interview prep | — (slice 9) |

## 5. UX behaviour (folded inline — no separate UX doc for S)

- **Active treatment.** Single ink-colored slot label with a 1px ink underline.
  Hover on inactive enabled slots: color shifts from `--ink-3` to `--ink-2` (no
  underline preview). Active slot uses `font-weight: 500`, all others `400`.
- **Disabled slots.** Rendered, but `aria-disabled="true"`, `pointer-events: none`,
  `cursor: not-allowed`, color `--ink-4`. Excluded from keyboard tab order (`tabindex="-1"`).
- **Keyboard nav.** Tab moves focus across enabled slots in DOM order
  (profile, tailor). Enter/Space on a focused slot fires `onTabChange`.
- **Search pill & user circle.** Decorative this slice — no click handler, no
  focus state, no input behaviour. (See §6 known compromises.)
- **Empty state.** Not applicable — the topbar always has six slots regardless of
  app state.
- **Loading state.** Not applicable — the topbar is static markup; nothing async.
- **Error state.** Not applicable — no remote dependency.
- **a11y.**
  - `<header role="banner">` (implicit from element semantics).
  - `<nav aria-label="Primary">` wrapping the slot list.
  - Each slot is a `<button type="button">` so screen readers announce them as
    actionable controls and Enter/Space activates them by default.

## 6. Known compromises (recorded for handover to later slices)

| # | Item | Carry to slice |
|---|---|---|
| 1 | User-initials circle hardcoded `LM` (matches shell.jsx mock). | slice 3 (`restyle-profile-editor` — wire to real profile data). |
| 2 | Search pill is decorative — no `⌘K` palette, no input focus. | slice 6 (`tailor-cv-screen`) or a future palette slice. |
| 3 | Four disabled nav slots are visually present. Each must be enabled when its slice ships. | slices 5 (jobs), 7 (dashboard), 8 (pipeline), 9 (interview). |
| 4 | Legacy `.header` CSS class kept in `global.css` for now. | Any later slice that removes it (cheap to leave). |
| 5 | Sigil mark is NOT rendered left of the wordmark (Q0.3 decision, 2026-05-11: "wordmark only, match shell.jsx"). The refined doc's "small sigil mark + MyCV wordmark" phrasing is resolved in favor of shell.jsx's actual `Topbar`, which renders only `MyCVLogo`. The `Sigil` component is preserved for company badges elsewhere. | n/a — closed by Q0.3. |

Record these as the slice-2 outputs in `workbench/4-ship/changes/CHANGE_LOG_2026-05-11_topbar-shell.md` (change-logger handles automatically).

## 7. Risks

1. **`switchTab` window event regression.** `ResumeGenerator.svelte:125` dispatches
   `new CustomEvent('switchTab', { detail: 'profile' })` after PDF generation. The
   `$effect` in `App.svelte` lines 12–18 still listens for it, so this contract
   survives — Topbar does not need to dispatch the event. Verify in test.
2. **Body padding flip.** Moving padding from `body` to `.container` changes the
   layout for any page that doesn't use `.container`. Grep confirms only
   `App.svelte` wraps content in `.container`, but the test suite must catch any
   regression.
3. **Design-tokens smoke test (`tests/test_design_tokens.py`) reads
   `getComputedStyle(document.body)`.** Asserting `padding: 0` is not in the
   current assertions, but changing body padding could shift the rendered
   `lineHeight` for elements inside body if any default-font-size cascade
   interacts. Run the existing test before and after to confirm no drift.
4. **Disabled slots — hover/focus discipline.** With `pointer-events: none` and
   `tabindex="-1"` they're inert. But ensure the active styling logic (`class:active`)
   only triggers for slots whose `tab` matches `activeTab` — never for disabled
   slots (whose `tab === null` so `null === activeTab` is false for valid values).
5. **Font loading.** `Instrument Serif` is already linked via `public/index.html`
   (`<link rel="stylesheet" href="https://fonts.googleapis.com/css2?…Instrument+Serif…">`
   — note: linked, not `rel="preload"`). No new font subset needed; the existing
   stylesheet covers all weights the Topbar uses (italic 400 for "my" + roman 600
   for "CV").

## 8. Test plan

**New test file:** `tests/test_topbar_shell.py` — playwright smoke (mirrors the
shape of `test_design_tokens.py`):

- **`test_topbar_renders_at_top`** — Topbar `<header>` is the first child of `<body>`;
  contains `MyCV` wordmark text and all six slot labels (`Dashboard`, `Pipeline`,
  `Saved jobs`, `Profile`, `Tailor CV`, `Interview prep`).
- **`test_no_legacy_tab_nav`** — `document.querySelector('.tab-nav')` returns null;
  no `<button>Resume Generator</button>` from the old TabNav remains.
- **`test_active_slot_treatment`** — On load (activeTab='profile'), the Profile
  slot button's computed `color` equals the wordmark's computed `color` (both
  consume `--ink`), AND the Profile slot's computed `borderBottomWidth` is `1px`.
  Using color-equivalence rather than a hard-coded RGB sidesteps Chromium's
  literal `oklch(...)` serialization. Inactive slots' computed color does NOT
  equal the wordmark's.
- **`test_disabled_slots_inert`** — Each of Dashboard / Pipeline / Saved jobs /
  Interview prep has `aria-disabled="true"` AND `tabindex="-1"` AND a computed
  `pointerEvents: none`. Clicking any of them keeps `<title>` and the rendered
  page body unchanged from the pre-click state (no view swap).
- **`test_click_tailor_routes`** — Click `Tailor CV` → the Resume Generator
  placeholder renders (assert a known unique selector from ResumeGenerator.svelte
  is now in the DOM); active treatment moves to `Tailor CV` (same color-equivalence
  assertion as test 3, now applied to the Tailor slot).

The existing `tests/test_design_tokens.py` must still pass — re-run as a regression
guard.

## 9. Implementation order (suggested)

1. Create `src/components/Topbar.svelte` standalone, with mocked `activeTab='profile'`
   prop for visual inspection.
2. Wire into `src/App.svelte`, remove TabNav import + markup, rename
   `handleTabChange` → `updateActiveTab` AND `handleSwitchTab` → `updateTabFromEvent`.
3. Update `src/styles/global.css` body+container padding.
4. Update `tests/test_design_tokens.py` expected oklch values (pre-existing fix).
5. Delete `src/components/TabNav.svelte`.
6. Build (`bun run build` or `npm run build`), open `public/index.html` to eyeball.
7. Add `tests/test_topbar_shell.py`, run pytest.
