# RETROSPECTIVE — restyle-resume-preview

Date: 2026-05-13
Slice: 4 of 9 — editorial redesign initiative
Ceremony: M (full)

## What landed

- `src/App.svelte` — 1-line container-wide extension to the resume tab.
- `src/components/Topbar.svelte` — dropped the unused `store` named import (slice 3 carryover, MN-A satisfied).
- `src/components/JobAnalysis.svelte` — rewritten body, dropped `--color-*` tokens, swapped `.skill-tag` matched/unmatched for `.pill-positive` / `.pill-warn`, eyebrow `JOB · REQUIREMENTS`, `Hide` / `Show` toggle copy.
- `src/components/TemplateSelector.svelte` — rewrite of body from `<select>` to vertical TemplateCard stack with mini-preview, name, sub, and `● active` marker; `bind:selected` contract preserved.
- `src/components/ResumeView.svelte` — full restyle: editorial header chrome with serif `<h1>` + match pill, 240px left rail (Templates · Language · Sections), Edit/Preview tab toggle with strict ARIA APG semantics, preview pane with paper-3 backdrop + A4 page surface + soft drop shadow, edit pane with seven `EditorialSection` blocks (01–07), preserved every inline-edit affordance (summary draft, skill rename, skill exclude/include, profile-skill add, work drag-reorder, work description edit).
- `src/components/ResumeSection.svelte` — deleted (zero consumers after the ResumeView restyle).
- PDF render path (`templates/resume_base.css`, four template HTMLs, inner `.pdf-preview` markup) — zero edits, hard byte-identity gate satisfied.

## What surprised

- **Legacy class regex collision on new class names.** The CHECKLIST's Scenario 15 grep matches substrings like `.resume-section` and `.skill-action` without word boundaries. The first build introduced `.resume-section-wrapper`, `.resume-section-excluded`, and re-used `.skill-action` as the inner button class — all three collided with the legacy-class regex and surfaced as false positives. Renamed to `.resume-block-wrapper`, `.resume-block-excluded`, `.skill-chip-action` to disambiguate. Lesson: when adopting an editorial taxonomy near legacy class names, pick a clearly non-overlapping prefix (`-block-` instead of `-section-`).

- **Plan-reviewer warning on `:global()` CSS scoping was load-bearing.** The plan-reviewer's MINOR finding flagged that the parent-side `.section-dimmed` rule wouldn't reach the EditorialSection child's `.editorial-section-title` class under Svelte's scoped CSS. Wrapped the rule with `:global(.resume-block-wrapper.section-dimmed .editorial-section-title)` per the warning. Without that catch, the section-dim feature would have silently failed at runtime — the wrapper class would land but no visual dim. The adversarial-review gate paid off here.

- **The first screenshot the user shared was the ResumeGenerator (input form), not ResumeView.** The Tailor CV tab routes to `ResumeGenerator` first; ResumeView is rendered only after opening a specific saved resume. The container-wide extension applies to the whole tab, so the ResumeGenerator input form now sits flush against the viewport edges with no padding. Side-effect of Must-have 1; the form is out of scope for this slice (slice 5 lands the Tailor CV restyle per `SLICE_INDEX.md`).

- **`pytest tests/` passed 263/263 with zero modifications.** The chrome-only nature of the slice meant zero schema, API, or business-logic edits — every existing test passed without touching test files. Slice 3 had similar properties; this is becoming a reliable pattern for the initiative.

## What was harder than expected

- **The Sections checkbox-row state derivation.** Computing the seven-row state cleanly required a `$derived.by(() => …)` that reads `resumeData` and `labels` reactively. The mapping from row label to `toggleSection` key — `Experience → 'work'`, not `'experience'` — was easy to mis-type. The IMPL_PLAN's R-2 explicitly called this out and the implementation honored it. Still worth flagging as a continued risk pattern: derived UI state that doesn't 1:1 map to backend keys is a subtle bug magnet.

