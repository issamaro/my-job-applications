# FEATURE_SPEC — flexible-resume-overview

date: 2026-05-05
ceremony: M
slug: flexible-resume-overview

## Persona

Solo user drafting tailored resumes for specific job applications. They generate a resume via LLM, then want to refine the result in place: tweak the summary, drop a generic skill the LLM kept, fix a typo, swap a skill name. They expect the PDF preview to reflect their edits without re-calling the LLM.

## Pain point

Today, only `work_experiences[*].description` is inline-editable on the Resume overview. The LLM-generated **summary** (`resumeData.summary`) and **skills list** (`resumeData.skills`) are rendered read-only. When the LLM produces a generic summary or picks an irrelevant skill, the user has no way to fix it short of regenerating — which spends another LLM call and may surface a different equally-imperfect output.

## Audit — what the LLM actually produces on the overview

(From `/services/llm/base.py:75-129` and `/services/resume_generator.py:69-105`.)

| Section | Source | Currently editable? | In scope this feature? |
|---|---|---|---|
| `personal_info` | User profile (passthrough) | No | **Out** — not LLM-generated |
| `summary` | LLM-generated text | **No** (read-only `<p>`) | **In** — make inline-editable |
| `work_experiences[*].description` | LLM-tailored from profile | Yes (textarea inline) | Out — already editable |
| `work_experiences[*].included` | LLM returns `true` for all | Yes (per-section toggle) | Out — recently shipped |
| `work_experiences[*].match_reasons` | LLM-generated (small label) | No | **Out** — display-only label, not user-curated |
| `skills[*].name` | LLM-picked from profile | No | **In** — make per-item editable (rename) |
| `skills[*].included` | LLM defaults to true | Section-wide toggle only | **In** — make per-item include/exclude |
| `skills[*].matched` | LLM derives from job analysis | No | Out — derived, not user-curated |
| `education[*]`, `languages[*]`, `projects[*]` | User profile (passthrough) | Section-wide toggle | Out — not LLM-generated content |
| `job_analysis` | LLM-generated | No (read-only) | Out — analytical view, not part of resume |

Net: **two and only two** new editing affordances are needed — inline-edit `summary`, and per-item curation (exclude / include / rename) on `skills`.

## Must-have

### MH-1 — Summary inline-edit
- The user can click the summary text on the overview's Edit tab and replace it with a textarea.
- Save persists `resumeData.summary` to the saved resume row via existing `updateResume()` API.
- Cancel discards the edit and restores the prior text.
- The PDF preview re-renders with the new summary as soon as the save succeeds (reactive on `resumeData`).

### MH-2 — Skills per-item exclude / include
- Each skill chip has an exclude affordance (e.g., a small `×` button).
- Excluded skills move into a visually distinct "available" group below the active list, where each has a re-include affordance (e.g., a small `+` button).
- The original LLM-picked list is preserved on the saved resume — exclusion is a flag (`skills[*].included`), not a deletion.
- Re-including a skill restores it to its **original position** in the active list (sort by stable original index, not append).

### MH-3 — Skills per-item rename (replace)
- Each active skill chip has an edit affordance.
- Editing a skill swaps the chip for a small inline input bound to `skills[*].name`.
- Save persists; cancel restores. `matched` and `included` remain unchanged.

### MH-4 — Persistence + PDF preview parity
- All three edit operations write the full `resume_content` JSON via the existing `PUT /api/resumes/{id}` endpoint.
- All edits survive a page reload (DB-backed).
- The PDF preview tab and the downloaded PDF reflect: edited summary, excluded skills omitted, renamed skills shown by new name.

### MH-5 — Regeneration is non-destructive
- "Regenerate" already creates a **new** `generated_resumes` row (one resume per generation, multiple per job; confirmed in `/services/resume_generator.py:84-102`).
- The user's edits live on the resume row they were made on. A fresh generation starts a new row with fresh LLM output — old edits are not silently lost.
- **Decision:** no extra warning UI is required because no destructive overwrite happens. The existing "Regenerate" button keeps its current behavior. (This resolves the open question in the refined item.)

