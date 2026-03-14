from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from python.helpers import settings
from python.helpers.runtime_state_report import build_runtime_state_report


def _write_json(path: Path, payload: dict) -> None:
    """Write a JSON payload to disk.

    Args:
        path: Output file path.
        payload: JSON payload to write.
    """
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_runtime_state_report_uses_repo_seed_when_present(tmp_path: Path) -> None:
    """Report uses repo seed values when a seed file exists."""
    default_settings = settings.get_default_settings()
    effective_settings = default_settings.copy()
    repo_seed = default_settings.copy()

    effective_settings["chat_model_name"] = "live-chat"
    repo_seed["chat_model_name"] = "seed-chat"

    effective_path = tmp_path / "live-settings.json"
    repo_seed_path = tmp_path / "repo-seed.json"
    root_env_path = tmp_path / "root.env"
    user_env_path = tmp_path / "usr.env"
    legacy_path = tmp_path / "tmp-settings.json"

    _write_json(repo_seed_path, repo_seed)
    root_env_path.write_text("FOO=1\n", encoding="utf-8")
    user_env_path.write_text("FOO=1\n", encoding="utf-8")

    report = build_runtime_state_report(
        effective_settings=effective_settings,
        default_settings=default_settings,
        effective_settings_path=str(effective_path),
        repo_seed_settings_path=str(repo_seed_path),
        root_env_path=str(root_env_path),
        user_env_path=str(user_env_path),
        legacy_settings_path=str(legacy_path),
    )

    assert report["seed"]["source"] == "repo_seed_settings"
    assert report["models"]["seed"]["chat"].endswith("seed-chat")
    assert report["models"]["drift_fields"] == ["chat_model_name"]
    assert report["drift"]["settings_path_drift"] is True


def test_runtime_state_report_detects_env_mcp_and_legacy_drift(tmp_path: Path) -> None:
    """Report includes focused warnings for env, MCP, and legacy drift."""
    default_settings = settings.get_default_settings()
    effective_settings = default_settings.copy()
    repo_seed = default_settings.copy()

    effective_settings["chat_model_name"] = "live-chat"
    effective_settings["util_model_name"] = "live-util"
    effective_settings["browser_model_name"] = "live-browser"
    effective_settings["mcp_servers"] = json.dumps(
        {
            "mcpServers": {
                "archon": {
                    "url": "http://archon-mcp:8051/mcp",
                    "transport": "streamable-http",
                }
            }
        }
    )
    repo_seed["mcp_servers"] = json.dumps(
        {"mcpServers": {"google_workspace": {"url": "http://workspace_mcp:8889/mcp"}}}
    )

    effective_path = tmp_path / "live-settings.json"
    repo_seed_path = tmp_path / "repo-seed.json"
    root_env_path = tmp_path / "root.env"
    user_env_path = tmp_path / "usr.env"
    legacy_path = tmp_path / "tmp-settings.json"

    _write_json(repo_seed_path, repo_seed)
    root_env_path.write_text("AUTH_LOGIN=root-user\nSHARED=same\n", encoding="utf-8")
    user_env_path.write_text("AUTH_LOGIN=usr-user\nSHARED=same\n", encoding="utf-8")
    legacy_path.write_text("{}", encoding="utf-8")

    report = build_runtime_state_report(
        effective_settings=effective_settings,
        default_settings=default_settings,
        effective_settings_path=str(effective_path),
        repo_seed_settings_path=str(repo_seed_path),
        root_env_path=str(root_env_path),
        user_env_path=str(user_env_path),
        legacy_settings_path=str(legacy_path),
    )

    assert report["env"]["user_overrides_root"] is True
    assert report["env"]["override_keys"] == ["AUTH_LOGIN"]
    assert report["mcp"]["live_server_names"] == ["archon"]
    assert report["mcp"]["seed_server_names"] == ["google_workspace"]
    assert "mcp_servers" in report["mcp"]["drift_fields"]
    assert report["drift"]["legacy_tmp_settings_present"] is True
    assert any(
        "usr/.env overrides root .env" in warning
        for warning in report["drift"]["warnings"]
    )
    assert any(
        "Live MCP config differs" in warning for warning in report["drift"]["warnings"]
    )
    assert any(
        "Legacy tmp/settings.json" in warning for warning in report["drift"]["warnings"]
    )


def test_runtime_state_report_falls_back_to_default_seed_when_repo_seed_missing(
    tmp_path: Path,
) -> None:
    """Report falls back to defaults when no repo seed file exists."""
    default_settings = settings.get_default_settings()
    effective_settings = default_settings.copy()
    effective_settings["chat_model_name"] = "live-chat"

    effective_path = tmp_path / "live-settings.json"
    missing_repo_seed_path = tmp_path / "missing-seed.json"
    root_env_path = tmp_path / "root.env"
    user_env_path = tmp_path / "usr.env"
    legacy_path = tmp_path / "tmp-settings.json"

    root_env_path.write_text("", encoding="utf-8")
    user_env_path.write_text("", encoding="utf-8")

    report = build_runtime_state_report(
        effective_settings=effective_settings,
        default_settings=default_settings,
        effective_settings_path=str(effective_path),
        repo_seed_settings_path=str(missing_repo_seed_path),
        root_env_path=str(root_env_path),
        user_env_path=str(user_env_path),
        legacy_settings_path=str(legacy_path),
    )

    assert report["seed"]["source"] == "default_settings"
    assert report["seed"]["repo_seed_present"] is False
    assert report["drift"]["settings_path_drift"] is False
    assert "chat_model_name" in report["models"]["drift_fields"]
