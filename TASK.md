# Task Log

## Completed

### 2026-03-03: Docker response-speed, status script, /health, Ollama repetition fix (Cursor)
- **Docker:** `shm_size: 512mb`, `memswap_limit: 16g` (service level), reservations 10G RAM / 3 CPUs, healthcheck `start_period: 30s`; container recreated.
- **Health:** No-auth `/health` route in `run_ui.py`; Docker healthcheck and `restart.sh` use `/health` (no 302s from curl).
- **Status:** `scripts/show_status.sh` prints container, health, Web UI, VNC, **Settings** (chat/util/browser from container), access URLs; `startup.sh` calls it at end; `MODELS.sh --status` runs same output.
- **Ollama repetition fix (RESPONSES.md follow-ups):** `scripts/ollama_create_modelfiles.sh` for glm-4.7-flash:32k (num_ctx 32768); presets ollama_glm, ollama_mixed, ollama_glm_claude use `glm-4.7-flash:32k` and per-preset kwargs (GLM frequency_penalty 1.45, ollama_claude 1.1, ollama_qwen3 temp 0.3). `agent.py`: LoopData.MAX_ITERATIONS=20, within-stream repetition detection (250-char block 3×), stream_repeat_detected handling.
- **Handoff:** `RESPONSES.md` — Claude ↔ Cursor coordination; Ollama section status set to "Cursor follow-up tasks complete".

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

## In Progress

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

## Discovered During Work

- `docs/archive/` contains 37 historical docs that are referenced nowhere in active docs — could be pruned
- `docs/troubleshooting/` has 14 files, many are single-fix notes — could be consolidated
