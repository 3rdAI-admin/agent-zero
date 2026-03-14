"""
Kill switch API — stop an autonomous run (SAFETY-02).

User or system can stop a running task by task_id, or stop all runs for a context.
Governance: this intervention point cannot be removed by agent self-edit.
"""

from python.helpers.api import ApiHandler, Input, Output, Request
from python.helpers.task_scheduler import TaskScheduler
from python.helpers.print_style import PrintStyle


class AutonomyKill(ApiHandler):
    """Kill switch: stop running task(s)."""

    async def process(self, input: Input, request: Request) -> Output:
        task_id = (input.get("task_id") or input.get("task_uuid") or "").strip()
        context_id = (input.get("context_id") or input.get("context") or "").strip()
        terminate_thread = input.get("terminate_thread", True)

        scheduler = TaskScheduler.get()

        if task_id:
            ok = scheduler.cancel_running_task(
                task_id, terminate_thread=terminate_thread
            )
            if ok:
                PrintStyle.info(f"Kill switch: stopped task {task_id}")
                try:
                    from python.helpers import audit_log

                    audit_log.log_autonomy_kill(task_id=task_id)
                except Exception:
                    pass
                return {
                    "success": True,
                    "message": f"Task '{task_id}' stop requested.",
                    "task_id": task_id,
                }
            task = scheduler.get_task_by_uuid(task_id)
            if not task:
                return {"error": f"Task '{task_id}' not found.", "task_id": task_id}
            return {
                "error": f"Task '{task_id}' is not running (nothing to stop).",
                "task_id": task_id,
            }

        if context_id:
            ok = scheduler.cancel_tasks_by_context(
                context_id, terminate_thread=terminate_thread
            )
            if ok:
                PrintStyle.info(
                    f"Kill switch: stopped all tasks for context {context_id}"
                )
                try:
                    from python.helpers import audit_log

                    audit_log.log_autonomy_kill(context_id=context_id)
                except Exception:
                    pass
                return {
                    "success": True,
                    "message": f"All tasks for context '{context_id}' stop requested.",
                    "context_id": context_id,
                }
            return {
                "error": f"No running tasks found for context '{context_id}'.",
                "context_id": context_id,
            }

        return {
            "error": "Provide task_id or context_id to stop.",
        }
