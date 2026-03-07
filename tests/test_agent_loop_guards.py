import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import agent as agent_module


class _DummyPrinter:
    def __init__(self, *args, **kwargs):
        pass

    def print(self, *args, **kwargs):
        pass

    def stream(self, *args, **kwargs):
        pass


def _build_agent():
    test_agent = agent_module.Agent.__new__(agent_module.Agent)
    test_agent.agent_name = "A0"
    test_agent.last_user_message = None
    test_agent.intervention = None
    test_agent.data = {}
    test_agent.context = SimpleNamespace(
        streaming_agent=None,
        task=SimpleNamespace(is_alive=lambda: True),
        log=SimpleNamespace(log=lambda *args, **kwargs: None),
    )
    return test_agent


@pytest.mark.asyncio
async def test_monologue_returns_on_duplicate_response(monkeypatch):
    """Duplicate model output should stop the run immediately."""
    test_agent = _build_agent()
    warnings: list[str] = []
    ai_responses: list[str] = []

    async def fake_call_extensions(*args, **kwargs):
        return None

    async def fake_handle_intervention(*args, **kwargs):
        return None

    async def fake_prepare_prompt(*args, **kwargs):
        test_agent.loop_data.last_response = "same response"
        return []

    async def fake_call_chat_model(*args, **kwargs):
        return "same response", ""

    async def fake_process_tools(*args, **kwargs):
        raise AssertionError("process_tools should not run for duplicate responses")

    def fake_hist_add_ai_response(message: str):
        ai_responses.append(message)
        return None

    def fake_hist_add_warning(message: str):
        warnings.append(message)
        return None

    def fake_read_prompt(file: str, **kwargs):
        assert file == "fw.msg_repeat.md"
        return "repeat warning"

    monkeypatch.setattr(agent_module, "PrintStyle", _DummyPrinter)
    test_agent.call_extensions = fake_call_extensions
    test_agent.handle_intervention = fake_handle_intervention
    test_agent.prepare_prompt = fake_prepare_prompt
    test_agent.call_chat_model = fake_call_chat_model
    test_agent.process_tools = fake_process_tools
    test_agent.hist_add_ai_response = fake_hist_add_ai_response
    test_agent.hist_add_warning = fake_hist_add_warning
    test_agent.read_prompt = fake_read_prompt

    result = await test_agent.monologue()

    assert result == "repeat warning"
    assert ai_responses == ["same response"]
    assert warnings == ["repeat warning"]


@pytest.mark.asyncio
async def test_monologue_returns_when_iteration_limit_exceeded(monkeypatch):
    """The max-iteration guard should terminate the run instead of restarting."""
    test_agent = _build_agent()
    warnings: list[str] = []

    async def fake_call_extensions(*args, **kwargs):
        return None

    async def fake_handle_intervention(*args, **kwargs):
        return None

    monkeypatch.setattr(agent_module, "PrintStyle", _DummyPrinter)
    monkeypatch.setattr(agent_module.LoopData, "MAX_ITERATIONS", -1)
    test_agent.call_extensions = fake_call_extensions
    test_agent.handle_intervention = fake_handle_intervention
    test_agent.hist_add_warning = lambda message: warnings.append(message)

    result = await test_agent.monologue()

    assert "Message loop stopped after -1 iterations." in result
    assert warnings == [result]
