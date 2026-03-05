# Task Log

## Completed

### 2026-03-03: Docker response-speed, status script, /health, Ollama repetition fix (Cursor)
- **Docker:** `shm_size: 512mb`, `memswap_limit: 16g` (service level), reservations 10G RAM / 3 CPUs, healthcheck `start_period: 30s`; container recreated.
- **Health:** No-auth `/health` route in `run_ui.py`; Docker healthcheck and `restart.sh` use `/health` (no 302s from curl).
- **Status:** `scripts/show_status.sh` prints container, health, Web UI, VNC, **Settings** (chat/util/browser from container), access URLs; `startup.sh` calls it at end; `MODELS.sh --status` runs same output.
- **Ollama repetition fix (RESPONSES.md follow-ups):** `scripts/ollama_create_modelfiles.sh` for glm-4.7-flash:32k (num_ctx 32768); presets ollama_glm, ollama_mixed, ollama_glm_claude use `glm-4.7-flash:32k` and per-preset kwargs (GLM frequency_penalty 1.45, ollama_claude 1.1, ollama_qwen3 temp 0.3). `agent.py`: LoopData.MAX_ITERATIONS=20, within-stream repetition detection (250-char block 3×), stream_repeat_detected handling.
- **Handoff:** `RESPONSES.md` — Claude ↔ Cursor coordination; Ollama section status set to "Cursor follow-up tasks complete".
- **IMPROVE.md #0 (ipython):** Added `ipython>=8.0.0` to `requirements.txt`; `code_execution_tool.execute_python_code` uses `shutil.which("ipython") or "python3"` so runtime works without ipython until image rebuild. IMPROVE.md updated: "For Claude (Cursor update)" section, #0 marked fixed, priority order #1 struck through.

### 2026-02-20: Agent Zero for ZeroClaw Integrators doc
- Created `docs/AGENT_ZERO_FOR_ZEROCLAW_INTEGRATORS.md`: entrypoints (REST /api_message, MCP SSE/HTTP, A2A), auth (X-API-KEY), example requests, constraints (rate limits, context lifetime 24h)
- Linked in `docs/DOCUMENTATION_INDEX.md` (Integration section and "I want to...")

### 2026-02-18: Code Review & Documentation Update
- Reviewed ~198 modified files (Black formatter pass + functional changes)
- Identified functional changes: memory consolidation bug fix, HTTPS/TLS LAN support, Docker build fix, macOS startup fix, faiss-cpu version relaxation
- Fixed 16+ broken links in `docs/DOCUMENTATION_INDEX.md` (post-reorganization paths)
- Fixed broken `../SECURITY_SETUP.md` links in `docs/COMPLETE_SETUP_GUIDE.md` (→ `./guides/SECURITY_SETUP.md`)
- Updated incomplete volume mount documentation to include all 5 Claude-related mounts
- Corrected `claude-pro` → `claude-pro-yolo` references across docs
- Added HTTPS/TLS documentation (`AGENT_ZERO_CERT_IPS`, `AGENT_ZERO_REGENERATE_CERT`)
- Updated `docs/README.md` with missing links (VNC, connectivity, native install, troubleshooting)
- Updated `QUICK_REFERENCE.md` (root) with new HTTPS/TLS env vars
- Updated `docs/QUICK_REFERENCE.md` with new environment variables
- Updated `DEPLOYMENT_QUICK_START.md` with HTTPS section and full data persistence list
- Added local changelog entry to `README.md`
- Created `PLANNING.md` and `TASK.md` per project conventions

