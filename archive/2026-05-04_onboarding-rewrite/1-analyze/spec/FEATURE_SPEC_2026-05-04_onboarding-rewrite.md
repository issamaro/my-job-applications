---
slug: onboarding-rewrite
date: 2026-05-04
ceremony_level: L
phase: 1-analyze
artifact: FEATURE_SPEC
revision: 3 (post-second-review, pre-flight + atomic + smoke deferred)
---

# Feature Spec — Onboarding Rewrite

## Persona

**Non-technical friend on macOS.** Has Homebrew installed. Comfortable copy-pasting commands into Terminal. No prior Python / Node / Git background. Reads the README linearly, will not improvise. If a step fails, they stop and message the maintainer.

## Pain point (today)

The onboarding surface (README + setup.sh + dev.sh) has five concrete first-run defects and one structural defect that, taken together, prevent the maintainer from sharing the project unattended:

1. **URL mismatch.** README step 4 directs the user to `http://localhost:5173`. dev.sh actually serves the app at `http://localhost:8000`. (Vite is not used; rollup-watch builds Svelte assets that FastAPI serves as static files.)
2. **HTTPS clone with password is dead.** README step 2 uses `git clone https://github.com/issamaro/MyCV-2.git`. GitHub no longer accepts HTTPS password auth.
3. **Wrong repo name everywhere.** README + scripts reference `MyCV-2`. The actual GitHub repo is `my-job-applications`. Clone command fails; `cd MyCV-2` fails.
4. **Provider selection does not persist correctly.** setup.sh writes `LLM_PROVIDER` to `~/.zshrc` only when no `LLM_PROVIDER` line exists yet (`if ! grep -q ... ; then ... fi` at lines 160 and 166). A user who runs setup.sh once with Claude, then re-runs choosing Gemini, ends up with `GEMINI_API_KEY` set but `LLM_PROVIDER=claude` still — boot fails with "ANTHROPIC_API_KEY not set".
5. **dev.sh breaks after `mv` of project folder.** dev.sh calls `uvicorn main:app` directly (line 71). After moving the folder, the user runs `uv sync && ./dev.sh` and gets `uvicorn: command not found`.
6. **(Structural)** The three artifacts (README, setup.sh, dev.sh) were authored independently and do not agree about the canonical URL or the canonical repo name. There is no single source of truth.

## Persistence mechanism (no `.env`)

This rewrite does NOT introduce a project-local `.env` file. All env vars (`LLM_PROVIDER`, `*_API_KEY`) are written to the user's shell-rc file. dev.sh does NOT source any project file — it relies on env vars already being in the shell, set either by the rc file at terminal startup, or by setup.sh having `export`ed them in the current shell session.

**Shell-rc detection.** setup.sh detects the *currently running* shell, not the login shell, via `ps -p $$ -o comm=` (returns `zsh` or `bash`). The match drives whether it writes to `~/.zshrc` or `~/.bashrc`. Falls back to `~/.zshrc` if detection returns anything else (default macOS shell).

**Atomicity.** All shell-rc writes are transactional: setup.sh reads existing state, runs all prompts, builds the new file content in memory, writes to a temp file, then atomically renames over the original. Cancel at any prompt → exit 0 with zero shell-rc changes and zero in-shell exports. Either the entire update lands or nothing does. No `sed -i` (sidesteps BSD vs GNU divergence).

**Terminal-staleness window.** Within the same terminal that ran setup.sh, exports in the current shell make a chained `./setup.sh && ./dev.sh` work without restart. New terminals pick up values from the rc file at launch. Only failure mode: a terminal opened *before* setup.sh ran in another terminal has captured stale env. README §6 troubleshooting addresses this with `source ~/.zshrc` or "open a new Terminal".

## Must-have list

### README.md

