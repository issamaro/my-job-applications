---
slug: onboarding-rewrite
date: 2026-05-04
ceremony_level: L
phase: 1-analyze
artifact: UX_DESIGN
revision: 3 (post-second-review, pre-flight + atomic + smoke deferred)
---

# UX Design — Onboarding Rewrite

The "UI" here is three surfaces seen by the non-technical user, in order:
**(A) README.md** — what they read in a browser/editor before opening Terminal.
**(B) setup.sh** — interactive prompts in Terminal.
**(C) dev.sh** — Terminal output banner + the browser tab the URL opens.

There is no project-local config file (no `.env`). All persisted env vars live in the user's shell-rc (`~/.zshrc` or `~/.bashrc`). There is no automated smoke script in this iteration — see `backlog/raw/onboarding-smoke-script.md` for the deferred follow-up.

---

## Surface A — README.md (linear flow)

### Section list (top to bottom)

1. **Title + one-sentence pitch.**
2. **Section 1 — Install Homebrew, Git, and gh** (combined; all via brew).
3. **Section 2 — Authenticate to GitHub** (NEW — must be before clone; `gh auth login`).
4. **Section 3 — Clone the project** (`gh repo clone issamaro/my-job-applications`).
5. **Section 4 — Run setup** (`./setup.sh`, mentions provider choice + cancel-anywhere-is-safe).
6. **Section 5 — Start the app** (`./dev.sh`, references `localhost:8000`).
7. **Section 6 — If something goes wrong** (troubleshooting with concrete recovery paths — see "Troubleshooting copy" below).
8. **Manual setup (developers)** — kept; updated to reflect that `setup.sh` writes to shell-rc.
9. **Tests** — kept.

### State coverage per section

| Section | Empty / first-read state | Success state | Error state |
|---|---|---|---|
| 2 — Auth | Reader has never used `gh`. README shows: open Terminal, run `gh auth login`, choose `GitHub.com` → `HTTPS` → `Login with a web browser`, paste 8-char code into the browser. | Terminal prints `✓ Logged in as <username>`. | If `gh` not on PATH: README points back to Section 1 (`brew install gh`). If browser flow times out: "Re-run `gh auth login` and paste the code within 15 minutes." |
| 3 — Clone | New folder doesn't exist yet. | `my-job-applications/` directory present, `cd` succeeds. | "Directory already exists" → "You already cloned it — `cd my-job-applications` and skip to Section 4." |
| 4 — Setup | No `LLM_PROVIDER` in shell-rc yet. | Setup runs, prints pre-flight summary, asks provider, asks key, atomically writes both, prints "Setup complete." | brew/uv/bun install step fails → setup.sh exits non-zero with the failing command's output (existing pattern, keep). User cancels at any prompt → setup.sh exits 0 with no shell-rc changes. |
| 5 — Run | Backend not running. | dev.sh banner shows `App running at: http://localhost:8000` and `Using LLM provider: <chosen>`. Browser opens, app loads. | Port 8000 busy → dev.sh kills the existing process (existing behavior). Stale terminal env → backend raises the existing `ValueError` from `services/llm/claude.py:27` (or `gemini.py:27`) and dev.sh exits. README §6 explains recovery. |

### Loading state

README itself has no loading state. The implied "loading" is `setup.sh` running for 1–5 minutes installing brew/uv/bun. setup.sh prints `▸ Installing X...` then `✓ X` per step (existing pattern).

### Copy guidelines

- Sections numbered, each ≤4 lines of prose + one fenced code block.
- Code blocks contain ONE command per block (so copy-paste cannot accidentally pick up a comment).
- The phrase `my-job-applications` appears verbatim in the clone, cd, and "where you are" lines.
- The phrase `http://localhost:8000` appears verbatim in section 5 and nowhere else.
- No "MyCV-2" anywhere.

### Troubleshooting copy (README §6)

Exact items the section must contain:

1. **"App says 'ANTHROPIC_API_KEY environment variable is not set' but I chose Gemini" (or symmetric)**
   - Open a new Terminal window (or run `source ~/.zshrc`).
   - Run `env | grep -E 'LLM_PROVIDER|API_KEY'` to see what's actually set.
   - If `LLM_PROVIDER` and your chosen provider's key don't match, re-run `./setup.sh`.
2. **"`uvicorn: command not found` after I moved the project folder"**
   - Run `uv sync` once, then `./dev.sh` again.
   - This rewrite uses `uv run uvicorn` so the moved-folder case shouldn't happen — if it does, file an issue.
3. **"Port 8000 already in use"**
   - dev.sh handles this automatically (kills the existing process). If it doesn't, find the offending process: `lsof -ti:8000` then `kill -9 <pid>`.
