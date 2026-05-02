# MyCV

AI-powered CV/Resume builder.

## Getting started

### 1. Install Git

Open **Terminal** (press `Cmd + Space`, type "Terminal", hit Enter).

Check if Git is already installed:

```bash
git --version
```

If you see a version number, skip to step 2. Otherwise, macOS will prompt you to install it — follow the prompt.

### 2. Download the project

```bash
git clone https://github.com/issamaro/MyCV-2.git
cd MyCV-2
```

### 3. Run setup

```bash
./setup.sh
```

This installs all dependencies and walks you through getting an API key for the AI features.

### 4. Start the app

```bash
./dev.sh
```

Then open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Manual setup (for developers)

### Prerequisites

- [Homebrew](https://brew.sh/)
- [uv](https://docs.astral.sh/uv/)
- [bun](https://bun.sh/)

### Install

```bash
brew install uv && brew install oven-sh/bun/bun
uv sync
bun install
```

### API key

The app reads the provider and key from environment variables. Add one of these to your `~/.zshrc`:

**Anthropic (Claude):**
```bash
export LLM_PROVIDER="claude"
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Google (Gemini):**
```bash
export LLM_PROVIDER="gemini"
export GEMINI_API_KEY="AIza..."
```

### Run

```bash
# Backend
uv run uvicorn main:app --reload

# Frontend (separate terminal)
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
