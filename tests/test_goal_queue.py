"""Tests for python/helpers/goal_queue.py — goal queue (AUTON-03)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from python.helpers.goal_queue import (
    _load_queue,
    _save_queue,
    enqueue_goal,
    list_queued,
    peek_next,
    pop_next,
)


@pytest.fixture(autouse=True)
def _isolate_queue(tmp_path, monkeypatch):
    """Redirect goal queue file to tmp_path so tests don't touch real data."""
    queue_file = str(tmp_path / "goal_queue.json")
    monkeypatch.setattr("python.helpers.goal_queue._queue_path", lambda: queue_file)


class TestQueuePersistence:
    """Load/save round-trip."""

    def test_empty_queue_returns_empty_list(self):
        """Expected use: fresh queue is empty."""
        assert _load_queue() == []

    def test_save_and_load_round_trip(self):
        """Expected use: saved UUIDs are loaded back."""
        _save_queue(["uuid-1", "uuid-2"])
        assert _load_queue() == ["uuid-1", "uuid-2"]

    def test_corrupt_json_returns_empty(self, tmp_path, monkeypatch):
        """Failure case: corrupt file treated as empty queue."""
        bad_file = str(tmp_path / "bad_queue.json")
        with open(bad_file, "w") as f:
            f.write("{bad json")
        monkeypatch.setattr("python.helpers.goal_queue._queue_path", lambda: bad_file)
        assert _load_queue() == []


class TestPopAndPeek:
    """Queue operations: pop, peek, list."""

    def test_pop_returns_first_and_removes(self):
        """Expected use: FIFO pop."""
        _save_queue(["a", "b", "c"])
        assert pop_next() == "a"
        assert _load_queue() == ["b", "c"]

    def test_pop_empty_returns_none(self):
        """Edge case: pop on empty queue."""
        assert pop_next() is None

    def test_peek_returns_first_without_removing(self):
        """Expected use: peek doesn't mutate."""
        _save_queue(["x", "y"])
        assert peek_next() == "x"
        assert _load_queue() == ["x", "y"]

    def test_peek_empty_returns_none(self):
        """Edge case: peek on empty queue."""
        assert peek_next() is None

    def test_list_queued_returns_copy(self):
        """Expected use: list_queued returns all UUIDs."""
        _save_queue(["1", "2", "3"])
        result = list_queued()
        assert result == ["1", "2", "3"]
        # Mutating the returned list doesn't affect the queue
        result.append("4")
        assert list_queued() == ["1", "2", "3"]


class TestEnqueueGoal:
    """enqueue_goal creates a task and appends UUID."""

    @pytest.mark.asyncio
    async def test_enqueue_creates_task_and_appends_uuid(self):
        """Expected use: enqueue adds UUID to queue and creates AdHocTask."""
        mock_scheduler = MagicMock()
        mock_scheduler.add_task = AsyncMock()

        with patch("python.helpers.goal_queue.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            uuid = await enqueue_goal(prompt="Do something useful")

        assert isinstance(uuid, str)
        assert len(uuid) > 0
        mock_scheduler.add_task.assert_awaited_once()
        assert uuid in list_queued()

    @pytest.mark.asyncio
    async def test_enqueue_multiple_preserves_order(self):
        """Edge case: multiple enqueues maintain FIFO order."""
        mock_scheduler = MagicMock()
        mock_scheduler.add_task = AsyncMock()

        uuids = []
        with patch("python.helpers.goal_queue.TaskScheduler") as MockTS:
            MockTS.get.return_value = mock_scheduler
            for i in range(3):
                u = await enqueue_goal(prompt=f"Goal {i}")
                uuids.append(u)

        queued = list_queued()
        assert queued == uuids