- **Section-excluded banner placement inside snippets.** Each `EditorialSection` block needed an in-snippet `{@const rowIncluded = …}` to gate the banner above the content rows. Svelte 5's `{@const}` works inside snippets, but only after the `{#snippet ... ()}` declaration — landed correctly on first try, but the pattern is unintuitive coming from React idioms.

- **TemplateCard mini-preview without a real preview.** The design source shows a generic stylised page sketch (three horizontal bars). Faking the page surface in CSS-only (no image asset, no inline SVG beyond what `<span>`s can render) required nested flex layout for the bars. Acceptable result — but a single Lucide-style icon component for each template would have been cleaner; deferred to a future "template thumbnails" slice if it's ever worth the asset weight.

## What the next similar feature should do differently

1. **Pre-flight grep against my own new class names.** Before writing the IMPL_PLAN's style block list, run the Scenario 15 regex against the proposed new class names locally to catch collisions like `.resume-section-wrapper` matching `\.resume-section`. The PLAN_VERIFIED gate doesn't usually do regex collision checks. Add to project-checks.md as a pre-build step.

2. **State-shape derivation goes into the IMPL_PLAN script-section diff verbatim.** The `sectionRows` derived state was sketched in prose in the plan (lines 110–125), then transcribed to code during build. A pre-tested code snippet in the plan would have been a single copy-paste. The translation step is where typos and missed edge cases sneak in.

3. **Cross-slice CSS scoping is a recurring footgun.** Both slice 3 and slice 4 ran into Svelte's scoped CSS limiting cross-component reach. Add a project-level "use `:global()` for any rule that targets a child component's compiled classes" note to project-checks.md.

4. **Container-wide side-effects on unrelated parents.** Extending `.container-wide` to the resume tab makes ResumeGenerator (the input form) lose its padding. Slice 5 (Tailor CV) will need to either re-add padding to its own root or assume `.container-wide`. Document the contract: any tab that opts into `.container-wide` is responsible for its own horizontal padding.

5. **CHECKLIST should mirror lean-code function-name renames as explicit checkboxes.** This slice renamed `getScoreClass` → `findMatchPillVariant`, `handleDownloadPdf` → `writeDownloadedPdf`. The CHECKLIST's lean-code self-check section covered this generically, but a per-rename checkbox would have made the change traceable in the final commit.

## Anything to add to project-checks.md

(No project-checks.md exists at root or under `.claude/` currently. Items below are candidates if/when one is created.)

1. **Grep new class names against Scenario 15's legacy-class regex before committing** — catches substring collisions like the three this slice hit.

2. **Mandatory `:global()` wrapping** for any CSS rule in a parent that targets a child component's compiled classes. Svelte's scoped CSS will silently drop the rule otherwise.

3. **`.container-wide` opt-in contract** — every screen that opts into `.container-wide` (max-width none, padding 0) is responsible for its own horizontal padding via its outer wrapper. The container itself supplies no padding.

4. **CHECKLIST must promote function renames as explicit checkboxes** (lean-code naming churn — verb-prefix rules apply, and renamed callsites need traceability).

5. **Resume tab routes to two distinct screens** — `ResumeGenerator` (input form, slice 5 target) and `ResumeView` (preview, this slice). Surfacing this in any future Resume-tab slice spec saves a confused screenshot pass.

## Numbers

- Files changed: 6 modified + 1 deleted = 7.
- LoC: ResumeView went from 1046 → ~1240 (more verbose because the editorial layout has more wrappers and explicit ARIA props). Net repo: +194 LoC.
- Tests: 263 / 263 pass, zero modifications.
- Build warnings: 4 (all pre-existing: Topbar role=banner, Languages/ResumeView drag handlers, PdfPreview redundant img alt). Zero new warnings introduced.
- PDF protected files diff: zero bytes.
- Legacy class grep: zero matches.
- Legacy token grep: zero matches.
- Topbar store import: zero matches post-edit.
- Prompts used: 2 (Q4 inspect verdict + user-asked follow-up to navigate into ResumeView). Q0/Q1/Q2/Q3/Q5 all skipped (analyze pre-VERIFIED, libraries reused, single approach, tests passed, change-log clean expected).
