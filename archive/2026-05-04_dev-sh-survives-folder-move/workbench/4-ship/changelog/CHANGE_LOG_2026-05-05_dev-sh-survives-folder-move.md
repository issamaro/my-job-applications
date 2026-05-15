# CHANGE_LOG — dev.sh survives a moved project folder

**feature:** dev-sh-survives-folder-move  
**date:** 2026-05-05  
**commit_base:** HEAD  
**total_files:** 3  
**total_additions:** +11  
**total_deletions:** −6

## Files by category

### Docs

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| README.md | M | +9 | −3 |

### Config

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| PROJECT_CHECKS.md | M | +1 | −2 |

### Other

| file | change_type | +lines | −lines |
|------|-------------|--------|--------|
| dev.sh | M | +1 | −1 |

## Scope drift

**Expected files (from IMPL_PLAN):**
- `dev.sh` (modify) ✓
- `README.md` (modify, two sections) ✓

**Additional files modified:**
- `PROJECT_CHECKS.md` — **IN_SCOPE_EXTENSION** (parity fix, line 156). User note: fixes the same `uv run uvicorn` → `uv run python -m uvicorn` pattern flagged by plan-reviewer as MINOR #2, applied consistently to manual-setup documentation path. Consistent with scope-IN ("manual-setup path") and aligns with README changes. Not drift; expected extension.

**Omitted files:**
- None. All planned files modified.

**Drift status:** None.

## Sensitive-area changes

| area | file | change |
|------|------|--------|
| setup/venv | dev.sh | Changed invocation from `uv run uvicorn` to `uv run python -m uvicorn` (bypasses broken shim on folder move) |
| setup/venv | README.md | Updated troubleshooting §6 entry to document auto-heal via Python module invocation |
| setup/manual | PROJECT_CHECKS.md | Synchronized manual-setup example with dev.sh pattern |

All changes are fixes to the venv relocation issue, not security or auth sensitive. Pattern change is documented and rationale is in IMPL_PLAN (pyvenv.cfg's `home =` is external to project; `python -m` resolves through it correctly after move).

## Suggested commit subject

```
fix: uvicorn survives project folder move via python -m invocation
```

---

*Workbench artifacts acknowledged:* `workbench/2-plan/design/IMPL_PLAN_2026-05-05_dev-sh-survives-folder-move.md`, `workbench/2-plan/research/uv-venv-relocation.md` (planning phase, no drift).
