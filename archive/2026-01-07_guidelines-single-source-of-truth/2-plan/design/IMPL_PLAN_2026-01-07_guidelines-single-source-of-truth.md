# Implementation Plan: Guidelines Single Source of Truth

**Date:** 2026-01-07
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-07_guidelines-single-source-of-truth.md

---

## 1. Affected Files

### Config/Dependencies

No config changes - this feature updates documentation/skill files only.

### Global Skills (Modify)

| File | Change | Description |
|------|--------|-------------|
| `~/.claude/commands/v4-implement.md` | Modify | Replace `uv pip` commands with `uv sync` and `uv tree` |
| `~/.claude/commands/v4-test.md` | Modify | Replace `uv pip show` with `uv tree --package` |
| `~/.claude/commands/v4-validate.md` | Modify | Replace `uv pip show` with `uv tree --package` |
| `~/.claude/commands/v4-scaffold.md` | Modify | Replace `uv pip install -r requirements.txt` with `uv sync` |
| `~/.claude/commands/v4-research.md` | Modify | Replace `uv pip install -r requirements.txt` with `uv sync` |
| `~/.claude/commands/v4-ecosystem.md` | Modify | Remove pip fallback, add "ask user if pyproject.toml missing" |

### Global Skills (Delete)

| File | Action | Description |
|------|--------|-------------|
| `~/.claude/commands/v3-analyze.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-build.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-checklist.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-close.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-design.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-feature.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-implement.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-inspect.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-plan.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-reflect.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-requirements.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-research.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-scope.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-ship.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-test.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-ux.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-verify-analysis.md` | Delete | Legacy v3 skill |
| `~/.claude/commands/v3-verify-plan.md` | Delete | Legacy v3 skill |

### Project Documentation (Modify)

| File | Change | Description |
|------|--------|-------------|
| `.claude/readme.md` | Modify | Update v3→v4 skill references, add doc hierarchy |
| `RETROSPECTIVE_INSIGHTS.md` | Modify | Update v3→v4 references (process ratings section) |
| `methodology-improvement/problem-statement.md` | Modify | Update v3→v4 references |

---

## 2. Database Changes

```sql
-- None (documentation-only feature)
```

---

## 3. Implementation Approach

### Strategy: Documentation-Only Updates

This feature involves no code changes to the MyCV-2 application. All changes are to:
1. Global skill files (`~/.claude/commands/`)
2. Project documentation files

### Pattern: Find and Replace

For each v4-* skill file:
1. Search for `uv pip` commands
2. Replace with modern uv equivalents per LIBRARY_NOTES
3. Add "ask user" logic for missing pyproject.toml (v4-ecosystem only)

### Validation Approach

After each skill modification:
- Grep for remaining `uv pip` patterns
- Verify replacement syntax matches LIBRARY_NOTES

### Error Handling

For v4-ecosystem: Instead of pip fallback, add explicit user prompt:
```markdown
If pyproject.toml is missing:
1. STOP - do not use pip commands
2. Ask user what to do
```

---

## 4. Implementation Order

### Phase 1: Update v4-* Skills (6 files)

1. [ ] **v4-implement.md** - Lines 74, 81: Replace pip commands
   - Line 74: `uv pip install -r requirements.txt` → `uv sync`
   - Line 81: `uv pip show [package] | grep Version` → `uv tree --package [package]`

2. [ ] **v4-test.md** - Line 47: Replace pip command
   - `uv pip show [package]` → `uv tree --package [package]`

3. [ ] **v4-validate.md** - Lines 40-41: Replace pip commands
   - `uv pip show [package] | grep Version` → `uv tree --package [package]`

4. [ ] **v4-scaffold.md** - Line 88: Replace pip command
   - `uv pip install -r requirements.txt` → `uv sync`

5. [ ] **v4-research.md** - Line 106: Replace pip command
   - `uv pip install -r requirements.txt` → `uv sync`

