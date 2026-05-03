---
slug: onboarding-rewrite
date: 2026-05-04
ceremony_level: L
phase: 1-analyze
artifact: FEATURE_SPEC
---

# Feature Spec — Onboarding Rewrite

## Persona

**Non-technical friend on macOS.** Has Homebrew installed. Comfortable copy-pasting commands into Terminal. No prior Python / Node / Git background. Reads the README linearly, will not improvise. If a step fails, they stop and message the maintainer.

## Pain point (today)

The onboarding surface (README + setup.sh + dev.sh) has five concrete first-run defects and one structural defect that, taken together, prevent the maintainer from sharing the project unattended:

1. **URL mismatch.** README step 4 directs the user to `http://localhost:5173`. dev.sh actually serves the app at `http://localhost:8000`. (Vite is not used; rollup-watch builds Svelte assets that FastAPI serves as static files.) The user opens 5173, sees nothing, assumes they broke it.
2. **HTTPS clone with password is dead.** README step 2 uses `git clone https://github.com/issamaro/MyCV-2.git`. GitHub no longer accepts HTTPS password auth. A non-technical user has no `gh auth login` configured and no SSH key.
3. **Wrong repo name everywhere.** README + scripts reference `MyCV-2`. The actual GitHub repo (`git@github.com:issamaro/my-job-applications.git`) is `my-job-applications`. Clone command fails; `cd MyCV-2` fails.
4. **Provider selection does not persist correctly.** setup.sh writes `LLM_PROVIDER` to `~/.zshrc` only when no `LLM_PROVIDER` line exists yet (`if ! grep -q ... ; then ... fi`). A user who runs setup.sh once with Claude, then re-runs choosing Gemini, ends up with `GEMINI_API_KEY` set but `LLM_PROVIDER=claude` still — boot fails with "ANTHROPIC_API_KEY not set".
5. **dev.sh breaks after `mv` of project folder.** dev.sh calls `uvicorn main:app` directly (line 71). After moving the folder, the user runs `uv sync && ./dev.sh`. Activation via `source .venv/bin/activate` (dev.sh line 40) does not consistently put `uvicorn` on PATH because uv-managed venvs may have stale absolute interpreter paths after `mv`. Result: `uvicorn: command not found`.
6. **(Structural)** The three artifacts (README, setup.sh, dev.sh) were authored independently and do not agree about the canonical URL, the canonical repo name, or where env vars live. There is no single source of truth.

## Must-have list

- README and dev.sh agree on the canonical app URL (`http://localhost:8000`).
- README walks the user through GitHub authentication BEFORE the clone step. Method: `gh auth login` (chosen because it ships in Homebrew, requires zero key-management knowledge, and works for both clone + future PRs).
- Every repo-name reference in README and setup.sh says `my-job-applications`. Zero `MyCV-2` mentions in onboarding-path files.
- setup.sh writes the API key AND the matching `LLM_PROVIDER` to a project-local `.env` file (project root). If `.env` already contains either key, setup.sh **updates** it (sed replace), it does not create a duplicate or leave a stale value.
- dev.sh sources `.env` (if present) before launching the backend, so the env vars take effect in the current shell without requiring a terminal restart or shell-rc pollution.
- dev.sh uses `uv run uvicorn ...` instead of `uvicorn ...`, so it works regardless of whether the venv is activated, regardless of where the project folder lives, and survives `mv`.
- A `smoke.sh` script (or equivalent documented checklist) runs the fresh-machine flow end-to-end on macOS and reports pass/fail per criterion.
- `.env` is in `.gitignore` (verify; do not commit secrets).
- Old shell-rc-based key writes are removed from setup.sh (no more polluting `~/.zshrc`).

## Out of scope

- App feature changes (FastAPI routes, Svelte UI, LLM call sites, prompts, DB schema).
- GUI installer (Electron/TUI).
- Mandatory Docker pivot.
- Linux / Windows onboarding (macOS only for this rewrite; Linux is best-effort by virtue of the same scripts).
- Removing the manual-setup section from README (kept for developers).

## BDD scenarios

### Scenario 1 — GitHub auth before clone

```
Given a fresh macOS account with Homebrew installed and no gh CLI configured
When the user follows README sections "Install Git" and "Authenticate to GitHub" linearly
Then `gh auth status` reports an authenticated session
And `gh repo clone issamaro/my-job-applications` succeeds without prompting for a password
And the local directory `my-job-applications/` exists
```

### Scenario 2 — Provider selection persists end-to-end

