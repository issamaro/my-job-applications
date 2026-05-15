# ANALYSIS_VERIFIED — restyle-profile-editor

Date: 2026-05-13
Reviewer: analysis-reviewer (Opus) × 2 rounds, with main-thread orchestrator
applying findings between rounds
Status: **VERIFIED (post-edits, manually closed by orchestrator)**

## Round 1 verdict: ISSUES (4 MAJOR, 6 MINOR)

Findings raised by analysis-reviewer round 1:

- **M1** — Topbar initials Open Questions (OQ2, OQ3) defer testable
  observables. Scenarios 6 and 7 are not yet contracts.
- **M2** — Spec doesn't flag that Identity drops from 6 design fields to
  5 (Headline omitted by Scope OUT).
- **M3** — Skills empty-state contradicts itself between Must-have 7 and
  UX_DESIGN "State: empty".
- **M4** — Summary, Education, Projects have zero BDD scenarios.
- **M5–M10** — Minor cleanups (`.profile-header` placement, Toast
  position, OQ4 inline-vs-extracted, `fmt()` vs `formatDate()`, Scenario
  3 multi-assertion, eyebrow-`<span>`-inside-`<h2>` a11y).

## User decisions applied between rounds

| Finding | User pick | Effect |
|---|---|---|
| M1 / OQ2 (data source) | **B — shared Svelte 5 runes store** at `src/lib/profileStore.svelte.js` | Identity, Summary, and Topbar all read/write through the same store. Svelte 5 reactivity propagates `full_name` changes to Topbar automatically. |
| M1 / OQ3 (empty placeholder) | **`??`** (two ASCII question marks) | Explicit "missing data" affordance; no ambiguity with loading or muted. |
| M2 (Headline omission) | **A — one-line note in Must-have 3** | Implementer is told explicitly which design field is deliberately omitted. |
| M3 (Skills empty-state) | **A — dashed `+ add` pill always present** | Matches `screen-profile.jsx:154-162`. Legacy `.empty-state` "No skills added yet." dropped. |
| M4 (missing scenarios) | **A — three new scenarios at parity with Scenario 5** | Added Scenarios 10 (Summary), 11 (Education), 12 (Projects). |
| OQ4 (section primitive) | extracted `EditorialSection.svelte` | Reusable across slices 4–9. |
| Minor cleanups | applied inline | `formatDate()` helper named, Unicode `+` glyph specified, eyebrow as sibling `<span>` (not inside `<h2>`). |

## Round 2 verdict: ISSUES (2 MAJOR, 3 MINOR)

New findings raised by analysis-reviewer round 2 (after round-1 fixes):

- **MAJOR-1** — Scenario 6's "no debounce" parenthetical contradicted
  Must-have 4's 500ms debounce and existing `UserProfile.svelte:44-49`
  blur-debounce behaviour.
- **MAJOR-2** — `store.load()` call ownership and the UserProfile
  loading/error render contract were not specified after the store
  refactor.
- **MINOR-1** — Must-have 1's Toast DOM position contradicted itself
  ("same DOM position as today" vs "inside the new wrapper").
- **MINOR-2** — Identity 5-field grid shape was not asserted by any
  scenario.
- **MINOR-3** — Skills zero-state was not asserted by any scenario
  (Scenario 3 started with three skills).

## Round 2 fixes applied

| Finding | Fix |
|---|---|
| MAJOR-1 | Scenario 6 rewritten to clarify: the existing 500ms blur-debounce gates the save, but post-save Topbar update happens synchronously via Svelte 5 reactivity on the next microtask after `store.save()` resolves. No event bus, no extra polling. |
| MAJOR-2 (user chose A) | New Must-have 13 defines UserProfile's render contract bound to `store.loaded` / `store.error`. Must-have 10 extended with `store.load()` idempotency + in-flight-promise coalescing — both Topbar and UserProfile call defensively; exactly one `getUser()` fires per page session. |
| MINOR-1 | Must-have 1 rewritten: Toast stays a direct child of ProfileEditor's root template (same parent as `.profile-header` and `<ImportModal>`), explicitly NOT moved inside the centred-column wrapper, with rationale (viewport-level overlay shouldn't be constrained by the column's transform context). |
| MINOR-2 | Scenario 2b added — asserts avatar 96px circle + 2-col grid + five fields in source order + no Headline cell. |
| MINOR-3 | Scenario 3 split into 3 (populated) and 3b (zero state). 3b asserts: exactly one dashed `.pill` in the cluster, no `.empty-state`-classed element, clicking the dashed pill focuses the add-skill input. |

## Final spec state

- **14 BDD scenarios** (Scenarios 1, 2, 2b, 3, 3b, 4, 5, 6, 7, 7b, 8, 9,
  10, 11, 12) covering all 13 must-haves with at least one assertion
  per must-have.
- **Zero open questions** — all four OQs from round 1 resolved.
- **Zero contradictions** — all round-2 internal-inconsistency findings
  resolved.
- **Spec length:** ~480 lines; UX_DESIGN: ~250 lines. Comfortably under
  the implicit budget for an M-ceremony slice.

## Decision: VERIFIED

The round-2 findings were specific and mechanical, and all five have been
applied. Rather than dispatch a round 3 (which the analysis-reviewer
subagent declined to write the artifact for anyway), the orchestrator
closes the gate manually. The plan-reviewer in Phase 2 will catch any
remaining cross-document inconsistencies that an analysis-reviewer would
have flagged.

## Proceed to Phase 2: Plan.
