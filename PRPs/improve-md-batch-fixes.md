# PRP: IMPROVE.md Batch Fixes - Logging, Documentation, Reliability

**Based on:** PRDs/improve-md-batch-fixes.md  
**Created:** 2026-03-04  
**Revised:** 2026-03-06 (per `/generate-prp`; no $ARGUMENTS — source PRD used. Line refs and Task 1 status updated.)  
**Confidence Score:** 8/10 (comprehensive context, clear patterns, executable validation)

---

## Goal

Implement 15 improvement opportunities from `IMPROVE.md` to reduce log noise by ~80%, improve documentation clarity, harden code execution, upgrade dependencies, and polish supervisor configuration. End state: Clean logs (< 10 WARNING lines per 90s window), zero MCP startup errors, no supervisor crash loops, and comprehensive knowledge/troubleshooting docs.

## Why

- **Observability**: Log noise (200+ WARNING lines per session) masks real issues; developers waste time filtering spam.
- **Reliability**: Truncated code execution causes infinite SyntaxError loops (CPU spikes to 1143%); MCP protocol violations block tool usage.
- **Onboarding**: Missing docs (OAuth, Playwright, venv recovery) force users to trial-and-error or waste agent turns recreating solutions.
- **Maintainability**: Dependency lag (LiteLLM unawaited coroutines, outdated Google API client) creates tech debt.
- **User Impact**: 258 X11 failure lines per startup (already fixed), 20+ health check log lines per 10 min (reduces journal usability).

## What

Implement fixes across 6 batches:

1. **Logging & Observability** (FR-1.1–1.3): Downgrade WebSocket/invalid-HTTP warnings to DEBUG; separate app/HTTP streams.
2. **API Documentation** (FR-2.1–2.2): Document OAuth well-known 404 expected; MCP SSE GET-only with 405 `Allow` header.
3. **Code Execution & Tools** (FR-3.1–3.5): Buffer/validate code before execution; verify Drive API knowledge; upgrade LiteLLM; document venv recovery, Playwright re-install.
4. **Dependencies & Knowledge** (FR-4.1–4.2): Add Google API client to main venv; create MCP/tools knowledge files.
5. **MCP Protocol** (FR-5.1–5.2): Fix notification context manager; remove/fix google_workspace MCP entry.
6. **UI/UX Polish** (FR-6.1–6.3): Add fluxbox minimal config; fix autocutsel timing; clarify token.json vs credentials.json.

### Success Criteria

- [ ] Log sample (200 lines, 90s window) shows <10 WARNING lines (was 40+)
- [ ] WebSocket "session not valid" logged at DEBUG (not WARNING)
- [ ] Agent uses Drive API (not Gmail) when asked to list Drive files
- [ ] Code execution detects incomplete code (unclosed parens), logs warning, defers execution
- [ ] LiteLLM >=1.85.0 installed; no "unawaited coroutine" in logs
- [ ] MCP notifications use context manager; no "RequestResponder must be used" warning
- [ ] google_workspace MCP entry fixed/removed; no ExceptionGroup on startup
- [ ] fluxbox/autocutsel RUNNING on first boot; no restart loop in logs
- [ ] docs/troubleshooting/venv_recovery.md exists with null-bytes fix
- [ ] knowledge/main/mcp_servers.md and preinstalled_tools.md created
- [ ] All validation gates pass (ruff, mypy, pytest, E2E)

---

## All Needed Context

### Documentation & References

```yaml
MUST READ:
  - file: run_ui.py:405-430
    why: WebSocket auth failure logging (PrintStyle.debug vs PrintStyle.warning)
    critical: FR-1.1 DONE — no session → DEBUG, session not valid → WARNING (lines 419-426)

  - file: python/tools/code_execution_tool.py:74-101
    why: Python/nodejs/terminal runtime routing; execute_python_code is where buffering/validation should happen
    critical: Code passed as `self.args["code"]` string; no validation before shlex/exec

  - file: python/helpers/mcp_server.py:98-150
    why: MCP tool send_message implementation; notifications may be sent outside context manager
    gotcha: FastMCP notifications must use `async with ctx.request_responder()` or trigger warning

  - file: docker/run/fs/etc/supervisor/conf.d/vnc.conf:47-62
    why: fluxbox supervisor config; currently startsecs=0 so every exit is unexpected
    pattern: Add minimal ~/.fluxbox/init or set depends_on=xvfb or increase startsecs to 3

  - file: knowledge/main/google_apis.md
    why: Existing knowledge file pattern; same structure for mcp_servers.md and preinstalled_tools.md
    pattern: Imperative title, "DO NOT recreate", specific paths, table of existing items

EXTERNAL DOCS:
  - url: https://github.com/madzak/python-json-logger
    why: python-json-logger for structured logging (if implementing FR-1.2 structured logs)
    section: JsonFormatter basic usage for uvicorn/app logs

  - url: https://github.com/BerriAI/litellm/releases
    why: Check latest LiteLLM version (>=1.85.0 recommended as of 2026-03-04)
    critical: Version 1.76.0+ has async cleanup fixes; check for .model_dump() deprecation fix

  - url: https://github.com/jlowin/fastmcp/issues/1753
    why: FastMCP RequestResponder context manager pattern for notifications/cancelled
    section: "Generated functions should accept ctx: Context and use `with ctx.request_responder() as rr:`"

  - url: https://wiki.archlinux.org/title/Fluxbox
    why: Fluxbox minimal config to prevent session.* errors
    section: ~/.fluxbox/init file with session.screen0.* defaults

  - url: https://docs.python.org/3/library/ast.html#ast.parse
    why: Python AST parsing for code validation (detect incomplete code, unclosed parens)
    critical: ast.parse() raises SyntaxError if code incomplete; can catch and defer execution
```

### Current Codebase Structure (Relevant Files)

