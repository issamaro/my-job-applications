# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Single source of application configuration — layered process-env, .env, and default constants.

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "claude")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
DATABASE = os.environ.get("DATABASE", "app.db")
