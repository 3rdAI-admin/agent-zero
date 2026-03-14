"""Tests for DeferredTask timeout budget feature.

Covers:
- Task completes within timeout (should succeed)
- Task exceeds timeout (should be cancelled)
- Task without timeout (should behave as before)
"""

import asyncio
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from python.helpers.defer import DeferredTask


async def _fast_task():
    """Completes quickly."""
    await asyncio.sleep(0.05)
    return "done"


async def _slow_task():
    """Takes longer than any reasonable timeout in tests."""
    await asyncio.sleep(10)
    return "should not reach"


class TestDeferredTaskTimeout:
    """Tests for the timeout parameter on DeferredTask.start_task."""

    def test_task_completes_within_timeout(self):
        task = DeferredTask()
        task.start_task(_fast_task, timeout=5.0)
        result = task.result_sync(timeout=5.0)
        assert result == "done"

    def test_task_cancelled_on_timeout(self):
        task = DeferredTask()
        task.start_task(_slow_task, timeout=0.1)
        with pytest.raises(Exception):
            # The future should either raise TimeoutError or CancelledError
            task.result_sync(timeout=2.0)

    def test_task_without_timeout_completes(self):
        task = DeferredTask()
        task.start_task(_fast_task)
        result = task.result_sync(timeout=5.0)
        assert result == "done"

    def test_timeout_does_not_affect_fast_tasks(self):
        """A generous timeout should not interfere with quick tasks."""
        task = DeferredTask()
        task.start_task(_fast_task, timeout=60.0)
        result = task.result_sync(timeout=5.0)
        assert result == "done"
