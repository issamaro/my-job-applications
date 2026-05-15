# IMPL_PLAN — dev.sh survives a moved project folder

- **slug:** `dev-sh-survives-folder-move`
- **date:** 2026-05-05
- **ceremony_level:** S (light plan, no UX, single library)
- **library notes:** `workbench-v6/2-plan/research/uv-venv-relocation.md`

## Verified root cause

Two file types live under `.venv/bin/`:

| File | Type | Survives `mv` of project? |
|---|---|---|
| `.venv/bin/python`, `.venv/bin/python3` | Symlink → `~/.local/share/uv/python/.../python3.13` | **Yes** — target is outside project. |
| `.venv/bin/uvicorn` (and other console-script shims) | 431-byte text file with absolute `/Users/.../.venv/bin/python3` baked into the shebang block | **No** — fails with `Failed to spawn: uvicorn / No such file or directory (os error 2)`. |

`pyvenv.cfg`'s `home =` line also points outside the project, so `uv run` itself resolves Python correctly after a move; only the shim launcher in `.venv/bin/uvicorn` is broken.

## Approach chosen — B (bypass the shim)

`uv run python -m uvicorn main:app …` resolves uvicorn through Python's import system. It uses the still-valid `.venv/bin/python` symlink and never touches the broken shim. Zero state to maintain, no recreation cost, no probe needed.

### Why not A or C

- **A (detect + recreate venv every run)** wastes cycles on the steady-state path and adds branching for a problem that B eliminates outright. Violates success criterion #2 ("does not unconditionally rebuild").
- **C (B + probe-and-heal safety net)** addresses a different failure mode (uv-managed Python interpreter pruned out from under the symlink). That is rarer than venv relocation and surfaces clearly via `uv sync`'s own error output. Adding a probe adds two `uv` invocations to every dev.sh start for an edge case the manual fallback already covers. Documented in README §6 instead.

### What B does NOT cover (and how we cover it)

- **Pruned uv Python interpreter** → `uv sync` already runs first; if Python is missing, `uv sync` errors loudly (and the existing `uv sync --quiet 2>/dev/null || uv sync` re-run shows the noise).
- **Shim-based tools other than uvicorn** → not used by `dev.sh` today. If we ever add one, prefer `uv run python -m <tool>` for the same reason.

## File-by-file plan

### 1. `dev.sh` (modify, 1 line)

**Location:** line 67.

**Before:**
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
```

**After:**
```bash
uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
```

Lean-code: no new function, no new abbreviation, no new comment. The change is a one-token substitution on the existing line.

No header changes — `dev.sh` is not a Lean-Code-managed source file (it has its own ASCII-banner header convention, not the BSD-3 two-line). Don't impose the lean header on shell scripts that already have an established style.

### 2. `README.md` §6 entry (modify, replace one paragraph)

**Location:** lines 85–86.

**Before:**
```
**`uvicorn: command not found` after I moved the project folder.**
Run `uv sync` once, then `./dev.sh` again. This rewrite uses `uv run uvicorn` so the moved-folder case shouldn't happen — if it does, please file an issue.
```

**After:**
```
**`Failed to spawn: uvicorn` (or `uvicorn: command not found`) after I moved the project folder.**
`dev.sh` launches uvicorn through `uv run python -m uvicorn`, which bypasses the venv shim that breaks on a folder move, so this case is handled automatically. If you still see this error (rare — usually means the uv-managed Python was uninstalled separately), recover with:

```bash
rm -rf .venv && uv sync
```

Then `./dev.sh` again.
```

### 3. `README.md` "Manual setup → Run" section (modify, 1 line)

**Location:** line 167.

**Before:** `uv run uvicorn main:app --reload`
**After:** `uv run python -m uvicorn main:app --reload`

Reason: scope-IN says "and/or setup.sh" and the manual path; the manual instructions should match dev.sh so a developer who copy-pastes from §"Run" doesn't reintroduce the bug.

### 4. Regression check (manual checklist item, no new file)

A scripted regression for "actually move the folder, run dev.sh, hit localhost:8000" requires either a tmpdir copy of the whole project or a docker-style isolation harness — both overkill for an S feature. Documented as a manual inspector checklist item:

- After running `dev.sh` once successfully, simulate the bug by writing a known-bad path into `.venv/bin/uvicorn`'s shebang, then re-run `dev.sh` and confirm uvicorn still starts and `curl http://localhost:8000/` returns 200.

(The existing pytest suite re-runs in test phase and catches any regression in app code. No new pytest is added — there is nothing python-side to assert.)

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `uv run python -m uvicorn` flag handling differs subtly from the shim invocation (e.g., `--reload` watcher arg passing) | Low — `python -m` is the documented uvicorn entry point and accepts identical CLI args (uvicorn's CLI is defined in `uvicorn.__main__`) | Manual smoke during inspect: confirm `--reload` still picks up file edits, port still 8000. |
| User on uv < 0.4 where `uv run python -m` semantics differ | Very low — repo pins `uv = 0.9.8` via `pyvenv.cfg`; `setup.sh` brews latest | None needed; setup.sh enforces brew uv. |
| Future contributor reintroduces `uv run uvicorn` in a new script | Low | README §6 entry now teaches the correct pattern; no project-level lint added (out of scope). |

## Test plan

- **Unit/integration:** existing `uv run pytest` suite (no new tests) — must remain green.
- **Manual regression:**
  1. From a clean checkout, run `./dev.sh`; confirm `curl -s http://localhost:8000/ -o /dev/null -w '%{http_code}'` returns `200`. Stop.
  2. Edit `.venv/bin/uvicorn`'s shebang to point at `/nonexistent/python3` (simulates the post-`mv` state without actually moving the folder).
  3. Re-run `./dev.sh`; confirm uvicorn still starts and curl still returns `200`.
  4. Restore the shim by `rm -rf .venv && uv sync` (clean up the test artifact).

## Out-of-scope confirmed

- Cross-shell support, replacing uv, app-level changes, auto-detecting Google Drive / iCloud relocations as a separate class — all explicitly OUT per refined spec, no creep here.
