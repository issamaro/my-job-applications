# IMPL_PLAN — screen-frame-ownership — 2026-07-06

Ceremony: S (light plan — no UX doc, no library research; every change clones an
in-repo pattern). Spec source: `backlog/refined/screen-frame-ownership.md`
(analyze skipped at S; the refined item carries success criteria + BDD sketch).

## Verified ground truth (audited this run)

- `.container` consumers are exactly three: `src/App.svelte:26` (wrapper div with
  `class:container-wide`), `src/styles/global.css:175-184` (both rules),
  `tests/test_topbar_shell.py:105-122` (`topbar_precedes_container`).
- Substring cousins that the static guard must NOT flag:
  `photo-upload-container` (PhotoUpload.svelte), `progress-container`
  (ProgressBar.svelte).
- `.container` rule body is `max-width: 800px; margin: 0 auto;
  padding: var(--spacing-section)` — this IS the pre-slice-4 geometry the
  temporary generator frame must reproduce.
- `main.js` mounts App into `document.body`; Topbar and the screen are siblings
  under body.
- `ProfileEditor.svelte:53` renders `<main class="editor-main">` unconditionally
  (outside any `{#if}`), with no API mock required — proven by
  `test_disabled_slots_inert`, which sees `.profile-header` (inside it) with no
  routes mocked.
- `--spacing-section: 24px` at `global.css:63`; stays until after slice 9
  (two-scales ledger entry) — safe for the temporary frame to consume.
- `ResumeView` self-frames (`.resume-preview` pads with `--d-pad`);
  `.editor-column` caps at 940px (asserted by `test_editorial_page_frame`).
- No other test and no sibling refined item references the container or
  `App.svelte`.
- Playwright harness pattern to clone: fixture trio `find_free_port` /
  `create_public_server` / `public_url` as in `tests/test_design_tokens.py:17-42`;
  static-guard pattern to clone: `test_no_legacy_color_tokens_in_components`
  (`tests/test_profile_editor_restyle.py:282`).

## File-by-file

### 1. `src/App.svelte` — modify

Delete the wrapper div (line 26) and its closing tag; keep the `{#if}` chain,
outdented, as direct children after `<Topbar/>`. No other change. The two-line
scope header already reads "mounts editorial Topbar and renders the active
screen" — stays accurate.

### 2. `src/styles/global.css` — modify

Delete the `.container` rule (lines 175-179) and `.container-wide` rule
(181-184). The `/* Layout */` banner stays (still owns `.header`, `.status`).

### 3. `src/components/ResumeGenerator.svelte` — modify

Restructure the branch chain so preview is the first branch and everything else
sits inside a temporary frame div (`view === 'input'` incl. its
profile-incomplete state, and `view === 'loading'`):

```svelte
<div class="resume-generator">
  {#if view === 'preview' && currentResume}
    <ResumeView ... />
  {:else if view === 'input' || view === 'loading'}
    <div class="generator-frame">
      {#if profileIncomplete && view === 'input'}
        ...unchanged profile-incomplete block...
      {:else if view === 'input'}
        ...unchanged input block (JobInput + generator-actions + SavedJobsList)...
      {:else}
        ...unchanged loading block (JobInput disabled + ProgressBar + loading-actions)...
      {/if}
    </div>
  {/if}
</div>
```

Branch-equivalence check: old chain rendered nothing for
`view === 'preview' && !currentResume`; new chain also renders nothing (falls to
the else-if, false). All four visible states map 1:1.

Style block gains:

```css
.generator-frame {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-section);
}
```

Deletion mark for slice 6 lives in the SLICE_INDEX line (item 7) and the new
test file's scope header — not in a code comment (lean-code: none allowed).

### 4. `tests/test_topbar_shell.py` — modify

In `test_topbar_renders_at_top`: add `page.wait_for_selector(".editor-main")`
after `create_loaded_page` (belt-and-braces; the root is unconditional), rename
`topbar_precedes_container` → `topbar_precedes_screen` at BOTH sites (the
assignment at line 105 and the assert at line 122), retarget the
`querySelector('.container')` to `.editor-main`, keep the
DOCUMENT_POSITION_FOLLOWING logic.

### 5. `tests/test_design_tokens.py` — modify (static guard home)

Append:

```python
SHELL_CONTAINER_CLASS = re.compile(r"(?<![\w-])container(?:-wide)?(?![\w-])")


def test_no_shell_container_classes_in_src():
    repo_root = Path(__file__).parent.parent
    sources = sorted(
        p for p in (repo_root / "src").rglob("*")
        if p.suffix in {".svelte", ".js", ".css"}
    )
    offenders = {}
    for source in sources:
        for number, line in enumerate(source.read_text().splitlines(), 1):
            if SHELL_CONTAINER_CLASS.search(line):
                offenders.setdefault(str(source.relative_to(repo_root)), []).append(number)
    assert offenders == {}, f"shell container class reintroduced: {offenders}"
```

The custom boundary `(?<![\w-])…(?![\w-])` treats `-` as a word char, so
`photo-upload-container` / `progress-container` pass while `class="container"`,
`class:container-wide`, `.container {`, and `querySelector('.container')` are
all caught. No browser, no fixture — pure file grep, per the
`test_no_legacy_color_tokens_in_components` pattern. `re` and `Path` are already
imported in this file.

