# Note: SASS Structure Oversight in Initial Implementation

**Date:** 2026-01-05
**Category:** LEARNING
**During:** /v4-implement

---

## What Happened

Initially implemented the `ImportModal.svelte` component with inline `<style>` blocks instead of using the project's established SASS architecture in `src/styles/`.

## Context

- **File(s):** `src/components/ImportModal.svelte`, `src/components/ProfileEditor.svelte`
- **Expected:** Use existing SASS structure with design tokens
- **Actual:** Created inline styles duplicating token values (colors, spacing)

### Project SASS Structure
```
src/styles/
├── _tokens.scss          # Design tokens ($color-primary, $spacing-grid, etc.)
├── _reset.scss
├── _layout.scss
├── _utilities.scss
├── components/
│   ├── _index.scss       # Forwards all component partials
│   ├── _buttons.scss
│   ├── _dialogs.scss
│   └── ...
├── views/
│   └── ...
└── main.scss             # Entry point
```

---

## Resolution

Refactored to follow project conventions:

1. Created `src/styles/components/_import-modal.scss` using design tokens
2. Added `@forward "import-modal"` to `_index.scss`
3. Removed inline `<style>` blocks from Svelte components

### Correct Pattern
```scss
// components/_import-modal.scss
@use "../tokens" as *;

.import-modal {
  max-width: 480px;
  width: 90%;
}

.drop-zone {
  border: 2px dashed $color-border;  // Use token, not hardcoded #e0e0e0
  // ...
}
```

---

## Impact

- **Immediate:** Fixed - styles now use SASS architecture
- **Future:** No - lesson learned
- **Checklist:** Yes - consider adding to project-checks.md

### Suggested Project Check
```markdown
## Frontend Styles
- [ ] New component styles added to `src/styles/components/`
- [ ] Styles use design tokens from `_tokens.scss`
- [ ] No inline `<style>` blocks with hardcoded values
- [ ] Component partial forwarded in `_index.scss`
```

---

*Captured during Import JSON Profile implementation*
