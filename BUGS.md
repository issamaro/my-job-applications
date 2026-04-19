# Diagnosed Bugs

Tracked bugs surfaced by codebase audit. Status as of 2026-04-19.

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

---

## Outstanding

### #4 — `ResumeView.svelte` edit pane hardcodes English `in`

**File:** [src/components/ResumeView.svelte:326](src/components/ResumeView.svelte:326)

Same class of bug as #3 but in a different component — the edit/view pane
used when reviewing a generated resume before exporting.

```svelte
<p>{edu.degree} {edu.field_of_study ? `in ${edu.field_of_study}` : ''} · ...
```

`ResumeView.svelte` carries its own `sectionTranslations` table
([src/components/ResumeView.svelte:18-46](src/components/ResumeView.svelte:18))
with section headers only — no `in` key. A FR/NL user editing a resume sees
`BS in Computer Science` in the editor but `BS en Computer Science` in the
preview and PDF.

**Suggested fix:** Add `in` to `sectionTranslations` for all three languages
(en: `"in"`, fr: `"en"`, nl: `"in"`) and replace the hardcoded string on
line 326. No `at` fix is needed here — work experience uses ` · ` as a
separator, not a connector word.

**Related cleanup to consider at the same time:** the inline translation
tables in `PdfPreview.svelte` and `ResumeView.svelte` duplicate the same
strings that live in `translations/*.json`. A single source of truth
(build-time JSON import or a shared JS module) would prevent future
drift. Out of scope for the straight bug fix.

---

## Notes

- This document lists bugs surfaced by a targeted audit of the three
  highest-impact user-visible issues. Other lower-priority findings from
  the broader audit are not included here; re-run the audit if you want
  that list re-surfaced.
- `database.py` references to `job_description_id` are intentional
  (migration code describing the historical rename) and not bugs.
- `CHANGELOG.md` mentions of the old name are historical and not bugs.
