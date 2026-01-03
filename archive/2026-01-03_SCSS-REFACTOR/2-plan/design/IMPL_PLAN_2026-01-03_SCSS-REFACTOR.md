# Implementation Plan: SCSS Architecture Refactor

**Date:** 2026-01-03
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-03_SCSS-REFACTOR.md

---

## 1. Affected Files

### Config/Dependencies
| File | Change | Description |
|------|--------|-------------|
| package.json | No change | `sass>=1.80.0` already present |

### Frontend - New SCSS Partials

| File | Change | Source Lines | Description |
|------|--------|--------------|-------------|
| `src/styles/_tokens.scss` | Create | 1-17 | Design tokens (colors, typography, spacing) |
| `src/styles/_reset.scss` | Create | 19-45 | Box-sizing, body, typography base |
| `src/styles/_layout.scss` | Create | 47-103 | Container, header, sections |
| `src/styles/_utilities.scss` | Create | 237-271 | Saved indicator, empty state, skeleton, animations |
| `src/styles/components/_buttons.scss` | Create | 105-138 | btn, btn-primary, btn-add |
| `src/styles/components/_forms.scss` | Create | 140-234, 394-414 | Inputs, labels, validation, checkbox, required |
| `src/styles/components/_sections.scss` | Create | 65-103 | Collapsible section component |
| `src/styles/components/_dialogs.scss` | Create | 364-392 | Modal dialogs |
| `src/styles/components/_tabs.scss` | Create | 416-445 | Tab navigation |
| `src/styles/components/_tags.scss` | Create | 327-362 | Tags and tag-remove |
| `src/styles/components/_lists.scss` | Create | 273-325 | Item list and item styles |
| `src/styles/components/_index.scss` | Create | - | Forward all components |
| `src/styles/views/_resume-generator.scss` | Create | 447-527 | JD input, progress bar |
| `src/styles/views/_requirements-analysis.scss` | Create | 529-630 | Requirements cards |
| `src/styles/views/_resume-preview.scss` | Create | 632-892 | Resume display, editing |
| `src/styles/views/_history.scss` | Create | 894-979 | Resume history list |
| `src/styles/views/_view-controls.scss` | Create | 981-1047 | View mode toggle, profile incomplete |
| `src/styles/views/_index.scss` | Create | - | Forward all views |
| `src/styles/main.scss` | Modify | - | Imports only (replace 1047 lines) |

### Directories to Create
| Path | Description |
|------|-------------|
| `src/styles/components/` | Reusable UI primitives |
| `src/styles/views/` | Composed layouts/screens |

---

## 2. Database Changes

```sql
-- None (pure CSS refactor)
```

---

## 3. Implementation Approach

### File Organization Strategy

The refactor extracts code from the monolithic `main.scss` (1,047 lines) into 16 focused partials organized by concern:

```
src/styles/
├── main.scss              # Entry point (~15 lines)
├── _tokens.scss           # Variables only (17 lines)
├── _reset.scss            # Base styles (27 lines)
├── _layout.scss           # Container/header (37 lines)
├── _utilities.scss        # States/animations (35 lines)
├── components/            # Reusable primitives
│   ├── _index.scss
│   ├── _buttons.scss      # 34 lines
│   ├── _forms.scss        # 95 lines + checkbox/required
│   ├── _sections.scss     # 39 lines
│   ├── _dialogs.scss      # 29 lines
│   ├── _tabs.scss         # 30 lines
│   ├── _tags.scss         # 36 lines
│   └── _lists.scss        # 53 lines
└── views/                 # Composed layouts
    ├── _index.scss
    ├── _resume-generator.scss    # 81 lines
    ├── _requirements-analysis.scss # 102 lines
    ├── _resume-preview.scss      # 261 lines
    ├── _history.scss             # 86 lines
    └── _view-controls.scss       # 67 lines
```

### Module Loading Pattern

Using Sass `@use` with `as *` to avoid namespace prefixes:

```scss
// _buttons.scss
@use "../tokens" as *;

.btn {
  padding: 8px $spacing-grid;
  // Uses $spacing-grid from tokens
}
```

### Index File Pattern

```scss
// components/_index.scss
@forward "buttons";
@forward "forms";
// etc.
```

### Entry Point Pattern

```scss
// main.scss
@use "tokens" as *;
@use "reset";
@use "layout";
@use "utilities";
@use "components";
@use "views";
```

### Error Handling

N/A - Pure CSS refactor, no runtime error handling needed.

---

## 4. Implementation Order

Dependencies flow: tokens → reset → layout → utilities → components → views → main

