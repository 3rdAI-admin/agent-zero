"""Tests for python/helpers/structured_log.py — structured JSON logging."""

import json
import logging

import pytest  # noqa: F401  (capsys fixture)

from python.helpers.structured_log import _JSONFormatter, get_logger


class TestJSONFormatter:
    """Tests for the _JSONFormatter class."""

    def setup_method(self):
        self.formatter = _JSONFormatter()

    def test_basic_format_produces_valid_json(self):
        """Expected use: a simple INFO log record produces valid JSON with required fields."""
        record = logging.LogRecord(
            name="a0.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="hello world",
            args=(),
            exc_info=None,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "a0.test"
        assert parsed["msg"] == "hello world"
        assert parsed["ts"].endswith("Z")

    def test_extra_fields_included(self):
        """Expected use: extra dict fields appear in the JSON output."""
        record = logging.LogRecord(
            name="a0.test",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="caution",
            args=(),
            exc_info=None,
        )
        record.source = "app"  # type: ignore[attr-defined]
        record.category = "warning"  # type: ignore[attr-defined]
        output = self.formatter.format(record)
        parsed = json.loads(output)
        assert parsed["source"] == "app"
        assert parsed["category"] == "warning"

    def test_exception_info_included(self):
        """Edge case: exception info is serialized into the JSON entry."""
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="a0.test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="failed",
            args=(),
            exc_info=exc_info,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)
        assert "exception" in parsed
        assert "ValueError: boom" in parsed["exception"]

    def test_non_serializable_extra_converted_to_str(self):
        """Edge case: non-JSON-serializable extra values become strings."""
        record = logging.LogRecord(
            name="a0.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )
        record.custom_obj = object()  # type: ignore[attr-defined]
        output = self.formatter.format(record)
        parsed = json.loads(output)
        assert "custom_obj" in parsed
        assert isinstance(parsed["custom_obj"], str)

    def test_format_args_interpolation(self):
        """Expected use: %-style args in msg are interpolated."""
        record = logging.LogRecord(
            name="a0.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="count=%d",
            args=(42,),
            exc_info=None,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)
        assert parsed["msg"] == "count=42"


class TestGetLogger:
    """Tests for the get_logger factory function."""

    def test_returns_logger_with_json_handler(self):
        """Expected use: returned logger has a handler with _JSONFormatter."""
        logger = get_logger("test_module")
        assert logger.name == "a0.test_module"
        assert len(logger.handlers) >= 1
        assert isinstance(logger.handlers[0].formatter, _JSONFormatter)

    def test_logger_does_not_propagate(self):
        """Expected use: logger.propagate is False so root logger doesn't double-emit."""
        logger = get_logger("test_no_propagate")
        assert logger.propagate is False

    def test_same_name_returns_same_logger(self):
        """Expected use: calling get_logger twice with same name returns the same instance."""
        a = get_logger("test_singleton")
        b = get_logger("test_singleton")
        assert a is b

    def test_logger_writes_json_to_stream(self):
        """Expected use: logger output is valid JSON written to handler stream."""
        import io

        logger = get_logger("test_stderr_output")
        # Capture by temporarily replacing the handler's stream
        buf = io.StringIO()
        handler = logger.handlers[0]
        original_stream = handler.stream
        handler.stream = buf
        try:
            logger.warning("test message")
        finally:
            handler.stream = original_stream
        lines = [line for line in buf.getvalue().strip().split("\n") if line]
        assert len(lines) >= 1
        parsed = json.loads(lines[-1])
        assert parsed["msg"] == "test message"
        assert parsed["level"] == "WARNING"

    def test_logger_level_filtering(self, capsys):
        """Failure case: messages below the logger's level are not emitted."""
        logger = get_logger("test_level_filter", level=logging.WARNING)
        logger.info("should not appear")
        captured = capsys.readouterr()
        # No output for INFO when level is WARNING
        assert "should not appear" not in captured.err