```bash
run_ui.py                                      # WebSocket auth logging (line 380-387)
python/tools/code_execution_tool.py            # Code execution (execute_python_code at line 74)
python/helpers/mcp_server.py                   # MCP server send_message tool (line 98-150)
python/helpers/mcp_handler.py                  # MCP client handler
docker/run/fs/etc/supervisor/conf.d/vnc.conf   # Supervisor config for fluxbox/autocutsel
knowledge/main/google_apis.md                  # Knowledge file pattern (imperative, tables)
docs/guides/mcp-setup.md                       # MCP setup docs (where to add SSE GET-only note)
docs/troubleshooting/                          # Existing troubleshooting docs (14 files)
.mcp.json                                      # MCP server config (archon currently; google_workspace in user settings)
requirements.txt                               # Python dependencies (LiteLLM, Google API client)
```

### Desired Codebase Tree (Files to Add/Modify)

```bash
# NEW FILES
knowledge/main/mcp_servers.md                  # Document available MCP servers (archon, crawl4ai_rag)
knowledge/main/preinstalled_tools.md           # Document container tools (nmap, nikto, nuclei, etc)
docs/troubleshooting/venv_recovery.md          # Corrupted venv recovery (null bytes error)
docs/troubleshooting/playwright_upgrade.md     # Playwright browser version mismatch after pip upgrade
docs/guides/GOOGLE_OAUTH_FILES.md             # Clarify token.json vs credentials.json
docker/run/fs/root/.fluxbox/init               # Minimal fluxbox config (session.screen0.* defaults)

# MODIFIED FILES
run_ui.py                                      # Downgrade WebSocket auth log to DEBUG when no session
python/tools/code_execution_tool.py            # Buffer/validate code with ast.parse() before execution
python/helpers/mcp_server.py                   # Wrap notifications in RequestResponder context manager
docker/run/fs/etc/supervisor/conf.d/vnc.conf   # autocutsel: depends_on=xvfb or startsecs=3; fluxbox: use ~/.fluxbox/init
requirements.txt                               # Upgrade litellm>=1.85.0, add google-auth + google-api-python-client
.mcp.json                                      # Remove google_workspace OR document it's disabled
docs/guides/mcp-setup.md                       # Add note: "MCP SSE endpoints are GET-only; POST returns 405"
docs/MCP_CLIENT_CONNECTION.md                  # Add: "/.well-known/oauth-authorization-server not implemented; 404 expected"
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: PrintStyle.warning() vs PrintStyle.debug()
# Gotcha: WebSocket auth failure before login is EXPECTED; must check session presence first
# Pattern (run_ui.py:384-387):
if not session.get("authentication"):
    PrintStyle.debug("WebSocket auth failed (no session): expected for pre-login clients")
else:
    PrintStyle.warning("WebSocket auth failed: session not valid")

# CRITICAL: ast.parse() for Python code validation
# Gotcha: Truncated code raises SyntaxError with "unexpected EOF" or "incomplete input"
# Pattern:
import ast
try:
    ast.parse(code)
except SyntaxError as e:
    if "incomplete" in str(e) or "EOF" in str(e) or "unclosed" in str(e):
        PrintStyle.warning(f"Code appears incomplete: {e}; deferring execution")
        return "Code validation failed: incomplete syntax. Please provide complete code."
    raise  # Re-raise other SyntaxErrors (e.g. typos, which should be executed and fail normally)

# CRITICAL: FastMCP notifications MUST use async with ctx.request_responder()
# Gotcha: Sending notifications outside context manager triggers "RequestResponder must be used as a context manager" warning
# Pattern (from FastMCP issue #1753):
async def send_message(...):
    async with mcp_server.request_context() as ctx:  # Ensure context manager wraps entire operation
        async with ctx.request_responder() as rr:
            # Send notifications here
            await ctx.send_notification(...)
            # Execute tool logic
            result = await execute_tool()
            return result

# CRITICAL: Fluxbox session.* errors
# Gotcha: Fluxbox exits (code 1) on missing session config keys like session.screen0.toolbar.alpha
# Pattern: Create ~/.fluxbox/init with minimal defaults BEFORE first fluxbox start
# File: docker/run/fs/root/.fluxbox/init (will be copied into image)
session.screen0.toolbar.alpha: 255
session.screen0.slit.alpha: 255
session.screen0.menu.alpha: 255
session.autoRaiseDelay: 250
session.cacheMax: 200
session.cacheLife: 5

# CRITICAL: LiteLLM async cleanup
# Gotcha: Versions <1.76.0 have unawaited coroutine in GLOBAL_LOGGING_WORKER cleanup
# Fix: Upgrade to litellm>=1.85.0 (latest as of 2026-03-04)
# Verify: Check requirements.txt has litellm>=1.85.0; rebuild container after upgrade

# CRITICAL: Google API client in main venv vs project venv
# Decision: Add to requirements.txt so code_execution_tool with runtime="python" works for Drive/Gmail snippets
# Gotcha: If not in main venv, agent must guess project venv path (error-prone)
# Pattern: Add google-auth>=2.0.0 and google-api-python-client>=2.0.0 to requirements.txt
```

---

## Implementation Blueprint

### Phase 1: Logging & Observability (2–3 days)

**Data Models:**
No new models; configuration changes only.

**Files Modified:**
- `run_ui.py` (WebSocket auth logging)
- (Optional) Structured logging setup if implementing FR-1.2

**Approach:**
1. **FR-1.1**: Modify `run_ui.py:380-387` to check `session.get("authentication")` presence before logging. If session is None/empty, log at DEBUG; if session exists but invalid, log WARNING.
2. **FR-1.3**: (Optional, low priority) Suppress uvicorn "Invalid HTTP request" by checking log message content and downgrading to DEBUG. This is cosmetic; defer if time-constrained.
3. **FR-1.2**: (Optional, future work) Structured logging requires installing python-json-logger, configuring JsonFormatter for uvicorn.access and app loggers. Defer to Phase 6 if complex.

### Phase 2: API Documentation (1 day)

**Files Modified:**
- `docs/MCP_CLIENT_CONNECTION.md`
- `docs/guides/mcp-setup.md`
- (Optional) `run_ui.py` to add 405 handler with `Allow: GET` for SSE endpoints

