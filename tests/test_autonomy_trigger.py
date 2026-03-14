"""Tests for python/api/autonomy_trigger.py — event trigger API (AUTON-02)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from python.api.autonomy_trigger import AutonomyTrigger
from python.helpers.task_scheduler import TaskState


@pytest.fixture
def handler():
    return AutonomyTrigger(app=MagicMock(), thread_lock=MagicMock())


@pytest.fixture
def mock_request():
    return MagicMock()


class TestTriggerByTaskId:
    """Trigger existing task by ID."""

    @pytest.mark.asyncio
    async def test_run_existing_idle_task(self, handler, mock_request):
        """Expected use: trigger an idle task by UUID."""
        mock_task = MagicMock()
        mock_task.state = TaskState.IDLE
        mock_scheduler = MagicMock()
        mock_scheduler.reload = AsyncMock()
        mock_scheduler.get_task_by_uuid.return_value = mock_task
        mock_scheduler.run_task_by_uuid = AsyncMock()

        with patch("python.api.autonomy_trigger.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            result = await handler.process({"task_id": "abc-123"}, mock_request)

        assert result["success"] is True
        assert "abc-123" in result["message"]
        mock_scheduler.run_task_by_uuid.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_run_already_running_task(self, handler, mock_request):
        """Edge case: task already running returns error."""
        mock_task = MagicMock()
        mock_task.state = TaskState.RUNNING
        mock_scheduler = MagicMock()
        mock_scheduler.reload = AsyncMock()
        mock_scheduler.get_task_by_uuid.return_value = mock_task

        with patch("python.api.autonomy_trigger.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            result = await handler.process({"task_id": "abc-123"}, mock_request)

        assert "error" in result
        assert "already running" in result["error"]

    @pytest.mark.asyncio
    async def test_run_disabled_task(self, handler, mock_request):
        """Edge case: disabled task returns error."""
        mock_task = MagicMock()
        mock_task.state = TaskState.DISABLED
        mock_scheduler = MagicMock()
        mock_scheduler.reload = AsyncMock()
        mock_scheduler.get_task_by_uuid.return_value = mock_task

        with patch("python.api.autonomy_trigger.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            result = await handler.process({"task_id": "abc-123"}, mock_request)

        assert "error" in result
        assert "disabled" in result["error"]

    @pytest.mark.asyncio
    async def test_run_nonexistent_task(self, handler, mock_request):
        """Failure case: task not found."""
        mock_scheduler = MagicMock()
        mock_scheduler.reload = AsyncMock()
        mock_scheduler.get_task_by_uuid.return_value = None

        with patch("python.api.autonomy_trigger.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            result = await handler.process({"task_id": "nope"}, mock_request)

        assert "error" in result
        assert "not found" in result["error"]


class TestTriggerByGoal:
    """Enqueue a new goal."""

    @pytest.mark.asyncio
    async def test_enqueue_goal(self, handler, mock_request):
        """Expected use: goal prompt creates and enqueues task."""
        with patch(
            "python.api.autonomy_trigger.enqueue_goal", new_callable=AsyncMock
        ) as mock_eq:
            mock_eq.return_value = "goal-uuid-456"
            result = await handler.process(
                {"goal": "Scan the network", "context": "lab env"}, mock_request
            )

        assert result["success"] is True
        assert result["task_id"] == "goal-uuid-456"
        mock_eq.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_enqueue_with_attachments(self, handler, mock_request):
        """Edge case: goal with attachments."""
        with patch(
            "python.api.autonomy_trigger.enqueue_goal", new_callable=AsyncMock
        ) as mock_eq:
            mock_eq.return_value = "att-uuid"
            result = await handler.process(
                {"goal": "Analyze file", "attachments": ["file1.txt", "file2.txt"]},
                mock_request,
            )

        assert result["success"] is True
        call_kwargs = mock_eq.call_args
        assert call_kwargs.kwargs.get("attachments") == ["file1.txt", "file2.txt"]


class TestTriggerValidation:
    """Input validation."""

    @pytest.mark.asyncio
    async def test_no_task_id_or_goal_returns_error(self, handler, mock_request):
        """Failure case: empty input returns error."""
        result = await handler.process({}, mock_request)
        assert "error" in result
