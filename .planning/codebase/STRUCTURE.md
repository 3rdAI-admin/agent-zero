# Codebase Structure

**Analysis Date:** 2025-02-20

## Directory Layout

```
[project-root]/
├── agent.py                 # Agent and AgentContext core; monologue, tools, extensions
├── initialize.py            # AgentConfig from settings; init chats, MCP, job loop, preload
├── models.py                # LLM config and invocation (LiteLLM, LangChain adapters)
├── run_ui.py                # Flask app entry; API registration; /mcp, /a2a mounts; init_a0
├── run_tunnel.py            # Tunnel entry (if used)
├── prompts/                 # Default prompt templates (system, fw.*, memory.*, etc.)
├── agents/                  # Per-profile overrides (prompts, tools, extensions)
│   ├── _example/            # Example agent with tools, extensions, prompts
│   ├── agent0/              # Agent0 profile prompts
│   ├── default/
│   ├── developer/
│   ├── hacker/
│   └── researcher/
├── python/
│   ├── api/                 # REST handlers (ApiHandler subclasses); one file per endpoint
│   ├── helpers/             # Shared utilities (api, defer, extension, files, mcp_server, etc.)
│   ├── extensions/          # Default extension points and implementations
│   └── tools/               # Default tools (response, code_execution_tool, memory_*, etc.)
├── webui/                   # Frontend: index.html/js/css, login, components, js, css, public, vendor
├── config/                  # Config examples (e.g. config/examples)
├── conf/                    # Runtime config (e.g. model_providers.yaml, projects.default.gitignore)
├── instruments/             # Instrument scripts (default/, custom/)
├── knowledge/               # Knowledge fragments/solutions (default/, custom/)
├── memory/                  # Runtime memory/embedding data
├── docker/                  # Docker build and run (base/, run/, scripts)
├── scripts/                 # Setup, testing, maintenance, docker scripts
├── tests/                   # Pytest tests
├── docs/                    # Documentation
├── lib/                     # Optional libs (e.g. lib/browser)
├── tmp/                     # Uploads, chats, scheduler, playwright, etc.
└── .planning/codebase/      # Codebase analysis docs (this file)
```

## Directory Purposes

**Root:**
- Purpose: Entry modules and top-level agent/config.
- Key files: `agent.py`, `initialize.py`, `models.py`, `run_ui.py`.

**prompts/:**
- Purpose: Default Markdown prompt templates (system prompts, fw.*, memory.*, behaviour.*).
- Key files: `agent.system.*.md`, `fw.*.md`, `agent.context.extras.md`; `agent.system.tools.py` / `agent.system.tools.md` for tool list generation.
- Lookup: `Agent.read_prompt` / `parse_prompt` use `prompts` then `agents/<profile>/prompts` if profile set.

**agents/:**
- Purpose: Profile-specific overrides; each subdir can have `prompts/`, `tools/`, `extensions/<extension_point>/`.
- Key dirs: `agents/agent0`, `agents/developer`, `agents/_example` (reference layout).
- Naming: Directory name = `AgentConfig.profile` (e.g. `agent0`, `developer`).

**python/api/:**
- Purpose: REST API handlers; each module typically one `ApiHandler` subclass, registered by `run_ui.run()`.
- Contains: `message.py`, `poll.py`, `history_get.py`, `settings_get.py`, `chat_*.py`, `backup_*.py`, `scheduler_*.py`, etc.
- Naming: `*.py`; class name arbitrary but must inherit `ApiHandler`; URL rule is `/<module_name>` (from `handler.__module__.split(".")[-1]`).

**python/helpers/:**
- Purpose: Shared logic used by agent, API, extensions, tools.
- Key files: `api.py` (ApiHandler base), `extension.py` (Extension, call_extensions), `extract_tools.py` (load_classes_from_folder/file, json_parse_dirty), `tool.py` (Tool, Response), `files.py`, `history.py`, `mcp_server.py`, `mcp_handler.py`, `fasta2a_server.py`, `settings.py`, `defer.py`, `runtime.py`, `dotenv.py`, `persist_chat.py`, `log.py`, `errors.py`, `context.py`, etc.

**python/extensions/:**
- Purpose: Default extension implementations; one subdir per extension point (e.g. `agent_init`, `message_loop_start`, `system_prompt`, `tool_execute_before`).
- Contains: `_<nn>_<name>.py` modules with `Extension` subclasses; loaded and sorted by filename.
- Naming: Subdir = extension point name; files often prefixed with number for order.

**python/tools/:**
- Purpose: Default tool implementations callable by the agent.
- Contains: `response.py`, `code_execution_tool.py`, `memory_save.py`, `memory_load.py`, `browser_agent.py`, `search_engine.py`, `document_query.py`, etc.; optional `security/` subdir.
- Naming: `<tool_name>.py`; class must inherit `Tool`; agent resolves by `python/tools/<name>.py` or `agents/<profile>/tools/<name>.py`.

**webui/:**
- Purpose: Static frontend and login.
- Contains: `index.html`, `index.js`, `index.css`, `login.html`, `login.css`; `components/` (chat, messages, sidebar, settings, etc.); `js/`, `css/`, `public/`, `vendor/`.
- Served at `/` via Flask static_folder; index content may be placeholder-replaced in `serve_index`.

**config/ and conf/:**
- Purpose: `config/` holds example config; `conf/` holds runtime config (e.g. model providers, project gitignore).
- Key files: `conf/model_providers.yaml`, `config/examples/` (if present).

**instruments/ and knowledge/:**
- Purpose: Scripts and knowledge fragments; structure under `default/` and `custom/` (e.g. knowledge/default/fragments, solutions, instruments, main).
- Used by: Agent prompts and knowledge/memory tooling.

