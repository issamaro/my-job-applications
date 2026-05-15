---
slug: chronological-experience-order
date: 2026-05-02
ceremony_level: M
phase: ship
artifact: retrospective
---

# Retrospective — Chronological Experience Order

## What surprised

**The drag-drop pattern was already a perfect template.** The plan budget for the Svelte 5 frontend assumed I'd need to look up runes syntax (`$state` reactivity rules for arrays, `ondrop` event handler signatures). Instead, `Languages.svelte:127-164` already had the exact pattern, and the only adaptation needed was scoping CSS to `.work-item` instead of `.item`. Skipping `docs-researcher` for Svelte 5 was the right call — in-repo references beat external docs when the project already has a working precedent.

**The drift between FEATURE_SPEC's "the array order is the source of truth" claim and the unused `order: int = 0` field on `ResumeWorkExperience`.** The schema has had this field for a long time without it actually controlling anything. The plan correctly flagged it as descriptive-only ("does not promote it to a sort key"), but a future feature that *does* try to use it would discover the same gotcha. Worth noting for project-checks.

## What was harder than expected

**Lean-code naming for HTML5 drag-drop event handlers.** The lean-code spec (CLAUDE.md) forbids `handleX` and only permits 9 verbs (read, write, create, delete, update, find, check, parse, render). Drag-drop callbacks are intrinsically "handle X event" callbacks — the spec doesn't fit. I ended up with `updateDraggedIndex`, `updateOrderOnHover`, `writeReorderedOrder`, `deleteDraggedIndex`. Internally consistent, but stylistically awkward. Plan-reviewer flagged this as MINOR (F4). Existing in-repo code (`Languages.svelte`) uses `handleDragStart`, etc. — those are pre-feature legacy and untouched here, but a future cleanup pass would benefit from a project-level decision: either widen the verb list with "handler" semantics or accept that event-handler naming is exempt.

## What the next similar feature should do differently

1. **When a feature reuses an existing in-repo pattern, name the canonical reference at the top of IMPL_PLAN and skip docs-research entirely.** I did this here for Svelte 5 / Languages.svelte and saved a research round.
2. **For frontend-touching features, start the dev server before dispatching `inspector`.** I started it after the build phase tests passed; doing it before would let the inspector validate URL reachability itself.
3. **Group inspector bullets by theme into 4 batches when there are >4 bullets.** The 12-bullet payload didn't fit AskUserQuestion's 4-question×4-option ceiling. I batched into 4 themes (Handle, Reorder, States, A11y+Gen). This pattern should be the default for inspector return.

## Anything to add to project-checks.md

- **`ResumeWorkExperience.order` field gotcha.** The field exists on the schema but has no effect on rendering or persistence. Array index in `resume_content.work_experiences` is the source of truth. If a future feature wants to drive ordering from the schema field, it must rewrite both the generator's sort and the editor's reorder-write paths.
- **Lean-code verb gap for event handlers.** Project should decide whether HTML5 event handlers are exempt from the 9-verb rule, or pick canonical mappings (e.g., always `update*` for state-mutating callbacks).
- **No keyboard-reorder for drag-drop lists.** Both `Languages.svelte` and the new `ResumeView.svelte` work-experience drag-drop lack keyboard alternatives. A future a11y-focused feature should add this across both surfaces simultaneously.
