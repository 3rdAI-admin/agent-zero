# Agent Zero – Fallback handoff log

Use this file when Archon is unreachable, timing out, or unavailable before tasks can be created there.

## Purpose

- Preserve work continuity across Cursor, Claude, and other agents
- Capture improvements and incidents locally first
- Provide a handoff artifact that can be synced into Archon later

## How to use

1. Add new items here only when Archon cannot be used reliably.
2. Keep each item atomic, testable, and evidence-based.
3. When Archon returns, create the matching task there and mark the local item as synced.

## Handoff template

```md
### [short-title]
- Status: new | in_progress | blocked | done_local | synced_to_archon
- Date: YYYY-MM-DD HH:MM TZ
- Area: runtime | models | mcp | ui | docs | docker | tests | security
- Summary:
- Trigger:
- Evidence:
  - Logs:
  - Files:
  - Commands:
- Proposed action:
  - Step 1
  - Step 2
- Validation:
  - Expected result 1
  - Expected result 2
- Archon sync:
  - Project:
  - Task ID:
  - Sync status: pending
```

## Current handoff items

### Response tool shape mismatch
- Status: synced_to_archon
- Date: 2026-03-08 13:05 -07:00
- Area: runtime
- Summary: Agent Zero intermittently surfaces `KeyError: 'message'` while finalizing a `response` tool call, even though the current repo and live container file now accept `content`.
- Trigger: user-facing completion after otherwise successful tool or task flow
- Evidence:
  - Logs: traceback references `/a0/python/tools/response.py` and old `text/message`-only behavior
  - Files: `python/tools/response.py`
  - Commands: verified current repo and live container file contents now include `text` / `message` / `content` fallback
- Proposed action:
  - Step 1: confirm whether the traceback is from a stale process, another implementation path, or cached runtime/log surface
  - Step 2: trace which argument shape actually reaches `ResponseTool`
  - Step 3: add or verify regression coverage for `content`-only payloads
- Validation:
  - Expected result 1: no new `KeyError: 'message'` after response tool execution
  - Expected result 2: `response` tool succeeds with `text`, `message`, or `content`
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `2f89d6c9-baee-4277-b55a-2a8fd7d94e70`
  - Assignee: Claude
  - Sync status: synced_to_archon

### Utility model downsizing
- Status: in_progress
- Date: 2026-03-08 13:05 -07:00
- Area: models
- Summary: Utility model was switched from `gpt-oss:20b` to `gemma3:1b` in the volume-backed runtime settings to reduce background latency and memory-consolidation timeouts.
- Trigger: repeated `Memory consolidation timeout for area fragments` and slow utility/background operations
- Evidence:
  - Logs: recurring memory consolidation timeout errors before the switch
  - Files: `/Users/james/Docker/A0_volume/settings.json`
  - Commands: verified live runtime settings after restart
- Proposed action:
  - Step 1: continue monitoring for new timeout events
  - Step 2: compare perceived response time across several user interactions
  - Step 3: determine whether the remaining latency is now dominated by the main chat/browser model
- Validation:
  - Expected result 1: memory-consolidation timeout spam reduces or disappears
  - Expected result 2: no regression in utility tasks like summarization or chat rename
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `654d201c-0ef2-4f55-93e4-e0b1d3cdb0f0`
  - Assignee: Claude
  - Sync status: partially_synced_structural_followup

### Runtime settings source of truth
- Status: synced_to_archon
- Date: 2026-03-08 13:20 -07:00
- Area: runtime
- Summary: Repo files, volume-backed settings, and live container behavior have drifted repeatedly, making performance work hard to trust.
- Trigger: multiple cases where runtime behavior did not match repo code or expected model/MCP settings
- Evidence:
  - Logs: live runtime sometimes reports behavior inconsistent with current repo files
  - Files: `/Users/james/Docker/A0_volume/settings.json`, `usr/settings.json`
  - Commands: repo file inspection versus in-container file inspection
- Proposed action:
  - Step 1: define one effective runtime settings source
  - Step 2: log the active settings path and effective model/MCP config on startup
  - Step 3: warn when repo seed settings and live settings diverge
- Validation:
  - Expected result 1: operators can tell exactly which settings file is active
  - Expected result 2: runtime drift is visible before debugging starts
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `70728303-bac5-41f0-8bfd-751be9f4824e`, `0ff64cff-ba01-4a5b-92c0-3185151477e8`
  - Assignee: Cursor
  - Sync status: synced_to_archon

