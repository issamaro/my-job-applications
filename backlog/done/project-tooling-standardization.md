# Project Tooling Standardization - SCOPED_FEATURE

**Size:** M
**Scoped:** 2026-01-06
**Files affected:** ~5
**Dependencies:** None
**Ready for:** /v4-feature
**Epic:** Environment & Dependency Management Overhaul

---

## Description

Establish a single, authoritative Python project configuration using modern standards. Currently the project has fragmented configuration: `.python-version` for version, `requirements.txt` for dependencies, but no `pyproject.toml` to unify them. This creates ambiguity for both humans and tools about how the project should be managed.

## Context (Current State)

| File | Purpose | Status |
|------|---------|--------|
| `.python-version` | Python version (3.13) | Exists |
| `requirements.txt` | Dependencies | Exists |
| `pyproject.toml` | Unified config | **MISSING** |
| `package.json` | Node config with engines constraint | Exists |

**Problem:** Python has no equivalent to `package.json`'s `engines` field. Tools like `uv` and `pip` don't enforce Python version from `.python-version`.

## Scope (IN)

- Adopt `uv` as the primary package manager with native commands:
  - `uv sync` to install dependencies
  - `uv run pytest` to run tests
  - `uv lock` to generate lockfile
- Create `pyproject.toml` as single source of truth:
  - `[project]` section (name, version, description)
  - `requires-python = ">=3.13"` constraint
  - `[project.dependencies]` for runtime deps
  - `[project.optional-dependencies.dev]` for test deps (pytest, etc.)
  - `[tool.pytest.ini_options]` for test config
  - `[tool.uv]` section if needed
- Remove `requirements.txt` (replaced by `uv.lock`)
- Keep `.python-version` for pyenv/asdf compatibility
- Update `.gitignore` to ignore both `venv/` and `.venv/` patterns

## Out of Scope (NOT)

- Changing the virtual environment location
- Updating slash commands (separate feature)

## Success Criteria

- [ ] `pyproject.toml` exists with valid `[project]` section
- [ ] `requires-python` constraint is `>=3.13`
- [ ] All dependencies migrated to `pyproject.toml`
- [ ] `uv sync` installs all dependencies
- [ ] `uv run pytest` runs tests successfully
- [ ] `uv.lock` is generated and committed
- [ ] `requirements.txt` is removed
- [ ] `.gitignore` ignores both `venv/` and `.venv/`

## Notes

- `pyproject.toml` is PEP 518/621 standard
- `uv` provides fast, reliable dependency resolution with lockfile
- `uv.lock` replaces `requirements.txt` for reproducible installs
