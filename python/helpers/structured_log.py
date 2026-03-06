"""Structured JSON logging for Agent Zero.

Emits JSON log lines to stderr so they can be parsed by log aggregators
(e.g. Docker logging drivers, fluentd, Loki) while keeping the existing
styled console output on stdout and HTML file logging untouched.

Usage:
    from python.helpers.structured_log import get_logger

    logger = get_logger("mymodule")
    logger.info("something happened", extra={"key": "value"})

The JSON format:
    {"ts": "2026-03-05T12:00:00.123Z", "level": "INFO", "logger": "mymodule", "msg": "...", ...extra}
"""

import json
import logging
import sys
from datetime import datetime, timezone


class _JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )[:-3] + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Merge extra fields passed via `extra={"key": "val"}` on the log call.
        # Skip internal LogRecord attributes to avoid noise.
        _SKIP = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())
        for key, val in record.__dict__.items():
            if key not in _SKIP and key not in entry:
                try:
                    json.dumps(val)  # ensure serializable
                    entry[key] = val
                except (TypeError, ValueError):
                    entry[key] = str(val)

        if record.exc_info and record.exc_info[1] is not None:
            entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(entry, default=str, ensure_ascii=False)


# Singleton handler shared by all structured loggers — writes to stderr.
_handler: logging.StreamHandler | None = None


def _get_handler() -> logging.StreamHandler:
    global _handler
    if _handler is None:
        _handler = logging.StreamHandler(sys.stderr)
        _handler.setFormatter(_JSONFormatter())
    return _handler


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger that emits structured JSON to stderr.

    Args:
        name: Logger name (e.g. "app", "api", "mcp").
        level: Minimum log level. Defaults to INFO.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(f"a0.{name}")
    if not logger.handlers:
        logger.addHandler(_get_handler())
        logger.setLevel(level)
        logger.propagate = False  # Don't bubble up to root (which is WARNING)
    return logger
