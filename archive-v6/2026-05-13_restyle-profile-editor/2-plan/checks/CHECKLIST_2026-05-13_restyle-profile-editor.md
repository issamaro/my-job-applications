feature: restyle-profile-editor
date: 2026-05-13
total_checkboxes: 98
derived_from: IMPL_PLAN_2026-05-13_restyle-profile-editor.md, SVELTE5_NOTES_2026-05-13_restyle-profile-editor.md, UX_DESIGN_2026-05-13_restyle-profile-editor.md, FEATURE_SPEC_2026-05-13_restyle-profile-editor.md

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` (verify: `cat .python-version`)  → source: IMPL_PLAN "Build & verify steps" + .python-version file
- [ ] Runtime version pinned: `package.json` `svelte` = `^5.0.0` (verify: `npm list svelte` or `cat package.json`)  → source: SVELTE5_NOTES "Version compatibility" — "All patterns below require Svelte 5.x"
- [ ] Virtual environment created and activated (verify: `which python` points to project venv)  → source: pyproject.toml `requires-python = ">=3.13"`

---

## Section 1 — Dependencies

- [ ] `svelte ^5.0.0` present in `package.json` devDependencies (verify: `npm list svelte`)  → source: SVELTE5_NOTES "Version compatibility" — runes API ($state, $derived, $effect, $props) stable as of 5.x
- [ ] `rollup ^4.0.0` present in `package.json` devDependencies (verify: `npm list rollup`)  → source: IMPL_PLAN "Build & verify steps" step 17 — `bun run build`
- [ ] `rollup-plugin-svelte ^7.2.0` present in `package.json` devDependencies (verify: `npm list rollup-plugin-svelte`)  → source: IMPL_PLAN build pipeline (package.json)
- [ ] `playwright >=1.40.0` present in `pyproject.toml` dependencies (verify: `uv tree --package playwright`)  → source: IMPL_PLAN "Tests" section — Playwright suite `test_profile_editor_restyle.py`
- [ ] `pytest >=8.0.0` present in `pyproject.toml` dev dependencies (verify: `uv tree --package pytest`)  → source: IMPL_PLAN "Build & verify steps" step 17 — `pytest tests/`
- [ ] `fastapi >=0.100.0` present in `pyproject.toml` dependencies (verify: `uv tree --package fastapi`)  → source: IMPL_PLAN "Tests" — tests serve `public/` and rely on live bundle against backend
- [ ] `cropperjs ^2.0.0` present in `package.json` dependencies (pre-existing entry in `package.json:11`; **currently unused by any code path** — `grep -rn cropperjs src/ public/ rollup.config.js` returns zero matches, PhotoUpload uses native `FileReader` not cropperjs). This checklist item is a sanity-check that the entry wasn't accidentally removed; do NOT use this as evidence that cropperjs is wired in. Verify: `npm list cropperjs`  → source: `package.json:11` — pre-existing dependency, unused

---

## Section 2 — Syntax (Svelte 5 rune patterns)

### Pattern 1 — Module-scoped runes singleton

- [ ] `export const store = $state({...})` form used at `src/lib/profileStore.svelte.js` (not `export let` with bare primitives)  → source: SVELTE5_NOTES Pattern 1 — "export const store = $state({...}) form is simpler and canonical"; IMPL_PLAN File 1 exports
- [ ] File extension is `.svelte.js` (not `.js`) on `src/lib/profileStore.svelte.js`  → source: SVELTE5_NOTES "Version compatibility" — "all patterns below require .svelte.js / .svelte.ts file extensions for non-component reactive modules"
- [ ] No bare primitive `export let x = $state(0)` for cross-module-tracked values  → source: SVELTE5_NOTES Pattern 1 — "Pitfall: Do NOT export let count = $state(0) with a bare primitive"

### Pattern 2 — Cross-component reactivity

- [ ] `Topbar.svelte` reads `store.profile.full_name` (via `readInitials()` / `$derived(readInitials())`) without any pub-sub wiring  → source: SVELTE5_NOTES Pattern 2 — "any component that reads store.profile.full_name in its template will reactively re-render when that property mutates"; IMPL_PLAN File 3
- [ ] `UserProfile.svelte` reads `store.profile.*` (not local `data` state) for field binding  → source: SVELTE5_NOTES Pattern 2; IMPL_PLAN File 4 change 1
- [ ] `ProfileEditor.svelte` writes `store.profile.summary` directly on blur  → source: SVELTE5_NOTES Pattern 2; IMPL_PLAN File 6 change 4

### Pattern 3 — `$effect` on mount for async load

- [ ] `Topbar.svelte` uses `$effect(() => { void readProfile(); })` (not async $effect, not onMount)  → source: SVELTE5_NOTES Pattern 3 — "void suppresses the Promise return value; $effect does not accept an async callback directly"; IMPL_PLAN File 3 change 2
- [ ] `UserProfile.svelte` uses `$effect(() => { void readProfile(); return () => { cleanup }; })` with cleanup for saveTimeout  → source: SVELTE5_NOTES Pattern 3 — "Return a function from the callback for cleanup"; IMPL_PLAN File 4 change 1
- [ ] No `async` keyword on any `$effect` callback in any modified file  → source: SVELTE5_NOTES Pattern 3 — "returning a Promise instead of undefined | (() => void) is incorrect"

### Pattern 4 — In-flight promise coalescing

- [ ] `_pending` in `profileStore.svelte.js` is a module-level `let` (not `$state`, not reactive)  → source: SVELTE5_NOTES Pattern 4 — "_pending is a module-level let (not $state) — it is not reactive, just a guard"
- [ ] `readProfile()` returns early if `_pending` is set, returns the existing promise  → source: SVELTE5_NOTES Pattern 4; IMPL_PLAN File 1 `readProfile()` body
- [ ] `readProfile()` returns early if `store.loaded === true`  → source: IMPL_PLAN File 1 — "if (store.loaded) return"; FEATURE_SPEC Must-have 10 — "exactly one getUser() request fires per page session"

### Pattern 5 — Deep mutation via proxy

- [ ] `Object.assign(store.profile, result)` used (not `store.profile = result`) in `readProfile()`  → source: SVELTE5_NOTES Pattern 5 — "Mutating store.profile.full_name is reactive without spreading. Svelte wraps the object in a Proxy"; IMPL_PLAN File 1 note
- [ ] `bind:value={store.profile.full_name}` (and other fields) used in `UserProfile.svelte` input elements  → source: SVELTE5_NOTES Pattern 8 — "bind:value accepts any assignable expression, including a property path into a reactive $state object"
- [ ] No `$state.raw` used on `store.profile` (would break deep reactivity)  → source: SVELTE5_NOTES Pattern 5 — "$state.raw — NOT deeply reactive: property mutation has no effect"

### Pattern 6 — Snippets / render children

- [ ] `EditorialSection.svelte` renders `{@render children()}` as the section body slot  → source: SVELTE5_NOTES Pattern 6 — snippets are "content-projection tool"; IMPL_PLAN File 2 markup; FEATURE_SPEC Must-have 2
- [ ] No deprecated `<slot>` used in `EditorialSection.svelte`  → source: SVELTE5_NOTES "Deprecated to avoid" — "slot-based content passing deprecated in Svelte 5, superseded by snippets"

### Pattern 7 — Playwright DOM-only assertions

- [ ] `test_profile_editor_restyle.py` tests use `page.query_selector` / `element.text_content()` (DOM assertions), NOT `page.evaluate` to read module-scoped `$state` objects  → source: SVELTE5_NOTES Pattern 7 — "page.evaluate() can read DOM output but cannot directly import ES module state without an exposed global"
- [ ] `parseInitials` edge cases tested through DOM output (`.topbar-user` text content) under a mocked `/api/users` GET via `page.route`; never via direct function call  → source: SVELTE5_NOTES Pattern 7; IMPL_PLAN "Tests" — route-interception approach

### Pattern 8 — `$bindable()` for child components

- [ ] `WorkExperience.svelte` declares `let { count = $bindable(0) } = $props()`  → source: IMPL_PLAN File 7 change 2; IMPL_PLAN File 6 — "each child component exposes a count $bindable() prop"
- [ ] `Education.svelte` declares `let { count = $bindable(0) } = $props()`  → source: IMPL_PLAN File 8
- [ ] `Skills.svelte` declares `let { count = $bindable(0) } = $props()`  → source: IMPL_PLAN File 9 change 2
- [ ] `Languages.svelte` declares `let { count = $bindable(0) } = $props()`  → source: IMPL_PLAN File 10 change 2
- [ ] `Projects.svelte` declares `let { count = $bindable(0) } = $props()`  → source: IMPL_PLAN File 11
- [ ] `PhotoUpload.svelte` confirms `photo` prop declared with `$bindable()` (pre-condition check before File 4 edit)  → source: IMPL_PLAN File 5 — "Plan-phase verification: read PhotoUpload.svelte and confirm whether photo is currently declared as $bindable()"

### Pattern 9 — `$effect` writeback to `$bindable` count prop (hazards)

- [ ] Each child's count-effect is **write-only on `count`**: the body matches `$effect(() => { count = items.length; })` and never reads `count` (forbidden shape: `count = count + items.length` — would trigger `effect_update_depth_exceeded`)  → source: SVELTE5_BINDABLE_NOTES Q5 — "Concrete loop that WOULD occur (to avoid): `count = items.length + count;` reads count → writes count → re-runs → error"
- [ ] `WorkExperience.svelte` count-effect reads only `items`, writes only `count`  → source: SVELTE5_BINDABLE_NOTES Q3 — "The effect dependency is `items` (read). The write target is `count`. These are different reactive values."
- [ ] `Education.svelte` count-effect reads only `items`, writes only `count`  → source: SVELTE5_BINDABLE_NOTES Q3
- [ ] `Skills.svelte` count-effect reads only `items`, writes only `count`  → source: SVELTE5_BINDABLE_NOTES Q3
- [ ] `Languages.svelte` count-effect reads only `items`, writes only `count`  → source: SVELTE5_BINDABLE_NOTES Q3
- [ ] `Projects.svelte` count-effect reads only `items`, writes only `count`  → source: SVELTE5_BINDABLE_NOTES Q3
- [ ] No `untrack()` call wraps the `items.length` read inside the count-effect (would be unnecessary noise; the effect tracks `items` legitimately)  → source: SVELTE5_BINDABLE_NOTES Q3 — "untrack() is therefore not required for this specific shape"
- [ ] Console is clean after `bun run build` + opening editor: no `ownership_invalid_mutation`, no `effect_update_depth_exceeded`, no `binding_property_non_reactive` warning  → source: SVELTE5_BINDABLE_NOTES Q2 hazard table

---

## Section 3 — UX states (per screen / section)

### Identity section (№ 01)

- [ ] Empty state: avatar circle shows `??` when `store.profile.full_name` is `""` or whitespace  → source: UX_DESIGN "State: empty" — "avatar circle shows the placeholder text ?? (two ASCII question marks)"; FEATURE_SPEC Scenario 7
- [ ] Loading state: `{#if !store.loaded && !store.error}` renders three `.skeleton` rows (height 40px each) in `UserProfile.svelte`  → source: UX_DESIGN "State: loading" — "skeleton blocks inside each section body"; IMPL_PLAN File 4 change 3; FEATURE_SPEC Must-have 13
- [ ] Error state: `{:else if store.error}` renders `<div class="form-error">{store.error}</div>` with copy `"Could not load profile. Please refresh."`  → source: UX_DESIGN "State: error" — "Network-level (load fails)"; FEATURE_SPEC Must-have 13
- [ ] Success state: when `store.loaded === true` and `store.error === null`, Identity card renders with avatar + 5-field grid  → source: UX_DESIGN "State: success (steady)"; FEATURE_SPEC Scenario 2b
- [ ] Identity card is flex row: avatar 96px × 96px circular left, fields grid right  → source: UX_DESIGN Screen 1 layout; FEATURE_SPEC Must-have 3 — "96px circular avatar slot on the left"
- [ ] Identity field grid is `1fr 1fr` with `gap: 12px`, contains exactly five `.form-row` cells: Full name, Email, Phone, Location, LinkedIn (in that source order)  → source: FEATURE_SPEC Scenario 2b; IMPL_PLAN File 4 change 3
- [ ] No `.form-row` with label `Headline`, `Title`, or `Headline / title` exists in the Identity grid  → source: FEATURE_SPEC Scenario 2b — "deliberate omission"; Must-have 3
- [ ] `Full name` and `Email` labels have `.required` decorator (renders `*` via `:after`) and input has `aria-required="true"`  → source: UX_DESIGN "State: empty" — "show required markers"; IMPL_PLAN File 4 change 3
- [ ] After valid save, `Saved` indicator appears at `var(--positive)` color and fades after 2s  → source: UX_DESIGN "State: success (steady)" — "Saved text indicator (var(--positive) color, fade-out after 2s)"
- [ ] Field validation error state: red border via `.error` class + `.error-message` text `Required` / `Invalid email address` below the field; no PUT fires  → source: UX_DESIGN "State: error" — "red border on input (var(--negative))"; FEATURE_SPEC Scenario 2

### Summary section (№ 02)

- [ ] Empty state: `.textarea` primitive renders with empty value; no placeholder copy  → source: UX_DESIGN "State: empty" — "empty .textarea primitive, no placeholder copy added"
- [ ] Loading state: Summary shows empty `.textarea` until `store.loaded === true` (no skeleton of its own)  → source: FEATURE_SPEC Must-have 13 — "Summary section does NOT render skeletons or error UI of their own. Summary section shows an empty .textarea until store.loaded === true"
- [ ] Success state: textarea value equals `store.profile.summary`; blur + 500ms debounce fires `writeProfile()`  → source: FEATURE_SPEC Scenario 10; IMPL_PLAN File 6 change 4
- [ ] Error state on save: `store.error` set to `"Could not save. Please try again."` visible to both Identity and Summary (shared store)  → source: UX_DESIGN "State: error" — "Network-level (save fails)"; IMPL_PLAN File 1 `writeProfile()` catch

### Experience section (№ 03)

- [ ] Empty state: existing `"No work experience added yet."` text preserved verbatim inside section body  → source: UX_DESIGN "State: empty" — "existing .empty-state text 'No work experience added yet.' (preserved verbatim)"
- [ ] Loading state: existing skeleton block (`<div class="skeleton" style="height: 60px;">`) inside section body  → source: UX_DESIGN "State: loading" — "Each child component manages its own loading skeleton today. Preserved verbatim."
- [ ] Success state: rows render as 3-column grid (`110px 1fr auto`, gap 18px, padding 16px 0); date rail on left (mono), body in middle, `.btn-ghost` Edit right  → source: FEATURE_SPEC Must-have 5; IMPL_PLAN File 7 change 3
- [ ] Error state: existing error display inside WorkExperience preserved; no restyle  → source: FEATURE_SPEC Must-have 12 — "Every existing validation error still surfaces against the new input styling"
- [ ] Row separator is `1px solid var(--rule-soft)` above every row except the first (`.not-first` class)  → source: FEATURE_SPEC Must-have 5; IMPL_PLAN File 7 change 3 — `.exp-row.not-first { border-top: 1px solid var(--rule-soft); }`
- [ ] `[+ Add experience]` button uses `.btn` class  → source: IMPL_PLAN File 7 change 3; UX_DESIGN Copy register
- [ ] Both rendered blocks in `WorkExperience.svelte` are restyled: the primary `{#each}` list (~lines 165-307) AND the inline `{#if showForm && !editingId}` "Add new" block (~lines 309-428). Every `<input>` and `<textarea>` inside the add-form block receives the new `.input` / `.textarea` classes; no `<input>` inherits legacy form styling  → source: IMPL_PLAN File 7 Touch points (MN2 fix); PLAN_VERIFIED MN2 — "the plan's 'Replace the row markup' instruction may overwrite the existing `{#each}` block but not address the secondary add-form block"

### Education section (№ 04)

- [ ] Empty state: existing `"No education added yet."` text preserved verbatim  → source: UX_DESIGN "State: empty"
- [ ] Loading state: existing skeleton preserved  → source: UX_DESIGN "State: loading"
- [ ] Success state: rows render as 3-column grid (`70px 1fr auto`, gap 18px, padding 12px 0); mono year left, degree+institution middle, `.btn-ghost` Edit right  → source: FEATURE_SPEC Must-have 6; Scenario 11; IMPL_PLAN File 8
- [ ] Error state: existing validation errors preserved against new `.input` styling  → source: FEATURE_SPEC Must-have 12
- [ ] `[+ Add education]` button uses `.btn` class  → source: IMPL_PLAN File 8; UX_DESIGN Copy register

### Skills section (№ 05)

- [ ] Empty state (zero skills): cluster contains exactly one `.pill` — the dashed `+ add` pill; NO `.empty-state` element with text `"No skills added yet."`  → source: UX_DESIGN "State: empty" — "legacy div.empty-state is dropped. The pill cluster ALWAYS renders the dashed + add pill"; FEATURE_SPEC Scenario 3b
- [ ] Loading state: existing skeleton preserved (Skills manages its own)  → source: UX_DESIGN "State: loading" — "Each child component manages its own loading skeleton"
- [ ] Success state: saved skills render as `.pill` chips (paper-2 bg, rule-soft border, r-sm radius, 12px, gap 6px); cluster ends with dashed `+ add` pill  → source: FEATURE_SPEC Must-have 7; Scenario 3; IMPL_PLAN File 9 change 3
- [ ] Error state: existing Skills error display preserved  → source: FEATURE_SPEC Must-have 12
- [ ] Each skill chip has `×` remove button with `aria-label="Remove {item.name}"`  → source: IMPL_PLAN File 9 change 3; UX_DESIGN Keyboard navigation map item 17
- [ ] Clicking dashed `+ add` pill focuses the add-skill input below  → source: FEATURE_SPEC Scenario 3b; IMPL_PLAN File 9 change 4 — `focusInput()`
- [ ] Skill pills override `.pill` global class for `font-family`, `text-transform`, `letter-spacing` (sentence-case 12px Inter, not 10px mono uppercase)  → source: IMPL_PLAN File 9 note — "Skills overrides font-family, text-transform, and letter-spacing back to body text"

### Languages section (№ 06)

- [ ] Empty state: existing `"No languages added yet."` text preserved verbatim  → source: UX_DESIGN "State: empty"
- [ ] Loading state: existing skeleton preserved  → source: UX_DESIGN "State: loading"
- [ ] Success state: 2-column grid (`1fr 1fr`, gap 8px) of `.lang-card` elements; each shows name (semibold 13px) + full CEFR label (`ink-3` 11px) left, CEFR code (mono 11px) right, `.btn-ghost` Edit  → source: FEATURE_SPEC Must-have 8; IMPL_PLAN File 10 change 3
- [ ] Error state: existing Languages error preserved  → source: FEATURE_SPEC Must-have 12
- [ ] `readCefrLabel(level)` helper used (not inline ternary); verb prefix `read` per lean-code  → source: IMPL_PLAN File 10 change 3 — "Use readCefrLabel(level)"
- [ ] Drag-to-reorder preserved: `draggable="true"` on `.lang-card`, drag handlers intact, cursor: grab  → source: FEATURE_SPEC Scenario 4; IMPL_PLAN File 10 change 4

### Projects section (№ 07)

- [ ] Empty state: existing `"No projects added yet."` text preserved verbatim  → source: UX_DESIGN "State: empty"
- [ ] Loading state: existing skeleton preserved  → source: UX_DESIGN "State: loading"
- [ ] Success state: rows render as 2-column grid (`1fr auto`); name semibold + technologies · URL link (ink-3 sub-line) + description (ink-2 13px); `.btn-ghost` Edit right  → source: FEATURE_SPEC Must-have 9; Scenario 12; IMPL_PLAN File 11
- [ ] Error state: existing Projects error preserved  → source: FEATURE_SPEC Must-have 12
- [ ] URL renders as `<a target="_blank" rel="noopener">` when `item.url` is set  → source: FEATURE_SPEC Scenario 12; IMPL_PLAN File 11 markup

---

## Section 4 — Tests

### Modified test

- [ ] `tests/test_topbar_shell.py::test_user_initials_circle` updated: installs a Playwright route via `create_users_mock(page, "Issa Maro")` (or inline equivalent) that fulfils `GET /api/users` with a synthetic profile JSON, gates on `wait_for_function(...textContent === 'IM')`, then asserts `.topbar-user` text equals `"IM"`  → source: IMPL_PLAN "Modify test_topbar_shell.py" — route-interception approach
- [ ] `test_user_initials_circle` no longer asserts `user["text"] == "LM"` (old hardcoded value) and no longer touches `localStorage`  → source: IMPL_PLAN File 13 "Modify" — "The test currently asserts user['text'] == 'LM'. After wiring..."
- [ ] `test_user_initials_circle` **preserves** the original visual-style assertions (MN-E fix): `width == "30px"`, `height == "30px"`, `borderRadius == "50%"`, `background == "oklch(0.16 0.04 265)"`, `color == "oklch(0.97 0.01 260)"`, `"Instrument Serif" in fontFamily`, `fontStyle == "italic"` — the rewrite changes only the text expectation, not the visual contract  → source: PLAN_VERIFIED MN-E — "the rewritten `test_user_initials_circle` silently drops the rich visual-style assertions from the original"
- [ ] `tests/test_topbar_shell.py` defines (or imports from `conftest.py`) `create_users_mock(page, full_name)` helper duplicating the one in `test_profile_editor_restyle.py`  → source: IMPL_PLAN "Helper added" — "duplicate the 8-line helper into test_profile_editor_restyle.py and test_topbar_shell.py"
- [ ] `src/lib/profileStore.svelte.js` `readProfile()` contains NO `localStorage` read, NO `mycv:test_*` key check, NO test-mode short-circuit — only the two guards (`store.loaded`, `_pending`) and the `getUser()` IIFE  → source: PLAN_VERIFIED M5 — "localStorage test-hook in production code is borderline acceptable but unsanitized"; IMPL_PLAN Tests section — "no test-only short-circuit baked into the shipped bundle"

### New test file — `tests/test_profile_editor_restyle.py`

- [ ] File has two-line lean-code header: `# Lean Code — BSD 3-Clause License — Vivian Voss, 2026` + `# Scope: Editorial restyle smoke tests for the profile editor.`  → source: IMPL_PLAN "Add test_profile_editor_restyle.py" code block
- [ ] `public_url` fixture: skips if `public/build/bundle.css` missing; spins up `ThreadingHTTPServer`; tears down on yield exit  → source: IMPL_PLAN "Add" fixture code
- [ ] `open_editor()` helper: calls `create_users_mock(page, full_name)` to install the route, navigates, waits for `.editor-main`  → source: IMPL_PLAN `open_editor` helper code — route-interception approach
- [ ] `create_users_mock(page, full_name)` helper defined: installs `page.route("**/api/users", write_users_response)` where `write_users_response` fulfils `GET` with JSON `{full_name, email: "test@example.com"}` and continues other methods  → source: IMPL_PLAN "Helper added" code block
- [ ] `test_editorial_page_frame` covers Scenario 1: eyebrow text `Workspace · profile`, display heading `Your source of truth.`, seven `№ NN` section headers in DOM order  → source: FEATURE_SPEC Scenario 1; IMPL_PLAN "test_editorial_page_frame"
- [ ] `test_identity_grid_shape` covers Scenario 2b: avatar 96px circle present, identity-grid `1fr 1fr` computed, five `.form-row` cells in order, no `Headline` label  → source: FEATURE_SPEC Scenario 2b; IMPL_PLAN "test_identity_grid_shape"
- [ ] `test_skills_zero_state` covers Scenario 3b: one `.pill` in cluster, dashed border-style, no `.empty-state` text, clicking it focuses add-skill input  → source: FEATURE_SPEC Scenario 3b; IMPL_PLAN "test_skills_zero_state"
- [ ] `test_no_legacy_color_tokens_in_components` (non-Playwright): greps seven component files for `--color-border`, `--color-primary-rgb`, `--color-text-rgb`, `#e0e0e0`; asserts zero matches  → source: FEATURE_SPEC Scenario 8; IMPL_PLAN `test_no_legacy_color_tokens_in_components` code block
- [ ] `test_initials_helper_edge_cases` covers Scenario 7b: via DOM — calls `create_users_mock(page, full_name)` once per edge-case value (`""`, `"Ada"`, `"  Ada   Byron  Lovelace "`, `"   "`), navigates, asserts `.topbar-user` text matches the expected initials  → source: FEATURE_SPEC Scenario 7b; IMPL_PLAN "test_initials_helper_edge_cases — DOM-based"
- [ ] `test_readprofile_coalesces_one_request` guards the store double-load invariant: injects a `window.fetch` wrapper that counts GET `/api/users` calls, asserts the count is exactly 1 after both `Topbar` and `UserProfile` `$effect`s have mounted  → source: IMPL_PLAN `test_readprofile_coalesces_one_request` code block; PLAN_VERIFIED M4 — "store double-load race is plausible... plan has no test for it"
- [ ] `test_readprofile_coalesces_one_request` uses its own inline route handler that increments a `call_count["n"]` counter (NOT the shared `create_users_mock` helper, since the helper doesn't expose a counter); the counter is asserted to equal 1 after `wait_for_timeout(500)`  → source: IMPL_PLAN test note — "this test uses its own inline route handler... because it needs to count calls"
- [ ] Scenarios 4 (drag), 6 (initials after save), 10 (summary round-trip), 11 (education edit), 12 (project edit) are marked deferred to manual inspection in test file comments  → source: IMPL_PLAN "Scenarios deferred to manual inspection"
- [ ] `bun run build && pytest tests/` reports zero failures after all changes  → source: IMPL_PLAN Build & verify step 17; FEATURE_SPEC Scenario 9

---

## Section 5 — Accessibility

- [ ] Document outline is `<h1>` (page display title `Your source of truth.`) + seven `<h2>` elements (one per EditorialSection); no other `<h1>` or `<h2>` outside this structure  → source: UX_DESIGN A11y — "page heading is h1; each section title is h2 inside the EditorialSection primitive"; IMPL_PLAN File 2 notes
- [ ] `№ NN` eyebrow is a `<span>` sibling of `<h2>` (NOT a child), so screen readers read seven clean section names without `№` prefix noise  → source: UX_DESIGN A11y — "The eyebrow № NN is visually decorative and renders as a sibling span next to the h2"; FEATURE_SPEC Must-have 2; IMPL_PLAN File 2 markup
- [ ] Section count number is also a sibling `<span>` (not inside the `<h2>`)  → source: UX_DESIGN A11y — "The count number is also a sibling span, not part of the heading"
- [ ] Identity inputs have `aria-required="true"` on `Full name` and `Email` fields  → source: UX_DESIGN A11y — "aria-required='true' and the .required label decorator"; IMPL_PLAN File 4 change 3
- [ ] Error messages linked via `aria-describedby` to their input id  → source: UX_DESIGN A11y — "aria-describedby links input to error-message id, as today"
- [ ] `.topbar-user` circle has `aria-hidden="true"` (preserved from slice 2)  → source: UX_DESIGN A11y — "Decorative avatar: aria-hidden='true' on the .topbar-user circle (already set)"
- [ ] Identity avatar (`<div class="identity-avatar">`) has `aria-hidden="true"` (user name is rendered as labelled field beside it)  → source: UX_DESIGN A11y — "The Identity avatar is also aria-hidden='true' because the user's full name is rendered as a labelled field directly beside it"
- [ ] Keyboard navigation: `Import JSON` button is focus-reachable before Identity fields; tab order follows the sequence in UX_DESIGN Keyboard navigation map (items 5–23)  → source: UX_DESIGN "Keyboard navigation map"
- [ ] Skills `×` remove buttons have `aria-label="Remove {item.name}"`  → source: IMPL_PLAN File 9 change 3; UX_DESIGN Keyboard navigation map item 17
- [ ] Drag-to-reorder (Languages) acknowledged as NOT keyboard-accessible in this slice; no regression from current behaviour; note filed for future a11y slice  → source: UX_DESIGN A11y — "it is not keyboard-accessible today... this slice does NOT add keyboard reorder. A new note will be filed for a future a11y slice"
- [ ] Focus rings preserved on `.btn`, `.input`, `.edit-btn` via existing `:focus` outline rule (`--accent`)  → source: UX_DESIGN A11y — "existing :focus outline via --color-primary (→ --accent) is preserved"
- [ ] Color contrast spot-check: `var(--ink)` on `var(--paper)` ~17:1 AA, `var(--ink-3)` on `var(--paper)` ~5:1 AA, `var(--negative)` on `var(--paper)` ~5:1 AA  → source: UX_DESIGN A11y — "var(--ink) on var(--paper) is ~17:1, var(--ink-3) on var(--paper) is ~5:1, both AA-safe"

---

## Section 6 — Project-specific (Lean-code rules from CLAUDE.md)

n/a — no project-checks.md found at repo root.

The following cross-cutting checks are derived from `CLAUDE.md` (lean-code directive), which governs all code in this project. They apply to every file created or modified by this slice.

### File headers

- [ ] `src/lib/profileStore.svelte.js` opens with exactly two comment lines: `// Lean Code — BSD 3-Clause License — Vivian Voss, 2026` then `// Scope: Shared profile state — load, save, initials helper.`  → source: CLAUDE.md "Every file begins with exactly two comment lines"; IMPL_PLAN File 1 header
- [ ] `src/components/EditorialSection.svelte` opens with `<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->` then `<!-- Scope: Numbered editorial section header — eyebrow, display title, optional count. -->`  → source: CLAUDE.md "Adapt syntax: // for JS... <!-- --> for Svelte"; IMPL_PLAN File 2 header
- [ ] `src/components/UserProfile.svelte`, `ProfileEditor.svelte`, `WorkExperience.svelte`, `Education.svelte`, `Skills.svelte`, `Languages.svelte`, `Projects.svelte` each have a two-line lean-code header added (currently absent per IMPL_PLAN)  → source: CLAUDE.md; IMPL_PLAN Files 4, 6, 7, 8, 9, 10, 11 — "Add lean-code header (currently missing)"
- [ ] `tests/test_profile_editor_restyle.py` opens with `# Lean Code — BSD 3-Clause License — Vivian Voss, 2026` then `# Scope: Editorial restyle smoke tests for the profile editor.`  → source: CLAUDE.md; IMPL_PLAN test file code block
- [ ] ZERO inline comments or docstrings anywhere in new or modified code (beyond the two-line file header)  → source: CLAUDE.md — "After the header: ZERO comments. No inline comments. No docstrings."

### Function verb compliance (nine-verb table)

- [ ] `profileStore.svelte.js` new functions use only permitted verbs: `readProfile()`, `writeProfile()`, `parseInitials()`, `readInitials()` — confirmed against the nine-verb table (`read`, `write`, `parse`)  → source: CLAUDE.md verb table; IMPL_PLAN File 1 notes — "renaming to readProfile(); parseInitials(); writeProfile()"
- [ ] No function in new/modified code uses forbidden verbs: `fetch`, `get`, `load`, `save`, `set`, `handle`, `process`, `manage`, `do`  → source: CLAUDE.md — "NEVER use instead" column and "Forbidden patterns"
- [ ] `readCefrLabel(level)` in `Languages.svelte` uses `read` prefix correctly  → source: CLAUDE.md verb table — `read` = "Retrieve data"; IMPL_PLAN File 10 — "Use readCefrLabel(level)"
- [ ] `UserProfile.svelte`'s new function `checkAndWrite()` uses permitted verbs `check` + `write` in sequence  → source: CLAUDE.md verb table; IMPL_PLAN File 4 change 2 — "Renamed save() → checkAndWrite() to satisfy lean-code one-verb rule"
- [ ] Pre-existing functions in modified files (`save`, `add`, `edit`, `cancel`, `validate`, `formatDate`) are NOT renamed in this slice (out-of-scope, tracked as follow-up)  → source: IMPL_PLAN "Risks" item 4 — "Several existing functions violate lean-code rules. The slice does not rename them — they're pre-existing, out of scope."

### Naming — no abbreviations

- [ ] No abbreviated identifiers in new code: `cfg`, `ctx`, `req`, `res`, `opts`, `params` etc. absent from `profileStore.svelte.js` and `EditorialSection.svelte`  → source: CLAUDE.md — "No abbreviations anywhere in names"
- [ ] `_pending` and `_savedTimeout` are module-private (underscore-prefixed convention for private vars, not abbreviations of a semantic name) — acceptable  → source: IMPL_PLAN File 1 — "_pending is a plain module-private let"

### Naming — no framework suffixes

- [ ] No data structure names ending in `DTO`, `Entity`, `Model`, `VO`, `Interface`, `Service`, `Manager`, `Helper`, `Utils`, `Factory`, `Builder`, `Provider`, `Adapter`  → source: CLAUDE.md "Data structures" and "Forbidden patterns"

### One function, one job

- [ ] `readProfile()` only reads (loads from API and populates store) — no validation, no UI side-effects  → source: CLAUDE.md — "One function, one job. If a function reads AND checks AND writes, split into three"; IMPL_PLAN File 1
- [ ] `writeProfile()` only writes (calls `updateUser`, sets saving/saved/error) — no field validation  → source: CLAUDE.md; IMPL_PLAN File 1 `writeProfile()`
- [ ] `checkAndWrite()` in `UserProfile.svelte` performs check then triggers write — two permitted operations chained by design (check validates, write saves); confirm each step is still single-purpose  → source: IMPL_PLAN File 4 change 2
- [ ] `parseInitials(fullName)` only transforms a string format — no DOM access, no store access  → source: CLAUDE.md — "parse: Transform a format"; IMPL_PLAN File 1 — `parseInitials` is pure

### Function name length

- [ ] No function name exceeds verb + three words: `readProfile`, `writeProfile`, `parseInitials`, `readInitials`, `checkAndWrite`, `readCefrLabel`, `focusInput`, `handleSummaryBlur` — all within limit  → source: CLAUDE.md — "Maximum three words after the verb. More → split the job."

### Legacy color token sweep

- [ ] `grep -nE '(--color-border|--color-primary-rgb|--color-text-rgb|#e0e0e0)'` across all seven modified component files returns zero matches after edits  → source: FEATURE_SPEC Must-have 11; Scenario 8; IMPL_PLAN `test_no_legacy_color_tokens_in_components`

### Designer sign-off flag

- [ ] Skills pill typography override (sentence-case 12px Inter vs. global `.pill` mono uppercase) has been shown to designer / stakeholder and accepted  → source: IMPL_PLAN File 9 note — "NOTE: this overrides the editorial .pill primitive's typographic register. Document in the inspector checklist for designer sign-off."

### Section.svelte deletion gate

- [ ] Before deleting `src/components/Section.svelte`: run `grep -rn "from.*Section\.svelte\|import Section" src/ tests/` and confirm zero matches  → source: IMPL_PLAN "Files to DELETE" — "Sanity check before deletion"

### App.svelte container guard

- [ ] `App.svelte` uses `class:container-wide={activeTab === 'profile'}` so `.container` element still exists for legacy Playwright test (`test_topbar_renders_at_top`)  → source: IMPL_PLAN File 12 — "keep .container element still exists (legacy tests pass)"
- [ ] `global.css` gains `.container-wide { max-width: none; padding: 0; }` rule  → source: IMPL_PLAN File 13; File 12 "Adopted plan"
- [ ] `pytest tests/test_design_tokens.py` still passes after `.container-wide` is added (plan-phase inspection confirmed it asserts only on `body` computed styles — `backgroundColor`, `color`, `fontFamily`, `fontSize`, `lineHeight`, `fontFeatureSettings`, `-webkit-font-smoothing` — and is insensitive to additive rule changes in `global.css`)  → source: IMPL_PLAN Risks 2b; PLAN_VERIFIED M6
- [ ] `pytest tests/test_topbar_shell.py::test_topbar_renders_at_top` still passes after File 12's `class:container-wide` is added — the legacy test depends on `.container` resolving at the page root; the conditional class adds `container-wide` alongside `container` rather than replacing it  → source: IMPL_PLAN File 12 "keep .container element still exists"; PLAN_VERIFIED MN6

### Toast placement

- [ ] `<Toast>` is a direct child of `ProfileEditor`'s root template (NOT inside `.editor-column` or `.editor-main`), so its stacking context is not constrained by the centred column  → source: FEATURE_SPEC Must-have 1 — "Toast element remains a direct child of ProfileEditor's root template... NOT moved inside the new editorial-column wrapper"
