# Claude Code Configuration Cleanup - SCOPED_FEATURE

**Size:** S
**Scoped:** 2026-01-06
**Files affected:** ~2
**Dependencies:** None
**Ready for:** /v4-feature
**Epic:** Environment & Dependency Management Overhaul

---

## Description

Clean up `.claude/settings.local.json` to remove legacy configuration that allows ambiguous environment paths. Currently, the settings permit both `venv/` and `.venv/` Python paths, which can cause Claude Code to use the wrong interpreter if both exist.

## Context (Current State)

`.claude/settings.local.json` lines 78-79:
```json
"Bash(\"/path/to/venv/bin/python\" --version)",
"Bash(\"/path/to/.venv/bin/python\" --version)"
```

**Problem:** If both directories exist (even temporarily), Claude Code has no preference and may use whichever it tries first.

**Actual state:**
- Only `.venv/` exists and should be used
- `venv/` permission is legacy from when both existed

## Scope (IN)

- Remove `venv/bin/python` permission from `settings.local.json`
- Keep only `.venv/bin/python` permission
- Document in `.claude/readme.md` which Python path is canonical
- Add permission for `uv` commands (future-proofing)

## Out of Scope (NOT)

- Adding environment validation hooks
- Modifying slash command behavior
- Adding pre-flight environment checks
- Changing how Claude Code discovers Python

## Success Criteria

- [ ] `settings.local.json` has only ONE Python path permission (`.venv/`)
- [ ] No `venv/` references remain in Claude Code configuration
- [ ] `.claude/readme.md` documents the canonical Python environment path
- [ ] `uv` commands are permitted (Bash(uv:*))

## Notes

- This is a defensive change - prevents future confusion if `venv/` gets created accidentally
- The settings file is project-local, so changes only affect this repository
- Consider adding a comment in settings explaining why only one path is allowed
