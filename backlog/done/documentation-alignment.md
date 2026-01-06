# Documentation Alignment - SCOPED_FEATURE

**Size:** S
**Scoped:** 2026-01-06
**Completed:** 2026-01-06
**Files affected:** ~2
**Dependencies:** project-tooling-standardization (for consistent paths)
**Ready for:** /v4-feature
**Epic:** Environment & Dependency Management Overhaul

---

## Description

Fix documentation that references incorrect paths and outdated setup procedures. `PROJECT_CHECKS.md` consistently references `venv/` but the actual virtual environment is `.venv/`. This causes confusion and failed commands when following the documentation.

## Context (Current State)

`PROJECT_CHECKS.md` references `venv/` in:
- Line 12: `source venv/bin/activate`
- Line 28-29: `test -d venv`
- Line 48: `source venv/bin/activate`
- Lines 123, 215: `source venv/bin/activate`

**Actual state:**
- Virtual environment is at `.venv/`
- `dev.sh` correctly uses `.venv/`
- `.gitignore` correctly ignores `.venv/`

## Scope (IN)

- Update all `venv/` references in `PROJECT_CHECKS.md` to `.venv/`
- Verify `dev.sh` comments match actual behavior
- Add "Environment Setup" section documenting:
  - Expected Python version (from `.python-version`)
  - Expected Node version (from `.nvmrc`)
  - How to create virtual environment
  - How to verify setup is correct

## Out of Scope (NOT)

- Creating a separate README.md file
- Documenting slash command usage
- Creating automated setup scripts
- CI/CD configuration

## Success Criteria

- [x] All `venv/` references in `PROJECT_CHECKS.md` changed to `.venv/`
- [x] Quick Validation command (line 12) works when copy-pasted
- [x] Environment Setup section exists documenting expected versions
- [x] No references to `venv/` remain in project documentation

## Notes

- `PROJECT_CHECKS.md` is the primary developer reference for this project
- Commands should be copy-paste ready - tested before documenting
- Keep documentation minimal but accurate

## Completion Notes

- Also updated `dev.sh` to use `uv sync` instead of `pip install`
- Partial orchestration: Analysis phase only, direct implementation for Size S feature
- Archive: `archive/2026-01-06_documentation-alignment/`
