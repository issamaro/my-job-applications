# MyCV

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
./dev.sh
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

If the backend fails to start with a message like `ANTHROPIC_API_KEY environment variable is not set` (or the Gemini equivalent) and you just ran `setup.sh`, your current Terminal window still has the old environment — open a new Terminal window or run `source ~/.zshrc`, then `./dev.sh` again. See section 6 for more recovery paths.

### 6. If something goes wrong

**App says `ANTHROPIC_API_KEY environment variable is not set` but I chose Gemini (or vice versa).**
Open a new Terminal window, or run `source ~/.zshrc`. Then check what's actually set:

```bash
env | grep -E 'LLM_PROVIDER|API_KEY'
```

If `LLM_PROVIDER` and your chosen provider's key don't match, re-run `./setup.sh`.

**`uvicorn: command not found` after I moved the project folder.**
Run `uv sync` once, then `./dev.sh` again. This rewrite uses `uv run uvicorn` so the moved-folder case shouldn't happen — if it does, please file an issue.

**Port 8000 already in use.**
`dev.sh` handles this automatically (kills the existing process). If it doesn't, find and kill the offender:

```bash
lsof -ti:8000
```

Then `kill -9 <pid>`.

**I had `LLM_PROVIDER` exported manually in my shell-rc from before.**
The new `setup.sh` always overwrites `LLM_PROVIDER` on each run, so it self-heals. Just re-run `./setup.sh` once.

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

```bash
bun install
```

### API key

The app reads the provider and key from environment variables. Add one of these to your `~/.zshrc`:

**Anthropic (Claude):**

```bash
export LLM_PROVIDER="claude"
```

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Google (Gemini):**

```bash
export LLM_PROVIDER="gemini"
```

```bash
export GEMINI_API_KEY="AIza..."
```

### Run

```bash
uv run uvicorn main:app --reload
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
