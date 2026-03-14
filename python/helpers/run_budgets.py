"""
Run budgets — configurable limits for autonomous runs (SAFETY-01).

Time, tool calls, tokens, or cost. Loaded from env and optional governance file;
agent cannot disable. Enforced in the executor (task_scheduler._run_task).
"""

from __future__ import annotations

import os
from typing import Optional

from pydantic import BaseModel, Field

from python.helpers.files import get_abs_path, read_file
from python.helpers.print_style import PrintStyle

GOVERNANCE_FOLDER = "usr/governance"
BUDGETS_FILE = "run_budgets.json"


class RunBudgets(BaseModel):
    """Configurable budgets for a single autonomous run. Zero or None means no limit."""

    max_seconds: Optional[float] = Field(
        default=None, description="Max wall-clock seconds per run"
    )
    max_tool_calls: Optional[int] = Field(
        default=None, description="Max tool invocations per run"
    )
    max_tokens: Optional[int] = Field(
        default=None, description="Max tokens per run (if available)"
    )
    max_cost_dollars: Optional[float] = Field(
        default=None, description="Max cost in dollars per run (if available)"
    )

    @classmethod
    def from_env(cls) -> "RunBudgets":
        """Load from environment variables (governance; agent cannot set)."""

        def _float(s: Optional[str]) -> Optional[float]:
            if not s:
                return None
            try:
                return float(s)
            except ValueError:
                return None

        def _int(s: Optional[str]) -> Optional[int]:
            if not s:
                return None
            try:
                return int(s)
            except ValueError:
                return None

        return cls(
            max_seconds=_float(os.environ.get("AGENTZ_RUN_BUDGET_SECONDS")),
            max_tool_calls=_int(os.environ.get("AGENTZ_RUN_BUDGET_TOOL_CALLS")),
            max_tokens=_int(os.environ.get("AGENTZ_RUN_BUDGET_TOKENS")),
            max_cost_dollars=_float(os.environ.get("AGENTZ_RUN_BUDGET_COST_DOLLARS")),
        )

    @classmethod
    def from_file(cls, path: Optional[str] = None) -> Optional["RunBudgets"]:
        """Load from governance file if present. Path defaults to usr/governance/run_budgets.json."""
        if path is None:
            path = get_abs_path(GOVERNANCE_FOLDER, BUDGETS_FILE)
        try:
            data = read_file(path)
            if not data or not data.strip():
                return None
            return cls.model_validate_json(data)
        except FileNotFoundError:
            return None
        except Exception as e:
            PrintStyle.warning(f"Could not load run budgets from {path}: {e}")
            return None

    @classmethod
    def get(cls, path: Optional[str] = None) -> "RunBudgets":
        """
        Get effective run budgets: file overrides env, env overrides defaults.
        Used by executor only; agent cannot disable.
        """
        from_env = cls.from_env()
        from_file = cls.from_file(path)
        if from_file is None:
            return from_env
        # Merge: file wins where set
        return cls(
            max_seconds=from_file.max_seconds
            if from_file.max_seconds is not None
            else from_env.max_seconds,
            max_tool_calls=from_file.max_tool_calls
            if from_file.max_tool_calls is not None
            else from_env.max_tool_calls,
            max_tokens=from_file.max_tokens
            if from_file.max_tokens is not None
            else from_env.max_tokens,
            max_cost_dollars=from_file.max_cost_dollars
            if from_file.max_cost_dollars is not None
            else from_env.max_cost_dollars,
        )

    def effective_timeout_seconds(self) -> Optional[float]:
        """Return timeout for asyncio.wait_for; None means no time limit."""
        return self.max_seconds
