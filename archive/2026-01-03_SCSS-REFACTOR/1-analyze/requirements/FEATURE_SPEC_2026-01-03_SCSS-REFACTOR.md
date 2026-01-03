# Feature Spec: SCSS Architecture Refactor

**Date:** 2026-01-03
**Status:** Draft

---

## 1. Problem Statement

### User Request
> Sass: refactor/improve strategy

### Pain Point
The current `main.scss` (1,047 lines) is a monolithic file containing:
- Design variables mixed with component styles
- No clear separation of concerns
- Difficult to maintain as the app grows
- Hard to find specific styles
- No component-level organization
- Potential for naming conflicts

### User Persona
- **Developer:** Needs maintainable, organized styles for faster development
- **Future contributors:** Need clear structure to understand and extend

---

## 2. Current State Analysis

### File Structure
```
src/styles/
└── main.scss (1,047 lines - everything in one file)
```

### Content Categories Identified
| Category | Lines | Description |
|----------|-------|-------------|
| Variables | 1-17 | Colors, typography, spacing |
| Reset/Base | 19-45 | Box-sizing, body, headings, paragraphs |
| Layout | 47-103 | Container, header, sections |
| Buttons | 105-138 | btn, btn-primary, btn-add |
| Forms | 140-234 | Inputs, labels, validation, errors |
| States | 237-271 | Saved indicator, empty, skeleton |
| Lists | 273-325 | Item lists and items |
| Tags | 328-362 | Tag components |
| Dialogs | 364-392 | Modal dialogs |
| Tabs | 416-445 | Tab navigation |
| Resume Generator | 447-527 | JD input, progress bar |
| Requirements | 529-630 | Requirements analysis cards |
| Resume Preview | 632-892 | Resume display and editing |
| History | 894-979 | Resume history list |
| View Controls | 981-1047 | View mode toggles |

---

## 3. BDD Scenarios

```gherkin
Feature: SCSS Architecture Refactor
  As a developer
  I want a modular SCSS architecture
  So that I can maintain and extend styles efficiently

Scenario: Build process compiles all partials
  Given the SCSS is split into multiple partial files
  When I run `npm run build:css`
  Then all partials are compiled into a single `global.css`
  And the output is identical in functionality to before

Scenario: Design tokens are centralized
  Given I need to change the primary color
  When I update the `$color-primary` variable in `_tokens.scss`
  Then all components using that token reflect the change

Scenario: Component styles are isolated
  Given I need to modify button styles
  When I open `components/_buttons.scss`
  Then I find all button-related styles in one place
  And no unrelated styles are in the file

Scenario: Developer finds styles quickly
  Given I need to style a new resume section component
  When I look for existing resume styles
  Then I find them in `components/_resume-preview.scss`
  And the naming convention is consistent

Scenario: Watch mode works with partials
  Given I am developing with `npm run watch:css`
  When I modify any partial file
  Then the CSS recompiles automatically
  And changes appear in the browser
```

---

## 4. Requirements

### Must Have (MVP)
- [ ] Extract design tokens into `_tokens.scss` (colors, typography, spacing)
- [ ] Create `_reset.scss` for CSS reset and base styles
- [ ] Create `_layout.scss` for container, header, structural styles
- [ ] Create `_utilities.scss` for animations, states, helpers
- [ ] Create component partials (reusable UI primitives):
  - [ ] `components/_buttons.scss`
  - [ ] `components/_forms.scss`
  - [ ] `components/_sections.scss`
  - [ ] `components/_dialogs.scss`
  - [ ] `components/_tabs.scss`
  - [ ] `components/_tags.scss`
  - [ ] `components/_lists.scss`
  - [ ] `components/_index.scss` (imports all components)
- [ ] Create view partials (composed layouts/screens):
  - [ ] `views/_resume-generator.scss`
  - [ ] `views/_resume-preview.scss`
  - [ ] `views/_requirements-analysis.scss`
  - [ ] `views/_history.scss`
  - [ ] `views/_index.scss` (imports all views)
- [ ] Create `main.scss` as import-only entry point
- [ ] Verify build process works (`npm run build:css`)
- [ ] Verify watch process works (`npm run watch:css`)
- [ ] Visual regression: app looks identical before/after

### Should Have (Enhancement)
- [ ] Add file header comments with purpose description
- [ ] Group related variables with comments in tokens
- [ ] Consistent naming convention documentation
- [ ] Index file for components directory

### Won't Have (Out of Scope)
- Component-scoped CSS (CSS modules, Svelte scoped styles)
- CSS-in-JS migration
- Theming system (dark mode)
- CSS custom properties migration
- New visual styles or redesign
- Build tool changes beyond SCSS imports

---

## 5. Proposed File Structure

```
src/styles/
├── main.scss              # Entry point (imports only)
├── _tokens.scss           # Design tokens (variables)
├── _reset.scss            # CSS reset and base styles
├── _layout.scss           # Container, header, structural
├── _utilities.scss        # Animations, states, helpers
├── components/            # Reusable UI primitives
│   ├── _index.scss        # Component imports
│   ├── _buttons.scss      # Button styles
│   ├── _forms.scss        # Form inputs, labels, validation
│   ├── _sections.scss     # Collapsible sections
│   ├── _dialogs.scss      # Modal dialogs
│   ├── _tabs.scss         # Tab navigation
│   ├── _tags.scss         # Tag/skill components
│   └── _lists.scss        # Item lists
└── views/                 # Composed layouts/screens
    ├── _index.scss        # View imports
    ├── _resume-generator.scss    # JD input, progress
    ├── _resume-preview.scss      # Resume display
    ├── _requirements-analysis.scss # Requirements cards
    └── _history.scss      # Resume history
```

### Architecture Rationale

| Directory | Purpose | Example |
|-----------|---------|---------|
| `components/` | Reusable UI primitives | Buttons, forms, dialogs |
| `views/` | Composed layouts using primitives | Resume preview, history list |

This separation scales as new features are added (e.g., Hiring Projects views).

---

## 6. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| SCSS compilation continues via npm scripts | Build | No change to build tooling |
| No component-scoped CSS needed now | Architecture | Global styles remain |
| Underscore prefix for partials is standard | Convention | `_partial.scss` pattern |
| Import order matters for cascade | Architecture | Tokens → Reset → Components |
| No visual changes expected | Testing | Pure refactor, identical output |

---

## 7. Acceptance Criteria Checklist

- [ ] All styles extracted from monolithic file into partials
- [ ] `npm run build:css` produces working `global.css`
- [ ] `npm run watch:css` recompiles on partial changes
- [ ] App appearance is visually identical (no regressions)
- [ ] Each partial has single responsibility
- [ ] Tokens file contains all design variables
- [ ] Developer can find component styles by component name

---

## 8. Open Questions

None - this is a straightforward refactor with clear boundaries.

---

*Next: /v3-verify-analysis (no UI changes, skip /v3-ux)*