4. **"I had `LLM_PROVIDER` exported manually in my shell-rc from before"**
   - The new setup.sh always overwrites `LLM_PROVIDER` on each run, so it self-heals. Just re-run `./setup.sh` once.

### Accessibility / readability

- Headings start at H2 inside README (H1 is title).
- Code blocks have language hint (` ```bash `) so GitHub renders them with a copy button.
- No emoji in commands (only in section dividers, if any).
- Hyperlinks use full text, not "click here".

---

## Surface B — setup.sh (interactive)

### High-level: two-phase atomic flow

setup.sh has two distinct phases:

- **Phase 1 — Plan (read-only).** Read shell-rc, run prompts, build the intended changeset in memory. No writes. Cancel at any step → exit 0 with zero changes.
- **Phase 2 — Commit (single atomic write).** Build the new shell-rc content in memory, write to a temp file, atomic `mv` over the original, then `export` into the current shell.

Either the entire update lands or nothing does.

### Pre-flight (Phase 1, before prompts)

After install steps complete and before any prompts, setup.sh reads shell-rc and prints a configuration summary:

```
Current configuration in ~/.zshrc:
  LLM_PROVIDER:        gemini
  ANTHROPIC_API_KEY:   not set
  GEMINI_API_KEY:      set (ends in …wXYZ)
```

If anomalies are detected, additional yellow ⚠ lines follow:

```
⚠ Mismatch: LLM_PROVIDER says gemini but no GEMINI_API_KEY found. Setup will fix this.
⚠ Found 2 duplicate ANTHROPIC_API_KEY lines — will collapse to one on save.
```

### Provider prompt (Phase 1)

```
Which provider? [1] Claude  [2] Gemini : 
```

Detected current value shown in brackets next to the matching number if any (e.g., `[2] Gemini  (currently selected)`).

### Key prompt (Phase 1) — explicit menus, no empty-Enter overloading

**Case A — chosen provider already has a key in shell-rc:**

```
You already have a GEMINI_API_KEY in ~/.zshrc (ends in …wXYZ).
  [1] Keep the existing key
  [2] Replace it with a new key
  [3] Cancel setup
Choice [1/2/3]: 
```

- `1` → record "use existing", proceed to commit.
- `2` → re-prompt as Case B.
- `3` → exit setup, no shell-rc changes.

**Case B — chosen provider has no key yet (or user picked Replace):**

```
Get a Gemini API key at https://aistudio.google.com/app/apikey
Paste your key (input hidden), or type 'cancel' to abort.
Key: 
```

- Non-empty input → record "new key value: <input>", proceed to commit.
- Input exactly `cancel` (literal) → exit setup, no shell-rc changes.
- Empty input (just Enter) → re-prompt with: `No key entered. Paste a key, or type 'cancel' to abort.` Loop until non-empty or `cancel`.

### Commit (Phase 2)

After all prompts complete, setup.sh:

1. Reads the rc file content into memory.
2. For each of `{LLM_PROVIDER, ANTHROPIC_API_KEY, GEMINI_API_KEY}` it intends to touch:
   - Counts matching `^export <VAR>=` lines (start-anchored, exact prefix; `# export` and indented lines do NOT match).
   - count == 0 → schedule append at end of file.
   - count == 1 → schedule in-place replace.
   - count > 1 → schedule "delete all matching, append one canonical".
3. Applies all scheduled operations to the in-memory copy.
4. Writes the result to `~/.zshrc.tmp.$$`.
5. `mv ~/.zshrc.tmp.$$ ~/.zshrc` (atomic on POSIX filesystems).
6. `export LLM_PROVIDER="<chosen>"` and `export <CHOSEN>_API_KEY="<value>"` in the current shell.
7. Prints success banner.

If step 4 or 5 fails: original rc untouched, no in-shell exports run, exit 1 with a diagnostic.

### Done banner (Phase 2 success)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Setup complete.

Run the app with:
    ./dev.sh

If you want to use a different terminal, open a new one OR
run `source ~/.zshrc` first, then ./dev.sh.
```

### State coverage

| State | What user sees |
|---|---|
| **Empty** (no LLM_PROVIDER in shell-rc) | Pre-flight summary shows all "not set". Both prompts shown. Done banner. |
| **Loading** (install steps) | Per-step `▸ Installing X...` lines with blue arrow (existing). |
| **Pre-flight anomaly — mismatch** | Yellow ⚠ line above the prompts, prompts continue normally. |
| **Pre-flight anomaly — duplicates** | Yellow ⚠ line above the prompts, duplicates collapsed at commit time. |
| **Re-run with provider switch** | Pre-flight shows current provider. Provider prompt shows it as `[N]  (currently selected)`. After Case A or B and commit, old `LLM_PROVIDER` line is collapsed to one with the new value. |
| **Case A: Keep existing** | Green `✓ Kept existing GEMINI_API_KEY.` Then done banner. |
| **Case A: Replace** | Falls through to Case B prompt. |
| **Case A: Cancel** | Plain message `Setup cancelled. No changes made.` Exit 0. |
| **Case B: Cancel** | Same as above. Exit 0. |
| **Empty key, looped** | Re-prompt with reminder. No exit, no writes. |
| **Atomic write fails** | Red `✗ Failed to write ~/.zshrc (disk full? permissions?). Original is unchanged.` Exit 1. |
| **brew install fails** | Existing `set -e` propagates. Pre-flight and prompts never ran. No rc changes. |

### Color/typography (Terminal)

- Reuse existing palette in setup.sh (BLUE/GREEN/YELLOW/RED + BOLD).
- One blank line between major sections; no decorative ASCII boxes beyond the existing dividers.
- Banner header stays single-line: `MyCV — Setup`.

### Keyboard navigation

- All prompts answered via `read -r` (Enter to submit).
- Hidden input for API keys via `read -rs`.
- Pressing Enter with no input on the key prompt loops; never has overloaded "keep existing" semantics.
- Ctrl-C exits cleanly at any prompt with no shell-rc changes (`set -e` plus the atomic-commit-only-at-end pattern guarantee).
- No arrow-key or fancy TUI — keep it copy-paste friendly.

---

## Surface C — dev.sh (terminal banner + browser)

### Banner (after launch)

```
╔══════════════════════════════════════════╗
║       MyCV Development Server            ║
╚══════════════════════════════════════════╝
Activating Python virtual environment...
Syncing Python dependencies...
Using LLM provider: gemini
Starting Svelte build watcher...
Starting FastAPI backend...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
App running at: http://localhost:8000
API docs at:    http://localhost:8000/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Press Ctrl+C to stop all servers
```

The bare `App running at: http://localhost:8000` is the canonical URL. Anything that compares "URL printed by dev.sh" vs "URL in README" matches against this line, not against the `/docs` line.

The `Using LLM provider:` line uses `${LLM_PROVIDER:-claude (default)}` so an unset variable still prints something (the default the factory would pick).

**Note for implementer:** `services/llm/factory.py:43` ALSO logs `Using LLM provider: <name>` via the Python logger after uvicorn starts. dev.sh's pre-launch echo of the same string is intentional duplication — runs BEFORE uvicorn so the user sees the active provider in the banner area, not buried in later log output. Do NOT consolidate.

### State coverage

| State | What user sees |
|---|---|
| **Empty / first run** | Banner above, browser-launchable URL. |
| **Loading** | Activate / sync / "Using LLM provider:" / Svelte / backend lines print sequentially. |
| **Success** | Banner shown; backend reachable at the URL printed; `Using LLM provider:` line shows the active provider. |
| **Error — provider/key mismatch** | Backend boot crashes inside uvicorn with the existing `ValueError` from `services/llm/claude.py:27` or `gemini.py:27`. dev.sh's `set -e` propagates exit. README §6 troubleshooting item 1 is the recovery path. |
| **Error — port busy** | Yellow `Killing existing process on port 8000...` (existing behavior). |
| **Error — uvicorn not on PATH** | Should NOT occur after this rewrite — `uv run uvicorn` doesn't depend on activation/PATH. If it does, treat as regression. |

### URL is the single source of truth

- dev.sh prints `http://localhost:8000` as the bare app URL.
- README references `http://localhost:8000`.
- Any future change to the port must update both files (call out in README dev section).

---

## Cross-cutting notes

- **No `.env` file anywhere.** All persisted env vars are in the user's shell-rc. dev.sh does NOT source any project file.
- **Shell-rc detection.** setup.sh detects via `ps -p $$ -o comm=` (current shell, not login shell). Falls back to `~/.zshrc` if detection returns anything other than `zsh` or `bash`.
- **Atomic writes.** All shell-rc edits go through "in-memory transform → tmp file → atomic mv". No `sed -i`. No partial-write states possible.
- **Cancel-anywhere is safe.** Ctrl-C, typing `cancel`, or choosing the Cancel menu option at any point leaves shell-rc byte-identical to before setup.sh ran.
- **The terminal-staleness window.** README §6 troubleshooting item 1 walks through the fix.
- **No-mouse path:** the whole flow is copy-paste from README into Terminal. No GUI step.
- **Internationalization:** English only. Not in scope.