### MCP tool-surface reduction in live runtime
- Status: synced_to_archon
- Date: 2026-03-08 13:20 -07:00
- Area: mcp
- Summary: The live runtime still reports `google_workspace` with `114 tools`, likely inflating prompts and slowing planning.
- Trigger: startup logs after rebuild and restart
- Evidence:
  - Logs: `MCPClientBase (google_workspace): Tools updated. Found 114 tools.`
  - Files: volume-backed settings and MCP config files
  - Commands: recent `docker logs agent-zero`
- Proposed action:
  - Step 1: verify why `allowed_tools` is not reducing the live tool count
  - Step 2: confirm which config path the live MCP client is actually reading
  - Step 3: reduce tool exposure to the intended working subset
- Validation:
  - Expected result 1: startup logs show the reduced tool count
  - Expected result 2: prompt/planning latency improves during MCP-heavy turns
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `0ff64cff-ba01-4a5b-92c0-3185151477e8`
  - Assignee: Cursor
  - Sync status: synced_to_archon

### Startup churn and readiness gap
- Status: synced_to_archon
- Date: 2026-03-08 13:20 -07:00
- Area: runtime
- Summary: Restarts still trigger expensive VectorDB, knowledge, and environment setup work long after health checks go green.
- Trigger: repeated restart monitoring and slow first-turn behavior after healthy status
- Evidence:
  - Logs: `Initializing VectorDB...`, knowledge processing, startup service churn
  - Files: preload/startup/runtime initialization paths
  - Commands: repeated restart and log inspection
- Proposed action:
  - Step 1: identify what startup work can be cached, deferred, or skipped when unchanged
  - Step 2: separate readiness from liveness
  - Step 3: avoid unnecessary full warmup on each restart
- Validation:
  - Expected result 1: faster time from restart to first successful turn
  - Expected result 2: fewer logs showing repeated heavy initialization
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `8b992247-f4c8-44a4-8707-8ed1cb9c0161`, `85a9b51e-6d97-44f1-bdc0-e1eab36c9d0b`, `28a8029d-78ea-41be-8e0b-0d63a078e3ce`
  - Assignee: Cursor
  - Sync status: synced_to_archon

### Tool execution flow hardening
- Status: in_progress
- Date: 2026-03-08 13:20 -07:00
- Area: runtime
- Summary: The agent still wastes turns on malformed generated Python and awkward terminal/code-execution flows even when the container is healthy.
- Trigger: recent `SyntaxError` failures and `Detected shell prompt, returning output early`
- Evidence:
  - Logs: syntax errors in generated Python; shell prompt early-return messages
  - Files: code execution path and response/tool execution flow
  - Commands: live log monitoring during user turns
- Proposed action:
  - Step 1: reduce reliance on fragile generated shell/Python wrappers where possible
  - Step 2: harden tool output parsing and early-return handling
  - Step 3: fail faster and more clearly when tool-generated code is malformed
- Validation:
  - Expected result 1: fewer wasted turns on tool-code syntax errors
  - Expected result 2: clearer recovery behavior when a tool step fails
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `0b77b48c-0180-4bfb-9430-bfb9fbfc9034`
  - Assignee: Claude
  - Sync status: partially_synced

### End-to-end latency instrumentation
- Status: synced_to_archon
- Date: 2026-03-08 13:20 -07:00
- Area: runtime
- Summary: Performance discussions still mix prompt-build time, model latency, tool execution time, and restart overhead because there is no per-turn timing breakdown.
- Trigger: repeated debugging sessions where "slow" meant different things in different turns
- Evidence:
  - Logs: symptoms are visible, but not attributed per phase
  - Files: request/agent/tool runtime paths
  - Commands: repeated manual log inspection
- Proposed action:
  - Step 1: add timings for prompt build, model call, tool execution, and post-processing
  - Step 2: emit one compact per-turn summary in structured logs
  - Step 3: use those timings to prioritize future optimization
- Validation:
  - Expected result 1: each slow turn shows where time was actually spent
  - Expected result 2: future performance work is evidence-based
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `6a86c4d3-254d-4d6f-874e-bca78edcb7c5`
  - Assignee: Cursor
  - Sync status: synced_to_archon

### Increase httpx connection pool for MCP clients
- Status: synced_to_archon
- Date: 2026-03-08 15:30 -07:00
- Area: mcp
- Summary: MCP httpx client uses default pool limits (5 connections/host) which bottlenecks high-frequency tool calls to local MCP servers.
- Trigger: Performance audit of container with local models (Claude Code validation session).
- Evidence:
  - Files: `python/helpers/mcp_handler.py` (lines 1139-1168, `CustomHTTPClientFactory`)
  - Logs: no explicit pool config; httpx defaults to 5 per-host connections
