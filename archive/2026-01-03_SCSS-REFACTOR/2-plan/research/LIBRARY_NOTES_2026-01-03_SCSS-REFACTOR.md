# Library Notes: SCSS Architecture Refactor

**Date:** 2026-01-03
**Purpose:** Ecosystem prerequisites and syntax reference for implementation

---

## 0. Ecosystem Prerequisites

### Runtime (from context7 lookups)
| Runtime | Version | Reason |
|---------|---------|--------|
| Node.js | >=20.0.0 <21.0.0 | Already pinned in package.json engines |

### Tooling
| Tool | Purpose | Verify |
|------|---------|--------|
| npm | Package management | `npm --version` |
| sass | SCSS compilation | `npx sass --version` |

### Setup Commands
```bash
npm install          # Install dependencies (sass ^1.80.0 already in devDependencies)
npm run build:css    # Compile SCSS to CSS
npm run watch:css    # Watch mode for development
```

---

## Sass (Dart Sass)

**Version Constraint:** `sass>=1.80.0` (already in package.json as `"sass": "^1.80.0"`)

### Module System Overview

Dart Sass uses a module system with `@use` and `@forward` rules. However, for this refactor we will use `@use` for loading partials since:
1. The existing codebase uses simple variable/mixin patterns
2. No need for complex forwarding or namespacing
3. Keeps the migration simple and reversible

### Correct Patterns

#### Loading Partials with @use
```scss
// main.scss (entry point)
@use "tokens";           // Loads _tokens.scss, namespace: tokens
@use "reset";            // Loads _reset.scss, namespace: reset
@use "layout";           // Loads _layout.scss, namespace: layout
```

#### Loading Partials Without Namespace (Recommended for this refactor)
```scss
// main.scss - use "as *" for direct variable access
@use "tokens" as *;      // Variables available without prefix
@use "reset";            // Just outputs CSS, no namespace needed
@use "layout";           // Just outputs CSS, no namespace needed
```

#### Index Files for Directories
```scss
// components/_index.scss
@forward "buttons";      // Exposes _buttons.scss
@forward "forms";        // Exposes _forms.scss
@forward "dialogs";      // Exposes _dialogs.scss

// main.scss
@use "components";       // Loads components/_index.scss
```

#### Partial File Naming
- Partials start with underscore: `_tokens.scss`
- Reference without underscore: `@use "tokens"`
- Extension optional: `@use "tokens"` or `@use "tokens.scss"`

### Deprecated (Avoid)

| Deprecated | Modern Alternative |
|------------|-------------------|
| `@import "file"` | `@use "file"` or `@use "file" as *` |
| `@import "file.scss"` | `@use "file"` |
| Global variables across files | `@use "tokens" as *` in each file that needs them |

**Note:** `@import` is deprecated in Dart Sass and will be removed in Sass 3.0. However, for this refactor, since we're organizing existing code and not sharing variables across files, we can use the simpler approach:

### Recommended Approach for This Refactor

Since the current architecture has all styles in one file and component partials will just contain CSS rules (not shared variables/mixins), we can use `@use` with `as *` for tokens and simple `@use` for CSS-only partials:

```scss
// main.scss (entry point)
@use "tokens" as *;        // Variables available globally in this file
@use "reset";              // CSS output only
@use "layout";             // CSS output only
@use "utilities";          // CSS output only
@use "components";         // Loads components/_index.scss
@use "views";              // Loads views/_index.scss
```

```scss
// _tokens.scss (variables only - no CSS output)
$color-primary: #0066cc;
$color-text: #1a1a1a;
// ... more variables
```

```scss
// components/_buttons.scss (needs tokens)
@use "../tokens" as *;     // Access token variables

.btn {
  color: $color-primary;
  // ... styles
}
```

### Code Examples

#### Entry Point Pattern
```scss
// main.scss
@use "tokens" as *;
@use "reset";
@use "layout";
@use "utilities";
@use "components";
@use "views";
```

#### Component Partial Pattern
```scss
// components/_buttons.scss
@use "../tokens" as *;

.btn {
  display: inline-block;
  padding: $spacing-field $spacing-grid;
  font-family: $font-stack;
  font-size: $font-size-body;
  color: $color-text;
  border: 1px solid $color-border;
  cursor: pointer;

  &:hover {
    background: $color-primary;
    color: $color-background;
  }
}

.btn-primary {
  background: $color-primary;
  color: $color-background;
  border-color: $color-primary;
}
```

#### Index File Pattern
```scss
// components/_index.scss
@forward "buttons";
@forward "forms";
@forward "sections";
@forward "dialogs";
@forward "tabs";
@forward "tags";
@forward "lists";
```

### CLI Commands

Build:
```bash
sass src/styles/main.scss:public/build/global.css --style=compressed
```

Watch:
```bash
sass src/styles/main.scss:public/build/global.css --watch
```

---

## Dependencies Summary

**No changes needed to package.json.** Current dependencies are sufficient:

```json
{
  "devDependencies": {
    "sass": "^1.80.0"
  }
}
```

The existing npm scripts will work unchanged:
- `npm run build:css` - Compiles all partials via main.scss entry point
- `npm run watch:css` - Watches all partials for changes

---

## Key Implementation Notes

1. **Import Order Matters:** Tokens must be loaded first, then reset, then layout, then components/views
2. **Each partial that uses variables must `@use "../tokens" as *`** at the top
3. **Underscore prefix:** All partials use underscore prefix (`_tokens.scss`)
4. **Reference without underscore:** `@use "tokens"` (not `@use "_tokens"`)
5. **No CSS output from tokens:** `_tokens.scss` should only contain variables, no CSS rules
6. **@forward in index files:** Use `@forward` to re-export from directories

---

*Reference for /v3-design and /v3-checklist*
