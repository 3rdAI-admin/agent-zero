"""Tests for python/helpers/autonomy_scheduler.py — APScheduler + SQLite (AUTON-01)."""

from unittest.mock import patch

import pytest

from python.helpers.task_scheduler import TaskSchedule
from python.helpers.autonomy_scheduler import (
    AutonomyScheduler,
    _schedule_to_trigger,
)


@pytest.fixture(autouse=True)
def _reset_singleton():
    """Reset the AutonomyScheduler singleton between tests."""
    AutonomyScheduler._instance = None
    AutonomyScheduler._scheduler = None
    AutonomyScheduler._started = False
    yield
    inst = AutonomyScheduler._instance
    if inst and inst._started:
        try:
            inst.shutdown(wait=False)
        except Exception:
            pass
    AutonomyScheduler._instance = None


class TestScheduleToTrigger:
    """Convert TaskSchedule to APScheduler CronTrigger."""

    def test_basic_cron_conversion(self):
        """Expected use: crontab fields map to CronTrigger."""
        schedule = TaskSchedule(
            minute="30", hour="2", day="*", month="*", weekday="*", timezone="UTC"
        )
        trigger = _schedule_to_trigger(schedule)
        assert trigger is not None
        assert str(trigger) != ""

    def test_complex_cron(self):
        """Edge case: complex cron expression."""
        schedule = TaskSchedule(
            minute="0,30",
            hour="9-17",
            day="1-15",
            month="1,6",
            weekday="mon-fri",
            timezone="America/New_York",
        )
        trigger = _schedule_to_trigger(schedule)
        assert trigger is not None

    def test_invalid_timezone_raises(self):
        """Failure case: bad timezone raises."""
        schedule = TaskSchedule(
            minute="0",
            hour="0",
            day="*",
            month="*",
            weekday="*",
            timezone="Not/A/Timezone",
        )
        with pytest.raises(Exception):
            _schedule_to_trigger(schedule)


class TestAutonomySchedulerSingleton:
    """Singleton pattern and lifecycle."""

    @patch("python.helpers.autonomy_scheduler._jobstore_url", return_value="sqlite:///")
    def test_get_returns_same_instance(self, _mock_url):
        """Expected use: get() returns singleton."""
        a = AutonomyScheduler.get()
        b = AutonomyScheduler.get()
        assert a is b

    @pytest.mark.asyncio
    @patch("python.helpers.autonomy_scheduler._jobstore_url", return_value="sqlite:///")
    async def test_start_and_shutdown(self, _mock_url):
        """Expected use: start/shutdown lifecycle."""
        sched = AutonomyScheduler.get()
        sched.start()
        assert sched._started is True
        sched.shutdown(wait=False)
        assert sched._started is False

    @pytest.mark.asyncio
    @patch("python.helpers.autonomy_scheduler._jobstore_url", return_value="sqlite:///")
    async def test_double_start_is_safe(self, _mock_url):
        """Edge case: calling start twice doesn't error."""
        sched = AutonomyScheduler.get()
        sched.start()
        sched.start()  # should not raise
        assert sched._started is True
        sched.shutdown(wait=False)

    @patch("python.helpers.autonomy_scheduler._jobstore_url", return_value="sqlite:///")
    def test_shutdown_without_start_is_safe(self, _mock_url):
        """Edge case: shutdown before start doesn't error."""
        sched = AutonomyScheduler.get()
        sched.shutdown()  # should not raise


class TestAutonomySchedulerJobs:
    """Job add/remove operations."""

    @pytest.mark.asyncio
    @patch("python.helpers.autonomy_scheduler._jobstore_url", return_value="sqlite:///")
    async def test_add_and_remove_job(self, _mock_url):
        """Expected use: add a job then remove it."""
        sched = AutonomyScheduler.get()
        sched.start()
        schedule = TaskSchedule(
            minute="0", hour="*", day="*", month="*", weekday="*", timezone="UTC"
        )
        sched.add_job_for_task("test-uuid-123", schedule)
        jobs = sched._scheduler.get_jobs()
        assert any(j.id == "test-uuid-123" for j in jobs)
        removed = sched.remove_job("test-uuid-123")
        assert removed is True
        jobs = sched._scheduler.get_jobs()
        assert not any(j.id == "test-uuid-123" for j in jobs)
        sched.shutdown(wait=False)

    @pytest.mark.asyncio
    @patch("python.helpers.autonomy_scheduler._jobstore_url", return_value="sqlite:///")
    async def test_remove_nonexistent_returns_false(self, _mock_url):
        """Failure case: removing a job that doesn't exist."""
        sched = AutonomyScheduler.get()
        sched.start()
        assert sched.remove_job("does-not-exist") is False
        sched.shutdown(wait=False)

    @pytest.mark.asyncio
    @patch("python.helpers.autonomy_scheduler._jobstore_url", return_value="sqlite:///")
    async def test_replace_existing_job(self, _mock_url):
        """Edge case: adding same UUID replaces the job."""
        sched = AutonomyScheduler.get()
        sched.start()
        schedule1 = TaskSchedule(
            minute="0", hour="1", day="*", month="*", weekday="*", timezone="UTC"
        )
        schedule2 = TaskSchedule(
            minute="30", hour="2", day="*", month="*", weekday="*", timezone="UTC"
        )
        sched.add_job_for_task("replace-uuid", schedule1)
        sched.add_job_for_task("replace-uuid", schedule2)
        jobs = [j for j in sched._scheduler.get_jobs() if j.id == "replace-uuid"]
        assert len(jobs) == 1
        sched.shutdown(wait=False)
