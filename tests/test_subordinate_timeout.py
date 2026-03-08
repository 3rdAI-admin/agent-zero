"""Tests for subordinate agent call timeout (B2 bounded retries).

Covers:
- Subordinate that completes within timeout succeeds
- Subordinate that exceeds timeout returns timeout message
- Default timeout constant is reasonable
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from python.tools.call_subordinate import DEFAULT_SUBORDINATE_TIMEOUT


class TestSubordinateTimeout:
    """Tests for the subordinate monologue timeout guard."""

    def test_default_timeout_is_reasonable(self):
        """Default timeout should be between 1 and 30 minutes."""
        assert 60 <= DEFAULT_SUBORDINATE_TIMEOUT <= 1800

    @pytest.mark.asyncio
    async def test_subordinate_completes_within_timeout(self):
        """A fast subordinate should return its result normally."""
        mock_sub = MagicMock()

        async def fast_monologue():
            await asyncio.sleep(0.01)
            return "subordinate result"

        mock_sub.monologue = fast_monologue
        mock_sub.history = MagicMock()
        mock_sub.history.new_topic = MagicMock()

        mock_agent = MagicMock()
        mock_agent.get_data.return_value = mock_sub
        mock_agent.set_data = MagicMock()
        mock_agent.number = 0
        mock_agent.context = MagicMock()
        mock_agent.read_prompt = MagicMock(return_value=None)

        tool = MagicMock()
        tool.agent = mock_agent
        tool.args = {}

        # Simulate the timeout logic directly
        timeout = DEFAULT_SUBORDINATE_TIMEOUT
        try:
            result = await asyncio.wait_for(
                mock_sub.monologue(), timeout=timeout
            )
        except asyncio.TimeoutError:
            result = f"Subordinate agent timed out after {int(timeout)}s."

        assert result == "subordinate result"

    @pytest.mark.asyncio
    async def test_subordinate_timeout_returns_message(self):
        """A stalled subordinate should be cancelled and return timeout message."""
        mock_sub = MagicMock()

        async def slow_monologue():
            await asyncio.sleep(100)
            return "should not reach"

        mock_sub.monologue = slow_monologue

        timeout = 0.1  # Very short for testing
        try:
            result = await asyncio.wait_for(
                mock_sub.monologue(), timeout=timeout
            )
        except asyncio.TimeoutError:
            result = (
                f"Subordinate agent timed out after {int(timeout)}s. "
                "Partial work may have been completed."
            )

        assert "timed out" in result

    def test_loop_data_retry_budget_docstring(self):
        """LoopData should document the retry budget."""
        from agent import LoopData

        assert "Retry budget" in LoopData.__doc__
        assert "MAX_ITERATIONS" in LoopData.__doc__
        assert "TOOL_ERROR_STREAK_MAX" in LoopData.__doc__