**Approach:**
1. **FR-2.1**: Add section to `docs/MCP_CLIENT_CONNECTION.md`:
   ```markdown
   ## OAuth Well-Known Endpoint
   Agent Zero does not implement OAuth 2.0 authorization server metadata.
   The endpoint `/.well-known/oauth-authorization-server` returns 404 (expected).
   MCP clients (e.g. Cursor) should use API key authentication via `X-API-KEY` header.
   ```
2. **FR-2.2**: Add note to `docs/guides/mcp-setup.md` under "SSE Transport" section:
   ```markdown
   **Important**: MCP SSE endpoints are GET-only. POST requests return 405 Method Not Allowed.
   Configure your MCP client to use `type: "sse"` transport with GET method.
   ```
3. (Optional) Add 405 handler in `run_ui.py` or `mcp_server.py` to return `Allow: GET` header on POST to SSE endpoints.

### Phase 3: Code Execution & Tool Reliability (3–4 days)

**Files Modified:**
- `python/tools/code_execution_tool.py`
- `requirements.txt`
- `docs/troubleshooting/venv_recovery.md` (NEW)
- `docs/troubleshooting/playwright_upgrade.md` (NEW)

**Approach:**

**FR-3.1: Buffer/Validate Code**

Add validation to `execute_python_code()` before execution:

```python
# python/tools/code_execution_tool.py (add after line 74, before actual execution)
import ast

async def execute_python_code(self, code: str, session: int, reset: bool) -> str:
    # NEW: Validate code completeness before execution
    try:
        ast.parse(code)
    except SyntaxError as e:
        error_msg = str(e).lower()
        if any(kw in error_msg for kw in ["incomplete", "eof", "unclosed", "unexpected end"]):
            warning = f"Code appears incomplete (SyntaxError: {e}). Please provide complete code before execution."
            PrintStyle.warning(warning)
            return warning  # Return to agent; do not execute
        # For other SyntaxErrors (typos, invalid syntax), allow execution to fail normally
        # so agent sees real error message

    # Existing execution logic continues...
    await self.prepare_state(reset=reset, session=session)
    # ... rest of execute_python_code
```

**FR-3.2: Verify Knowledge Recall**

Manual test after Phase 4 (knowledge files created):
1. Start agent session
2. Ask: "List files in this Google Drive folder: https://drive.google.com/drive/folders/EXAMPLE"
3. Verify agent uses `build('drive', 'v3', credentials=creds)` NOT `build('gmail', 'v1', ...)`
4. If agent uses Gmail API, update `knowledge/main/google_apis.md` with more explicit warnings

**FR-3.3: Upgrade LiteLLM**

```bash
# requirements.txt
# Before:
# litellm>=1.82.0

# After:
litellm>=1.85.0  # Fixes async cleanup, unawaited coroutine in GLOBAL_LOGGING_WORKER
```

After container rebuild, verify:
```bash
docker logs agent-zero --tail 500 | grep -i "unawaited coroutine"
# Expected: No matches
```

**FR-3.4: Document Venv Recovery**

Create `docs/troubleshooting/venv_recovery.md`:

```markdown
# Corrupted Python Virtual Environment Recovery

## Symptom
- `code_execution_tool` fails with "null bytes error" when invoking venv Python
- Error: `bad magic number in <venv_path>/lib/python3.x/...`

## Root Cause
Project venv interpreter corrupted (disk I/O error, incomplete write, Docker restart mid-install).

## Fix
1. Remove corrupted venv directory:
   ```bash
   rm -rf /path/to/venv_dir
   ```

2. Recreate venv:
   ```bash
   python3 -m venv /path/to/venv_dir
   ```

3. Reinstall requirements:
   ```bash
   /path/to/venv_dir/bin/pip install -r requirements.txt
   ```

4. Test:
   ```bash
   /path/to/venv_dir/bin/python3 --version
   ```

## Prevention
- Use main venv (`/opt/venv-a0/bin/python3`) for Google API scripts instead of project venvs
- Add `google-auth` and `google-api-python-client` to main venv (see requirements.txt)
```

**FR-3.5: Playwright Upgrade Docs**

Create `docs/troubleshooting/playwright_upgrade.md`:

```markdown
# Playwright Browser Version Mismatch After Upgrade

## Symptom
- `crawl4ai_rag.crawl_website` fails with "Executable doesn't exist at /root/.cache/ms-playwright/chromium-XXXX/chrome-linux/chrome"
- Error occurs after `pip install --upgrade playwright` inside container

## Root Cause
Playwright pip package upgrades (e.g. 1.52.0 → 1.58.0) may require different browser binaries.
The volume-mounted browser directory (`./playwright-browsers`) has old chromium version.

## Fix
```bash
# Inside container:
playwright install chromium

# Or from host:
docker exec -it agent-zero playwright install chromium
```

## Prevention
- After upgrading Playwright pip package, always re-run `playwright install chromium`
- (Optional) Add startup check in `run_ui.py` to compare pip version to installed browser version
```

### Phase 4: Dependencies & Knowledge (1–2 days)

**Files Modified:**
- `requirements.txt`

**Files Created:**
- `knowledge/main/mcp_servers.md`
- `knowledge/main/preinstalled_tools.md`

**Approach:**

**FR-4.1: Google API Client in Main Venv**

```bash
# requirements.txt (add after existing google packages or at end)
google-auth>=2.35.0
google-api-python-client>=2.150.0
```

After rebuild, verify:
```bash
docker exec -it agent-zero /opt/venv-a0/bin/python3 -c "from googleapiclient.discovery import build; print('OK')"
# Expected: OK
```

**FR-4.2: Knowledge Files**

Create `knowledge/main/mcp_servers.md` (mirror pattern from google_apis.md):

