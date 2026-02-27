"""Tests for Venice / Agent Zero API auth: get_api_key trimming and fail-fast on missing key."""
from __future__ import annotations

import pytest

from litellm.exceptions import AuthenticationError as LiteLLMAuthError


def test_get_api_key_trims_whitespace(monkeypatch):
    """API key read from env is stripped so paste newlines/spaces don't cause 401."""
    import models
    monkeypatch.setattr(
        "python.helpers.dotenv.get_dotenv_value",
        lambda key, default=None: "  sk-venice-key-12345  \n" if key == "API_KEY_VENICE" else default,
    )
    key = models.get_api_key("venice")
    assert key == "sk-venice-key-12345"


def test_get_api_key_returns_none_string_when_missing(monkeypatch):
    """When no key is set, get_api_key returns 'None' string."""
    import models
    monkeypatch.setattr(
        "python.helpers.dotenv.get_dotenv_value",
        lambda key, default=None: default,
    )
    key = models.get_api_key("venice")
    assert key == "None"


def test_merge_provider_defaults_venice_raises_when_key_missing(monkeypatch):
    """For provider venice, _merge_provider_defaults raises LiteLLMAuthError if no valid key."""
    import models
    monkeypatch.setattr(models, "get_api_key", lambda _: "None")
    with pytest.raises(LiteLLMAuthError) as exc_info:
        models._merge_provider_defaults("chat", "venice", {})
    assert "No valid API key" in str(exc_info.value)
    assert "API_KEY_VENICE" in str(exc_info.value)


def test_merge_provider_defaults_a0_venice_raises_when_key_missing(monkeypatch):
    """For provider a0_venice, _merge_provider_defaults raises LiteLLMAuthError if no valid key."""
    import models
    monkeypatch.setattr(models, "get_api_key", lambda _: "")
    with pytest.raises(LiteLLMAuthError) as exc_info:
        models._merge_provider_defaults("chat", "a0_venice", {})
    assert "No valid API key" in str(exc_info.value)
    assert "API_KEY_A0_VENICE" in str(exc_info.value)


def test_merge_provider_defaults_venice_does_not_raise_when_key_present(monkeypatch):
    """For provider venice, _merge_provider_defaults does not raise when key is set."""
    import models
    monkeypatch.setattr(models, "get_api_key", lambda _: "sk-venice-valid-key-at-least-10-chars")
    provider_name, kwargs = models._merge_provider_defaults("chat", "venice", {})
    assert kwargs.get("api_key") == "sk-venice-valid-key-at-least-10-chars"
    assert provider_name == "openai"


def test_merge_provider_defaults_a0_venice_does_not_raise_when_key_present(monkeypatch):
    """For provider a0_venice, _merge_provider_defaults does not raise when key is set."""
    import models
    monkeypatch.setattr(models, "get_api_key", lambda _: "sk-a0-valid-dashboard-key-here")
    provider_name, kwargs = models._merge_provider_defaults("chat", "a0_venice", {})
    assert kwargs.get("api_key") == "sk-a0-valid-dashboard-key-here"
    assert provider_name == "openai"


def test_merge_provider_defaults_venice_raises_when_key_too_short(monkeypatch):
    """Key with fewer than 10 chars is treated as invalid for Venice."""
    import models
    monkeypatch.setattr(models, "get_api_key", lambda _: "short")
    with pytest.raises(LiteLLMAuthError) as exc_info:
        models._merge_provider_defaults("chat", "venice", {})
    assert "No valid API key" in str(exc_info.value)
