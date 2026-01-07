# Change Log: Guidelines Single Source of Truth

**Date:** 2026-01-07
**Feature Spec:** FEATURE_SPEC_2026-01-07_guidelines-single-source-of-truth.md
**Implementation Plan:** IMPL_PLAN_2026-01-07_guidelines-single-source-of-truth.md

---

## Files Modified

### Global Skills (~/.claude/commands/)

| File | Change | Description |
|------|--------|-------------|
| v4-implement.md | Lines 74, 81 | `uv pip install` → `uv sync`, `uv pip show` → `uv tree --package` |
| v4-test.md | Line 47 | `uv pip show` → `uv tree --package`, `requirements.txt` → `pyproject.toml` |
| v4-validate.md | Lines 40-41 | `uv pip show` → `uv tree --package` |
| v4-scaffold.md | Line 88 | `uv pip install` → `uv sync` |
| v4-research.md | Line 106 | `uv pip install` → `uv sync` |
| v4-ecosystem.md | New section | Added "Handling Missing pyproject.toml" section |

### Global Skills Deleted

| File | Action |
|------|--------|
| v3-analyze.md | Deleted |
| v3-build.md | Deleted |
| v3-checklist.md | Deleted |
| v3-close.md | Deleted |
| v3-design.md | Deleted |
| v3-feature.md | Deleted |
| v3-implement.md | Deleted |
| v3-inspect.md | Deleted |
| v3-plan.md | Deleted |
| v3-reflect.md | Deleted |
| v3-requirements.md | Deleted |
| v3-research.md | Deleted |
| v3-scope.md | Deleted |
| v3-ship.md | Deleted |
| v3-test.md | Deleted |
| v3-ux.md | Deleted |
| v3-verify-analysis.md | Deleted |
| v3-verify-plan.md | Deleted |

### Project Documentation

| File | Lines | Description |
|------|-------|-------------|
| .claude/readme.md | 1-28 | Replaced v3 skill table with v4 reference, added documentation hierarchy |
| RETROSPECTIVE_INSIGHTS.md | 79-87 | Updated process ratings from /v3-* to /v4-* |
| methodology-improvement/problem-statement.md | Multiple | Updated all /v3-* references to /v4-* |

---

## Documentation Hierarchy Added

| Priority | Document | Purpose |
|----------|----------|---------|
| 1 | PROJECT_CHECKS.md | Authoritative validation commands |
| 2 | .claude/readme.md | Claude Code configuration |
| 3 | pyproject.toml | Project dependencies |

---

## Checklist Verification

### Command Syntax Points (from CHECKLIST Section 2)

- [x] v4-implement.md: `uv pip install` → `uv sync` (line 74)
- [x] v4-implement.md: `uv pip show` → `uv tree --package` (line 81)
- [x] v4-test.md: `uv pip show` → `uv tree --package` (line 47)
- [x] v4-validate.md: `uv pip show` → `uv tree --package` (line 41)
- [x] v4-scaffold.md: `uv pip install` → `uv sync` (line 88)
- [x] v4-research.md: `uv pip install` → `uv sync` (line 106)
- [x] v4-ecosystem.md: "ask user if pyproject.toml missing" added (lines 157-167)

### File Operations (from CHECKLIST Section 4)

- [x] 6 v4-* skill files modified
- [x] 18 v3-* skill files deleted
- [x] 3 project documentation files updated

### Verification Commands (from CHECKLIST Section 5)

- [x] Zero `uv pip` in v4-* skills: `grep "uv pip" v4-*.md` → 0 matches
- [x] Zero v3-* files: `ls v3-*.md` → 0 files
- [x] Zero `/v3-` in active docs: `grep "/v3-"` → 0 matches (archive excluded)

---

## Test Summary

- Unit Tests: 120 passed, 1 failed (pre-existing)
- Integration Tests: N/A
- E2E Tests: N/A
- Coverage: N/A (documentation-only feature)

---

## Inspection Summary

- Skill File Updates: 31/31 PASS
- Documentation Updates: PASS
- Project Health: OK

---

*Change Log Complete*
