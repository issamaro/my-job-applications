"""Tests for setup.sh's .env writer functions."""

import subprocess
from pathlib import Path


SETUP_SH = Path(__file__).resolve().parent.parent / "setup.sh"


def run_function(script, env_overrides=None, path_prefix=None):
    """Source setup.sh in a clean shell and run a snippet against its functions.

    The __main__ block is guarded by BASH_SOURCE == $0, so sourcing defines the
    functions without triggering the dependency install. Multi-line inputs are
    passed via env so no shell quoting has to survive.
    """
    path = "/usr/bin:/bin"
    if path_prefix:
        path = f"{path_prefix}:{path}"
    env = {"HOME": "/tmp", "PATH": path}
    if env_overrides:
        env.update(env_overrides)
    cmd = f'source "{SETUP_SH}" >/dev/null 2>&1; {script}'
    result = subprocess.run(
        ["bash", "-c", cmd],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"bash exited {result.returncode}: {result.stderr}"
    return result.stdout


class TestCreateEnvContent:
    def test_empty_input_claude_and_key(self):
        out = run_function(
            'create_env_content "$EXISTING" "claude" "$KEY"',
            env_overrides={"EXISTING": "", "KEY": "sk-ant-TESTKEY99"},
        )
        assert "LLM_PROVIDER=claude" in out
        assert "ANTHROPIC_API_KEY=sk-ant-TESTKEY99" in out

    def test_preserves_other_lines_and_no_duplicate_provider(self):
        existing = "DATABASE=custom.db\nLLM_PROVIDER=claude\nANTHROPIC_API_KEY=old\n"
        out = run_function(
            'create_env_content "$EXISTING" "gemini" "$KEY"',
            env_overrides={"EXISTING": existing, "KEY": "g-NEWKEY"},
        )
        assert "DATABASE=custom.db" in out
        assert "LLM_PROVIDER=gemini" in out
        assert "GEMINI_API_KEY=g-NEWKEY" in out
        assert out.count("LLM_PROVIDER=") == 1

    def test_empty_key_preserves_existing_key(self):
        existing = "LLM_PROVIDER=claude\nANTHROPIC_API_KEY=sk-keepme\n"
        out = run_function(
            'create_env_content "$EXISTING" "claude" ""',
            env_overrides={"EXISTING": existing},
        )
        assert "ANTHROPIC_API_KEY=sk-keepme" in out


class TestReadKeyFromPass:
    def test_returns_pass_secret_when_stubbed(self, tmp_path):
        bindir = tmp_path / "bin"
        bindir.mkdir()
        stub = bindir / "pass"
        stub.write_text("#!/bin/bash\necho 'stub-secret-1234'\n")
        stub.chmod(0o755)
        out = run_function("read_key_from_pass claude", path_prefix=str(bindir))
        assert out.strip() == "stub-secret-1234"

    def test_empty_when_pass_absent(self):
        out = run_function("read_key_from_pass claude")
        assert out.strip() == ""


class TestWriteEnvAtomic:
    def test_writes_content_with_mode_600(self, tmp_path):
        target = tmp_path / ".env"
        run_function(
            'write_env_atomic "$CONTENT" "$TARGET"',
            env_overrides={"CONTENT": "LLM_PROVIDER=claude\nANTHROPIC_API_KEY=sk-x", "TARGET": str(target)},
        )
        assert target.read_text() == "LLM_PROVIDER=claude\nANTHROPIC_API_KEY=sk-x"
        assert oct(target.stat().st_mode & 0o777) == "0o600"
