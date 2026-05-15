feature: dev-sh-survives-folder-move
date: 2026-05-05
total_checkboxes: 18
derived_from: IMPL_PLAN_2026-05-05_dev-sh-survives-folder-move.md, uv-venv-relocation.md, dev-sh-survives-folder-move.md (refined spec)

---

## Section 0 — Ecosystem

- [ ] Runtime version pinned: `.python-version` = `3.13` (verify: `cat .python-version`)  → source: IMPL_PLAN §"Risks" — "repo pins uv 0.9.8 via pyvenv.cfg; setup.sh brews latest"; `.python-version` file = `3.13`
- [ ] `pyproject.toml` requires-python constraint matches pinned version: `>=3.13` present (verify: `grep requires-python pyproject.toml`)  → source: pyproject.toml line 5
- [ ] Virtual environment created and activated (verify: `ls .venv/bin/python`)  → source: uv-venv-relocation.md §Q2 — `.venv/bin/python` must exist as the symlink that `uv run` resolves

---

## Section 1 — Dependencies

- [ ] `uvicorn>=0.32.0` present in `pyproject.toml` (verify: `uv tree --package uvicorn`)  → source: IMPL_PLAN §"File-by-file plan / 1. dev.sh" — command uses `uvicorn main:app`; pyproject.toml line 9
- [ ] `uv` available on PATH at version 0.9.x (verify: `uv --version`)  → source: uv-venv-relocation.md header `version_constraint: uv 0.9.8` and IMPL_PLAN §"Risks" row "User on uv < 0.4…"

---

## Section 2 — Syntax / Patterns

- [ ] `dev.sh` line 67 uses `uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &` (not `uv run uvicorn`)  → source: IMPL_PLAN §"File-by-file plan / 1. dev.sh" Before/After diff
- [ ] `.venv/bin/python` is a symlink targeting a path outside the project tree (verify: `readlink .venv/bin/python`)  → source: uv-venv-relocation.md §Q2 — "uv run locates `.venv/bin/python` (the interpreter binary, not a shim — it is a real symlink or copy set at venv creation time)"
- [ ] `.venv/bin/uvicorn` shim is NOT consulted by the new launch path — confirmed by reading `dev.sh` line 67 and seeing `python -m`  → source: uv-venv-relocation.md §Q2 — "The broken shim at `.venv/bin/uvicorn` is never consulted"

---

## Section 3 — UX

n/a — no UX_DESIGN source (ceremony_level S, no UI changes)

---

## Section 4 — Tests

### Automated

- [ ] Existing `uv run pytest` suite passes without modification (verify: `uv run pytest` exits 0)  → source: IMPL_PLAN §"Test plan" — "existing `uv run pytest` suite (no new tests) — must remain green"

### Manual regression (4-step sequence from IMPL_PLAN §"Test plan")

- [ ] Step 1 — From a clean checkout, run `./dev.sh`; confirm `curl -s http://localhost:8000/ -o /dev/null -w '%{http_code}'` returns `200`; then stop `dev.sh`  → source: IMPL_PLAN §"Test plan" step 1
- [ ] Step 2 — Edit `.venv/bin/uvicorn` shebang line to point at `/nonexistent/python3` (simulates the post-`mv` broken-path state without moving the folder)  → source: IMPL_PLAN §"Test plan" step 2
- [ ] Step 3 — Re-run `./dev.sh`; confirm uvicorn still starts and `curl -s http://localhost:8000/ -o /dev/null -w '%{http_code}'` still returns `200` (the shim is bypassed)  → source: IMPL_PLAN §"Test plan" step 3
- [ ] Step 4 — Clean up the test artifact: `rm -rf .venv && uv sync`  → source: IMPL_PLAN §"Test plan" step 4

### Success-criteria checks (from refined spec)

- [ ] `./dev.sh` exits 0 after a simulated `mv` (shebang corruption, step 2-3 above) with no manual intervention beyond `cd` into the new path  → source: refined spec §"Success criteria" criterion 1
- [ ] `dev.sh` does not unconditionally rebuild the venv on a normal (non-moved) run — `uv sync --quiet` is the only overhead  → source: refined spec §"Success criteria" criterion 2
- [ ] No wall-of-uv-output emitted in the moved-folder path (Approach B never triggers recreation, so this is satisfied by design; verify no new `rm -rf .venv` in `dev.sh`)  → source: refined spec §"Success criteria" criterion 3

---

## Section 5 — Accessibility

n/a — no UX_DESIGN source (no UI changes)

---

## Section 6 — Documentation checks (derived from IMPL_PLAN file-by-file plan)

- [ ] `README.md` lines 85–86: paragraph updated — title now reads `Failed to spawn: uvicorn (or uvicorn: command not found) after I moved the project folder.` and body references `uv run python -m uvicorn` bypass  → source: IMPL_PLAN §"File-by-file plan / 2. README.md §6 entry" After block
- [ ] `README.md` line 167 (Manual setup → Run section): command updated to `uv run python -m uvicorn main:app --reload` (not `uv run uvicorn`)  → source: IMPL_PLAN §"File-by-file plan / 3. README.md 'Manual setup → Run' section"
- [ ] `README.md` §6 recovery snippet present: ` ```bash\nrm -rf .venv && uv sync\n``` ` followed by "Then `./dev.sh` again."  → source: IMPL_PLAN §"File-by-file plan / 2. README.md §6 entry" After block; also uv-venv-relocation.md §Q3 — "correct two-step: rm -rf .venv && uv sync"

---

## Section 7 — Project-specific

n/a — no project-checks.md found at project root
