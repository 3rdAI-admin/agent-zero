# RESPONSES.md – Claude ↔ Cursor handoff

Use this file to coordinate between **Claude** (e.g. Claude Code / API) and **Cursor** so both have a single source of truth for decisions, done work, and next steps.

---

## Purpose

- **Claude** can write: decisions, user requests, suggested remediations, or “Cursor: please do X.”
- **Cursor** can write: what was implemented, verification results, or “done / blocked / needs input.”
- **Either** can append to **Remediations** and **Status** so the other knows what’s in progress or complete.

---

## Current focus: Docker response-speed improvements

**Goal:** Improve Agent Zero container response speeds and predictability.

---

## Decisions (agreed)

| Decision | Notes |
|----------|--------|
| Add `shm_size: '512mb'` | Larger `/dev/shm` for Chromium/Playwright; improves browser responsiveness. |
| Cap swap so container doesn’t use extra swap | Set total memory+swap = memory limit for predictable latency under memory pressure. |
| Use service-level `memswap_limit` | Compose does not support `memory_swap` under `deploy.resources.limits`; use `memswap_limit` at service level. |
| Do **not** add Uvicorn workers for now | Single worker is fine for this ASGI/WebSocket stack; workers would require shared-state handling. |

---

## Implemented (Cursor)

| Item | Status | File(s) |
|------|--------|--------|
| `shm_size: '512mb'` | Done | `docker-compose.yml` |
| `memswap_limit: 16g` (service level) | Done | `docker-compose.yml` |
| Container recreated with new settings | Done | `docker compose up -d --force-recreate agent-zero` |
| ~~`memory_swap` under deploy.resources.limits~~ | Reverted (not allowed by Compose) | — |
| Raise reservations to 10G RAM, 3 CPUs | Done | `docker-compose.yml` |
| Shorten healthcheck `start_period` to 30s | Done | `docker-compose.yml` |

---

## Remediations / next steps

- [x] **Optional:** If the host has free resources, consider raising CPU/memory **reservations** (e.g. 10G RAM, 3 CPUs) for more consistent latency. *(Done: 10G, 3 CPUs.)*
- [ ] **Optional (Linux):** For I/O-heavy dirs (`memory`, `knowledge`, `logs`, `tmp`), consider named volumes instead of bind mounts if disk-bound slowdowns appear.
- [x] **Optional:** Shorten healthcheck `start_period` if the app is usually ready in 20–30s (cosmetic; doesn’t change app speed). *(Done: 30s.)*

*Add or check off items above as Claude or Cursor complete them.*

---

## For Claude

- Add any new user requests or decisions in **Decisions** or **Remediations**.
- If you want Cursor to do something specific, add a line under **Remediations** or a short “**Cursor:** …” section below.

---

## For Cursor

- When you implement something from **Remediations**, move it to **Implemented** and note the file(s).
- If something is blocked or needs user/Claude input, add a “**Blocked / needs input:**” line and what’s needed.

---

## Blocked / needs input

*(None at this time.)*

---
---

# Ollama Preset Speed & Repetition Fix

> **Status:** Cursor follow-up tasks complete (Modelfile script, loop detection, per-preset kwargs, validation).
> **Date:** 2026-03-03
> **Active Preset:** `ollama-glm-claude`

---

## Problem

GLM-4.7-Flash on the `ollama-glm-claude` preset was stuck in a **repetition loop** — its reasoning stream repeated the same ~30-line block endlessly without producing a JSON tool call. This wasted tokens, time, and made Agent Zero unresponsive.

### Root Causes

1. **Temperature 0.1** — too deterministic, causes loops in MoE models
2. **No repeat penalty** — Ollama default 1.1 is too weak for GLM's MoE architecture
3. **No max_tokens cap** — model generates indefinitely during loops
4. **128K context length** — wasteful for local inference (GLM allocates 202K tokens of VRAM)
5. **Agent Zero's loop detection** (`agent.py:479`) only compares full responses across turns, not within a single generation

### Evidence from Logs

```
*Actually, I can try to use `document_query` on the URL...*
*Let's use the browser agent.*
*After download, I will use `code_execution_tool`...*
*The script needs to: 1. Read... 2. Create a VC One-Pager... 3. Send via Gmail API.*
*Let's start.*
*Wait, I need to check the file structure again...*
[loops back to start — repeats 4+ times]
```

---

## Critical Discovery: LiteLLM Parameter Mapping

LiteLLM **silently drops** Ollama-native params (`repeat_penalty`, `num_predict`, `num_ctx`). Must use **OpenAI-compatible names**:

