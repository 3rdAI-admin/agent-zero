"""Tests for Ollama preset kwargs (anti-repetition, context length, parameter mapping)."""
from __future__ import annotations

import sys
import os

import pytest

# Ensure repo root is on path so we can import the presets module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.switch_model_preset import (
    PRESETS,
    _OLLAMA_CHAT_KWARGS,
    _OLLAMA_BROWSER_KWARGS,
    _OLLAMA_UTIL_KWARGS,
)

OLLAMA_PRESETS = [
    "ollama",
    "ollama_dual",
    "ollama_glm",
    "ollama_qwen3",
    "ollama_mixed",
    "ollama_claude",
    "ollama_glm_claude",
]

NON_OLLAMA_PRESETS = ["anthropic", "venice", "agent_zero"]

REQUIRED_CHAT_KEYS = {"temperature", "frequency_penalty", "max_tokens"}
REQUIRED_UTIL_KEYS = {"temperature", "frequency_penalty", "max_tokens"}
REQUIRED_BROWSER_KEYS = {"temperature", "frequency_penalty", "max_tokens"}


class TestOllamaPresetsHaveKwargs:
    """All Ollama presets must include anti-repetition kwargs."""

    @pytest.mark.parametrize("preset_name", OLLAMA_PRESETS)
    def test_chat_kwargs_present(self, preset_name: str) -> None:
        preset = PRESETS[preset_name]
        kwargs = preset.get("chat_model_kwargs", {})
        missing = REQUIRED_CHAT_KEYS - set(kwargs.keys())
        assert not missing, f"{preset_name} chat_model_kwargs missing: {missing}"

    @pytest.mark.parametrize("preset_name", OLLAMA_PRESETS)
    def test_util_kwargs_present(self, preset_name: str) -> None:
        preset = PRESETS[preset_name]
        kwargs = preset.get("util_model_kwargs", {})
        missing = REQUIRED_UTIL_KEYS - set(kwargs.keys())
        assert not missing, f"{preset_name} util_model_kwargs missing: {missing}"

    @pytest.mark.parametrize("preset_name", OLLAMA_PRESETS)
    def test_browser_kwargs_present(self, preset_name: str) -> None:
        preset = PRESETS[preset_name]
        kwargs = preset.get("browser_model_kwargs", {})
        missing = REQUIRED_BROWSER_KEYS - set(kwargs.keys())
        assert not missing, f"{preset_name} browser_model_kwargs missing: {missing}"


class TestNonOllamaPresetsUntouched:
    """Non-Ollama presets should not have Ollama-specific kwargs injected."""

    @pytest.mark.parametrize("preset_name", NON_OLLAMA_PRESETS)
    def test_no_ollama_chat_kwargs(self, preset_name: str) -> None:
        preset = PRESETS[preset_name]
        kwargs = preset.get("chat_model_kwargs", {})
        # frequency_penalty is Ollama-specific; should not appear in cloud presets
        assert "frequency_penalty" not in kwargs, (
            f"{preset_name} should not have frequency_penalty in chat_model_kwargs"
        )


class TestContextLengths:
    """All Ollama presets should have chat_model_ctx_length of 32000."""

    @pytest.mark.parametrize("preset_name", OLLAMA_PRESETS)
    def test_chat_ctx_length(self, preset_name: str) -> None:
        preset = PRESETS[preset_name]
        ctx = preset.get("chat_model_ctx_length")
        assert ctx == 32000, (
            f"{preset_name} chat_model_ctx_length should be 32000, got {ctx}"
        )


class TestKwargsValues:
    """Verify specific parameter values are within expected ranges."""

    def test_chat_temperature_above_zero(self) -> None:
        assert _OLLAMA_CHAT_KWARGS["temperature"] > 0.1, (
            "Chat temperature should be > 0.1 to avoid repetition loops"
        )

    def test_chat_frequency_penalty_strong(self) -> None:
        assert _OLLAMA_CHAT_KWARGS["frequency_penalty"] >= 1.2, (
            "Chat frequency_penalty should be >= 1.2 for effective repeat prevention"
        )

    def test_chat_max_tokens_capped(self) -> None:
        assert 1024 <= _OLLAMA_CHAT_KWARGS["max_tokens"] <= 8192, (
            "Chat max_tokens should be between 1024 and 8192"
        )

    def test_util_max_tokens_smaller_than_chat(self) -> None:
        assert _OLLAMA_UTIL_KWARGS["max_tokens"] <= _OLLAMA_CHAT_KWARGS["max_tokens"], (
            "Utility max_tokens should be <= chat max_tokens"
        )

    def test_deepseek_has_ollama_kwargs_for_util_browser(self) -> None:
        ds = PRESETS["deepseek"]
        assert "util_model_kwargs" in ds, "deepseek should have util_model_kwargs"
        assert "browser_model_kwargs" in ds, "deepseek should have browser_model_kwargs"
        assert "chat_model_kwargs" not in ds, (
            "deepseek should NOT have chat_model_kwargs (chat uses DeepSeek API)"
        )
