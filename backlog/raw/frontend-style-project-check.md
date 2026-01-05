# Frontend Style Project Check

Source: import-json-profile retrospective
Date: 2026-01-05

During implementation, inline `<style>` blocks were initially used instead of the project's SASS architecture (`src/styles/`). This was caught during review and refactored.

Consider adding a project check to prevent this in future features.

Potential approaches:
- Add to project-checks.md or create one if it doesn't exist
- Document the SASS structure in a CONTRIBUTING.md or similar

Suggested checks:
- [ ] New component styles added to `src/styles/components/`
- [ ] Styles use design tokens from `_tokens.scss`
- [ ] No inline `<style>` blocks with hardcoded values
- [ ] Component partial forwarded in `_index.scss`