- README and dev.sh agree on the canonical app URL: `http://localhost:8000`. The phrase appears verbatim in the README "Start the app" section and in dev.sh's banner. Zero `localhost:5173` mentions.
- README walks the user through GitHub authentication BEFORE the clone step. Method: `gh auth login` (chosen because `gh` ships in Homebrew, requires zero key-management knowledge, and works for both clone + future PRs).
- Every repo-name reference in README and setup.sh says `my-job-applications`. Zero `MyCV-2` mentions in onboarding-path files.
- README includes a §6 "If something goes wrong" section with concrete recovery copy for: stale terminal env (provider/key mismatch error), `uvicorn: command not found` after move, port 8000 busy, and stale exports already written by older setup.sh runs.

### setup.sh — pre-flight

- Before any prompts, setup.sh reads the rc file and prints a "Current configuration" summary listing the detected current `LLM_PROVIDER`, `ANTHROPIC_API_KEY` presence, and `GEMINI_API_KEY` presence.
- The summary includes anomaly warnings:
  - Mismatch (e.g., `LLM_PROVIDER=gemini` but no `GEMINI_API_KEY`): yellow ⚠ line "Mismatch: LLM_PROVIDER says <X> but no <X>_API_KEY found. Setup will fix this."
  - Duplicates (more than one matching `^export <VAR>=` line for any of the three vars): yellow ⚠ line "Found N duplicate <VAR> lines — will collapse to one."
- The pre-flight reads only — no writes.

### setup.sh — provider prompt

- Same as today: `Which provider? [1] Claude  [2] Gemini :`. Detected current value shown if any.

### setup.sh — key prompt (explicit menus, no empty-Enter overloading)

- **Case A (chosen provider already has a key in shell-rc):**
  Three-way menu: `[1] Keep existing  [2] Replace  [3] Cancel`. The existing key's last 4 characters are shown (e.g., `(ends in …wXYZ)`).
- **Case B (no existing key for chosen provider, OR user chose Replace in Case A):**
  Prompt: `Paste your <provider> API key (input hidden), or type 'cancel' to abort. Key:`.
  - Non-empty input → use as the new key.
  - Literal `cancel` → exit setup with no writes.
  - Empty input (just Enter) → re-prompt with a clarifying line, no overloaded semantics.
- The user's choices in Case A and Case B are recorded in memory only — no shell-rc writes happen yet.

### setup.sh — atomic commit

- After all prompts complete (and only then), setup.sh builds the new shell-rc content in memory:
  - For each of `{LLM_PROVIDER, ANTHROPIC_API_KEY, GEMINI_API_KEY}` we're touching:
    1. Count matching `^export <VAR>=` lines (start-anchored, exact prefix; commented lines `# export ...` and indented lines do NOT match).
    2. If count == 0 → schedule append.
    3. If count == 1 → schedule in-place replace.
    4. If count > 1 → schedule "delete all matching, append one canonical" (collapses pre-existing duplicates).
  - The OTHER provider's `*_API_KEY` is never read or modified.
- Writes the new content to `~/.zshrc.tmp.<pid>` (or `.bashrc.tmp.<pid>`), then `mv` over the original. If the write fails, the original is untouched.
- After the rename succeeds, `export`s the new `LLM_PROVIDER` and the chosen key into the current shell session.
- Implementation uses pure-bash in-memory transformation (no `sed -i`).

### setup.sh — final state guarantee

- After a successful setup.sh exit, the shell-rc is in exactly one consistent state for the chosen provider:
  - `LLM_PROVIDER` line present and matches the user's choice.
  - `<chosen>_API_KEY` line present (newly written or preserved-by-keep).
- If the user cancels at any prompt, shell-rc is byte-identical to before setup.sh ran.
- The "Setup complete" banner on success tells the user: if running dev.sh in a *different* terminal, open a new one or run `source ~/.zshrc` first.

### dev.sh

