# UX_DESIGN — flexible-resume-overview

date: 2026-05-05
slug: flexible-resume-overview

## Surfaces affected

Single surface: the **Resume overview > Edit tab** at `src/components/ResumeView.svelte`. Two regions inside that surface:

- **A.** Personal-info card → contains the `summary` block at lines 291-293.
- **B.** Skills section → list of chips at lines 360-367.

The PDF preview (`PdfPreview.svelte`) is read-only consumer of `resumeData`; no UI changes there beyond what reactive props give us for free.

## Design intent

Mirror the existing work-experience inline-edit pattern (`ResumeView.svelte:321-347`):
- Click an Edit affordance → swap the display element for an input (textarea for summary; small text input for skill name).
- Save / Cancel buttons next to the input.
- Saved-indicator badge appears for ~2s after success (mirror `savedId` pattern at `ResumeView.svelte:108-110`).

Mirror the existing per-section toggle for **batch** include/exclude already at `ResumeView.svelte:354-368` — but add a per-item exclude affordance per skill chip.

---

## Region A — Summary inline edit

### A.1 Display state (default)
```
┌─ Personal-info card ─────────────────────────┐
│ Jane Doe                                      │
│ jane@…  ·  +32 …                              │
│ Brussels  ·  linkedin.com/in/jane             │
│                                               │
│ Versatile engineer with broad experience.     │
│                                              [Edit]
└───────────────────────────────────────────────┘
```
- Summary text rendered as today (`<p class="summary">`).
- New `[Edit]` button, right-aligned under the summary, same `.edit-btn` class as work-experience's edit button.

### A.2 Editing state
```
┌─ Personal-info card ─────────────────────────┐
│ Jane Doe                                      │
│ jane@…  ·  +32 …                              │
│ Brussels  ·  linkedin.com/in/jane             │
│ ┌───────────────────────────────────────────┐ │
│ │ Versatile engineer with broad…           │ │
│ │                                          │ │
│ └───────────────────────────────────────────┘ │
│ [Save] [Cancel]                               │
└───────────────────────────────────────────────┘
```
- `<textarea>` with 4 rows, full card width, pre-filled with current `summary`.
- `[Save]` (primary), `[Cancel]` (secondary). Same classes as work-experience.

### A.3 Saving state
- `[Save]` label changes to `Saving…` and is disabled (mirror `disabled={saving}` at line 328).
- `[Cancel]` is also disabled to prevent stale-cancel.

### A.4 Saved state (transient, ~2s)
```
│ Versatile engineer with broad experience.     │
│ Saved        ←  small green text, fades after 2s
│                                              [Edit]
```
- Badge "Saved" appears alongside `[Edit]`. Mirror the existing `savedId === exp.id` pattern at lines 343-345.

### A.5 Empty-summary state
- If `summary === ""` after save, the card renders no summary line (existing `{#if resumeData.summary}` guard kept).
- An `[Add summary]` affordance appears in place — clicking opens the textarea pre-empty.

### A.6 Error state
- API failure → existing `Toast` component (already used at `ResumeView.svelte:432`) shows `"Could not save summary. Try again."` (red). Editing state stays open so the user can retry.

### A.7 Keyboard / a11y
- `[Edit]` button is keyboard-focusable; `Enter` opens the editor.
- Inside the textarea, `Cmd/Ctrl+Enter` saves; `Esc` cancels.
- Saved indicator uses `aria-live="polite"` so screen readers announce "Saved".
- Focus returns to `[Edit]` after save/cancel.

---

## Region B — Skills curation

### B.0 Section toggle behavior (revised)
- The existing per-section `toggleSection('skills')` at `ResumeView.svelte:129-133` is rewritten with a deterministic two-state rule:
  - If `resumeData.skills.some(s => s.included === false)` → set every skill to `included: true` (re-include all).
  - Otherwise → set every skill to `included: false` (exclude all).
- Behavior contract: after a user has selectively excluded items, the **first** press of the section toggle restores them; the second press excludes everything; the third re-includes everything. This is testable via S10 + S11.
- Other sections (`work`, `education`, `languages`, `projects`) are NOT changed.

### B.1 Display state (default — at least one skill, all included)
```
Skills                                 [Toggle section]
─────────────────────────────────────────
Active:
  ┌──────┐ ┌──────┐ ┌──────────┐ ┌─────┐
  │Python│ │Java  │ │Brainfuck │ │SQL  │
  │ ✓ ✎ ×│ │ ✎ × │ │   ✎ ×    │ │✓ ✎ ×│
  └──────┘ └──────┘ └──────────┘ └─────┘

Available (excluded — click + to re-include):
  (empty)
```
- Each chip shows: skill name, `✓` if `matched` (existing affordance), `✎` (edit/rename), `×` (exclude).
- Hover reveals affordances if they're not always visible (decision: always-visible to avoid hover-only on touch).
- The existing per-section toggle at the section header is **kept** (batch include/exclude all). Per-item × is in addition.

