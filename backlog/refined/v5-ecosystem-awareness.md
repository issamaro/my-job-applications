# v5-ecosystem-awareness

**Size:** S
**Date:** 2026-01-07
**Est. Files:** 3 (v5-research.md, v5-scaffold.md, v5-implement.md)
**Dependencies:** None

---

## Description

Ensure v5 slash commands respect and verify the project's actual ecosystem state before making assumptions or taking actions.

Two related problems to solve:
1. **Init vs Sprint venv handling** - Sprint commands (v5-implement) should NOT create venv; only init commands (v5-scaffold) should
2. **Research pre-check** - v5-research should check existing `.python-version`, `pyproject.toml`, `.nvmrc` before looking up external docs

---

## Scope (IN)

- Add "Check Existing Project" step to v5-research before context7 lookup
- Ensure v5-scaffold creates venv (`uv venv`)
- Ensure v5-implement only syncs dependencies (`uv sync`)
- Apply same pattern to Node ecosystem (npm install vs npm ci)

---

## Out of Scope (NOT)

- v4 skill updates (separate effort)
- Automated ecosystem detection (manual checks sufficient)
- New file creation for ecosystem config

---

## Success Criteria

- [ ] v5-research reads `.python-version` before stating Python version
- [ ] v5-research reads `pyproject.toml` before suggesting dependencies
- [ ] v5-scaffold includes `uv venv` creation step
- [ ] v5-implement uses only `uv sync`, never `uv venv`
- [ ] Node equivalent: v5-scaffold runs `npm install`, v5-implement runs `npm ci`

---

## Notes

- Originated from two raw items: `v5-skills-ecosystem-enforcement-review.md` and `v4-research-skill-check-existing-ecosystem-versions-first.md`
- User explicitly prefers `uv sync` over any `uv pip` commands