6. [ ] **v4-ecosystem.md** - Add missing pyproject.toml handling
   - Add explicit "ask user" logic instead of pip fallback

### Phase 2: Delete v3-* Skills (18 files)

7. [ ] Delete all 18 v3-*.md files from `~/.claude/commands/`
   - Single `rm` command for all files

### Phase 3: Update Project Documentation (3 files)

8. [ ] **.claude/readme.md** - Restructure completely
   - Replace v3 skill table with v4 skill reference
   - Add documentation hierarchy section
   - Keep Python Environment section (already modern uv)

9. [ ] **RETROSPECTIVE_INSIGHTS.md** - Update process ratings
   - Replace `/v3-scope` → `/v4-scope` 
   - Replace `/v3-analyze` → `/v4-analyze`
   - Replace `/v3-plan` → `/v4-plan`
   - Replace `/v3-build` → `/v4-build`
   - Replace `/v3-ship` → `/v4-ship`

10. [ ] **methodology-improvement/problem-statement.md** - Update references
    - Replace `/v3-*` → `/v4-*` throughout
    - Update problem descriptions to reflect v4 context

### Phase 4: Verification

11. [ ] Grep all v4-* skills for `uv pip` - expect 0 results
12. [ ] Verify no v3-*.md files remain in `~/.claude/commands/`
13. [ ] Grep documentation files for `v3-` - expect 0 results (except archive references)

---

## 5. Specific Changes Detail

### v4-implement.md Changes

**Before (Line 74):**
```bash
uv pip install -r requirements.txt
```

**After:**
```bash
uv sync
```

**Before (Line 81):**
```bash
uv pip show [package] | grep Version
```

**After:**
```bash
uv tree --package [package]
```

---

### v4-test.md Changes

**Before (Line 47):**
```markdown
| `requirements.txt` | `uv pip show [package] \| grep Version` |
```

**After:**
```markdown
| `pyproject.toml` | `uv tree --package [package]` |
```

---

### v4-validate.md Changes

**Before (Lines 40-41):**
```bash
# Python
uv pip show [package] | grep Version
```

**After:**
```bash
# Python
uv tree --package [package]
```

---

### v4-scaffold.md Changes

**Before (Line 88):**
```bash
uv pip install -r requirements.txt
```

**After:**
```bash
uv sync
```

---

### v4-research.md Changes

**Before (Line 106):**
```bash
uv pip install -r requirements.txt
```

**After:**
```bash
uv sync
```

---

### v4-ecosystem.md Changes

Add new section for missing pyproject.toml handling:

```markdown
### Handling Missing pyproject.toml

If the project does not have pyproject.toml:

1. **STOP** - Do not use pip or requirements.txt commands
2. **Ask user** how to proceed:
   - "This project doesn't have pyproject.toml. Would you like me to:
     a) Create pyproject.toml with `uv init`
     b) Help you set up the project structure
     c) Proceed without dependency management"
3. Wait for user response before continuing
```

---

### .claude/readme.md Changes

Replace entire Global Skills section with:

```markdown
## Global Skills Location

User-defined skills (v4 methodology) are located at:

```
~/.claude/commands/
```

### v4 Skills

See v4-* files in `~/.claude/commands/` for available skills.

### Documentation Hierarchy

| Priority | Document | Purpose |
|----------|----------|---------|
| 1 | PROJECT_CHECKS.md | Authoritative validation commands |
| 2 | .claude/readme.md | Claude Code configuration |
| 3 | pyproject.toml | Project dependencies |

### Editing Skills

To modify a skill:
```bash
code ~/.claude/commands/v4-feature.md
```
```

---

## 6. Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| v3 skills still referenced elsewhere | Low | Low | Grep project for `/v3-` references |
| uv tree command syntax incorrect | Low | Med | Already verified locally (uv 0.9.8) |
| Missing v3 file in delete list | Low | Low | Use glob pattern `v3-*.md` |

---

*Next: /v4-checklist*
