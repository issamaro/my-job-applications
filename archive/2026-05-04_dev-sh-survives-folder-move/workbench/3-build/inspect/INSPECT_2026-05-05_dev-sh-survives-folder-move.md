feature: dev-sh-survives-folder-move
date: 2026-05-05
status: READY
playwright: skipped

---

## Inspector notes

No UI surface is touched by this feature (ceremony_level S, backend launch fix only). Playwright smoke was intentionally skipped — there is no new UI state to exercise and running the suite would not verify the venv-shim bypass.

---

## Static verification (pre-user)

All three file changes were confirmed present in the working tree before this artifact was written.

| File | Location | Expected text | Observed |
|---|---|---|---|
| `dev.sh` | line 67 | `uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &` | PASS |
| `README.md` §6 | lines 85–86 | title starts `Failed to spawn: uvicorn` + body references `uv run python -m uvicorn` + recovery snippet `rm -rf .venv && uv sync` | PASS |
| `README.md` Manual setup → Run | line 173 | `uv run python -m uvicorn main:app --reload` | PASS |

---

## Manual checklist — regression sequence

Group A: Functional regression (4 steps — must be run in order)

- Step 1: In the project root, run `./dev.sh`. Once it settles, run `curl -s http://localhost:8000/ -o /dev/null -w '%{http_code}'` in a second terminal and confirm it prints `200`. Then stop `dev.sh` (Ctrl-C or kill the PID).
- Step 2: Open `.venv/bin/uvicorn` in any editor and change the shebang line (first line, starts with `#!/`) to `#!/nonexistent/python3`. Save. Do NOT run `uv sync` after this — the corrupted shim must stay in place.
- Step 3: Re-run `./dev.sh`. Confirm uvicorn starts without error and `curl -s http://localhost:8000/ -o /dev/null -w '%{http_code}'` still returns `200`. This proves the shim is bypassed.
- Step 4: Run `rm -rf .venv && uv sync` to restore the clean state. Confirm the command exits 0 and `.venv/bin/python` is recreated (`ls .venv/bin/python`).

Group B: Documentation checks (3 items — read-only, no server needed)

- Doc 1: Open `README.md` and find §6 (Troubleshooting). Confirm the entry title reads: `Failed to spawn: uvicorn` (or `uvicorn: command not found`) after I moved the project folder. Confirm the body mentions `uv run python -m uvicorn` and does NOT say "shouldn't happen — please file an issue".
- Doc 2: In the same §6 entry, confirm the recovery snippet is exactly: `rm -rf .venv && uv sync` followed by "Then `./dev.sh` again."
- Doc 3: Open `README.md`, find the "Manual setup → Run" section. Confirm the run command reads `uv run python -m uvicorn main:app --reload` (not `uv run uvicorn`).

---

## Decisions

none — parent collects user verdict
