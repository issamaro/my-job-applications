# Library Notes: Project Tooling Standardization

**Date:** 2026-01-06
**Purpose:** Ecosystem prerequisites and uv syntax reference

---

## 0. Ecosystem Prerequisites

### Runtime
| Runtime | Version | Reason |
|---------|---------|--------|
| Python | >=3.13 | Matches `.python-version`, modern features |

### Tooling
| Tool | Purpose | Verify |
|------|---------|--------|
| uv | Package manager, venv, lockfile | `uv --version` |

### Setup Commands
```bash
# Fresh setup
uv sync

# Run commands in project environment
uv run pytest

# Update lockfile after dependency changes
uv lock
```

---

## uv (astral-sh/uv)

**Source:** context7 `/llmstxt/docs_astral_sh-uv-llms.txt`

### Key Concepts

1. **`uv sync`** - Installs all dependencies (runtime + dev groups by default)
2. **`uv lock`** - Generates/updates `uv.lock` lockfile
3. **`uv run <cmd>`** - Runs command in project environment
4. **`uv add <pkg>`** - Adds dependency to pyproject.toml

### pyproject.toml Structure (Current Best Practice)

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Project description"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.100.0",
    "pydantic>=2.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.uv]
default-groups = ["dev"]
```

### Important: Use `[dependency-groups]` NOT `[project.optional-dependencies]`

The docs show `[dependency-groups]` as the modern approach for dev dependencies:

```toml
# CORRECT (modern uv approach)
[dependency-groups]
dev = [
    "pytest>=8.0.0",
]

# AVOID (old optional-dependencies approach)
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
]
```

The `dev` group is special-cased by uv and installed by default with `uv sync`.

### Commands Reference

| Command | Purpose |
|---------|---------|
| `uv sync` | Install all deps (creates venv if needed) |
| `uv sync --locked` | Install using exact lockfile versions |
| `uv sync --all-extras` | Include all optional extras |
| `uv run pytest` | Run pytest in project env |
| `uv lock` | Generate/update uv.lock |
| `uv add <pkg>` | Add runtime dependency |
| `uv add --dev <pkg>` | Add dev dependency |

### CI/CD Example (GitHub Actions)

```yaml
- name: Install the project
  run: uv sync --locked --all-extras

- name: Run tests
  run: uv run pytest tests
```

---

## pytest Configuration in pyproject.toml

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

---

## Dependencies Summary

**pyproject.toml `[project.dependencies]`:**
```
fastapi>=0.100.0
pydantic>=2.0
uvicorn>=0.32.0
anthropic>=0.40.0
python-dotenv>=1.0.0
weasyprint>=62.0
jinja2>=3.1.0
```

**pyproject.toml `[dependency-groups.dev]`:**
```
pytest>=8.0.0
pytest-asyncio>=0.24.0
httpx>=0.27.0
```

---

*Reference for /v4-design and /v4-implement*
