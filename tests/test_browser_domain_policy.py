"""Tests for browser domain policy enforcement (Phase 2d).

Covers:
- _resolve_allowed_domains() priority: env > policy file > defaults
- BROWSER_ALLOW_ALL escape hatch
- Navigation logging via audit_log
- Default domain list is non-empty and reasonable
- Domain allowlist is wired into BrowserProfile (not hardcoded wildcard)

Note: browser_use is only available inside the Docker container, so we mock
it at the module level before importing browser_agent.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Mock the browser_use package tree (only available inside Docker container).
# Must be done before any project imports because the import chain reaches
# browser_use_monkeypatch.py which needs browser_use.llm submodule, and
# python.helpers.browser_use needs a `browser_use` attribute injected.
_mock_bu = MagicMock()
for mod_name in [
    "browser_use",
    "browser_use.llm",
    "browser_use.agent",
    "browser_use.browser",
    "browser_use.controller",
]:
    sys.modules.setdefault(mod_name, _mock_bu)

# The helper module python.helpers.browser_use gets `browser_use` as an
# attribute when the real package is installed. Patch it for host-side testing.
import python.helpers.browser_use as _bu_helper

if not hasattr(_bu_helper, "browser_use"):
    _bu_helper.browser_use = _mock_bu  # type: ignore[attr-defined]

from python.tools.browser_agent import (
    DEFAULT_BROWSER_DOMAINS,
    _log_navigation,
    _resolve_allowed_domains,
)


class TestResolveAllowedDomains:
    """_resolve_allowed_domains() should follow priority: env > policy > defaults."""

    def test_defaults_when_no_config(self):
        """With no env var and no policy file, returns DEFAULT_BROWSER_DOMAINS."""
        with (
            patch.dict(os.environ, {}, clear=False),
            patch(
                "python.tools.browser_agent.get_browser_allowed_domains",
                return_value=[],
            ),
        ):
            os.environ.pop("BROWSER_ALLOW_ALL", None)
            result = _resolve_allowed_domains()

        assert result == DEFAULT_BROWSER_DOMAINS
        assert len(result) > 10
        assert "*.google.com" in result
        assert "localhost" in result

    def test_policy_file_overrides_defaults(self):
        """When tool_policy.json has browser.allowed_domains, use those."""
        policy_domains = ["*.example.com", "*.internal.corp"]
        with (
            patch.dict(os.environ, {}, clear=False),
            patch(
                "python.tools.browser_agent.get_browser_allowed_domains",
                return_value=policy_domains,
            ),
        ):
            os.environ.pop("BROWSER_ALLOW_ALL", None)
            result = _resolve_allowed_domains()

        assert result == policy_domains

    def test_browser_allow_all_env_var(self):
        """BROWSER_ALLOW_ALL=true should return wildcard."""
        with patch.dict(os.environ, {"BROWSER_ALLOW_ALL": "true"}, clear=False):
            result = _resolve_allowed_domains()

        assert result == ["*"]

    def test_browser_allow_all_case_insensitive(self):
        """BROWSER_ALLOW_ALL should be case-insensitive."""
        with patch.dict(os.environ, {"BROWSER_ALLOW_ALL": "True"}, clear=False):
            result = _resolve_allowed_domains()

        assert result == ["*"]

    def test_browser_allow_all_false_ignored(self):
        """BROWSER_ALLOW_ALL=false should not enable wildcard."""
        with (
            patch.dict(os.environ, {"BROWSER_ALLOW_ALL": "false"}, clear=False),
            patch(
                "python.tools.browser_agent.get_browser_allowed_domains",
                return_value=[],
            ),
        ):
            result = _resolve_allowed_domains()

        assert result != ["*"]
        assert len(result) > 1


class TestDefaultDomainList:
    """DEFAULT_BROWSER_DOMAINS should be reasonable and well-formed."""

    def test_contains_essential_domains(self):
        essential = [
            "*.google.com",
            "*.github.com",
            "*.stackoverflow.com",
            "*.wikipedia.org",
            "*.python.org",
            "localhost",
        ]
        for domain in essential:
            assert domain in DEFAULT_BROWSER_DOMAINS, f"Missing essential: {domain}"

    def test_no_wildcard_in_defaults(self):
        """Defaults should NOT include bare '*' — that defeats the purpose."""
        assert "*" not in DEFAULT_BROWSER_DOMAINS

    def test_all_entries_are_strings(self):
        for entry in DEFAULT_BROWSER_DOMAINS:
            assert isinstance(entry, str)
            assert len(entry) > 0


class TestNavigationLogging:
    """_log_navigation should write structured events to audit_log."""

    def test_logs_allowed_navigation(self):
        with patch("python.tools.browser_agent.audit_log.write") as mock_write:
            _log_navigation(
                url="https://example.com/page",
                domain="example.com",
                allowed=True,
                context_id="ctx-123",
                agent_name="Agent 0",
            )

        mock_write.assert_called_once_with(
            "browser_navigation",
            tool_name="browser_agent",
            agent_name="Agent 0",
            context_id="ctx-123",
            details={
                "url": "https://example.com/page",
                "domain": "example.com",
                "allowed": True,
            },
        )

    def test_logs_blocked_navigation(self):
        with patch("python.tools.browser_agent.audit_log.write") as mock_write:
            _log_navigation(
                url="https://evil.com/hack",
                domain="evil.com",
                allowed=False,
                context_id="ctx-456",
                agent_name="Agent 1",
            )

        call_kwargs = mock_write.call_args
        assert call_kwargs[1]["details"]["allowed"] is False
        assert call_kwargs[1]["details"]["domain"] == "evil.com"

    def test_long_url_truncated(self):
        long_url = "https://example.com/" + "a" * 1000

        with patch("python.tools.browser_agent.audit_log.write") as mock_write:
            _log_navigation(
                url=long_url,
                domain="example.com",
                allowed=True,
            )

        logged_url = mock_write.call_args[1]["details"]["url"]
        assert len(logged_url) <= 500


class TestDomainAllowlistIntegration:
    """Verify allowed_domains is no longer hardcoded to wildcard."""

    def test_no_hardcoded_wildcard_in_source(self):
        """The source should not contain the old hardcoded wildcard pattern."""
        import inspect
        from python.tools.browser_agent import State

        source = inspect.getsource(State._initialize)
        assert '["*", "http://*", "https://*"]' not in source
        assert "_resolve_allowed_domains()" in source

    def test_resolve_returns_list(self):
        """_resolve_allowed_domains always returns a list."""
        with (
            patch.dict(os.environ, {}, clear=False),
            patch(
                "python.tools.browser_agent.get_browser_allowed_domains",
                return_value=[],
            ),
        ):
            os.environ.pop("BROWSER_ALLOW_ALL", None)
            result = _resolve_allowed_domains()

        assert isinstance(result, list)
        assert all(isinstance(d, str) for d in result)


class TestToolPolicyDomainChecker:
    """Verify tool_policy.is_domain_allowed works correctly."""

    def test_allowed_domain(self):
        from python.helpers.tool_policy import is_domain_allowed

        with patch(
            "python.helpers.tool_policy.get_browser_allowed_domains",
            return_value=["*.google.com", "localhost"],
        ):
            allowed, reason = is_domain_allowed("https://www.google.com/search")
            assert allowed is True

    def test_blocked_domain(self):
        from python.helpers.tool_policy import is_domain_allowed

        with patch(
            "python.helpers.tool_policy.get_browser_allowed_domains",
            return_value=["*.google.com", "localhost"],
        ):
            allowed, reason = is_domain_allowed("https://evil.com/hack")
            assert allowed is False
            assert "evil.com" in reason

    def test_no_domains_configured_allows_all(self):
        from python.helpers.tool_policy import is_domain_allowed

        with patch(
            "python.helpers.tool_policy.get_browser_allowed_domains",
            return_value=[],
        ):
            allowed, reason = is_domain_allowed("https://anything.com")
            assert allowed is True

    def test_invalid_url(self):
        from python.helpers.tool_policy import is_domain_allowed

        with patch(
            "python.helpers.tool_policy.get_browser_allowed_domains",
            return_value=["*.google.com"],
        ):
            allowed, reason = is_domain_allowed("")
            assert allowed is False