### 2026-02-20: Enable Concurrent API Request Handling
- Root cause: all AgentContexts shared a single EventLoopThread singleton — one crash killed all inflight tasks
- Per-context EventLoopThread isolation: `thread_name=f"AgentContext-{self.id}"` in `agent.py`
- EventLoopThread.terminate() now cleans up `_instances` cache (`python/helpers/defer.py`)
- Context removal now terminates its thread: `task.kill(terminate_thread=True)`
- Added `last_result`/`last_error` fields to AgentContext for async result polling
- NEW endpoint: `POST /api_message_async` — fire-and-forget, returns `{context_id, status: "processing"}` immediately
- NEW endpoint: `POST /api_message_status` — poll task status (processing/completed/failed/idle/not_found)
- Existing `/api_message` unchanged (backward compatible)
- Tests: `tests/test_concurrent_api.py` — 11 tests, all passing
- Verified: two concurrent async requests processed independently in live container
- Archon task: 835f888b (feature: concurrent-api, status: done)

### 2026-02-20: ZeroClaw Integration Research & Analysis
- Researched ZeroClaw framework (Rust-native AI agent, MIT license)
- Created integration analysis: `PRPs/zeroclaw-integration-analysis.md`
- Agent Zero feedback incorporated (revised priorities: SQLite Memory → Security → Channels → Sidecar)
- Cursor contributed: `docs/AGENT_ZERO_FOR_ZEROCLAW_INTEGRATORS.md`
- Archon task: 77e5edf9 (feature: zeroclaw-integration, status: done)

### 2026-02-20: Project Validation — Full Pass
- P1 Lint: ruff check — all passed
- P2 Types: mypy — warnings only (pre-existing upstream), no critical errors
- P3 Style: ruff format — 203 files already formatted
- P4 Tests: pytest — 11/11 passed (7.09s)
- P5 E2E: Docker rebuild, validate.sh 9/9 phases passed (container healthy)
- Bug fix: restored `send_file`/`session` re-exports in `python/helpers/api.py` (lost in commit 54c51a0)

### 2026-03-03: Fix xvfb/X11 crash loop in Agent Zero container
- **Root cause:** Stale `/tmp/.X99-lock` on restart caused Xvfb to exit 1 in a loop; autocutsel `-fork` flag caused immediate daemonize (supervisor sees crash); no `startretries`/`startsecs` on dependent services; event listener killed the entire container on any FATAL state.
- **Fix 1 — start_xvfb.sh wrapper:** New `/exe/start_xvfb.sh` cleans up stale X lock files before exec-ing Xvfb.
- **Fix 2 — vnc.conf:** Added `startsecs=0`, `startretries=10` to fluxbox/x11vnc/autocutsel so they retry gracefully instead of going FATAL. Removed `-fork` from autocutsel. Added `1MB` log rotation caps.
- **Fix 3 — supervisor_event_listener.py:** Added `NON_ESSENTIAL_PROCESSES` set; X11/VNC FATAL states are logged as warnings but no longer kill supervisord.
- **Fix 4 — Dockerfiles:** Both `Dockerfile` and `docker/run/Dockerfile` updated to `chmod +x /exe/start_xvfb.sh`.
- **Verified:** Live-tested in running container — full stop/start cycles, Xvfb kill recovery, all services stable.

### 2026-03-03: Fix MCP Archon server timeout on Agent Zero startup
- **Root causes (3):**
  1. **Protocol mismatch:** `.mcp.json` used `"transport": "http"` but Agent Zero's `mcp_handler.py` only recognized `"type"` field and didn't map `"transport"`. The `type` defaulted to `"sse"`, so the SSE client was used against Archon's Streamable HTTP server.
  2. **Network isolation:** `agent-zero` (agentz_default, 172.18.x) and `archon-mcp` (archon_app-network, 172.22.x) were on different Docker networks. Traffic via host IP (192.168.50.7) went through Docker Desktop port proxy, which was unreliable.
  3. **Dead `archon-local` entry:** `127.0.0.1:8051` never works for cross-container communication.