Also append one bundle-text assertion to `test_bundle_carries_consolidation_rules`
(same file, same mechanism — the built stylesheet is the artifact the criterion
names):

```python
    assert re.search(r"\.resume-preview[^{]*\{[^}]*padding:\s*var\(--d-pad\)", css)
```

(Verified against the current bundle: Svelte scopes the selector as
`.resume-preview.svelte-kyrtaa { padding: var(--d-pad); … }` — the hash sits
between the class and the brace and changes on rebuild, so the pattern must be
`[^{]*`, not `\s*`. `[^{]*`/`[^}]*` cannot cross braces, so the match stays
inside one rule; the only other `.resume-preview` rule is the focus-visible
group, whose body carries no `padding:`.)

This is the honest, cheap half of success criterion C3 for `.resume-preview`:
the rule that produces its `--d-pad` padding still ships in `bundle.css` after
the container deletion. The *rendered* "unchanged geometry" judgment for the
preview screen routes to an inspector visual bullet (Phase 3 step 5), because a
computed-style probe would need a populated `currentResume` (generate/load
round-trip + API mock surface) for a screen this change never touches — not
worth building for a claim the stylesheet + eyeball check already covers.

### 6. `tests/test_generator_frame.py` — create

Two-line header scope: "Smoke-test the temporary generator input frame —
deleted with slice 6 (tailor-cv-screen)." Clone the fixture trio from
`test_design_tokens.py`. One test, `test_generator_input_frame_geometry`:

- context with `viewport={"width": 1512, "height": 860}` (success criterion
  pins 1512×860)
- goto, wait `.topbar`, click `[data-slot-id="tailor"]`, wait `.generator-frame`
- computed `maxWidth` of `.generator-frame` == `"800px"` (the
  `test_editorial_page_frame` 940px check, retargeted)
- `getBoundingClientRect`: `left > 0`, `right < innerWidth`, and
  `|left - (innerWidth - right)| <= 1` — centered with visible margins both
  sides (rect-based because Chromium's computed value for `margin: auto` is
  used-value-dependent; the rect is the honest geometry probe)

No API mocks: `checkProfile()` failing against the static server leaves
`profileIncomplete = false`, so the input branch renders (same no-mock stance as
`test_click_tailor_routes`).

### 7. `design-bundle/SLICE_INDEX.md` — modify

Add one bullet to "Shared decisions (fixed across all slices)":

> - **Screens self-frame (2026-07-06, screen-frame-ownership):** the app shell
>   mounts Topbar and the bare active screen; every screen declares its own
>   page frame. Slices 5–9 must not extend or reintroduce a shell container —
>   a static guard in `tests/test_design_tokens.py` fails on any
>   `container`/`container-wide` class usage in `src/`. The generator's
>   temporary 800px input frame (`.generator-frame`,
>   `tests/test_generator_frame.py`) is pre-slice-4 geometry restored; slice 6
>   deletes both with its restyle.

(`design-bundle/` is gitignored — the edit ships with this item the same way
the 2026-06-10 consolidation amendments did: applied now, not committed.)

## Build order

1 → 2 → 3 (source), rebuild bundle (`bun run build`), then 4 → 5 → 6 (tests),
then 7 (ledger). Rebuild before test-runner or every Playwright test goes stale
against the old bundle.

## Risks

- **Auto-margin computed values**: mitigated — centering asserted via
  bounding rect, only `max-width` via computed style (proven mechanism at
  940px).
- **Generator screen loses edge-flush width on input view**: intended — that IS
  the feature (pre-slice-4 geometry restored); preview branch stays bare and
  full-bleed.
- **Static guard false positives**: checked — the only `container` tokens in
  `src/` after this change are the two hyphenated cousins, which the boundary
  regex skips. Guard scans `src/` only, so tests/docs may say "container"
  freely.
- **Stale bundle**: build step is explicit in the order above; every Playwright
  fixture already skips (loudly) when `bundle.css` is missing.

## Test plan

- New: `test_generator_input_frame_geometry`, `test_no_shell_container_classes_in_src`,
  plus one `.resume-preview`/`--d-pad` bundle-text assertion appended to
  `test_bundle_carries_consolidation_rules`.
- Retargeted: `test_topbar_renders_at_top`.
- Regression: full pytest suite — `.editor-column` (940px) is asserted by
  `test_editorial_page_frame`; `.resume-preview` has no computed-style test
  anywhere (nothing to regress in-suite) — its coverage is the bundle-text
  assertion above plus an inspector visual bullet.

## Success criteria traceability (refined item → verification)

| Criterion | Verified by |
|---|---|
| zero `container-wide` in `src/`, zero `.container` in global.css | static guard + `grep` spot-check at ship |
| Tailor CV form centered ≤ 800px at 1512×860 | `test_generator_input_frame_geometry` |
| `.editor-column` 940px unchanged | existing `test_editorial_page_frame` (regression) |
| `.resume-preview` `--d-pad` unchanged | bundle-text assertion in `test_bundle_carries_consolidation_rules` + inspector visual bullet (no computed-style test exists or is added — a probe would need a full generate round-trip for a screen this change never touches) |
| static guard passes | `test_no_shell_container_classes_in_src` |
| generator frame test passes | same file |
| full suite green incl. retargeted topbar test | test-runner |
| SLICE_INDEX carries the contract line | ship-phase ledger sweep |
