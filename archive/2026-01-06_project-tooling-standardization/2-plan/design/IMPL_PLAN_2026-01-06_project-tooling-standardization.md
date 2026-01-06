# Implementation Plan: Project Tooling Standardization

**Date:** 2026-01-06
**Status:** Draft
**Feature Spec:** FEATURE_SPEC_2026-01-06_project-tooling-standardization.md

---

## 1. Affected Files

### Config/Dependencies
| File | Change | Description |
|------|--------|-------------|
| `pyproject.toml` | Create | New unified config with deps from LIBRARY_NOTES |
| `uv.lock` | Create | Generated lockfile for reproducible builds |
| `requirements.txt` | Delete | Replaced by pyproject.toml + uv.lock |
| `.gitignore` | Modify | Add `venv/` pattern (`.venv/` already present) |

### Backend
| File | Change | Description |
|------|--------|-------------|
| None | - | No code changes required |

### Frontend
| File | Change | Description |
|------|--------|-------------|
| None | - | No code changes required |

### Tests
| File | Change | Description |
|------|--------|-------------|
| None | - | No test file changes (pytest config moves to pyproject.toml) |

---

## 2. Database Changes

```sql
None
```

---

## 3. Implementation Approach

### Config Structure
Single `pyproject.toml` following PEP 621 with uv extensions:
- `[project]` - metadata and runtime dependencies
- `[dependency-groups]` - dev dependencies (modern uv approach, NOT optional-dependencies)
- `[tool.pytest.ini_options]` - test configuration
- `[tool.uv]` - uv-specific settings

### Validation
- `uv sync` validates Python version against `requires-python`
- `uv lock` validates all dependencies resolve correctly

### Error Handling
- If Python < 3.13: uv reports constraint error and blocks installation
- If dependency conflict: uv reports resolution failure

---

## 4. Implementation Order

### Step 1: Create pyproject.toml
```toml
[project]
name = "mycv"
version = "1.0.0"
description = "AI-powered CV/Resume builder"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.100.0",
    "pydantic>=2.0",
    "uvicorn>=0.32.0",
    "anthropic>=0.40.0",
    "python-dotenv>=1.0.0",
    "weasyprint>=62.0",
    "jinja2>=3.1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.uv]
default-groups = ["dev"]
```

### Step 2: Update .gitignore
Add `venv/` to Python section (`.venv/` already present on line 2).

### Step 3: Generate lockfile
```bash
uv lock
```
This creates `uv.lock` with pinned versions.

### Step 4: Verify installation
```bash
uv sync
```
This installs all dependencies and creates/updates venv.

### Step 5: Verify tests run
```bash
uv run pytest
```
Confirms pytest config works from pyproject.toml.

### Step 6: Remove requirements.txt
```bash
rm requirements.txt
```

---

## 5. Risks

| Risk | L | I | Mitigation |
|------|---|---|------------|
| uv not installed on dev machine | Low | Low | Document in README, easy to install |
| Dependency resolution differs from pip | Low | Med | Test thoroughly before removing requirements.txt |
| Existing .venv incompatible | Low | Low | `uv sync` recreates cleanly |

---

## 6. pyproject.toml Full Content

```toml
[project]
name = "mycv"
version = "1.0.0"
description = "AI-powered CV/Resume builder"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.100.0",
    "pydantic>=2.0",
    "uvicorn>=0.32.0",
    "anthropic>=0.40.0",
    "python-dotenv>=1.0.0",
    "weasyprint>=62.0",
    "jinja2>=3.1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.uv]
default-groups = ["dev"]
```

---

*Next: /v4-checklist*
