# Feature Spec: Documentation Alignment

**Date:** 2026-01-06
**Source:** backlog/refined/documentation-alignment.md
**Status:** Draft

---

## 1. Problem Statement

### User Request
> Fix documentation that references incorrect paths and outdated setup procedures. `PROJECT_CHECKS.md` consistently references `venv/` but the actual virtual environment is `.venv/`.

### Pain Point
Developers following `PROJECT_CHECKS.md` encounter failed commands because the documentation references `venv/` while the actual virtual environment is at `.venv/`. This causes confusion and wasted time troubleshooting what appears to be a setup issue.

### User Persona
- **Primary:** New developers onboarding to the project
- **Secondary:** Existing developers following documented validation procedures

---

## 2. BDD Scenarios

```gherkin
Feature: Accurate Documentation Paths
  As a developer
  I want documentation commands to reference correct paths
  So that I can copy-paste commands and have them work immediately

Scenario: Quick Validation command works
  Given I have cloned the repository
  And I have set up my environment following standard conventions
  When I copy-paste the Quick Validation command from PROJECT_CHECKS.md
  Then the command executes successfully
  And I see "All checks passed" output

Scenario: Environment setup check works
  Given I am verifying my environment setup
  When I run the venv existence check from PROJECT_CHECKS.md
  Then it correctly identifies if .venv exists or not
  And provides accurate instructions if missing

Scenario: CI/Pre-commit script works
  Given I want to run the pre-commit validation
  When I execute the validation commands from PROJECT_CHECKS.md
  Then all commands execute using the correct .venv path
  And the validation completes successfully

Scenario: Environment Setup section exists
  Given I am a new developer
  When I read PROJECT_CHECKS.md
  Then I find an Environment Setup section
  And it documents the expected Python version (3.13)
  And it documents the expected Node version (20)
  And it explains how to create the virtual environment
```

---

## 3. Requirements

### Must Have
- [ ] Change all `venv/` references to `.venv/` in PROJECT_CHECKS.md
- [ ] Update line 12: `source venv/bin/activate` → `source .venv/bin/activate`
- [ ] Update line 28-29: `test -d venv` → `test -d .venv`
- [ ] Update line 32, 48, 73, 123, 215: all `source venv/bin/activate` references
- [ ] Update line 235: fix pip install path reference in troubleshooting
- [ ] Add Environment Setup section documenting:
  - Expected Python version: 3.13 (from `.python-version`)
  - Expected Node version: 20 (from `.nvmrc`)
  - How to create virtual environment with correct name
  - How to verify setup is correct

### Should Have
- [ ] Verify dev.sh comments match actual behavior (confirmed: already correct)

### Won't Have
- Creating a separate README.md file
- Documenting slash command usage
- Creating automated setup scripts
- CI/CD configuration

---

## 4. Assumptions

| Assumption | Category | Notes |
|------------|----------|-------|
| `.venv/` is the canonical location | Architecture | Confirmed: dev.sh uses `.venv/`, .gitignore has `.venv/` |
| Python 3.13 is required | Environment | From `.python-version` |
| Node 20 is required | Environment | From `.nvmrc` |
| No existing Environment Setup section | Documentation | Need to add one |

---

## 5. Open Questions

None - scope is clear from refined feature.

---

## 6. Files to Modify

| File | Changes |
|------|---------|
| `PROJECT_CHECKS.md` | Update all `venv/` → `.venv/`, add Environment Setup section |

---

## 7. Scope Verification

**In Scope (from SCOPED_FEATURE):**
- Update all `venv/` references ✓
- Verify dev.sh comments ✓ (already correct)
- Add Environment Setup section ✓

**Out of Scope (from SCOPED_FEATURE):**
- Creating separate README.md
- Documenting slash command usage
- Creating automated setup scripts
- CI/CD configuration

---

*Next: /v4-verify-analysis (no UI changes)*
