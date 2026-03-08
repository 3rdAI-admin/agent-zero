from python.helpers.api import ApiHandler, Input, Output, Request, Response

from python.helpers import persist_chat


MAX_CHAT_NAME_LENGTH = 40


class RenameChat(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        """Rename an existing chat context and persist the updated display name."""
        ctxid = input.get("context", "")
        raw_name = input.get("name", "")
        name = str(raw_name).strip()

        if not ctxid:
            return Response(
                '{"error": "Context is required"}',
                status=400,
                mimetype="application/json",
            )

        if not name:
            return Response(
                '{"error": "Chat name is required"}',
                status=400,
                mimetype="application/json",
            )

        if len(name) > MAX_CHAT_NAME_LENGTH:
            name = name[:MAX_CHAT_NAME_LENGTH]

        context = self.use_context(ctxid, create_if_not_exists=False)
        context.name = name
        persist_chat.save_tmp_chat(context)

        from python.helpers.state_monitor_integration import mark_dirty_all

        mark_dirty_all(reason="api.chat_rename.RenameChat")

        return {
            "ok": True,
            "context": context.id,
            "name": context.name,
            "message": "Chat renamed.",
        }
