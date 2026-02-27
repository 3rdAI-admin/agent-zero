"""
Async API message endpoint.

Accepts the same parameters as /api_message but returns immediately
with a context_id that can be used to poll for results via
/api_message_status.
"""

import base64
import os
from agent import AgentContext, AgentContextType, UserMessage
from python.helpers.api import ApiHandler, Request, Response
from python.helpers import files
from python.helpers.print_style import PrintStyle
from werkzeug.utils import secure_filename
from initialize import initialize_agent


class ApiMessageAsync(ApiHandler):
    """Fire-and-forget API message handler.

    Starts agent processing in the background and returns immediately
    with a context_id for status polling via /api_message_status.
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

    async def process(self, input: dict, request: Request) -> dict | Response:
        """Accept a message and start async processing.

        Args:
            input: Request body with keys:
                message (str): Required. The user message.
                context_id (str): Optional. Existing context to continue.
                attachments (list): Optional. Base64-encoded file attachments.
                lifetime_hours (int): Optional. Context lifetime (default 24).

        Returns:
            dict: {"context_id": str, "status": "processing"}
        """
        context_id = input.get("context_id", "")
        message = input.get("message", "")
        attachments = input.get("attachments", [])

        if not message:
            return Response(
                '{"error": "Message is required"}',
                status=400,
                mimetype="application/json",
            )

        # Handle base64-encoded attachments
        attachment_paths: list[str] = []
        if attachments:
            upload_folder_int = "/a0/tmp/uploads"
            upload_folder_ext = files.get_abs_path("tmp/uploads")
            os.makedirs(upload_folder_ext, exist_ok=True)

            for attachment in attachments:
                if (
                    not isinstance(attachment, dict)
                    or "filename" not in attachment
                    or "base64" not in attachment
                ):
                    continue
                try:
                    filename = secure_filename(attachment["filename"])
                    if not filename:
                        continue
                    file_content = base64.b64decode(attachment["base64"])
                    save_path = os.path.join(upload_folder_ext, filename)
                    with open(save_path, "wb") as f:
                        f.write(file_content)
                    attachment_paths.append(os.path.join(upload_folder_int, filename))
                except Exception as e:
                    PrintStyle.error(
                        f"Failed to process attachment {attachment.get('filename', 'unknown')}: {e}"
                    )

        # Get or create context
        if context_id:
            context = AgentContext.use(context_id)
            if not context:
                return Response(
                    '{"error": "Context not found"}',
                    status=404,
                    mimetype="application/json",
                )
        else:
            config = initialize_agent()
            context = AgentContext(config=config, type=AgentContextType.USER)
            AgentContext.use(context.id)
            context_id = context.id

        # Log the message
        attachment_filenames = (
            [os.path.basename(path) for path in attachment_paths]
            if attachment_paths
            else []
        )
        PrintStyle(
            background_color="#6C3483", font_color="white", bold=True, padding=True
        ).print("External API message (async):")
        PrintStyle(font_color="white", padding=False).print(f"> {message}")

        context.log.log(
            type="user",
            heading="User message",
            content=message,
            kvps={"attachments": attachment_filenames},
        )

        # Start processing — fire and forget
        context.communicate(UserMessage(message, attachment_paths))

        # Return immediately
        return {
            "context_id": context_id,
            "status": "processing",
        }
