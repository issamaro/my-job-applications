# IMPL_PLAN — flexible-resume-overview

date: 2026-05-05
slug: flexible-resume-overview
ceremony: M

## Strategy at a glance

The feature is a pure front-end extension: every backend contract this needs (`PUT /api/resumes/{id}` accepting a full `ResumeContent`; `ResumeSkill.included: bool = True`; `ResumeSkill.name: str` mutable) is already in place. The work is two new editing affordances inside `src/components/ResumeView.svelte`, a tightening of the existing `toggleSection('skills')` handler, and three to four new tests.

No new component files. Adding new components for "summary editor" and "skills editor" would scatter shared state (`resumeData`, `editingId`, `saving`, `savedId`, `toastMessage`) across files, violating CLAUDE.md "Do NOT scatter one operation across multiple files/classes." The work-experience pattern lives inline in this file already; the new pattern lives in the same file beside it.

No new API endpoints. No new schema fields. No DB migration.

## Library posture

Single library: Svelte 5 (`^5.0.0`, per `package.json:14`). All patterns the plan uses (`$state`, `$derived`, `$props`, `{#if}`, snippets, `bind:value`, `onclick`) are already in `src/components/ResumeView.svelte` and `src/components/PdfPreview.svelte` — no new APIs, no version concerns. Skipping parallel docs research per the orchestrator carve-out for `libraries ≤ 1` plus established pattern in the same file.

## File-by-file plan

### F1 — `src/components/ResumeView.svelte` (modify)

Touch points:

#### F1.1 — New state slots (script block, around lines 57-68)

Add five new `$state` vars immediately after the existing `editingId` / `editValue` / `saving` / `savedId` group:

- `let editingSummary = $state(false);` — boolean, single instance (only one summary per resume).
- `let summaryDraft = $state('');` — buffer for the textarea while editing.
- `let editingSkillIndex = $state(null);` — number | null, the array index of the skill being renamed; null when no skill rename is open.
- `let skillDraft = $state('');` — buffer for the rename input.
- `let savingSkillIndex = $state(null);` — number | null, index of skill currently mid-save (used to drive the per-chip `opacity: 0.5` per UX B.4).

These five vars are all locally scoped to ResumeView.svelte; nothing leaks out via props.

#### F1.2 — New functions (script block, after `cancelEdit` at line 121, before `toggleSection` at line 123)

All functions follow lean-code verb prefixes from CLAUDE.md.

- `function startEditSummary()` — sets `summaryDraft = resumeData.summary || ''; editingSummary = true;`. One job.
- `function cancelEditSummary()` — sets `editingSummary = false; summaryDraft = '';`. One job.
- `async function writeSummaryEdit()` — sets `saving = true`; assigns `resumeData.summary = summaryDraft`; awaits `updateResume(resume.id, resumeData)`; on success: `editingSummary = false; savedId = '__summary__'; setTimeout(() => savedId = null, 2000);`; on failure: emits `toastType = 'error'; toastMessage = 'Could not save summary. Try again.';` and leaves the editor open. Mirrors the existing `saveEdit()` shape at lines 100-116. The sentinel string `'__summary__'` is used because `savedId` already drives a per-work-experience saved badge by ID; `'__summary__'` cannot collide with any work-experience id (those are numeric).
- `function startEditSkill(skillIndex)` — sets `skillDraft = resumeData.skills[skillIndex].name; editingSkillIndex = skillIndex;`. One job.
- `function cancelEditSkill()` — `editingSkillIndex = null; skillDraft = '';`. One job.
- `async function writeSkillRename(skillIndex)` — guard: if `skillDraft.trim() === ''`, treat as cancel (do not save empty name). Otherwise assign `resumeData.skills[skillIndex].name = skillDraft.trim(); savingSkillIndex = skillIndex;` then await `updateResume(...)`. On error revert via `resumeData = JSON.parse(JSON.stringify(resume.resume));` and toast (same shape as reorder error at lines 178-181). Settle: `savingSkillIndex = null; editingSkillIndex = null;`.
- `async function updateSkillInclusion(skillIndex, included)` — single function for both exclude and re-include. Sets `savingSkillIndex = skillIndex`; assigns `resumeData.skills[skillIndex].included = included;`; await save; toast on success (`'Saved'`) or revert + error toast on failure; clear `savingSkillIndex`.

