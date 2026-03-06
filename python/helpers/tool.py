import time
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from agent import Agent, LoopData
from python.helpers.print_style import PrintStyle
from python.helpers.strings import sanitize_string


class PolicyViolation(Exception):
    """Raised when a tool execution is blocked by governance policy."""

    pass


@dataclass
class Response:
    message: str
    break_loop: bool
    additional: dict[str, Any] | None = None


class Tool:
    def __init__(
        self,
        agent: Agent,
        name: str,
        method: str | None,
        args: dict[str, str],
        message: str,
        loop_data: LoopData | None,
        **kwargs,
    ) -> None:
        self.agent = agent
        self.name = name
        self.method = method
        self.args = args
        self.loop_data = loop_data
        self.message = message
        self.progress: str = ""

    @abstractmethod
    async def execute(self, **kwargs) -> Response:
        pass

    def set_progress(self, content: str | None):
        self.progress = content or ""

    def add_progress(self, content: str | None):
        if not content:
            return
        self.progress += content

    async def before_execution(self, **kwargs):
        # Policy check: is this tool allowed by governance?
        try:
            from python.helpers.tool_policy import is_tool_allowed

            allowed, reason = is_tool_allowed(self.name)
            if not allowed:
                from python.helpers.audit_log import write as audit_write

                audit_write(
                    "policy_violation",
                    tool_name=self.name,
                    agent_name=self.agent.agent_name,
                    context_id=self.agent.context.id,
                    details={"reason": reason},
                )
                raise PolicyViolation(reason)
        except PolicyViolation:
            raise
        except Exception:
            pass  # Policy module unavailable; allow execution

        PrintStyle(
            font_color="#1B4F72", padding=True, background_color="white", bold=True
        ).print(f"{self.agent.agent_name}: Using tool '{self.name}'")
        self.log = self.get_log_object()
        self._exec_start = time.monotonic()
        if self.args and isinstance(self.args, dict):
            for key, value in self.args.items():
                PrintStyle(font_color="#85C1E9", bold=True).stream(
                    self.nice_key(key) + ": "
                )
                PrintStyle(
                    font_color="#85C1E9",
                    padding=isinstance(value, str) and "\n" in value,
                ).stream(value)
                PrintStyle().print()

        # Audit: record tool invocation
        try:
            from python.helpers.audit_log import log_tool_call

            log_tool_call(
                tool_name=self.name,
                method=self.method,
                tool_args=self.args if isinstance(self.args, dict) else {},
                agent_name=self.agent.agent_name,
                context_id=self.agent.context.id,
            )
        except Exception:
            pass  # Audit must never break tool execution

    async def after_execution(self, response: Response, **kwargs):
        text = sanitize_string(response.message.strip())
        self.agent.hist_add_tool_result(self.name, text, **(response.additional or {}))
        PrintStyle(
            font_color="#1B4F72", background_color="white", padding=True, bold=True
        ).print(f"{self.agent.agent_name}: Response from tool '{self.name}'")
        PrintStyle(font_color="#85C1E9").print(text)
        self.log.update(content=text)

        # Audit: record tool result
        try:
            from python.helpers.audit_log import log_tool_result

            duration_ms = (time.monotonic() - self._exec_start) * 1000
            log_tool_result(
                tool_name=self.name,
                method=self.method,
                result_summary=text,
                success=not response.break_loop,
                agent_name=self.agent.agent_name,
                context_id=self.agent.context.id,
                duration_ms=duration_ms,
            )
        except Exception:
            pass  # Audit must never break tool execution

    def get_log_object(self):
        if self.method:
            heading = f"icon://construction {self.agent.agent_name}: Using tool '{self.name}:{self.method}'"
        else:
            heading = (
                f"icon://construction {self.agent.agent_name}: Using tool '{self.name}'"
            )
        return self.agent.context.log.log(
            type="tool",
            heading=heading,
            content="",
            kvps=self.args,
            _tool_name=self.name,
        )

    def nice_key(self, key: str):
        words = key.split("_")
        words = [words[0].capitalize()] + [word.lower() for word in words[1:]]
        result = " ".join(words)
        return result
