#!/usr/bin/env python3
"""
Update or list Archon project tasks via the Archon REST API.

Requires Archon server running (e.g. start_all.sh --archon).
Base URL: ARCHON_API_URL env or http://localhost:8181

Usage:
  python scripts/archon_api_tasks.py list [--project-id UUID]
  python scripts/archon_api_tasks.py create --project-id UUID --title "..." [--description "..." [--feature "..."]]
  python scripts/archon_api_tasks.py update TASK_ID --status done [--description "..."]

Examples:
  python scripts/archon_api_tasks.py list
  python scripts/archon_api_tasks.py list --project-id 610ae854-2244-4cb8-a291-1e31561377ab
  python scripts/archon_api_tasks.py create --project-id 610ae854-2244-4cb8-a291-1e31561377ab --title "Fix X" --feature improve-md
  python scripts/archon_api_tasks.py update 835f888b-xxxx --status done
"""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE = "http://localhost:8181"


def get_base_url() -> str:
    return os.environ.get("ARCHON_API_URL", DEFAULT_BASE).rstrip("/")


def api_get(path: str, params: dict | None = None) -> dict:
    url = f"{get_base_url()}{path}"
    if params:
        q = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if q:
            url += "?" + q
    req = Request(url, method="GET")
    req.add_header("Accept", "application/json")
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def api_put(path: str, data: dict) -> dict:
    url = f"{get_base_url()}{path}"
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, method="PUT")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def api_post(path: str, data: dict) -> dict:
    url = f"{get_base_url()}{path}"
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def cmd_list(project_id: str | None) -> int:
    params = {"include_closed": "true", "per_page": "50"}
    if project_id:
        params["project_id"] = project_id
    try:
        out = api_get("/api/tasks", params=params)
    except HTTPError as e:
        print(f"API error: {e.code} {e.reason}", file=sys.stderr)
        if e.fp:
            try:
                body = e.fp.read().decode()
                print(body, file=sys.stderr)
            except Exception:
                pass
        return 1
    except URLError as e:
        print(f"Request failed: {e.reason}", file=sys.stderr)
        return 1

    tasks = out.get("tasks", out) if isinstance(out, dict) else out
    if not isinstance(tasks, list):
        tasks = []
    for t in tasks:
        tid = t.get("id", "")
        status = t.get("status", "?")
        title = (t.get("title") or "")[:60]
        feature = t.get("feature") or ""
        print(f"  {tid}  {status:8}  {feature:20}  {title}")
    print(f"Total: {len(tasks)} tasks")
    return 0


def cmd_update(task_id: str, status: str | None, description: str | None) -> int:
    payload = {}
    if status is not None:
        payload["status"] = status
    if description is not None:
        payload["description"] = description
    if not payload:
        print("Provide at least one of --status or --description", file=sys.stderr)
        return 1
    try:
        out = api_put(f"/api/tasks/{task_id}", payload)
    except HTTPError as e:
        print(f"API error: {e.code} {e.reason}", file=sys.stderr)
        if e.fp:
            try:
                print(e.fp.read().decode(), file=sys.stderr)
            except Exception:
                pass
        return 1
    except URLError as e:
        print(f"Request failed: {e.reason}", file=sys.stderr)
        return 1

    task = out.get("task", out)
    print("Updated:", task.get("id"), task.get("status"), task.get("title", "")[:50])
    return 0


def cmd_create(project_id: str, title: str, description: str | None, feature: str | None) -> int:
    if not project_id or not title:
        print("Provide --project-id and --title", file=sys.stderr)
        return 1
    payload = {
        "project_id": project_id,
        "title": title[: 500] if len(title) > 500 else title,
        "description": description or "",
        "assignee": "User",
        "task_order": 0,
    }
    if feature:
        payload["feature"] = feature
    try:
        out = api_post("/api/tasks", payload)
    except HTTPError as e:
        print(f"API error: {e.code} {e.reason}", file=sys.stderr)
        if e.fp:
            try:
                print(e.fp.read().decode(), file=sys.stderr)
            except Exception:
                pass
        return 1
    except URLError as e:
        print(f"Request failed: {e.reason}", file=sys.stderr)
        return 1

    task = out.get("task", out)
    print("Created:", task.get("id"), task.get("status", "todo"), (task.get("title") or "")[:60])
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List or update Archon tasks via REST API (ARCHON_API_URL)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    list_p = sub.add_parser("list", help="List tasks (optional project filter)")
    list_p.add_argument(
        "--project-id",
        default=None,
        help="Project UUID (e.g. A0 SIP: 610ae854-2244-4cb8-a291-1e31561377ab)",
    )
    list_p.set_defaults(func=lambda a: cmd_list(a.project_id))

    up_p = sub.add_parser("update", help="Update a task by ID")
    up_p.add_argument("task_id", help="Task UUID (full or short)")
    up_p.add_argument(
        "--status",
        choices=["todo", "doing", "review", "done"],
        default=None,
        help="Set task status",
    )
    up_p.add_argument("--description", default=None, help="Set task description")
    up_p.set_defaults(
        func=lambda a: cmd_update(a.task_id, a.status, a.description)
    )

    create_p = sub.add_parser("create", help="Create a task")
    create_p.add_argument("--project-id", required=True, help="Project UUID")
    create_p.add_argument("--title", required=True, help="Task title")
    create_p.add_argument("--description", default=None, help="Task description")
    create_p.add_argument("--feature", default=None, help="Feature label (e.g. improve-md)")
    create_p.set_defaults(
        func=lambda a: cmd_create(a.project_id, a.title, a.description, a.feature)
    )

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
