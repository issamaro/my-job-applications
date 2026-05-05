# uv venv relocation — research notes

library: uv (Astral)
resolved_id: /llmstxt/astral_sh_uv_llms_txt
version_constraint: uv 0.9.8
runtime_constraint: uv 0.9.x
queried: 2026-05-05

---

## Q1 — Does `uv sync` rewrite broken shims after the project is `mv`'d?

**Answer: No. `uv sync` does NOT automatically detect or repair a relocated venv.**

The docs describe `uv sync` solely as: "synchronizes the current project's dependencies with the virtual environment based on the lockfile." There is no documented behavior that reads `pyvenv.cfg`, detects absolute-path drift in shims, or rewrites entrypoints.

The `--relocatable` flag on `uv venv` is the only documented mechanism for making shims path-safe:

> "Make the virtual environment relocatable. A relocatable virtual environment can be moved around and redistributed without invalidating its associated entrypoint and activation scripts. Note that this can only be guaranteed for standard `console_scripts` and `gui_scripts`."
> — docs.astral.sh/uv/reference/cli (uv venv --relocatable)

Implication: a venv created **without** `--relocatable` (the default) bakes absolute paths into shim headers. Moving the project directory breaks those shims. `uv sync` will install/remove packages against that venv but will **leave broken shims in place**.

The only documented heal path is: `rm -rf .venv && uv sync` (or `uv venv` which "removes and replaces" any existing env at the target path, then `uv sync`).

---

## Q2 — Does `uv run python -m uvicorn` bypass the broken shim?

**Answer: Yes, with high confidence — but the guarantee is implicit, not explicitly stated for this scenario.**

The docs state:

> "`uv run` ensures that the project environment is up-to-date before executing the command."
> — docs.astral.sh/uv/concepts/projects/run

> "Before each execution, `uv run` ensures that your lockfile is synchronized with `pyproject.toml` and that your environment matches the lockfile."
> — docs.astral.sh/uv/guides/projects

`uv run python -m uvicorn` resolves via two independent mechanisms:
1. `uv run` locates `.venv/bin/python` (the interpreter binary, not a shim — it is a real symlink or copy set at venv creation time).
2. `python -m uvicorn` then resolves `uvicorn` through Python's import system (`sys.path`), not through any shim file.

The broken shim at `.venv/bin/uvicorn` is **never consulted**. This approach is therefore safe for a relocated project as long as the Python interpreter symlink itself is intact (it targets the system/managed Python, not an absolute path into the old project tree).

The `-m` / `--module` flag is documented explicitly:

> "`--module` *module*, `-m` — Run a Python module. Equivalent to `python -m <module>`."
> — docs.astral.sh/uv/reference/cli

---

## Q3 — Is there a documented command to explicitly heal a relocated venv?

**Answer: No single "heal" command exists. The documented pattern is recreate.**

`uv venv [PATH]` docs state:

> "If a virtual environment exists at the target path, it will be removed and a new, empty virtual environment will be created."

So the correct two-step is:

```sh
uv venv          # removes .venv, creates fresh empty one
uv sync          # populates from lockfile
```

Or equivalently (since `uv sync` will recreate the venv if absent):

```sh
rm -rf .venv && uv sync
```

There is no `--reload`, `--repair`, or `--rewrite-shims` option documented anywhere.

---

## Q4 — Is there a reliable uv probe to distinguish "moved venv" from "missing Python"?

**Answer: No documented probe specifically distinguishes relocation from other failures.**

Available probes and what they actually test:

| Probe | What it tests | Distinguishes relocation? |
|---|---|---|
| `uv python find` | Finds a Python executable (prefers `.venv`) | No — succeeds if `.venv/bin/python` symlink resolves |
| `uv run python -c 'pass'` (exit code) | Full sync + interpreter execution | Partial — fails if interpreter is broken, but also fails for network/lock issues |
| `uv pip check` | Missing/conflicting deps in active env | No — does not check shim paths |

**Practical probe for `dev.sh`:** The cheapest reliable signal for "venv is usable" is:

```sh
uv run --no-sync python -c 'import uvicorn' 2>/dev/null
```

- `--no-sync` skips the lock check (fast).
- If exit code is non-zero, the interpreter or `uvicorn` package is broken/absent → trigger `rm -rf .venv && uv sync`.
- This does NOT distinguish cause (relocation vs. missing Python vs. corrupt install), but for `dev.sh` purposes the recovery action is identical in all cases.

`uv run` without `--no-sync` would also work but adds a lockfile staleness check on every invocation — acceptable overhead if consistency matters more than speed.

---

## Recommended `dev.sh` approach (confirmed safe by docs)

1. Replace `uv run uvicorn` with `uv run python -m uvicorn` — bypasses shim entirely (Q2 confirmed).
2. Pre-flight probe: `uv run --no-sync python -c 'import uvicorn'`; on failure, `rm -rf .venv && uv sync` then retry.
3. Do NOT rely on `uv sync` alone to repair a moved venv — it will not rewrite shims (Q1 confirmed).

---

## Deprecated to avoid

none documented for venv/run commands in the queried version.

## Open questions

- Whether `uv run` re-resolves `.venv/bin/python` via the real binary or via a shim is not explicitly stated in the docs. Empirical testing on a moved project is advisable before shipping.
- Whether `uv 0.9.x` introduced any behavioral change to shim rewriting vs. earlier versions — changelog not queried; docs don't call out version-specific changes here.
