# Diagnosed Bugs

Tracked bugs surfaced by codebase audit. Status as of 2026-04-19 — all 4 bugs fixed as of 2026-04-20.
A second batch (#5–#12) was surfaced by the 2026-06-10 design-migration
consolidation audit (slices 1–4 review; see `design-bundle/SLICE_INDEX.md`,
"Consolidation pass — 2026-06-10") and fixed the same day.

---

## Fixed

### #1 — Job linking silently drops on resume generation

**Commit:** `46d8ed6`
**File:** [src/lib/api.js:169](src/lib/api.js:169)

Frontend sent `job_description_id` in the `POST /api/resumes/generate` body;
backend schema expects `job_id`. Pydantic v2's default `extra='ignore'` silently
dropped the unknown field, so every resume generated from a saved job was
created with `job_id = NULL` and showed up as an orphan in the Saved Jobs list.

**Fix:** Renamed the `generateResume` parameter and body key to `job_id`.

---

### #2 — `setup.sh` fallback wrote a non-existent env var

**Commit:** `46d8ed6`
**File:** [setup.sh:94](setup.sh:94)

When `.env.example` was missing, the script's `else` branch wrote a heredoc
with `GOOGLE_API_KEY=`, but the Gemini provider reads `GEMINI_API_KEY`. The
branch was effectively unreachable in the supported `git clone` workflow,
which is why it persisted. It also drifted from `.env.example` (missing
`LLM_PROVIDER`, `CLAUDE_MODEL`, `GEMINI_MODEL`).

**Fix:** Deleted the fallback heredoc and made the script fail fast with
`".env.example is missing — run setup.sh from a full git clone of the repo."`

---

### #3 — PDF preview hardcoded English `at` / `in`

**Commit:** `46d8ed6`
**File:** [src/components/PdfPreview.svelte](src/components/PdfPreview.svelte)

The Svelte preview rendered `"<title> at <company>"` and
`"<degree> in <field>"` as literal English across all languages, while the
server-side Jinja templates read translated connectors from
[translations/fr.json](translations/fr.json) and
[translations/nl.json](translations/nl.json) via `{{ labels.at }}` /
`{{ labels.in }}`. French and Dutch users saw `at` / `in` in the preview but
`chez` / `en` (or `bij`) in the exported PDF.

**Fix:** Added `at` and `in` entries to the inline `translations` object for
all three languages (en/fr/nl) and replaced the hardcoded strings with
`{t.at}` / `{t.in}` in the Brussels, classic, modern, and EU-classic
branches.

**Verified:** Browser-automation check of the live preview confirmed
`chez Acme Corp` + `BS en Computer Science` (FR) and `bij Acme Corp` (NL)
across Modern and Brussels templates.

### #4 — `ResumeView.svelte` edit pane hardcodes English `in`

**Commit:** `26c9670`
**File:** [src/components/ResumeView.svelte:326](src/components/ResumeView.svelte:326)

Same class of bug as #3 but in a different component — the edit/view pane
used when reviewing a generated resume before exporting.

**Fix:** Added `in` to `sectionTranslations` for all three languages
(en: `"in"`, fr: `"en"`, nl: `"in"`) and replaced the hardcoded string on
line 326 with `${labels.in}`. No `at` fix needed — work experience uses ` · `
as a separator, not a connector word.

---

### #5 — Resume section toggles never persisted; preview lied about the PDF

**Commit:** `6dd8aa3`
**File:** [src/components/ResumeView.svelte:310](src/components/ResumeView.svelte:310)

Only the `skills` branch of `toggleSection` called `updateResume`;
work/education/projects/languages mutated local state only. The A4 preview
updated while Download PDF re-rendered the stored resume server-side, so an
unchecked section still appeared in the downloaded file. First click was
also a no-op when `included` was `undefined` (`!undefined === true`).

**Fix:** Replaced with `updateSectionInclusion(section, included)` driven
by the rail row's current state — every section persists, with a scoped
rollback and error toast on failure.

**Verified:** Full pytest suite green; live smoke against the running app.

---

### #6 — Edit/Preview tabs unreachable by keyboard

**Commit:** `6dd8aa3`
**File:** [src/components/ResumeView.svelte:476](src/components/ResumeView.svelte:476)

The ARIA tablist used roving `tabindex` (inactive tab at `-1`) with no
arrow-key handler anywhere, so keyboard users could never switch modes —
despite the slice-4 retrospective claiming "strict ARIA APG semantics".

**Fix:** APG keyboard support on the tabs — ArrowLeft/ArrowRight/Home/End
switch `editMode` and focus the now-active tab.

---

### #7 — Error reverts wiped prior saves

**Commit:** `6dd8aa3`
**File:** [src/components/ResumeView.svelte](src/components/ResumeView.svelte)

Failure paths in skill rename, skill inclusion, and drag reorder reset
`resumeData` to the original generation snapshot (`resume.resume`),
discarding every previously persisted edit from the UI.

**Fix:** Scoped reverts — only the failed field or order is restored. Drag
state is captured and cleared synchronously so `dragend` cannot race the
async drop save.

---

### #8 — Required-field validation unreachable; a failed save replaced the form

**Commit:** `ca9df79`
**Files:** [src/components/UserProfile.svelte:16](src/components/UserProfile.svelte:16),
[src/lib/profileStore.svelte.js:56](src/lib/profileStore.svelte.js:56)

`handleBlur` early-returned when `full_name`/`email` was empty, so
`checkAndWrite`'s `'Required'` errors could only fire for whitespace-only
input. Separately, a failed `writeProfile` set `store.error`, which the
template treats as a load failure — the entire identity card was swapped
for an error box, losing the user's editing context.

**Fix:** Blur always debounces into `checkAndWrite` (which already refuses
to write while errors exist); save failures set a new `store.saveError`,
rendered inline beside the saved indicator.

---

### #9 — ConfirmDialog silently dropped the `title` prop

**Commit:** `ca9df79`
**File:** [src/components/ConfirmDialog.svelte:2](src/components/ConfirmDialog.svelte:2)

`SavedJobsList` and `SavedJobItem` passed `title="Delete Job?"` /
`"Delete Resume?"`, but the component only destructured
`message/onConfirm/onCancel` — the heading never rendered.

**Fix:** `title` renders as the dialog heading, `message` as the body
line; the six short-question callers migrated from `message` to `title`.

---

### #10 — Duplicate DOM ids across simultaneously-mounted forms

**Commit:** `ca9df79`
**Files:** [src/components/Languages.svelte](src/components/Languages.svelte),
[src/components/Projects.svelte](src/components/Projects.svelte)

Both components rendered `id="name"` and `id="new_name"` on the same
profile page — invalid HTML with broken label and `aria-describedby`
association.

**Fix:** Domain-prefixed ids (`lang_name` / `new_lang_name` /
`lang-name-error`, `proj_name` / `new_proj_name`), matching Projects' own
`proj_url` convention.

---

### #11 — Cancelled drag desynced the UI order from the server

**Commits:** `ca9df79` (Languages), `6dd8aa3` (ResumeView work list)
**File:** [src/components/Languages.svelte:141](src/components/Languages.svelte:141)

Drag-over reordered the list optimistically; a cancelled drag (Escape or
drop outside) hit only `dragend`, which neither persisted nor reverted —
the UI order diverged from the server until reload. Languages' failed
reorder also left a sticky `error` that permanently replaced the grid.

**Fix:** Order snapshot at dragstart, restored on cancelled dragend (drop
clears the drag state synchronously first); `loadData` clears `error` on
success.

---

### #12 — "Saved" indicator faded out the instant it appeared

**Commit:** `91440cb`
**File:** [src/styles/global.css](src/styles/global.css)

`class:fading={!saving}` is true the moment `saved` flips on (saving has
already returned to false), so the 0.5 s `fadeOut` ran immediately and the
indicator was invisible for 1.5 s of its 2 s lifetime — across all six
components using the pattern.

**Fix:** `animation: fadeOut 0.5s ease-out 1.5s forwards` — visible
~1.5 s, fades 0.5 s, unmounts at 2 s. CSS-only; no component changes.

---

### #13 — Escape never closed the ConfirmDialog

**Commit:** `069d857`
**File:** [src/components/ConfirmDialog.svelte](src/components/ConfirmDialog.svelte)

The mount effect focuses the dialog card, and the card's
`onkeydown={(e) => e.stopPropagation()}` swallowed every keystroke before
it could bubble to the backdrop — the only place the Escape handler
lived. Since focus always started inside the card, Escape was dead in
every delete flow app-wide (Education, Languages, Projects, Skills,
PhotoUpload, WorkExperience, SavedJobsList, SavedJobItem). Cancel button
and backdrop click were unaffected. ImportModal never had the bug — its
card has no keydown stopper, so Escape bubbles to the backdrop handler.

**Fix:** Escape is handled by a `svelte:window` listener while the dialog
is mounted, so it also works after tabbing focus out of the dialog (no
focus trap exists — a known, separate APG gap shared with ImportModal).
The card's keydown stopper is gone; click behavior is unchanged.
Regression tests: `tests/test_confirm_dialog.py` (Escape focused,
Escape after tab-out, backdrop click cancels, in-card click doesn't).

---

## Outstanding

None. Batch 1 (#1–#4) fixed as of commit `26c9670`; batch 2 (#5–#12) fixed
as of commits `6dd8aa3`–`91440cb` (2026-06-10); #13 fixed as of commit
`069d857` (2026-07-06).

---

## Notes

- This document lists bugs surfaced by a targeted audit of the three
  highest-impact user-visible issues. Other lower-priority findings from
  the broader audit are not included here; re-run the audit if you want
  that list re-surfaced.
- `database.py` references to `job_description_id` are intentional
  (migration code describing the historical rename) and not bugs.
- `CHANGELOG.md` mentions of the old name are historical and not bugs.