```markdown
# Available MCP Servers — Already Configured

DO NOT create new MCP server entries or ask user to configure. The servers below are already set up.

## Connected MCP Servers

| Server | Type | URL | Tools | Status |
|--------|------|-----|-------|--------|
| archon | streamable-http | http://archon-mcp:8051/mcp | 14 tools (task management, Supabase integration) | Active |
| crawl4ai_rag | streamable-http | (configured in user settings) | 5 tools (web crawling, RAG) | Active |

## Archon Tools

- Task management: create_task, list_tasks, update_task, complete_task
- Database: query_supabase, insert_supabase, update_supabase
- Integration: sync_to_ide8, handoff_to_ide
- (Full list: 14 tools; see .mcp.json or user settings)

## Crawl4AI RAG Tools

- crawl_website: Fetch and parse web content
- extract_structured_data: Extract JSON from HTML
- (Full list: 5 tools; see MCP connection logs)

## Configuration

MCP server configuration is in:
- **System-wide**: `.mcp.json` (root of project; used by agent-zero)
- **User-specific**: `/a0/usr/settings.json` (per-user MCP servers)

## Important

- NEVER ask user to add new MCP server entries (they're already configured)
- NEVER recreate Archon/crawl4ai tools manually (use MCP tools instead)
- If MCP connection fails, check Docker network (agent-zero must join archon_app-network)
```

Create `knowledge/main/preinstalled_tools.md`:

```markdown
# Pre-Installed Tools in Agent Zero Container

DO NOT install these tools manually. They are already available in the container.

## Security & Penetration Testing

| Tool | Path | Purpose |
|------|------|---------|
| nmap | /usr/bin/nmap | Network scanner |
| nikto | /usr/bin/nikto | Web server vulnerability scanner |
| nuclei | /usr/local/bin/nuclei | Vulnerability scanner with templates |
| sqlmap | /usr/bin/sqlmap | SQL injection testing |
| gobuster | /usr/bin/gobuster | Directory/file brute-forcing |
| wpscan | /usr/bin/wpscan | WordPress vulnerability scanner |

## Development & Utilities

| Tool | Path | Purpose |
|------|------|---------|
| git | /usr/bin/git | Version control |
| docker | /usr/bin/docker | Container management (Docker-in-Docker) |
| curl | /usr/bin/curl | HTTP client |
| wget | /usr/bin/wget | File downloader |
| jq | /usr/bin/jq | JSON processor |
| python3 | /opt/venv-a0/bin/python3 | Python interpreter (main venv) |
| node | /usr/bin/node | Node.js runtime |

## Browser & Automation

| Tool | Path | Purpose |
|------|------|---------|
| chromium | /root/.cache/ms-playwright/chromium-*/chrome-linux/chrome | Playwright browser |
| firefox | (available via apt if needed) | Alternative browser |

## Important

- All tools are in PATH; use direct commands (e.g. `nmap -sV target.com`)
- For Playwright: Use `crawl4ai_rag` MCP tools or `code_execution_tool` with runtime="terminal"
- For Google APIs: Use main venv (`/opt/venv-a0/bin/python3`) or project venv (see knowledge/main/google_apis.md)
```

### Phase 5: MCP Protocol & Config (1 day)

**Files Modified:**
- `python/helpers/mcp_server.py`
- `.mcp.json` OR user settings file (if google_workspace entry exists)

**Approach:**

**FR-5.1: Fix Notification Context Manager**

Review `python/helpers/mcp_server.py:98-150` (send_message tool):
- If notifications are sent (e.g. on timeout/cancel), ensure they're wrapped in `async with ctx.request_responder() as rr:`
- Pattern from FastMCP issue #1753:

```python
# python/helpers/mcp_server.py (send_message tool)
async def send_message(...) -> Union[ToolResponse, ToolError]:
    # Get project name from context
    project_name = _mcp_project_name.get()

    # CRITICAL: Ensure entire operation is in request context
    async with mcp_server.request_context() as ctx:
        async with ctx.request_responder() as rr:
            try:
                # Initialize/get context
                context: AgentContext | None = ...

                # Execute message
                result = await context.send_message(...)

                # If timeout/cancel occurs, handle within this block
                return ToolResponse(status="success", response=result, chat_id=context.id)

            except asyncio.TimeoutError:
                # Send cancellation notification WITHIN context manager
                await ctx.send_notification(
                    method="notifications/cancelled",
                    params={"requestId": ..., "reason": "Request timed out"}
                )
                return ToolError(error="Request timed out", chat_id=chat_id)

            except Exception as e:
                return ToolError(error=str(e), chat_id=chat_id or "unknown")
```

**FR-5.2: Fix google_workspace MCP Entry**

Check if `.mcp.json` or `/a0/usr/settings.json` has `google_workspace` entry:

```bash
# If google_workspace exists in .mcp.json:
# Option 1: Remove it (cleanest)
{
  "mcpServers": {
    "archon": { ... }
    // "google_workspace": { ... }  <-- REMOVE this
  }
}

# Option 2: Comment out and document
{
  "mcpServers": {
    "archon": { ... }
    // "google_workspace": {
    //   "comment": "DISABLED: workspace-mcp server not running. To enable, start workspace-mcp on host:8889 and update URL below",
    //   "type": "streamable-http",
    //   "url": "http://workspace_mcp:8889/mcp"
    // }
  }
}
```

Verify after change:
```bash
docker logs agent-zero --tail 200 | grep "google_workspace.*ExceptionGroup"
# Expected: No matches
```

### Phase 6: UI/UX Polish (1–2 days)

**Files Created:**
- `docker/run/fs/root/.fluxbox/init`
- `docs/guides/GOOGLE_OAUTH_FILES.md`

**Files Modified:**
- `docker/run/fs/etc/supervisor/conf.d/vnc.conf`
- `docker/run/Dockerfile` (add COPY for .fluxbox/init)
- `Dockerfile` (add COPY for .fluxbox/init)

**Approach:**

**FR-6.1: Fluxbox Minimal Config**

Create `docker/run/fs/root/.fluxbox/init`:

```
session.screen0.toolbar.alpha: 255
session.screen0.slit.alpha: 255
session.screen0.menu.alpha: 255
session.screen0.toolbar.placement: TopCenter
session.screen0.slit.placement: RightBottom
session.autoRaiseDelay: 250
session.cacheMax: 200
session.cacheLife: 5
session.menuSearch: itemstart
```

Add to `docker/run/Dockerfile` and `Dockerfile` (after other fs/ copies):

