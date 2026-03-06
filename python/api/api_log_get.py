import json
from agent import AgentContext
from python.helpers.api import ApiHandler, Request, Response


def _parse_length(
    value: str | int | None, default: int = 100, max_val: int = 1000
) -> int:
    """Parse length parameter; return default if invalid, clamp to [1, max_val]."""
    if value is None:
        return default
    try:
        n = int(value) if not isinstance(value, int) else value
    except (ValueError, TypeError):
        return default
    return max(1, min(n, max_val))


class ApiLogGet(ApiHandler):
    @classmethod
    def get_methods(cls) -> list[str]:
        return ["GET", "POST"]

    @classmethod
    def requires_auth(cls) -> bool:
        return False  # No web auth required

    @classmethod
    def requires_csrf(cls) -> bool:
        return False  # No CSRF required

    @classmethod
    def requires_api_key(cls) -> bool:
        return True  # Require API key

    async def process(self, input: dict, request: Request) -> dict | Response:
        # Extract parameters (support both query params for GET and body for POST)
        if request.method == "GET":
            context_id = request.args.get("context_id", "")
            length = _parse_length(request.args.get("length", 100))
        else:
            context_id = input.get("context_id", "")
            length = _parse_length(input.get("length", 100))

        if not context_id:
            return Response(
                '{"error": "context_id is required"}',
                status=400,
                mimetype="application/json",
            )

        # Get context
        context = AgentContext.use(context_id)
        if not context:
            return Response(
                '{"error": "Context not found"}',
                status=404,
                mimetype="application/json",
            )

        try:
            # Get total number of log items
            total_items = len(context.log.logs)

            # Calculate start position (from newest, so we work backwards)
            start_pos = max(0, total_items - length)

            # Get log items from the calculated start position
            log_items = context.log.output(start=start_pos)

            # Return log data with metadata
            return {
                "context_id": context_id,
                "log": {
                    "guid": context.log.guid,
                    "total_items": total_items,
                    "returned_items": len(log_items),
                    "start_position": start_pos,
                    "progress": context.log.progress,
                    "progress_active": bool(context.log.progress_active),
                    "items": log_items,
                },
            }

        except Exception:
            return Response(
                json.dumps({"error": "An error occurred retrieving the log"}),
                status=500,
                mimetype="application/json",
            )
