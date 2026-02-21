# Architecture

**Analysis Date:** 2025-02-20

## Pattern Overview

**Overall:** Agent-centric monolith with plugin-style extensions and tools, Flask web UI + ASGI mounts for MCP/A2A.

**Key Characteristics:**
- Single process: Flask WSGI app serves web UI and REST API; `/mcp` and `/a2a` are ASGI mounts (FastMCP, A2A).
- Agent runloop is async (monologue → message loop → LLM → tool parse/execute → extensions at named hooks).
- Tools and API handlers are discovered by scanning folders for subclasses of `Tool` and `ApiHandler`; extensions are loaded by extension-point folder name.
- Context is global (in-memory `AgentContext._contexts`); each context has one primary agent and optional streaming agent; tasks run in `DeferredTask` threads.

## Layers

**Entry / HTTP:**
- Purpose: Serve UI, REST API, MCP, and A2A.
- Location: `run_ui.py`, `python/api/*.py`, `python/helpers/mcp_server.py`, `python/helpers/fasta2a_server.py`
- Contains: Flask app, route registration, auth/CSRF decorators, `DispatcherMiddleware` for `/mcp` and `/a2a`, API handler discovery via `load_classes_from_folder("python/api", "*.py", ApiHandler)`.
- Depends on: `initialize`, `agent`, `python.helpers` (api, files, mcp_server, fasta2a_server, runtime, dotenv, process, login).
- Used by: Browser, MCP clients, A2A clients.

**Agent core:**
- Purpose: Context and agent lifecycle, message handling, monologue loop, prompt building, tool dispatch.
- Location: `agent.py`
- Contains: `AgentContext`, `AgentConfig`, `UserMessage`, `LoopData`, `Agent` (monologue, prepare_prompt, process_tools, get_tool, call_extensions), `InterventionException` / `HandledException`.
- Depends on: `models`, `python.helpers` (extract_tools, files, errors, history, tokens, context, dirty_json, defer, log, localization, extension, errors), `langchain_core` (prompts, messages).
- Used by: API handlers (via `use_context` and `communicate`), extensions, tools, MCP/A2A when delegating to agent.

**Extensions (hooks):**
- Purpose: Pluggable behaviour at fixed points (agent_init, monologue_start/end, message_loop_*, system_prompt, tool_execute_before/after, stream hooks, hist_add_*, etc.).
- Location: `python/extensions/<extension_point>/` and optionally `agents/<profile>/extensions/<extension_point>/`
- Contains: Subclasses of `Extension` from `python/helpers/extension.py`; loaded by `call_extensions(extension_point, agent, **kwargs)` which merges default and profile-specific extensions, then runs each `execute(**kwargs)`.
- Depends on: `agent`, `python.helpers` (files, extract_tools).
- Used by: `Agent` (and occasionally API flow, e.g. `user_message_ui`).

**Tools:**
- Purpose: Implement agent actions (code execution, memory, browser, search, response, etc.); can be local or MCP-backed.
- Location: `python/tools/*.py` and optionally `agents/<profile>/tools/*.py`
- Contains: Subclasses of `Tool` from `python/helpers/tool.py`; instantiated by `Agent.get_tool(name, method, args, message, loop_data)` which tries profile tool file then `python/tools/<name>.py`, else `Unknown`.
- Depends on: `agent`, `python/helpers` (e.g. shell, files, memory, settings).
- Used by: `Agent.process_tools` after parsing JSON tool request from LLM output; MCP tools via `python/helpers/mcp_handler.py` before local fallback.

**Models / LLM:**
- Purpose: Chat, utility, embedding, browser model config and invocation; LiteLLM + LangChain adapters.
- Location: `models.py`
- Contains: `ModelType`, `ModelConfig`, `get_chat_model`, `get_embedding_model`, `get_browser_model`, unified call with streaming/reasoning.
- Depends on: `python.helpers` (dotenv, settings, providers, rate_limiter, tokens, dirty_json, browser_use_monkeypatch), `litellm`, `langchain_core`, `sentence_transformers` (optional).
- Used by: `Agent` (get_chat_model, get_utility_model, get_browser_model, get_embedding_model), tools that call LLMs.

**Initialization / config:**
- Purpose: Build `AgentConfig` from settings, create initial contexts, start MCP and job loop.
- Location: `initialize.py`
- Contains: `initialize_agent`, `initialize_chats`, `initialize_mcp`, `initialize_job_loop`, `initialize_preload`, runtime/config overrides.
- Depends on: `agent`, `models`, `python.helpers` (runtime, settings, defer, persist_chat, mcp_handler, job_loop).
- Used by: `run_ui.py` (before/after server start: init_a0 → initialize_chats, initialize_mcp, initialize_job_loop, initialize_preload); API handlers that need config via context.

**Web UI:**
- Purpose: Static frontend (HTML/CSS/JS) and login; no separate build step in tree—served as static from Flask.
- Location: `webui/` (index.html, index.js, index.css, login.html, components/, js/, css/, public/, vendor/)
- Contains: Chat UI, projects, settings, messages, modals, etc.; placeholders replaced by server (e.g. version) in `serve_index`.
- Depends on: Backend API (e.g. `/message`, `/poll`, `/history_get`).
- Used by: User browser.

## Data Flow

**User message to agent response:**

