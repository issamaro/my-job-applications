# Feature Spec: Guidelines Single Source of Truth

**Date:** 2026-01-07
**Source:** backlog/done/guidelines-single-source-of-truth.md
**Status:** Draft
**Revision:** 2 (NO `uv pip` anywhere)

---

## 1. Problem Statement

### User Request
> Update v4-* skills to use modern uv commands only (`uv sync`, `uv tree`, `uv add`). Remove ALL `uv pip` commands. If pyproject.toml is missing, ask the user instead of falling back to pip.

### Pain Point
Two interconnected problems:
1. **Guidelines are spread** across multiple files with duplication
2. **v4-* skills use `uv pip` commands** which are legacy - modern uv doesn't need them

### User Persona
- **Primary:** Developer (Claude Code user) following v4-* skill workflows
- **Secondary:** Project maintainers keeping documentation synchronized

---

## 2. BDD Scenarios

```gherkin
Feature: Guidelines Single Source of Truth
  As a developer using Claude Code v4-* skills
  I want skills to use correct modern uv commands (no uv pip)
  So that I use the modern workflow without legacy patterns

Scenario: Developer runs v4-implement on pyproject.toml project
  Given a project with pyproject.toml and uv.lock
  When the developer follows v4-implement instructions
  Then the skill recommends "uv sync" for dependency installation
  And the skill recommends "uv tree" to check packages
  And no "uv pip" commands are mentioned anywhere

Scenario: Developer runs v4-ecosystem on new project
  Given a project being set up
  When the developer invokes v4-ecosystem
  Then the skill checks for pyproject.toml
  And if pyproject.toml exists, recommends "uv sync"
  And if pyproject.toml is missing, asks the user what to do
  And never mentions "uv pip" or "pip" commands

Scenario: Developer checks package installation
  Given a project with uv-managed dependencies
  When the developer needs to verify a package is installed
  Then the skill recommends "uv tree" or "uv tree --package [name]"
  And does not mention "uv pip list" or "uv pip show"

Scenario: Developer looks for authoritative setup instructions
  Given the project documentation
  When the developer reads .claude/readme.md
  Then they find a documentation hierarchy section
  And the hierarchy points to PROJECT_CHECKS.md for validation commands
  And setup instructions are not duplicated between files

Scenario: Missing pyproject.toml
  Given a project without pyproject.toml
  When the developer follows v4-* skill instructions
  Then the skill asks the user how to proceed
  And does NOT fall back to pip or requirements.txt automatically

Scenario: v3 skills are removed
  Given the global skills directory ~/.claude/commands/
  When the cleanup is complete
  Then no v3-*.md files exist
  And /v3-* commands are no longer available
  And documentation only references v4-* skills
```

---

## 3. Requirements

### Must Have
- [ ] Update v4-implement.md: Replace `uv pip install -r requirements.txt` with `uv sync`
- [ ] Update v4-implement.md: Replace `uv pip show` with `uv tree`
- [ ] Update v4-test.md: Replace `uv pip show` with `uv tree`
- [ ] Update v4-validate.md: Replace `uv pip show` with `uv tree`
- [ ] Update v4-scaffold.md: Replace `uv pip install -r requirements.txt` with `uv sync`
- [ ] Update v4-research.md: Replace `uv pip install -r requirements.txt` with `uv sync`
- [ ] Update v4-ecosystem.md: Use modern uv only, ask user if pyproject.toml missing
- [ ] Add documentation hierarchy section to `.claude/readme.md`
- [ ] Ensure PROJECT_CHECKS.md is referenced as authoritative for validation commands
- [ ] Delete 18 v3-* skill files from `~/.claude/commands/`
- [ ] Remove v3 references from `RETROSPECTIVE_INSIGHTS.md`
- [ ] Remove v3 references from `methodology-improvement/problem-statement.md`
- [ ] Verify ZERO `uv pip` commands remain in any v4-* skill

### Should Have
- [ ] Remove duplicated setup instructions from `.claude/readme.md`

### Won't Have
- Any `uv pip` commands (not even `uv pip list`)
- pip fallback for missing pyproject.toml (ask user instead)
- Creating new skills
- Changing project tooling itself
- Modifying archive files (historical records)

---

## 4. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| Global skills are at `~/.claude/commands/` | Architecture | Verified |
| Modern uv (0.4.0+) is being used | Library | `uv 0.9.8` verified |
| `uv tree` replaces `uv pip list` and `uv pip show` | Library | Modern uv pattern |
| Projects should have pyproject.toml | Architecture | Ask user if missing |

---

## 5. Open Questions

- None. The scope is clear: remove ALL `uv pip` commands, use modern uv only.

---

*Next: /v4-verify-analysis (no UI changes in this feature)*
