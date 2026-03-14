# Codebase Index — Agent Zero

**Last updated:** 2026-03-06  
**Purpose:** Quick reference to find entry points, APIs, tools, and structure. For full layout and conventions see [STRUCTURE.md](./STRUCTURE.md) and [ARCHITECTURE.md](./ARCHITECTURE.md).

## Entry points

| File | Role |
|------|------|
| `run_ui.py` | Web server entry; Flask app; mounts API, /mcp, /a2a; `init_a0()` |
| `agent.py` | Agent, AgentContext, monologue loop, tool dispatch (no direct CLI) |
| `initialize.py` | AgentConfig from settings; init chats, MCP, job loop |
| `models.py` | LLM config and invocation (LiteLLM, LangChain) |

## Top-level layout

```
├── agent.py, initialize.py, models.py, run_ui.py
├── prompts/           # Default prompt templates
├── agents/            # Profile overrides (agent0, developer, _example, …)
├── python/
│   ├── api/           # REST handlers (76 modules → POST /<name>)
│   ├── helpers/       # Shared utilities (api, defer, files, mcp_server, …)
│   ├── extensions/    # Extension points (22 hooks)
│   ├── tools/         # Default tools (18 + security/)
│   └── websocket_handlers/
├── webui/             # Frontend (index, login, components, js, css)
├── config/, conf/     # Example and runtime config
├── knowledge/, memory/, instruments/
├── docker/            # Build and run (base/, run/, workspace-mcp)
├── scripts/           # Setup, testing, maintenance
├── tests/             # Pytest
├── docs/              # Documentation
└── .planning/         # Planning, roadmap, codebase docs
```

## API modules (python/api/)

76 handlers; route = `POST /<module_name>`. Examples:

- **Chat:** `message.py`, `poll.py`, `history_get.py`, `chat_create.py`, `chat_load.py`, `chat_remove.py`, `chat_reset.py`, `api_message.py`, `api_message_async.py`, `api_message_status.py`
- **Settings:** `settings_get.py`, `settings_set.py`
- **Scheduler:** `scheduler_tasks_list.py`, `scheduler_task_create.py`, `scheduler_task_run.py`, …
- **Backup:** `backup_create.py`, `backup_restore.py`, `backup_inspect.py`, …
- **MCP:** `mcp_servers_status.py`, `mcp_servers_apply.py`, `mcp_server_get_detail.py`, …
- **Projects, skills, notifications, health, upload, file_info, image_get, …**

## Tools (python/tools/)

- `response.py`, `code_execution_tool.py`, `memory_save.py`, `memory_load.py`, `memory_forget.py`, `memory_delete.py`
- `browser_agent.py`, `search_engine.py`, `document_query.py`, `vision_load.py`
- `behaviour_adjustment.py`, `scheduler.py`, `notify_user.py`, `input.py`, `wait.py`
- `call_subordinate.py`, `a2a_chat.py`, `skills_tool.py`, `unknown.py`
- `security/`: `web_scanner.py`, `code_scanner.py`, `network_scanner.py`, `finding_manager.py`

## Extension points (python/extensions/)

- `agent_init`, `banners`, `before_main_llm_call`, `error_format`, `hist_add_before`, `hist_add_tool_result`
- `message_loop_start`, `message_loop_end`, `message_loop_prompts_before`, `message_loop_prompts_after`
- `monologue_start`, `monologue_end`
- `process_chain_end`, `user_message_ui`
- `reasoning_stream`, `reasoning_stream_chunk`, `reasoning_stream_end`
- `response_stream`, `response_stream_chunk`, `response_stream_end`
- `system_prompt`, `tool_execute_before`, `tool_execute_after`, `util_model_call_before`

## Helpers (python/helpers/)

- **API / core:** `api.py` (ApiHandler), `extension.py`, `tool.py`, `extract_tools.py`
- **Settings / env:** `settings.py`, `dotenv.py`
- **MCP / A2A:** `mcp_server.py`, `mcp_handler.py`, `fasta2a_server.py`
- **Persistence:** `history.py`, `persist_chat.py`, `files.py`, `context.py`
- **Runtime:** `runtime.py`, `defer.py`, `log.py`, `structured_log.py`, `errors.py`, `print_style.py`
- **Other:** `file_browser.py`, `backup.py`, `git.py`, …

## Config and data

- **Settings:** `python/helpers/settings.py`, `conf/model_providers.yaml`
- **Env:** `usr/.env` (or root `.env`); loaded via `python/helpers/dotenv.py`
- **Runtime data:** `usr/` (chats, settings.json, scheduler, uploads, memory, projects)

## Tests and validation

- **Tests:** `tests/` — pytest; exclusions in validate-project (rate_limiter_test, chunk_parser_test, test_fasta2a_client, email_parser_test)
- **Scripts:** `scripts/testing/verify-e2e-fixes.sh`, `scripts/testing/validate.sh` (container)
- **CI:** `.github/workflows/verify-e2e-fixes.yml` (pytest + ruff)

## Documentation

- **Index:** `docs/DOCUMENTATION_INDEX.md`
- **Setup:** `docs/setup/dev-setup.md`, `docs/guides/TESTING_AND_CI.md`
- **Workflow:** `docs/guides/A0_SIP_WORKFLOW.md`
- **Planning:** `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`

---

*Use this index to jump to the right area; see STRUCTURE.md for naming and where to add new code.*