1. HTTP POST to `/message` (or equivalent) → `python/api/message.py` `Message.process` → `use_context(ctxid)` → `context.communicate(UserMessage(...))`.
2. `AgentContext.communicate` either sets `intervention` on current agent or starts `DeferredTask` with `_process_chain(current_agent, msg)`.
3. `_process_chain`: `agent.hist_add_user_message(msg)` → `await agent.monologue()`; optional callback up to superior agent with result.
4. In `Agent.monologue`: loop over `message_loop_start` → `prepare_prompt` (system + history; `message_loop_prompts_before` / `message_loop_prompts_after`) → `call_chat_model` (streaming/reasoning callbacks through extensions) → `hist_add_ai_response` → `process_tools(agent_response)`.
5. `process_tools`: parse JSON tool request from message; resolve tool via MCP (`mcp_handler.get_tool`) or `get_tool(name, ...)` (profile then `python/tools/<name>.py`); run `tool_execute_before` → `tool.execute` → `tool_execute_after` → `tool.after_execution`; if `response.break_loop`, return message and exit loop.
6. Result flows back to API response or to superior in `_process_chain`; `last_result` / `last_error` on context for async poll.

**State management:**
- Contexts: `AgentContext._contexts` dict keyed by id; current context id in context vars via `python/helpers/context`.
- Per-context: `AgentContext.log`, `agent0`, `streaming_agent`, `task` (DeferredTask), `data` / `output_data`.
- Per-agent: `Agent.history`, `data`, `last_user_message`, `loop_data` (per iteration).
- Chats/persistence: `python/helpers/persist_chat` (tmp chats), `python/helpers/history` for in-memory history structure.

## Key Abstractions

**AgentContext:**
- Purpose: Isolated conversation/run environment; holds config, agent instance(s), log, task, and key-value data.
- Examples: `agent.py` (class and static get/use/current/set_current/remove/first/all).
- Pattern: Registry of contexts + context var for “current”; creation via constructor with optional `set_current`.

**Agent:**
- Purpose: One “agent” in a context; runs monologue loop, owns history, resolves and runs tools, calls extensions.
- Examples: `agent.py` (Agent class), `initialize.py` (config only; agent created when context is).
- Pattern: Config + context; tools and extensions loaded by name/folder; LLM via `models`.

**ApiHandler:**
- Purpose: One REST endpoint; POST handler with optional loopback, auth, API key, CSRF.
- Examples: `python/helpers/api.py` (base), `python/api/message.py`, `python/api/poll.py`, etc.
- Pattern: Subclass implements `process(input, request)`; `handle_request` does JSON/response and error formatting; registered in `run_ui.run()` from `load_classes_from_folder("python/api", "*.py", ApiHandler)`.

**Extension:**
- Purpose: Hook at a named extension point with access to agent and kwargs.
- Examples: `python/helpers/extension.py` (`call_extensions`, `Extension`), `python/extensions/*` and `agents/*/extensions/*`.
- Pattern: One folder per extension point; classes inheriting `Extension`; sorted by module name; default + profile merge.

**Tool:**
- Purpose: One invocable action (name, optional method, args) returning `Response(message, break_loop, additional)`.
- Examples: `python/helpers/tool.py` (`Tool`, `Response`), `python/tools/response.py`, `python/tools/code_execution_tool.py`, etc.
- Pattern: Resolved by name (and optional method); profile then `python/tools/<name>.py`; MCP can supply tool before local.

## Entry Points

**Web server:**
- Location: `run_ui.py` (`if __name__ == "__main__": runtime.initialize(); dotenv.load_dotenv(); run()`).
- Triggers: `python run_ui.py` (or equivalent).
- Responsibilities: Create Flask app, register API handlers from `python/api`, mount `/mcp` and `/a2a`, optional TLS, start WSGI server, then `init_a0()` (chats, MCP, job loop, preload).

**Agent runloop:**
- Location: `agent.py` (`Agent.monologue`).
- Triggers: `AgentContext.communicate` (or nudge) starts task that runs `_process_chain` → `agent.monologue()`.
- Responsibilities: Message loop, prompt build, LLM call, tool parsing and execution, extension hooks, history updates.

**MCP server:**
- Location: `python/helpers/mcp_server.py` (FastMCP app), mounted at `/mcp` in `run_ui.py`.
- Triggers: Requests to `/mcp` (e.g. SSE).
- Responsibilities: Expose tools (e.g. send_message) that delegate to AgentContext/agent; integrate with Cursor/other MCP clients.

**A2A server:**
- Location: `python/helpers/fasta2a_server.py`, mounted at `/a2a` in `run_ui.py`.
- Triggers: A2A protocol requests.
- Responsibilities: Agent-to-agent communication endpoint.

## Error Handling

**Strategy:** Critical path raises `HandledException` to stop loop; repairable path uses `RepairableException` and forwards to LLM; interventions use `InterventionException` to skip iteration without killing loop.

**Patterns:**
- `Agent.handle_critical_exception`: logs, prints, then raises `HandledException` (or re-raises for `HandledException`/`CancelledError`).
- `process_tools`: tool not found or init failure → hist_add_warning and log; no valid JSON tool request → hist_add_warning (misformat).
- API: `ApiHandler.handle_request` catches exception, returns 500 with `format_error(e)`.
- Extensions/tools: exceptions propagate to agent or task runner unless caught inside extension/tool.

## Cross-Cutting Concerns

**Logging:** `AgentContext.log` (Log instance); `PrintStyle` for console; extensions and tools use context log and PrintStyle.

**Validation:** Request/input in API handlers (e.g. JSON/form); tool args from LLM parsed as JSON (dirty_json); Pydantic in MCP/FastMCP models.

**Authentication:** Session-based for UI (`requires_auth`, login_handler); optional API key (`requires_api_key`); loopback-only for some handlers (`requires_loopback`); CSRF via `csrf_protect` where auth required.

---

*Architecture analysis: 2025-02-20*
