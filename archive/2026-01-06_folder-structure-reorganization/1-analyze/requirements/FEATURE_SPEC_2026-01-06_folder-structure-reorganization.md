# Feature Spec: Folder Structure Reorganization

**Date:** 2026-01-06
**Source:** backlog/refined/folder-structure-reorganization.md
**Status:** Draft

---

## 1. Problem Statement

### User Request
> "I don't like the current structure of the project. Give relevant alternatives."

### Pain Point
The user perceives the project structure as having:
- Too many files at the root level (~20 files)
- Potential dead/unnecessary files
- Unclear grouping (backend vs frontend vs docs)

However, **analysis reveals the codebase is actually well-structured** with no dead files detected. The real issues are:
1. Root-level clutter (database.py, schemas.py, dev.sh mixed together)
2. `src/` name doesn't clarify it contains frontend code
3. Documentation files mixed with application code at root

### User Persona
Developer/maintainer who wants clear mental model of where things belong.

---

## 2. BDD Scenarios

```gherkin
Feature: Folder Structure Reorganization
  As a developer maintaining this project
  I want a clearer folder organization
  So that I can quickly locate files and understand the architecture

Scenario: Revised Option E implementation (CHOSEN)
  Given user has reviewed thorough risk analysis
  When reorganization is implemented
  Then src/ is renamed to frontend/
  And docs/ directory contains documentation files
  And scripts/ directory contains dev.sh
  And all Python code stays at root (no import changes)
  And methodology folders stay at root
  And tests continue to pass

Scenario: Build configuration updated
  Given src/ has been renamed to frontend/
  When rollup.config.js path is updated
  And package.json sass paths are updated
  Then npm run build succeeds
  And npm run dev succeeds
```

---

## 3. Requirements

### Must Have
- [x] Present current structure analysis to user ✓
- [x] Present viable reorganization alternatives with honest trade-offs ✓
- [x] Get explicit user approval before implementation ✓
- [ ] Rename `src/` → `frontend/`
- [ ] Update `rollup.config.js` path: `src/main.js` → `frontend/main.js`
- [ ] Update `package.json` sass paths (2 places)
- [ ] Create `docs/` directory
- [ ] Move documentation files to `docs/`
- [ ] Create `scripts/` directory
- [ ] Move `dev.sh` to `scripts/`
- [ ] Update `dev.sh` to work from new location
- [ ] Verify `npm run build` works
- [ ] Verify `npm run dev` works
- [ ] Verify Python tests pass

### Should Have
- [ ] Use `git mv` for tracked files to preserve history

### Won't Have
- Moving Python modules (routes/, services/, database.py, schemas.py)
- Moving pyproject.toml (breaks uv)
- Moving templates/ (breaks pdf_generator.py path logic)
- Updating any Python imports
- Changing methodology folders (archive/, backlog/, workbench/)

---

## 4. Risk Analysis (Thorough)

### Python Environment Constraints (CRITICAL)

| Item | Constraint | Why |
|------|------------|-----|
| `pyproject.toml` | MUST stay at root | `uv sync` expects it here; `.venv` created relative to it |
| `.venv/` | MUST stay at root | `dev.sh` expects it; IDE Python config |
| `routes/` | MUST stay at root | All Python imports are root-relative |
| `services/` | MUST stay at root | Imports from routes/, resume_generator.py |
| `database.py` | MUST stay at root | Imported by routes/, services/ |
| `schemas.py` | MUST stay at root | Imported by routes/, services/ |
| `main.py` | MUST stay at root | `uvicorn main:app` command |
| `templates/` | MUST stay at root | `pdf_generator.py` uses `Path(__file__).parent.parent / "templates"` |
| `tests/` | MUST stay at root | `pytest.ini_options.testpaths = ["tests"]` |

**Moving any of the above would require updating 20+ Python files and risk breaking the entire backend.**

### Frontend Changes (Low Risk)

| File | Change | Risk |
|------|--------|------|
| `rollup.config.js:10` | `src/main.js` → `frontend/main.js` | Low - single path |
| `package.json:11` | `src/styles/main.scss` → `frontend/styles/main.scss` | Low |
| `package.json:13` | `src/styles/main.scss` → `frontend/styles/main.scss` | Low |

### Script Changes (Low Risk)

| File | Change | Risk |
|------|--------|------|
| `dev.sh` | Move to `scripts/dev.sh` | Low - uses `SCRIPT_DIR` logic |
| `dev.sh` | Update path logic for new location | Low |

---

## 5. Chosen Approach: Revised Option E

### Final Structure
```
MyCV-2/
├── frontend/              # Renamed from src/
│   ├── components/        # 23 Svelte components
│   ├── lib/               # api.js
│   └── styles/            # SCSS architecture
├── routes/                # STAYS AT ROOT
├── services/              # STAYS AT ROOT
├── templates/             # STAYS AT ROOT
├── tests/                 # STAYS AT ROOT
├── main.py                # STAYS AT ROOT
├── database.py            # STAYS AT ROOT
├── schemas.py             # STAYS AT ROOT
├── pyproject.toml         # STAYS AT ROOT
├── package.json           # STAYS AT ROOT (update paths)
├── rollup.config.js       # STAYS AT ROOT (update path)
├── public/                # STAYS AT ROOT
├── docs/                  # NEW
│   ├── CHANGELOG.md
│   ├── PROJECT_CHECKS.md
│   └── RETROSPECTIVE_INSIGHTS.md
├── scripts/               # NEW
│   └── dev.sh
├── workbench/             # STAYS AT ROOT
├── archive/               # STAYS AT ROOT
└── backlog/               # STAYS AT ROOT
```

### Changes Summary

| Category | Items | Files to Update |
|----------|-------|-----------------|
| Rename | `src/` → `frontend/` | 0 (git mv) |
| Config update | rollup.config.js | 1 line |
| Config update | package.json | 2 lines |
| Create dir | `docs/` | 0 |
| Move files | CHANGELOG.md, PROJECT_CHECKS.md, RETROSPECTIVE_INSIGHTS.md | 0 (git mv) |
| Create dir | `scripts/` | 0 |
| Move + update | dev.sh → scripts/dev.sh | ~5 lines |

**Total files requiring code changes: 3**
**Risk level: Low**

---

## 6. Files to Move

### To `docs/`:
- `CHANGELOG.md`
- `PROJECT_CHECKS.md`
- `RETROSPECTIVE_INSIGHTS.md`

### To `scripts/`:
- `dev.sh`

### Rename:
- `src/` → `frontend/`

---

## 7. Verification Checklist

After implementation:
- [ ] `npm run build` succeeds (frontend compiles)
- [ ] `npm run build:css` succeeds (SASS compiles)
- [ ] `npm run watch` succeeds (Rollup watches)
- [ ] `npm run watch:css` succeeds (SASS watches)
- [ ] `./scripts/dev.sh` starts all servers
- [ ] `uv sync` works
- [ ] `pytest` passes all tests
- [ ] Application loads at http://localhost:8000

---

*Next: /v4-verify-analysis*