Lean-code self-check on the verb table: `start*`, `cancel*` are not in the nine permitted verbs. Looking at existing precedent: `startEdit`, `cancelEdit`, `saveEdit`, `getScoreClass`, `formatDate`, `formatWorkDate`, `handleDownloadPdf` already exist in this file and break the rule. Per FEATURE_SPEC R5 decision, I'm not refactoring legacy names but new code should comply where it makes sense. Decision per the spec carve-out: keep `startEditSummary/cancelEditSummary/startEditSkill/cancelEditSkill` for symmetry with the local convention used at lines 95-121 (`startEdit/cancelEdit/saveEdit`); use `writeSummaryEdit / writeSkillRename / updateSkillInclusion` for the save-side functions which DO comply with the verb table. This is intentional and noted here so the plan-reviewer doesn't flag a false positive.

#### F1.3 — Modify `toggleSection('skills')` (lines 129-133)

Replace the body of the `else if (section === 'skills')` branch with the deterministic two-state rule from MH-6 / UX B.0:

```js
} else if (section === 'skills') {
  const anyExcluded = resumeData.skills.some(s => s.included === false);
  resumeData.skills = resumeData.skills.map(s => ({ ...s, included: anyExcluded }));
}
```

`anyExcluded === true` → re-include all (set `included: true`). `anyExcluded === false` → all currently included → exclude all. This change is **only** to the `skills` branch; `work`, `education`, `languages`, `projects` branches at lines 124-128, 134-148 are untouched.

Note: `toggleSection` does NOT persist on its own today — the pattern is local-state-only, persisted by the next save. To satisfy S10 / S11 ("the change is persisted"), the new skills branch persists immediately via the same `updateResume` call shape used elsewhere in this file.

Final shape of the modified handler:

```js
async function toggleSection(section) {
  if (section === 'work') { /* unchanged */ }
  else if (section === 'skills') {
    const previous = JSON.parse(JSON.stringify(resumeData.skills));
    const anyExcluded = resumeData.skills.some(s => s.included === false);
    resumeData.skills = resumeData.skills.map(s => ({ ...s, included: anyExcluded }));
    try {
      await updateResume(resume.id, resumeData);
    } catch (err) {
      resumeData.skills = previous;
      toastType = 'error';
      toastMessage = 'Could not save skills. Try again.';
    }
  }
  else if (section === 'education') { /* unchanged */ }
  else if (section === 'projects') { /* unchanged */ }
  else if (section === 'languages') { /* unchanged */ }
}
```

The function becomes `async`. All callers via `onToggle={() => toggleSection('skills')}` continue to work — Svelte's event handlers accept functions returning a Promise; the returned promise is simply not awaited at the call site. The other branches (`work`, `education`, `projects`, `languages`) do nothing async and return immediately, so the async return is harmless for them. No change to `ResumeSection.svelte` is required.

#### F1.4 — Modify the personal-info card markup (lines 277-295)

Replace the current `{#if resumeData.summary}` block (lines 291-293) with one that respects the editing state:

- When `editingSummary === true`: render a `<textarea bind:value={summaryDraft} rows="4" autofocus></textarea>` followed by `[Save] [Cancel]` buttons. Mirror the work-experience inline edit at lines 322-333. `Save` calls `writeSummaryEdit()`, disabled while `saving`. `Cancel` calls `cancelEditSummary()`.
- When `editingSummary === false` and `resumeData.summary` is truthy: render the existing `<p class="summary">{resumeData.summary}</p>` followed by an `[Edit]` button (`<button class="edit-btn" onclick={startEditSummary}>Edit</button>`) and a saved-indicator span shown when `savedId === '__summary__'`.
- When `editingSummary === false` and `resumeData.summary` is falsy: render an `[Add summary]` button instead. `onclick={startEditSummary}` (same handler — opens the textarea pre-empty).

