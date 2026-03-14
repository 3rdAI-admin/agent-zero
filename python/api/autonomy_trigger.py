"""
Event trigger API — run a task by UUID or enqueue a goal (AUTON-02).

POST body: {"task_id": "uuid"} to run existing task, or
{"goal": "prompt", "context": "...", "system_prompt": "..."} to enqueue a new goal.
Governance: trigger source is configurable; this endpoint is the webhook/event entry.
"""

from python.helpers.api import ApiHandler, Input, Output, Request
from python.helpers.task_scheduler import TaskScheduler, TaskState
from python.helpers.goal_queue import enqueue_goal
from python.helpers.print_style import PrintStyle


class AutonomyTrigger(ApiHandler):
    """Webhook/event trigger: run task by ID or enqueue a goal."""

    async def process(self, input: Input, request: Request) -> Output:
        task_id = (input.get("task_id") or input.get("task_uuid") or "").strip()
        goal = (input.get("goal") or input.get("prompt") or "").strip()

        if task_id:
            task_context = (input.get("context") or "").strip() or None
            return await self._run_task(task_id, task_context)
        if goal:
            return await self._enqueue_goal(input)
        return {
            "error": "Provide either task_id (to run existing task) or goal (to enqueue a new goal).",
        }

    async def _run_task(self, task_id: str, task_context: str | None = None) -> Output:
        scheduler = TaskScheduler.get()
        await scheduler.reload()
        task = scheduler.get_task_by_uuid(task_id)
        if not task:
            return {"error": f"Task '{task_id}' not found."}
        if task.state == TaskState.RUNNING:
            return {
                "error": f"Task '{task_id}' is already running.",
                "task_id": task_id,
            }
        if task.state == TaskState.DISABLED:
            return {"error": f"Task '{task_id}' is disabled.", "task_id": task_id}

        try:
            await scheduler.run_task_by_uuid(task_id, task_context=task_context)
            from python.helpers import audit_log

            audit_log.log_autonomy_trigger(task_id=task_id, context_id=task_context)
            return {
                "success": True,
                "message": f"Task '{task_id}' started.",
                "task_id": task_id,
            }
        except ValueError as e:
            return {"error": str(e), "task_id": task_id}
        except Exception as e:
            PrintStyle.error(f"AutonomyTrigger run_task {task_id}: {e}")
            try:
                from python.helpers import audit_log

                audit_log.log_autonomy_trigger(
                    task_id=task_id, context_id=task_context, error=str(e)
                )
            except Exception:
                pass
            return {"error": f"Failed to start task: {e}", "task_id": task_id}

    async def _enqueue_goal(self, input: Input) -> Output:
        goal = (input.get("goal") or input.get("prompt") or "").strip()
        context = (input.get("context") or "").strip() or None
        system_prompt = (input.get("system_prompt") or "").strip() or ""
        name = (input.get("name") or "").strip() or None
        attachments = input.get("attachments")
        if isinstance(attachments, list):
            attachments = [str(a) for a in attachments]
        else:
            attachments = None

        task_uuid = await enqueue_goal(
            prompt=goal,
            system_prompt=system_prompt,
            context=context,
            attachments=attachments,
            name=name,
        )
        try:
            from python.helpers import audit_log

            audit_log.log_autonomy_trigger(
                task_id=task_uuid, goal=goal, context_id=context
            )
        except Exception:
            pass
        return {
            "success": True,
            "message": "Goal enqueued.",
            "task_id": task_uuid,
        }
