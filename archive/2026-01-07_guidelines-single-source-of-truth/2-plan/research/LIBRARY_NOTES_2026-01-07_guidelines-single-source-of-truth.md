# Library Notes: Guidelines Single Source of Truth

**Date:** 2026-01-07
**Purpose:** Document modern uv command syntax for skill updates

---

## 0. Ecosystem Prerequisites

### Runtime
| Runtime | Version | Reason |
|---------|---------|--------|
| Python | 3.13 | Current project version (verified in pyproject.toml) |
| uv | 0.9.8+ | Modern uv with project management features |

### Tooling
| Tool | Purpose | Verify |
|------|---------|--------|
| uv | Python version + venv + packages + project management | `uv --version` |

### Setup Commands (Modern uv - NO pip)
```bash
# Install Python version
uv python install 3.13

# Create venv (auto-detects Python from pyproject.toml)
uv venv

# Activate venv
source .venv/bin/activate

# Sync dependencies from pyproject.toml + uv.lock
uv sync

# Sync with all extras and dev dependencies
uv sync --all-extras --dev
```

---

## 1. uv (Package/Project Manager)

**Version Constraint:** `uv>=0.4.0` (project management features)
**Installed:** `uv 0.9.8`

### Correct Patterns (Modern uv)

| Task | Command | Notes |
|------|---------|-------|
| Install all dependencies | `uv sync` | Syncs from pyproject.toml + uv.lock |
| Install with dev deps | `uv sync --dev` | Includes dev dependency group |
| Install locked versions | `uv sync --locked` | Fails if lockfile out of date |
| Add a package | `uv add [package]` | Updates pyproject.toml + uv.lock |
| Add dev dependency | `uv add --dev [package]` | Adds to dev group |
| View dependency tree | `uv tree` | Shows all project dependencies |
| Check specific package | `uv tree --package [name]` | Shows package and its deps |
| Check outdated packages | `uv tree --outdated` | Shows latest available versions |
| Run a command | `uv run [command]` | Runs in project environment |

### Deprecated (Avoid) - NEVER USE

| Old Pattern | Why Avoid | Modern Alternative |
|-------------|-----------|-------------------|
| `uv pip install -r requirements.txt` | Legacy pip interface | `uv sync` |
| `uv pip install [package]` | Legacy pip interface | `uv add [package]` |
| `uv pip list` | Legacy pip interface | `uv tree` |
| `uv pip show [package]` | Legacy pip interface | `uv tree --package [name]` |
| `uv pip freeze` | Legacy pip interface | `uv export` (if needed) |
| `pip install` | Not uv-managed | `uv add` or `uv sync` |

### Code Examples

```bash
# Check if a package is installed (CORRECT)
uv tree --package pytest
# Output shows pytest and its dependencies if installed

# Check all project dependencies (CORRECT)
uv tree --depth 1
# Output shows direct dependencies only

# Install project dependencies (CORRECT)
uv sync

# Install with locked versions for CI (CORRECT)
uv sync --locked --all-extras --dev
```

### Key Behavioral Notes

1. **`uv sync` requires pyproject.toml** - If missing, command fails
2. **`uv tree` requires pyproject.toml** - Shows project dependency tree
3. **No fallback to pip** - If pyproject.toml missing, ask user
4. **Lockfile auto-created** - `uv sync` creates uv.lock if missing

---

## 2. Handling Missing pyproject.toml

**Policy:** Ask user, do not fallback to pip

```markdown
If pyproject.toml is missing:

1. STOP - do not use pip commands
2. Ask user: "This project doesn't have pyproject.toml. Would you like me to:
   a) Create pyproject.toml with `uv init`
   b) Help you set up the project structure
   c) Proceed without dependency management"
3. Wait for user response before continuing
```

---

## 3. Command Reference Summary

### For v4-* Skill Updates

| Skill | Old Command | New Command |
|-------|-------------|-------------|
| v4-implement | `uv pip install -r requirements.txt` | `uv sync` |
| v4-implement | `uv pip show [pkg]` | `uv tree --package [pkg]` |
| v4-test | `uv pip show pytest` | `uv tree --package pytest` |
| v4-validate | `uv pip show [pkg]` | `uv tree --package [pkg]` |
| v4-scaffold | `uv pip install -r requirements.txt` | `uv sync` |
| v4-research | `uv pip install -r requirements.txt` | `uv sync` |
| v4-ecosystem | Check for pyproject.toml | Ask user if missing |

---

## Dependencies Summary

**No new dependencies required** - This feature updates documentation/skill files only.

The project already uses modern uv (0.9.8) with pyproject.toml.

---

*Reference for /v4-design and /v4-checklist*
