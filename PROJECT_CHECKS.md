# Project Validation Checks: MyCV-2

**Purpose:** Reusable validation checks for verifying project health
**Usage:** Run before shipping features, after major changes, or to verify setup

---

## Quick Validation (All Checks)

```bash
# Run all checks in sequence
source venv/bin/activate && \
python -c "from main import app; print('Backend: OK')" && \
python -m pytest -v && \
npm run build && \
echo "All checks passed"
```

---

## Individual Checks

### 1. Environment Setup

**When to run:** After cloning, after changing dependencies

```bash
# Check Python venv exists
test -d venv && echo "venv: OK" || echo "venv: MISSING - run 'python3 -m venv venv'"

# Check dependencies installed
source venv/bin/activate
python -c "import fastapi, pydantic, uvicorn; print('Python deps: OK')"

# Check Node dependencies
npm list --depth=0 | head -10
```

**Expected output:** No missing dependencies

---

### 2. Backend Health

**When to run:** Before any backend work

```bash
source venv/bin/activate

# Test app imports (catches import errors, circular deps)
python -c "from main import app; print('FastAPI app: OK')"

# Test database can initialize
python -c "from database import init_db; init_db(); print('Database: OK')"

# Test all routes import
python -c "
from routes import personal_info, work_experiences, education
from routes import skills, projects, resumes, job_descriptions
print('All routes: OK')
"
```

**Expected output:** All "OK" messages, no exceptions

---

### 3. Test Suite

**When to run:** Before every commit, after any code change

```bash
source venv/bin/activate

# Full test run with verbose output
python -m pytest -v

# Quick check (stop on first failure)
python -m pytest -x

# Run specific test file
python -m pytest tests/test_resumes.py -v

# Run tests matching pattern
python -m pytest -k "test_generate" -v
```

**Expected output:** All tests pass (101 as of 2026-01-04)

---

### 4. Frontend Build

**When to run:** Before shipping UI changes

```bash
# Full build (SCSS + Rollup)
npm run build

# Verify output files exist
ls -la public/build/bundle.js public/build/global.css

# Check bundle size (should be < 500KB)
wc -c public/build/bundle.js
```

**Expected output:**
- "created public/build/bundle.js" message
- Both files exist
- Circular dep warnings from Svelte internals (safe to ignore)

---

### 5. Development Server

**When to run:** Manual testing, UI verification

```bash
# Start full stack
./dev.sh

# Or manually:
source venv/bin/activate
uvicorn main:app --reload &
npm run watch:css &
npx rollup -c -w
```

**Verify:**
- http://localhost:8000 - Main app loads
- http://localhost:8000/docs - Swagger UI works
- http://localhost:8000/api/personal-info - API responds

---

### 6. API Smoke Test

**When to run:** After API changes

```bash
# Start server first, then:

# Personal info endpoint
curl -s http://localhost:8000/api/personal-info | head -c 100

# Skills list
curl -s http://localhost:8000/api/skills

# Resumes list
curl -s http://localhost:8000/api/resumes

# Job descriptions list
curl -s http://localhost:8000/api/job-descriptions
```

**Expected output:** JSON responses (may be empty arrays)

---

### 7. PDF Generation (System Deps)

**When to run:** After environment changes, on new machines

```bash
# Check WeasyPrint can import
source venv/bin/activate
python -c "from weasyprint import HTML; print('WeasyPrint: OK')"

# If fails on macOS:
brew list pango || brew install pango
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"
```

**Expected output:** "WeasyPrint: OK"

---

### 8. LLM Integration (Optional)

**When to run:** When testing AI features

```bash
# Check API key is set
test -n "$ANTHROPIC_API_KEY" && echo "API key: SET" || echo "API key: MISSING"

# Or check .env file
grep -q ANTHROPIC_API_KEY .env && echo ".env has key" || echo ".env missing key"
```

**Note:** API key not required for non-AI features

---

## CI/Pre-commit Checklist

For automated validation before commits:

```bash
#!/bin/bash
# save as: scripts/validate.sh

set -e  # Exit on first failure

echo "=== MyCV-2 Validation ==="

echo "1. Activating venv..."
source venv/bin/activate

echo "2. Checking imports..."
python -c "from main import app"

echo "3. Running tests..."
python -m pytest -q

echo "4. Building frontend..."
npm run build

echo "=== All checks passed ==="
```

---

## Failure Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | venv not active or deps missing | `source venv/bin/activate && pip install -r requirements.txt` |
| `WeasyPrint import error` | Missing system library | `brew install pango && export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"` |
| `npm ERR! engine` | Wrong Node version | `nvm use 20` |
| Tests fail with DB errors | Stale test DB | Delete `test_*.db` files |
| Rollup circular dep warnings | Svelte internals | Safe to ignore if build succeeds |

---

## Health Indicators

| Metric | Healthy Range | Current |
|--------|---------------|---------|
| Test count | >80 | 101 |
| Test duration | <30s | 7.86s |
| Bundle size | <500KB | ~250KB |
| Build time | <5s | ~1s |

---

*Validation checks extracted from retrospectives and project experience*