```dockerfile
# Copy fluxbox minimal config to prevent session.* errors
COPY --chown=root:root docker/run/fs/root/.fluxbox/init /root/.fluxbox/init
# OR if using Dockerfile (not docker/run/Dockerfile):
COPY --chown=root:root fs/root/.fluxbox/init /root/.fluxbox/init
```

**FR-6.2: Autocutsel Timing Fix**

Modify `docker/run/fs/etc/supervisor/conf.d/vnc.conf`:

```ini
[program:autocutsel]
command=/usr/bin/autocutsel -selection CLIPBOARD
environment=DISPLAY=":99"
autostart=true
autorestart=true
priority=40
# Option 1: Add dependency on xvfb (cleanest)
depends_on=xvfb

# Option 2: Increase startsecs so supervisor waits for display before marking RUNNING
# startsecs=3
# startretries=10

stderr_logfile=/var/log/supervisor/autocutsel.err.log
stdout_logfile=/var/log/supervisor/autocutsel.out.log
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
```

Note: `depends_on` may require supervisord 4.0+. If unavailable, use `startsecs=3`.

**FR-6.3: Clarify token.json vs credentials.json**

Create `docs/guides/GOOGLE_OAUTH_FILES.md`:

```markdown
# Google OAuth Files Explained

## Two Separate Files

Google OAuth authentication uses **two distinct JSON files** with different purposes:

### credentials.json (OAuth Client Metadata)

- **Purpose**: Holds OAuth 2.0 client application metadata
- **Contents**:
  - `client_id`: Your OAuth app's client ID
  - `client_secret`: Your OAuth app's client secret
  - `redirect_uris`: Allowed redirect URLs (usually localhost for desktop apps)
- **Obtained from**: Google Cloud Console → APIs & Services → Credentials → Create OAuth 2.0 Client ID
- **Security**: Contains client secret; keep private but not as sensitive as token.json
- **Location in Agent Zero**: `/a0/usr/projects/a0_sip/credentials.json`

### token.json (Runtime Access Tokens)

- **Purpose**: Holds the actual access token and refresh token for API calls
- **Contents**:
  - `token` / `access_token`: Short-lived access token (expires in ~1 hour)
  - `refresh_token`: Long-lived refresh token (used to get new access tokens)
  - `expiry`: When the current access token expires (ISO 8601 timestamp)
  - `scopes`: Authorized scopes (gmail.send, drive, spreadsheets, etc.)
- **Obtained from**: First OAuth flow (user consent); automatically refreshed by client libraries
- **Security**: HIGHLY SENSITIVE; contains refresh token which grants long-term access
- **Location in Agent Zero**: `/a0/usr/projects/a0_sip/token.json`

## Common Confusion

- **"credentials file is missing refresh_token"**: This is expected. `credentials.json` NEVER has `refresh_token`; that's in `token.json`.
- **"token file is missing client_secret"**: This is expected. `token.json` NEVER has `client_secret`; that's in `credentials.json`.

## Workflow

1. Download `credentials.json` from Google Cloud Console
2. Run OAuth flow (e.g. `gmail_oauth.py`); user consents in browser
3. OAuth flow creates `token.json` with access token and refresh token
4. Use `token.json` for all API calls (client libraries auto-refresh when expired)
5. NEVER ask user to re-authenticate unless `token.json` is deleted or refresh token is revoked

## Agent Zero Locations

- **credentials.json**: `/a0/usr/projects/a0_sip/credentials.json`
- **token.json**: `/a0/usr/projects/a0_sip/token.json`
- **Account**: agentz@th3rdai.com
- **Scopes**: gmail.send, gmail.readonly, drive, spreadsheets, presentations, cloud-platform

See `knowledge/main/google_apis.md` for usage examples.
```

Update `knowledge/main/google_apis.md` (add reference at top):

```markdown
# Google API Integration — Already Configured

(Existing content...)

## OAuth Files

For details on `credentials.json` vs `token.json`, see [docs/guides/GOOGLE_OAUTH_FILES.md](../../docs/guides/GOOGLE_OAUTH_FILES.md).
```

---

## Multi-Agent Task Breakdown (Small Tasks for Accuracy)

```yaml
# Task ID | Scope | Assignable Unit | Acceptance | Est. Time
Task 1    | WebSocket auth logging downgrade          | Agent/Pass 1 | Log sample shows DEBUG for no-session cases       | 30 min
Task 2    | Code validation (ast.parse)               | Agent/Pass 2 | Incomplete code logged; execution deferred        | 1 hr
Task 3    | LiteLLM upgrade in requirements.txt       | Agent/Pass 3 | requirements.txt has litellm>=1.85.0              | 10 min
Task 4    | Venv recovery docs                        | Agent/Pass 4 | docs/troubleshooting/venv_recovery.md exists      | 30 min
Task 5    | Playwright upgrade docs                   | Agent/Pass 5 | docs/troubleshooting/playwright_upgrade.md exists | 30 min
Task 6    | Google API client in requirements.txt     | Agent/Pass 6 | Main venv can import googleapiclient.discovery    | 15 min
Task 7    | MCP servers knowledge file                | Agent/Pass 7 | knowledge/main/mcp_servers.md created             | 45 min
Task 8    | Preinstalled tools knowledge file         | Agent/Pass 8 | knowledge/main/preinstalled_tools.md created      | 45 min
Task 9    | MCP notification context manager fix      | Agent/Pass 9 | No "RequestResponder must be used" warning        | 1.5 hr
Task 10   | google_workspace MCP entry fix            | Agent/Pass 10 | No ExceptionGroup on startup                      | 15 min
Task 11   | Fluxbox minimal config                    | Agent/Pass 11 | ~/.fluxbox/init created; no session.* errors      | 1 hr
Task 12   | Autocutsel timing fix                     | Agent/Pass 12 | No autocutsel BACKOFF in logs                     | 30 min
Task 13   | Google OAuth files docs                   | Agent/Pass 13 | docs/guides/GOOGLE_OAUTH_FILES.md created         | 45 min
Task 14   | MCP SSE GET-only documentation            | Agent/Pass 14 | docs/guides/mcp-setup.md updated                  | 20 min
Task 15   | OAuth well-known endpoint docs            | Agent/Pass 15 | docs/MCP_CLIENT_CONNECTION.md updated             | 15 min
```

