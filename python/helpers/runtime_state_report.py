import json
import os
from typing import Any

from python.helpers import dotenv, files, settings

MODEL_FIELDS = [
    "chat_model_provider",
    "chat_model_name",
    "chat_model_api_base",
    "util_model_provider",
    "util_model_name",
    "util_model_api_base",
    "browser_model_provider",
    "browser_model_name",
    "browser_model_api_base",
]

MCP_FIELDS = [
    "mcp_servers",
    "mcp_client_init_timeout",
    "mcp_client_tool_timeout",
    "mcp_server_enabled",
]

RUNTIME_DERIVED_FIELDS = [
    "mcp_server_token",
    "auth_login",
    "auth_password",
    "rfc_password",
    "root_password",
    "secrets",
]


def _read_json_file(path: str) -> dict[str, Any] | None:
    """Read a JSON file if it exists.

    Args:
        path: Absolute path to the JSON file.

    Returns:
        Parsed JSON object when present and valid, else `None`.
    """
    if not path or not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as handle:
        parsed = json.load(handle)

    return parsed if isinstance(parsed, dict) else None


def _read_env_file(path: str) -> dict[str, str]:
    """Read a dotenv-style file into a simple key/value mapping.

    Args:
        path: Absolute path to the dotenv file.

    Returns:
        Parsed environment values. Comments and blank lines are ignored.
    """
    if not path or not os.path.exists(path):
        return {}

    parsed: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            parsed[key.strip()] = value.strip()
    return parsed


def _normalize_mcp_servers(value: Any) -> dict[str, Any]:
    """Normalize MCP server config to a dictionary.

    Args:
        value: Raw MCP server config from settings, stringified JSON, or dict.

    Returns:
        Parsed MCP configuration dictionary.
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _stable_json(value: Any) -> str:
    """Serialize a value in stable form for drift comparison.

    Args:
        value: Value to serialize.

    Returns:
        Stable JSON string representation.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _model_summary(data: dict[str, Any]) -> dict[str, str]:
    """Build a compact per-role model summary.

    Args:
        data: Settings-like dictionary.

    Returns:
        Role-to-summary mapping for chat, utility, and browser models.
    """
    summary: dict[str, str] = {}
    role_prefixes = {"chat": "chat", "utility": "util", "browser": "browser"}
    for label, prefix in role_prefixes.items():
        provider = data.get(f"{prefix}_model_provider", "")
        name = data.get(f"{prefix}_model_name", "")
        api_base = data.get(f"{prefix}_model_api_base", "")
        rendered = f"{provider}/{name}".strip("/")
        if api_base:
            rendered = f"{rendered} @ {api_base}"
        summary[label] = rendered or "(unset)"
    return summary


def _mcp_server_names(data: dict[str, Any]) -> list[str]:
    """Extract MCP server names from a settings-like dictionary.

    Args:
        data: Settings-like dictionary.

    Returns:
        Sorted MCP server names.
    """
    mcp_config = _normalize_mcp_servers(data.get("mcp_servers"))
    servers = mcp_config.get("mcpServers", {})
    if not isinstance(servers, dict):
        return []
    return sorted(str(name) for name in servers.keys())


def _combine_seed_reference(
    default_settings: dict[str, Any], repo_seed: dict[str, Any] | None
) -> dict[str, Any]:
    """Combine default settings with repo seed overrides.

    Args:
        default_settings: Normalized default settings.
        repo_seed: Repo seed settings file contents, if present.

    Returns:
        Settings reference used for drift comparisons.
    """
    combined = default_settings.copy()
    if repo_seed:
        combined.update(repo_seed)
    return combined