- `dev.sh` uses `uv run uvicorn ...` instead of `uvicorn ...`, so it works regardless of whether the venv is activated, regardless of where the project folder lives, and survives `mv`.
- `dev.sh` prints the active provider after the venv-activation step: `echo "Using LLM provider: ${LLM_PROVIDER:-claude (default)}"`. Provides positive evidence for verification.
- `dev.sh` does NOT source any project file. Env vars come from the shell.

## Out of scope

- App feature changes (FastAPI routes, Svelte UI, LLM call sites, prompts, DB schema). In particular: no change to `services/llm/factory.py` to add provider/key mismatch detection.
- GUI installer (Electron/TUI).
- Mandatory Docker pivot.
- Linux / Windows onboarding (macOS only; Linux is incidentally supported because the in-memory transformation has no platform-divergent flags, but not promised).
- Removing the manual-setup section from README (kept for developers; updated to reflect that setup.sh writes to shell-rc).
- Cleaning up stale `*_API_KEY` lines already written to existing users' rc files by previous setup.sh versions. The new always-update logic for `LLM_PROVIDER` self-heals; orphan `*_API_KEY` lines remain (harmless).
- **Automated smoke script (`smoke.sh`).** Deferred to follow-up backlog item `backlog/raw/onboarding-smoke-script.md`. Build-gate verification this iteration is the manual inspector checklist (see "Verification" below).

## BDD scenarios

### Scenario 1 — GitHub auth before clone

```
Given a fresh macOS account with Homebrew installed and no gh CLI configured
When the user follows README sections "Install Git and gh" and "Authenticate to GitHub" linearly
Then `gh auth status` reports an authenticated session
And `gh repo clone issamaro/my-job-applications` succeeds without prompting for a password
And the local directory `my-job-applications/` exists
```

### Scenario 2 — Provider selection persists end-to-end

#### 2a — Fresh shell-rc, choose Gemini, paste key

```
Given a clean ~/.zshrc with no LLM_PROVIDER and no GEMINI_API_KEY lines
When the user runs ./setup.sh, selects "2" (Gemini), and pastes a non-empty key "AIzaTEST123"
Then ~/.zshrc contains exactly one line `export LLM_PROVIDER="gemini"` and exactly one line `export GEMINI_API_KEY="AIzaTEST123"`
And no live API call was made by setup.sh (the value is treated as opaque)
And the current shell has both env vars exported
```

#### 2b — Re-run switches provider, preserves orphan key

```
Given a ~/.zshrc that already has `export LLM_PROVIDER="claude"` and `export ANTHROPIC_API_KEY="sk-ant-OLD"`
When the user re-runs ./setup.sh, selects "2" (Gemini), and pastes a new key "AIzaNEW"
Then ~/.zshrc contains `export LLM_PROVIDER="gemini"` (the old `claude` line is gone — collapsed to one)
And ~/.zshrc contains `export GEMINI_API_KEY="AIzaNEW"` (newly appended)
And the previous `export ANTHROPIC_API_KEY="sk-ant-OLD"` line is still present untouched
```

#### 2c — Existing key, user chooses Keep

```
Given a ~/.zshrc that has `export LLM_PROVIDER="claude"` and `export GEMINI_API_KEY="AIzaEXISTING"`
When the user runs ./setup.sh, selects "2" (Gemini), and chooses "[1] Keep existing" at the key menu
Then ~/.zshrc has `export LLM_PROVIDER="gemini"` (updated)
And ~/.zshrc still has `export GEMINI_API_KEY="AIzaEXISTING"` (unchanged)
And the current shell has LLM_PROVIDER=gemini and GEMINI_API_KEY=AIzaEXISTING exported
```

#### 2d — Cancel anywhere → no writes