---

## List of Tasks (In Dependency Order)

### Task 1: WebSocket Auth Logging Downgrade (Phase 1) — DONE

**Status:** Already implemented in `run_ui.py:419-426` (no session → DEBUG, session not valid → WARNING). Skip implementation; run acceptance only if desired.

**MODIFY run_ui.py:405-430** (reference only; code already present)
- FIND pattern: `PrintStyle.warning(f"WebSocket authentication failed for {_namespace} {sid}: session not valid")`
- REPLACE with:
  ```python
  # Check if session exists before logging level decision
  if not session.get("authentication"):
      PrintStyle.debug(
          f"WebSocket authentication failed for {_namespace} {sid}: no session (expected for pre-login clients)"
      )
  else:
      PrintStyle.warning(
          f"WebSocket authentication failed for {_namespace} {sid}: session not valid"
      )
  ```
- PRESERVE: Existing auth flow logic (do not change return False or credentials check)

**Acceptance:**
```bash
# Start container, open browser (pre-login), trigger WebSocket connection
docker logs agent-zero --tail 100 | grep "WebSocket authentication failed"
# Expected: Line contains "DEBUG" or does not appear (filtered at DEBUG level)
```

---

### Task 2: Code Validation with ast.parse (Phase 3)

**MODIFY python/tools/code_execution_tool.py**
- FIND pattern: `async def execute_python_code(self, code: str, session: int, reset: bool) -> str:`
- INJECT after function start (before `await self.prepare_state`):
  ```python
  # Validate code completeness to prevent SyntaxError loops from truncated streams
  import ast
  try:
      ast.parse(code)
  except SyntaxError as e:
      error_msg = str(e).lower()
      incomplete_keywords = ["incomplete", "eof", "unclosed", "unexpected end"]
      if any(kw in error_msg for kw in incomplete_keywords):
          warning = f"Code appears incomplete (SyntaxError: {e}). Please provide complete code before execution."
          PrintStyle.warning(warning)
          return warning
      # For other SyntaxErrors (typos, invalid syntax), allow execution to fail normally
  ```
- PRESERVE: Existing prepare_state, shell execution, output handling

**Acceptance:**
```python
# Manual test: Create incomplete code snippet
test_code = 'print("hello'  # Missing closing quote and paren

# Execute via code_execution_tool
# Expected: Tool returns "Code appears incomplete..." without executing
# Logs show PrintStyle.warning with SyntaxError details
```

---

### Task 3: LiteLLM Upgrade (Phase 3)

**MODIFY requirements.txt**
- FIND pattern: `litellm>=1.82.0`
- REPLACE with: `litellm>=1.85.0`

**Acceptance:**
```bash
# Rebuild container
docker compose down && docker compose build --no-cache && docker compose up -d

# Verify version
docker exec -it agent-zero /opt/venv-a0/bin/pip show litellm | grep Version
# Expected: Version: 1.85.0 or higher

# Check logs for unawaited coroutine
docker logs agent-zero --tail 500 | grep -i "unawaited coroutine"
# Expected: No matches (or only pre-upgrade historical entries)
```

---

### Task 4: Venv Recovery Docs (Phase 3)

**CREATE docs/troubleshooting/venv_recovery.md**
- MIRROR pattern from: `docs/troubleshooting/VNC_TROUBLESHOOTING.md` (symptom, root cause, fix, prevention structure)
- CONTENT: See Phase 3 blueprint above (null bytes error recovery)

**Acceptance:**
```bash
# File exists
ls -lh docs/troubleshooting/venv_recovery.md
# Expected: File exists, ~1-2KB

# Content check
grep -i "null bytes error" docs/troubleshooting/venv_recovery.md
# Expected: Match found in Symptom section
```

---

### Task 5: Playwright Upgrade Docs (Phase 3)

**CREATE docs/troubleshooting/playwright_upgrade.md**
- MIRROR pattern from: `docs/troubleshooting/venv_recovery.md` (symptom, root cause, fix, prevention)
- CONTENT: See Phase 3 blueprint above (browser version mismatch)

**Acceptance:**
```bash
ls -lh docs/troubleshooting/playwright_upgrade.md
# Expected: File exists

grep -i "playwright install chromium" docs/troubleshooting/playwright_upgrade.md
# Expected: Match found in Fix section
```

---

### Task 6: Google API Client in Main Venv (Phase 4)

**MODIFY requirements.txt**
- FIND pattern: End of file or near existing google-* packages
- APPEND:
  ```
  google-auth>=2.35.0
  google-api-python-client>=2.150.0
  ```

**Acceptance:**
```bash
# Rebuild and verify
docker compose down && docker compose build --no-cache && docker compose up -d
docker exec -it agent-zero /opt/venv-a0/bin/python3 -c "from googleapiclient.discovery import build; print('OK')"
# Expected: OK
```

---

### Task 7: MCP Servers Knowledge File (Phase 4)

**CREATE knowledge/main/mcp_servers.md**
- MIRROR pattern from: `knowledge/main/google_apis.md` (imperative title, "DO NOT recreate", tables, specific paths)
- CONTENT: See Phase 4 blueprint above (archon, crawl4ai_rag documentation)

**Acceptance:**
```bash
ls -lh knowledge/main/mcp_servers.md
# Expected: File exists

grep -i "archon" knowledge/main/mcp_servers.md
# Expected: Table row with archon server details

# Verify agent recalls (manual test after file created)
# Ask agent: "What MCP servers are available?"
# Expected: Agent responds with archon and crawl4ai_rag (from knowledge file)
```

---

### Task 8: Preinstalled Tools Knowledge File (Phase 4)

**CREATE knowledge/main/preinstalled_tools.md**
- MIRROR pattern from: `knowledge/main/google_apis.md`
- CONTENT: See Phase 4 blueprint above (nmap, nikto, nuclei, etc.)

