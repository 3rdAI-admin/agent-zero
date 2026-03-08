from unittest.mock import Mock

import preload


def test_resolve_preload_settings_uses_defaults_for_build(monkeypatch):
    default_settings = {"mode": "default"}
    effective_settings = {"mode": "effective"}

    get_default = Mock(return_value=default_settings)
    get_effective = Mock(return_value=effective_settings)

    monkeypatch.setattr(preload.settings, "get_default_settings", get_default)
    monkeypatch.setattr(preload.settings, "get_settings", get_effective)

    result = preload.resolve_preload_settings(defaults_only=True)

    assert result == default_settings
    get_default.assert_called_once_with()
    get_effective.assert_not_called()


def test_resolve_preload_settings_uses_effective_runtime_settings(monkeypatch):
    default_settings = {"mode": "default"}
    effective_settings = {"mode": "effective"}

    get_default = Mock(return_value=default_settings)
    get_effective = Mock(return_value=effective_settings)

    monkeypatch.setattr(preload.settings, "get_default_settings", get_default)
    monkeypatch.setattr(preload.settings, "get_settings", get_effective)

    result = preload.resolve_preload_settings(defaults_only=False)

    assert result == effective_settings
    get_effective.assert_called_once_with()
    get_default.assert_not_called()
