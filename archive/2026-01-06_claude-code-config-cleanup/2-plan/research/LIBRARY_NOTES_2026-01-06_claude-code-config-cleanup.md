# Library Notes: Claude Code Configuration Cleanup

**Date:** 2026-01-06
**Purpose:** Ecosystem prerequisites and syntax reference

---

## 0. Ecosystem Prerequisites

### Runtime
| Runtime | Version | Reason |
|---------|---------|--------|
| N/A | N/A | No runtime code - configuration files only |

### Tooling
| Tool | Purpose | Verify |
|------|---------|--------|
| Claude Code | Configuration target | Settings in `.claude/` |
| Text editor | JSON/Markdown editing | N/A |

### Setup Commands
```bash
# No setup required - editing existing configuration files
```

---

## 1. File Format: JSON (settings.local.json)

**No library needed** - native JSON format

### Correct Patterns
- Permission entries are strings in the `permissions.allow` array
- Format: `"Bash(\"full/path/to/executable\" args)"`
- Paths with spaces must be quoted inside the Bash() wrapper

### Current Structure (lines 78-79)
```json
"Bash(\"/path/to/venv/bin/python\" --version)",
"Bash(\"/path/to/.venv/bin/python\" --version)"
```

### Target Structure
```json
"Bash(\"/path/to/.venv/bin/python\" --version)"
```

### Syntax Notes
- Remove line 78 entirely (venv permission)
- Keep line 79 (but renumber to 78)
- Ensure valid JSON after edit (no trailing comma issues)

---

## 2. File Format: Markdown (readme.md)

**No library needed** - standard GitHub-flavored Markdown

### Correct Patterns
- Use `##` for section headers
- Use code blocks with language hints (```bash```)
- Use tables for structured information

### Addition Location
- Add new section after existing content
- Document Python environment conventions

---

## Dependencies Summary

**No dependencies required**

This feature modifies only:
1. `.claude/settings.local.json` - JSON configuration
2. `.claude/readme.md` - Markdown documentation

No package installations or version constraints apply.

---

*Reference for /v4-implement and /v4-checklist*
