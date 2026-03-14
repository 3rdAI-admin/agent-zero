"""Tests for python/helpers/tool_policy.py — tool execution policy (AUTON-04, AUTON-06)."""

import os
from unittest.mock import patch


from python.helpers import tool_policy


class TestDisabledTools:
    """Tool disable/enable via governance policy."""

    def test_no_config_all_allowed(self):
        """Expected use: no config file = all tools allowed."""
        with patch.object(tool_policy, "_load_config", return_value={}):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("AGENTZ_DISABLED_TOOLS", None)
                allowed, reason = tool_policy.is_tool_allowed("code_execution_tool")
        assert allowed is True
        assert reason == ""

    def test_disabled_by_config(self, tmp_path):
        """Expected use: tool listed in disabled_tools is blocked."""
        config = {"disabled_tools": ["browser_agent", "dangerous_tool"]}
        with patch.object(tool_policy, "_load_config", return_value=config):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("AGENTZ_DISABLED_TOOLS", None)
                allowed, reason = tool_policy.is_tool_allowed("browser_agent")
        assert allowed is False
        assert "browser_agent" in reason

    def test_disabled_by_env(self):
        """Expected use: AGENTZ_DISABLED_TOOLS env disables tools."""
        with patch.object(tool_policy, "_load_config", return_value={}):
            with patch.dict(
                os.environ,
                {"AGENTZ_DISABLED_TOOLS": "browser_agent,ssh_tool"},
                clear=False,
            ):
                allowed, _ = tool_policy.is_tool_allowed("browser_agent")
                allowed2, _ = tool_policy.is_tool_allowed("code_execution_tool")
        assert allowed is False
        assert allowed2 is True

    def test_env_and_config_merged(self):
        """Edge case: disabled tools from both sources are merged."""
        config = {"disabled_tools": ["tool_a"]}
        with patch.object(tool_policy, "_load_config", return_value=config):
            with patch.dict(
                os.environ, {"AGENTZ_DISABLED_TOOLS": "tool_b"}, clear=False
            ):
                disabled = tool_policy.get_disabled_tools()
        assert "tool_a" in disabled
        assert "tool_b" in disabled


class TestRestrictedPaths:
    """Path-based restrictions from governance policy."""

    def test_no_restrictions(self):
        """Expected use: no restricted paths = all paths allowed."""
        with patch.object(tool_policy, "_load_config", return_value={}):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("AGENTZ_RESTRICTED_PATHS", None)
                restricted, _ = tool_policy.is_path_restricted("/etc/passwd")
        assert restricted is False

    def test_restricted_by_config(self):
        """Expected use: path matching restricted prefix is blocked."""
        config = {"restricted_paths": ["/etc/shadow", "/root/.ssh"]}
        with patch.object(tool_policy, "_load_config", return_value=config):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("AGENTZ_RESTRICTED_PATHS", None)
                restricted, reason = tool_policy.is_path_restricted("/etc/shadow")
        assert restricted is True
        assert "/etc/shadow" in reason

    def test_restricted_by_env(self):
        """Expected use: AGENTZ_RESTRICTED_PATHS env blocks paths."""
        with patch.object(tool_policy, "_load_config", return_value={}):
            with patch.dict(
                os.environ,
                {"AGENTZ_RESTRICTED_PATHS": "/etc/shadow,/root/.ssh"},
                clear=False,
            ):
                restricted, _ = tool_policy.is_path_restricted("/root/.ssh/id_rsa")
        assert restricted is True

    def test_non_matching_path_allowed(self):
        """Edge case: path not matching any prefix is allowed."""
        config = {"restricted_paths": ["/etc/shadow"]}
        with patch.object(tool_policy, "_load_config", return_value=config):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("AGENTZ_RESTRICTED_PATHS", None)
                restricted, _ = tool_policy.is_path_restricted("/tmp/safe.txt")
        assert restricted is False


class TestBrowserDomainPolicy:
    """Browser domain allowlist from governance policy."""

    def test_no_domains_all_allowed(self):
        """Expected use: no browser.allowed_domains = unrestricted."""
        with patch.object(tool_policy, "_load_config", return_value={}):
            allowed, _ = tool_policy.is_domain_allowed("https://evil.com/page")
        assert allowed is True

    def test_domain_in_allowlist(self):
        """Expected use: matching domain is allowed."""
        config = {"browser": {"allowed_domains": ["*.example.com", "localhost"]}}
        with patch.object(tool_policy, "_load_config", return_value=config):
            allowed, _ = tool_policy.is_domain_allowed("https://api.example.com/data")
        assert allowed is True

    def test_domain_not_in_allowlist(self):
        """Failure case: non-matching domain is blocked."""
        config = {"browser": {"allowed_domains": ["*.example.com"]}}
        with patch.object(tool_policy, "_load_config", return_value=config):
            allowed, reason = tool_policy.is_domain_allowed("https://evil.com/steal")
        assert allowed is False
        assert "evil.com" in reason

    def test_localhost_allowed(self):
        """Edge case: localhost matches exactly."""
        config = {"browser": {"allowed_domains": ["localhost"]}}
        with patch.object(tool_policy, "_load_config", return_value=config):
            allowed, _ = tool_policy.is_domain_allowed("http://localhost:8080/app")
        assert allowed is True