### Phase 1: Foundation (must be first)
1. [ ] Create `src/styles/components/` directory
2. [ ] Create `src/styles/views/` directory
3. [ ] Create `_tokens.scss` - Extract lines 1-17, group variables with section comments (Colors, Typography, Spacing)

### Phase 2: Base Styles (depends on tokens)
4. [ ] Create `_reset.scss` - Extract lines 19-45, add file header comment, add `@use "tokens" as *`
5. [ ] Create `_layout.scss` - Extract lines 47-64, add file header comment, add `@use "tokens" as *`

### Phase 3: Components (depends on tokens)
6. [ ] Create `components/_sections.scss` - Extract lines 65-103, add file header comment, add `@use "../tokens" as *`
7. [ ] Create `components/_buttons.scss` - Extract lines 105-138, add file header comment, add `@use "../tokens" as *`
8. [ ] Create `components/_forms.scss` - Extract lines 140-234 + 394-414, add file header comment, add `@use "../tokens" as *`
9. [ ] Create `components/_tags.scss` - Extract lines 327-362, add file header comment, add `@use "../tokens" as *`
10. [ ] Create `components/_dialogs.scss` - Extract lines 364-392, add file header comment, add `@use "../tokens" as *`
11. [ ] Create `components/_tabs.scss` - Extract lines 416-445, add file header comment, add `@use "../tokens" as *`
12. [ ] Create `components/_lists.scss` - Extract lines 273-325, add file header comment, add `@use "../tokens" as *`
13. [ ] Create `components/_index.scss` - Forward all component partials, add file header comment

### Phase 4: Utilities (depends on tokens)
14. [ ] Create `_utilities.scss` - Extract lines 237-271, add file header comment, add `@use "tokens" as *`

### Phase 5: Views (depends on tokens)
15. [ ] Create `views/_resume-generator.scss` - Extract lines 447-527, add file header comment, add `@use "../tokens" as *`
16. [ ] Create `views/_requirements-analysis.scss` - Extract lines 529-630, add file header comment, add `@use "../tokens" as *`
17. [ ] Create `views/_resume-preview.scss` - Extract lines 632-892, add file header comment, add `@use "../tokens" as *`
18. [ ] Create `views/_history.scss` - Extract lines 894-979, add file header comment, add `@use "../tokens" as *`
19. [ ] Create `views/_view-controls.scss` - Extract lines 981-1047, add file header comment, add `@use "../tokens" as *`
20. [ ] Create `views/_index.scss` - Forward all view partials, add file header comment

### Phase 6: Entry Point (final)
21. [ ] Replace `main.scss` content with imports only

### Phase 7: Verification
22. [ ] Run `npm run build:css` - Verify compilation succeeds
23. [ ] Compare output size - Should be similar to before
24. [ ] Visual check - App appearance identical

---

## 5. Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Import order causes cascade issues | Low | Med | Follow strict order: tokens → reset → layout → utilities → components → views |
| Missing variable in partial | Low | High | Each partial includes `@use "../tokens" as *` |
| Watch mode doesn't detect partial changes | Low | Med | Test with `npm run watch:css` before marking complete |
| Visual regression | Low | High | Side-by-side comparison before/after |

---

## 6. Line Extraction Map

Detailed mapping from `main.scss` to new partials:

| Lines | Current Content | Target Partial |
|-------|-----------------|----------------|
| 1-17 | Variables (colors, typography, spacing) | `_tokens.scss` |
| 19-45 | Reset (box-sizing, body, headings, p) | `_reset.scss` |
| 47-64 | Container, header, status | `_layout.scss` |
| 65-103 | Section, section-header, section-content | `components/_sections.scss` |
| 105-138 | btn, btn-primary, btn-add | `components/_buttons.scss` |
| 140-234 | Forms, inputs, validation | `components/_forms.scss` |
| 237-271 | Saved indicator, empty, skeleton | `_utilities.scss` |
| 273-325 | Item list, item styles | `components/_lists.scss` |
| 327-362 | Tags, tag-remove | `components/_tags.scss` |
| 364-392 | Dialog backdrop, dialog | `components/_dialogs.scss` |
| 394-414 | Checkbox, required indicator | `components/_forms.scss` (append) |
| 416-445 | Tab nav, tab-btn | `components/_tabs.scss` |
| 447-527 | Resume generator, JD input, progress | `views/_resume-generator.scss` |
| 529-630 | Requirements analysis cards | `views/_requirements-analysis.scss` |
| 632-892 | Resume preview, sections, editing | `views/_resume-preview.scss` |
| 894-979 | History section, list | `views/_history.scss` |
| 981-1047 | View mode, profile incomplete, download | `views/_view-controls.scss` |

---

*Next: /v3-checklist*