```
Given a ~/.zshrc that has `export LLM_PROVIDER="claude"` and `export ANTHROPIC_API_KEY="sk-ant-X"`
When the user runs ./setup.sh and presses Ctrl-C at the provider prompt
  OR types 'cancel' at the key prompt
  OR chooses "[3] Cancel" at the existing-key menu
Then ~/.zshrc is byte-identical to before setup.sh ran (no LLM_PROVIDER change, no key write, no duplicate cleanup applied either)
And setup.sh exits with code 0
And the current shell's env is unchanged
```

#### 2e — Pre-flight detects mismatch

```
Given a ~/.zshrc where `export LLM_PROVIDER="gemini"` exists but no `export GEMINI_API_KEY=` line is present
When the user runs ./setup.sh
Then setup.sh prints (before any prompt) a yellow ⚠ line containing "Mismatch: LLM_PROVIDER says gemini but no GEMINI_API_KEY found"
And the prompts continue normally so the user can fix the state
```

#### 2f — Pre-flight detects duplicates and collapses on commit

```
Given a ~/.zshrc with two `export ANTHROPIC_API_KEY="..."` lines (legacy from a buggy older setup.sh)
When the user runs ./setup.sh, selects "1" (Claude), and chooses "[1] Keep existing" at the key menu
Then setup.sh prints (before any prompt) a yellow ⚠ line containing "Found 2 duplicate ANTHROPIC_API_KEY lines — will collapse to one"
And after setup.sh exits, ~/.zshrc has exactly one `export ANTHROPIC_API_KEY=` line (with the most recent of the two values, or with the first — implementation MAY choose either deterministically; the contract is that exactly one remains)
```

#### 2g — Backend boots with chosen provider, verified positively (parameterized)

```
Given a shell where LLM_PROVIDER=<P> and the matching <P>_API_KEY is set to a non-empty value
  (P in {claude, gemini})
When the user runs ./dev.sh
Then dev.sh stdout contains a line matching exactly `Using LLM provider: <P>`
And dev.sh stderr does NOT contain `<P_OTHER>_API_KEY environment variable is not set`
  (i.e., when P=gemini, no ANTHROPIC error; when P=claude, no GEMINI error)
And the backend responds 200 to GET http://localhost:8000/
```

### Scenario 3 — Portable launch after mv

```
Given a working install at ~/projects/my-job-applications with .venv populated
When the user runs `mv ~/projects/my-job-applications ~/code/my-job-applications` and then `cd ~/code/my-job-applications && ./dev.sh`
Then dev.sh stdout contains a line "App running at: http://localhost:8000"
And no line in dev.sh stdout/stderr matches "command not found"
And the backend responds 200 to GET http://localhost:8000/
```

### Scenario 4 — URL agreement

```
Given a fresh checkout
When grep is run on README.md for "localhost:"
Then every match is "localhost:8000" — there are zero "localhost:5173" mentions

Given dev.sh has just printed its banner
When the user reads the line `App running at: http://localhost:8000`
Then opening that exact URL in a browser loads the app (HTTP 200, non-empty body)
And that URL string equals the URL cited in README's "Start the app" section
```

### Scenario 5 — Repo name consistency

```
Given the repo root
When `grep -ri "MyCV-2"` is run on README.md and setup.sh
Then there are zero matches in either file