Keyboard: `Esc` on the textarea triggers `cancelEditSummary()` via `onkeydown`. `Cmd/Ctrl+Enter` triggers `writeSummaryEdit()`. Implement via a single small handler `handleSummaryKey(e)` defined alongside the others. (Verb-table note: `handle*` is on the forbidden list — rename to `readSummaryKey` or `parseSummaryKey`. Pick `parseSummaryKey` since it transforms a key event into a routed action — plausible reading of the verb. Actually that's strained; `read` is closer ("read the key and dispatch"). Decision: `readSummaryKey(e)`.)

#### F1.5 — Modify the skills section markup (lines 354-368)

Replace the `{#snippet children()}` body of the Skills section with two snippets / branches:

```
Active group:
  {#each resumeData.skills as skill, index}
    {#if skill.included !== false}
      <span class="skill-tag" class:matched={skill.matched} class:saving-skill={savingSkillIndex === index}>
        {#if editingSkillIndex === index}
          <input bind:value={skillDraft} onkeydown={readSkillKey} aria-label="Rename skill {skill.name}" />
          <button onclick={() => writeSkillRename(index)} aria-label="Save skill name">✓</button>
          <button onclick={cancelEditSkill} aria-label="Cancel rename">×</button>
        {:else}
          {skill.name} {skill.matched ? '✓' : ''}
          <button class="skill-action" onclick={() => startEditSkill(index)} aria-label="Rename skill {skill.name}">✎</button>
          <button class="skill-action" onclick={() => updateSkillInclusion(index, false)} aria-label="Exclude skill {skill.name}">×</button>
        {/if}
      </span>
    {/if}
  {/each}

Available group (only if any excluded):
  {#if resumeData.skills.some(s => s.included === false)}
    <h4 class="available-skills-header">Available skills</h4>
    <div class="skill-tags available">
      {#each resumeData.skills as skill, index}
        {#if skill.included === false}
          <span class="skill-tag excluded" class:saving-skill={savingSkillIndex === index}>
            {skill.name}
            <button class="skill-action" onclick={() => updateSkillInclusion(index, true)} aria-label="Re-include skill {skill.name}">+</button>
          </span>
        {/if}
      {/each}
    </div>
  {/if}

  {#if resumeData.skills.length > 0 && resumeData.skills.every(s => s.included === false)}
    <p class="all-excluded-note">All skills excluded — re-include one below, or use the section toggle.</p>
  {/if}
```

Critical: the `{#each}` iterates over the **stable array** `resumeData.skills` and filters via `{#if}`. This guarantees the original index passed to `updateSkillInclusion(index, …)` matches the position in `resume_content.skills`, which is the load-bearing invariant from FEATURE_SPEC R7 and UX B.7. Do NOT use `.filter()` to derive a sublist for `{#each}` — that would lose the stable index.

Per CLAUDE.md "ZERO comments. No inline comments." — no inline comment will be added. The invariant is communicated by:
- The function names themselves (`updateSkillInclusion`, `writeSkillRename` — only flag and name mutations, never reorder).
- The plan + spec + UX as durable documentation outside the source file.
- The pattern is already established in this file's existing work-experience drag-reorder code, which iterates the stable array.

`readSkillKey` handles `Enter` → save, `Esc` → cancel, on the rename input (mirrors `readSummaryKey`).

#### F1.6 — New CSS (style block, append to existing `.skill-tag` rules at lines 705-719)

- `.skill-tag .skill-action { … }` — small button, `border: none; background: none; cursor: pointer; padding: 2px 4px; font-size: 12px; opacity: 0.6;` with `:hover { opacity: 1; }` and `:focus { outline: 2px solid var(--color-primary); outline-offset: 1px; }`.
- `.skill-tag.saving-skill { opacity: 0.5; pointer-events: none; }` — implements UX B.4 loading state.
- `.skill-tag.excluded { opacity: 0.5; }` — Available group styling.
- `.skill-tag input { min-width: 100px; max-width: 300px; field-sizing: content; }` with a fallback selector `@supports not (field-sizing: content) { .skill-tag input { width: 160px; } }`.
- `.available-skills-header { font-size: 12px; color: rgb(var(--color-text-rgb) / 0.6); margin-top: 12px; margin-bottom: 6px; font-weight: 500; text-transform: uppercase; }`.
- `.all-excluded-note { font-size: 13px; color: rgb(var(--color-text-rgb) / 0.6); font-style: italic; }`.
- `.summary-edit textarea { width: 100%; }` — wrapper class around the new summary textarea (mirror existing `.inline-edit textarea` at line 608).
- `.summary-add-btn` — same as `.edit-btn` but small, used for the empty-state Add summary CTA. Could simply reuse `.edit-btn` and apply text "Add summary" — decision: reuse `.edit-btn`, no new class needed.

No changes to existing rules at lines 705-719 (matched class etc.).

### F2 — `tests/test_resumes.py` (add three new tests)

Existing `test_update_resume` at line 163 already covers summary update via PUT. Add three new pytest tests next to it:

- `test_update_resume_skill_excluded` — POST a generation, then PUT with one skill `included: false`; assert GET returns the same skills list with that skill still present and `included === False`.
- `test_update_resume_skill_renamed` — same shape but mutate the skill's `name`; assert round-trip preserves new name and unchanged `matched`/`included`.
- `test_update_resume_summary_empty` — PUT with `summary: ""`; assert GET returns `summary: ""` (not None and not the prior value).

These exercise the back-end contract end-to-end and are the regression catch in case someone changes `update_resume` to drop fields with falsy values. Use the `client` fixture from `tests/conftest.py` (defined at conftest.py:26-29) and decorate each test with `@patch("services.resume_generator.llm_service.analyze_and_generate")` exposing `mock_llm` as the first parameter — that's the pattern at `tests/test_resumes.py:162-163`. `mock_llm` is NOT a conftest fixture; it's a `unittest.mock.patch` object provided by the decorator.

No frontend tests added — the project has no JS test runner configured (`package.json` lacks `test` script and no `vitest`/`jest` listed). Out of scope.

### F3 — `src/components/PdfPreview.svelte` (no change)

`includedSkills` derived at lines 56-58 already filters on `included !== false`, so excluded skills naturally disappear from the preview. Renamed skill names already render via `{skill.name}` at line 137 / 204. Edited summaries already render via `{@render summarySection(resumeData.summary)}` at lines 222 / 246 / 268. **No changes needed.**

### F4 — `src/components/ResumeSection.svelte` (no change expected)

The `onToggle` callback wires through to `toggleSection('skills')` — that's the only relationship. Treating `ResumeSection` as opaque. No changes.

### F5 — Backend (no change)

- `routes/resumes.py:59-64` PUT endpoint — accepts whole `ResumeContent`; no change.
- `services/resume_generator.py:137-167` — round-trips arbitrary `ResumeContent`; no change.
- `schemas.py:240` `ResumeSkill` — already has `included: bool = True` and `name: str` mutable; no change.
- `database.py` — `resume_content` is a JSON blob; no migration.

## Risks

- **R-Plan-1 — The personal-info card uses a `.contact-line` margin class that may collide with the new save/cancel buttons inside it.** Mitigation: wrap the new summary-edit affordance in a dedicated `.summary-edit` div so it inherits no inherited margin from siblings.
- **R-Plan-2 — `field-sizing: content` is unsupported in some browsers.** Mitigation: `@supports not` fallback at 160px fixed (already in F1.6).
- **R-Plan-3 — `autofocus` on conditionally rendered inputs is unreliable in some frameworks.** Resolved: this codebase already uses the `{#if editing}<input … autofocus />` pattern at `src/components/SavedJobItem.svelte:118-128`, with a `<!-- svelte-ignore a11y_autofocus -->` directive on the line above. Mirror exactly that pattern for both the summary textarea and the skill rename input. No `bind:this`, no `$effect`, no extra state. The svelte-ignore directive IS allowed since it's a compiler hint, not a documentation comment.
- **R-Plan-4 — `setTimeout` clearing `savedId` collides if both summary save and skill rename save happen in rapid succession.** Mitigation: only the summary save uses `savedId`. Skill rename uses `savingSkillIndex` only and shows toast — no `savedId` indicator per UX B.4 decision. So no collision.
- **R-Plan-5 — The "any excluded → re-include all" rule for the section toggle has surprising UX if user has excluded one skill, presses toggle expecting "exclude all," and instead gets "re-include all."** Documented in MH-6 and accepted; the BDD scenarios codify the rule as the contract.
- **R-Plan-6 — Testing the toggle's persistence (S10/S11 say "the change is persisted") changes `toggleSection` from local-state-only to async-PUT for the skills branch only.** Documented in F1.3 with explicit try/catch and revert-on-error. The asymmetry is acceptable and is the only way to satisfy the spec without a separate "Save batch" affordance.
- **R-Plan-7 — Toast component duration is 3000ms (`Toast.svelte:12`).** UX_DESIGN B.4 / S1 reference "2000ms" — that's specifically the **savedId** badge inside the personal-info card (the `setTimeout` at `ResumeView.svelte:110`), not the Toast. The Toast naturally lasts 3s as defined in `Toast.svelte`; we do not pass a duration. Implementation simply sets `toastMessage` and `toastType`, mirroring the reorder pattern at `ResumeView.svelte:174-181`. No duration tweak needed.

## Test plan

- Run existing `pytest tests/` — must stay green (covers the 14 modules in `tests/`).
- Run new three tests in `test_resumes.py` — must pass.
- Run `bun run build` (or `npm run build`) — Svelte compile must succeed (no TS, but `rollup-plugin-svelte` does syntax + reactivity checks).
- Manual verification (inspector phase): cover BDD scenarios S1–S12 in a real browser against `app.db`.

## Out-of-plan items (explicit non-decisions)

- No drag-reorder of skills.
- No undo/redo.
- No batch rename UI.
- No new component files.
- No backend schema or route changes.
- No translations of new copy.
- No reactive re-fetch of `resumeData` from server after every save (existing pattern: server response from `updateResume()` is awaited but the local `resumeData` is the source of truth for re-render until next reload). Continue that pattern.
