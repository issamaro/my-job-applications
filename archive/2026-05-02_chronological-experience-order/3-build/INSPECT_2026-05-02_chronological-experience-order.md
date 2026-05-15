---
feature: chronological-experience-order
date: 2026-05-02
status: READY
playwright: skipped
ceremony_level: M
dev_server_url: http://127.0.0.1:8000
---

# Inspection — Chronological Experience Order

## Playwright

skipped — no `playwright.config.*` found at project root. Per agent contract, automated smoke is skipped when Playwright is not already present.

## Manual checklist

The user should open the dev server at `http://127.0.0.1:8000`, navigate to a previously-generated resume in the Resume Editor, and verify each bullet below. Each bullet is a verb-led action that takes under 30s.

- Open the Resume Editor for a resume with at least 3 work experiences. Confirm each work item shows a `⋮⋮` drag handle on its left and the `1.` / `2.` / `3.` numbering still renders next to the title.
- Hover the `⋮⋮` handle on any work item. Confirm the cursor changes to `grab` (open hand). Press and hold — confirm cursor changes to `grabbing` (closed hand).
- Drag the third work item up above the first. Confirm the array reorders live as you drag (items shift visually under the cursor) and the leading numbers `1.`, `2.`, `3.` update in real time to match the new positions.
- While dragging, look at the item being moved. Confirm it shows the mid-drag style: `opacity: 0.5` (visibly faded) and `background: #f0f0f0` (light gray).
- Release the mouse to drop. Confirm the existing `Saved` indicator / toast appears (reusing `ResumeView.svelte`'s existing save-confirmation pattern) and no error toast shows.
- Reload the page (Cmd+R). Confirm the work-experience list keeps the new order — the drop persisted across reload.
- Click `Edit` on one work item to enter inline-edit mode. Try to drag that item by its handle. Confirm it does NOT drag (the `draggable` attribute is off while `editingId === exp.id`). Confirm other (non-editing) items in the list ARE still draggable.
- Cancel the edit, then drag-drop reorder again. Confirm reorder works again once edit mode exits.
- Trigger a save failure: open DevTools → Network → enable "Offline", then drag-drop one item. Confirm an error toast appears ("Could not save order." or equivalent) AND the visible order reverts to the pre-drag order (re-cloned from `resume.resume`).
- Re-enable network. Open DevTools → Accessibility tree (or use VoiceOver: Cmd+F5). Focus or inspect the `⋮⋮` handle. Confirm its accessible name is announced as "Drag to reorder" (from `aria-label`).
- Press `Tab` repeatedly through a work item. Confirm focus reaches the `Edit` button as before, and confirm the drag handle is NOT a tab stop (it's a `<span>` with no `tabindex` — the keyboard focus flow must be unchanged from baseline).
- Open a resume with an empty `work_experiences` array (or a freshly-generated one with no included items). Confirm zero drag handles render and the empty `<div class="work-list">` layout is unchanged.
- Generate a new resume from a JD. Confirm the work experiences arrive pre-sorted reverse-chronologically (newest `start_date` first) without any user reorder action — this verifies the server-side sort is taking effect end-to-end.

## Decisions

none — parent collects user verdict