Given README.md
When the clone command in the "Clone the project" section is extracted
Then it reads `gh repo clone issamaro/my-job-applications`
And the subsequent `cd` line reads `cd my-job-applications`
```

## Verification (build gate)

Build-gate verification is the **manual inspector checklist**. The v6 inspector subagent assembles the checklist payload from this spec's BDD scenarios + the UX_DESIGN states. The maintainer walks each item before declaring the feature done.

Concrete items the inspector pass must cover:

| # | Check | Maps to |
|---|---|---|
| 1 | `grep -ri "MyCV-2" README.md setup.sh` returns zero hits | Scenario 5, Success #5 |
| 2 | `grep "localhost:" README.md` shows only `:8000` matches | Scenario 4, Success #6 |
| 3 | README has a §"Authenticate to GitHub" section before "Clone the project" with `gh auth login` walkthrough | Scenario 1, Success #2 |
| 4 | Run `./setup.sh`, exercise Case A all three menu paths (Keep / Replace / Cancel) | Scenario 2c, 2d |
| 5 | Run `./setup.sh`, exercise Case B paste path | Scenario 2a |
| 6 | Run `./setup.sh` with a manually-broken rc (e.g., add a duplicate key line); confirm pre-flight prints the duplicate warning AND post-run rc has one line | Scenario 2f |
| 7 | Run `./setup.sh` with a manually-induced mismatch; confirm pre-flight prints the mismatch warning | Scenario 2e |
| 8 | Run `./dev.sh`; eyeball the `Using LLM provider:` line; visit `http://localhost:8000/`; confirm 200 | Scenario 2g, Scenario 4 |
| 9 | `mv` the project folder, re-run `./dev.sh`, confirm app loads | Scenario 3, Success #4 |
| 10 | Open README §6 troubleshooting; confirm copy reads correctly for the four documented scenarios | Must-have list |

Pass = all 10 items observed once. Inspector verdict with any "Fail" returns to build phase.

## Success criteria

| # | Criterion | How verified |
|---|---|---|
| 2 | `gh auth login` walkthrough exists in README | Inspector item 3 |
| 3 | Provider + key persist together in shell-rc and update on re-run | Inspector items 4–6 + Scenarios 2a–2f |
| 4 | `dev.sh` works from any folder location | Inspector item 9 |
| 5 | All repo references say `my-job-applications` (zero `MyCV-2`) in README + setup.sh | Inspector item 1 |
| 6 | URL matches between README and dev.sh banner | Inspector item 2 + 8 |
| 8 | Active provider verifiable from dev.sh stdout | Inspector item 8 + Scenario 2g |
| 9 | setup.sh atomic-write guarantee: cancel at any point leaves rc untouched | Inspector item 4 + Scenario 2d |

(Numbering preserves legacy slots; #1 is post-ship validation, #7 is the deferred smoke script.)

## Post-ship validation (NOT a build gate)

- **#1 — README is linearly followable end-to-end on fresh macOS.** Within ~2 weeks of ship, the maintainer walks a non-technical contact through the README on a fresh machine. Friction observed becomes a follow-up backlog item.

## Risks

- **R1 (medium):** dev.sh runs in terminal B that was opened before setup.sh ran in terminal A → terminal B has stale env. Mitigation: README §6 troubleshooting tells user to `source ~/.zshrc` or open a new Terminal. setup.sh banner mentions this when keys were just written.
- **R2 (low):** `gh repo clone` requires `gh` CLI — must be installed before the clone step. Mitigation: README installs it via Homebrew in step 1.
- **R3 (low):** `uv run uvicorn` re-syncs deps on every run. Adds ~1s latency to dev.sh startup (informally measured; not a gate). Acceptable for dev.
- **R4 (low):** existing users with `LLM_PROVIDER` already in `~/.zshrc` from previous setup.sh runs — the new always-update logic overwrites correctly on next run, so this is self-healing.
- **R5 (low):** Pain-point 5's root cause was inferred; the `uv run uvicorn` fix works regardless of which exact PATH-vs-stale-path mechanism was at play.
- **R6 (low):** `services/llm/factory.py:43` already logs `Using LLM provider: <name>` via the Python logger. dev.sh's pre-launch echo of the same string is intentional duplication — the echo runs BEFORE uvicorn starts, the factory log runs after. Implementer must not consolidate them on the assumption they're redundant. Watch item, not a defect.

## Test plan summary

- **Pytest:** existing test suite must still pass (regression catch). No new app tests (scope OUT for app changes).
- **Inspector checklist:** the 10 items above. Pass = build-gate satisfied.
- **Manual inspect:** read the README top-to-bottom and confirm each step references the right URL/repo/auth method/no-MyCV-2.
