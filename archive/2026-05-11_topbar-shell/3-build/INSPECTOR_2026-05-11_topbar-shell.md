# INSPECTOR — topbar-shell

feature: topbar-shell
date: 2026-05-11
status: READY
playwright: skipped (no playwright.config.* found at project root)

---

## Playwright

Skipped. `ls playwright.config.*` returned no matches in the project root or `public/`.
The 251/251 automated test results are recorded in `workbench/3-build/TEST_RESULTS_2026-05-11_topbar-shell.md`.

---

## Manual checklist

Eyeball pass against `http://127.0.0.1:8765/`. Each item is a single look or one keyboard action.

### A — Topbar geometry and layout

- Open `http://127.0.0.1:8765/`. Using DevTools (Elements → Computed), confirm the `<header class="topbar">` computed height is exactly **64px**.
- With DevTools open, confirm the topbar stretches the full viewport width (no left/right margin, no max-width cap on the header itself).
- Confirm the page body content below the topbar is centered with horizontal padding — not flush to the viewport edges.
- Confirm there is a **1px horizontal rule** at the very bottom of the topbar, visually separating it from the page body below.

### B — MyCVLogo wordmark

- Look at the brand area on the left. Confirm "**my**" is in italic Instrument Serif and "**CV**" is in roman (upright) Instrument Serif — both in the same baseline group with no gap between them.
- Confirm there is a small **cobalt/blue dot** immediately to the right of "CV", visually raised above the baseline (not sitting on the text line).
- Confirm there is no separate sigil icon to the left of the wordmark — the wordmark "myCV" + dot is the only brand element.

### C — Nav slot labels and order

- Confirm exactly **6 slot labels** appear in the nav, left to right in this order: Dashboard · Pipeline · Saved jobs · Profile · Tailor CV · Interview prep.

### D — Active slot treatment (Profile on load)

- On load the **Profile** slot should be active. Confirm its label is in ink color (dark, not muted grey) and weight visibly heavier (500 vs 400).
- Confirm Profile has a **1px ink-colored underline** that appears to butt up against the topbar's bottom rule (the underline and the bottom rule overlap — there is no gap between them).
- Confirm none of the other five slots show an underline.

### E — Disabled slots

- Confirm **Dashboard, Pipeline, Saved jobs, and Interview prep** labels are visibly muted — noticeably lighter/greyer than the Profile label.
- Hover over the Dashboard label. Confirm the cursor is **not-allowed** (circle-slash), not a pointer.
- Click Dashboard. Confirm **nothing happens** — the page body does not change, Profile remains active.

### F — Enabled slot click (Tailor CV)

- Click **Tailor CV**. Confirm the page body switches to the Resume Generator view.
- Confirm **Tailor CV** now shows the active treatment (ink color, bold, 1px underline) and Profile loses it.
- Confirm the topbar itself does not re-render or flicker during the transition.

### G — Search pill

- Confirm the search pill is visible to the right of the nav, with placeholder text "Find a job, resume…" and a **⌘K** badge on the right end of the pill.
- Confirm the pill has a visible border/outline and a light background that differs from the topbar background.
- Click the pill. Confirm **nothing happens** (decorative this slice — no palette opens).

### H — User-initials circle

- Confirm a **30×30 filled circle** appears to the right of the search pill, with the letters **LM** centered inside it.
- Confirm the circle background is the ink color (dark) and the letters are in light/paper color, in italic Instrument Serif.

### I — Keyboard navigation

- Click anywhere outside the topbar to clear focus, then press **Tab** repeatedly. Confirm focus lands on **Profile** first, then **Tailor CV** — skipping all four disabled slots.
- With focus on **Profile**, press **Enter**. Confirm the Profile view is active (or stays active if already active).
- With focus on **Tailor CV**, press **Enter**. Confirm the view switches to the Resume Generator.
- Press **Space** on a focused enabled slot. Confirm it also activates the slot (same as Enter).

### J — No legacy nav

- Confirm there is **no second nav surface** on the page — no `TabNav` bar, no `h1>MyCV` heading, no duplicate "Profile / Resume Generator" button row below the topbar.

---

## Decisions

none — parent collects user verdict