### MH-6 — Section-wide skills toggle stays deterministic, doesn't clobber selectively
- The existing per-section toggle at `ResumeView.svelte:129-133` flips all skills based on `skills[0]?.included`. With per-item exclusions in play, this is ambiguous.
- **Decision:** rewrite the skills-section toggle to a deterministic two-state rule: if **any** skill is currently `included === false`, clicking the toggle sets all to `included = true` ("re-include all"); otherwise it sets all to `false` ("exclude all"). This means after selective exclusion, the toggle's natural next press restores the user's selectively-hidden items. The user can still bulk-exclude after that with one more press.
- Other section toggles (`work`, `education`, `languages`, `projects`) keep their current array-based logic — out of scope.

## Out of scope (explicit)

- No LLM re-prompting after edits.
- No new resume sections.
- No edits flowing back to the global user profile.
- No template / `resume_base.css` changes.
- No reordering of skills (skills are unordered tags; only summary text and skill name/inclusion change).
- No edits to `personal_info`, `education`, `languages`, `projects`, `job_analysis`, `match_reasons` — out per audit table above.

## BDD scenarios

### S1 — Edit summary, see in PDF preview
**Given** a saved job application has a generated resume with an LLM-written summary "Versatile engineer with broad experience.",
**When** the user opens the Resume overview, clicks the summary text, replaces it with "Senior backend engineer focused on payments infrastructure.", and clicks Save,
**Then** the summary on the Edit tab shows the new text within 1 second,
**And** a "Saved" indicator appears for exactly 2000ms (matching the existing pattern at `ResumeView.svelte:110`),
**And** switching to the Preview tab renders the new summary in the PDF preview.

### S2 — Edit summary, reload, persisted
**Given** the user has saved an edited summary on a resume,
**When** the user reloads the page and re-opens the same resume,
**Then** the edited summary is shown (not the original LLM text).

### S3 — Cancel summary edit
**Given** the user is editing the summary and has typed new content,
**When** the user clicks Cancel,
**Then** the textarea closes, the original summary is shown unchanged, and no API call is made.

### S4 — Exclude a skill
**Given** the resume has skills `[Python, Java, Brainfuck, SQL]` all included,
**When** the user clicks the exclude `×` on `Brainfuck`,
**Then** `Brainfuck` moves out of the active list and appears in the "Available" group with a `+` button,
**And** the PDF preview omits `Brainfuck`,
**And** the change is persisted.

### S5 — Re-include an excluded skill restores original position
**Given** the resume's original LLM list was `[Python, Java, Brainfuck, SQL]` and `Brainfuck` is currently excluded,
**When** the user clicks `+` on `Brainfuck` in the Available group,
**Then** `Brainfuck` reappears between `Java` and `SQL` (its original index 2),
**And** the PDF preview shows `Python, Java, Brainfuck, SQL` in that order.

### S6 — Rename a skill
**Given** the resume has skill `Postgres`,
**When** the user clicks Edit on `Postgres`, types `PostgreSQL`, and saves,
**Then** the skill chip displays `PostgreSQL`,
**And** the PDF preview shows `PostgreSQL`,
**And** `matched` and `included` flags on that skill are unchanged.

### S7 — Cancel rename
**Given** the user is renaming a skill and has typed new text,
**When** the user clicks Cancel,
**Then** the chip restores its original name unchanged and no API call is made.

### S9 — Save empty summary
**Given** a saved resume with a non-empty summary,
**When** the user clicks Edit, deletes all text from the textarea, and clicks Save,
**Then** `PUT /api/resumes/{id}` is called with `resume.summary === ""`,
**And** the editor closes,
**And** the personal-info card no longer renders the `<p class="summary">` block,
**And** an `Add summary` affordance appears in its place,
**And** the PDF preview omits the summary block.

