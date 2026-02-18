from python.helpers.api import ApiHandler, Request, Response
from python.helpers import files, memory, notification, projects, notification, runtime
import os
from werkzeug.utils import secure_filename


class GetKnowledgePath(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        ctxid = input.get("ctxid", "")
        if not ctxid:
            raise Exception("No context id provided")
        context = self.use_context(ctxid)

        project_name = projects.get_context_project_name(context)
        if project_name:
            knowledge_folder = projects.get_project_meta_folder(project_name, "knowledge")
        else:
            knowledge_folder = memory.get_custom_knowledge_subdir_abs(context.agent0)

        # For native installs, return actual path; for Docker, normalize to /a0/
        if runtime.is_dockerized():
            knowledge_folder = files.normalize_a0_path(knowledge_folder)
        # For native installs, use the actual path as-is

        return {
            "ok": True,
            "path": knowledge_folder,
        }