---
slug: chronological-experience-order
date: 2026-05-02
ceremony_level: M
phase: analyze
artifact: feature-spec
---

# Feature Spec — Chronological Experience Order

## Persona
The resume owner / job-seeker. MyCV is a single-user app, so the only actor is the user generating and editing their own tailored resumes.

## Pain
The LLM is currently instructed to reorder work experiences "by relevance to the job." In practice this puts older-but-relevant jobs above recent ones, which looks unprofessional and confuses recruiters who expect reverse-chronological order. The user has no way to fix this on already-generated resumes without regenerating, which costs another LLM round-trip and may reshuffle other content.

## Intent
- Stop instructing the LLM to reorder by relevance.
- Force reverse-chronological order (newest start_date first) **server-side** when generating new resumes, so it's authoritative regardless of what the LLM emits.
- Add a drag-and-drop reorder affordance on the Resume Editor's Work Experience list, so legacy resumes can be reordered manually without regeneration. Reuses the existing pattern from `src/components/Languages.svelte`.

## Scope IN (must-have)
1. Remove the "Reorder work experiences by relevance (most relevant first)" line from `services/llm/base.py` (both occurrences: SYSTEM_PROMPT and USER_PROMPT_TEMPLATE).
2. After the LLM returns work experiences, sort them by `start_date` descending (most recent first) in `services/resume_generator.py` before persisting. Items with `included=true` keep their inclusion flag — only ORDER is enforced.
3. Add drag-and-drop reorder UI to the Work Experience section of `src/components/ResumeView.svelte`. On drop, persist the new order via the existing `updateResume` API (the resume_content JSON's `work_experiences[]` array order IS the persisted order).
4. The reorder must persist across reloads (which is automatic, since saving the resume rewrites the array in the order shown).

## Scope OUT
- Education ordering — only Work Experience changes.
- Inclusion filtering — the LLM may still set `included=false`. Only ORDER of included items is forced chronological at generation time.
- No migration / backfill script for resumes generated before this change. The drag-drop affordance is the fallback.
- No new user-facing toggle to switch between chronological and relevance modes.
- No changes to the profile-side `WorkExperience.svelte` (that already shows the user's own experiences in DB-id order, not in this feature's path).
- No changes to the generation API contract (no new endpoint, no new fields). The `order` field in `ResumeWorkExperience` is descriptive — this feature does not promote it to a sort key, since the array index is the source of truth.

## Success criteria
- An automated test asserts that calling `resume_generator_service.generate(...)` with a profile containing experiences in non-chronological order returns a `resume.work_experiences` list sorted by `start_date` descending.
- An automated test asserts that the LLM prompts in `services/llm/base.py` no longer contain the substring "Reorder work experiences by relevance".
- Manual: opening a previously-generated resume and dragging an item up/down, then reloading, shows the new order.
- Manual: existing already-generated resumes load with their stored order intact.

## BDD scenarios

### Scenario 1 — generation produces chronological order
- **Given** a profile with experiences A (start_date 2020-01), B (start_date 2024-06), C (start_date 2022-03)
- **When** the user generates a resume for any job description
- **Then** the rendered `work_experiences` are ordered B, C, A (newest first)

### Scenario 2 — drag-drop reorder persists
- **Given** a previously-generated resume whose stored `work_experiences[]` order is [A, B, C]
- **When** the user opens the Resume Editor and drags B above A, then reloads the page
- **Then** the work-experience list shows order [B, A, C]

### Scenario 3 — included=false items don't appear, remaining items stay chronological
- **Given** a profile with experiences X (2024, marked `included=false` by LLM), Y (2023), Z (2022)
- **When** the user generates a resume
- **Then** X is hidden and the visible list is [Y, Z]

### Scenario 4 — current position (end_date null) sorts chronologically by start_date
- **Given** a profile with experiences P (start_date 2024-01, ongoing/end_date null) and Q (start_date 2023-06, end_date 2024-12)
- **When** the user generates a resume
- **Then** P appears above Q (current job above past job, both ordered by start_date)

## Non-functional notes
- No performance regression: sort is O(n log n) on a list that's typically <20 items.
- No new dependencies. All work uses HTML5 drag-drop (already proven in Languages.svelte) and stdlib `sorted()` in Python.
- Accessibility: drag-drop is the primary affordance; keyboard reorder is OUT of scope for this feature (Languages.svelte also doesn't support keyboard reorder yet — would be a separate cross-cutting fix).
