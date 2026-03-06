"""Tests for python/helpers/run_budgets.py — configurable run budgets (SAFETY-01)."""

import json
import os
from unittest.mock import patch


from python.helpers.run_budgets import RunBudgets


class TestRunBudgetsFromEnv:
    """Loading budgets from environment variables."""

    def test_loads_all_env_vars(self):
        """Expected use: all four budget env vars are read correctly."""
        env = {
            "AGENTZ_RUN_BUDGET_SECONDS": "300",
            "AGENTZ_RUN_BUDGET_TOOL_CALLS": "50",
            "AGENTZ_RUN_BUDGET_TOKENS": "10000",
            "AGENTZ_RUN_BUDGET_COST_DOLLARS": "1.5",
        }
        with patch.dict(os.environ, env, clear=False):
            b = RunBudgets.from_env()
        assert b.max_seconds == 300.0
        assert b.max_tool_calls == 50
        assert b.max_tokens == 10000
        assert b.max_cost_dollars == 1.5

    def test_defaults_to_none_when_unset(self):
        """Expected use: missing env vars yield None (no limit)."""
        env_keys = [
            "AGENTZ_RUN_BUDGET_SECONDS",
            "AGENTZ_RUN_BUDGET_TOOL_CALLS",
            "AGENTZ_RUN_BUDGET_TOKENS",
            "AGENTZ_RUN_BUDGET_COST_DOLLARS",
        ]
        cleaned = {k: "" for k in env_keys}
        with patch.dict(os.environ, cleaned, clear=False):
            b = RunBudgets.from_env()
        assert b.max_seconds is None
        assert b.max_tool_calls is None
        assert b.max_tokens is None
        assert b.max_cost_dollars is None

    def test_invalid_env_values_become_none(self):
        """Failure case: non-numeric env values are silently ignored."""
        env = {
            "AGENTZ_RUN_BUDGET_SECONDS": "not-a-number",
            "AGENTZ_RUN_BUDGET_TOOL_CALLS": "abc",
        }
        with patch.dict(os.environ, env, clear=False):
            b = RunBudgets.from_env()
        assert b.max_seconds is None
        assert b.max_tool_calls is None


class TestRunBudgetsFromFile:
    """Loading budgets from governance JSON file."""

    def test_loads_valid_json(self, tmp_path):
        """Expected use: valid JSON file is parsed into RunBudgets."""
        f = tmp_path / "budgets.json"
        f.write_text(json.dumps({"max_seconds": 120, "max_tool_calls": 25}))
        b = RunBudgets.from_file(str(f))
        assert b.max_seconds == 120.0
        assert b.max_tool_calls == 25
        assert b.max_tokens is None

    def test_missing_file_returns_none(self, tmp_path):
        """Edge case: non-existent file returns None (no override)."""
        result = RunBudgets.from_file(str(tmp_path / "nope.json"))
        assert result is None

    def test_empty_file_returns_none(self, tmp_path):
        """Edge case: empty file returns None."""
        f = tmp_path / "empty.json"
        f.write_text("")
        result = RunBudgets.from_file(str(f))
        assert result is None

    def test_invalid_json_returns_none(self, tmp_path):
        """Failure case: malformed JSON returns None with warning."""
        f = tmp_path / "bad.json"
        f.write_text("{not valid json")
        result = RunBudgets.from_file(str(f))
        assert result is None


class TestRunBudgetsGet:
    """Merged budget resolution: file overrides env."""

    def test_file_overrides_env(self, tmp_path):
        """Expected use: file values take precedence over env."""
        f = tmp_path / "budgets.json"
        f.write_text(json.dumps({"max_seconds": 60}))
        env = {"AGENTZ_RUN_BUDGET_SECONDS": "300", "AGENTZ_RUN_BUDGET_TOOL_CALLS": "10"}
        with patch.dict(os.environ, env, clear=False):
            b = RunBudgets.get(path=str(f))
        assert b.max_seconds == 60.0  # file wins
        assert b.max_tool_calls == 10  # env fallback

    def test_env_only_when_no_file(self, tmp_path):
        """Edge case: no file means env-only budgets."""
        env = {"AGENTZ_RUN_BUDGET_SECONDS": "200"}
        with patch.dict(os.environ, env, clear=False):
            b = RunBudgets.get(path=str(tmp_path / "missing.json"))
        assert b.max_seconds == 200.0


class TestEffectiveTimeout:
    """effective_timeout_seconds helper."""

    def test_returns_value_when_set(self):
        b = RunBudgets(max_seconds=42.0)
        assert b.effective_timeout_seconds() == 42.0

    def test_returns_none_when_unset(self):
        b = RunBudgets()
        assert b.effective_timeout_seconds() is None
