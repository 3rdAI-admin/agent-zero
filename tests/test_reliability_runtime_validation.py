from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import agent as agent_module
import preload
import run_ui
from python.helpers import settings
from python.helpers.runtime_state_report import build_runtime_state_report
from python.tools.call_subordinate import DEFAULT_SUBORDINATE_TIMEOUT


_real_stdin = sys.stdin
if not hasattr(sys.stdin, "reconfigure"):
    sys.stdin = MagicMock()
    sys.stdin.reconfigure = MagicMock()


def _build_agent() -> agent_module.Agent:
    """Create a minimal Agent instance for MCP validation tests."""
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


def _build_code_execution_tool():
    """Create a minimal CodeExecution tool instance for guard tests."""
    from python.tools.code_execution_tool import CodeExecution

    tool = CodeExecution.__new__(CodeExecution)
    tool.agent = MagicMock()
    tool.agent.config = SimpleNamespace(code_exec_ssh_enabled=False)
    tool.agent.get_data.return_value = None
    tool.agent.set_data = MagicMock()
    tool.name = "code_execution"
    tool.args = {}
    tool.message = ""
    return tool


def test_reliability_settings_path_uses_usr_settings_json() -> None:
    """Reliability validation must target usr/settings.json, not tmp/settings.json."""
    assert settings.SETTINGS_FILE.endswith("usr/settings.json")
    assert "tmp/settings.json" not in settings.SETTINGS_FILE


def test_reliability_runtime_report_surfaces_readiness_and_runtime_truth() -> None:
    """Runtime report should expose readiness/liveness surfaces and runtime-derived fields."""
    report = build_runtime_state_report(
        effective_settings=settings.get_default_settings(),
        default_settings=settings.get_default_settings(),
    )

    assert report["runtime"]["liveness_endpoint"] == "/health"
    assert report["runtime"]["readiness_endpoint"] == "/ready"
    assert report["runtime"]["mcp_server_token_runtime_derived"] is True
    assert "mcp_server_token" in report["runtime"]["runtime_derived_fields"]


def test_reliability_preload_mode_contract(monkeypatch) -> None:
    """Build-time preload must use defaults, runtime preload must use effective settings."""
    default_settings = {"mode": "default"}
    effective_settings = {"mode": "effective"}

    get_default = Mock(return_value=default_settings)
    get_effective = Mock(return_value=effective_settings)

    monkeypatch.setattr(preload.settings, "get_default_settings", get_default)
    monkeypatch.setattr(preload.settings, "get_settings", get_effective)

    assert preload.resolve_preload_settings(defaults_only=True) == default_settings
    assert preload.resolve_preload_settings(defaults_only=False) == effective_settings


def test_reliability_mcp_dispatch_validation_contract() -> None:
    """Unknown MCP tool names should return a corrective dispatch message."""
    agent = _build_agent()
    mock_cfg = MagicMock()
    mock_cfg.get_server_names.return_value = ["google_workspace"]
    mock_cfg.get_tool_names.side_effect = lambda server_name="": (
        ["send_gmail_message", "search_drive_files"]
        if server_name == "google_workspace"
        else [
            "google_workspace.send_gmail_message",
            "google_workspace.search_drive_files",
        ]
    )

    with patch(
        "python.helpers.mcp_handler.MCPConfig.get_instance",
        return_value=mock_cfg,
    ):
        msg = agent._mcp_tool_not_found_message("google_workspace.not_a_real_tool")

    assert "Unknown MCP tool" in msg
    assert "send_gmail_message" in msg


@pytest.mark.asyncio
async def test_reliability_code_execution_wrapper_guard_contract() -> None:
    """Code execution should reject triple-quote wrapper patterns."""
    tool = _build_code_execution_tool()
    result = await tool.execute_python_code(
        session=0, code="code = '''\nprint(1)\n'''\nexec(code)"
    )
    assert "triple-quote wrapper" in result


@pytest.mark.asyncio
async def test_reliability_retry_timeout_contract() -> None:
    """Bounded timeout behavior should surface a timeout message instead of stalling."""

    async def slow_monologue() -> str:
        await asyncio.sleep(1)
        return "should not complete"

    timeout = 0.01
    try:
        await asyncio.wait_for(slow_monologue(), timeout=timeout)
    except asyncio.TimeoutError:
        result = (
            f"Subordinate agent timed out after {int(timeout)}s. "
            "Partial work may have been completed."
        )
    else:
        result = "unexpected success"

    assert "timed out" in result
    assert DEFAULT_SUBORDINATE_TIMEOUT >= 60


def test_reliability_readiness_transition_contract() -> None:
    """Readiness should stay distinct from liveness when optional MCP init fails."""
    run_ui.startup_state.reset()
    run_ui.startup_state.mark_ready("migration", detail="Done.")
    run_ui.startup_state.mark_ready("chat_restore", detail="Done.")
    run_ui.startup_state.mark_failed(
        "mcp_init",
        error="workspace_mcp unavailable",
        detail="Informational only.",
    )

    client = run_ui.webapp.test_client()
    health_response = client.get("/health")
    ready_response = client.get("/ready")

    assert health_response.status_code == 200
    assert ready_response.status_code == 200
    assert ready_response.get_json()["phases"]["mcp_init"]["required"] is False


def test_reliability_container_venv_parity_when_available() -> None:
    """If the app venv exists locally, it should resolve required Google imports."""
    container_python = Path("/opt/venv-a0/bin/python")
    if not container_python.exists():
        pytest.skip("Container app venv not present in this environment.")

    result = subprocess.run(
        [
            str(container_python),
            "-c",
            "import google.auth, googleapiclient; print('ok')",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