- **Fix 1 — `.mcp.json`:** Changed URL from `192.168.50.7` to Docker DNS name `archon-mcp`, set `type: "streamable-http"`, added per-server `init_timeout: 30` / `tool_timeout: 120`, removed dead `archon-local` entry.
- **Fix 2 — `docker-compose.yml`:** Added `archon_app-network` (external) so agent-zero joins Archon's network on every start; documented dependency.
- **Fix 3 — `mcp_handler.py`:** `_determine_server_type()` now checks `transport` key (Claude Desktop config format). Added `_normalize_transport_to_type()` to map `"http"` to `"streamable-http"`. `MCPServerRemote.update()` now accepts `transport` and remaps it to `type`. `_is_streaming_http_type()` now recognizes bare `"http"`.
- **Fix 4 — `settings.py`:** Increased `mcp_client_init_timeout` default from 10s to 30s.
- **Verified:** `curl` from inside agent-zero to `http://archon-mcp:8051/mcp` returns HTTP 200 with proper MCP response.

### 2026-03-05: Tool error streak loop detection (#22)
- **Problem:** GLM-4.7-Flash stuck generating broken Python (e.g. `p_title.font.size Pt(54)` missing `=`), gets SyntaxError, retries endlessly. CPU spiked to 1143%.
- **Fix:** Added `tool_error_streak` counter to `LoopData` in `agent.py` — tracks consecutive tool execution errors by pattern (SyntaxError, IndentationError, NameError, TypeError, ModuleNotFoundError, FileNotFoundError). After 3 consecutive failures of same tool, breaks loop with warning.
- **Validated:** 153/153 tests pass, E2E 9/9, hot-deployed to running container.

