---
feature: onboarding-rewrite
date: 2026-05-04
status: READY
playwright: skipped
---

# Inspection Results — Onboarding Rewrite

## Playwright

skipped — feature is shell scripts + docs (no web UI). The maintainer runs dev.sh manually as part of I-8 and I-9.

## Manual Checklist

The 10 items below are drawn directly from the Inspector Checklist at the bottom of CHECKLIST_2026-05-04_onboarding-rewrite.md (FEATURE_SPEC §Verification).

- **I-1** Run `grep -ri "MyCV-2" README.md setup.sh` and confirm it returns zero hits.
- **I-2** Run `grep "localhost:" README.md` and confirm every match shows `:8000` — no `:5173` or other port.
- **I-3** Open README.md and confirm a "Authenticate to GitHub" section exists BEFORE the "Clone the project" section, and that it contains a `gh auth login` walkthrough in a fenced bash block.
- **I-4** Run `./setup.sh`; when you reach the key menu (Case A), exercise all three options in separate runs: choose `[1] Keep`, then `[2] Replace`, then `[3] Cancel`. Confirm that after the Cancel run `~/.zshrc` is byte-identical to its pre-run state and the terminal prints `Setup cancelled. No changes made.` — NOT `Setup complete`.
- **I-5** Run `./setup.sh`; choose a provider that has no existing key so you land in Case B. Paste a non-empty test key. Confirm the run completes with the done banner and `~/.zshrc` contains exactly one `export <CHOSEN>_API_KEY=` line with the value you entered.
- **I-6** Manually insert a duplicate key line into `~/.zshrc` (e.g., add a second `export ANTHROPIC_API_KEY="sk-ant-DUP"` line). Run `./setup.sh` and confirm: (a) the pre-flight summary prints a yellow `⚠ Found N duplicate ANTHROPIC_API_KEY lines — will collapse to one on save.` warning; (b) after the run, `grep "^export ANTHROPIC_API_KEY=" ~/.zshrc | wc -l` returns `1`.
- **I-7** Set `LLM_PROVIDER=gemini` in `~/.zshrc` but ensure no `GEMINI_API_KEY` line is present. Run `./setup.sh` and confirm the pre-flight summary prints a yellow `⚠ Mismatch: LLM_PROVIDER says gemini but no GEMINI_API_KEY found. Setup will fix this.` line before any prompt.
- **I-8** Run `./dev.sh` from the project directory. Confirm the terminal banner includes a `Using LLM provider: <provider>` line. Then visit `http://localhost:8000/` in a browser and confirm it returns HTTP 200 (page loads without error).
- **I-9** Move the project folder to a new path (e.g., `mv ~/projects/my-job-applications ~/tmp/my-job-applications-moved`). From the new path, run `./dev.sh`. Confirm the banner shows `App running at: http://localhost:8000`, no "command not found" errors appear in stdout/stderr, and the app responds with HTTP 200 at that URL. (Move it back when done.)
- **I-10** Open README §6 "If something goes wrong". Confirm it contains exactly four troubleshooting items covering: (1) wrong provider's API key error / `source ~/.zshrc` recovery; (2) "`uvicorn: command not found` after mv" / `uv sync` recovery; (3) "Port 8000 already in use" / `lsof -ti:8000` manual kill; (4) stale manually-exported `LLM_PROVIDER` / re-run `./setup.sh` self-heal.

## Decisions

none — parent collects user verdict
