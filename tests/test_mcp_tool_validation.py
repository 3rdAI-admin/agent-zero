"""Tests for MCP tool-name validation at the dispatch layer.

Covers:
- MCPConfig.get_server_names() and get_tool_names() helpers
- Agent._mcp_tool_not_found_message() targeted correction
- Dispatch guard: dot-separated names bypass Unknown fallback
"""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import agent as agent_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _DummyPrinter:
    def __init__(self, *args, **kwargs):
        pass

    def print(self, *args, **kwargs):
        pass

    def stream(self, *args, **kwargs):
        pass


def _build_agent():
    """Create a minimal Agent instance for unit testing."""
    test_agent = agent_module.Agent.__new__(agent_module.Agent)
    test_agent.agent_name = "A0"
    test_agent.last_user_message = None
    test_agent.intervention = None
    test_agent.data = {}
    test_agent.context = SimpleNamespace(
        streaming_agent=None,
        task=SimpleNamespace(is_alive=lambda: True),
        log=SimpleNamespace(log=lambda *args, **kwargs: None),
    )
    test_agent.history = []
    return test_agent


def _mock_mcp_config(servers: dict[str, list[str]]):
    """Return a mock MCPConfig with given servers and tool names.

    Args:
        servers: mapping of server_name -> list of tool names.
    """
    mock = MagicMock()
    mock.get_server_names.return_value = list(servers.keys())

    def _get_tool_names(server_name=""):
        if server_name:
            return list(servers.get(server_name, []))
        names = []
        for sname, tools in servers.items():
            for t in tools:
                names.append(f"{sname}.{t}")
        return names

    mock.get_tool_names.side_effect = _get_tool_names
    mock.has_tool.return_value = False
    mock.get_tool.return_value = None
    return mock


# ---------------------------------------------------------------------------
# MCPConfig.get_server_names / get_tool_names unit tests
# ---------------------------------------------------------------------------


class TestMCPConfigHelpers:
    """Tests for the new lightweight helpers on MCPConfig."""

    @staticmethod
    def _make_cfg(servers):
        """Build an MCPConfig-like object using the real methods but mock servers."""
        from python.helpers.mcp_handler import MCPConfig

        cfg = MagicMock(spec=MCPConfig)
        cfg.servers = servers
        # Bind the real methods so we test actual logic
        import threading

        lock = threading.Lock()
        cfg._MCPConfig__lock = lock

        # Bind real implementations
        cfg.get_server_names = lambda: MCPConfig.get_server_names.__get__(
            cfg, type(cfg)
        )()
        cfg.get_tool_names = lambda server_name="": MCPConfig.get_tool_names.__get__(
            cfg, type(cfg)
        )(server_name)
        return cfg

    def test_get_server_names_returns_names(self):
        server1 = MagicMock()
        server1.name = "google_workspace"
        server2 = MagicMock()
        server2.name = "archon"
        cfg = self._make_cfg([server1, server2])

        assert cfg.get_server_names() == ["google_workspace", "archon"]

    def test_get_tool_names_all_servers(self):
        server1 = MagicMock()
        server1.name = "srv"
        server1.get_tools.return_value = [{"name": "tool_a"}, {"name": "tool_b"}]
        cfg = self._make_cfg([server1])

        result = cfg.get_tool_names()
        assert result == ["srv.tool_a", "srv.tool_b"]

    def test_get_tool_names_single_server(self):
        server1 = MagicMock()
        server1.name = "srv"
        server1.get_tools.return_value = [{"name": "tool_a"}, {"name": "tool_b"}]
        server2 = MagicMock()
        server2.name = "other"
        server2.get_tools.return_value = [{"name": "tool_c"}]
        cfg = self._make_cfg([server1, server2])

        result = cfg.get_tool_names("srv")
        assert result == ["tool_a", "tool_b"]

    def test_get_tool_names_unknown_server_returns_empty(self):
        cfg = self._make_cfg([])
        assert cfg.get_tool_names("nonexistent") == []


# ---------------------------------------------------------------------------
# Agent._mcp_tool_not_found_message tests
# ---------------------------------------------------------------------------


class TestMCPToolNotFoundMessage:
    """Tests for the targeted correction message builder."""

    def test_known_server_unknown_tool(self):
        agent = _build_agent()
        mock_cfg = _mock_mcp_config(
            {
                "google_workspace": ["send_gmail_message", "search_drive_files"],
            }
        )
        with patch(
            "python.helpers.mcp_handler.MCPConfig.get_instance",
            return_value=mock_cfg,
        ):
            msg = agent._mcp_tool_not_found_message("google_workspace.nonexistent_tool")

        assert "Unknown MCP tool" in msg
        assert "google_workspace" in msg
        assert "send_gmail_message" in msg
        assert "search_drive_files" in msg

    def test_unknown_server(self):
        agent = _build_agent()
        mock_cfg = _mock_mcp_config(
            {
                "google_workspace": ["send_gmail_message"],
                "archon": ["list_tasks"],
            }
        )
        with patch(
            "python.helpers.mcp_handler.MCPConfig.get_instance",
            return_value=mock_cfg,
        ):
            msg = agent._mcp_tool_not_found_message("fake_server.some_tool")

        assert "Unknown MCP server" in msg
        assert "fake_server" in msg
        assert "google_workspace" in msg
        assert "archon" in msg

    def test_mcp_import_failure_graceful(self):
        """When MCP handler is unavailable, return a safe fallback message."""
        agent = _build_agent()
        with patch(
            "python.helpers.mcp_handler.MCPConfig.get_instance",
            side_effect=RuntimeError("not initialized"),
        ):
            msg = agent._mcp_tool_not_found_message("srv.tool")

        assert "Unknown tool" in msg
        assert "srv.tool" in msg

    def test_empty_server_tools(self):
        """Server exists but has no tools (e.g., initialization pending)."""
        agent = _build_agent()
        mock_cfg = _mock_mcp_config({"google_workspace": []})
        with patch(
            "python.helpers.mcp_handler.MCPConfig.get_instance",
            return_value=mock_cfg,
        ):
            msg = agent._mcp_tool_not_found_message("google_workspace.anything")

        assert "Unknown MCP tool" in msg
        assert "(none)" in msg
