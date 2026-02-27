"""
API message status endpoint.

Polls the status of an async API message task started via
/api_message_async. Returns the current status and result
(if completed).
"""

from agent import AgentContext
from python.helpers.api import ApiHandler, Request, Response


class ApiMessageStatus(ApiHandler):
    """Poll for the status of an async API message task.

    Returns the processing state of a given context_id and,
    when completed, the agent's response text.
    """

    @classmethod
    def requires_auth(cls) -> bool:
        return False

    @classmethod
    def requires_csrf(cls) -> bool:
        return False

    @classmethod
    def requires_api_key(cls) -> bool:
        return True

    @classmethod
    def get_methods(cls) -> list[str]:
        return ["POST", "GET"]

    async def process(self, input: dict, request: Request) -> dict | Response:
        """Check the status of a running or completed task.

        Args:
            input: Request body (POST) or query params (GET) with:
                context_id (str): Required. The context ID to check.

        Returns:
            dict: {
                "context_id": str,
                "status": "processing" | "completed" | "failed" | "idle" | "not_found",
                "response": str | None
            }
        """
        # Support both POST body and GET query params
        context_id = input.get("context_id", "") or request.args.get("context_id", "")

        if not context_id:
            return Response(
                '{"error": "context_id is required"}',
                status=400,
                mimetype="application/json",
            )

        context = AgentContext.get(context_id)
        if not context:
            return {
                "context_id": context_id,
                "status": "not_found",
                "response": None,
            }

        # Task is currently running
        if context.task and context.task.is_alive():
            return {
                "context_id": context_id,
                "status": "processing",
                "response": None,
            }

        # Check stored result (set by _process_chain)
        if context.last_result is not None:
            return {
                "context_id": context_id,
                "status": "completed",
                "response": context.last_result,
            }

        # Check stored error
        if context.last_error is not None:
            return {
                "context_id": context_id,
                "status": "failed",
                "response": context.last_error,
            }

        # Task finished but check future directly as fallback
        if context.task and context.task.is_ready():
            try:
                result = context.task._future.result(timeout=0)  # type: ignore
                return {
                    "context_id": context_id,
                    "status": "completed",
                    "response": str(result) if result else "",
                }
            except Exception as e:
                return {
                    "context_id": context_id,
                    "status": "failed",
                    "response": str(e),
                }

        # No task started or context is idle
        return {
            "context_id": context_id,
            "status": "idle",
            "response": None,
        }
