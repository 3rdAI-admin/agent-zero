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

# Shared Ollama kwargs for each model role.
# Uses OpenAI-compatible param names that LiteLLM maps to Ollama equivalents:
#   temperature       -> temperature       (direct)
#   top_p             -> top_p             (direct)
#   frequency_penalty -> repeat_penalty    (mapped by OllamaChatConfig.map_openai_params)
#   max_tokens        -> num_predict       (mapped by OllamaChatConfig.map_openai_params)
#   num_ctx           -> num_ctx           (Ollama-native, passed through by LiteLLM)
#
# num_ctx controls the KV-cache context window. Ollama defaults can be huge (e.g. 202K
# for glm-4.7-flash) which consumes massive VRAM and causes stalls. Always set explicitly.
# Recommendations by model param count:
#   <= 3B  -> 4096    (~0.5 GB KV overhead)
#   4-8B   -> 8192    (~1 GB)
#   9-30B  -> 16384   (~2-8 GB)
#   > 30B  -> 8192    (conserve VRAM for weights)
_OLLAMA_CHAT_KWARGS: dict = {
    "temperature": 0.4,          # Up from 0.1; reduces deterministic repetition loops
    "frequency_penalty": 1.3,    # -> repeat_penalty 1.3; penalize repeated tokens
    "max_tokens": 4096,          # -> num_predict 4096; cap output per response
    "top_p": 0.9,                # Nucleus sampling for diversity
}
_OLLAMA_BROWSER_KWARGS: dict = {
    "temperature": 0.2,          # Lower for structured browser extraction
    "frequency_penalty": 1.3,    # -> repeat_penalty 1.3
    "max_tokens": 4096,          # -> num_predict 4096
}
_OLLAMA_UTIL_KWARGS: dict = {
    "temperature": 0.2,          # Low for deterministic utility tasks
    "frequency_penalty": 1.2,    # -> repeat_penalty 1.2; lighter for utility
    "max_tokens": 2048,          # -> num_predict 2048; utility responses shorter
}

# num_ctx values by model size tier
_CTX_SMALL = 4096    # <= 3B params (gemma3:1b)
_CTX_MEDIUM = 8192   # 4-8B params (qwen2.5:latest, qwen3:latest)
_CTX_LARGE = 16384   # 9-30B params (qwen3-14b, gpt-oss:20b, devstral, glm-4.7-flash, qwen3-coder)