**Acceptance:**
```bash
ls -lh knowledge/main/preinstalled_tools.md
# Expected: File exists

grep -i "nmap\|nikto\|nuclei" knowledge/main/preinstalled_tools.md
# Expected: Table rows for security tools
```

---

### Task 9: MCP Notification Context Manager Fix (Phase 5)

**MODIFY python/helpers/mcp_server.py:98-150 (send_message tool)**
- FIND pattern: `async def send_message(...) -> Union[ToolResponse, ToolError]:`
- WRAP entire tool logic in `async with mcp_server.request_context() as ctx:` and `async with ctx.request_responder() as rr:`
- ENSURE: Any notifications (e.g. on timeout/cancel) are sent INSIDE the context manager
- MIRROR pattern from: FastMCP issue #1753 (see blueprint above)

**Acceptance:**
```bash
# Trigger timeout scenario (e.g. long-running agent task)
# Check logs for MCP warnings
docker logs agent-zero --tail 500 | grep "RequestResponder must be used as a context manager"
# Expected: No matches

# Verify MCP tools still work
# Test: Call send_message via MCP client (Cursor)
# Expected: Tool executes successfully; no warnings
```

---

### Task 10: google_workspace MCP Entry Fix (Phase 5)

**MODIFY .mcp.json OR /a0/usr/settings.json**
- FIND: `"google_workspace"` entry (if exists)
- OPTION 1: DELETE entry entirely
- OPTION 2: COMMENT OUT with explanation (see blueprint above)

**Acceptance:**
```bash
# Start container
docker compose up -d

# Check logs for google_workspace errors
docker logs agent-zero --tail 200 | grep "google_workspace.*ExceptionGroup"
# Expected: No matches

# Verify other MCP servers still work
docker logs agent-zero --tail 200 | grep "archon.*14 tools"
# Expected: Match found (archon loaded successfully)
```

---

### Task 11: Fluxbox Minimal Config (Phase 6)

**CREATE docker/run/fs/root/.fluxbox/init**
- CONTENT: See Phase 6 blueprint above (session.screen0.* defaults)

**MODIFY docker/run/Dockerfile**
- FIND pattern: `COPY --chown=root:root docker/run/fs/exe/` (or similar COPY for fs/)
- INJECT after:
  ```dockerfile
  # Copy fluxbox minimal config to prevent session.* errors
  COPY --chown=root:root docker/run/fs/root/.fluxbox/init /root/.fluxbox/init
  ```

**MODIFY Dockerfile (main Dockerfile if different from docker/run/Dockerfile)**
- SAME pattern as above (adjust path if needed)

**Acceptance:**
```bash
# Rebuild
docker compose down && docker compose build --no-cache && docker compose up -d

# Check logs for fluxbox errors
docker logs agent-zero --tail 500 | grep "fluxbox.*exited.*exit status 1"
# Expected: No matches

docker logs agent-zero --tail 500 | grep "Failed to read: session\."
# Expected: No matches
```

---

### Task 12: Autocutsel Timing Fix (Phase 6)

**MODIFY docker/run/fs/etc/supervisor/conf.d/vnc.conf**
- FIND pattern: `[program:autocutsel]`
- INJECT (choose option based on supervisord version):
  - **Option 1 (if supervisord 4.0+)**: Add `depends_on=xvfb` line
  - **Option 2 (if older)**: Change `startsecs=0` to `startsecs=3`

**Acceptance:**
```bash
# Rebuild and restart
docker compose down && docker compose build --no-cache && docker compose up -d

# Check logs for autocutsel BACKOFF
docker logs agent-zero --tail 500 | grep "autocutsel.*BACKOFF"
# Expected: No matches (or very few on first startup, then stable)

# Verify autocutsel is RUNNING
docker exec -it agent-zero supervisorctl status autocutsel
# Expected: autocutsel  RUNNING
```

---

### Task 13: Google OAuth Files Docs (Phase 6)

**CREATE docs/guides/GOOGLE_OAUTH_FILES.md**
- CONTENT: See Phase 6 blueprint above (explain credentials.json vs token.json)

**MODIFY knowledge/main/google_apis.md**
- FIND pattern: Top of file after title
- INJECT after "DO NOT recreate..." section:
  ```markdown
  ## OAuth Files
  For details on `credentials.json` vs `token.json`, see [docs/guides/GOOGLE_OAUTH_FILES.md](../../docs/guides/GOOGLE_OAUTH_FILES.md).
  ```

**Acceptance:**
```bash
ls -lh docs/guides/GOOGLE_OAUTH_FILES.md
# Expected: File exists, ~2-3KB

grep -i "credentials.json.*client_secret" docs/guides/GOOGLE_OAUTH_FILES.md
# Expected: Match in credentials.json section

grep -i "token.json.*refresh_token" docs/guides/GOOGLE_OAUTH_FILES.md
# Expected: Match in token.json section
```

---

### Task 14: MCP SSE GET-Only Documentation (Phase 2)

**MODIFY docs/guides/mcp-setup.md**
- FIND pattern: Section about SSE transport (search for "sse" or "transport")
- INJECT note:
  ```markdown
  **Important**: MCP SSE endpoints are GET-only. POST requests will return `405 Method Not Allowed`.
  Ensure your MCP client is configured to use `type: "sse"` transport with GET method.
  If you see 405 errors, check your client configuration.
  ```

**Acceptance:**
```bash
grep -i "SSE endpoints are GET-only" docs/guides/mcp-setup.md
# Expected: Match found

# Optional: Test 405 response
curl -X POST http://localhost:8888/mcp/EXAMPLE/sse
# Expected: 405 Method Not Allowed (or connection refused if endpoint doesn't exist)
```

---

### Task 15: OAuth Well-Known Endpoint Docs (Phase 2)

