"""Tests for python/helpers/host_control.py — bounded host control (AUTON-04, AUTON-06)."""

import json
import os
from unittest.mock import patch


from python.helpers.host_control import (
    get_host_control_config,
    is_terminal_command_allowed,
)


class TestGetHostControlConfig:
    """Loading policy from env and file."""

    def test_permissive_default_no_file_no_env(self):
        """Expected use: no config yields permissive."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove env vars that might be set
            for key in list(os.environ.keys()):
                if key.startswith("AGENTZ_HOST_CONTROL"):
                    del os.environ[key]
        policy, allow, deny = get_host_control_config()
        assert policy == "permissive"
        assert allow == []
        assert deny == []

    def test_env_overrides_policy(self):
        """Env AGENTZ_HOST_CONTROL_POLICY sets policy."""
        with patch.dict(
            os.environ,
            {
                "AGENTZ_HOST_CONTROL_POLICY": "allowlist",
                "AGENTZ_HOST_CONTROL_ALLOWLIST": "ls,cat",
            },
            clear=False,
        ):
            policy, allow, deny = get_host_control_config()
        assert policy == "allowlist"
        assert "ls" in allow
        assert "cat" in allow

    def test_file_config(self, tmp_path):
        """Expected use: JSON file sets policy and lists."""
        config_file = tmp_path / "host_control.json"
        config_file.write_text(
            json.dumps(
                {"policy": "deny", "allowlist": ["ls"], "denylist": ["rm -rf", "sudo"]}
            )
        )
        with patch(
            "python.helpers.host_control._config_path", return_value=str(config_file)
        ):
            policy, allow, deny = get_host_control_config()
        assert policy == "deny"
        assert "ls" in allow
        assert "rm -rf" in deny
        assert "sudo" in deny


class TestIsTerminalCommandAllowed:
    """Command check against policy."""

    def test_permissive_allows_any(self):
        """Permissive: any command allowed."""
        with patch("python.helpers.host_control.get_host_control_config") as m:
            m.return_value = ("permissive", [], [])
            allowed, _ = is_terminal_command_allowed("rm -rf /")
        assert allowed is True

    def test_allowlist_allows_only_listed(self):
        """Allowlist: only commands matching prefix allowed."""
        with patch("python.helpers.host_control.get_host_control_config") as m:
            m.return_value = ("allowlist", ["ls", "cat ", "echo"], [])
            allowed, _ = is_terminal_command_allowed("ls -la")
            assert allowed is True
            allowed, _ = is_terminal_command_allowed("echo hello")
            assert allowed is True
            allowed, reason = is_terminal_command_allowed("rm -rf /")
            assert allowed is False
            assert "allowlist" in reason.lower()

    def test_allowlist_empty_denies_all(self):
        """Allowlist with empty list: no terminal commands allowed."""
        with patch("python.helpers.host_control.get_host_control_config") as m:
            m.return_value = ("allowlist", [], [])
            allowed, reason = is_terminal_command_allowed("ls")
            assert allowed is False
            assert "no entries" in reason.lower() or "disabled" in reason.lower()

    def test_deny_blocks_denylist_prefix(self):
        """Deny policy: commands matching denylist are blocked."""
        with patch("python.helpers.host_control.get_host_control_config") as m:
            m.return_value = ("deny", [], ["rm -rf", "sudo"])
            allowed, _ = is_terminal_command_allowed("ls")
            assert allowed is True
            allowed, reason = is_terminal_command_allowed("rm -rf /tmp")
            assert allowed is False
            assert "denied" in reason.lower() or "rm -rf" in reason
            allowed, _ = is_terminal_command_allowed("sudo apt update")
            assert allowed is False

    def test_empty_command_denied(self):
        """Edge case: empty command is not allowed."""
        with patch("python.helpers.host_control.get_host_control_config") as m:
            m.return_value = ("permissive", [], [])
            allowed, reason = is_terminal_command_allowed("   ")
            assert allowed is False
            assert "empty" in reason.lower()