# Presets: provider, model name, api_base (empty = use provider default from model_providers.yaml)
PRESETS = {
    "google": {
        "chat_model_provider": "google",
        "chat_model_name": "gemini-2.5-flash",
        "chat_model_api_base": "",
        "chat_model_ctx_length": 1000000,
        "util_model_provider": "google",
        "util_model_name": "gemini-2.5-flash",
        "util_model_api_base": "",
        "util_model_ctx_length": 1000000,
        "util_model_kwargs": {"temperature": 0.2},
        "browser_model_provider": "google",
        "browser_model_name": "gemini-2.5-flash",
        "browser_model_api_base": "",
    },
    "google_pro": {
        "chat_model_provider": "google",
        "chat_model_name": "gemini-2.5-pro",
        "chat_model_api_base": "",
        "chat_model_ctx_length": 1000000,
        "util_model_provider": "google",
        "util_model_name": "gemini-2.5-flash",
        "util_model_api_base": "",
        "util_model_ctx_length": 1000000,
        "util_model_kwargs": {"temperature": 0.2},
        "browser_model_provider": "google",
        "browser_model_name": "gemini-2.5-flash",
        "browser_model_api_base": "",
    },
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
        "chat_model_ctx_length": 128000,
        "util_model_provider": "venice",
        "util_model_name": "qwen3-4b",
        "util_model_api_base": "",
        "util_model_ctx_length": 32000,
        "browser_model_provider": "venice",
        "browser_model_name": "mistral-31-24b",
        "browser_model_api_base": "",
    },
    "agent_zero": {
        "chat_model_provider": "a0_venice",
        "chat_model_name": "mistral-31-24b",
        "chat_model_api_base": "https://llm.agent-zero.ai/v1",
        "chat_model_ctx_length": 128000,
        "util_model_provider": "a0_venice",
        "util_model_name": "qwen3-4b",
        "util_model_api_base": "https://llm.agent-zero.ai/v1",
        "util_model_ctx_length": 32000,
        "util_model_kwargs": {"temperature": 0.2},
        "browser_model_provider": "a0_venice",
        "browser_model_name": "mistral-31-24b",
        "browser_model_api_base": "https://llm.agent-zero.ai/v1",
    },
    "deepseek": {
        "chat_model_provider": "deepseek",
        "chat_model_name": "deepseek-chat",
        "chat_model_api_base": "",
        "chat_model_ctx_length": 64000,
        "chat_model_vision": False,
        "util_model_provider": "ollama",
        "util_model_name": "gemma3:1b",
        "util_model_api_base": "http://192.168.50.7:11434",
        "util_model_ctx_length": 32000,
        "util_model_kwargs": {**_OLLAMA_UTIL_KWARGS, "num_ctx": _CTX_SMALL},
        "browser_model_provider": "ollama",
        "browser_model_name": "qwen2.5:latest",
        "browser_model_api_base": "http://192.168.50.7:11434",
        "browser_model_kwargs": {**_OLLAMA_BROWSER_KWARGS, "num_ctx": _CTX_MEDIUM},
    },
    "ollama": {
        "chat_model_provider": "ollama",
        "chat_model_name": "qwen2.5:latest",
        "chat_model_api_base": "http://192.168.50.7:11434",
        "chat_model_ctx_length": 32000,
        "chat_model_kwargs": {**_OLLAMA_CHAT_KWARGS, "num_ctx": _CTX_MEDIUM},
        "util_model_provider": "ollama",
        "util_model_name": "gemma3:1b",
        "util_model_api_base": "http://192.168.50.7:11434",
        "util_model_ctx_length": 32000,
        "util_model_kwargs": {**_OLLAMA_UTIL_KWARGS, "num_ctx": _CTX_SMALL},
        "browser_model_provider": "ollama",
        "browser_model_name": "qwen2.5:latest",
        "browser_model_api_base": "http://192.168.50.7:11434",
        "browser_model_kwargs": {**_OLLAMA_BROWSER_KWARGS, "num_ctx": _CTX_MEDIUM},
    },
    "ollama_dual": {
        # .7 = local, .10 = remote: chat/browser on local (low latency), utility on remote (offload background work)
        "chat_model_provider": "ollama",
        "chat_model_name": "qwen2.5:latest",
        "chat_model_api_base": "http://192.168.50.7:11434",
        "chat_model_ctx_length": 32000,
        "chat_model_kwargs": {**_OLLAMA_CHAT_KWARGS, "num_ctx": _CTX_MEDIUM},
        "util_model_provider": "ollama",
        "util_model_name": "gemma3:1b",
        "util_model_api_base": "http://192.168.50.10:11434",
        "util_model_ctx_length": 32000,
        "util_model_kwargs": {**_OLLAMA_UTIL_KWARGS, "num_ctx": _CTX_SMALL},
        "browser_model_provider": "ollama",
        "browser_model_name": "qwen2.5:latest",
        "browser_model_api_base": "http://192.168.50.7:11434",
        "browser_model_kwargs": {**_OLLAMA_BROWSER_KWARGS, "num_ctx": _CTX_MEDIUM},
    },
    "ollama_glm": {
        # GLM-4.7-Flash 30B MoE (~3B active). Use :32k for VRAM savings (run scripts/ollama_create_modelfiles.sh on Ollama server first).
        "chat_model_provider": "ollama",
        "chat_model_name": "glm-4.7-flash:32k",
        "chat_model_api_base": "http://192.168.50.7:11434",
        "chat_model_ctx_length": 32000,
        "chat_model_kwargs": {**_OLLAMA_CHAT_KWARGS, "frequency_penalty": 1.45, "num_ctx": _CTX_LARGE},
        "util_model_provider": "ollama",
        "util_model_name": "gpt-oss:20b",
        "util_model_api_base": "http://192.168.50.7:11434",
        "util_model_ctx_length": 32000,
        "util_model_kwargs": {**_OLLAMA_UTIL_KWARGS, "num_ctx": _CTX_LARGE},
        "browser_model_provider": "ollama",
        "browser_model_name": "glm-4.7-flash:32k",
        "browser_model_api_base": "http://192.168.50.7:11434",
        "browser_model_kwargs": {**_OLLAMA_BROWSER_KWARGS, "frequency_penalty": 1.45, "num_ctx": _CTX_LARGE},
    },
    "ollama_qwen3": {
        # Qwen3-Coder 30B MoE: agentic-trained; slightly higher temp for diversity
        # Requires: ollama pull qwen3-coder:30b
        "chat_model_provider": "ollama",
        "chat_model_name": "qwen3-coder:30b",
        "chat_model_api_base": "http://192.168.50.7:11434",
        "chat_model_ctx_length": 32000,
        "chat_model_kwargs": {**_OLLAMA_CHAT_KWARGS, "temperature": 0.3, "num_ctx": _CTX_LARGE},
        "util_model_provider": "ollama",
        "util_model_name": "qwen2.5:latest",
        "util_model_api_base": "http://192.168.50.7:11434",
        "util_model_ctx_length": 32000,
        "util_model_kwargs": {**_OLLAMA_UTIL_KWARGS, "num_ctx": _CTX_MEDIUM},
        "browser_model_provider": "ollama",
        "browser_model_name": "qwen3-coder:30b",
        "browser_model_api_base": "http://192.168.50.7:11434",
        "browser_model_kwargs": {**_OLLAMA_BROWSER_KWARGS, "num_ctx": _CTX_LARGE},
    },
    "ollama_mixed": {
        # Best-of-breed: GLM chat (reasoning), Devstral browser (384K ctx, vision), GPT-OSS utility (fast)
        # Requires: ollama pull devstral-small-2; GLM :32k via scripts/ollama_create_modelfiles.sh
        "chat_model_provider": "ollama",
        "chat_model_name": "glm-4.7-flash:32k",
        "chat_model_api_base": "http://192.168.50.7:11434",
        "chat_model_ctx_length": 32000,
        "chat_model_kwargs": {**_OLLAMA_CHAT_KWARGS, "frequency_penalty": 1.45, "num_ctx": _CTX_LARGE},
        "util_model_provider": "ollama",
        "util_model_name": "gpt-oss:20b",
        "util_model_api_base": "http://192.168.50.7:11434",
        "util_model_ctx_length": 32000,
        "util_model_kwargs": {**_OLLAMA_UTIL_KWARGS, "num_ctx": _CTX_LARGE},
        "browser_model_provider": "ollama",
        "browser_model_name": "devstral-small-2",
        "browser_model_api_base": "http://192.168.50.7:11434",
        "browser_model_kwargs": {**_OLLAMA_BROWSER_KWARGS, "num_ctx": _CTX_LARGE},
    },
    "ollama_baz": {
        # Claude Opus 4.5 distilled into Qwen3-14B (TeichAI): dense model, all roles
        # Requires: ollama pull bazobehram/qwen3-14b-claude-4.5-opus-high-reasoning
        "chat_model_provider": "ollama",
        "chat_model_name": "bazobehram/qwen3-14b-claude-4.5-opus-high-reasoning",
        "chat_model_api_base": "http://192.168.50.7:11434",
        "chat_model_ctx_length": 32000,
        "chat_model_kwargs": {**_OLLAMA_CHAT_KWARGS, "num_ctx": _CTX_LARGE},
        "util_model_provider": "ollama",
        "util_model_name": "bazobehram/qwen3-14b-claude-4.5-opus-high-reasoning",
        "util_model_api_base": "http://192.168.50.7:11434",
        "util_model_ctx_length": 32000,
        "util_model_kwargs": {**_OLLAMA_UTIL_KWARGS, "num_ctx": _CTX_LARGE},
        "browser_model_provider": "ollama",
        "browser_model_name": "bazobehram/qwen3-14b-claude-4.5-opus-high-reasoning",
        "browser_model_api_base": "http://192.168.50.7:11434",
        "browser_model_kwargs": {**_OLLAMA_BROWSER_KWARGS, "num_ctx": _CTX_LARGE},
    },
    "ollama_glm_claude": {
        # Hybrid: GLM-4.7-Flash chat/browser + Claude-distilled utility. GLM :32k via scripts/ollama_create_modelfiles.sh
        "chat_model_provider": "ollama",
        "chat_model_name": "glm-4.7-flash:32k",
        "chat_model_api_base": "http://192.168.50.7:11434",
        "chat_model_ctx_length": 32000,
        "chat_model_kwargs": {**_OLLAMA_CHAT_KWARGS, "frequency_penalty": 1.45, "num_ctx": _CTX_LARGE},
        "util_model_provider": "ollama",
        "util_model_name": "bazobehram/qwen3-14b-claude-4.5-opus-high-reasoning",
        "util_model_api_base": "http://192.168.50.7:11434",
        "util_model_ctx_length": 32000,
        "util_model_kwargs": {**_OLLAMA_UTIL_KWARGS, "frequency_penalty": 1.1, "num_ctx": _CTX_LARGE},
        "browser_model_provider": "ollama",
        "browser_model_name": "glm-4.7-flash:32k",
        "browser_model_api_base": "http://192.168.50.7:11434",
        "browser_model_kwargs": {**_OLLAMA_BROWSER_KWARGS, "frequency_penalty": 1.45, "num_ctx": _CTX_LARGE},
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
    # Normalize hyphenated preset names to underscore keys
    preset_name = raw.replace("-", "_")
    if len(sys.argv) < 2 or preset_name not in PRESETS:
        print(
            "Usage: switch_model_preset.py <preset> [--test-llm]  (presets: anthropic venice agent-zero deepseek ollama ollama-dual ollama-glm ollama-qwen3 ollama-mixed ollama-baz ollama-glm-claude)",
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

    # Verify: confirm the file we wrote has the preset (this is the source of truth when A0_USR_PATH is set)
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
        else:
            verify_ok = True
            print("Verification: settings file matches preset.")
        # When A0_USR_PATH is set we wrote to the volume; app's settings module reads repo path, so skip that check
        if not os.environ.get("A0_USR_PATH"):
            from python.helpers import settings as settings_helper
            settings_helper.reload_settings()
            s = settings_helper.get_settings()
            errors = []
            for key, expected in preset.items():
                actual = s.get(key)
                if actual != expected:
                    errors.append(f"  {key}: expected {expected!r}, got {actual!r}")
            if errors:
                print("Load check (repo path): mismatch —", errors[0] if errors else "")
            elif not disk_ok:
                pass
            else:
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
