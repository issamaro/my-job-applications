# Checklist: Claude Code Configuration Cleanup

**Date:** 2026-01-06
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

| Requirement | Version | Verify | Status |
|-------------|---------|--------|--------|
| N/A | N/A | Configuration files only | [ ] |

- [x] No runtime environment needed for this change
- [x] Changes are to Claude Code config, not project code

**This feature modifies Claude Code settings, not project code.**

---

## 1. Dependencies (CRITICAL)

| Library | Constraint | Manifest | Status |
|---------|-----------|----------|--------|
| N/A | N/A | No dependencies | [x] |

**No dependencies for configuration file edits.**

---

## 2. Syntax

- [ ] JSON: Valid syntax after removing line → `.claude/settings.local.json`
- [ ] JSON: No trailing comma issues after line removal
- [ ] Markdown: Proper heading hierarchy → `.claude/readme.md`
- [ ] Markdown: Code blocks have language hints

---

## 3. UX

- [ ] N/A - No user-facing UI changes

---

## 4. Tests

| Test Type | Description | Status |
|-----------|-------------|--------|
| Manual | JSON parses without error | [ ] |
| Manual | Claude Code starts without error | [ ] |
| Manual | Readme renders correctly in viewer | [ ] |

**Verification commands:**
```bash
# Validate JSON syntax
python -c "import json; json.load(open('.claude/settings.local.json'))"

# Test Claude Code functionality (run any simple command)
# Claude Code should load settings without error
```

---

## 5. Accessibility

- [ ] N/A - No UI components

---

## 6. Project-Specific (from PROJECT_CHECKS.md)

**Note:** This feature doesn't affect project code, so most PROJECT_CHECKS.md items don't apply.

Relevant check:
- [ ] No `venv/` references remain in Claude Code configuration (aligns with `.venv/` being canonical)

**From PROJECT_CHECKS.md observation:** The file still references `venv/` in some commands (legacy). This feature ensures Claude Code settings are updated to `.venv/` only.

---

## 7. Success Criteria (from SCOPED_FEATURE)

- [ ] `settings.local.json` has only ONE Python path permission (`.venv/`)
- [ ] No `venv/` references remain in Claude Code configuration
- [ ] `.claude/readme.md` documents the canonical Python environment path
- [ ] `uv` commands are permitted (`Bash(uv:*)`) - Already exists, verify still present

---

## Verification at Closure

Each item above will be checked with file:line reference at `/v4-close`.

**Final verification:**
```bash
# Check no venv/ in settings (should return nothing)
grep -n "venv/bin/python" .claude/settings.local.json | grep -v "\.venv"

# Check .venv/ still permitted
grep -n ".venv/bin/python" .claude/settings.local.json

# Check uv permitted
grep -n "Bash(uv:" .claude/settings.local.json
```

---

*Contract for /v4-implement*
