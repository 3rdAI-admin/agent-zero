from python.helpers.api import ApiHandler, Request, Response
from python.helpers import files, memory, notification, projects, notification, runtime
import os
from werkzeug.utils import secure_filename


class GetChatFilesPath(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        ctxid = input.get("ctxid", "")
        if not ctxid:
            raise Exception("No context id provided")
        context = self.use_context(ctxid)

        project_name = projects.get_context_project_name(context)
        if project_name:
            project_path = projects.get_project_folder(project_name)
            # For native installs, return actual path; for Docker, normalize to /a0/
            if runtime.is_dockerized():
                folder = files.normalize_a0_path(project_path)
            else:
                folder = project_path
        else:
            # For native installs, use home directory; for Docker, use /root
            if runtime.is_dockerized():
                folder = "/root"  # root in container
            else:
                folder = os.path.expanduser("~")  # user home directory

        return {
            "ok": True,
            "path": folder,
        }