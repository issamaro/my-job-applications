---
slug: chronological-experience-order
date: 2026-05-02
ceremony_level: M
phase: analyze
artifact: ux-design
---

# UX Design — Chronological Experience Order

Two surfaces are affected. **Server-side sort** has no UI footprint (the order arrives pre-sorted). The **drag-drop affordance** is the only visible UX change.

## Surface 1 — Resume Editor (Work Experience section)

Affected file: `src/components/ResumeView.svelte`, the `<ResumeSection title={labels.workExperience}>` block (around line 259-305).

### Current state (baseline)

Each work item is a `<div class="work-item">` showing:
- `1.` (work-number) + `Title · Company`
- date range
- description (with inline-edit textarea on Edit click)
- match-reasons + Edit button + saved indicator

There is no drag handle, no drag affordance, no reorder UI.

### Target state — list view (default)

Each work item gains a left-side drag handle, mirroring `Languages.svelte`. The numbering (`1.`, `2.`, ...) is preserved and reflects the current array index — so it updates as items are reordered.

```
┌────────────────────────────────────────────────────────┐
│ ⋮⋮  1. Senior Engineer · Acme Corp                     │
│     Jan 2024 – Present                                 │
│     Built distributed systems serving 10M users…       │
│     Match: Python, AWS                  [Edit]         │
├────────────────────────────────────────────────────────┤
│ ⋮⋮  2. Engineer · Beta Inc                             │
│     Jun 2021 – Dec 2023                                │
│     Owned the billing service…                         │
│     Match: SQL                          [Edit]         │
├────────────────────────────────────────────────────────┤
│ ⋮⋮  3. Junior Dev · Gamma LLC                          │
│     Mar 2019 – May 2021                                │
│     Frontend work on customer dashboard…               │
│                                         [Edit]         │
└────────────────────────────────────────────────────────┘
```

The `⋮⋮` handle uses `cursor: grab` and shows `cursor: grabbing` on `:active`. Hovering the row does **not** show the move cursor — only the handle does. This matches Languages.svelte exactly.

### State: mid-drag

The dragged item gets `opacity: 0.5; background: #f0f0f0` (matches Languages.svelte's `.item.dragging` style). As the user drags over another item, the array reorders live (the same pattern Languages.svelte uses in `handleDragOver`). The numbering updates in real time.

### State: drop / persisting

On drop, the front-end calls `updateResume(resume.id, resumeData)` with the new array order. While saving, the existing `saving` state and `Saved` indicator pattern from `ResumeView.svelte` is reused — the toast or saved indicator confirms.

### State: drop fails

If the API call fails, fall back to reload (same as `Languages.svelte` line 156-158) and show the existing error pattern. We rely on the existing `Toast` already wired into `ResumeView.svelte`.

### State: edit mode active on an item

When `editingId === exp.id`, the item shows the existing description textarea. The drag handle is still visible but the item is **not draggable while editing** (we set `draggable="true"` only when not in edit mode, mirroring how Languages.svelte handles its inline-edit state via `{#if editingId === item.id && showForm}`).

### State: only one work item

The drag handle still renders for visual consistency, but dragging is a no-op (drop on self). No special handling needed; this is how Languages.svelte behaves.

## Surface 2 — Generation flow (server-side sort)

No UI footprint. Existing UI:
- User pastes a JD → clicks Generate → spinner → resume appears.

The only observable change: work experiences arrive in reverse-chronological order. There is no toggle, no badge, no copy change.

## Empty / loading / error states

- **Loading (resume fetch in progress)**: existing `resumeData` null check already handles this. No change.
- **Empty work_experiences array**: existing layout (an empty `<div class="work-list">`) is unchanged. No drag handles render.
- **Generation error**: existing error path in `generate_resume` route is unchanged; no new error sources are introduced. The new `sorted()` call is on a list that's already validated by Pydantic.

## Accessibility notes

- The drag handle uses `aria-label="Drag to reorder"` (same as Languages.svelte line 246).
- Keyboard reorder is **out of scope** — Languages.svelte does not support it either. Adding keyboard reorder for both surfaces would be a separate accessibility-focused feature.
- Screen-reader users keep working from the existing list reading; the visual numbering (`1.`, `2.`) gives them index context.

## Keyboard nav map

- `Tab` reaches the drag handle (it's a `<span>`, so technically not focusable; matches Languages.svelte). Recommend NOT changing this in scope — if we make the handle focusable, we must implement keyboard reorder, which is a larger lift.
- `Tab` reaches the `Edit` button on each item (already true).
- The new drag-drop adds no new tab stops.

## Copy

No new strings. The handle is purely visual. The "Saved" / "Could not save" copy is reused from existing patterns in `ResumeView.svelte`.

## Design tokens / styles

Reuse the exact CSS from `Languages.svelte` lines 315-341:
- `.drag-handle-wrapper { display: flex; align-items: center; gap: 12px; }`
- `.drag-handle { cursor: grab; color: #999; font-size: 16px; user-select: none; }`
- `.drag-handle:active { cursor: grabbing; }`
- `.item.dragging { opacity: 0.5; background: #f0f0f0; }`

Adapt the selectors to `.work-item` so they don't collide with other item-classed elements on the page. Or scope via a parent class — implementer's choice during build phase.
