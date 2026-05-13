---
feature: restyle-profile-editor
date: 2026-05-13
ceremony_level: M
slice: 3 of 9 (editorial redesign)
---

## What went smoothly

- **Plan-as-paste.** The IMPL_PLAN's code blocks were paste-ready for the new files (`profileStore.svelte.js`, `EditorialSection.svelte`) and the test file. The build agent's job was largely structural assembly, not creative invention.
- **MN-E preservation.** The eight visual-style assertions in `test_user_initials_circle` (width, height, borderRadius, background, color, fontFamily, fontStyle) survived the rewrite verbatim. Only the text expectation changed (`LM` → `IM`) plus a `wait_for_function` gate. The plan-review catch saved a silent coverage loss.
- **Pattern 9 hazard avoided.** Every child's `$effect(() => { count = items.length; })` stayed write-only on `count`. No `effect_update_depth_exceeded`, no `ownership_invalid_mutation`. The plan's hazard table was load-bearing.
- **Test coverage.** 263/263 passes including 6 new restyle tests, the modified topbar-shell test, the design-tokens regression test, and the legacy `test_topbar_renders_at_top`.

## What was harder than expected

- **`.container` test legacy.** `App.svelte`'s outer `.container` would have constrained the 940 px editor column. The naive fix (drop `.container` for profile) broke `test_topbar_renders_at_top`'s `compareDocumentPosition` check, which silently short-circuits to `false` when `.container` is null. The accepted resolution was a class-conditional (`class:container-wide={activeTab === 'profile'}`) plus a one-line CSS override — adds a layer but keeps the legacy test intact. **Takeaway:** when an outer wrapper has tests that ride on its mere existence, prefer adding a sibling class to nullify its constraints over removing the element.
- **WorkExperience's two render blocks.** MN2 (caught at plan-review) flagged that `WorkExperience.svelte` renders both a primary `{#each}` list AND an inline `{#if showForm && !editingId}` add-form block — both with `<input>` / `<textarea>` elements needing the new `.input` / `.textarea` classes. A naive restyle would have updated only the list and left the add-form leaking legacy styles. **Takeaway:** for restyle slices, always grep each component for ALL conditional render branches, not just the steady-state view.
- **localStorage hook temptation.** An early draft of `readProfile()` would have read a `mycv:test_full_name` localStorage key to spoof the user for Playwright tests. M5 review rejected it — it leaked a test code path into the production bundle, made the Topbar user-spoofable via DevTools, and silently invalidated the coalescing test. The accepted approach (`page.route` interception of `/api/users`) keeps the store single-job and the production bundle clean.

## What to do differently next slice

- **Promote inspector bullets to CHECKLIST checkboxes.** MN-A was a process annoyance: the IMPL_PLAN's Manual Inspection bullets (MI-4 through MI-12) lived only in the plan, not as CHECKLIST checkboxes. The inspector subagent read the plan to find them. Next time, the checklist-builder should mirror manual-inspection bullets into CHECKLIST so the inspector has a single source of truth.
- **Pre-existing function names left untouched.** The slice's "lean-code only for new code" rule held. Pre-existing `save()`, `add()`, `edit()`, `validate()`, `formatDate()` were not renamed. A future "lean-code sweep" slice should target those — but trying to bundle it into a restyle would have ballooned scope.

## Candidates for project-checks.md

(No `project-checks.md` exists today; these are seeds if/when one is added.)

- When restyling a form-bearing component with both a read view and an edit/add form, grep all conditional render blocks (`{#if}`, `{#each}` inline forms) and confirm every `<input>` / `<textarea>` / `<select>` in every block receives the new primitive class.
- Before deleting a wrapper component (e.g., `Section.svelte`), run a final consumer-grep. Even if the plan claims a single consumer, partial-name matches (e.g., `ResumeSection.svelte`) can create false hits — anchor the grep with `\.svelte\|import [SymbolName] `.
- When a layout wrapper (`.container`) has legacy tests that ride on its existence, add a conditional sibling class to nullify constraints rather than removing the element. Saves a brittle test rewrite.

## Carry-over to slice 4

- **Topbar `store` named import.** `Topbar.svelte` imports `store` from `profileStore.svelte.js` per the IMPL_PLAN's line 202 verbatim, but `store` is never referenced in the Topbar template/script — `readInitials()` reads `store.profile.full_name` internally. Rollup tolerates the unused import. Slice 4 could clean this up if the import gets flagged by lint, OR add an explicit `// store import kept reachable via readInitials` comment — but per lean-code that comment is forbidden, so the cleaner move is to drop the unused symbol from the import statement next slice if it doesn't break anything.
- **The "MI-6 / MI-10 / MI-11 / MI-12 require backend" pattern** will repeat for every slice that touches a save flow. Worth a project-level decision: should the workflow auto-start `uvicorn` for `/v6-feature` runs, or accept that ~4 manual items per slice remain Skipped-Until-Manual?