```
Given a clean checkout with no .env file
When the user runs ./setup.sh and selects "2" (Gemini) and pastes a Gemini API key "AIzaTEST123"
Then the project-root .env contains exactly one line `GEMINI_API_KEY="AIzaTEST123"` and exactly one line `LLM_PROVIDER="gemini"`
And no LLM_PROVIDER or *_API_KEY export was added to ~/.zshrc

Given a checkout where .env already has `LLM_PROVIDER="claude"` and `ANTHROPIC_API_KEY="sk-ant-OLD"`
When the user re-runs ./setup.sh and selects "2" (Gemini) with key "AIzaNEW"
Then .env contains `LLM_PROVIDER="gemini"` (not claude) and `GEMINI_API_KEY="AIzaNEW"`
And the previous ANTHROPIC_API_KEY line is preserved (not deleted) but LLM_PROVIDER is updated in place

Given a .env with LLM_PROVIDER=gemini and a valid GEMINI_API_KEY
When the user runs ./dev.sh
Then the backend boot log does NOT contain "ANTHROPIC_API_KEY environment variable is not set"
And the running provider, queried via /docs or a request, is Gemini
```

### Scenario 3 — Portable launch after mv

```
Given a working install at ~/projects/my-job-applications with .venv populated
When the user runs `mv ~/projects/my-job-applications ~/code/my-job-applications` and then `cd ~/code/my-job-applications && ./dev.sh`
Then dev.sh prints "App running at: http://localhost:8000"
And no line in dev.sh stdout/stderr matches "command not found"
And the backend responds 200 to GET http://localhost:8000/
```

### Scenario 4 — URL agreement

```
Given a fresh checkout
When grep is run on README.md for "localhost:"
Then every match is "localhost:8000" — there are zero "localhost:5173" mentions

Given dev.sh has just printed its banner
When the user opens the URL printed in the banner
Then the page loads (HTTP 200, non-empty body)
And the URL printed equals the URL cited in README step 4
```

### Scenario 5 — Repo name consistency

```
Given the repo root
When `grep -ri "MyCV-2"` is run on README.md and setup.sh
Then there are zero matches in either file

Given README.md
When the clone command in step 2 is extracted
Then it reads `gh repo clone issamaro/my-job-applications` (or `git clone git@github.com:issamaro/my-job-applications.git`)
And the subsequent `cd` line reads `cd my-job-applications`
```

### Scenario 6 — Smoke evidence

```
Given the new ./smoke.sh script
When run on a machine with a populated .env
Then it exits 0
And its stdout contains a checklist where every line begins with "✓" (no "✗" lines)
And the checklist covers: gh auth status, repo path matches my-job-applications, .env has both keys, dev.sh boots, /-endpoint returns 200, no "command not found" in dev.sh log
```

## Success criteria (binary, observable)

| # | Criterion | How verified |
|---|---|---|
| 1 | README is linearly followable end-to-end on fresh macOS | Manual smoke test by a non-developer reader |
| 2 | `gh auth login` walkthrough exists and works | Scenario 1 |
| 3 | Provider + key persist together in `.env` and update on re-run | Scenario 2 (all three paragraphs) |
| 4 | `dev.sh` works from any folder location | Scenario 3 |
| 5 | All repo references say `my-job-applications` (zero `MyCV-2`) in README + setup.sh | Scenario 5 + grep check |
| 6 | URL matches between README and dev.sh banner | Scenario 4 |
| 7 | `smoke.sh` exits 0 on the maintainer's machine | Scenario 6 |
| 8 | `.env` is in `.gitignore` | `git check-ignore .env` returns 0 |

## Risks

- **R1 (low):** sourcing `.env` in dev.sh requires keys to be quoted correctly (handle spaces / special chars). Mitigation: have setup.sh always quote with double-quotes; document constraint.
- **R2 (low):** `gh repo clone` requires `gh` CLI — must be installed before the clone step. Mitigation: README installs it via Homebrew in step 1.
- **R3 (medium):** `uv run uvicorn` re-syncs deps on every run. Adds ~1s latency to dev.sh startup. Acceptable for dev.
- **R4 (low):** existing users who already have `LLM_PROVIDER` exported in `~/.zshrc` will see shell env override `.env`. Document this in README "If you previously ran an older setup.sh, run `unset LLM_PROVIDER` or remove the line from ~/.zshrc."
- **R5 (medium):** `smoke.sh` cannot fully verify a "fresh machine" from a populated machine. Smoke covers the launch + provider-selection paths; the fresh-machine claim is verified by the maintainer running it on a second account or VM at least once.

## Test plan summary

- Pytest: no new app tests (scope OUT for app changes). Existing test suite must still pass (regression catch).
- Shell smoke: `smoke.sh` exits 0 on maintainer's machine before ship.
- Manual inspect: walk the README top-to-bottom mentally and confirm each step exists and references the right URL/repo/auth method.