**MODIFY docs/MCP_CLIENT_CONNECTION.md**
- FIND pattern: Section about authentication or common errors
- INJECT new section:
  ```markdown
  ## OAuth Well-Known Endpoint (404 Expected)

  Agent Zero does not implement OAuth 2.0 authorization server metadata.
  The endpoint `/.well-known/oauth-authorization-server` returns 404 (this is expected).

  **For MCP Clients (e.g. Cursor):**
  - Use API key authentication via `X-API-KEY` header (see environment variables)
  - Do NOT configure OAuth; it is not supported
  - The 404 on `/.well-known/oauth-authorization-server` is normal and can be ignored
  ```

**Acceptance:**
```bash
grep -i "oauth-authorization-server.*404" docs/MCP_CLIENT_CONNECTION.md
# Expected: Match found in new section

# Test endpoint
curl http://localhost:8888/.well-known/oauth-authorization-server
# Expected: 404 Not Found (as documented)
```

---

## Validation Loop

### Level 1: Syntax & Style (Run After Each Task)

```bash
# Run from project root
ruff check --fix python/ run_ui.py
mypy python/ run_ui.py

# Expected: No errors
# If errors: READ the error message, understand root cause, fix code, re-run
```

### Level 2: Unit Tests (Run After Code Changes)

```bash
# Existing tests should still pass
uv run pytest tests/ -v -k "not test_debug_logging_respects_runtime_flag"

# Expected: All pass (except known pre-existing failure)
# If failing: Check if new code broke existing behavior; fix and re-run
```

### Level 3: Integration Test (Run After Container Rebuild)

```bash
# Rebuild container
docker compose down && docker compose build --no-cache && docker compose up -d

# Health check
curl http://localhost:8888/health
# Expected: {"status": "healthy"}

# Log sample (90s window)
sleep 90 && docker logs agent-zero --tail 200 > /tmp/agent-zero-logs.txt

# Check WARNING count
grep -i "warning" /tmp/agent-zero-logs.txt | wc -l
# Expected: <10 (was ~40 before fixes)

# Check specific fixes
grep "session not valid" /tmp/agent-zero-logs.txt | grep -i "debug"
# Expected: Match found (or no matches if DEBUG filtered by log level)

grep "RequestResponder must be used" /tmp/agent-zero-logs.txt
# Expected: No matches

grep "google_workspace.*ExceptionGroup" /tmp/agent-zero-logs.txt
# Expected: No matches

grep "fluxbox.*exited.*exit status 1" /tmp/agent-zero-logs.txt
# Expected: No matches
```

### Level 4: Manual Verification (Knowledge Recall)

```bash
# Start agent session via Web UI
# Test 1: Ask "What MCP servers are available?"
# Expected: Agent responds with archon and crawl4ai_rag from knowledge file

# Test 2: Ask "List files in this Google Drive folder: <EXAMPLE_URL>"
# Expected: Agent uses build('drive', 'v3', ...) NOT build('gmail', 'v1', ...)

# Test 3: Trigger incomplete code execution
# Paste in Web UI: code_execution_tool with code='print("hello'  # incomplete
# Expected: Tool returns "Code appears incomplete..." without executing
```

---

## Final Validation Checklist

- [ ] All tasks 1–15 completed
- [ ] `ruff check python/ run_ui.py` → No errors
- [ ] `mypy python/ run_ui.py` → No errors
- [ ] `uv run pytest tests/ -v` → 152/153 pass (1 pre-existing failure OK)
- [ ] Container rebuilds successfully: `docker compose build --no-cache`
- [ ] Health check passes: `curl http://localhost:8888/health` → 200
- [ ] Log sample (<10 WARNING in 90s window): `docker logs agent-zero --tail 200 | grep -i warning | wc -l`
- [ ] WebSocket auth logged at DEBUG (not WARNING) for pre-login clients
- [ ] No "RequestResponder must be used" warning in logs
- [ ] No google_workspace ExceptionGroup in logs
- [ ] No fluxbox/autocutsel restart loop in logs
- [ ] Knowledge files created: `ls knowledge/main/{mcp_servers,preinstalled_tools}.md`
- [ ] Troubleshooting docs created: `ls docs/troubleshooting/{venv_recovery,playwright_upgrade}.md`
- [ ] Google OAuth docs created: `ls docs/guides/GOOGLE_OAUTH_FILES.md`
- [ ] MCP/OAuth docs updated: `grep -i "GET-only\|404 expected" docs/guides/mcp-setup.md docs/MCP_CLIENT_CONNECTION.md`
- [ ] Agent recalls MCP servers when asked (manual test)
- [ ] Agent uses Drive API for Drive folder listing (manual test)
- [ ] Incomplete code execution deferred with warning (manual test)

---

## Anti-Patterns to Avoid

- ❌ Don't skip `ast.parse()` validation because "it might slow down execution" — SyntaxError loops are worse
- ❌ Don't log WebSocket auth failures at WARNING if session is None — that's expected for healthcheck/pre-login
- ❌ Don't send MCP notifications outside `async with ctx.request_responder()` — always use context manager
- ❌ Don't create new Google API venv patterns — add to main venv so code_execution_tool works
- ❌ Don't skip fluxbox config — missing session.* keys cause 258 log lines per startup
- ❌ Don't add google_workspace MCP entry without starting the server — causes ExceptionGroup on every boot
- ❌ Don't upgrade LiteLLM without verifying unawaited coroutine fix — check logs after rebuild
- ❌ Don't skip documentation tasks — knowledge files prevent agent from wasting turns recreating solutions

---

## Confidence Score: 8/10

**Strengths:**
- Comprehensive context (file paths, line numbers, existing patterns)
- Clear validation gates (executable commands)
- Small task breakdown (15 tasks, 15 min – 1.5 hr each)
- Real code snippets from codebase
- External docs for complex fixes (FastMCP, fluxbox, LiteLLM)

**Risks:**
- FastMCP context manager fix (Task 9) may require deeper understanding of fastmcp internals (1.5 hr estimate could expand to 3 hr)
- Structured logging (FR-1.2) deferred to future work; if required, add 2–3 days
- Knowledge recall verification (manual tests) depends on agent's retrieval accuracy

**Mitigation:**
- Task 9 can be validated incrementally (add context manager, test, adjust)
- Structured logging is optional (low priority)
- Knowledge files follow proven pattern (google_apis.md); high confidence in recall