| Use this (OpenAI kwarg) | Maps to (Ollama param) | Notes |
|---|---|---|
| `frequency_penalty` | `repeat_penalty` | Direct value pass-through |
| `max_tokens` | `num_predict` | Direct value pass-through |
| `temperature` | `temperature` | Direct |
| `top_p` | `top_p` | Direct |

**`num_ctx` has NO OpenAI equivalent** — cannot be set via kwargs. Must use Ollama Modelfile.

Mapping source: `.venv/.../litellm/llms/ollama/chat/transformation.py:152` (`OllamaChatConfig.map_openai_params`)

---

## Decisions (agreed)

| Decision | Notes |
|----------|--------|
| Use shared kwargs dicts for all Ollama presets | `_OLLAMA_CHAT_KWARGS`, `_OLLAMA_BROWSER_KWARGS`, `_OLLAMA_UTIL_KWARGS` in `switch_model_preset.py` |
| Use OpenAI-compat param names | `frequency_penalty` -> `repeat_penalty`, `max_tokens` -> `num_predict` (LiteLLM maps them) |
| Reduce `chat_model_ctx_length` to 32000 | From 128K; 32K * 0.7 history ratio = 22.4K tokens (~8-10 turns) |
| Chat temperature 0.4, browser/util 0.2 | Balance diversity vs consistency |
| `frequency_penalty` 1.3 chat/browser, 1.2 utility | Stronger penalty for chat where loops occur |
| `max_tokens` 4096 chat/browser, 2048 utility | Cap runaway generation |

---

## Implemented (Claude Code)

| Item | Status | File(s) |
|------|--------|--------|
| Shared Ollama kwargs dicts | Done | `scripts/switch_model_preset.py` |
| Applied kwargs to all 7 Ollama presets | Done | `scripts/switch_model_preset.py` |
| Applied kwargs to deepseek util/browser | Done | `scripts/switch_model_preset.py` |
| Reduced chat_model_ctx_length 128K -> 32K | Done | `scripts/switch_model_preset.py` |
| Updated MODELS.sh help text | Done | `MODELS.sh` |
| Preset validation tests | Done | `tests/test_ollama_preset_kwargs.py` |
| Applied preset and restarted Agent Zero | Done | `A0_volume/settings.json`, `docker compose down && up` |

---

## Follow-Up Tasks for Cursor

### Task 1: Ollama Modelfile for `num_ctx` (VRAM optimization) ✅ DONE (Cursor)

Since `num_ctx` can't be set via LiteLLM kwargs, create Modelfiles to constrain VRAM allocation:

```bash
# On the Ollama server (192.168.50.7):
cat > /tmp/Modelfile.glm32k << 'EOF'
FROM glm-4.7-flash:latest
PARAMETER num_ctx 32768
EOF
ollama create glm-4.7-flash:32k -f /tmp/Modelfile.glm32k

# Then update presets to use glm-4.7-flash:32k instead of glm-4.7-flash:latest
```

This would reduce GLM's VRAM from ~40GB to ~20GB.

**Files:** `scripts/switch_model_preset.py` (presets now use `glm-4.7-flash:32k`), `scripts/ollama_create_modelfiles.sh` (generates Modelfile + instructions; run on Ollama server).

### Task 2: Enhanced loop detection in `agent.py` ✅ DONE (Cursor)

Current detection (`agent.py:479-490`) only catches exact duplicate responses across turns. Could add:

- **Within-generation repetition detection**: Monitor streaming output for repeated blocks
- **Max iteration guard**: Cap monologue loop iterations (currently unbounded)
- Location: `agent.py` lines 389-539, the `monologue()` method

**Files:** `agent.py` — added `LoopData.MAX_ITERATIONS = 20`, max-iteration guard at message loop start, `stream_repeat_detected` in LoopData; within-stream repetition check in `stream_callback` (250-char block repeated 3×); after `call_chat_model`, if `stream_repeat_detected` treat like repeat (warning + stop).

### Task 3: Tune kwargs per model ✅ DONE (Cursor)

The shared kwargs are a baseline. Each model may benefit from tuning:

- GLM-4.7-Flash: May need higher `frequency_penalty` (1.4-1.5) if loops persist
- bazobehram/qwen3-14b: Dense model, may tolerate lower `frequency_penalty` (1.1)
- qwen3-coder:30b: Agentic-trained, may work better with `temperature` 0.3

**Done:** GLM presets use `frequency_penalty` 1.45 (chat/browser); ollama_claude util/browser use 1.1; ollama_qwen3 chat uses `temperature` 0.3.

