"""Shell-rc detection tests for setup.sh."""

import subprocess
from pathlib import Path


SETUP_SH = Path(__file__).resolve().parent.parent / "setup.sh"


def run_detection(home, env_overrides, shell, provider):
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin", **env_overrides}
    cmd = (
        f'source "{SETUP_SH}" >/dev/null 2>&1; '
        f'find_existing_key "{provider}" "{shell}"; '
        f'printf "%s\\n%s\\n" "$EXISTING_KEY" "$EXISTING_KEY_SOURCE"'
    )
    result = subprocess.run(
        ["bash", "-c", cmd],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"bash exited {result.returncode}: {result.stderr}"
    lines = result.stdout.split("\n")
    return lines[0], lines[1]


def run_preflight(home, env_overrides, shell):
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin", **env_overrides}
    rc_target = f"{home}/.{shell}rc"
    cmd = (
        f'source "{SETUP_SH}" >/dev/null 2>&1; '
        f'rc_target="{rc_target}"; '
        f'rc_content="$(read_rc_content "$rc_target")"; '
        f'render_preflight_summary "$rc_content" "$HOME/.{shell}rc" "$rc_target" "{shell}"'
    )
    result = subprocess.run(
        ["bash", "-c", cmd],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"bash exited {result.returncode}: {result.stderr}"
    return result.stdout + result.stderr


def run_replace_warning(home, source, rc_target, key_var):
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}
    cmd = (
        f'source "{SETUP_SH}" >/dev/null 2>&1; '
        f'render_replace_warning "{source}" "{rc_target}" "{key_var}"'
    )
    result = subprocess.run(
        ["bash", "-c", cmd],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"bash exited {result.returncode}: {result.stderr}"
    return result.stdout + result.stderr


def run_current_shell(home, shell_env):
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}
    if shell_env is not None:
        env["SHELL"] = shell_env
    cmd = (
        f'source "{SETUP_SH}" >/dev/null 2>&1; '
        f'find_current_shell'
    )
    result = subprocess.run(
        ["bash", "-c", cmd],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"bash exited {result.returncode}: {result.stderr}"
    return result.stdout


class TestFindCurrentShell:
    def test_shell_env_zsh(self, tmp_path):
        assert run_current_shell(tmp_path, "/bin/zsh") == "zsh"

    def test_shell_env_bash(self, tmp_path):
        assert run_current_shell(tmp_path, "/bin/bash") == "bash"

    def test_shell_env_zsh_unusual_path(self, tmp_path):
        assert run_current_shell(tmp_path, "/opt/homebrew/bin/zsh") == "zsh"

    def test_shell_env_unset_falls_back(self, tmp_path):
        result = run_current_shell(tmp_path, None)
        assert result in ("zsh", "bash")


class TestFindExistingKey:
    def test_key_in_zshenv_only(self, tmp_path):
        (tmp_path / ".zshenv").write_text('export ANTHROPIC_API_KEY="sk-ant-AAAA0001"\n')
        value, source = run_detection(tmp_path, {"ANTHROPIC_API_KEY": "sk-ant-AAAA0001"}, "zsh", "claude")
        assert value == "sk-ant-AAAA0001"
        assert source.endswith(".zshenv")

    def test_no_key_anywhere(self, tmp_path):
        value, source = run_detection(tmp_path, {}, "zsh", "claude")
        assert value == ""
        assert source == ""

    def test_key_in_zshrc(self, tmp_path):
        (tmp_path / ".zshrc").write_text('export ANTHROPIC_API_KEY="sk-ant-BBBB0002"\n')
        value, source = run_detection(tmp_path, {}, "zsh", "claude")
        assert value == "sk-ant-BBBB0002"
        assert source.endswith(".zshrc")

    def test_key_in_env_only(self, tmp_path):
        value, source = run_detection(tmp_path, {"ANTHROPIC_API_KEY": "sk-ant-CCCC0003"}, "zsh", "claude")
        assert value == "sk-ant-CCCC0003"
        assert source == "live env only"

    def test_zshenv_precedes_zshrc(self, tmp_path):
        (tmp_path / ".zshenv").write_text('export ANTHROPIC_API_KEY="sk-ant-EEEE0001"\n')
        (tmp_path / ".zshrc").write_text('export ANTHROPIC_API_KEY="sk-ant-FFFF0002"\n')
        value, source = run_detection(tmp_path, {}, "zsh", "claude")
        assert value == "sk-ant-EEEE0001"
        assert source.endswith(".zshenv")

    def test_bash_candidates(self, tmp_path):
        (tmp_path / ".bash_profile").write_text('export ANTHROPIC_API_KEY="sk-ant-DDDD0004"\n')
        value, source = run_detection(tmp_path, {}, "bash", "claude")
        assert value == "sk-ant-DDDD0004"
        assert source.endswith(".bash_profile")

    def test_gemini_provider_routes_to_gemini_key(self, tmp_path):
        (tmp_path / ".zshrc").write_text('export GEMINI_API_KEY="g-test-7777"\n')
        value, source = run_detection(tmp_path, {}, "zsh", "gemini")
        assert value == "g-test-7777"
        assert source.endswith(".zshrc")


class TestPreflightSummary:
    def test_preflight_shows_zshenv_source(self, tmp_path):
        (tmp_path / ".zshenv").write_text('export ANTHROPIC_API_KEY="sk-ant-AAAA0001"\n')
        out = run_preflight(tmp_path, {"ANTHROPIC_API_KEY": "sk-ant-AAAA0001"}, "zsh")
        assert "(from ~/.zshenv)" in out
        assert "ANTHROPIC_API_KEY:" in out

    def test_preflight_live_env_only(self, tmp_path):
        out = run_preflight(tmp_path, {"ANTHROPIC_API_KEY": "sk-ant-CCCC0003"}, "zsh")
        assert "(live env only)" in out

    def test_preflight_heading_renamed(self, tmp_path):
        out = run_preflight(tmp_path, {}, "zsh")
        assert "Detected configuration:" in out
        assert "Current configuration in" not in out

    def test_preflight_write_target_line(self, tmp_path):
        out = run_preflight(tmp_path, {}, "zsh")
        assert "Write target:" in out
        assert "~/.zshrc" in out

    def test_preflight_mismatch(self, tmp_path):
        (tmp_path / ".zshrc").write_text('export LLM_PROVIDER="gemini"\n')
        out = run_preflight(tmp_path, {}, "zsh")
        assert "Mismatch: LLM_PROVIDER says gemini but no GEMINI_API_KEY found. Setup will fix this." in out

    def test_preflight_duplicate_warning(self, tmp_path):
        (tmp_path / ".zshrc").write_text(
            'export ANTHROPIC_API_KEY="sk-ant-1111"\n'
            'export ANTHROPIC_API_KEY="sk-ant-2222"\n'
        )
        out = run_preflight(tmp_path, {}, "zsh")
        assert "Found 2 duplicate ANTHROPIC_API_KEY lines" in out
        assert "will collapse to one on save" in out


class TestReplaceWarning:
    def test_warns_when_source_differs(self, tmp_path):
        out = run_replace_warning(
            tmp_path,
            f"{tmp_path}/.zshenv",
            f"{tmp_path}/.zshrc",
            "ANTHROPIC_API_KEY",
        )
        assert "Existing key is exported from" in out
        assert ".zshenv" in out
        assert ".zshrc" in out

    def test_silent_when_source_equals_target(self, tmp_path):
        out = run_replace_warning(
            tmp_path,
            f"{tmp_path}/.zshrc",
            f"{tmp_path}/.zshrc",
            "ANTHROPIC_API_KEY",
        )
        assert "New key will be written" not in out

    def test_silent_when_source_is_live_env(self, tmp_path):
        out = run_replace_warning(
            tmp_path,
            "live env only",
            f"{tmp_path}/.zshrc",
            "ANTHROPIC_API_KEY",
        )
        assert "New key will be written" not in out

    def test_silent_when_source_symlinks_to_target(self, tmp_path):
        actual = tmp_path / "dotfiles" / "zshrc"
        actual.parent.mkdir()
        actual.write_text('export ANTHROPIC_API_KEY="sk-ant-9999"\n')
        symlink = tmp_path / ".zshrc"
        symlink.symlink_to(actual)
        out = run_replace_warning(
            tmp_path,
            str(symlink),
            str(actual),
            "ANTHROPIC_API_KEY",
        )
        assert "New key will be written" not in out
