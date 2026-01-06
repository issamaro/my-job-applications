# Feature Spec: Claude Code Configuration Cleanup

**Date:** 2026-01-06
**Source:** backlog/done/claude-code-config-cleanup.md
**Status:** Draft

---

## 1. Problem Statement

### User Request
> Clean up `.claude/settings.local.json` to remove legacy configuration that allows ambiguous environment paths.

### Pain Point
The current settings permit both `venv/` and `.venv/` Python paths, which can cause Claude Code to use the wrong interpreter if both directories exist. This creates a potential for inconsistent Python environment usage.

### User Persona
Developer using Claude Code for Python development who needs deterministic environment resolution.

---

## 2. BDD Scenarios

```gherkin
Feature: Claude Code Configuration Cleanup
  As a developer using Claude Code
  I want a single canonical Python path configured
  So that Claude Code always uses the correct interpreter

Scenario: Only .venv path is permitted
  Given the settings.local.json file exists
  When Claude Code checks Python permissions
  Then it should only find .venv/bin/python permitted
  And no venv/bin/python permission exists

Scenario: Documentation reflects canonical path
  Given the .claude/readme.md file exists
  When a developer reads the documentation
  Then they find .venv/ documented as the canonical Python environment
  And the reasoning is explained

Scenario: Legacy venv directory created accidentally
  Given only .venv permission exists in settings
  When a user accidentally creates a venv/ directory
  Then Claude Code ignores venv/ for Python commands
  And continues using .venv/ exclusively
```

---

## 3. Requirements

### Must Have
- [ ] Remove `venv/bin/python` permission from `settings.local.json` (line 78)
- [ ] Keep only `.venv/bin/python` permission
- [ ] Document canonical Python path in `.claude/readme.md`

### Should Have
- [ ] Add explanatory comment in readme about why single path is enforced

### Won't Have
- Adding environment validation hooks
- Modifying slash command behavior
- Adding pre-flight environment checks
- Changing how Claude Code discovers Python

---

## 4. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| `.venv/` is the only active environment | Architecture | Verified: only `.venv/` exists |
| `uv` commands already permitted | Library | Line 19 shows `Bash(uv:*)` already allowed |
| No other code references `venv/` path | Architecture | Only settings.local.json has the reference |

---

## 5. Open Questions

- None - scope is clear and files are identified

---

## 6. Files to Modify

| File | Change |
|------|--------|
| `.claude/settings.local.json` | Remove line 78 (venv permission) |
| `.claude/readme.md` | Add Python environment section |

---

*Next: /v4-verify-analysis (no UI changes)*
