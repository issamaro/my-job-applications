feature: restyle-profile-editor
date: 2026-05-13
status: READY
playwright: skipped (dev server not running; build bundle present; 263/263 tests passing per caller)

---

## Manual checklist

Items requiring behavioral judgment or a live backend — all computed-style
and DOM-shape checks are covered by the Playwright test suite.

### MI-4 — Languages drag preserved

- Scroll to the Languages section. Drag the second language card to the
  first slot and drop it. Expected: cards swap visually and the new order
  persists after a hard reload (Ctrl+Shift+R / Cmd+Shift+R). Fail if cards
  don't swap, swap reverts on hover-out, or reload restores the original order.

### MI-5 — Experience timeline visual order

- Open the Profile editor with at least one Experience entry. Expected: the
  most-recent entry appears at the top of the list; dates render in the left
  rail, title/company/description in the right block, with no visual overlap.
  Fail if entries are in chronological (oldest-first) order, or if the date
  and content columns visually bleed into each other.

### MI-6 — Topbar initials live-update on name save (Skip — backend not running)

- skip_reason: backend not running
- In the Identity card, change Full name to a different two-word name (e.g.
  "Ada Lovelace") and click away. Expected: the Topbar user circle updates to
  the new initials ("AL") within ~1 s without a page reload. Fail if the
  circle stays on the old initials until reload.

### MI-10 — Summary round-trip (Skip — backend not running)

- skip_reason: backend not running
- Type a non-empty summary, blur the textarea, then hard-reload. Expected:
  the typed text reappears verbatim. Fail if the textarea is empty, truncated,
  or shows a previous value.

### MI-11 — Education edit round-trip (Skip — backend not running)

- skip_reason: backend not running
- Open an existing Education entry, change the institution name, save, then
  hard-reload. Expected: the new institution name renders in the list. Fail if
  the old value persists.

### MI-12 — Project edit round-trip (Skip — backend not running)

- skip_reason: backend not running
- Open an existing Project entry, change the project name, save, then
  hard-reload. Expected: the new name renders in the list. Fail if the old
  value persists.

### Designer sign-off — Skills pill typography

- In the Skills section, confirm that skill chips render in sentence-case
  Inter (e.g. "Python", not "PYTHON"), at roughly 12 px, and without the
  mono uppercase tracking that other `.pill` elements use. Confirm this
  override is acceptable to the designer/stakeholder. Fail if chips still
  render in mono uppercase, or if the override has not been signed off.

---

## Decisions

none — parent collects user verdict
