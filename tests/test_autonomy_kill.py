"""Tests for python/api/autonomy_kill.py — kill switch API (SAFETY-02)."""

from unittest.mock import MagicMock, patch

import pytest

from python.api.autonomy_kill import AutonomyKill


@pytest.fixture
def handler():
    return AutonomyKill(app=MagicMock(), thread_lock=MagicMock())


@pytest.fixture
def mock_request():
    return MagicMock()


class TestKillByTaskId:
    """Stop a running task by UUID."""

    @pytest.mark.asyncio
    async def test_kill_running_task(self, handler, mock_request):
        """Expected use: stop a running task."""
        mock_scheduler = MagicMock()
        mock_scheduler.cancel_running_task.return_value = True

        with patch("python.api.autonomy_kill.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            result = await handler.process({"task_id": "run-123"}, mock_request)

        assert result["success"] is True
        assert "run-123" in result["message"]
        mock_scheduler.cancel_running_task.assert_called_once_with(
            "run-123", terminate_thread=True
        )

    @pytest.mark.asyncio
    async def test_kill_not_running_task(self, handler, mock_request):
        """Edge case: task exists but isn't running."""
        mock_scheduler = MagicMock()
        mock_scheduler.cancel_running_task.return_value = False
        mock_task = MagicMock()
        mock_scheduler.get_task_by_uuid.return_value = mock_task

        with patch("python.api.autonomy_kill.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            result = await handler.process({"task_id": "idle-456"}, mock_request)

        assert "error" in result
        assert "not running" in result["error"]

    @pytest.mark.asyncio
    async def test_kill_nonexistent_task(self, handler, mock_request):
        """Failure case: task doesn't exist."""
        mock_scheduler = MagicMock()
        mock_scheduler.cancel_running_task.return_value = False
        mock_scheduler.get_task_by_uuid.return_value = None

        with patch("python.api.autonomy_kill.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            result = await handler.process({"task_id": "nope"}, mock_request)

        assert "error" in result
        assert "not found" in result["error"]


class TestKillByContext:
    """Stop all tasks for a context."""

    @pytest.mark.asyncio
    async def test_kill_by_context(self, handler, mock_request):
        """Expected use: stop all running tasks for a context."""
        mock_scheduler = MagicMock()
        mock_scheduler.cancel_tasks_by_context.return_value = True

        with patch("python.api.autonomy_kill.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            result = await handler.process({"context_id": "ctx-789"}, mock_request)

        assert result["success"] is True
        assert "ctx-789" in result["message"]

    @pytest.mark.asyncio
    async def test_kill_context_no_running_tasks(self, handler, mock_request):
        """Edge case: no running tasks for the context."""
        mock_scheduler = MagicMock()
        mock_scheduler.cancel_tasks_by_context.return_value = False

        with patch("python.api.autonomy_kill.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            result = await handler.process({"context_id": "empty-ctx"}, mock_request)

        assert "error" in result
        assert "No running tasks" in result["error"]


class TestKillValidation:
    """Input validation."""

    @pytest.mark.asyncio
    async def test_no_task_id_or_context_returns_error(self, handler, mock_request):
        """Failure case: empty input."""
        with patch("python.api.autonomy_kill.TaskScheduler") as MockTS:
            MockTS.get.return_value = MagicMock()
            result = await handler.process({}, mock_request)

        assert "error" in result
        assert "Provide" in result["error"]

    @pytest.mark.asyncio
    async def test_terminate_thread_flag_passed(self, handler, mock_request):
        """Expected use: terminate_thread=False is forwarded."""
        mock_scheduler = MagicMock()
        mock_scheduler.cancel_running_task.return_value = True

        with patch("python.api.autonomy_kill.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            await handler.process(
                {"task_id": "t-1", "terminate_thread": False}, mock_request
            )

        mock_scheduler.cancel_running_task.assert_called_once_with(
            "t-1", terminate_thread=False
        )