### S10 — Section toggle restores selectively excluded skills
**Given** a resume with skills `[Python (included), Java (excluded), SQL (included)]`,
**When** the user clicks the Skills section toggle button,
**Then** all three skills become `included: true` (the rule: any-excluded → re-include-all on first press),
**And** the active list renders `[Python, Java, SQL]` in original order,
**And** the change is persisted.

### S11 — Section toggle then excludes all when nothing is excluded
**Given** all skills on a resume are currently `included: true`,
**When** the user clicks the Skills section toggle,
**Then** all skills become `included: false`,
**And** all chips appear in the Available group.

### S12 — Rename to duplicate name is allowed (no merge)
**Given** a resume with skills `[Python, Postgres, SQL]`,
**When** the user renames `Postgres` → `Python`,
**Then** the saved skills list is `[Python, Python, SQL]` (two distinct entries with the same name),
**And** no warning, merge, or deduplication occurs (rename is a pure name swap on that index).

### S8 — Regeneration does not destroy edits
**Given** the user has edited the summary on resume A for job J,
**When** the user clicks Regenerate and a new resume B is created for job J,
**Then** resume A still exists in the saved-job's resume list with the edited summary,
**And** resume B contains fresh LLM output.

## Success criteria (testable)

1. Click summary → textarea opens with current text pre-filled. (S1, S3)
2. Save summary → `PUT /api/resumes/{id}` is called with updated `resume.summary`; UI shows saved indicator. (S1)
3. Reload after summary save → DB-backed value renders, not LLM original. (S2)
4. Click `×` on a skill chip → that skill's `included` becomes `false`; chip moves to Available group; PDF preview omits it. (S4)
5. Click `+` on an excluded skill → `included` becomes `true`; chip returns to its original index in the active list. (S5)
6. Click Edit on a skill chip → input replaces chip; save persists `name`, leaves `matched` and `included` untouched. (S6, S7)
7. All three edit flows reach the same PDF preview component (`PdfPreview.svelte`) without code duplication of preview logic.
8. Existing work-experience inline-edit and section toggle behaviour is unchanged (regression check).
9. Regenerate continues to create a new `generated_resumes` row; existing rows are untouched. (S8)

## Risks / unknowns to resolve in planning

- **R1 — Original skill order preservation.** If the saved `skills` array is mutated in-place when toggling include/exclude, "original position" is lost on re-include. Need an `original_index` or equivalent (sort key derived once from initial LLM output). The plan must specify whether to add a field to `ResumeSkill` or to keep order stable in the array and only flip `included`.
- **R2 — Rename + match state.** If a user renames `Postgres` → `PostgreSQL`, does `matched` re-evaluate? Spec says no — `matched` stays as-is (it was set from the LLM-generated job analysis at generation time and is now a snapshot). Future feature could re-match locally; out of scope.
- **R6 — Rename to duplicate name.** Resolved in S12: allowed without merge or warning. The skills array can hold two entries with identical `name` post-rename; PDF rendering and persistence treat them as independent entries.
- **R7 — Original-position contract is convention-only.** `ResumeSkill` (`schemas.py:240`) has no `id` or `original_index`. The plan must enforce in code review: new code may **not** call `.filter()`, `.splice()`, `.sort()`, or any method that changes `resumeData.skills` length or order. The only allowed mutations are flag flips (`included`) and field overwrites (`name`). The implementation file header should call this out explicitly.
- **R3 — Empty summary.** What does `summary === ""` mean? Treat as: render no `<p class="summary">` block (consistent with current `{#if resumeData.summary}` guard at `ResumeView.svelte:291`). Save-empty is allowed.
- **R4 — Concurrent edits.** Single-user solo project; no concurrency considered.
- **R5 — Lean-code rule conflict.** Existing JS code uses `handleDownloadPdf`, `getScoreClass`, `formatDate`, `setTimeout` etc. — these violate the lean-code verb table. Per CLAUDE.md scope is "every file you write or modify" — but the project already has many violations. Decision: lean-code rules apply to new functions I add; existing names stay (renaming `handleDownloadPdf` is out of scope for this feature). New functions added by this feature must use permitted verbs.
