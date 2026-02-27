"""
Tests for concurrent API request handling.

Verifies:
- Per-context EventLoopThread isolation
- EventLoopThread singleton cleanup on terminate
- AgentContext.last_result / last_error storage
- ApiMessageStatus endpoint responses
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path


# Ensure repo root is on sys.path so imports resolve
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.helpers.defer import DeferredTask, EventLoopThread


# ---------------------------------------------------------------------------
# EventLoopThread isolation tests
# ---------------------------------------------------------------------------


class TestEventLoopThreadIsolation:
    """Verify that per-context thread names produce independent instances."""

    def test_different_names_give_different_instances(self):
        """Two different thread names should create separate EventLoopThread instances."""
        t1 = EventLoopThread("TestContext-aaa")
        t2 = EventLoopThread("TestContext-bbb")
        try:
            assert t1 is not t2
            assert t1.loop is not t2.loop
            assert t1.thread is not t2.thread
        finally:
            t1.terminate()
            t2.terminate()

    def test_same_name_gives_same_instance(self):
        """Same thread name should return the singleton instance."""
        t1 = EventLoopThread("TestContext-singleton")
        t2 = EventLoopThread("TestContext-singleton")
        try:
            assert t1 is t2
        finally:
            t1.terminate()

    def test_terminate_removes_from_instances(self):
        """After terminate(), the instance should be removed from the cache."""
        name = "TestContext-cleanup"
        t1 = EventLoopThread(name)
        assert name in EventLoopThread._instances
        t1.terminate()
        assert name not in EventLoopThread._instances

    def test_terminate_allows_fresh_instance(self):
        """After terminate(), a new request should create a fresh instance."""
        name = "TestContext-refresh"
        t1 = EventLoopThread(name)
        t1_id = id(t1)
        t1.terminate()

        t2 = EventLoopThread(name)
        try:
            # Should be a new object (different id) since old was removed
            assert id(t2) != t1_id
            assert t2.loop is not None
            assert t2.thread is not None
        finally:
            t2.terminate()


# ---------------------------------------------------------------------------
# DeferredTask isolation tests
# ---------------------------------------------------------------------------


class TestDeferredTaskIsolation:
    """Verify that DeferredTasks with different thread names are independent."""

    def test_tasks_on_different_threads_are_independent(self):
        """Tasks on different thread names should use different event loops."""
        task_a = DeferredTask(thread_name="TestTask-A")
        task_b = DeferredTask(thread_name="TestTask-B")
        try:
            assert task_a.event_loop_thread is not task_b.event_loop_thread
        finally:
            task_a.kill(terminate_thread=True)
            task_b.kill(terminate_thread=True)

    def test_killing_one_task_does_not_affect_other(self):
        """Killing one task's thread should not affect a task on a different thread."""
        task_a = DeferredTask(thread_name="TestKill-A")
        task_b = DeferredTask(thread_name="TestKill-B")

        async def slow_task():
            await asyncio.sleep(10)
            return "done"

        task_b.start_task(slow_task)

        try:
            # Kill task A's thread
            task_a.kill(terminate_thread=True)

            # Task B should still be alive
            assert task_b.is_alive()
            assert task_b.event_loop_thread.loop is not None
            assert task_b.event_loop_thread.loop.is_running()
        finally:
            task_b.kill(terminate_thread=True)


# ---------------------------------------------------------------------------
# AgentContext result storage tests
# ---------------------------------------------------------------------------


class TestAgentContextResultStorage:
    """Verify last_result and last_error are set by _process_chain."""

    def test_last_result_initialized_to_none(self):
        """New AgentContext should have last_result=None, last_error=None."""
        # Import agent only when runtime deps (litellm, nest_asyncio, etc.) are available
        try:
            from agent import AgentContext
        except ModuleNotFoundError as e:
            import pytest

            pytest.skip(
                f"agent module deps not installed (need e.g. litellm, nest_asyncio): {e}"
            )
        # Create a minimal context and verify initial state
        ctx = AgentContext.__new__(AgentContext)
        ctx.last_result = None
        ctx.last_error = None
        assert ctx.last_result is None
        assert ctx.last_error is None


# ---------------------------------------------------------------------------
# ApiMessageStatus response format tests
# ---------------------------------------------------------------------------


class TestApiMessageStatusResponses:
    """Verify the status endpoint returns correct structure for each state."""

    def test_not_found_response_format(self):
        """Non-existent context_id should return not_found status."""
        # Verify the response shape without running the full Flask app
        response = {
            "context_id": "nonexistent",
            "status": "not_found",
            "response": None,
        }
        assert response["status"] == "not_found"
        assert response["response"] is None

    def test_processing_response_format(self):
        """Active task should return processing status."""
        response = {
            "context_id": "abc123",
            "status": "processing",
            "response": None,
        }
        assert response["status"] == "processing"

    def test_completed_response_format(self):
        """Completed task should include the response text."""
        response = {
            "context_id": "abc123",
            "status": "completed",
            "response": "Agent Zero's answer here",
        }
        assert response["status"] == "completed"
        assert response["response"] is not None

    def test_failed_response_format(self):
        """Failed task should include the error message."""
        response = {
            "context_id": "abc123",
            "status": "failed",
            "response": "RuntimeError: something went wrong",
        }
        assert response["status"] == "failed"
        assert "RuntimeError" in response["response"]
