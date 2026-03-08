"""Regression tests for ResponseTool argument compatibility.

Verifies that ResponseTool handles all plausible argument shapes:
- text (canonical, from prompt template)
- message (legacy/alternate)
- content (alternate)
- empty args (should not raise)
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _make_response_tool(args: dict):
    """Create a ResponseTool instance with the given args dict."""
    from python.tools.response import ResponseTool

    tool = ResponseTool.__new__(ResponseTool)
    tool.args = args
    tool.agent = MagicMock()
    tool.name = "response"
    tool.message = MagicMock()
    tool.loop_data = MagicMock()
    return tool


class TestResponseToolCompat:
    """ResponseTool must accept text, message, or content without KeyError."""

    @pytest.mark.asyncio
    async def test_text_key(self):
        tool = _make_response_tool({"text": "hello from text"})
        resp = await tool.execute()
        assert resp.message == "hello from text"
        assert resp.break_loop is True

    @pytest.mark.asyncio
    async def test_message_key(self):
        tool = _make_response_tool({"message": "hello from message"})
        resp = await tool.execute()
        assert resp.message == "hello from message"
        assert resp.break_loop is True

    @pytest.mark.asyncio
    async def test_content_key(self):
        tool = _make_response_tool({"content": "hello from content"})
        resp = await tool.execute()
        assert resp.message == "hello from content"
        assert resp.break_loop is True

    @pytest.mark.asyncio
    async def test_empty_args_no_error(self):
        """Empty args should return empty string, not raise KeyError."""
        tool = _make_response_tool({})
        resp = await tool.execute()
        assert resp.message == ""
        assert resp.break_loop is True

    @pytest.mark.asyncio
    async def test_text_takes_priority(self):
        """When multiple keys present, text should win."""
        tool = _make_response_tool(
            {
                "text": "from text",
                "message": "from message",
                "content": "from content",
            }
        )
        resp = await tool.execute()
        assert resp.message == "from text"

    @pytest.mark.asyncio
    async def test_message_fallback_over_content(self):
        """message should be preferred over content when text is absent."""
        tool = _make_response_tool(
            {
                "message": "from message",
                "content": "from content",
            }
        )
        resp = await tool.execute()
        assert resp.message == "from message"
