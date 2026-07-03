"""Tests for the settings module's .env + process-env layering."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROBE = (
    "import settings; "
    "print(settings.LLM_PROVIDER); "
    "print(settings.ANTHROPIC_API_KEY); "
    "print(settings.CLAUDE_MODEL); "
    "print(settings.GEMINI_API_KEY); "
    "print(settings.GEMINI_MODEL); "
    "print(settings.DATABASE)"
)


def read_settings_in_subprocess(tmp_path, dotenv_text=None, extra_env=None):
    """Import a copy of settings.py in a clean subprocess and return its values.

    A copy is used so the __file__-derived .env path points at tmp_path. The
    environment is reduced to PATH so no dev-shell config leaks in — the only way to
    exercise load_dotenv faithfully (monkeypatching settings would not touch it).
    """
    shutil.copy(PROJECT_ROOT / "settings.py", tmp_path / "settings.py")
    if dotenv_text is not None:
        (tmp_path / ".env").write_text(dotenv_text)
    env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(tmp_path)}
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    return {
        "LLM_PROVIDER": lines[0],
        "ANTHROPIC_API_KEY": lines[1],
        "CLAUDE_MODEL": lines[2],
        "GEMINI_API_KEY": lines[3],
        "GEMINI_MODEL": lines[4],
        "DATABASE": lines[5],
    }


def test_defaults_when_no_dotenv_and_clean_env(tmp_path):
    """No .env and no config env vars yields the documented defaults."""
    values = read_settings_in_subprocess(tmp_path)
    assert values["LLM_PROVIDER"] == "claude"
    assert values["ANTHROPIC_API_KEY"] == ""
    assert values["CLAUDE_MODEL"] == "claude-sonnet-4-20250514"
    assert values["GEMINI_API_KEY"] == ""
    assert values["GEMINI_MODEL"] == "gemini-2.5-flash"
    assert values["DATABASE"] == "app.db"


def test_dotenv_fills_gap(tmp_path):
    """A value present only in .env is visible via settings."""
    values = read_settings_in_subprocess(tmp_path, dotenv_text="LLM_PROVIDER=gemini\n")
    assert values["LLM_PROVIDER"] == "gemini"


def test_process_env_overrides_dotenv(tmp_path):
    """Process env wins over .env for the same variable."""
    values = read_settings_in_subprocess(
        tmp_path,
        dotenv_text="ANTHROPIC_API_KEY=fromdotenv\n",
        extra_env={"ANTHROPIC_API_KEY": "fromshell"},
    )
    assert values["ANTHROPIC_API_KEY"] == "fromshell"


def test_database_overridable_via_env(tmp_path):
    """DATABASE resolves from the process environment."""
    values = read_settings_in_subprocess(
        tmp_path, extra_env={"DATABASE": "/tmp/probe.db"}
    )
    assert values["DATABASE"] == "/tmp/probe.db"


ENV_EXAMPLE_KEY = re.compile(r"^([A-Z_][A-Z0-9_]*)=")
SETTINGS_KEY = re.compile(r'os\.environ\.get\(\s*["\']([A-Z_][A-Z0-9_]*)["\']')


def test_env_example_matches_settings_keys():
    """.env.example and settings.py must declare the same variable names."""
    example_keys = set()
    for line in (PROJECT_ROOT / ".env.example").read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = ENV_EXAMPLE_KEY.match(stripped)
        if match:
            example_keys.add(match.group(1))

    settings_keys = set(SETTINGS_KEY.findall((PROJECT_ROOT / "settings.py").read_text()))

    assert example_keys == settings_keys, (
        "drift between .env.example and settings.py: "
        f"only in .env.example={example_keys - settings_keys}, "
        f"only in settings.py={settings_keys - example_keys}"
    )