### B.2 Display state — some excluded
```
Active:
  ┌──────┐ ┌──────┐ ┌─────┐
  │Python│ │Java  │ │SQL  │
  │ ✓ ✎ ×│ │ ✎ × │ │✓ ✎ ×│
  └──────┘ └──────┘ └─────┘

Available (excluded — click + to re-include):
  ┌──────────┐
  │Brainfuck │
  │    +     │
  └──────────┘
```
- "Available" header shown only when ≥1 skill is excluded.
- Available chips are dimmer (e.g., 50% opacity) and only show `+`.
- Re-including a skill restores it to its original index — see B.7 ordering rule.

### B.3 Editing skill name (rename)
```
  ┌──────────────┐
  │ [Postgres__] │  ← inline input pre-filled
  │ [✓] [×]      │
  └──────────────┘
```
- Chip swaps for an input + small Save / Cancel (icon buttons `[✓] [×]`).
- `Enter` saves; `Esc` cancels.
- Width: CSS `min-width: 100px; max-width: 300px; width: auto;` with `field-sizing: content` if supported (modern Chromium / Safari TP); otherwise a fixed 160px input. Saved name displays in original chip layout (no width change).

### B.4 Saving / saved (per-item)
- **Loading:** while the PUT call is in flight, the affected chip's wrapper element gets `opacity: 0.5` and `pointer-events: none`. No spinner. The chip dims for the duration of the network request only — when the promise resolves (success or error), the dim is removed.
- **Success:** no per-chip persistent indicator. The existing `Toast` (already in the file, hard-coded 3000ms duration at `Toast.svelte:12`) emits a single "Saved" message via the same `toastMessage` / `toastType` state used by the reorder flow at `ResumeView.svelte:175-180`.
- **Error:** dim is removed; toast emits "Could not save skills. Try again." (red); `resumeData = JSON.parse(JSON.stringify(resume.resume))` reverts local state (mirror of lines 178-180).

### B.5 Error state
- API failure → toast `"Could not save skills. Try again."` (red).
- Local optimistic update is reverted (re-fetch resume from server, mirror reorder error handling at `ResumeView.svelte:178-181`).

### B.6 Empty states
- **No skills at all:** the section header still renders with the existing toggle; body says "No skills." (No new edit affordance.)
- **All skills excluded:** Active group says "All skills excluded — re-include below or use the section toggle to bring them all back."

### B.7 Ordering rule (critical)
- The `skills` array order in `resume_content` is the **original LLM order**. Excluding does not reorder; including does not reorder; renaming does not reorder. Only `included` and `name` mutate.
- The Active group renders `skills.filter(s => s.included !== false)` in the same order.
- The Available group renders `skills.filter(s => s.included === false)` in the same order.
- Re-including is purely a flag flip, so the active list naturally re-receives the skill at its original position.
- The PDF preview already filters on `included` (`PdfPreview.svelte:56-58`), so PDF order matches.
- **Code rule:** new code MUST NOT call `.filter()`, `.splice()`, `.sort()`, `.push()`, or `.pop()` on `resumeData.skills` in a way that mutates the array. Filtering for rendering only is fine (it produces a new array; the source stays intact). The implementer adds an inline note in the new component or section file referencing this rule (one comment is permitted as a load-bearing invariant note per the "non-obvious why" carve-out).

### B.8 Keyboard / a11y
- Each affordance is a `<button>` with `aria-label`: `"Edit skill {name}"`, `"Exclude skill {name}"`, `"Re-include skill {name}"`.
- Focus order: chip Edit → chip Exclude → next chip.
- After excluding, focus moves to the **next active chip's Edit** button. After re-including, focus moves to the **re-included chip's Edit** button.
- Edit input is autofocused on open.

---

## State coverage matrix

| Region | Empty | Loading (mid-save) | Success | Error |
|---|---|---|---|---|
| Summary | A.5 (Add summary affordance) | A.3 (Save disabled, "Saving…") | A.4 (Saved indicator 2s) | A.6 (toast + editor stays open) |
| Skills (per-item) | B.6 (no skills / all excluded message) | B.4 (transient gray-out) | B.4 (toast "Saved") | B.5 (toast + revert) |

---

## Concrete copy

| Element | Text |
|---|---|
| Summary edit button | `Edit` |
| Summary save | `Save` / `Saving…` |
| Summary cancel | `Cancel` |
| Summary saved badge | `Saved` |
| Summary empty CTA | `Add summary` |
| Summary error toast | `Could not save summary. Try again.` |
| Skill exclude aria-label | `Exclude skill {name}` |
| Skill include aria-label | `Re-include skill {name}` |
| Skill rename aria-label | `Rename skill {name}` |
| Available header | `Available skills` |
| All-excluded notice | `All skills excluded — re-include one below, or use the section toggle.` |
| Skills error toast | `Could not save skills. Try again.` |

Translations: today only the section labels are localised (`sectionTranslations` at `ResumeView.svelte:18-49`). New copy above is English-only for this iteration; localisation can follow in a separate feature. Add an entry in `sectionTranslations` for `availableSkills` so the structure exists for future translation, but don't translate the rest yet.

---

## Out of scope for UX

- No keyboard shortcut for "add skill" (creating new skills is out of scope — the LLM list is the universe).
- No drag-reorder of skills.
- No undo/redo stack (rely on Cancel during edit; persisted edits stand).
- No batch rename or batch exclude UI (the existing section-wide toggle covers batch exclude).
- No mobile-specific layout — assume desktop-class viewport (existing app constraint).
