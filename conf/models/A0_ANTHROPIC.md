# Agent Zero – Anthropic configuration snapshot

**Source:** `tmp/settings.json` (and `.env` for API key)  
**Saved:** 2026-02-26  
**Settings version:** v0.9.7-17

---

## Provider

All three LLM roles are set to **Anthropic** (`anthropic`).  
API key is read from `.env`: set **`API_KEY_ANTHROPIC`** (or `ANTHROPIC_API_KEY` where supported).  
Do not commit `.env` or paste API keys into this file.

---

## Chat model (main agent)

| Setting | Value |
|--------|--------|
| `chat_model_provider` | anthropic |
| `chat_model_name` | claude-sonnet-4-20250514 |
| `chat_model_api_base` | https://api.anthropic.com |
| `chat_model_kwargs` | `{"temperature":"0.1"}` |
| `chat_model_ctx_length` | 200000 |
| `chat_model_ctx_history` | 0.77 |
| `chat_model_vision` | true |
| `chat_model_rl_requests` | 0 |
| `chat_model_rl_input` | 0 |
| `chat_model_rl_output` | 0 |

---

## Utility model (framework tasks)

| Setting | Value |
|--------|--------|
| `util_model_provider` | anthropic |
| `util_model_name` | claude-haiku-4-5-20251001 |
| `util_model_api_base` | https://api.anthropic.com |
| `util_model_kwargs` | `{"temperature":"0.2"}` |
| `util_model_ctx_length` | 100000 |
| `util_model_ctx_input` | 0.7 |
| `util_model_rl_requests` | 50 |
| `util_model_rl_input` | 40000 |
| `util_model_rl_output` | 8000 |

---

## Browser model (browser-use)

| Setting | Value |
|--------|--------|
| `browser_model_provider` | anthropic |
| `browser_model_name` | claude-sonnet-4-20250514 |
| `browser_model_api_base` | https://api.anthropic.com |
| `browser_model_kwargs` | `{"temperature":"0.0"}` |
| `browser_model_vision` | true |
| `browser_model_rl_requests` | 0 |
| `browser_model_rl_input` | 0 |
| `browser_model_rl_output` | 0 |

---

## Embedding model (unchanged)

Embedding remains **HuggingFace** (local):

- `embed_model_provider`: huggingface  
- `embed_model_name`: sentence-transformers/all-MiniLM-L6-v2  

---

## Other settings (non-Anthropic)

- **Agent profile:** agent0  
- **Memory:** recall enabled, memorize enabled  
- **API keys in UI:** `api_keys` is `{}` (key from `.env` used)  
- **LiteLLM global:** `litellm_global_kwargs`: `{}`  
- **MCP:** servers configured (archon, crawl4ai-rag); token from UI if set  

---

## Restoring this configuration

1. Set `API_KEY_ANTHROPIC` in `.env`.
2. In the Web UI (**Settings**), set:
   - Chat model: provider **Anthropic**, model **claude-sonnet-4-20250514**, API base **https://api.anthropic.com**, temperature **0.1**.
   - Utility model: provider **Anthropic**, model **claude-haiku-4-5-20251001**, temperature **0.2**.
   - Browser model: provider **Anthropic**, model **claude-sonnet-4-20250514**, temperature **0.0**.
3. Or replace the Anthropic-related keys in `tmp/settings.json` with the values above (no API key values in that file).

Model names use **bare IDs** (no `anthropic/` prefix) so the double-prefix fix in `models.py` works with either prefixed or bare names.