def build_runtime_state_report(
    *,
    effective_settings: dict[str, Any] | None = None,
    default_settings: dict[str, Any] | None = None,
    effective_settings_path: str | None = None,
    repo_seed_settings_path: str | None = None,
    root_env_path: str | None = None,
    user_env_path: str | None = None,
    legacy_settings_path: str | None = None,
) -> dict[str, Any]:
    """Build an operator-facing runtime state and drift report.

    Args:
        effective_settings: Effective live settings override for tests.
        default_settings: Default settings override for tests.
        effective_settings_path: Live settings path override for tests.
        repo_seed_settings_path: Repo seed settings path override for tests.
        root_env_path: Root `.env` path override for tests.
        user_env_path: `usr/.env` path override for tests.
        legacy_settings_path: Legacy tmp settings path override for tests.

    Returns:
        JSON-serializable runtime state report.
    """
    live_settings = (effective_settings or settings.get_settings()).copy()
    defaults = (default_settings or settings.get_default_settings()).copy()
    live_path = effective_settings_path or settings.SETTINGS_FILE
    repo_seed_path = repo_seed_settings_path or "/git/agent-zero/usr/settings.json"
    root_path = root_env_path or files.get_abs_path(".env")
    user_path = user_env_path or dotenv.get_dotenv_file_path()
    legacy_path = legacy_settings_path or files.get_abs_path("tmp/settings.json")

    repo_seed_raw = _read_json_file(repo_seed_path)
    seed_reference = _combine_seed_reference(defaults, repo_seed_raw)
    root_env = _read_env_file(root_path)
    user_env = _read_env_file(user_path)
    override_keys = sorted(
        key
        for key, value in user_env.items()
        if key in root_env and root_env.get(key) != value
    )

    model_drift_fields = sorted(
        field
        for field in MODEL_FIELDS
        if live_settings.get(field) != seed_reference.get(field)
    )
    mcp_drift_fields = sorted(
        field
        for field in MCP_FIELDS
        if (
            _stable_json(_normalize_mcp_servers(live_settings.get(field)))
            != _stable_json(_normalize_mcp_servers(seed_reference.get(field)))
            if field == "mcp_servers"
            else live_settings.get(field) != seed_reference.get(field)
        )
    )

    live_realpath = os.path.realpath(live_path) if live_path else ""
    seed_realpath = os.path.realpath(repo_seed_path) if repo_seed_raw else live_realpath
    settings_path_drift = bool(repo_seed_raw) and live_realpath != seed_realpath
    legacy_settings_present = os.path.exists(legacy_path)

    warnings: list[str] = []
    if settings_path_drift:
        warnings.append(
            "Live settings path differs from repo seed; repo usr/settings.json is seed-only."
        )
    if override_keys:
        warnings.append(
            f"usr/.env overrides root .env for {len(override_keys)} key(s)."
        )
    if model_drift_fields:
        warnings.append("Live model assignment differs from repo seed/defaults.")
    if mcp_drift_fields:
        warnings.append("Live MCP config differs from repo seed/defaults.")
    if legacy_settings_present:
        warnings.append(
            "Legacy tmp/settings.json is still present; treat it as migration input only."
        )

    return {
        "paths": {
            "effective_settings_path": live_path,
            "repo_seed_settings_path": repo_seed_path,
            "root_env_path": root_path,
            "user_env_path": user_path,
            "legacy_settings_path": legacy_path,
        },
        "seed": {
            "source": "repo_seed_settings" if repo_seed_raw else "default_settings",
            "repo_seed_present": bool(repo_seed_raw),
        },
        "env": {
            "root_env_present": os.path.exists(root_path),
            "user_env_present": os.path.exists(user_path),
            "user_overrides_root": bool(override_keys),
            "override_keys": override_keys,
            "override_count": len(override_keys),
        },
        "runtime": {
            "auth_configured": bool(live_settings.get("auth_login")),
            "runtime_derived_fields": RUNTIME_DERIVED_FIELDS,
            "mcp_server_token_runtime_derived": True,
            "preload_runtime_source": "effective_settings",
            "preload_build_source": "defaults_only",
            "liveness_endpoint": "/health",
            "readiness_endpoint": "/ready",
        },
        "models": {
            "live": _model_summary(live_settings),
            "seed": _model_summary(seed_reference),
            "drift_fields": model_drift_fields,
        },
        "mcp": {
            "live_server_names": _mcp_server_names(live_settings),
            "seed_server_names": _mcp_server_names(seed_reference),
            "drift_fields": mcp_drift_fields,
        },
        "drift": {
            "settings_path_drift": settings_path_drift,
            "legacy_tmp_settings_present": legacy_settings_present,
            "warnings": warnings,
        },
    }
