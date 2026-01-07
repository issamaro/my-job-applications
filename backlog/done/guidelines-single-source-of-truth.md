# Guidelines Single Source of Truth - SCOPED_FEATURE

**Size:** L
**Scoped:** 2026-01-06
**Files affected:** ~30 (documentation files, .claude/, global v4-* skills, v3-* removal)
**Dependencies:** None
**Ready for:** /v4-feature
**Epic:** Environment & Dependency Management Overhaul

---

## Description

Two interconnected problems:

1. **Guidelines are spread** across multiple files with duplication
2. **v4-* skills are outdated** - they reference old `uv pip` patterns and `requirements.txt` when modern `uv` uses `pyproject.toml` + `uv sync`

## Audit (2026-01-06)

### Problem 1: Guidelines Spread

| File | Purpose | Duplication Issue |
|------|---------|-------------------|
| `.claude/readme.md` | Claude config | Has setup instructions |
| `PROJECT_CHECKS.md` | Validation | Also has setup instructions |
| `RETROSPECTIVE_INSIGHTS.md` | Patterns | Environment notes scattered |
| `~/.claude/commands/v4-*` | Global skills | Tooling assumptions |

### Problem 2: v4-* Skills Are Outdated

**Project actual state:**
- `pyproject.toml` with dependencies (PEP 621)
- `uv.lock` for lockfile
- `uv sync` for installation
- NO `requirements.txt` file
- NO `uv pip` commands

**What v4-* skills assume (WRONG):**

| Skill | What it says | Problem |
|-------|--------------|---------|
| v4-implement.md:74 | `uv pip install -r requirements.txt` | Use `uv sync` |
| v4-implement.md:81 | `uv pip show [package]` | Use `uv tree` instead |
| v4-test.md:47 | `uv pip show [package]` | Use `uv tree` |
| v4-validate.md:41 | `uv pip show [package]` | Use `uv tree` |
| v4-scaffold.md:88 | `uv pip install -r requirements.txt` | Use `uv sync` |
| v4-research.md:106 | `uv pip install -r requirements.txt` | Use `uv sync` |
| v4-ecosystem.md:61 | Recommends `uv` but shows old patterns | Update examples |

**Correct modern uv commands (NO `uv pip` AT ALL):**
```bash
# Install dependencies (reads pyproject.toml + uv.lock)
uv sync

# Add a dependency
uv add fastapi

# Add dev dependency
uv add --dev pytest

# Run command in venv
uv run pytest

# Check installed packages / dependency tree
uv tree

# Check specific package
uv tree --package [name]
```

## Scope (IN)

### 1. Update v4-* Skills (6 files)

Replace ALL `uv pip` patterns with modern uv commands (NO `uv pip` anywhere):

| Skill | Changes |
|-------|---------|
| v4-implement.md | `uv sync` instead of `uv pip install -r`, `uv tree` instead of `uv pip show` |
| v4-test.md | `uv tree` instead of `uv pip show` |
| v4-validate.md | `uv tree` instead of `uv pip show` |
| v4-scaffold.md | `uv sync` instead of `uv pip install -r` |
| v4-research.md | `uv sync` instead of `uv pip install -r` |
| v4-ecosystem.md | Modern uv workflow, ask user if pyproject.toml missing |

### 2. Define Documentation Hierarchy

Add to `.claude/readme.md`:

```markdown
## Documentation Hierarchy

| For... | Authoritative Source |
|--------|----------------------|
| What tools Claude can use | `.claude/settings.local.json` |
| Project setup & config | `.claude/readme.md` (this file) |
| Validation commands | `PROJECT_CHECKS.md` |
| Process patterns | `RETROSPECTIVE_INSIGHTS.md` |
| How to work (methodology) | `~/.claude/commands/v4-*` |
```

### 3. Consolidate Setup Instructions

- Keep detailed setup in `PROJECT_CHECKS.md`
- `.claude/readme.md` references it, doesn't duplicate
- Add "Last updated" to tooling sections

### 4. Add Project-Local Detection to v4-ecosystem

v4-ecosystem should check:
1. Does `pyproject.toml` + `uv.lock` exist? → Use `uv sync`
2. Does `pyproject.toml` exist (no lock)? → Use `uv lock && uv sync`
3. Missing pyproject.toml? → **ASK USER** (do not fall back to pip)
4. Document detected setup in ECOSYSTEM_DECISION artifact

### 5. Remove v3-* Skills (ADDED 2026-01-07)

**Delete 18 v3-* skill files from `~/.claude/commands/`:**
- v3-analyze.md, v3-build.md, v3-checklist.md, v3-close.md
- v3-design.md, v3-feature.md, v3-implement.md, v3-inspect.md
- v3-plan.md, v3-reflect.md, v3-requirements.md, v3-research.md
- v3-scope.md, v3-ship.md, v3-test.md, v3-ux.md
- v3-verify-analysis.md, v3-verify-plan.md

**Remove v3 references from non-archive documentation:**
- `RETROSPECTIVE_INSIGHTS.md` - remove v3 mentions
- `methodology-improvement/problem-statement.md` - remove v3 mentions
- `.claude/readme.md` - ensure only v4 references

**Note:** Archive files are historical records and will NOT be modified.

## Out of Scope (NOT)
- Any `uv pip` commands (use modern uv only)
- pip fallback (ask user instead)
- Creating new skills
- Changing project tooling

## Success Criteria

- [ ] All v4-* skills use `uv sync` and `uv tree` (NO `uv pip` anywhere)
- [ ] v4-ecosystem detects pyproject.toml, asks user if missing
- [ ] `.claude/readme.md` has documentation hierarchy section
- [ ] No duplicated setup instructions between files
- [ ] PROJECT_CHECKS.md is the authoritative source for validation commands
- [ ] All 18 v3-* skill files deleted from `~/.claude/commands/`
- [ ] No v3 references in non-archive documentation
- [ ] Zero `uv pip` commands in any v4-* skill

## Notes

- Global skills (`~/.claude/commands/`) affect ALL projects
- **NO `uv pip` commands** - modern uv doesn't need them
- If pyproject.toml missing → ask user, don't fall back to pip
- `uv sync` is idempotent and handles lockfile creation/update
- `uv tree` replaces `uv pip list` and `uv pip show`

## Three-Layer Model

1. **Layer 1:** `.claude/readme.md` - Project-specific config (what's different here)
2. **Layer 2:** `v4-* skills` - Methodology (how to work, global)
3. **Layer 3:** `PROJECT_CHECKS.md` - Operational details (commands to run)

**Fix needed:**
- Layer 2 outdated (wrong uv commands - has `uv pip` which shouldn't exist)
- Layer 1 should define hierarchy and point to Layer 3
- Layer 2 should use modern uv only, ask user if pyproject.toml missing

---

## Supersedes

- `backlog/refined/skill-environment-awareness.md` (outdated - said project uses pip)
- `backlog/raw/sort-everything-out.md` (captured)

---

*Scoped from merge of sort-everything-out.md + skill-environment-awareness.md*
