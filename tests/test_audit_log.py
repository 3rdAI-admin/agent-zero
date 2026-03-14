"""Tests for python/helpers/audit_log.py — append-only audit log (SAFETY-03)."""

import json
import os
import re
from unittest.mock import patch


from python.helpers import audit_log


ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


class TestAuditLogWrite:
    """Append-only write and path resolution."""

    def test_path_from_env(self, tmp_path):
        """Expected use: AGENTZ_AUDIT_LOG_PATH overrides default path."""
        env_path = tmp_path / "custom_audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.write("test_event", details={"k": "v"})
        assert env_path.exists()
        line = env_path.read_text().strip()
        obj = json.loads(line)
        assert obj["event"] == "test_event"
        assert obj["details"] == {"k": "v"}
        assert ISO_RE.match(obj["ts"]), f"Expected ISO timestamp, got {obj['ts']}"

    def test_iso_timestamp_format(self, tmp_path):
        """Timestamps use ISO 8601 UTC format, not epoch."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.write("ts_test")
        obj = json.loads(env_path.read_text().strip())
        assert ISO_RE.match(obj["ts"])
        assert obj["ts"].endswith("Z")

    def test_append_mode_multiple_writes(self, tmp_path):
        """Multiple writes produce multiple JSONL lines (append, not overwrite)."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.write("event_1")
            audit_log.write("event_2")
            audit_log.write("event_3")
        lines = env_path.read_text().strip().split("\n")
        assert len(lines) == 3
        assert json.loads(lines[0])["event"] == "event_1"
        assert json.loads(lines[2])["event"] == "event_3"

    def test_sanitize_truncates_long_strings(self, tmp_path):
        """Sanitization: long strings in details are truncated."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.write(
                "tool_execution",
                tool_name="code_execution_tool",
                tool_args={"code": "x" * 2000},
            )
        obj = json.loads(env_path.read_text().strip())
        # Args masked/truncated to _MAX_ARG_LEN (1000)
        assert len(obj["args"]["code"]) <= 1000

    def test_unwritable_path_does_not_raise(self, tmp_path):
        """Failure case: unwritable path silently fails (no app crash)."""
        env_path = tmp_path / "no_such_dir" / "deep" / "audit.jsonl"
        # Make parent read-only so creation fails
        parent = tmp_path / "no_such_dir"
        parent.mkdir()
        parent.chmod(0o444)
        try:
            with patch.dict(
                os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
            ):
                audit_log.write("should_not_crash")  # Must not raise
        finally:
            parent.chmod(0o755)


class TestLogToolCall:
    """log_tool_call records tool invocations."""

    def test_basic_tool_call(self, tmp_path):
        """Expected use: log_tool_call records tool, method, args, agent, context."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.log_tool_call(
                tool_name="code_execution_tool",
                method="python",
                tool_args={"code": "print('hi')"},
                agent_name="Agent 1",
                context_id="ctx-abc",
            )
        obj = json.loads(env_path.read_text().strip())
        assert obj["event"] == "tool_call"
        assert obj["tool"] == "code_execution_tool"
        assert obj["method"] == "python"
        assert obj["agent"] == "Agent 1"
        assert obj["context"] == "ctx-abc"
        assert "code" in obj["args"]

    def test_tool_call_none_method(self, tmp_path):
        """Edge case: method=None omits method key from record."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.log_tool_call(
                tool_name="memory_tool",
                method=None,
                tool_args={"query": "test"},
                agent_name="Agent 1",
                context_id="ctx-1",
            )
        obj = json.loads(env_path.read_text().strip())
        assert "method" not in obj


class TestLogToolResult:
    """log_tool_result records execution outcomes."""

    def test_success_result(self, tmp_path):
        """Expected use: successful tool result with duration."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.log_tool_result(
                tool_name="code_execution_tool",
                method="terminal",
                result_summary="output text here",
                success=True,
                agent_name="Agent 1",
                context_id="ctx-abc",
                duration_ms=142.567,
            )
        obj = json.loads(env_path.read_text().strip())
        assert obj["event"] == "tool_result"
        assert obj["tool"] == "code_execution_tool"
        assert obj["details"]["success"] is True
        assert obj["details"]["duration_ms"] == 142.6
        assert "output text" in obj["details"]["result"]

    def test_failure_result(self, tmp_path):
        """Edge case: failed tool result records success=False."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.log_tool_result(
                tool_name="code_execution_tool",
                method="python",
                result_summary="SyntaxError: invalid syntax",
                success=False,
                agent_name="Agent 1",
                context_id="ctx-1",
            )
        obj = json.loads(env_path.read_text().strip())
        assert obj["details"]["success"] is False

    def test_result_truncated(self, tmp_path):
        """Edge case: very long results are truncated."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.log_tool_result(
                tool_name="t",
                method=None,
                result_summary="x" * 2000,
                success=True,
            )
        obj = json.loads(env_path.read_text().strip())
        assert len(obj["details"]["result"]) <= 500


class TestSecretsMasking:
    """Args are masked via secrets filter when available."""

    def test_mask_args_with_secrets(self, tmp_path):
        """Expected use: secret values in args are replaced by placeholders."""
        with patch("python.helpers.secrets.get_secrets_manager") as mock_sm:
            sm_instance = mock_sm.return_value
            sm_instance.mask_values.side_effect = lambda text: text.replace(
                "supersecret123", "§§secret(API_KEY)"
            )
            result = audit_log._mask_args({"token": "supersecret123", "query": "hello"})
        assert result["token"] == "§§secret(API_KEY)"
        assert result["query"] == "hello"

    def test_mask_args_fallback_on_error(self):
        """Failure case: secrets module error falls back to truncation."""
        with patch(
            "python.helpers.secrets.get_secrets_manager",
            side_effect=Exception("no secrets"),
        ):
            result = audit_log._mask_args({"key": "value"})
        assert result["key"] == "value"  # Returned as-is (truncated, not masked)


class TestBackwardCompat:
    """Phase 1 convenience wrappers still work."""

    def test_log_tool_execution(self, tmp_path):
        """log_tool_execution writes correct event type."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.log_tool_execution(
                "code_execution_tool",
                {"runtime": "terminal", "code": "echo hi"},
                context_id="ctx-1",
            )
        obj = json.loads(env_path.read_text().strip())
        assert obj["event"] == "tool_execution"
        assert obj["tool"] == "code_execution_tool"
        assert obj["context"] == "ctx-1"

    def test_log_autonomy_trigger_and_kill(self, tmp_path):
        """autonomy_trigger and autonomy_kill write correct events."""
        env_path = tmp_path / "audit.jsonl"
        with patch.dict(
            os.environ, {"AGENTZ_AUDIT_LOG_PATH": str(env_path)}, clear=False
        ):
            audit_log.log_autonomy_trigger(task_id="t-1", goal="Do X")
            audit_log.log_autonomy_kill(task_id="t-1")
        lines = env_path.read_text().strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["event"] == "autonomy_trigger"
        assert json.loads(lines[0])["task_id"] == "t-1"
        assert json.loads(lines[1])["event"] == "autonomy_kill"
        assert json.loads(lines[1])["task_id"] == "t-1"
