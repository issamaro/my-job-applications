# MyCV

AI-powered CV/Resume builder.

## Prerequisites

- Python 3.13+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Volta](https://volta.sh/) (Node.js version manager) - recommended

## Setup

### Node.js (via Volta)

Install Volta (one-time):

```bash
curl https://get.volta.sh | bash
```

Volta automatically uses the correct Node.js version when you enter the project directory (pinned in `package.json`).

### Python (via uv)

```bash
uv sync
```

### Frontend dependencies

```bash
npm install
```

## Development

### Backend

```bash
uv run uvicorn app.main:app --reload
```

### Frontend

```bash
npm run dev
```

### Build

```bash
npm run build
```

## Tests

```bash
uv run pytest
```
