import asyncio
import threading
from types import SimpleNamespace

from flask import Flask, Response

from python.api.chat_rename import MAX_CHAT_NAME_LENGTH, RenameChat


def test_chat_rename_updates_context_and_marks_dirty(monkeypatch):
    app = Flask(__name__)
    handler = RenameChat(app, threading.RLock())
    context = SimpleNamespace(id="ctx-1", name="Old name")
    saved_contexts = []
    dirty_reasons = []

    monkeypatch.setattr(handler, "use_context", lambda ctxid, create_if_not_exists=False: context)
    monkeypatch.setattr(
        "python.api.chat_rename.persist_chat.save_tmp_chat",
        lambda ctx: saved_contexts.append(ctx),
    )
    monkeypatch.setattr(
        "python.helpers.state_monitor_integration.mark_dirty_all",
        lambda reason: dirty_reasons.append(reason),
    )

    result = asyncio.run(
        handler.process({"context": "ctx-1", "name": "  Renamed chat  "}, None)
    )

    assert result["ok"] is True
    assert result["name"] == "Renamed chat"
    assert context.name == "Renamed chat"
    assert saved_contexts == [context]
    assert dirty_reasons == ["api.chat_rename.RenameChat"]


def test_chat_rename_truncates_overlong_names(monkeypatch):
    app = Flask(__name__)
    handler = RenameChat(app, threading.RLock())
    context = SimpleNamespace(id="ctx-1", name="Old name")

    monkeypatch.setattr(handler, "use_context", lambda ctxid, create_if_not_exists=False: context)
    monkeypatch.setattr("python.api.chat_rename.persist_chat.save_tmp_chat", lambda ctx: None)
    monkeypatch.setattr("python.helpers.state_monitor_integration.mark_dirty_all", lambda reason: None)

    result = asyncio.run(
        handler.process(
            {"context": "ctx-1", "name": "x" * (MAX_CHAT_NAME_LENGTH + 10)},
            None,
        )
    )

    assert result["name"] == "x" * MAX_CHAT_NAME_LENGTH
    assert context.name == "x" * MAX_CHAT_NAME_LENGTH


def test_chat_rename_rejects_blank_names():
    app = Flask(__name__)
    handler = RenameChat(app, threading.RLock())

    result = asyncio.run(handler.process({"context": "ctx-1", "name": "   "}, None))

    assert isinstance(result, Response)
    assert result.status_code == 400
    assert b"Chat name is required" in result.get_data()
