# Agent Zero – Improvement log

Findings from monitoring the app and logs. Update this file when testing or after reviewing `docker logs agent-zero`.

**Last monitored:** 2026-03-04 (batch improvements implemented: WebSocket auth, code validation, MCP context manager, autocutsel timing, documentation)

---

## Task ownership & status

| Task | Owner | Status |
|------|--------|--------|
| ipython (#0) | Claude Code (me) | Done — installed in container + added to Dockerfile |
| xvfb crash loop (#10) | Background agent | Done — `start_xvfb.sh` wrapper, supervisor configs fixed, non-fatal X11 |
| Archon MCP timeout (#1) | Background agent | Done — Docker DNS, network join, protocol fix, init_timeout 30s |
| Starlette assertion (#9) | Cursor | Done — SSE handler wrapped; AssertionError/connection errors logged (mcp_server.py) |
| Health check log noise | Cursor | Done — _HealthCheckAccessLogFilter suppresses GET /health 200 (run_ui.py) |
| Duplicate POST /projects | Cursor | Done — loadProjectsList deduplicated via in-flight promise (projects-store.js) |

---

## For Claude (Cursor update)

**2026-03-03 — Issue #0 (ipython) addressed:**

- **requirements.txt:** Added `ipython>=8.0.0` so new Docker builds and venvs get ipython; `runtime: "python"` will use it when available.
- **code_execution_tool.py:** Fallback when ipython is not installed: `python_runner = shutil.which("ipython") or "python3"`; command is `{python_runner} -c {escaped_code}`. So existing containers without ipython still work via `python3` until the image is rebuilt.
- **Priority order:** #0 can be marked done after next image rebuild; fallback is live immediately. No change to `google_apis.md` or knowledge; that mitigation remains as-is.

---

## Monitoring (continued) – same day

- **Status:** Container still healthy (Up 7 min), Web UI and VNC RUNNING, /health 200.
- **New:** Agent attempted to list Google Drive folder; generated code that builds **Gmail** service then calls `service.files().list()` (Drive API). Gmail service has no `.files()` — must use `build('drive', 'v3', credentials=creds)`. Agent then retried but streamed code was split mid-line, producing **SyntaxError: '(' was never closed** (e.g. `credentials=creds)` broken across log/stream). See **Issue 8** and **Opportunities** below.

### Automated 90s monitor run (same day)

- **ASGI exception on shutdown:** During server shutdown, `Exception in ASGI application` in MCP SSE path: Starlette `body_stream` saw `http.response.start` when it expected `http.response.body` (`/a0/python/helpers/mcp_server.py` → fastmcp → starlette). Likely client disconnect or response ordering during shutdown. **Opportunity:** Handle disconnect/shutdown in MCP SSE route so response lifecycle is closed cleanly; catch and log instead of raising into ASGI.
- **Supervisor FATAL / kill (null):** Processes `autocutsel`, `xvfb`, `fluxbox` entered FATAL (from_state BACKOFF). Event listener ran "Killing off supervisord instance" then `CRITICAL: Why am I still alive? Send KILL to all processes...` and `/bin/kill: failed to parse argument: '(null)'`. **Opportunity:** Fix event listener so it never passes a null pid to `kill`; make autocutsel/xvfb/fluxbox optional or more resilient so FATAL doesn’t cascade.
- **Recurring:** OAuth 404, POST /mcp/.../sse 405, WebSocket session not valid, Archon 10s timeout, pathspec/litellm deprecations, SyntaxError from streamed code (agent then reasoned about “how Python is parsing my code when embedded in a shell command”).

### Second 90s monitor run (same day)

- **Status after run:** Container healthy (Up about a minute), Web UI and VNC RUNNING.
- **Same pattern:** ASGI exception on shutdown (MCP SSE body_stream), supervisor FATAL for autocutsel → xvfb → fluxbox, then **x11vnc** "gave up: entered FATAL state, too many start retries too quickly", and `/bin/kill: failed to parse argument: '(null)'`. After restart, server process 58 started; OAuth 404, POST /mcp/.../sse 405, WebSocket auth failed, Archon timeout, and code_execution SyntaxError again.
- **Takeaway:** Display stack (xvfb, fluxbox, autocutsel) and then x11vnc enter FATAL in a cascade; the event listener's kill path still receives a null pid. After supervisor restarts, run_ui and VNC report RUNNING again. Fixing the null-pid kill and making display/VNC optional or more resilient would reduce log noise and avoid repeated FATAL cycles.

### Monitor run 2026-03-03

- **Status:** Container Up ~1 hr (healthy); `/health` 200. Web UI and VNC RUNNING. HTTP mode (`AGENT_ZERO_HTTP_ONLY=1`); in-app Flare tunnel available.
- **Log sample:** Last 200 lines + grep for WARNING/ERROR/Deprecation/Invalid HTTP.
- **Issues observed:**
  1. **Deprecations still in logs:** pathspec `GitWildMatchPattern` / `gitignore` (file_tree/backup were fixed; may be another caller or image not rebuilt); litellm `processed_chunk.dict()` → use `model_dump`; faiss/numpy `numpy.core._multiarray_umath` + SWIG `SwigPyPacked` (upstream). Repeats on many requests → log noise.
  2. **Invalid HTTP request:** Multiple `WARNING: Invalid HTTP request received.` — client (e.g. healthcheck or scanner) sending non-HTTP to port 80; not suppressed by health access-log filter (that only filters GET /health 200 in access log). **Opportunity:** Consider suppressing or downgrading this uvicorn message if it’s from known probes.
  3. **MCP notification warning:** `Failed to validate notification: RequestResponder must be used as a context manager. Message was: method='notifications/cancelled' params={'requestId': 9, 'reason': 'McpError: MCP error -32001: Request timed out'}`. Suggests MCP response path sending a notification outside context manager. **Opportunity:** Ensure notification/response lifecycle uses context manager in MCP stack (likely fastmcp/mcp dependency).
  4. **ASGI Exception / ExceptionGroup:** `Exception in ASGI application` with `ExceptionGroup: unhandled errors in a TaskGroup` in MCP path — consistent with disconnect/timeout during SSE. Already mitigated by Starlette #9 wrap; may still surface on certain client disconnect patterns.
  5. **code_execution_tool / Playwright:** Agent tried to test Playwright. (a) `google_api_env` venv Python reported “corrupted (null bytes error)” so agent tried system `python3`. (b) System Python hit `externally-managed-environment` (PEP 668) so `pip install playwright` failed. Agent then tried `/a0/usr/workdir` with system pip and failed again. **Opportunity:** Document that project venvs with corrupted interpreters should be recreated; consider using main venv or container-installed Playwright for “test Playwright” when no healthy project venv exists.
- **Positives:** No crashes; MCP POST /mcp/.../messages/ 202 Accepted; health 200; agent reasoning and tool calls present in logs.
- **Follow-up (same day, evening):** Container Up 3 min (healthy), `/health` 200. **fluxbox** in restart loop: supervisor repeatedly logs `WARN exited: fluxbox (exit status 1; not expected)` and respawns; `/var/log/supervisor/fluxbox.err.log` shows `Failed to read: session.*` (session.cacheMax, session.autoRaiseDelay, etc.) then "Setting default value" — fluxbox may be exiting due to missing/incomplete config or display timing. **Opportunity:** Add minimal `~/.fluxbox` config so fluxbox doesn’t exit, or make fluxbox autostart=false and start it only when VNC is first used. faiss/numpy deprecations still present in log sample.

### Monitor run 2026-03-03 22:58 (active agent session)

- **Status:** Container Up 17 min (healthy); CPU 0.47% (idle). Memory 1.538 GiB. All 8 services RUNNING (17 min uptime). Agent was actively generating PCI-ASSISTANT one-pager via `code_execution_tool` (terminal runtime).
- **Critical finding — health filter NOT working + log interleaving corrupts JSON:**
  1. **`_HealthCheckAccessLogFilter` not filtering:** 20× `GET /health HTTP/1.1" 200 OK` in 10 minutes of logs. The filter exists at `run_ui.py:41` and is installed at line 562, but health checks still pass through. **Root cause (likely):** Uvicorn's `Server.startup()` calls `config.configure_logging()` which reconfigures loggers and may remove filters added before `.run()`. The filter must be installed AFTER uvicorn finishes its logger setup, not before. **Issue #20.**
  2. **Log interleaving corrupts agent JSON output (SEVERE):** Health check log lines inject mid-token into the agent's streaming JSON, e.g. `"tool_name": "code_executionINFO:     127.0.0.1:47376 - "GET /health HTTP/1.1" 200 OK\n_tool"`. The tool name `code_execution_tool` is split into `code_execution` and `_tool` with a health check line between them. This happens because agent streaming output and uvicorn access log share stdout without synchronization. This is worse than issue #6 (log interleaving for readability) — it's **data corruption** that could cause JSON parse failures if output is consumed programmatically. **Issue #21.** **Opportunity:** (a) Fix health filter to eliminate the most frequent interleaver; (b) route uvicorn access log to a separate file/stream; (c) use a shared lock or line-buffered wrapper for stdout writes.
- **Agent activity:** Agent used `code_execution_tool` (terminal runtime) to create PCI-ASSISTANT one-pager via heredoc. SyntaxError occurred on first attempt (triple-quote truncation), then succeeded via heredoc approach. MCP active: multiple POST /mcp/messages/ 202 Accepted from 172.217.14.123 (Cursor/IDE).
- **No new HTTP errors** beyond already-documented patterns.

### Monitor run 2026-03-03 22:50 (post-rebuild)

- **Status:** Container Up 8 min (healthy); `/health` 302 (OK). All 8 supervisor services RUNNING. CPU settled at 6% (spiked to 93% during startup loading). Memory 1.73 GiB / 7.65 GiB. 112 PIDs.
- **New issues observed:**
  1. **google_workspace MCP fails with ExceptionGroup:** `MCPClientBase (google_workspace - list_tools_op): Error during operation: ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)`. Root cause: user settings (`/a0/usr/settings.json`) define `google_workspace` at `http://host.docker.internal:8000/mcp` (type: `streamable-http`), but port 8000 on the host runs the **PCI-ASSISTANT backend** (uvicorn with `--ssl-keyfile`/`--ssl-certfile`). Plain HTTP hits an HTTPS server → `curl: (52) Empty reply from server`. **Issue #17.** **Opportunity:** Either start the actual workspace-mcp server on the host, change URL to `https://...`, or remove the entry from user settings if not needed.
  2. **MCP `streamablehttp_client` deprecation:** `DeprecationWarning: Use streamable_http_client instead` at startup. `mcp_handler.py:33` imports deprecated `streamablehttp_client` from `mcp.client.streamable_http`. **Issue #18.** **Opportunity:** Rename import to `streamable_http_client` (the new name in the mcp package).
  3. **autocutsel crash-loop at startup:** 4× `WARN exited: autocutsel (exit status 1; not expected)` before stabilizing. Happens because xvfb hasn't created the display socket yet when autocutsel starts. Currently `startsecs=0` so supervisor counts every exit as unexpected. **Improvement to #10.** **Opportunity:** Add `depends_on=xvfb` or a startup delay, or increase `startsecs` to 3 so supervisor waits for stability.
  4. **fluxbox session.* errors (still present):** `Failed to read: session.screen0.toolbar.alpha` (and ~10 other keys) → "Setting default value". Cosmetic but contributes log noise. See action item #15.
  5. **SyntaxError: incomplete input:** Agent tried to execute a Python script (PCI-ASSISTANT one-pager creation) but the code was truncated mid-triple-quote string. `Cell In[1], line 4 SyntaxError: incomplete input`. Recurring pattern — see issue #8 (streamed code split).
  6. **Pydantic .dict() deprecation (litellm):** Still appearing despite litellm>=1.82.0 in requirements.txt. The installed version may not have the fix, or the deprecation path changed. See #5.
- **Recurring (no change):** faiss/numpy `numpy.core._multiarray_umath`, SwigPy module warnings (upstream). OAuth 404, MCP SSE 405 (documented).
- **Positives:** All services RUNNING on first try (no xvfb FATAL cascade). archon (14 tools) and crawl4ai_rag (5 tools) loaded successfully. CPU settles quickly. No container kills or crashes.
- **Resource snapshot:**
  ```
  CPU:     6.22% (settled from 93% startup spike)
  Memory:  1.73 GiB / 7.65 GiB
  PIDs:    112
  Net:     56.7 MB in / 4.29 MB out
  Block:   1.73 GB read / 231 MB write
  ```

### Monitor run 2026-03-03 (credential focus)

- **Status:** Container Up 10 min (healthy); `/health` 200.
- **Credential issues observed:**
  1. **document_query returned full token.json to agent (LEAK):** The agent used `document_query` with path `/a0/usr/projects/a0_sip/token.json`. The tool returned the entire file (access token, refresh_token, client_id, client_secret) into the response and logs. **Fixed:** In `python/helpers/document_query.py`, added blocklist: `document_get_content` raises "Access denied" for basenames `token.json`, `credentials.json`, `secrets.env`, `.env`, `.env.local`; same check when retrieving from the vector store.
  2. **Agent confusion about credentials.json vs token.json:** Logs showed "credentials file exists but is missing refresh_token" and "missing client_secret, refresh_token, client_id". credentials.json has client_id/client_secret; token.json has refresh_token + access token. **Opportunity:** Clarify in knowledge (e.g. google_apis.md) that token.json holds runtime tokens, credentials.json holds OAuth client ids only.
- **Recommendation:** Rotate the exposed OAuth client secret and refresh token if the log output was persisted or shared.

### Monitor run 2026-02-18

- **Status:** Container Up 17 min (healthy); Web UI and VNC RUNNING. Settings: ollama glm-4.7-flash:32k (chat/browser), qwen3-14b-claude-4.5-opus-high-reasoning (utility).
- **Log sample:** Last ~400 lines + 90s window (idle); no Starlette assertion or xvfb/supervisor FATAL in window.
- **Recurring (low impact):**
  - **pathspec:** `GitWildMatchPattern ('gitwildmatch')` deprecated — use `'gitignore'` (see #5).
  - **litellm:** `processed_chunk.dict()` deprecated — use `model_dump` (see #5).
  - **GET /health 200:** Still present in logs when access log is enabled. If the running image has the health filter, ensure `uvicorn_access_logs_enabled` is True and filter is attached; otherwise rebuild/restart to pick up `_HealthCheckAccessLogFilter`.
- **Google API / code_execution:**
  - Agent used **system python3** for Drive script → `ModuleNotFoundError: No module named 'google.oauth2'` (main venv has no google-* packages). Agent then correctly used **project venv** `/a0/usr/workdir/google_api_env/bin/python3` and script ran; Drive API returned **403 Insufficient Permission** (OAuth token missing Drive scope — user/consent issue, not code).
  - **Opportunity:** Either add `google-auth`/`google-api-python-client` to main venv so `runtime: "python"` can run simple Drive/Gmail snippets, or keep as-is and document in `google_apis.md` that project-specific venv is required for Google APIs.
- **Positives:** No crashes in window; MCP POST /mcp/.../messages/ 202 Accepted (normal); agent recovered from module error by switching to project venv.

---

## Completed Improvements (this session)

| Improvement | Status | Details |
|-------------|--------|---------|
| GLM repetition loop fix | Done | Added `frequency_penalty`, `max_tokens`, `temperature` via LiteLLM OpenAI-compat kwargs to all Ollama presets |
| Context length 128K → 32K | Done | Reduced VRAM usage, faster inference for all Ollama presets |
| `glm-4.7-flash:32k` Modelfile | Done | Created on Ollama server (192.168.50.7) for VRAM optimization |
| Enhanced loop detection | Done (Cursor) | Within-stream repeat detection (250-char block × 3) + max iteration guard (20) in `agent.py` |
| Per-model kwargs tuning | Done (Cursor) | GLM `frequency_penalty` 1.45, qwen3 `temperature` 0.3, ollama_claude util 1.1 |
| Playwright browser persistence | Done | Volume mount `./playwright-browsers:/root/.cache/ms-playwright` + Dockerfile install step |
| Google API knowledge file | Done | `knowledge/main/google_apis.md` — indexed (3 files found, 2 new docs from 1 file) |
| Preset validation tests | Done | `tests/test_ollama_preset_kwargs.py` — 36 tests passing |
| Starlette assertion (#9) | Done (Cursor) | MCP SSE: try/except AssertionError + connection errors; log and continue (mcp_server.py) |
| Health check log noise | Done (Cursor) | _HealthCheckAccessLogFilter on uvicorn.access for GET /health 200 (run_ui.py) |
| Duplicate POST /projects | Done (Cursor) | loadProjectsList in-flight promise deduplication (projects-store.js) |
| Health filter bypass (#20) | Done | `_FilteredUvicornServer` subclass installs filter AFTER uvicorn startup (run_ui.py) |
| Log interleaving (#21) | Done | Access log redirected from stdout to stderr in `_FilteredUvicornServer.startup()` |
| MCP import deprecation (#18) | Done | `streamablehttp_client` → `streamable_http_client`; adapted to new API (mcp_handler.py) |
| Tool error streak loop (#22) | Done | Consecutive tool error detection (3× same tool fails → break loop) in agent.py |

---

## Resource Snapshot (latest — 2026-03-03 22:50)

```
Container:   Up (healthy), rebuilt at 22:40
CPU:         6.22% (settled from 93% startup spike)
Memory:      1.73 GiB / 7.65 GiB (limit: 16 GiB, reservation: 10 GiB)
Network:     56.7 MB in / 4.29 MB out
Block I/O:   1.73 GB read / 231 MB write
PIDs:        112
Playwright:  898 MB persisted at ./playwright-browsers/ (chromium-1169)
Ollama:      GLM-4.7-Flash:32k (chat/browser) + bazobehram/qwen3-14b (utility)
MCP:         crawl4ai_rag (5 tools, OK) | archon (14 tools, OK) | google_workspace (FAIL — wrong server)
Knowledge:   3 files indexed in /a0/knowledge/main/
Supervisor:  8 RUNNING, 4 one-shot EXITED (normal), 0 FATAL
```

---

## Issues observed

### 0. `ipython` not installed — `code_execution_tool` python runtime broken ✅ FIXED (Cursor)

**Priority:** HIGH — agent cannot run Python code via `runtime: "python"`

```
A0: Using tool 'code_execution_tool' (runtime: python)
-bash: ipython: command not found
```

- **Cause:** Agent Zero's `code_execution_tool` with `runtime: "python"` shells out to `ipython`, which is not installed in `/opt/venv-a0/`.
- **Impact:** Agent must fall back to `runtime: "terminal"` with explicit python paths. Wastes turns when agent first tries python runtime, fails, then switches.
- **Fixed (Cursor 2026-03-03):**
  - [x] **Quick fix:** `ipython>=8.0.0` added to `requirements.txt` (new image/venv will have ipython)
  - [x] **Robust fix:** `code_execution_tool.execute_python_code` uses `shutil.which("ipython") or "python3"` so existing containers work with `python3` until rebuild
  - [ ] Knowledge file workaround remains: `google_apis.md` tells agent to use `runtime: "terminal"` where relevant

### 1. MCP Archon timeout at startup ✅ FIXED (Background agent)

```
MCPClientBase (archon - list_tools_op): Error during operation: McpError: Timed out while waiting for response to ClientRequest. Waited 10.0 seconds.
MCPClientBase (archon): 'update_tools' operation failed
```

- **Root causes (3):**
  1. **Protocol mismatch** (most critical): `.mcp.json` used `"transport": "http"` but `mcp_handler.py` only checked `"type"` field → used SSE client to connect to Streamable HTTP server → always times out.
  2. **Docker network isolation**: agent-zero on `agentz_default` (172.18.x), archon-mcp on `archon_app-network` (172.22.x) → host IP proxy (`192.168.50.7`) was unreliable.
  3. **Dead `archon-local` entry**: `127.0.0.1:8051` never works cross-container → connection refused on every startup.
- **Fixed:**
  - `.mcp.json`: URL → `http://archon-mcp:8051/mcp` (Docker DNS), `"type": "streamable-http"`, `init_timeout: 30`, `tool_timeout: 120`, removed `archon-local`
  - `docker-compose.yml`: Added `archon_app-network` (external) to agent-zero service
  - `mcp_handler.py`: `_determine_server_type()` now checks `transport` field; `_is_streaming_http_type()` recognizes `"http"`; new `_normalize_transport_to_type()` mapper; `MCPServerRemote.update()` accepts `"transport"` key
  - `settings.py`: Default `mcp_client_init_timeout` raised from 10s to 30s
- **Verified:** `curl -X POST http://archon-mcp:8051/mcp` from agent-zero container returns HTTP 200 with `initialize` response.

### 2. WebSocket auth failure before login

```
Warning: WebSocket authentication failed for /state_sync TX5PMmltbHEm36xZAAAB: session not valid
```

- **Cause:** Client (e.g. browser) opens WebSocket to `/state_sync` before or without a valid session (e.g. pre-login, expired cookie).
- **Impact:** Expected for unauthenticated clients; may generate log noise.
- **Opportunity:** Consider not logging at WARNING when the request has no session (treat as expected); or rate-limit this log line to avoid spam on repeated reconnects.

### 3. OAuth discovery 404

```
GET /.well-known/oauth-authorization-server HTTP/1.1" 404 Not Found
```

- **Cause:** A client (e.g. Cursor or IDE at 142.251.34.74) is probing for OAuth 2.0 authorization server metadata. Agent Zero does not implement this endpoint.
- **Impact:** None if OAuth is not used for that client; client may fall back to other auth.
- **Opportunity:** If OAuth-based IDE integration is desired, add `/.well-known/oauth-authorization-server` returning JSON (e.g. `authorization_endpoint`, `token_endpoint`, `jwks_uri`). Otherwise document that this 404 is expected.

### 4. MCP SSE endpoint 405 on POST

```
POST /mcp/t-.../sse HTTP/1.1" 405 Method Not Allowed
```

- **Cause:** SSE is GET-only; client sent POST (e.g. misconfigured MCP client or preflight).
- **Impact:** Request fails; client may retry with GET.
- **Opportunity:** Document that MCP SSE must be GET; optionally return 405 with an `Allow: GET` header or a short body explaining the correct method.

### 5. Deprecation warnings in logs (pathspec + litellm addressed)

| Source | Message | Suggestion | Status |
|--------|--------|------------|--------|
| faiss/loader.py | `numpy.core._multiarray_umath` deprecated, use `numpy._core` or public API | Upgrade faiss-cpu / numpy or suppress in loader if upstream has no fix yet. | Upstream; monitor. |
| importlib/SWIG | `SwigPyPacked` / `SwigPyObject` / `swigvarlink` have no `__module__` | Likely from a compiled dependency (e.g. faiss); track upstream or suppress. | Upstream. |
| pathspec | `GitWildMatchPattern ('gitwildmatch')` deprecated, use `'gitignore'` | Pin or upgrade pathspec; use `gitignore` pattern type where supported. | **Done:** file_tree + backup use `from_lines(\"gitignore\", ...)`; pathspec>=1.0.4. |
| litellm (streaming_handler.py) | Pydantic `.dict()` deprecated, use `.model_dump()` | Upstream LiteLLM; upgrade when fixed or patch locally. | **Done:** litellm>=1.82.0 in requirements.txt. |

- **Opportunity:** Add a small “deprecation summary” script or CI step that parses logs and reports these so they can be tracked and addressed over time.

### 6. Log interleaving

- **Observation:** Application output (e.g. “Reasoning:”, “Response:”, JSON) and Uvicorn access lines (“INFO: GET /health”) are interleaved on stdout.
- **Impact:** Harder to grep or parse logs by concern (app vs HTTP).
- **Opportunity:** Use structured logging (JSON) with a `logger` or `source` field; or separate app logs to a different stream/file (e.g. app to stderr, uvicorn to stdout, or both to files with rotation).

### 7. Duplicate POST /projects

- **Observation:** Two identical `POST /projects HTTP/1.1" 200 OK` in quick succession.
- **Possible cause:** Frontend double-submit (e.g. two tabs, or button fired twice).
- **Opportunity:** Add idempotency (e.g. client-generated request id) or debounce on the client for project create/list.

### 8. code_execution_tool: streamed code split / wrong API (Drive vs Gmail)

- **Observation:** Agent generated Python that builds `service = build('gmail', 'v1', ...)` then calls `service.files().list(...)`. Gmail API has no `files()`; that is the **Drive API**. Execution then failed with **SyntaxError: '(' was never closed** — the streamed code was broken mid-expression (e.g. `credentials=creds)` split so the closing `)` appeared on another line or was truncated).
- **Impact:** Drive folder listing fails; user sees syntax error instead of “use Drive API”.
- **Mitigated:** `knowledge/main/google_apis.md` now documents correct per-service API patterns (Gmail, Drive, Sheets, Slides). Agent should recall this knowledge in future conversations.
- **Opportunity:** (1) Verify knowledge recall helps in next Drive-related conversation. (2) Ensure code_execution_tool receives complete code (e.g. buffer until full JSON/delimiter, or reject truncated payloads).

### 9. ASGI exception in MCP SSE during shutdown

- **Observation:** On server shutdown, `Exception in ASGI application`: Starlette `body_stream` expected `http.response.body` but received `http.response.start` again (MCP SSE route: mcp_server.py → fastmcp → starlette).
- **Impact:** Noisy traceback on restart/stop; possible unclean disconnect for MCP clients.
- **Opportunity:** In MCP SSE handler, handle client disconnect and shutdown gracefully; catch response-ordering edge cases and log instead of raising.

### 10. Supervisor FATAL and kill (null) — 258 X11 failures per startup ✅ FIXED (Background agent)

- **Observation:** Processes `autocutsel`, `xvfb`, `fluxbox` entered FATAL (from_state BACKOFF). Supervisor event listener then ran “Killing off supervisord instance” and later `CRITICAL: Why am I still alive? Send KILL to all processes...` with `/bin/kill: failed to parse argument: '(null)'`. **258 X11-related failure lines per startup cycle** — massive log noise.
- **Root causes (4):**
  1. Stale X11 lock files (`/tmp/.X99-lock`) prevent Xvfb from binding display :99
  2. Cascade failure: xvfb FATAL → fluxbox, x11vnc, autocutsel all FATAL
  3. `autocutsel -fork` flag incompatible with supervisor (forks immediately, supervisor sees exit)
  4. Event listener kills entire container on ANY FATAL, including non-essential X11 services
- **Fixed:**
  - `docker/run/fs/exe/start_xvfb.sh` (NEW): Wrapper removes stale lock files before exec-ing Xvfb
  - `docker/run/fs/etc/supervisor/conf.d/vnc.conf`: Uses `start_xvfb.sh` wrapper; added `startsecs=2`, `startretries=5` to xvfb; added `startsecs=0`, `startretries=10` to fluxbox/x11vnc/autocutsel; removed `-fork` from autocutsel; added log rotation caps
  - `docker/run/fs/exe/supervisor_event_listener.py`: Added `NON_ESSENTIAL_PROCESSES` frozenset for VNC/X11; non-essential FATAL only logs warning, doesn't kill supervisord; fixed bug where `debug_mode` would `continue` without calling `listener.ok()`
  - Both `Dockerfile` and `docker/run/Dockerfile`: Added `start_xvfb.sh` to chmod line
- **Verified:** After simulated xvfb crash, supervisor recovers cleanly without killing the container.

### 11. LiteLLM unawaited coroutine (streaming)

- **Observation:** `RuntimeWarning: coroutine 'BaseLLMHTTPHandler.acompletion_stream_function' was never awaited` — seen during Ollama streaming responses.
- **Impact:** Low — may cause occasional dropped or incomplete streaming responses.
- **Opportunity:** Update LiteLLM to latest version; monitor if this causes visible response drops.

### 12. Playwright was missing (FIXED)

- **Observation:** `crawl4ai_rag.crawl_website` failed with `BrowserType.launch: Executable doesn't exist at /root/.cache/ms-playwright/chromium-1208/chrome-linux/chrome`. Playwright 1.52.0 pip package was installed but browser binaries were never downloaded. Lost on every container recreate.
- **Fixed:** Volume mount `./playwright-browsers:/root/.cache/ms-playwright` in `docker-compose.yml` + `playwright install chromium` in Dockerfile. Browsers (898 MB) now persist across recreates. System deps installed manually (`libasound2t64`, `libgbm1`, etc.) since `--with-deps` fails on Kali.
- **Remaining risk:** If Playwright pip package upgrades (e.g. 1.52 → 1.58), it may want different browser versions (chromium-1208 vs chromium-1169). May need to re-run `playwright install chromium` after venv updates.

### 17. google_workspace MCP fails at startup (ExceptionGroup)

- **Observation:** `MCPClientBase (google_workspace - list_tools_op): Error during operation: ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)` on every container start.
- **Root cause:** User settings (`/a0/usr/settings.json`) define `google_workspace` as `type: streamable-http` at `http://host.docker.internal:8000/mcp`. Port 8000 on the host runs the **PCI-ASSISTANT backend** (uvicorn with SSL). Plain HTTP → HTTPS = empty reply. The actual workspace-mcp server is not running.
- **Impact:** MCP tool listing fails for google_workspace on every startup. archon and crawl4ai_rag unaffected.
- **Opportunity:** (a) Start the workspace-mcp server on the host (e.g. `workspace-mcp --port 8000`), (b) update the URL to the correct host/port/scheme, or (c) remove the `google_workspace` entry from user settings if not currently needed.

### 18. MCP `streamablehttp_client` import deprecated ✅ FIXED

- **Observation:** `DeprecationWarning: Use streamable_http_client instead.` logged at startup from `mcp_handler.py:33`.
- **Root cause:** `mcp_handler.py` imports `streamablehttp_client` (old name) from `mcp.client.streamable_http`. The mcp package renamed it to `streamable_http_client`.
- **Fixed:** Renamed import to `streamable_http_client` and updated call site. New API takes `http_client: httpx.AsyncClient` instead of individual `headers`/`timeout`/`httpx_client_factory` params — adapted `_create_stdio_transport` to build the client via `CustomHTTPClientFactory` and pass it directly.

### 20. Health check filter not working — `_HealthCheckAccessLogFilter` bypassed ✅ FIXED

- **Observation:** `GET /health HTTP/1.1" 200 OK` still appears in logs (20× in 10 minutes) despite `_HealthCheckAccessLogFilter` being defined (`run_ui.py:41`) and installed (`run_ui.py:562`).
- **Root cause:** Uvicorn's `Server.startup()` calls `config.configure_logging()` which reconfigures the `uvicorn.access` logger — removing filters added before `.run()`.
- **Fixed:** Created `_FilteredUvicornServer(uvicorn.Server)` subclass that overrides `startup()` to install the health filter AFTER `super().startup()` completes (after uvicorn configures its loggers). Filter is now guaranteed to persist.

### 21. Log interleaving corrupts agent JSON output (SEVERE) ✅ FIXED

- **Observation:** Uvicorn access log lines inject mid-token into the agent's streaming JSON output on stdout.
- **Root cause:** Agent streaming output and uvicorn access log both write to stdout (fd 1) without synchronization. Concurrent writes from different threads interleave at arbitrary byte boundaries.
- **Fixed:** `_FilteredUvicornServer.startup()` redirects the access log handler from `sys.stdout` to `sys.stderr` after uvicorn configures its loggers. Access logs now write to fd 2, agent output stays on fd 1 — no byte-level interleaving. Both streams still appear in `docker logs` but on different file descriptors.

### 22. Agent stuck in SyntaxError retry loop (code_execution_tool) ✅ FIXED

- **Observation:** GLM-4.7-Flash generates broken Python (e.g. `p_title.font.size Pt(54)` missing `=`), gets SyntaxError, regenerates near-identical broken code endlessly. CPU spiked to 1143%. Fluxbox crash-loop noise (11,190 of 12,075 log lines) masked the real issue.
- **Root cause:** Existing loop detection checks (250-char block repeat, exact multi-turn match, 20 max iterations) miss this pattern because the code varies slightly each iteration while the *error* is identical. The model never learns from the error.
- **Fixed:** Added consecutive tool error streak detection to `agent.py`:
  - `LoopData` tracks `tool_error_streak` (count), `tool_error_streak_name` (tool), `TOOL_ERROR_STREAK_MAX` (3)
  - After each tool execution, checks response for error patterns (`SyntaxError`, `IndentationError`, `NameError`, `TypeError`, `ModuleNotFoundError`, `FileNotFoundError`)
  - If same tool fails 3× consecutively with matching error patterns, breaks the loop with a warning message telling the agent to try a different approach
  - Counter resets on success or tool change

---

## Positive observations

- Container **healthy**; **/health** returns 200; Web UI and VNC **RUNNING**.
- Login flow works (302 to login, then 200 after POST /login); static assets 304 where appropriate.
- MCP **crawl4ai_rag** tools updated (5 tools); **Preload completed**.
- Agent responds with reasoning and structured JSON tool calls (e.g. response, code_execution_tool).
- Settings: **ollama glm-4.7-flash:32k** (chat/browser), **bazobehram/qwen3-14b-claude-4.5-opus-high-reasoning** (utility).

---

## Opportunities (product / UX)

- **Gmail vs Drive API:** User asked to “list files in this folder” (Google Drive link). Agent inferred Gmail API for “Drive folder”; listing Drive files requires **Drive API**, not Gmail API. Mitigated by `knowledge/main/google_apis.md` knowledge file.
- **Health check volume:** Many `GET /health` lines from Docker and scripts; consider reducing log level for 200 responses on /health (e.g. log at DEBUG) to keep logs focused.
- **Knowledge file for other tools:** The `google_apis.md` pattern could be extended to document other pre-installed tools, MCP servers, and scripts so the agent doesn't recreate them.

---

## Priority Order (recommended fix sequence)

1. ~~**ipython (#0)**~~ — **DONE:** ipython in requirements + fallback to python3 in code_execution_tool (Cursor)
2. ~~**xvfb crash loop (#10)**~~ — **DONE:** start_xvfb.sh wrapper, supervisor configs fixed, non-essential FATAL no longer kills container (Background agent)
3. ~~**Archon MCP timeout (#1)**~~ — **DONE:** Docker DNS, network join, protocol fix, init_timeout 30s (Background agent)
4. ~~**Starlette assertion (#9)**~~ — **DONE:** SSE handler wrapped with try/except (Cursor)
5. ~~**Health check log noise**~~ — **DONE:** _HealthCheckAccessLogFilter suppresses GET /health 200 (Cursor)
6. ~~**Package deprecations (#5)**~~ — pathspec: use `gitignore` in file_tree + backup; litellm>=1.82.0 in requirements. faiss/numpy remain upstream.

---

## Action items (suggested improvements)

From **Issues observed**, **Opportunities**, and **Monitor runs** (2026-02-18, 2026-03-03). Check off when done.

**Synced to Archon:** All 11 items created as tasks in A0 SIP project (`610ae854-2244-4cb8-a291-1e31561377ab`), feature `improve-md`. List/update via `python scripts/archon_api_tasks.py list --project-id 610ae854-2244-4cb8-a291-1e31561377ab` and `update TASK_ID --status done`.

| # | Action | Source | Owner | Status |
|---|--------|--------|--------|--------|
| 1 | Downgrade WebSocket auth log when no session: log at DEBUG or rate-limit "session not valid" line | #2 | Claude Code | ✅ Done (2026-03-04) |
| 2 | Document or implement OAuth: add `/.well-known/oauth-authorization-server` if IDE OAuth desired; else document that 404 is expected | #3 | Claude Code | ✅ Done (2026-03-04) |
| 3 | Document MCP SSE method: state that SSE is GET-only; optionally return 405 with `Allow: GET` or short explanatory body | #4 | Claude Code | ✅ Done (2026-03-04) |
| 4 | Package deprecations: upgrade faiss/numpy, pathspec (use `gitignore` pattern), LiteLLM (`.model_dump()`); add CI or script to report deprecations from logs | #5 | Done (pathspec + litellm); faiss/numpy upstream | ⚠️ Partial — browser-use 0.5.11→0.11.13, litellm 1.63.2→1.79.3, pypdf secure 6.7.5; full litellm 1.82.0 blocked by unknown dependency (2026-03-04) |
| 5 | Log structure: introduce structured logging (JSON with logger/source) or separate app vs HTTP to different streams/files | #6 | — | — |
| 6 | code_execution_tool: verify Drive knowledge recall in next Drive-related run; consider buffering/validating complete code before execution to avoid truncated stream | #8 | Claude Code | ✅ ast.parse validation (2026-03-04) |
| 7 | LiteLLM: upgrade to latest; monitor for unawaited coroutine / dropped streaming | #11 | Claude Code | ⚠️ Partial — browser-use 0.5.11→0.11.13 resolves openai conflict, litellm 1.63.2→1.79.3; full 1.82.0 blocked by unknown dependency (2026-03-04) |
| 8 | Playwright: document or automate re-running `playwright install chromium` after venv/Playwright pip upgrades | #12 | Claude Code | ✅ Done — docs/troubleshooting/playwright_upgrade.md (2026-03-04) |
| 9 | Health filter: verify `_HealthCheckAccessLogFilter` is active in running image (restart/rebuild if needed); confirm when `uvicorn_access_logs_enabled` is True | Monitor 2026-02-18 | — | — |
| 10 | Google API in main venv: add `google-auth` / `google-api-python-client` to main venv for `runtime: "python"` Drive/Gmail snippets, or document in `google_apis.md` that project venv is required | Monitor 2026-02-18 | Claude Code | ✅ Done — requirements.txt (2026-03-04) |
| 11 | Knowledge files: extend `google_apis.md` pattern to other pre-installed tools, MCP servers, and scripts so the agent doesn't recreate them | Opportunities | Claude Code | ✅ Done — knowledge/main/{mcp_servers,preinstalled_tools}.md (2026-03-04) |
| 12 | Invalid HTTP request: consider suppressing or downgrading uvicorn "Invalid HTTP request received" when from known probes (healthcheck/scanner) | Monitor 2026-03-03 | — | — |
| 13 | MCP RequestResponder: ensure notifications (e.g. notifications/cancelled on timeout) are sent inside context manager; fix or report upstream (fastmcp/mcp) | Monitor 2026-03-03 | Claude Code | ✅ Done — python/helpers/mcp_server.py (2026-03-04) |
| 14 | code_execution / Playwright: document corrupted project venv recovery; consider using main venv or container Playwright when project venv Python is broken | Monitor 2026-03-03 | Claude Code | ✅ Done — docs/troubleshooting/venv_recovery.md (2026-03-04) |
| 15 | fluxbox restart loop: add minimal ~/.fluxbox config or set autostart=false and start on VNC use to stop "exited (exit status 1)" / "Failed to read: session.*" spam | Monitor 2026-03-03 (evening) | Background agent | ✅ Done — docker/run/fs/root/.fluxbox/init (2026-03-03) |
| 16 | Google OAuth: clarify in knowledge (google_apis.md or GMAIL_OAUTH_SETUP) that token.json holds refresh_token/access token, credentials.json holds client_id/client_secret only | Monitor 2026-03-03 (credential) | Claude Code | ✅ Done — docs/guides/GOOGLE_OAUTH_FILES.md (2026-03-04) |
| 17 | google_workspace MCP: fix or remove entry in user settings — port 8000 is PCI-ASSISTANT (SSL), not workspace-mcp. Either start workspace-mcp, fix URL/scheme, or remove entry | #17 | — | — |
| 18 | MCP `streamablehttp_client` → `streamable_http_client`: update import in `mcp_handler.py:33` and call site to use new name before old is removed | #18 | Cursor | ✅ Done (2026-03-03) |
| 19 | autocutsel startup race: add `depends_on=xvfb` or increase `startsecs` from 0 to 3 in supervisor config so it waits for display before starting | #10 (improvement) | Claude Code | ✅ Done — vnc.conf startsecs=3 (2026-03-04) |
| 20 | Health filter bypass: `_HealthCheckAccessLogFilter` not working — uvicorn `configure_logging()` likely resets filters. Install filter AFTER uvicorn startup, not before `.run()` | #20 | Cursor | ✅ Done (2026-03-03) |
| 21 | Log interleaving corrupts JSON (SEVERE): uvicorn access log injects mid-token into agent streaming output. Fix #20 first, then route access log to separate file or add stdout write lock | #21 | Cursor | ✅ Done (2026-03-03) |

---

## How to refresh this file

1. Run: `./scripts/show_status.sh` and `docker logs agent-zero --tail 500 2>&1 | sed 's/\x1b\[[0-9;]*m//g'`.
2. Check for new errors, timeouts, 4xx/5xx, deprecations, and repeated patterns.
3. Append new issues under **Issues observed** with date and a short **Opportunity**.
4. Update **Last monitored** at the top.
5. Add or check off items in **Action items** as improvements are implemented.

---

## Continue monitoring while the app is running

Run in a separate terminal to tail logs and surface possible issues (errors, timeouts, 4xx/5xx). Press Ctrl+C to stop.

```bash
./scripts/monitor_agent_zero.sh
```

The script prints a short status, then follows logs and highlights lines containing `Error`, `error`, `WARNING`, `Warning`, `timeout`, `404`, `500`, `McpError`, `SyntaxError`, `Traceback`. Optionally log to a file and run in the background:

```bash
./scripts/monitor_agent_zero.sh 2>&1 | tee -a monitor_$(date +%Y%m%d).log
```
