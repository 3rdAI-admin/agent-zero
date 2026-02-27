#!/usr/bin/env python3
"""
Apply a model preset (anthropic, venice, agent_zero, ollama) to usr/settings.json and optionally verify.
Used by MODELS.sh.

Agent Zero API (agent_zero) preset: a0_venice, https://llm.agent-zero.ai/v1,
  mistral-31-24b (chat/browser), qwen3-4b (utility, temperature 0.2). Key: API_KEY_A0_VENICE.
"""
from __future__ import annotations

import json
import os
import sys

# Presets: provider, model name, api_base (empty = use provider default from model_providers.yaml)
PRESETS = {
    "anthropic": {
        "chat_model_provider": "anthropic",
        "chat_model_name": "claude-sonnet-4-6",
        "chat_model_api_base": "",
        "util_model_provider": "anthropic",
        "util_model_name": "claude-sonnet-4-6",
        "util_model_api_base": "",
        "browser_model_provider": "anthropic",
        "browser_model_name": "claude-sonnet-4-6",
        "browser_model_api_base": "",
    },
    "venice": {
        "chat_model_provider": "venice",
        "chat_model_name": "mistral-31-24b",
        "chat_model_api_base": "",
        "util_model_provider": "venice",
        "util_model_name": "qwen3-4b",
        "util_model_api_base": "",
        "browser_model_provider": "venice",
        "browser_model_name": "mistral-31-24b",
        "browser_model_api_base": "",
    },
    "agent_zero": {
        "chat_model_provider": "a0_venice",
        "chat_model_name": "mistral-31-24b",
        "chat_model_api_base": "https://llm.agent-zero.ai/v1",
        "util_model_provider": "a0_venice",
        "util_model_name": "qwen3-4b",
        "util_model_api_base": "https://llm.agent-zero.ai/v1",
        "util_model_kwargs": {"temperature": 0.2},
        "browser_model_provider": "a0_venice",
        "browser_model_name": "mistral-31-24b",
        "browser_model_api_base": "https://llm.agent-zero.ai/v1",
    },
    "ollama": {
        "chat_model_provider": "ollama",
        "chat_model_name": "qwen2.5:latest",
        "chat_model_api_base": "http://localhost:11434",
        "util_model_provider": "ollama",
        "util_model_name": "qwen2.5:latest",
        "util_model_api_base": "http://localhost:11434",
        "browser_model_provider": "ollama",
        "browser_model_name": "qwen2.5:latest",
        "browser_model_api_base": "http://localhost:11434",
    },
}

# Keys we never write (sensitive; kept from existing file or env)
SENSITIVE_KEYS = {"api_keys", "auth_login", "auth_password", "rfc_password", "root_password"}


def get_settings_path():
    base = os.environ.get("A0_USR_PATH")
    if base:
        return os.path.join(base, "settings.json")
    # Same resolution as python.helpers.files.get_abs_path("usr/settings.json")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    return os.path.join(repo_root, "usr", "settings.json")


def main():
    raw = sys.argv[1].lower() if len(sys.argv) >= 2 else ""
    preset_name = "agent_zero" if raw in ("agent-zero", "agent_zero") else raw
    if len(sys.argv) < 2 or preset_name not in PRESETS:
        print(
            "Usage: switch_model_preset.py <anthropic|venice|agent-zero|ollama> [--test-llm]",
            file=sys.stderr,
        )
        sys.exit(2)
    test_llm = "--test-llm" in sys.argv
    settings_path = get_settings_path()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, repo_root)
    os.chdir(repo_root)

    preset = PRESETS[preset_name]
    existing = {}
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        try:
            from python.helpers import settings as settings_helper
            default = settings_helper.get_default_settings()
            existing = {k: default[k] for k in default}
        except Exception:
            pass
    # Merge: existing first, then preset (preset overwrites model-related keys)
    merged = {**existing, **preset}
    # Remove sensitive so we don't overwrite with empty
    for k in SENSITIVE_KEYS:
        merged.pop(k, None)
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4)
        f.flush()
        os.fsync(f.fileno())
    print(f"Applied preset: {preset_name}")
    print(f"Settings file: {settings_path}")

    # Verify: confirm file on disk has preset, then load via app's settings module
    verify_ok = False
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            on_disk = json.load(f)
        disk_ok = all(on_disk.get(k) == v for k, v in preset.items())
        if not disk_ok:
            print("On-disk check: mismatch")
            for k in preset:
                if on_disk.get(k) != preset[k]:
                    print(f"  {k}: expected {preset[k]!r}, on disk {on_disk.get(k)!r}")
        from python.helpers import settings as settings_helper

        settings_helper.reload_settings()
        s = settings_helper.get_settings()
        errors = []
        for key, expected in preset.items():
            actual = s.get(key)
            if actual != expected:
                errors.append(f"  {key}: expected {expected!r}, got {actual!r}")
        if errors:
            print("Verification issues (values may have been normalized):")
            for e in errors:
                print(e)
        else:
            verify_ok = True
            print("Verification: settings load and match preset.")
    except Exception as e:
        print(f"Verification (load): {e}")

    if test_llm and verify_ok:
        try:
            import asyncio
            from python.helpers import settings as settings_helper
            import models

            s = settings_helper.get_settings()
            chat = models.get_chat_model(
                s["chat_model_provider"],
                s["chat_model_name"],
            )
            async def _one_token():
                out, _ = await chat.unified_call(
                    system_message="You are a test.",
                    user_message="Reply with exactly the word OK and nothing else.",
                )
                return (out or "").strip().upper().startswith("OK") or "ok" in (out or "").lower()

            result = asyncio.run(_one_token())
            if result:
                print("LLM test: success (model responded).")
            else:
                print("LLM test: model responded but content unexpected.")
        except Exception as e:
            print(f"LLM test: {e}")

    # Exit 0 if we applied and wrote; 1 if verification failed (settings still updated)
    sys.exit(0 if verify_ok else 1)


if __name__ == "__main__":
    main()
