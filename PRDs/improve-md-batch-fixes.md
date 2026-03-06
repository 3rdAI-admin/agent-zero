# Product Requirements Document (PRD)

**Product / Feature:** Agent Zero – IMPROVE.md Batch Fixes (Logging, Documentation, Reliability)
**Version:** 1.0
**Date:** 2026-03-04
**Status:** Draft

---

## 1. Overview

### 1.1 Purpose
Address 15 improvement opportunities identified in `IMPROVE.md` (action items #1–#19, excluding completed items #4, #18, #20, #21) to improve Agent Zero's observability, reliability, documentation, and user experience. These fixes span logging hygiene, API documentation, code execution robustness, dependency management, MCP protocol compliance, and UI polish.

### 1.2 Goals
- **Reduce log noise** by downgrading non-actionable warnings and separating concerns (app vs HTTP vs system).
- **Improve documentation** for OAuth, MCP, Google APIs, and Playwright to reduce setup friction and agent confusion.
- **Harden code execution** by buffering/validating streamed code and documenting venv recovery.
- **Upgrade dependencies** (LiteLLM, Google API client) for better reliability and maintainability.
- **Polish supervisor config** (fluxbox, autocutsel) to eliminate restart loops and log spam.
- **Ensure MCP compliance** (context managers, correct server URLs).

### 1.3 Non-Goals
- **NOT** adding new features (e.g. new tools, new MCP servers, new agent capabilities).
- **NOT** refactoring core agent loop or memory system (reserved for separate PRD).
- **NOT** fixing upstream issues (faiss/numpy deprecations are tracked but deferred to upstream).

---

## 2. Background & Problem

### 2.1 Problem Statement
After extensive monitoring (2026-02-18 through 2026-03-03), 15 improvement opportunities were identified across logging, documentation, and reliability:
- **Log noise:** WebSocket auth failures, invalid HTTP requests, fluxbox crashes generate hundreds of non-actionable WARNING lines per session.
- **Missing docs:** OAuth well-known endpoint (404), MCP SSE method restrictions (405), Google OAuth credential files, Playwright re-install after upgrades all cause user confusion or wasted agent turns.
- **Code execution fragility:** Streamed code can be truncated mid-expression (SyntaxError); agent retries endlessly. Corrupted project venvs break Google API workflows.
- **Dependency lag:** LiteLLM unawaited coroutine warning; Google API client missing from main venv forces agent to guess project venv paths.
- **MCP protocol issues:** Notifications sent outside context managers (warnings); incorrect google_workspace URL (ExceptionGroup on every startup).
- **Supervisor noise:** fluxbox restart loop (258 lines/startup), autocutsel race condition with xvfb.

### 2.2 User / Stakeholder
- **Primary users:** Developers running Agent Zero in Docker who monitor logs, integrate MCP clients (Cursor), and use Google APIs / Playwright.
- **Stakeholders:** Operations teams monitoring container health; new contributors following setup docs; agent itself (knowledge files reduce wasted turns).

---

## 3. Requirements

### 3.1 Functional Requirements

#### Batch 1: Logging & Observability
| ID | Requirement | Source | Priority |
|----|-------------|--------|----------|
| FR-1.1 | Downgrade WebSocket "session not valid" log from WARNING to DEBUG when request has no session cookie (expected for unauthenticated clients). | IMPROVE.md #1 | Should |
| FR-1.2 | Implement structured logging (JSON with `logger`, `source`, `level` fields) or separate app logs (stderr) from HTTP access logs (stdout/file) for easier filtering. | IMPROVE.md #5 | Should |
| FR-1.3 | Suppress or downgrade uvicorn "Invalid HTTP request received" to DEBUG when from healthcheck probe (no valid HTTP headers). | IMPROVE.md #12 | Could |

#### Batch 2: API Documentation & Standards
| ID | Requirement | Source | Priority |
|----|-------------|--------|----------|
| FR-2.1 | Add `/.well-known/oauth-authorization-server` endpoint returning JSON metadata (if OAuth is desired for MCP clients) OR document in MCP_CLIENT_CONNECTION.md that 404 is expected and OAuth is not implemented. | IMPROVE.md #2 | Could |
| FR-2.2 | Document in `docs/MCP_CLIENT_CONNECTION.md` or inline comment that MCP SSE endpoints are GET-only. Optionally return 405 with `Allow: GET` header on POST requests. | IMPROVE.md #3 | Could |

#### Batch 3: Code Execution & Tool Reliability
| ID | Requirement | Source | Priority |
|----|-------------|--------|----------|
| FR-3.1 | Buffer or validate complete code in `code_execution_tool` before execution to avoid truncated stream SyntaxErrors. Log warning if code appears incomplete (e.g. unclosed parens, mid-string). | IMPROVE.md #6 | Should |
| FR-3.2 | Verify `knowledge/main/google_apis.md` recall in next Drive-related agent session (test: ask agent to list Drive files and confirm it uses Drive API, not Gmail). | IMPROVE.md #6 | Must (verification) |
| FR-3.3 | Upgrade LiteLLM to latest version (>=1.85.0 as of 2026-03-04); monitor logs for unawaited coroutine warning. If warning persists, file upstream issue. | IMPROVE.md #7 | Should |
| FR-3.4 | Document in `docs/troubleshooting/` or `docs/guides/` how to recover from corrupted project venv (symptom: "null bytes error" when invoking venv Python). Steps: remove venv dir, recreate via `python3 -m venv`, reinstall requirements. | IMPROVE.md #14 | Should |
| FR-3.5 | Add note to Playwright docs (`docs/guides/playwright.md` or inline in `run_ui.py` / tool docstring) that `playwright install chromium` must be re-run after Playwright pip upgrades (version mismatch). Optionally add startup check that compares pip version to installed browser version and logs warning. | IMPROVE.md #8 | Should |

#### Batch 4: Dependencies & Environment
| ID | Requirement | Source | Priority |
|----|-------------|--------|----------|
| FR-4.1 | Add `google-auth` and `google-api-python-client` to main venv (`requirements.txt`) so `code_execution_tool` with `runtime: "python"` can run Drive/Gmail snippets without project venv. OR document in `knowledge/main/google_apis.md` that project venv is always required. | IMPROVE.md #10 | Should (choose one approach) |
| FR-4.2 | Create additional knowledge files (e.g. `knowledge/main/mcp_servers.md`, `knowledge/main/preinstalled_tools.md`) documenting available MCP servers and container tools so agent doesn't recreate them. | IMPROVE.md #11 | Could |

#### Batch 5: MCP Protocol Compliance
| ID | Requirement | Source | Priority |
|----|-------------|--------|----------|
| FR-5.1 | Ensure MCP notifications (e.g. `notifications/cancelled` on timeout) are sent inside `async with` context manager for `RequestResponder`. Fix in `mcp_server.py` or report upstream to fastmcp/mcp. | IMPROVE.md #13 | Should |
| FR-5.2 | Fix or remove `google_workspace` MCP entry in default user settings. Current URL (`http://host.docker.internal:8000/mcp`) points to PCI-ASSISTANT (SSL). Either start actual workspace-mcp server, update URL to correct port/scheme, or comment out entry with explanation. | IMPROVE.md #17 | Must |

#### Batch 6: UI/UX Polish
| ID | Requirement | Source | Priority |
|----|-------------|--------|----------|
| FR-6.1 | Add minimal `~/.fluxbox/init` config so fluxbox doesn't exit on missing session.* keys. OR set `autostart=false` in supervisor and document that fluxbox starts on first VNC connect. | IMPROVE.md #15 | Should |
| FR-6.2 | Add `depends_on=xvfb` to autocutsel in supervisor config, or increase `startsecs` from 0 to 3 so supervisor waits for display before marking RUNNING. | IMPROVE.md #19 | Should |
| FR-6.3 | Clarify in `knowledge/main/google_apis.md` or `docs/guides/GMAIL_OAUTH_SETUP.md` that `token.json` holds runtime tokens (refresh_token, access_token) and `credentials.json` holds OAuth client metadata (client_id, client_secret). | IMPROVE.md #16 | Should |

### 3.2 Non-Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | All fixes must pass existing validation gates (P1–P5: lint, types, style, tests, E2E). | Must |
| NFR-2 | No new secrets hardcoded; use `.env` or document in knowledge files. | Must |
| NFR-3 | Code style: Python (Black, Ruff), type hints where applicable, files under 500 lines. | Should |
| NFR-4 | Existing tests must pass; add new tests for buffered code validation (FR-3.1) if feasible. | Should |
| NFR-5 | Dependency upgrades (LiteLLM, Google API) must not break existing Ollama/OpenAI/Anthropic tool execution. | Must |

### 3.3 Success Criteria
- [ ] Log sample (200 lines, 90s window) shows DEBUG-level or absent WebSocket/invalid-HTTP warnings (not WARNING).
- [ ] Structured logging or log separation allows `grep 'source: app'` to filter agent reasoning without HTTP noise.
- [ ] OAuth well-known endpoint returns JSON or `docs/MCP_CLIENT_CONNECTION.md` states 404 is expected.
- [ ] MCP SSE 405 includes `Allow: GET` header or docs explain GET-only.
- [ ] Agent uses Drive API (not Gmail) when asked to list Drive files (knowledge recall verification).
- [ ] Streamed code with unclosed parens logged as warning; execution deferred until valid or timeout.
- [ ] LiteLLM upgraded; no unawaited coroutine warning in logs after 90s run.
- [ ] Playwright upgrade docs added; startup check logs warning if browser version mismatches pip package.
- [ ] Main venv has Google API client OR `google_apis.md` documents project venv requirement.
- [ ] `knowledge/main/mcp_servers.md` exists and agent recalls available servers when asked.
- [ ] MCP notifications use context manager; no `RequestResponder must be used as a context manager` warning.
- [ ] `google_workspace` MCP entry fixed/removed; no ExceptionGroup on startup.
- [ ] fluxbox RUNNING without restart loop; no `session.*` errors in logs.
- [ ] autocutsel RUNNING on first try; no BACKOFF → FATAL cascade.
- [ ] `google_apis.md` or `GMAIL_OAUTH_SETUP.md` clarifies token.json vs credentials.json.

---

## 4. Scope & Constraints

### 4.1 In Scope
- Logging configuration changes (`run_ui.py`, supervisor configs, uvicorn log level/handler).
- Documentation updates (`docs/MCP_CLIENT_CONNECTION.md`, `docs/troubleshooting/`, `knowledge/main/google_apis.md`, `knowledge/main/mcp_servers.md`).
- Code changes to `code_execution_tool.py` (buffer validation), `mcp_server.py` (context manager), `.mcp.json` / user settings (google_workspace).
- Dependency upgrades (`requirements.txt`: LiteLLM, google-auth, google-api-python-client).
- Supervisor config polish (`docker/run/fs/etc/supervisor/conf.d/vnc.conf`: fluxbox init, autocutsel depends_on).
- Playwright startup check (optional: version mismatch warning).
- OAuth well-known endpoint (if chosen) or MCP docs clarification.

### 4.2 Out of Scope
- New features (new tools, new MCP servers, new agent capabilities).
- Refactoring agent loop, memory consolidation, or context management (separate PRD).
- Upstream fixes (faiss/numpy deprecations tracked but not fixed here).
- Comprehensive structured logging migration (FR-1.2 is "consider" / "opportunistic"; full migration is future work).

### 4.3 Constraints & Assumptions
- **Constraints:** Must maintain backward compatibility with existing projects, memory, and tool execution. Must pass all validation gates (P1–P5).
- **Assumptions:** LiteLLM >=1.85.0 has unawaited coroutine fix (or warning is benign). Google API client in main venv does not conflict with project-specific venvs. Fluxbox config and autocutsel timing fixes do not break VNC in any environment.

---

## 5. Implementation Phases (Suggested)

### Phase 1: Logging & Observability (2–3 days)
- FR-1.1: Downgrade WebSocket auth log to DEBUG
- FR-1.3: Suppress invalid HTTP log or downgrade to DEBUG
- FR-1.2: (Optional) Structured logging or log separation (if time permits; defer to Phase 6 if complex)
- **Deliverable:** Log noise reduced by ~80%; `docker logs agent-zero --tail 200` shows mostly agent reasoning and tool output.

### Phase 2: API Documentation (1 day)
- FR-2.1: OAuth well-known endpoint or MCP docs clarification
- FR-2.2: MCP SSE GET-only documentation + 405 `Allow` header
- **Deliverable:** `docs/MCP_CLIENT_CONNECTION.md` updated; no user confusion about 404/405.

### Phase 3: Code Execution & Tool Reliability (3–4 days)
- FR-3.1: Buffer/validate code in `code_execution_tool`
- FR-3.2: Verify knowledge recall (test Drive API usage)
- FR-3.3: Upgrade LiteLLM, monitor logs
- FR-3.4: Document venv recovery in troubleshooting
- FR-3.5: Playwright upgrade docs + optional startup check
- **Deliverable:** No more SyntaxError loops from truncated code; LiteLLM warning gone; recovery docs available.

### Phase 4: Dependencies & Knowledge (1–2 days)
- FR-4.1: Add Google API client to main venv OR document project venv requirement
- FR-4.2: Create `mcp_servers.md` and `preinstalled_tools.md` knowledge files
- **Deliverable:** Agent can run Drive snippets without guessing venv paths; agent recalls available MCP servers.

### Phase 5: MCP Protocol & Config (1 day)
- FR-5.1: Fix MCP notification context manager (or file upstream issue)
- FR-5.2: Fix/remove `google_workspace` MCP entry
- **Deliverable:** No MCP warnings on startup; all configured servers connect or are documented as disabled.

### Phase 6: UI/UX Polish (1–2 days)
- FR-6.1: fluxbox config or autostart=false
- FR-6.2: autocutsel `depends_on=xvfb` or `startsecs` increase
- FR-6.3: Clarify token.json vs credentials.json in docs/knowledge
- **Deliverable:** VNC services stable on first boot; no fluxbox/autocutsel restart loops; Google OAuth docs clear.

**Total estimate:** 9–13 days (single developer); can parallelize Phases 1+2, 3+4, 5+6 if multiple contributors.

---

## 6. Acceptance Criteria (Test Plan)

### Pre-implementation
- [ ] Run `/validate-project --thorough` — all gates pass (baseline)
- [ ] Capture `docker logs agent-zero --tail 500` — count WARNING lines (baseline: ~50–100 in 90s window)

### Post-Phase 1 (Logging)
- [ ] Run 90s monitor; count WARNING lines for WebSocket/invalid-HTTP — expect <5 (was ~20+)
- [ ] `docker logs agent-zero --tail 200 | grep -i warning | wc -l` — expect <10 (was ~40)

### Post-Phase 2 (API Docs)
- [ ] `curl http://localhost:8888/.well-known/oauth-authorization-server` — returns JSON OR `docs/MCP_CLIENT_CONNECTION.md` states 404 expected
- [ ] `curl -X POST http://localhost:8888/mcp/.../sse` — returns 405 with `Allow: GET` OR docs explain GET-only

### Post-Phase 3 (Code Execution)
- [ ] Ask agent: "List files in this Google Drive folder: https://drive.google.com/drive/folders/..." — agent uses `build('drive', 'v3')`, not `build('gmail', 'v1')`
- [ ] Inject truncated code via manual test (e.g. `code_execution_tool` with `print("hello` incomplete) — tool logs warning, defers execution
- [ ] `docker logs agent-zero | grep -i "unawaited coroutine"` — no matches after LiteLLM upgrade
- [ ] `docs/troubleshooting/venv_recovery.md` exists and includes null-bytes recovery steps
- [ ] Upgrade Playwright pip package (if available) — startup log warns "browser version mismatch" OR docs state re-run `playwright install chromium`

### Post-Phase 4 (Dependencies)
- [ ] Agent uses `runtime: "python"` for Drive API snippet — succeeds without project venv (if main venv approach chosen) OR `google_apis.md` states project venv required
- [ ] Ask agent: "What MCP servers are available?" — agent recalls archon, crawl4ai_rag from `mcp_servers.md`

### Post-Phase 5 (MCP)
- [ ] `docker logs agent-zero | grep "RequestResponder must be used as a context manager"` — no matches
- [ ] `docker logs agent-zero | grep "google_workspace.*ExceptionGroup"` — no matches on startup

### Post-Phase 6 (UI/UX)
- [ ] `docker logs agent-zero | grep "fluxbox.*exited.*exit status 1"` — no matches in first 5 min
- [ ] `docker logs agent-zero | grep "autocutsel.*BACKOFF"` — no matches in first 2 min
- [ ] `knowledge/main/google_apis.md` or `docs/guides/GMAIL_OAUTH_SETUP.md` includes "token.json vs credentials.json" section

### Final validation
- [ ] Run `/validate-project --thorough` — all gates pass (P1–P5 green)
- [ ] 90s monitor run — CPU <10%, no FATAL, no MCP timeout, <10 WARNING lines total
- [ ] E2E smoke test: ask agent to (1) list Drive files, (2) crawl a URL (crawl4ai_rag), (3) create an Archon task — all succeed

---

## 7. References & Context

- **Source:** [IMPROVE.md](../IMPROVE.md) — monitoring log from 2026-02-18 through 2026-03-03
- **Action items:** Lines 350–378 (table)
- **Completed (not in scope here):** #0 (ipython), #4 (partial: pathspec/litellm), #9 (Starlette assertion), #10 (xvfb), #18 (MCP import), #20 (health filter), #21 (log interleaving), #22 (tool error streak)
- **Related docs:**
  - [docs/MCP_CLIENT_CONNECTION.md](../docs/MCP_CLIENT_CONNECTION.md)
  - [docs/troubleshooting/](../docs/troubleshooting/)
  - [knowledge/main/google_apis.md](../knowledge/main/google_apis.md)
  - [PLANNING.md](../PLANNING.md)
  - [TASK.md](../TASK.md)
- **Validation:** [.claude/commands/validate-project.md](../.claude/commands/validate-project.md)

---

## 8. Approval & Next Steps

### Approval Checklist
- [ ] User (james@th3rdai.com) reviews PRD scope and priorities
- [ ] Confirm phasing: sequential (Phases 1→6) or parallel batches (1+2, 3+4, 5+6)?
- [ ] Confirm LiteLLM upgrade strategy: upgrade and monitor, or upgrade + pin version if stable?
- [ ] Confirm Google API approach: main venv (easier for agent) or project venv only (cleaner isolation)?
- [ ] Confirm OAuth well-known: implement endpoint or document 404 expected?

### Next Steps
1. **Review this PRD** — adjust priorities, phasing, or scope as needed
2. **Run `/generate-prp PRDs/improve-md-batch-fixes.md`** — create execution plan (PRP) with multi-agent task breakdown
3. **Run `/execute-prp PRPs/improve-md-batch-fixes.md`** — implement in phases or parallel batches
4. **Run `/validate-project --thorough`** — verify all gates pass after each phase
5. **Update IMPROVE.md** — check off completed action items, update monitoring notes
6. **Commit** — atomic commits per phase or logical batch

---

**Prepared by:** Claude Code (claude-sonnet-4-5)
**Date:** 2026-03-04
**Status:** Draft — awaiting user approval
