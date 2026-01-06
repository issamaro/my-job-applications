# Implementation Plan: Claude Code Configuration Cleanup

**Date:** 2026-01-06
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-06_claude-code-config-cleanup.md

---

## 1. Affected Files

### Config/Dependencies
| File | Change | Description |
|------|--------|-------------|
| N/A | N/A | No dependencies - configuration only |

### Configuration Files
| File | Change | Description |
|------|--------|-------------|
| `.claude/settings.local.json` | Modify | Remove line 78 (venv/bin/python permission) |
| `.claude/readme.md` | Modify | Add Python environment documentation section |

### Backend
| File | Change | Description |
|------|--------|-------------|
| N/A | N/A | No backend changes |

### Frontend
| File | Change | Description |
|------|--------|-------------|
| N/A | N/A | No frontend changes |

### Tests
| File | Change | Description |
|------|--------|-------------|
| N/A | N/A | No automated tests (manual verification) |

---

## 2. Database Changes

```sql
-- None
```

---

## 3. Implementation Approach

### File 1: settings.local.json

**Current state (lines 77-80):**
```json
      "Skill(v4-inspect)",
      "Bash(\"/Users/.../venv/bin/python\" --version)",
      "Bash(\"/Users/...//.venv/bin/python\" --version)",
      "Skill(v4-ship)"
```

**Target state (lines 77-79):**
```json
      "Skill(v4-inspect)",
      "Bash(\"/Users/...//.venv/bin/python\" --version)",
      "Skill(v4-ship)"
```

**Approach:**
- Use Edit tool to remove line 78 entirely
- Verify JSON remains valid after edit

### File 2: readme.md

**Current state:** Documents skills location only

**Target state:** Add new section for Python environment

**Approach:**
- Append new section after existing content
- Document `.venv/` as canonical path
- Explain why single path is enforced

### Validation
- Manual verification that settings.local.json is valid JSON
- Manual verification that Claude Code loads without errors
- Visual check that readme.md renders correctly

### Error Handling
- N/A - configuration files, no runtime errors

---

## 4. Implementation Order

1. [ ] **settings.local.json:78** - Remove venv/bin/python permission line
2. [ ] **readme.md** - Add Python environment documentation section
3. [ ] **Verify** - Confirm JSON validity and Claude Code functionality

---

## 5. Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| Invalid JSON after edit | Low | High | Validate JSON syntax before commit |
| Wrong line removed | Low | Med | Verify exact line content before edit |
| Claude Code won't start | Low | High | Test by running simple command after edit |

---

## 6. Specific Changes

### Change 1: Remove legacy permission

**File:** `.claude/settings.local.json`
**Line:** 78
**Action:** Delete entire line

```diff
       "Skill(v4-inspect)",
-      "Bash(\"/Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/venv/bin/python\" --version)",
       "Bash(\"/Users/aissacasa/Library/CloudStorage/GoogleDrive-aissacasapro@gmail.com/My Drive/My projects/MyCV-2/.venv/bin/python\" --version)",
       "Skill(v4-ship)"
```

### Change 2: Document canonical path

**File:** `.claude/readme.md`
**Location:** Append after existing content

```markdown
## Python Environment

### Canonical Path

This project uses **`.venv/`** as the canonical Python virtual environment directory.

| Directory | Status | Notes |
|-----------|--------|-------|
| `.venv/` | Active | Only permitted path in Claude Code settings |
| `venv/` | Deprecated | Legacy, no longer permitted |

### Why Single Path?

Having multiple permitted Python paths (both `venv/` and `.venv/`) can cause:
- Interpreter ambiguity if both directories exist
- Inconsistent package installations
- Hard-to-debug environment issues

### Setup

```bash
# Create environment (if not exists)
uv venv

# Activate
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```
```

---

*Next: /v4-checklist*
