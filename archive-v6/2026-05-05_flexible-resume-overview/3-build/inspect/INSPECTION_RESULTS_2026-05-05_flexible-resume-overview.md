feature: flexible-resume-overview
date: 2026-05-05
status: READY
playwright: skipped

---

## Playwright

skipped — no playwright.config.* found in project root and dev server not started.

---

## Manual checklist

Covers BDD scenarios S1–S12 and all UI states from UX_DESIGN regions A and B.

### Region A — Summary inline edit

- Open a resume's Edit tab that has a non-empty summary. Confirm the summary text is visible as a paragraph and an `[Edit]` button appears below it (right-aligned).
- Click `[Edit]`. Confirm a textarea with 4 rows opens pre-filled with the current summary text, alongside `[Save]` and `[Cancel]` buttons. Confirm the textarea receives focus automatically.
- With the textarea open, press `Esc`. Confirm the textarea closes and the original summary text re-appears unchanged.
- With the textarea open, edit the text, then press `Cmd+Enter` (or `Ctrl+Enter` on Windows). Confirm a "Saving…" disabled button appears briefly, then a green "Saved" badge appears for ~2 seconds, then the updated summary text is shown in display state with `[Edit]` restored.
- With the textarea open, click `[Save]`. Confirm `[Save]` and `[Cancel]` both disable while the PUT is in flight, then the display state returns with updated text and a 2-second "Saved" badge.
- Clear the summary textarea to empty and save. Confirm the summary paragraph disappears and an `[Add summary]` button appears in its place. Click `[Add summary]` and confirm an empty textarea opens ready for input.
- Simulate an API failure (e.g., disable the network or stop the backend). Edit the summary and click `[Save]`. Confirm a red toast "Could not save summary. Try again." appears for ~3 seconds, and the editor stays open so you can retry.

### Region B — Skills curation

- Open a resume with multiple skills, all included. Confirm each chip shows the skill name, a `✎` (rename) button, and a `×` (exclude) button. Confirm matched skills also show a `✓` indicator. Confirm no "Available skills" header is visible.
- Click `×` on one skill chip. Confirm the chip disappears from the active group, an "Available skills" header appears, and the excluded skill appears below with only a `+` button (dimmed at ~50% opacity). Confirm a "Saved" toast fires. Confirm the active chips retain their original relative order.
- Click `+` on an excluded skill. Confirm it moves back into the active group at its original position, the "Available skills" header disappears if no others remain excluded, and a "Saved" toast fires.
- Click `✎` on a skill chip. Confirm the chip swaps to a text input pre-filled with the skill name, plus `[✓]` and `[×]` icon buttons. Confirm the input is auto-focused. Edit the name and press `Enter`. Confirm the chip returns to display state with the new name, and a "Saved" toast fires.
- With a rename input open, press `Esc`. Confirm the input closes and the original skill name is restored without saving.
- Exclude every skill one by one (or use the section toggle twice if needed). Confirm the active area shows the message "All skills excluded — re-include one below, or use the section toggle." Confirm the "Available skills" header and all chips still appear in the available group.
- With some skills excluded, click the "Toggle section" button. Confirm all skills are re-included (active group shows all chips, "Available skills" header gone). Click "Toggle section" again. Confirm all skills are excluded (all chips move to available group).
- Simulate an API failure, then click `×` on a skill. Confirm a red toast "Could not save skills. Try again." appears, and the chip reverts to its pre-click state (optimistic update rolled back).
- Open browser DevTools, inspect a skill chip's exclude button. Confirm its `aria-label` is `Exclude skill {name}`. Inspect the rename button: `aria-label="Rename skill {name}"`. Inspect the re-include button: `aria-label="Re-include skill {name}"`.
- Tab through the skills section without a mouse. Confirm each `✎` and `×` button is reachable via keyboard and activatable with `Enter`.

---

## Decisions

none — parent collects user verdict
