"""
Autonomy scheduler — APScheduler + SQLite job store for Phase 1 (when to act).

Jobs persist across container restarts. When a job fires, it runs the
existing TaskScheduler task by UUID so the executor is agnostic to trigger type.
Governance: this module is part of the immutable autonomy layer; agent cannot
disable or edit it.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger

from python.helpers.files import get_abs_path, make_dirs
from python.helpers.print_style import PrintStyle

if TYPE_CHECKING:
    from python.helpers.task_scheduler import TaskSchedule

SCHEDULER_FOLDER = "usr/scheduler"
AUTONOMY_DB = "autonomy_jobs.sqlite"
JOBSTORE_NAME = "default"


def _jobstore_url() -> str:
    """SQLite URL for job store; ensures directory exists."""
    dir_path = get_abs_path(SCHEDULER_FOLDER)
    if not os.path.isdir(dir_path):
        make_dirs(get_abs_path(SCHEDULER_FOLDER))
    path = get_abs_path(SCHEDULER_FOLDER, AUTONOMY_DB)
    return f"sqlite:///{path}"


async def _run_scheduled_task(task_uuid: str) -> None:
    """Job payload: run TaskScheduler task by UUID (same executor for all triggers)."""
    from python.helpers.task_scheduler import TaskScheduler

    scheduler = TaskScheduler.get()
    try:
        await scheduler.run_task_by_uuid(task_uuid)
    except ValueError as e:
        PrintStyle.warning(f"Autonomy scheduler job for task {task_uuid} skipped: {e}")
    except Exception as e:
        PrintStyle.error(f"Autonomy scheduler job for task {task_uuid} failed: {e}")


def _schedule_to_trigger(schedule: "TaskSchedule") -> CronTrigger:
    """Convert TaskSchedule (crontab fields) to APScheduler CronTrigger."""
    tz = pytz.timezone(schedule.timezone or "UTC")
    return CronTrigger(
        minute=schedule.minute,
        hour=schedule.hour,
        day=schedule.day,
        month=schedule.month,
        day_of_week=schedule.weekday,
        timezone=tz,
    )


class AutonomyScheduler:
    """APScheduler wrapper with SQLite job store; syncs with TaskScheduler scheduled tasks."""

    _instance: Optional["AutonomyScheduler"] = None
    _scheduler: Optional[AsyncIOScheduler] = None
    _started: bool = False

    @classmethod
    def get(cls) -> "AutonomyScheduler":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        jobstores = {
            JOBSTORE_NAME: SQLAlchemyJobStore(url=_jobstore_url()),
        }
        self._scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            job_defaults={"coalesce": True, "max_instances": 1},
        )
        self._initialized = True

    def start(self) -> None:
        """Start the scheduler; safe to call from asyncio loop only."""
        if self._scheduler is None or self._started:
            return
        self._scheduler.start()
        self._started = True
        PrintStyle.info("Autonomy scheduler (APScheduler + SQLite) started.")

    def shutdown(self, wait: bool = True) -> None:
        """Stop the scheduler."""
        if self._scheduler is None or not self._started:
            return
        self._scheduler.shutdown(wait=wait)
        self._started = False
        PrintStyle.info("Autonomy scheduler shut down.")

    def add_job_for_task(self, task_uuid: str, schedule: "TaskSchedule") -> None:
        """Add or replace a cron job for the given task UUID."""
        if self._scheduler is None:
            return
        trigger = _schedule_to_trigger(schedule)
        # Run coroutine in executor: APScheduler will run the coroutine in the event loop
        self._scheduler.add_job(
            _run_scheduled_task,
            trigger=trigger,
            id=task_uuid,
            name=task_uuid,
            args=[task_uuid],
            replace_existing=True,
            jobstore=JOBSTORE_NAME,
        )

    def remove_job(self, task_uuid: str) -> bool:
        """Remove job by task UUID. Returns True if a job was removed."""
        if self._scheduler is None:
            return False
        try:
            self._scheduler.remove_job(task_uuid, jobstore=JOBSTORE_NAME)
            return True
        except Exception:
            return False

    def sync_scheduled_tasks(self) -> None:
        """
        Sync APScheduler jobs with TaskScheduler scheduled tasks.
        - Adds/updates jobs for every ScheduledTask that is IDLE or DISABLED (we still
          register so next run time is correct; execution is skipped by TaskScheduler if disabled).
        - Removes jobs for task UUIDs that no longer exist or are not scheduled type.
        """
        from python.helpers.task_scheduler import TaskScheduler, ScheduledTask

        scheduler = TaskScheduler.get()
        tasks = scheduler.get_tasks()
        scheduled_uuids = set()
        for task in tasks:
            if isinstance(task, ScheduledTask):
                scheduled_uuids.add(task.uuid)
                self.add_job_for_task(task.uuid, task.schedule)

        if self._scheduler is None:
            return
        for job in self._scheduler.get_jobs(jobstore=JOBSTORE_NAME):
            if job.id not in scheduled_uuids:
                self.remove_job(job.id)
