# My Job Applications

AI-powered CV/Resume builder.

## Getting started

### 1. Install Homebrew, Git, and gh

Open **Terminal** (press `Cmd + Space`, type "Terminal", hit Enter).

If you don't already have [Homebrew](https://brew.sh/) installed, follow the install command on its homepage. Then install Git and the GitHub CLI:

```bash
brew install git gh
```

### 2. Authenticate to GitHub

GitHub no longer accepts passwords for `git clone`, so log in once with the GitHub CLI:

```bash
gh auth login
```

Answer the prompts as follows:

- **What account do you want to log into?** → `GitHub.com`
- **What is your preferred protocol?** → `HTTPS`
- **Authenticate Git with your GitHub credentials?** → `Yes`
- **How would you like to authenticate?** → `Login with a web browser`

Copy the 8-character code shown in Terminal, paste it into the browser tab that opens, and approve the request.

When it succeeds you'll see:

```
✓ Logged in as <your-github-username>
```

If `gh` is not found, return to step 1 and run `brew install gh` again.

### 3. Clone the project

```bash
gh repo clone issamaro/my-job-applications
```

Then enter the new folder:

```bash
cd my-job-applications
```

If you see `directory already exists`, you've already cloned it — just `cd my-job-applications` and skip ahead to step 4.

### 4. Run setup

```bash
./setup.sh
```

This installs all remaining dependencies and walks you through choosing an AI provider and pasting an API key. You can press `Ctrl + C` or type `cancel` at any prompt — nothing is written until you confirm a key.

### 5. Start the app

```bash
./run.sh
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

`run.sh` builds the frontend once (if it isn't built yet) and serves the app as a single process. If the backend complains that a key is not set, jump to section 6. While editing code, use `./dev.sh` instead for live reload — see [Develop vs run](#develop-vs-run).

### 6. If something goes wrong

**App says `ANTHROPIC_API_KEY environment variable is not set` (or the Gemini equivalent), or it uses the wrong provider.**
Check your `.env` — it should have `LLM_PROVIDER` set to your provider and the matching key filled in. Re-run `./setup.sh` to rewrite it. One subtlety: if you separately `export`ed a key or `LLM_PROVIDER` in your shell config (`~/.zshrc`, `direnv`, …), that exported value wins over `.env` — remove it if it disagrees with what you chose.

**`Failed to spawn: uvicorn` (or `uvicorn: command not found`) after I moved the project folder.**
Both `run.sh` and `dev.sh` launch uvicorn through `uv run python -m uvicorn`, which goes through the still-valid Python symlink in `.venv/bin/` and bypasses the `.venv/bin/uvicorn` shim that breaks on a folder move — so this case is handled automatically. If you still see this error (rare; usually means the uv-managed Python interpreter was uninstalled separately), recover with:

```bash
rm -rf .venv && uv sync
```

Then start the app again.

**Port 8000 already in use.**
Both scripts handle this automatically (they kill the existing process). If that doesn't work, find and kill the offender:

```bash
lsof -ti:8000
```

Then `kill -9 <pid>`.

### Develop vs run

- **`./run.sh`** — build the frontend once, then serve a single process on `127.0.0.1:8000`. This is the everyday "just use the app" command; a fresh `./setup.sh` already builds the bundle for you.
- **`./dev.sh`** — run the Rollup watcher and the auto-reloading backend together on `0.0.0.0:8000`. Use this while editing code: `.svelte` changes rebuild the bundle and `.py` changes reload the server.

---

## Manual setup (for developers)

### Prerequisites

- [Homebrew](https://brew.sh/)
- [uv](https://docs.astral.sh/uv/)
- [bun](https://bun.sh/)

### Install

```bash
brew install uv
```

```bash
brew install oven-sh/bun/bun
```

```bash
uv sync
```

```bash
PLAYWRIGHT_BROWSERS_PATH=0 uv run playwright install chromium
```

`PLAYWRIGHT_BROWSERS_PATH=0` installs Chromium inside the project's `.venv` instead of the user-wide cache, so each project owns its own browser.

On Linux only, also install the system shared libraries Chromium needs (`libnspr4`, `libnss3`, etc.). These are OS-level packages — they cannot be scoped to `.venv`. Skip this on macOS.

```bash
sudo uv run playwright install-deps chromium
```

```bash
bun install
```

### API key

The app reads its config from a project-local `.env`. Copy the template:

```bash
cp .env.example .env
```

Then edit `.env` — set `LLM_PROVIDER` and paste the matching key:

**Anthropic (Claude):**

```
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
```

**Google (Gemini):**

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
```

`.env` is gitignored, so the key never gets committed. If you'd rather keep the key in your environment (e.g. via `direnv` or `pass`), export `LLM_PROVIDER` and the key there instead — the reader honours process-env over `.env`, so an exported value always wins. `./setup.sh` automates all of this (and can pull the key straight from `pass`).

### Run

```bash
uv run python -m uvicorn main:app --reload
```

```bash
bun run dev
```

### Build

```bash
bun run build
```

## Tests

```bash
uv run pytest
```
