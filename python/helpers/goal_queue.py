"""
Goal queue — explicit tasks/goals enqueued by user or system (AUTON-03).

Executor runs the same agent loop for queue-driven work. Goals are stored as
task UUIDs; enqueue creates an AdHocTask and appends its UUID to the queue.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from typing import Optional

from python.helpers.files import get_abs_path, make_dirs, read_file, write_file
from python.helpers.task_scheduler import (
    AdHocTask,
    TaskScheduler,
)
from python.helpers import guids

SCHEDULER_FOLDER = "usr/scheduler"
GOAL_QUEUE_FILE = "goal_queue.json"


def _queue_path() -> str:
    path = get_abs_path(SCHEDULER_FOLDER, GOAL_QUEUE_FILE)
    dir_path = get_abs_path(SCHEDULER_FOLDER)
    make_dirs(dir_path)
    return path


_lock = threading.RLock()


def _load_queue() -> list[str]:
    """Load list of task UUIDs from disk."""
    path = _queue_path()
    try:
        data = read_file(path)
        if not data or not data.strip():
            return []
        obj = json.loads(data)
        return obj.get("task_uuids", [])
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, TypeError):
        return []


def _save_queue(task_uuids: list[str]) -> None:
    """Persist list of task UUIDs."""
    with _lock:
        path = _queue_path()
        write_file(
            path,
            json.dumps(
                {
                    "task_uuids": task_uuids,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            ),
        )


async def enqueue_goal(
    prompt: str,
    system_prompt: str = "",
    context: Optional[str] = None,
    attachments: Optional[list[str]] = None,
    name: Optional[str] = None,
) -> str:
    """
    Create an AdHocTask for the goal, add it to TaskScheduler, and enqueue its UUID.
    Returns the task UUID.
    """
    task_name = name or f"goal-{guids.generate_id()[:8]}"
    token = str(guids.generate_id())[:16]
    task = AdHocTask.create(
        name=task_name,
        system_prompt=system_prompt
        or "You are an autonomous agent. Complete the user's goal.",
        prompt=prompt,
        token=token,
        attachments=attachments or [],
    )
    scheduler = TaskScheduler.get()
    await scheduler.add_task(task)
    with _lock:
        uuids = _load_queue()
        uuids.append(task.uuid)
        _save_queue(uuids)
    return task.uuid


def pop_next() -> Optional[str]:
    """Remove and return the next task UUID from the queue, or None if empty."""
    with _lock:
        uuids = _load_queue()
        if not uuids:
            return None
        task_uuid = uuids.pop(0)
        _save_queue(uuids)
        return task_uuid


def peek_next() -> Optional[str]:
    """Return the next task UUID without removing it."""
    with _lock:
        uuids = _load_queue()
        return uuids[0] if uuids else None


def list_queued() -> list[str]:
    """Return all queued task UUIDs (read-only)."""
    with _lock:
        return _load_queue().copy()
