---
slug: onboarding-rewrite
date: 2026-05-04
ceremony_level: L
phase: 1-analyze
artifact: UX_DESIGN
---

# UX Design — Onboarding Rewrite

The "UI" here is three surfaces seen by the non-technical user, in order:
**(A) README.md** — what they read in a browser/editor before opening Terminal.
**(B) setup.sh** — interactive prompts in Terminal.
**(C) dev.sh** — Terminal output banner + the browser tab the URL opens.

## Surface A — README.md (linear flow)

### Section list (top to bottom)

1. **Title + one-sentence pitch.**
2. **Section 1 — Install Homebrew & Git** (combined; both via brew).
3. **Section 2 — Authenticate to GitHub** (NEW — must be before clone).
4. **Section 3 — Clone the project** (uses `gh repo clone`).
5. **Section 4 — Run setup** (`./setup.sh`, mentions provider choice).
6. **Section 5 — Start the app** (`./dev.sh`, references `localhost:8000`).
7. **Section 6 — If something goes wrong** (troubleshooting: stale ~/.zshrc, missing key, port already in use).
8. **Manual setup (developers)** — kept; updated to reflect `.env` instead of `~/.zshrc` exports.
9. **Tests** — kept.

### State coverage per section

A README "state" maps to a reader outcome. For each section:

| Section | Empty / first-read state | Success state | Error state |
|---|---|---|---|
| 2 — Auth | Reader has never used `gh`. README shows: open Terminal, run `gh auth login`, choose GitHub.com → HTTPS → "Login with a web browser", paste 8-char code. | Terminal prints `✓ Logged in as <username>`. | If `gh` not on PATH: README points back to Section 1 (install Homebrew + `brew install gh`). If browser flow times out: README says "Re-run `gh auth login` and paste the code within 15 minutes." |
| 3 — Clone | New folder doesn't exist yet. | `my-job-applications/` directory present, `cd` succeeds. | If "directory already exists": README says "You already cloned it — `cd my-job-applications` and skip to Section 4." |
| 4 — Setup | No `.env` yet. | Setup runs, asks provider, asks key, writes `.env`, prints "Setup complete." | If brew/uv/bun install step fails: setup.sh exits non-zero with the failing command's output (not a generic error). |
| 5 — Run | Backend not running. | dev.sh banner shows `App running at: http://localhost:8000`. Browser opens, app loads. | If port 8000 busy: dev.sh kills the existing process (current behavior, keep). If `LLM_PROVIDER` mismatched: backend boot logs the mismatch — README troubleshooting section explains. |

### Loading state

README itself has no loading state. The implied "loading" is `setup.sh` running for 1–5 minutes installing brew/uv/bun. setup.sh already prints `▸ Installing X...` then `✓ X` per step — keep that pattern.

### Copy guidelines

- Sections numbered, each ≤4 lines of prose + one fenced code block.
- Code blocks contain ONE command per block (so copy-paste cannot accidentally pick up a comment).
- The phrase `my-job-applications` appears verbatim in the clone, cd, and "where you are" lines.
- The phrase `http://localhost:8000` appears verbatim in section 5 and nowhere else.
- No "MyCV-2" anywhere.

### Accessibility / readability

