"""Tests for code-execution pre-execution guards.

Covers:
- Oversized payload rejection (Python and Node.js)
- Triple-quote wrapper pattern detection (Python)
- Edge cases: just-under-limit, non-wrapper triple-quotes
"""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Reason: tty_session.py calls sys.stdin.reconfigure() at import time which
# fails in pytest.  Mock it before importing the tool.
_real_stdin = sys.stdin
if not hasattr(sys.stdin, "reconfigure"):
    sys.stdin = MagicMock()
    sys.stdin.reconfigure = MagicMock()


def _build_tool():
    """Create a minimal CodeExecution tool instance for unit testing."""
    from python.tools.code_execution_tool import CodeExecution

    tool = CodeExecution.__new__(CodeExecution)
    tool.agent = MagicMock()
    tool.agent.config = SimpleNamespace(code_exec_ssh_enabled=False)
    tool.agent.get_data.return_value = None
    tool.agent.set_data = MagicMock()
    tool.name = "code_execution"
    tool.args = {}
    tool.message = ""
    return tool


# ---------------------------------------------------------------------------
# Size threshold tests
# ---------------------------------------------------------------------------


class TestSizeThreshold:
    """Tests for oversized payload rejection."""

    @pytest.mark.asyncio
    async def test_python_rejects_oversized_code(self):
        tool = _build_tool()
        big_code = "x = 1\n" * 20_000  # well over 100KB
        result = await tool.execute_python_code(session=0, code=big_code)
        assert "too large" in result
        assert "Write the code to a file" in result

    @pytest.mark.asyncio
    async def test_nodejs_rejects_oversized_code(self):
        tool = _build_tool()
        big_code = "var x = 1;\n" * 15_000
        result = await tool.execute_nodejs_code(session=0, code=big_code)
        assert "too large" in result

    @pytest.mark.asyncio
    async def test_python_accepts_code_under_limit(self):
        """Code under the size limit should pass the guard (may fail later at execution)."""
        tool = _build_tool()
        small_code = "print('hello')"
        assert len(small_code) < tool.MAX_CODE_SIZE
        # We can't fully execute without a shell, but the guard should NOT trigger.
        # We patch terminal_session to avoid actual execution.
        tool.terminal_session = AsyncMock(return_value="hello")
        tool.format_command_for_output = MagicMock(return_value="print('hello')")
        result = await tool.execute_python_code(session=0, code=small_code)
        assert "too large" not in result


# ---------------------------------------------------------------------------
# Wrapper pattern tests
# ---------------------------------------------------------------------------


class TestWrapperPatternDetection:
    """Tests for triple-quote wrapper pattern detection."""

    @pytest.mark.asyncio
    async def test_rejects_triple_single_quote_wrapper(self):
        tool = _build_tool()
        code = "code = '''\nprint('hello')\n'''\nexec(code)"
        result = await tool.execute_python_code(session=0, code=code)
        assert "triple-quote wrapper" in result

    @pytest.mark.asyncio
    async def test_rejects_triple_double_quote_wrapper(self):
        tool = _build_tool()
        code = 'script = """\nimport os\nos.listdir()\n"""\nexec(script)'
        result = await tool.execute_python_code(session=0, code=code)
        assert "triple-quote wrapper" in result

    @pytest.mark.asyncio
    async def test_rejects_exec_with_triple_quotes(self):
        tool = _build_tool()
        code = 'exec("""\nprint("hello")\n""")'
        result = await tool.execute_python_code(session=0, code=code)
        assert "triple-quote wrapper" in result

    @pytest.mark.asyncio
    async def test_allows_normal_code_with_docstrings(self):
        """Docstrings that aren't assignment wrappers should pass."""
        tool = _build_tool()
        code = 'def foo():\n    """A docstring."""\n    return 42\nprint(foo())'
        # Should NOT trigger wrapper detection
        tool.terminal_session = AsyncMock(return_value="42")
        tool.format_command_for_output = MagicMock(return_value="...")
        result = await tool.execute_python_code(session=0, code=code)
        assert "triple-quote wrapper" not in result

    @pytest.mark.asyncio
    async def test_allows_triple_quote_in_print(self):
        """Triple quotes inside a print/string literal (not assignment) should pass."""
        tool = _build_tool()
        code = "print('''hello world''')"
        tool.terminal_session = AsyncMock(return_value="hello world")
        tool.format_command_for_output = MagicMock(return_value="...")
        result = await tool.execute_python_code(session=0, code=code)
        assert "triple-quote wrapper" not in result


# ---------------------------------------------------------------------------
# Guard ordering tests
# ---------------------------------------------------------------------------


class TestGuardOrdering:
    """Verify guards fire in the correct order."""

    @pytest.mark.asyncio
    async def test_size_check_fires_before_wrapper_check(self):
        """An oversized payload with a wrapper pattern should get the size error."""
        tool = _build_tool()
        # Build oversized code that also has a wrapper pattern
        big_code = "code = '''\n" + "x = 1\n" * 20_000 + "'''\nexec(code)"
        result = await tool.execute_python_code(session=0, code=big_code)
        assert "too large" in result
        assert "triple-quote" not in result

    @pytest.mark.asyncio
    async def test_wrapper_check_fires_before_ast_parse(self):
        """A wrapper pattern should be caught even if the code is syntactically valid."""
        tool = _build_tool()
        code = "code = '''\nprint(1)\n'''\nexec(code)"
        result = await tool.execute_python_code(session=0, code=code)
        assert "triple-quote wrapper" in result