### Task 4: Monitor and validate after restart ✅ DONE (Cursor)

After restart, check logs for:
- GLM producing JSON tool calls within ~4K tokens (no repetition)
- Response times (should be faster with 32K ctx vs 128K)
- Utility model (bazobehram) working correctly with `frequency_penalty` 1.2

```bash
docker logs agent-zero --tail 100 2>&1 | sed 's/\x1b\[[0-9;]*m//g'
```
Ran 2026-03-03: server up, health 200, MCP in use; no GLM repetition in sampled tail.

---

## Architecture Reference

### Kwargs flow

```
switch_model_preset.py PRESETS dict
    -> settings.json (chat_model_kwargs, util_model_kwargs, browser_model_kwargs)
    -> python/helpers/settings.py get_settings()
    -> initialize.py _normalize_model_kwargs() -> ModelConfig(kwargs=...)
    -> models.py ModelConfig.build_kwargs()
    -> litellm.acompletion(**call_kwargs)
    -> OllamaChatConfig.map_openai_params()
    -> Ollama /api/chat (repeat_penalty, num_predict, temperature, top_p)
```

### Key files

| File | Purpose |
|---|---|
| `scripts/switch_model_preset.py` | Preset definitions (MODIFIED) |
| `MODELS.sh` | Shell wrapper (MODIFIED) |
| `models.py` | LiteLLM integration, ModelConfig.build_kwargs() |
| `initialize.py` | Config init, _normalize_model_kwargs() |
| `agent.py:479-490` | Loop detection (basic exact-match) |
| `python/helpers/settings.py` | Settings schema |
| `conf/model_providers.yaml` | Provider config (Ollama has no special kwargs) |

### Current server state

- **Ollama server:** 192.168.50.7:11434
- **Models loaded:** GLM-4.7-Flash (40.4GB VRAM, ctx=202752), bazobehram (15.9GB VRAM, ctx=40960)
- **Total VRAM:** 56.3GB

---
---

# Infrastructure Fixes (from IMPROVE.md monitoring)

> **Status:** See **IMPROVE.md** → "Task ownership & status" for current owner and status of each item.
> **Date:** 2026-03-03
> **Reference:** See `IMPROVE.md` for full issue descriptions and priority order.

---

## Done (Claude Code)

| Item | Status | Details |
|------|--------|---------|
| ipython (#0) | Done | Installed in container + added to Dockerfile — `code_execution_tool` python runtime works |
| Playwright browser persistence | Done | Volume mount + Dockerfile step — browsers survive container recreates |
| Google API knowledge file | Done | `knowledge/main/google_apis.md` — agent no longer needs to re-discover/recreate Google scripts |

---

## Done (Background agents)

| Item | Status | Details |
|------|--------|---------|
| xvfb crash loop (#10) | Done | `start_xvfb.sh` wrapper removes stale locks; supervisor configs: `startsecs`, `startretries`, removed `-fork`; event listener: non-essential FATAL only warns, doesn't kill container |
| Archon MCP timeout (#1) | Done | 3 root causes: protocol mismatch (SSE→StreamableHTTP), Docker network isolation, dead `archon-local`. Fixed `.mcp.json` (Docker DNS, correct type, timeouts), `docker-compose.yml` (archon network), `mcp_handler.py` (transport field support), `settings.py` (init_timeout 10→30s) |

---

## Cursor Tasks (assigned in RESPONSES.md) — completed

### Task 1: Starlette AssertionError in MCP SSE endpoint — Done

On server shutdown, Starlette raises `AssertionError` in the MCP SSE route. **Implemented:** `python/helpers/mcp_server.py` — wrapped `await sse_app(...)` in try/except for `AssertionError`, `ConnectionResetError`, `BrokenPipeError`, and `asyncio.CancelledError`; log and continue so ASGI shutdown is clean.

### Task 2: Health check log noise — Done

Every 30s, Docker's healthcheck generates `GET /health` 200 in the Uvicorn access log. **Implemented:** `run_ui.py` — added `_HealthCheckAccessLogFilter` that suppresses log records for ` /health ` + ` 200 `; filter attached to `uvicorn.access` when access logs are enabled.

### Task 3: Duplicate POST /projects on page load — Done

Two identical `POST /projects` fired on login. **Implemented:** `webui/components/projects/projects-store.js` — `loadProjectsList()` now reuses an in-flight promise (`_loadProjectsListPromise`); concurrent callers get the same request, so only one POST per load.

---

## Blocked / needs input

*(None at this time.)*
