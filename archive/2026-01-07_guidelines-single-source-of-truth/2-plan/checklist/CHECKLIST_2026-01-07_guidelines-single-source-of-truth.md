# Checklist: Guidelines Single Source of Truth

**Date:** 2026-01-07
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

| Requirement | Version | Verify | Status |
|-------------|---------|--------|--------|
| uv | 0.9.8+ | `uv --version` | [ ] |

- [ ] Global skills directory accessible: `ls ~/.claude/commands/`

**STOP if ecosystem is not ready.**

---

## 1. Dependencies (CRITICAL)

No new dependencies - this is a documentation-only feature.

| Check | Status |
|-------|--------|
| No dependencies to add | [x] N/A |

---

## 2. Command Syntax (from LIBRARY_NOTES)

### v4-implement.md

- [ ] Line ~74: `uv pip install -r requirements.txt` → `uv sync`
- [ ] Line ~81: `uv pip show [package] | grep Version` → `uv tree --package [package]`

### v4-test.md

- [ ] Line ~47: `uv pip show [package]` → `uv tree --package [package]`
- [ ] Manifest reference: `requirements.txt` → `pyproject.toml`

### v4-validate.md

- [ ] Lines ~40-41: `uv pip show [package] | grep Version` → `uv tree --package [package]`

### v4-scaffold.md

- [ ] Line ~88: `uv pip install -r requirements.txt` → `uv sync`

### v4-research.md

- [ ] Line ~106: `uv pip install -r requirements.txt` → `uv sync`

### v4-ecosystem.md

- [ ] Add "ask user if pyproject.toml missing" logic
- [ ] No pip fallback present

---

## 3. UX (User Experience)

N/A - No UI changes in this feature.

---

## 4. File Operations

### Phase 1: v4-* Skill Updates (6 files)

- [ ] `~/.claude/commands/v4-implement.md` modified
- [ ] `~/.claude/commands/v4-test.md` modified
- [ ] `~/.claude/commands/v4-validate.md` modified
- [ ] `~/.claude/commands/v4-scaffold.md` modified
- [ ] `~/.claude/commands/v4-research.md` modified
- [ ] `~/.claude/commands/v4-ecosystem.md` modified

### Phase 2: v3-* Skill Deletion (18 files)

- [ ] `~/.claude/commands/v3-analyze.md` deleted
- [ ] `~/.claude/commands/v3-build.md` deleted
- [ ] `~/.claude/commands/v3-checklist.md` deleted
- [ ] `~/.claude/commands/v3-close.md` deleted
- [ ] `~/.claude/commands/v3-design.md` deleted
- [ ] `~/.claude/commands/v3-feature.md` deleted
- [ ] `~/.claude/commands/v3-implement.md` deleted
- [ ] `~/.claude/commands/v3-inspect.md` deleted
- [ ] `~/.claude/commands/v3-plan.md` deleted
- [ ] `~/.claude/commands/v3-reflect.md` deleted
- [ ] `~/.claude/commands/v3-requirements.md` deleted
- [ ] `~/.claude/commands/v3-research.md` deleted
- [ ] `~/.claude/commands/v3-scope.md` deleted
- [ ] `~/.claude/commands/v3-ship.md` deleted
- [ ] `~/.claude/commands/v3-test.md` deleted
- [ ] `~/.claude/commands/v3-ux.md` deleted
- [ ] `~/.claude/commands/v3-verify-analysis.md` deleted
- [ ] `~/.claude/commands/v3-verify-plan.md` deleted

### Phase 3: Documentation Updates (3 files)

- [ ] `.claude/readme.md` updated (v3→v4 references, doc hierarchy added)
- [ ] `RETROSPECTIVE_INSIGHTS.md` updated (v3→v4 references)
- [ ] `methodology-improvement/problem-statement.md` updated (v3→v4 references)

---

## 5. Verification Commands

### Zero `uv pip` Commands

After implementation, run:

```bash
# Check all v4-* skills for uv pip (expect 0 results)
grep -l "uv pip" ~/.claude/commands/v4-*.md 2>/dev/null && echo "FAIL: uv pip found" || echo "PASS: no uv pip"
```

- [ ] Zero `uv pip` commands in v4-* skills

### Zero v3-* Skills Remaining

```bash
# Check no v3-* files remain (expect 0 results)
ls ~/.claude/commands/v3-*.md 2>/dev/null && echo "FAIL: v3 files found" || echo "PASS: no v3 files"
```

- [ ] Zero v3-* files in `~/.claude/commands/`

### Documentation v3 References

```bash
# Check project docs for /v3- references (should only be in archive/)
grep -rn "/v3-" .claude/ RETROSPECTIVE_INSIGHTS.md methodology-improvement/ 2>/dev/null | grep -v "archive/" && echo "FAIL: v3 refs found" || echo "PASS: no v3 refs"
```

- [ ] Zero `/v3-` references in non-archive documentation

---

## 6. Project-Specific (from PROJECT_CHECKS.md)

### Applicable Checks

| Check | Applicability | Notes |
|-------|---------------|-------|
| Python venv setup | N/A | No code changes |
| Backend health | N/A | No code changes |
| Test suite | N/A | No code changes |
| Frontend build | N/A | No code changes |

### Post-Implementation Verification

After all changes, verify project still healthy:

```bash
# Quick validation (should still pass - no code changed)
source .venv/bin/activate && python -c "from main import app; print('Backend: OK')"
```

- [ ] Project still healthy after documentation changes

---

## 7. Accessibility

N/A - No UI changes in this feature.

---

## Summary

| Section | Items | Critical |
|---------|-------|----------|
| 0. Ecosystem | 2 | Yes |
| 1. Dependencies | 0 | - |
| 2. Command Syntax | 10 | Yes |
| 3. UX | 0 | - |
| 4. File Operations | 27 | Yes |
| 5. Verification | 3 | Yes |
| 6. Project-Specific | 1 | No |
| 7. Accessibility | 0 | - |
| **Total** | **43** | |

---

## Verification at Closure

Each item above will be checked with file:line reference at `/v4-close`.

---

*Contract for /v4-implement*
