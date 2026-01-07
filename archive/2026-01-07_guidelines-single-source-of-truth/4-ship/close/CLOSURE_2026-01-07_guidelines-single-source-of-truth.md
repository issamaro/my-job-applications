# Closure: Guidelines Single Source of Truth

**Date:** 2026-01-07
**Status:** COMPLETE

---

## Summary

Updated v4-* skills to use modern uv commands only (`uv sync`, `uv tree`). Removed all deprecated `uv pip` commands. Deleted 18 legacy v3-* skill files. Added documentation hierarchy to project readme.

---

## Deliverables

- [x] v4-* skills updated with modern uv commands
- [x] v3-* skills deleted (18 files)
- [x] Documentation updated with v4 references
- [x] Documentation hierarchy added
- [x] Tests verified (no regressions)
- [x] Inspection passed
- [x] Refined spec moved to `backlog/done/`
- [x] Workbench archived
- [x] Git commit created

---

## Requirements Completed

### Must Have (13/13)

| # | Requirement | Status |
|---|-------------|--------|
| 1 | v4-implement.md: `uv pip install` → `uv sync` | Done |
| 2 | v4-implement.md: `uv pip show` → `uv tree` | Done |
| 3 | v4-test.md: `uv pip show` → `uv tree` | Done |
| 4 | v4-validate.md: `uv pip show` → `uv tree` | Done |
| 5 | v4-scaffold.md: `uv pip install` → `uv sync` | Done |
| 6 | v4-research.md: `uv pip install` → `uv sync` | Done |
| 7 | v4-ecosystem.md: Ask user if pyproject.toml missing | Done |
| 8 | Add documentation hierarchy to `.claude/readme.md` | Done |
| 9 | Reference PROJECT_CHECKS.md as authoritative | Done |
| 10 | Delete 18 v3-* skill files | Done |
| 11 | Remove v3 refs from RETROSPECTIVE_INSIGHTS.md | Done |
| 12 | Remove v3 refs from problem-statement.md | Done |
| 13 | Verify ZERO `uv pip` commands remain | Done |

### Should Have (1/1)

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Remove duplicated setup instructions | Done |

---

## Commit Reference

**Hash:** (to be added after commit)
**Message:** docs: Update v4 skills to modern uv commands, remove v3 skills

---

## Archive Location

`archive/2026-01-07_guidelines-single-source-of-truth/`

---

*Feature Complete*
