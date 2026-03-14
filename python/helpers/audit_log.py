"""Append-only audit log for tool executions and high-stakes actions (SAFETY-03).

The agent has no tool or code path to write to this log. Only this module
appends to the log file. The governance directory is protected from agent
writes by tool-level path checks (Phase 2f).

File is opened with os.O_APPEND for POSIX append-only guarantees.
Path is from AGENTZ_AUDIT_LOG_PATH or usr/governance/audit.jsonl.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from typing import Any

from python.helpers.files import get_abs_path

GOVERNANCE_FOLDER = "usr/governance"
AUDIT_LOG_FILENAME = "audit.jsonl"
_ENV_KEY = "AGENTZ_AUDIT_LOG_PATH"
_lock = threading.Lock()
_MAX_ARG_LEN = 1000
_MAX_RESULT_LEN = 500


def _log_path() -> str:
    """Return absolute path for the audit log file."""
    env_path = os.environ.get(_ENV_KEY, "").strip()
    if env_path:
        return os.path.abspath(env_path)
    return get_abs_path(GOVERNANCE_FOLDER, AUDIT_LOG_FILENAME)


def _ensure_dir(path: str) -> None:
    """Ensure parent directory exists."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def _now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _truncate(text: str, max_len: int) -> str:
    """Truncate text, appending ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _sanitize(obj: Any, max_len: int = 500) -> Any:
    """Sanitize for audit: truncate strings, recurse into dicts/lists."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return _truncate(obj, max_len)
    if isinstance(obj, dict):
        return {k: _sanitize(v, max_len) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(x, max_len) for x in obj]
    return obj


def _mask_args(args: dict[str, Any]) -> dict[str, str]:
    """Mask secret values in tool arguments using the secrets filter.

    Args:
        args: Raw tool arguments dict.

    Returns:
        dict: Arguments with secret values replaced by placeholders.
    """
    masked: dict[str, str] = {}
    try:
        from python.helpers.secrets import get_secrets_manager

        sm = get_secrets_manager()
        for key, value in args.items():
            text = str(value) if not isinstance(value, str) else value
            text = _truncate(text, _MAX_ARG_LEN)
            masked[key] = sm.mask_values(text)
    except Exception:
        # Fallback: truncate but don't mask (secrets module unavailable)
        for key, value in args.items():
            text = str(value) if not isinstance(value, str) else value
            masked[key] = _truncate(text, _MAX_ARG_LEN)
    return masked


def _append_record(record: dict[str, Any]) -> None:
    """Append a JSON record to the audit log using O_APPEND.

    Args:
        record: Dictionary to serialize as a JSON line.
    """
    line = json.dumps(record, default=str, ensure_ascii=False) + "\n"
    path = _log_path()
    with _lock:
        try:
            _ensure_dir(path)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            try:
                os.write(fd, line.encode("utf-8"))
            finally:
                os.close(fd)
        except OSError:
            pass  # Do not fail the app if audit log is unwritable


def write(
    event: str,
    *,
    tool_name: str | None = None,
    method: str | None = None,
    tool_args: dict[str, Any] | None = None,
    agent_name: str | None = None,
    context_id: str | None = None,
    task_id: str | None = None,
    details: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    """Append a single JSON line to the audit log. Thread-safe.

    Args:
        event: Event type (e.g. "tool_call", "tool_result", "autonomy_trigger").
        tool_name: Name of tool.
        method: Tool sub-method (e.g. "python", "terminal").
        tool_args: Raw tool arguments (will be masked and sanitized).
        agent_name: Name of the calling agent.
        context_id: Chat/context identifier.
        task_id: Task UUID (for autonomy events).
        details: Optional extra key-value data (sanitized).
        error: Optional error message.
    """
    payload: dict[str, Any] = {
        "ts": _now_iso(),
        "event": event,
    }
    if tool_name is not None:
        payload["tool"] = tool_name
    if method is not None:
        payload["method"] = method
    if tool_args is not None:
        payload["args"] = _mask_args(tool_args)
    if agent_name is not None:
        payload["agent"] = agent_name
    if context_id is not None:
        payload["context"] = context_id[:200]
    if task_id is not None:
        payload["task_id"] = task_id
    if details is not None:
        payload["details"] = _sanitize(details)
    if error is not None:
        payload["error"] = _truncate(error, 500)

    _append_record(payload)


def log_tool_call(
    tool_name: str,
    method: str | None,
    tool_args: dict[str, Any],
    agent_name: str = "",
    context_id: str = "",
) -> None:
    """Log a tool invocation (before execution).

    Args:
        tool_name: Name of the tool being called.
        method: Sub-method (e.g. "python", "terminal"), or None.
        tool_args: Raw arguments (will be masked and truncated).
        agent_name: Name of the calling agent.
        context_id: Agent context identifier.
    """
    write(
        "tool_call",
        tool_name=tool_name,
        method=method,
        tool_args=tool_args,
        agent_name=agent_name,
        context_id=context_id,
    )


def log_tool_result(
    tool_name: str,
    method: str | None,
    result_summary: str,
    success: bool,
    agent_name: str = "",
    context_id: str = "",
    duration_ms: float | None = None,
) -> None:
    """Log a tool execution result (after execution).

    Args:
        tool_name: Name of the tool that executed.
        method: Sub-method, or None.
        result_summary: Truncated output text.
        success: Whether execution succeeded without error.
        agent_name: Name of the calling agent.
        context_id: Agent context identifier.
        duration_ms: Execution wall-clock time in milliseconds.
    """
    details: dict[str, Any] = {
        "success": success,
        "result": _truncate(result_summary, _MAX_RESULT_LEN),
    }
    if duration_ms is not None:
        details["duration_ms"] = round(duration_ms, 1)
    write(
        "tool_result",
        tool_name=tool_name,
        method=method,
        agent_name=agent_name,
        context_id=context_id,
        details=details,
    )


# --- Convenience wrappers (backward-compatible with Phase 1 callers) ---


def log_tool_execution(
    tool_name: str,
    tool_args: dict[str, Any],
    context_id: str | None = None,
) -> None:
    """Convenience: log a tool execution event (Phase 1 compat)."""
    write(
        "tool_execution",
        tool_name=tool_name,
        tool_args=tool_args,
        context_id=context_id,
    )


def log_autonomy_trigger(
    task_id: str | None = None,
    goal: str | None = None,
    context_id: str | None = None,
    error: str | None = None,
) -> None:
    """Convenience: log autonomy trigger (run task or enqueue goal)."""
    details = {}
    if goal is not None:
        details["goal"] = _truncate(goal, 300)
    write(
        "autonomy_trigger",
        task_id=task_id,
        context_id=context_id,
        details=details if details else None,
        error=error,
    )


def log_autonomy_kill(
    task_id: str | None = None,
    context_id: str | None = None,
) -> None:
    """Convenience: log kill switch invocation."""
    write(
        "autonomy_kill",
        task_id=task_id,
        context_id=context_id,
    )
