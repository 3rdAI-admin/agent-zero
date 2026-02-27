# Fix Anthropic Model Configuration

**Date**: 2026-02-26
**Status**: RESOLVED — Option A (code) + Option B (settings) applied
**Assignees**: Claude Code (diagnosis, Option B, verification) + Cursor (Option A in code)

**Resolution**
- **Claude**: Applied Option B — removed `anthropic/` prefix from `tmp/settings.json`. Models confirmed working (chat, utility, browser). Remaining aiohttp event loop warnings are cosmetic.
- **Cursor**: Applied Option A in `models.py` so prefixed names in settings no longer double-prefix:
  - `LiteLLMChatWrapper.__init__`: if `model.startswith(f"{provider}/")` use `model` as-is, else `f"{provider}/{model}"`.
  - `LiteLLMEmbeddingWrapper.__init__`: same logic for embedding model names.
  - Kept `ANTHROPIC_MODEL_REMAP` and date-stamped Sonnet 4 fallback in `_adjust_call_args` for retired/old model IDs.
- **Result**: Both prefixed (`anthropic/claude-...`) and bare (`claude-...`) names in settings now work; container must be rebuilt to pick up `models.py` changes.

## Problem

Agent Zero returns `404 Not Found` for all Anthropic model calls. Two independent issues combine to break it:

### Issue 1: Double-prefixed model name

`models.py:314` in `LiteLLMChatWrapper.__init__` prepends `{provider}/` to the model name:

```python
# models.py line 314
model_value = f"{provider}/{model}"
```

Settings already store model names WITH the provider prefix (e.g. `anthropic/claude-sonnet-4-20250514`), so litellm receives `anthropic/anthropic/claude-sonnet-4-20250514` — which 404s.

**Evidence** from container logs:
```
AnthropicException - {"type":"error","error":{"type":"not_found_error",
"message":"model: anthropic/claude-sonnet-4-20250514"}}
```

The Anthropic API expects just `claude-sonnet-4-20250514` (no prefix). Litellm normally strips `anthropic/` when it appears once, but the double-prefix breaks this.

### Issue 2: Retired model names

Anthropic retired the Claude 3.5 family on 2026-02-19. The previous settings used:
- `anthropic/claude-3-5-sonnet-latest` (chat + browser) — **retired, 404**
- `anthropic/claude-3-5-haiku-latest` (utility) — **retired, 404**

Settings have been updated to use current models but the double-prefix bug still prevents them from working.

### Issue 3: Container runs stale code

The `ANTHROPIC_MODEL_REMAP` and prefix-stripping logic added to the host `models.py` is NOT present in the running container. The container was built from the Docker image and does not mount `models.py` — only `tmp/settings.json` is mounted.

## Root Cause Chain

```
settings.json has: "chat_model_name": "anthropic/claude-sonnet-4-20250514"
                                       ^^^^^^^^^^-- provider prefix already here

models.py:314:  model_value = f"{provider}/{model}"
                              = "anthropic/anthropic/claude-sonnet-4-20250514"
                                           ^^^^^^^^^^-- doubled!

litellm strips ONE "anthropic/" prefix → sends "anthropic/claude-sonnet-4-20250514" to API
Anthropic API expects "claude-sonnet-4-20250514" → 404 Not Found
```

## Fix Options

### Option A: Strip prefix in LiteLLMChatWrapper (recommended)

In `models.py:314`, avoid double-prefixing:

```python
# Before (line 314):
model_value = f"{provider}/{model}"

# After:
if model.startswith(f"{provider}/"):
    model_value = model  # already prefixed
else:
    model_value = f"{provider}/{model}"
```

This is the safest fix — it handles both prefixed and non-prefixed model names in settings.

### Option B: Remove prefix from settings

Change `tmp/settings.json` model names to bare names:
- `"chat_model_name": "claude-sonnet-4-20250514"` (no `anthropic/` prefix)
- `"util_model_name": "claude-haiku-4-5-20251001"` (no `anthropic/` prefix)
- `"browser_model_name": "claude-sonnet-4-20250514"` (no `anthropic/` prefix)

This works but is fragile — the Web UI settings page may re-add the prefix.

### Option C: Both A + B

Apply Option A for robustness, then also fix settings. Belt and suspenders.

## Current Model Names (valid as of 2026-02-26)

| Role | Retired Name | Current Name |
|------|-------------|-------------|
| Chat | `claude-3-5-sonnet-latest` | `claude-sonnet-4-20250514` |
| Utility | `claude-3-5-haiku-latest` | `claude-haiku-4-5-20251001` |
| Browser | `claude-3-5-sonnet-latest` | `claude-sonnet-4-20250514` |

Verified working inside container via direct litellm call:
```python
litellm.completion(model='anthropic/claude-sonnet-4-20250514', ...)  # OK
litellm.completion(model='anthropic/claude-haiku-4-5-20251001', ...)  # OK
```

## Verification Steps

After applying the fix:

1. **Rebuild container** (required so `/a0` in the image gets repo code; Dockerfile now has `RUN mkdir -p /a0 && cp -rn /git/agent-zero/. /a0/`): `docker compose build agent-zero && docker compose up -d`
2. **Check logs**: `docker logs agent-zero --tail 50 2>&1 | grep -i error`
3. **Test from container**:
   ```bash
   docker exec agent-zero /opt/venv-a0/bin/python3 -c "
   import os; os.environ['LITELLM_LOG']='ERROR'
   from dotenv import load_dotenv; load_dotenv('/a0/.env')
   import litellm; litellm.suppress_debug_info=True
   r = litellm.completion(model='anthropic/claude-sonnet-4-20250514',
       messages=[{'role':'user','content':'Say hello'}], max_tokens=10,
       api_key=os.getenv('API_KEY_ANTHROPIC'))
   print('OK:', r.choices[0].message.content)
   "
   ```
4. **Send a message via the Web UI** at http://localhost:8888

## Files to Modify

| File | Line | Change |
|------|------|--------|
| `models.py` | 314 | Fix double-prefix (Option A) |
| `tmp/settings.json` | 4, 16, 33 | Model names already updated |

## Context

- Container: `agent-zero` (healthy, running)
- litellm version: `1.79.3`
- API key: `API_KEY_ANTHROPIC` in `.env` (valid, tested)
- Provider config: `conf/model_providers.yaml` maps `anthropic` → `litellm_provider: anthropic`

---

## Collaboration handoff (Cursor ↔ Claude)

**For Claude:** Cursor has applied Option A in `models.py` (see Resolution above). The host repo has the fix; the running container will not until the image is rebuilt. If the user still sees 404s after changing settings, suggest: `docker compose build && docker compose up -d` from the AgentZ repo root, then re-run the Verification Steps above.

**For Cursor:** Claude applied Option B (bare model names in `tmp/settings.json`) and confirmed models work. The Web UI may persist prefixed names again; Option A in code ensures both prefixed and bare names work so no need to re-edit settings unless desired.

**If 404s return:** Check (1) `tmp/settings.json` model names and (2) that the container was rebuilt after the `models.py` double-prefix fix. Use the inline litellm test in Verification Steps to confirm the API key and model ID from inside the container.
