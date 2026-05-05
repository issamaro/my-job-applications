# RETROSPECTIVE — flexible-resume-overview

date: 2026-05-05 (shipped 2026-05-06)
slug: flexible-resume-overview
ceremony: M
prompts_used: 4 (Q0 implicit; Q4 verdict; Q-scope extension; Q-final)

## What surprised

- **Hidden coupling in `ResumeSection.svelte`'s `included` prop.** Both the plan and the plan-reviewer treated `ResumeSection` as opaque (zero-diff gate F4). The component's `included` prop secretly drives two things at once: the toggle button's ON/OFF visual *and* whether children render at all. With per-item curation, passing `resumeData.skills?.[0]?.included !== false` meant excluding skill 0 hid the entire skills body — including the available-group affordance designed to recover from that very state.
- **The bug only surfaced in manual verification.** Automated tests (245 passing) and adversarial plan review didn't catch it. Q4 inspection caught it the moment a real user excluded the first chip. This is exactly the value of the manual verification gate — it punctured an assumption no static check could.
- **Scope extension landed mid-build.** The spec scoped "Available skills" as LLM-picked-and-user-excluded only. The user, on first encounter, immediately wanted un-picked profile skills addable too — not as a re-prompt, but as a one-click append from the existing global skills profile. Implemented in-place (small, derived `availableProfileSkills` + a new `createSkillFromProfile` function).

## What was harder than expected

- Reconciling the spec's "stable original index" invariant with appending profile skills. Resolved cleanly: profile additions go to the end of `resumeData.skills` and inherit the same flag-flip / re-include semantics; the LLM-picked block keeps its original indices intact.
- Deciding the smallest patch for Bug #1 without breaking the zero-diff gate. Chose `included={true}` always for the skills `ResumeSection` rather than modifying the shared component. Trade-off: toggle always reads "ON" — a small visual lie when all skills are excluded, but the inline "All skills excluded" note inside the body makes the actual state legible. Acceptable.

## What the next similar feature should do differently

- **When introducing per-item curation into a section that previously had a binary toggle, audit the toggle component for hidden semantics.** The plan should explicitly ask: "what else does the binary `included` flag drive — visibility, layout, accessibility state?" — not just trust the zero-diff gate.
- **In the analyze phase, ask the user about the breadth of "available."** A single AskUserQuestion at scope time — "does the available list include un-picked items from the user's broader profile?" — would have surfaced the scope extension before plan, not in the middle of build.
- **The `included` prop on `ResumeSection` should probably be split into `visible` and `enabled` (or have a `force-children` opt-out).** If another section ever gets per-item curation, the same trap is set. A small refactor to `ResumeSection.svelte` would make this safer; deferred — out of scope for this feature.

## To add to project-checks.md

- New manual-verification step for any feature that mixes per-item curation with `ResumeSection`: "exclude the **first** item; confirm the section body remains visible and the Available group renders."
- For the next feature touching `resume_content` JSON: confirm that newly added skill entries from profile sources round-trip through `PUT /api/resumes/{id}` without dropping `matched: false`.