### 2026-03-03–04: Batch improvements (IMPROVE.md #1–#21)
- **Code fixes:** Health filter bypass (#20), log interleaving (#21), MCP import deprecation (#18), WebSocket auth log (#1), code validation ast.parse (#6), MCP context manager (#13), autocutsel timing (#19), xvfb crash loop (#10)
- **Documentation:** OAuth well-known (#2), MCP SSE GET-only (#3), Playwright upgrade (#8), venv recovery (#14), Google OAuth files (#16), knowledge files for tools/MCP (#11)
- **Dependency upgrades:** browser-use 0.5.11→0.11.13, litellm 1.63.2→1.79.3, pypdf secure 6.7.5
- **Status:** 17 of 21 action items complete. Remaining: #5 (structured logging), #9 (health filter verify), #12 (invalid HTTP suppress), #17 (google_workspace MCP entry)

## In Progress

(none)

## Completed: Google Workspace MCP container and docs (2026-03-03)

- **Container:** Docker service `workspace_mcp` (container name `workspace_mcp`), port 8889, streamable-http; Agent Zero connects at `http://workspace_mcp:8889/mcp`.
- **Docs:** `docker/workspace-mcp/README.md`, `docs/setup/GOOGLE_WORKSPACE_MCP_CONTAINER.md`, `docs/guides/mcp-setup.md` (Option 2a/2b), `QUICK_REFERENCE.md`, `docs/DOCUMENTATION_INDEX.md`; Web UI examples and scripts/setup/README updated.
- **Archon:** If tracking in Archon, mark task done with: `python scripts/archon_api_tasks.py update <TASK_ID> --status done --description "Google Workspace MCP container + docs"`.

## Upcoming — ZeroClaw Integration (PRP-aligned)

Source: `PRPs/zeroclaw-integration-analysis.md` (Revised 2026-02-20)

### Phase 1: SQLite Hybrid Memory (5-8 days)
- [ ] Step 0: Extract `MemoryBackend` abstract interface from `python/helpers/memory.py` (FAISS tightly coupled)
- [ ] Build `python/helpers/memory_sqlite.py` — FTS5 + vector, implements `MemoryBackend`
- [ ] Settings toggle: `MEMORY_BACKEND=faiss|sqlite` (FAISS default)
- [ ] Migration tool: FAISS → SQLite export/import
- [ ] Update `MemoryConsolidator` to use backend-agnostic search
- [ ] Pytest tests for SQLite memory backend

### Phase 2: Security Enhancements (2-3 days)
- [ ] Encrypted secrets vault (replace plaintext `.env` for sensitive keys)
- [ ] MCP client pairing flow (one-time code exchange)
- [ ] Audit logging for tool executions

### Phase 3: Channel Bridge (2-3 days)
- [ ] Configure ZeroClaw channels (Telegram, Discord, or Slack)
- [ ] ZeroClaw → Agent Zero bridge via `/api_message_async` + `/api_message_status`
- [ ] Channel-specific context handling
- [ ] E2E test: Telegram → ZeroClaw → Agent Zero → response → Telegram

### Phase 4: Rust Tool Sidecar (1-2 days)
- [ ] Add ZeroClaw container to `docker-compose.yml`
- [ ] Configure ZeroClaw MCP server
- [ ] Add ZeroClaw as MCP tool provider in Agent Zero settings
- [ ] Test tool delegation (shell, file, git)

## Backlog

- Reconcile `docs/installation.md` (references upstream `agent0ai/agent-zero` image) with local build workflow
- Consider consolidating duplicate `QUICK_REFERENCE.md` (root vs docs/)
- Add explicit port note to `docs/NATIVE_INSTALLATION.md` (native uses 8000 vs Docker 8888)
- Review `docs/CLAUDE_CODE_INTEGRATION.md` for `install_security_tools.sh` vs `install_owasp_tools.sh` naming
- ~~Sync Archon tasks with PRP phases~~ (done via direct psql — MCP was down, synced via Supabase DB)

### Action items from IMPROVE.md

See **IMPROVE.md** → "Action items (suggested improvements)" for full list. Summary:

- [x] **#1** — WebSocket auth: log at DEBUG for pre-login (2026-03-04)
- [x] **#2** — OAuth: documented 404 expected in MCP_CLIENT_CONNECTION.md (2026-03-04)
- [x] **#3** — MCP SSE: documented GET-only in mcp-setup.md (2026-03-04)
- [x] **#4/#7** — Deps: browser-use 0.11.13, litellm 1.79.3; full 1.82.0 blocked (2026-03-04)
- [ ] **#5** — Log structure: structured logging or separate app vs HTTP streams
- [x] **#6** — code_execution: ast.parse validation (2026-03-04)
- [x] **#8** — Playwright: docs/troubleshooting/playwright_upgrade.md (2026-03-04)
- [ ] **#9** — Verify health filter in running image
- [x] **#10** — Google API in main venv: requirements.txt (2026-03-04)
- [x] **#11** — Knowledge files: mcp_servers.md, preinstalled_tools.md (2026-03-04)
- [ ] **#12** — Invalid HTTP request: suppress for known probes
- [x] **#13** — MCP context manager: mcp_server.py (2026-03-04)
- [x] **#14** — Venv recovery: docs/troubleshooting/venv_recovery.md (2026-03-04)
- [x] **#15** — Fluxbox config: docker/run/fs/root/.fluxbox/init (2026-03-03)
- [x] **#16** — Google OAuth docs: GOOGLE_OAUTH_FILES.md (2026-03-04)
- [ ] **#17** — google_workspace MCP: fix/remove entry
- [x] **#18** — MCP import: streamable_http_client (2026-03-03)
- [x] **#19** — Autocutsel timing: startsecs=3 (2026-03-04)
- [x] **#20** — Health filter bypass: _FilteredUvicornServer (2026-03-03)
- [x] **#21** — Log interleaving: stderr redirect (2026-03-03)
- [x] **#22** — Tool error streak: agent.py loop detection (2026-03-05)

## Discovered During Work

- `docs/archive/` contains 37 historical docs that are referenced nowhere in active docs — could be pruned
- `docs/troubleshooting/` has 14 files, many are single-fix notes — could be consolidated