**docker/:**
- Purpose: Docker build and run layout (base image, run image, fs overlay).
- Contains: `docker/base/`, `docker/run/`, `docker/run/fs/`, install scripts.

**scripts/:**
- Purpose: Setup, testing, maintenance, and docker helper scripts.
- Contains: `scripts/setup/`, `scripts/testing/`, `scripts/maintenance/`, `scripts/docker/`.

**tests/:**
- Purpose: Pytest tests.
- Contains: Test modules; may mirror source layout or be feature-focused.

**tmp/:**
- Purpose: Runtime scratch (uploads, chat state, scheduler, playwright, downloads).
- Generated: Yes. Often gitignored or ephemeral.

## Key File Locations

**Entry points:**
- `run_ui.py`: Web server and init_a0.
- `agent.py`: Agent and context logic (no direct CLI; invoked via API/task).

**Configuration:**
- `initialize.py`: Builds `AgentConfig` from `python/helpers/settings.get_settings()`.
- `python/helpers/settings.py`: Central settings schema and defaults.
- `python/helpers/dotenv.py`: Env loading; `.env` existence only (do not read contents in docs).
- `conf/model_providers.yaml`: Model provider config.

**Core logic:**
- `agent.py`: AgentContext, Agent, AgentConfig, UserMessage, LoopData, monologue, process_tools, get_tool, prepare_prompt, call_extensions.
- `models.py`: ModelConfig, get_chat_model, get_embedding_model, get_browser_model, unified streaming.
- `python/helpers/extension.py`: Extension base and call_extensions.
- `python/helpers/tool.py`: Tool base and Response.
- `python/helpers/extract_tools.py`: load_classes_from_folder, load_classes_from_file, json_parse_dirty.

**API and integrations:**
- `python/helpers/api.py`: ApiHandler base.
- `python/api/message.py`: Main message endpoint (communicate → context.communicate).
- `python/helpers/mcp_server.py`: FastMCP app for /mcp.
- `python/helpers/fasta2a_server.py`: A2A app for /a2a.
- `python/helpers/mcp_handler.py`: MCP tool resolution for agent.

**Testing:**
- `tests/`: Pytest roots; test file names typically `*_test.py` or `test_*.py`.

## Naming Conventions

**Files:**
- Python: `snake_case.py`; API handlers live in `python/api/` with arbitrary module names (URL = last part of module name).
- Prompts: `*.md` in `prompts/` or `agents/<profile>/prompts/` (e.g. `fw.user_message.md`, `agent.system.main.md`).
- Extensions: `_<nn>_<name>.py` in `python/extensions/<extension_point>/` or `agents/<profile>/extensions/<extension_point>/`.

**Directories:**
- Profile names under `agents/`: lowercase, e.g. `agent0`, `developer`, `_example`.
- Extension points: one folder per point under `python/extensions/` and optionally under `agents/<profile>/extensions/`.

**Classes:**
- ApiHandler subclasses in `python/api/*.py`; one per file for discovery.
- Extension subclasses in extension-point folders; Tool subclasses in `python/tools/` or `agents/<profile>/tools/`.

## Where to Add New Code

**New API endpoint:**
- Add `python/api/<name>.py` with a class inheriting `ApiHandler` from `python/helpers/api.py`, implementing `process(self, input, request)`. Register by convention in `run_ui.run()` via `load_classes_from_folder("python/api", "*.py", ApiHandler)`; route becomes `POST /<name>`.

**New tool:**
- Default: add `python/tools/<tool_name>.py` with a class inheriting `Tool` from `python/helpers/tool.py`, implementing `async def execute(self, **kwargs) -> Response`. Agent resolves by `name` → `python/tools/<name>.py` (or profile `agents/<profile>/tools/<name>.py`). Expose in system prompts (e.g. `prompts/agent.system.tools.md` / `.py`) if needed.

**New extension:**
- Add a module under `python/extensions/<extension_point>/` (and optionally under `agents/<profile>/extensions/<extension_point>/`) with a class inheriting `Extension` from `python/helpers/extension.py`, implementing `async def execute(self, **kwargs)`. Extension point name must match where `call_extensions(extension_point, ...)` is invoked in `agent.py` (or API).

**New agent profile:**
- Create `agents/<profile_name>/` with optional subdirs: `prompts/`, `tools/`, `extensions/<point>/`. Set `AgentConfig.profile` (e.g. via settings `agent_profile`) to `<profile_name>`.

**Frontend change:**
- Edit `webui/index.html`, `webui/index.js`, `webui/index.css`, or files under `webui/components/`, `webui/js/`, `webui/css/`; add assets under `webui/public/` or `webui/vendor/` as needed.

**New prompt template:**
- Add `prompts/<name>.md` (or `agents/<profile>/prompts/<name>.md`); reference via `Agent.read_prompt(name)` or `parse_prompt(name, **kwargs)`.

## Special Directories

**tmp/:**
- Purpose: Uploads, chat persistence, scheduler state, playwright, downloads.
- Generated: Yes.
- Committed: Typically no (gitignore).

**memory/:**
- Purpose: Embeddings and default memory storage.
- Generated: Yes at runtime.
- Committed: Usually no.

**knowledge/default/ and knowledge/custom/:**
- Purpose: User/default knowledge fragments, solutions, instruments.
- Generated: Partially (user content).
- Committed: Structure/examples possible; user data often no.

**.planning/codebase/:**
- Purpose: Codebase analysis documents (ARCHITECTURE.md, STRUCTURE.md, etc.).
- Generated: By mapping/planning tools.
- Committed: Yes for reference.

---

*Structure analysis: 2025-02-20*