- Proposed action:
  - Step 1: Add `limits=httpx.Limits(max_connections=40, max_keepalive_connections=20)` to `CustomHTTPClientFactory.create()`
  - Step 2: Verify no connection leak under sustained MCP tool usage
- Validation:
  - Expected result 1: Reduced latency on back-to-back MCP tool calls (especially google_workspace)
  - Expected result 2: No connection errors or socket exhaustion under load
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `a92bbea5-c1f6-4d99-8a71-0e4b5c46e3b6`
  - Assignee: Claude
  - Sync status: synced_to_archon

### Switch Uvicorn WebSocket implementation from wsproto to auto
- Status: synced_to_archon
- Date: 2026-03-08 15:30 -07:00
- Area: runtime
- Summary: Uvicorn is configured with `ws="wsproto"` (pure Python). Switching to `ws="auto"` prefers `httptools` (C extension) when available for faster WebSocket I/O.
- Trigger: Performance audit of container with local models (Claude Code validation session).
- Evidence:
  - Files: `run_ui.py` (line 659, `ws="wsproto"`)
  - Logs: httptools is already in the dependency tree via uvicorn
- Proposed action:
  - Step 1: Change `ws="wsproto"` to `ws="auto"` in `run_ui.py`
  - Step 2: Verify WebSocket connections still work correctly (state sync, chat, dev namespace)
- Validation:
  - Expected result 1: WebSocket connections established without error
  - Expected result 2: Measurably lower CPU on sustained WebSocket traffic (state pushes)
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `2c8143e7-0703-42c7-8a06-2708ac952284`
  - Assignee: Cursor
  - Sync status: synced_to_archon

### Make VNC/X11 supervisor services conditional
- Status: synced_to_archon
- Date: 2026-03-08 15:30 -07:00
- Area: docker
- Summary: 6 supervisor processes (xvfb, fluxbox, x11vnc, autocutsel, wallpaper, setup_vnc_password) run unconditionally, consuming ~100MB RAM even when no VNC client connects.
- Trigger: Performance audit — container runs on 16GB limit with local models consuming most VRAM/RAM.
- Evidence:
  - Files: `docker/run/fs/etc/supervisor/conf.d/vnc.conf`
  - Commands: `supervisorctl status` shows all 6 VNC processes always running
- Proposed action:
  - Step 1: Wrap vnc.conf services with `autostart=%(ENV_ENABLE_VNC)s` or use a startup script that conditionally includes vnc.conf
  - Step 2: Default `ENABLE_VNC=true` in docker-compose.yml to preserve current behavior
  - Step 3: Document in README that `ENABLE_VNC=false` disables the desktop
- Validation:
  - Expected result 1: With `ENABLE_VNC=false`, no xvfb/fluxbox/x11vnc processes running
  - Expected result 2: With `ENABLE_VNC=true` (default), behavior identical to current
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `3b3b013d-12cf-49b5-ae82-78fb9a7e8ad8`
  - Assignee: Cursor
  - Sync status: synced_to_archon

### Add Uvicorn multi-worker support
- Status: synced_to_archon
- Date: 2026-03-08 15:30 -07:00
- Area: runtime
- Summary: Uvicorn runs single-worker (no `workers` param). Adding `workers=2` enables concurrent HTTP request handling, unblocking parallel tool calls from the LLM.
- Trigger: Performance audit — single event loop blocks when one request does synchronous I/O.
- Evidence:
  - Files: `run_ui.py` (lines 653-662, `uvicorn.Config(...)` — no `workers` param)
  - Logs: would manifest as increased latency under concurrent tool execution
- Proposed action:
  - Step 1: Add `workers=int(os.environ.get("UVICORN_WORKERS", "1"))` to uvicorn.Config
  - Step 2: Set `UVICORN_WORKERS=2` in docker-compose.yml
  - Step 3: Verify WebSocket state sync and SocketIO still work with multiple workers (may need sticky sessions or shared state)
- Validation:
  - Expected result 1: Two uvicorn worker processes visible in `ps aux`
  - Expected result 2: Concurrent API requests handled without blocking each other
  - Expected result 3: WebSocket/SocketIO connections remain stable across workers
- Archon sync:
  - Project: AgentZ / A0 SIP
  - Task ID: `af59349f-10c8-4e35-9160-3fe373bb1992`
  - Assignee: Cursor
  - Sync status: synced_to_archon
