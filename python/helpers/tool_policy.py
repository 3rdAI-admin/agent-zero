"""Tool execution policy — enable/disable tools and restrict paths (AUTON-04, AUTON-06).

Policy is loaded from usr/governance/tool_policy.json or env. The agent
cannot modify files in the governance directory (enforced by files.py).

Config example (usr/governance/tool_policy.json):
{
    "disabled_tools": ["browser_agent"],
    "restricted_paths": ["/etc/shadow", "/root/.ssh"],
    "browser": {
        "allowed_domains": ["*.example.com", "localhost"]
    }
}

Environment overrides:
    AGENTZ_DISABLED_TOOLS  — comma-separated tool names to disable
    AGENTZ_RESTRICTED_PATHS — comma-separated path prefixes to block
"""

from __future__ import annotations

import json
import os
from fnmatch import fnmatch
from typing import Any

from python.helpers.files import get_abs_path, read_file

GOVERNANCE_FOLDER = "usr/governance"
TOOL_POLICY_FILE = "tool_policy.json"
_ENV_DISABLED_TOOLS = "AGENTZ_DISABLED_TOOLS"
_ENV_RESTRICTED_PATHS = "AGENTZ_RESTRICTED_PATHS"


def _config_path() -> str:
    """Return absolute path for the tool policy file."""
    return get_abs_path(GOVERNANCE_FOLDER, TOOL_POLICY_FILE)


def _load_config() -> dict[str, Any]:
    """Load tool policy config from governance file.

    Returns:
        dict: Parsed config or empty dict if file missing/invalid.
    """
    path = _config_path()
    try:
        data = read_file(path)
        if not data or not data.strip():
            return {}
        return json.loads(data)
    except (FileNotFoundError, ValueError, TypeError):
        return {}


def get_disabled_tools() -> set[str]:
    """Get set of tool names that are disabled by policy.

    Returns:
        set: Tool names that should be blocked from execution.
    """
    config = _load_config()
    disabled: set[str] = set()

    # From config file
    file_disabled = config.get("disabled_tools", [])
    if isinstance(file_disabled, list):
        disabled.update(str(t).strip() for t in file_disabled if t)

    # From env (comma-separated)
    env_val = (os.environ.get(_ENV_DISABLED_TOOLS) or "").strip()
    if env_val:
        disabled.update(t.strip() for t in env_val.split(",") if t.strip())

    return disabled


def is_tool_allowed(tool_name: str) -> tuple[bool, str]:
    """Check if a tool is allowed by the current policy.

    Args:
        tool_name: Name of the tool to check.

    Returns:
        (allowed, reason). If allowed is False, reason describes why.
    """
    disabled = get_disabled_tools()
    if tool_name in disabled:
        return False, f"Tool '{tool_name}' is disabled by governance policy."
    return True, ""


def get_restricted_paths() -> list[str]:
    """Get list of path prefixes that tools cannot access.

    Returns:
        list: Path prefixes (absolute or relative) that should be blocked.
    """
    config = _load_config()
    paths: list[str] = []

    file_paths = config.get("restricted_paths", [])
    if isinstance(file_paths, list):
        paths.extend(str(p).strip() for p in file_paths if p)

    env_val = (os.environ.get(_ENV_RESTRICTED_PATHS) or "").strip()
    if env_val:
        paths.extend(p.strip() for p in env_val.split(",") if p.strip())

    return paths


def is_path_restricted(path: str) -> tuple[bool, str]:
    """Check if a path is restricted by policy.

    Args:
        path: Path to check (absolute or relative).

    Returns:
        (restricted, reason). If restricted is True, reason describes why.
    """
    restricted = get_restricted_paths()
    abs_path = os.path.abspath(path)
    for prefix in restricted:
        abs_prefix = os.path.abspath(prefix)
        if abs_path.startswith(abs_prefix):
            return (
                True,
                f"Path '{path}' is restricted by governance policy (matches: {prefix!r}).",
            )
    return False, ""


def get_browser_allowed_domains() -> list[str]:
    """Get list of allowed browser domains from policy.

    Returns:
        list: Domain patterns (supports fnmatch globs). Empty = unrestricted.
    """
    config = _load_config()
    browser = config.get("browser", {})
    if not isinstance(browser, dict):
        return []
    domains = browser.get("allowed_domains", [])
    if not isinstance(domains, list):
        return []
    return [str(d).strip() for d in domains if d]


def is_domain_allowed(url: str) -> tuple[bool, str]:
    """Check if a URL's domain is allowed by browser policy.

    Args:
        url: Full URL to check.

    Returns:
        (allowed, reason). If no domains configured, all are allowed.
    """
    domains = get_browser_allowed_domains()
    if not domains:
        return True, ""  # No restriction configured

    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        hostname = parsed.hostname or ""
    except Exception:
        return False, f"Cannot parse URL: {url!r}"

    for pattern in domains:
        if fnmatch(hostname, pattern):
            return True, ""

    return False, (
        f"Domain '{hostname}' is not in the browser allowlist. "
        f"Allowed: {', '.join(domains[:10])}" + ("..." if len(domains) > 10 else "")
    )
