# Checklist: Project Tooling Standardization

**Date:** 2026-01-06
**Purpose:** Verification contract for implementation

---

## 0. Ecosystem (CRITICAL - VERIFY FIRST)

| Requirement | Version | Verify | Status |
|-------------|---------|--------|--------|
| Python | >=3.13 | `python --version` | [ ] |
| uv | any | `uv --version` | [ ] |

- [ ] uv is installed and available in PATH

**STOP if ecosystem is not ready.**

---

## 1. Dependencies (CRITICAL)

### Runtime Dependencies
| Library | Constraint | In pyproject.toml | Status |
|---------|-----------|-------------------|--------|
| fastapi | `>=0.100.0` | `[project.dependencies]` | [ ] |
| pydantic | `>=2.0` | `[project.dependencies]` | [ ] |
| uvicorn | `>=0.32.0` | `[project.dependencies]` | [ ] |
| anthropic | `>=0.40.0` | `[project.dependencies]` | [ ] |
| python-dotenv | `>=1.0.0` | `[project.dependencies]` | [ ] |
| weasyprint | `>=62.0` | `[project.dependencies]` | [ ] |
| jinja2 | `>=3.1.0` | `[project.dependencies]` | [ ] |

### Dev Dependencies
| Library | Constraint | In pyproject.toml | Status |
|---------|-----------|-------------------|--------|
| pytest | `>=8.0.0` | `[dependency-groups.dev]` | [ ] |
| pytest-asyncio | `>=0.24.0` | `[dependency-groups.dev]` | [ ] |
| httpx | `>=0.27.0` | `[dependency-groups.dev]` | [ ] |

**STOP if any dependency is missing.**

---

## 2. Syntax (pyproject.toml Structure)

- [ ] `[project]` section exists with name, version, description
- [ ] `requires-python = ">=3.13"` is set
- [ ] `[project.dependencies]` contains runtime deps (array format)
- [ ] `[dependency-groups]` used (NOT `[project.optional-dependencies]`)
- [ ] `[dependency-groups.dev]` contains test deps
- [ ] `[tool.pytest.ini_options]` configured
- [ ] `[tool.uv]` section with `default-groups = ["dev"]`

---

## 3. UX

N/A - No UI changes in this feature.

---

## 4. Tests

- [ ] `uv lock` succeeds without errors
- [ ] `uv sync` succeeds without errors
- [ ] `uv run pytest` executes and passes
- [ ] Existing tests still pass after migration

---

## 5. Accessibility

N/A - No UI changes in this feature.

---

## 6. Project-Specific

None - no `project-checks.md` found.

---

## 7. File Changes

| File | Action | Verified |
|------|--------|----------|
| `pyproject.toml` | Created | [ ] |
| `uv.lock` | Generated | [ ] |
| `requirements.txt` | Deleted | [ ] |
| `.gitignore` | `venv/` added | [ ] |

---

## 8. Success Criteria (from SCOPED_FEATURE)

- [ ] `pyproject.toml` exists with valid `[project]` section
- [ ] `requires-python` constraint is `>=3.13`
- [ ] All dependencies migrated to `pyproject.toml`
- [ ] `uv sync` installs all dependencies
- [ ] `uv run pytest` runs tests successfully
- [ ] `uv.lock` is generated
- [ ] `requirements.txt` is removed
- [ ] `.gitignore` ignores both `venv/` and `.venv/`

---

## Verification at Closure

Each item above will be checked with file:line reference at `/v4-close`.

---

*Contract for /v4-implement*
