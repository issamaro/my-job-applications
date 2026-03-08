# MyCV

AI-powered CV/Resume builder.

## Prerequisites

- [Homebrew](https://brew.sh/) (macOS package manager)
- [uv](https://docs.astral.sh/uv/) — Python version + package manager
- [bun](https://bun.sh/) — Node.js runtime + package manager

## Setup

Run once:

```bash
./setup.sh
```

This installs all dependencies (Homebrew, uv, bun, Python 3.13, Python packages, Node packages).

### Manual setup (if preferred)

```bash
# Install package managers
brew install uv bun

# Python dependencies
uv sync

# Node dependencies
bun install
```

## Development

```bash
./dev.sh
```

Or manually:

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
