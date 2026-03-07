import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import run_ui


def test_socketio_engine_configuration_defaults():
    server = run_ui.socketio_server.eio

    assert server.ping_interval == 25
    assert server.ping_timeout == 20
    assert server.max_http_buffer_size == 50 * 1024 * 1024


class TestHealthCheckAccessLogFilter:
    """Tests for _HealthCheckAccessLogFilter."""

    def test_suppresses_health_200(self):
        """Health check GET /health 200 should be filtered out."""
        f = run_ui._HealthCheckAccessLogFilter()
        record = logging.LogRecord(
            "uvicorn.access", logging.INFO, "", 0, "%s", (), None
        )
        record.args = ("127.0.0.1:1234", "GET", "/health", "HTTP/1.1", 200)
        assert f.filter(record) is False

    def test_passes_other_requests(self):
        """Non-health requests should pass through."""
        f = run_ui._HealthCheckAccessLogFilter()
        record = logging.LogRecord(
            "uvicorn.access", logging.INFO, "", 0, "%s", (), None
        )
        record.args = ("127.0.0.1:1234", "GET", "/api/test", "HTTP/1.1", 200)
        assert f.filter(record) is True

    def test_passes_health_non_200(self):
        """Health check with non-200 status should pass through."""
        f = run_ui._HealthCheckAccessLogFilter()
        record = logging.LogRecord(
            "uvicorn.access", logging.INFO, "", 0, "%s", (), None
        )
        record.args = ("127.0.0.1:1234", "GET", "/health", "HTTP/1.1", 500)
        assert f.filter(record) is True


class TestInvalidHTTPRequestFilter:
    """Tests for _InvalidHTTPRequestFilter."""

    def test_suppresses_invalid_http_warning(self):
        """'Invalid HTTP request received' WARNING should be filtered out."""
        f = run_ui._InvalidHTTPRequestFilter()
        record = logging.LogRecord(
            "uvicorn.error",
            logging.WARNING,
            "",
            0,
            "Invalid HTTP request received.",
            (),
            None,
        )
        assert f.filter(record) is False

    def test_passes_other_warnings(self):
        """Other WARNING messages should pass through."""
        f = run_ui._InvalidHTTPRequestFilter()
        record = logging.LogRecord(
            "uvicorn.error",
            logging.WARNING,
            "",
            0,
            "Some other warning",
            (),
            None,
        )
        assert f.filter(record) is True

    def test_passes_error_level(self):
        """ERROR level messages mentioning 'Invalid HTTP' should pass (only suppress WARNING)."""
        f = run_ui._InvalidHTTPRequestFilter()
        record = logging.LogRecord(
            "uvicorn.error",
            logging.ERROR,
            "",
            0,
            "Invalid HTTP request received.",
            (),
            None,
        )
        assert f.filter(record) is True
