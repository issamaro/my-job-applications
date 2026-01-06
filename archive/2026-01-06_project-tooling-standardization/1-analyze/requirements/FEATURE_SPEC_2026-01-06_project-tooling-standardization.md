# Feature Spec: Project Tooling Standardization

**Date:** 2026-01-06
**Source:** backlog/done/project-tooling-standardization.md
**Status:** Draft

---

## 1. Problem Statement

### User Request
> Establish a single, authoritative Python project configuration using modern standards with `uv` as the package manager.

### Pain Point
The project has fragmented configuration:
- `.python-version` specifies Python 3.13 (for pyenv/asdf)
- `requirements.txt` lists dependencies without lockfile
- No `pyproject.toml` to unify project metadata
- No reproducible dependency resolution (no lockfile)

This creates ambiguity about how the project should be managed and makes builds non-reproducible.

### User Persona
- **Developers** setting up the project for the first time
- **CI/CD systems** that need reproducible builds
- **Future maintainers** who expect modern Python tooling

---

## 2. BDD Scenarios

```gherkin
Feature: Modern Python Project Configuration with uv
  As a developer
  I want unified project configuration with uv
  So that dependency management is fast, reproducible, and standardized

Scenario: Fresh project setup with uv sync
  Given a clean checkout of the repository
  And uv is installed
  When I run "uv sync"
  Then a virtual environment is created
  And all runtime dependencies are installed
  And dev dependencies are installed

Scenario: Running tests with uv run
  Given the project is synced with uv
  When I run "uv run pytest"
  Then pytest executes using pyproject.toml config
  And tests run successfully

Scenario: Reproducible builds via lockfile
  Given pyproject.toml defines dependencies
  When I run "uv lock"
  Then uv.lock is generated with pinned versions
  And subsequent "uv sync" uses exact versions from lockfile

Scenario: Python version enforcement
  Given pyproject.toml has requires-python = ">=3.13"
  When I try to sync with Python < 3.13
  Then uv reports a Python version constraint error
  And installation is blocked

Scenario: Dev dependencies separated
  Given pyproject.toml has [project.optional-dependencies.dev]
  When I run "uv sync"
  Then both runtime and dev dependencies are installed
  And dev deps are clearly separated in pyproject.toml
```

---

## 3. Requirements

### Must Have
- [ ] Create `pyproject.toml` with `[project]` section (name, version, description)
- [ ] Set `requires-python = ">=3.13"`
- [ ] Add `[project.dependencies]` with runtime deps
- [ ] Add `[project.optional-dependencies.dev]` with test deps
- [ ] Add `[tool.pytest.ini_options]` for test config
- [ ] Generate `uv.lock` lockfile
- [ ] Remove `requirements.txt`
- [ ] Update `.gitignore` to include `venv/` pattern
- [ ] Verify `uv sync` works
- [ ] Verify `uv run pytest` works

### Should Have
- [ ] Add `[tool.uv]` section if beneficial

### Won't Have
- Changing the virtual environment location
- Updating slash commands (separate feature)

---

## 4. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| `uv` is installed on dev machines | Tooling | Standard for modern Python dev |
| Python 3.13+ is available | Architecture | Matches `.python-version` |
| Existing `.venv/` can be recreated | Architecture | `uv sync` will handle this |
| All current deps support Python 3.13 | Library | Likely true for modern versions |

---

## 5. Dependencies to Migrate

**Current `requirements.txt`:**

| Package | Version | Category |
|---------|---------|----------|
| fastapi | >=0.100.0 | Runtime |
| pydantic | >=2.0 | Runtime |
| uvicorn | >=0.32.0 | Runtime |
| anthropic | >=0.40.0 | Runtime |
| python-dotenv | >=1.0.0 | Runtime |
| weasyprint | >=62.0 | Runtime |
| jinja2 | >=3.1.0 | Runtime |
| pytest | >=8.0.0 | Dev |
| pytest-asyncio | >=0.24.0 | Dev |
| httpx | >=0.27.0 | Dev |

---

## 6. Open Questions

- None. Scope is well-defined.

---

*Next: /v4-verify-analysis (no UI changes)*
