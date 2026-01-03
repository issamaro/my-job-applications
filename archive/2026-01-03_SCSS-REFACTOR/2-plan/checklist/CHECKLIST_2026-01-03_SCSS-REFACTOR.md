# Checklist: SCSS Architecture Refactor

**Date:** 2026-01-03
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

From LIBRARY_NOTES Section 0:

| Requirement | Version | Verify Command | Status |
|-------------|---------|----------------|--------|
| Node.js | >=20.0.0 <21.0.0 | `node --version` | [ ] |
| npm | any | `npm --version` | [ ] |
| sass | >=1.80.0 | `npx sass --version` | [ ] |

- [ ] Dependencies installed (`npm install`)
- [ ] Build script works (`npm run build:css`)

**STOP if ecosystem is not ready.**

---

## 1. Dependencies (CRITICAL)

From LIBRARY_NOTES - no changes required:

| Library | Constraint | Manifest | Status |
|---------|-----------|----------|--------|
| sass | `^1.80.0` | package.json | [ ] Already present |

**No dependency changes needed for this refactor.**

---

## 2. Syntax Points

From LIBRARY_NOTES - use modern Sass module system:

### Module Loading
- [ ] `@use` directive used (not `@import`) → all partials
- [ ] `@use "tokens" as *` for token access → all partials except `_tokens.scss`
- [ ] `@forward` used in index files → `components/_index.scss`, `views/_index.scss`

### Partial Naming
- [ ] All partials use underscore prefix → `_tokens.scss`, `_reset.scss`, etc.
- [ ] References omit underscore → `@use "tokens"` not `@use "_tokens"`

### File Structure
- [ ] Entry point is import-only → `main.scss` has no CSS rules, only `@use` statements

---

## 3. File Creation Points

From IMPL_PLAN - all partials created:

### Foundation Partials
- [ ] `src/styles/_tokens.scss` created (lines 1-17)
- [ ] `src/styles/_reset.scss` created (lines 19-45)
- [ ] `src/styles/_layout.scss` created (lines 47-64)
- [ ] `src/styles/_utilities.scss` created (lines 237-271)

### Component Partials
- [ ] `src/styles/components/` directory created
- [ ] `src/styles/components/_buttons.scss` created (lines 105-138)
- [ ] `src/styles/components/_forms.scss` created (lines 140-234, 394-414)
- [ ] `src/styles/components/_sections.scss` created (lines 65-103)
- [ ] `src/styles/components/_dialogs.scss` created (lines 364-392)
- [ ] `src/styles/components/_tabs.scss` created (lines 416-445)
- [ ] `src/styles/components/_tags.scss` created (lines 327-362)
- [ ] `src/styles/components/_lists.scss` created (lines 273-325)
- [ ] `src/styles/components/_index.scss` created (forwards all components)

### View Partials
- [ ] `src/styles/views/` directory created
- [ ] `src/styles/views/_resume-generator.scss` created (lines 447-527)
- [ ] `src/styles/views/_requirements-analysis.scss` created (lines 529-630)
- [ ] `src/styles/views/_resume-preview.scss` created (lines 632-892)
- [ ] `src/styles/views/_history.scss` created (lines 894-979)
- [ ] `src/styles/views/_view-controls.scss` created (lines 981-1047)
- [ ] `src/styles/views/_index.scss` created (forwards all views)

### Entry Point
- [ ] `src/styles/main.scss` updated to imports-only

---

## 4. Build Verification Points

From FEATURE_SPEC BDD scenarios:

### Build Process
- [ ] `npm run build:css` completes without errors
- [ ] `public/build/global.css` is generated
- [ ] Output CSS is non-empty

### Watch Process
- [ ] `npm run watch:css` starts successfully
- [ ] Modifying a partial triggers recompilation (test with `_tokens.scss`)

### Visual Regression
- [ ] App loads in browser
- [ ] No visual differences from before refactor
- [ ] All pages render correctly (Profile, Generator, Preview)

---

## 5. UX Points

From FEATURE_SPEC - no UX changes (pure refactor):

- [ ] **No visual changes** - App appearance identical before/after
- [ ] **No functional changes** - All interactions work identically

---

## 6. Test Points

From FEATURE_SPEC scenarios - manual verification:

### Scenario: Build process compiles all partials
- [ ] All 16 partials are imported via index files
- [ ] Single `global.css` output produced
- [ ] No SCSS compilation errors

### Scenario: Design tokens are centralized
- [ ] All color variables in `_tokens.scss`
- [ ] All typography variables in `_tokens.scss`
- [ ] All spacing variables in `_tokens.scss`
- [ ] Partials use tokens via `@use "../tokens" as *`

### Scenario: Component styles are isolated
- [ ] Button styles only in `_buttons.scss`
- [ ] Form styles only in `_forms.scss`
- [ ] No style duplication across partials

### Scenario: Developer finds styles quickly
- [ ] File names match component/view names
- [ ] Clear separation: components vs views

### Scenario: Watch mode works with partials
- [ ] Modifying `_tokens.scss` triggers rebuild
- [ ] Modifying any component partial triggers rebuild
- [ ] Modifying any view partial triggers rebuild

---

## 7. Import Order Verification

From LIBRARY_NOTES - cascade order matters:

- [ ] `main.scss` imports in this order:
  1. `@use "tokens" as *`
  2. `@use "reset"`
  3. `@use "layout"`
  4. `@use "utilities"`
  5. `@use "components"`
  6. `@use "views"`

---

## 8. Code Quality Points

From FEATURE_SPEC Should Have (MANDATORY):

### File Header Comments
- [ ] `_tokens.scss` has header comment describing purpose
- [ ] `_reset.scss` has header comment describing purpose
- [ ] `_layout.scss` has header comment describing purpose
- [ ] `_utilities.scss` has header comment describing purpose
- [ ] `components/_buttons.scss` has header comment
- [ ] `components/_forms.scss` has header comment
- [ ] `components/_sections.scss` has header comment
- [ ] `components/_dialogs.scss` has header comment
- [ ] `components/_tabs.scss` has header comment
- [ ] `components/_tags.scss` has header comment
- [ ] `components/_lists.scss` has header comment
- [ ] `components/_index.scss` has header comment
- [ ] `views/_resume-generator.scss` has header comment
- [ ] `views/_requirements-analysis.scss` has header comment
- [ ] `views/_resume-preview.scss` has header comment
- [ ] `views/_history.scss` has header comment
- [ ] `views/_view-controls.scss` has header comment
- [ ] `views/_index.scss` has header comment

### Token Organization
- [ ] `_tokens.scss` has `// Colors` section comment
- [ ] `_tokens.scss` has `// Typography` section comment
- [ ] `_tokens.scss` has `// Spacing` section comment

---

## Verification at Closure

Each item above will be checked with file:line reference at `/v3-close`.

**Mandatory for completion:**
- All Section 0-4 items must be checked
- Section 5-6 scenarios must pass
- Section 7 import order must be correct
- Section 8 code quality items must be present

---

*Contract for /v3-implement*
