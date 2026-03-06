"""
Bounded host control — allowlist or deny list for terminal commands (AUTON-04, AUTON-06).

Policy is loaded from usr/governance/host_control.json or env; the agent cannot
disable or bypass this configuration. Only terminal (shell) commands are checked;
python/nodejs code execution is not restricted by this module.
"""

from __future__ import annotations

import os
from typing import Literal

from python.helpers.files import get_abs_path, read_file

GOVERNANCE_FOLDER = "usr/governance"
HOST_CONTROL_FILE = "host_control.json"
_ENV_POLICY = "AGENTZ_HOST_CONTROL_POLICY"  # allowlist | deny | permissive
_ENV_ALLOWLIST = "AGENTZ_HOST_CONTROL_ALLOWLIST"  # comma-separated prefixes
_ENV_DENYLIST = "AGENTZ_HOST_CONTROL_DENYLIST"  # comma-separated prefixes


def _config_path() -> str:
    return get_abs_path(GOVERNANCE_FOLDER, HOST_CONTROL_FILE)


def _load_policy_from_file() -> tuple[str | None, list[str], list[str]]:
    """Returns (policy, allowlist, denylist). policy is None if not set."""
    path = _config_path()
    try:
        data = read_file(path)
        if not data or not data.strip():
            return None, [], []
        import json

        obj = json.loads(data)
        policy = obj.get("policy")  # "allowlist" | "deny" | "permissive"
        allowlist = obj.get("allowlist") or []
        denylist = obj.get("denylist") or []
        if not isinstance(allowlist, list):
            allowlist = []
        if not isinstance(denylist, list):
            denylist = []
        allowlist = [str(x).strip() for x in allowlist if x]
        denylist = [str(x).strip() for x in denylist if x]
        return policy, allowlist, denylist
    except (FileNotFoundError, ValueError, TypeError):
        return None, [], []


def get_host_control_config() -> tuple[
    Literal["allowlist", "deny", "permissive"],
    list[str],
    list[str],
]:
    """
    Load host control policy. Env overrides file for policy type;
    allowlist/denylist are merged (file first, then env).

    Returns:
        (policy, allowlist, denylist). policy is one of allowlist, deny, permissive.
        permissive = no check (allow all). allowlist = allow only if command
        starts with an allowlist entry. deny = allow unless command starts with
        a denylist entry.
    """
    policy_env = (os.environ.get(_ENV_POLICY) or "").strip().lower()
    allow_env = (os.environ.get(_ENV_ALLOWLIST) or "").strip()
    deny_env = (os.environ.get(_ENV_DENYLIST) or "").strip()

    policy_file, allow_file, deny_file = _load_policy_from_file()

    policy: Literal["allowlist", "deny", "permissive"] = "permissive"
    if policy_env in ("allowlist", "deny", "permissive"):
        policy = policy_env  # type: ignore
    elif policy_file in ("allowlist", "deny", "permissive"):
        policy = policy_file  # type: ignore

    allowlist = list(allow_file) + [
        x.strip() for x in allow_env.split(",") if x.strip()
    ]
    denylist = list(deny_file) + [x.strip() for x in deny_env.split(",") if x.strip()]

    return policy, allowlist, denylist


def is_terminal_command_allowed(command: str) -> tuple[bool, str]:
    """
    Check if a terminal command is allowed under the current host control policy.

    Args:
        command: The raw command string (e.g. "apt-get install zip").

    Returns:
        (allowed, reason). If allowed is False, reason describes why (for agent message).
    """
    cmd_stripped = command.strip()
    if not cmd_stripped:
        return False, "Empty command not allowed."

    policy, allowlist, denylist = get_host_control_config()

    if policy == "permissive":
        return True, ""

    if policy == "allowlist":
        if not allowlist:
            # Empty allowlist and policy allowlist → allow nothing
            return (
                False,
                "Host control policy is allowlist but no entries configured; terminal commands are disabled.",
            )
        for prefix in allowlist:
            if cmd_stripped.startswith(prefix) or cmd_stripped == prefix:
                return True, ""
        return False, (
            f"Command not in allowlist. Allowed prefixes: {', '.join(allowlist[:10])}"
            + ("..." if len(allowlist) > 10 else "")
        )

    if policy == "deny":
        for prefix in denylist:
            if cmd_stripped.startswith(prefix) or cmd_stripped == prefix:
                return (
                    False,
                    f"Command is denied by host control (matches: {prefix!r}).",
                )
        return True, ""

    return True, ""