- Headings start at H2 inside README (H1 is title).
- Code blocks have language hint (` ```bash `) so GitHub renders them with a copy button.
- No emoji in commands (only in section dividers, if any).
- Hyperlinks use full text, not "click here".

## Surface B — setup.sh (interactive)

### Prompt flow (state machine)

```
[start]
  │
  ▼
Detect & install: brew → uv → python 3.13 → bun → uv sync → playwright → bun install
  │   each step: "▸ Installing X..." → "✓ X"   (existing pattern, keep)
  │
  ▼
Read existing .env (if present); detect existing LLM_PROVIDER value
  │
  ▼
[provider prompt]
  "Which provider? [1] Claude  [2] Gemini : "
  │   default highlighted = existing value if any
  │
  ▼
[key prompt]
  Skipped if matching *_API_KEY already in .env (and user confirms to keep)
  Else: "Paste your <provider> API key (input hidden):"
  │
  ▼
Write .env atomically:
  - update or insert LLM_PROVIDER="<chosen>"
  - update or insert <chosen>_API_KEY="<value>"
  - leave the other provider's key alone if present
  │
  ▼
[done banner]
  "✓ Setup complete. Run ./dev.sh to start."
```

### State coverage

| State | What user sees |
|---|---|
| **Empty** (no .env) | Both prompts shown. Done banner says "Created .env with <provider>." |
| **Loading** | Per-step `▸ Installing X...` lines with spinner-ish blue arrow. |
| **Success** | Final `✓ Setup complete.` banner with green check. Trailing `Start the app with: ./dev.sh`. |
| **Error — brew install fails** | Red `✗ <command> failed (exit N).` Script exits 1. No partial `.env` written. |
| **Error — empty key entered** | Yellow `! No key entered — skipping. Set <VAR> in .env manually before running the app.` Script does NOT exit; provider line still updated. |
| **Re-run with existing key** | "Found existing GEMINI_API_KEY in .env. Keep it? [Y/n]" — default Y. If Y, skips key prompt. If n, re-prompts. |
| **Re-run with provider switch** | Detects mismatch. Prints "Switching LLM_PROVIDER from claude → gemini." Updates in place. |

### Color/typography (Terminal)

- Reuse existing palette in setup.sh (BLUE/GREEN/YELLOW/RED + BOLD).
- One blank line between major sections; no decorative ASCII boxes beyond the existing dividers.
- Banner header stays single-line: `MyCV — Setup`.

### Keyboard navigation

- All prompts answered via `read -r` (Enter to submit).
- Hidden input for API keys via `read -rs`.
- Ctrl-C exits cleanly (`set -e` already kills on signal).
- No arrow-key or fancy TUI — keep it copy-paste friendly.

## Surface C — dev.sh (terminal banner + browser)

### Banner (after launch)

```
╔══════════════════════════════════════════╗
║       MyCV Development Server            ║
╚══════════════════════════════════════════╝
Loading environment from .env...
Activating Python virtual environment...
Syncing Python dependencies...
Starting Svelte build watcher...
Starting FastAPI backend...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
App running at: http://localhost:8000
API docs at:    http://localhost:8000/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Press Ctrl+C to stop all servers
```

### State coverage

| State | What user sees |
|---|---|
| **Empty / first run** | Banner above, browser-launchable URL. |
| **Loading** | Lines 2–5 print sequentially as each substep completes. Existing colored lines kept. |
| **Success** | Banner shown; backend reachable at the URL printed. |
| **Error — .env missing key** | Backend boot crashes inside uvicorn; the error is the existing `ValueError("ANTHROPIC_API_KEY environment variable is not set")` from `services/llm/claude.py`. dev.sh's `set -e` propagates the exit. README troubleshooting section addresses this. |
| **Error — port busy** | Yellow line `Killing existing process on port 8000...` (current behavior). |
| **Error — uvicorn not on PATH** | Should NOT occur after this rewrite — `uv run uvicorn` doesn't depend on PATH. If it does, treat as regression. |

### URL is the single source of truth

- dev.sh prints `http://localhost:8000`.
- README references `http://localhost:8000`.
- Any future change to the port must update both files (call out in README dev section).

## Surface D — smoke.sh (NEW, maintainer-facing)

Plain bash script run by the maintainer before sharing. Prints a checklist:

```
=== Onboarding smoke test ===
✓ gh installed
✓ gh auth status: authenticated as <username>
✓ Working dir matches my-job-applications
✓ .env present
✓ .env has LLM_PROVIDER
✓ .env has matching *_API_KEY for chosen provider
✓ uv run uvicorn --version succeeds
✓ dev.sh boot reaches "App running at"
✓ HTTP 200 from http://localhost:8000/
✓ no "command not found" in dev.sh log

PASS (10/10)
```

Failures swap `✓` for `✗` and exit non-zero. Output is the acceptance evidence for the rewrite.

## Surface E — .env file (artifact, not seen unless opened)

Format: KEY="value" per line. Created/updated by setup.sh. Read by dev.sh. Gitignored.

```
# Created by setup.sh — safe to edit by hand. KEY="value" format.
LLM_PROVIDER="gemini"
GEMINI_API_KEY="AIza..."
# ANTHROPIC_API_KEY="sk-ant-..."   # optional second provider
```

## Cross-cutting notes

- **Rollback path:** A user with an existing `~/.zshrc` containing `LLM_PROVIDER` may see the old value override `.env` (env vars from rc are loaded first). README troubleshooting section calls this out and tells the user to remove those lines.
- **No-mouse path:** The whole flow is copy-paste from README into Terminal. No GUI step.
- **Internationalization:** English only. Not in scope.
