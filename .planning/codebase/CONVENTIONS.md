# Coding Conventions

**Analysis Date:** 2026-02-20

## Naming Patterns

**Files:**
- Snake_case for Python modules: `api.py`, `defer.py`, `file_tree.py`, `errors.py`, `print_style.py`. Use descriptive module names that match the primary abstraction (e.g. `api_message_async.py`, `api_message_status.py`).

**Functions:**
- Snake_case: `file_tree()`, `format_error()`, `get_abs_path()`, `materialize_structure()`, `run_coroutine()`. Use verb-noun or get/set prefixes where appropriate.

**Variables:**
- Snake_case for locals and parameters: `relative_path`, `input_data`, `base_rel`, `thread_name`. Constants in UPPER_SNAKE in some modules (e.g. `SORT_BY_NAME`, `OUTPUT_MODE_STRING` in `python/helpers/file_tree.py`).

**Types/Classes:**
- PascalCase: `ApiHandler`, `EventLoopThread`, `DeferredTask`, `AgentContext`, `RepairableException`. Class names are singular nouns or noun phrases.

**Private / internal:**
- Leading underscore for internal helpers: `_start()`, `_run_event_loop()`, `_get_embeddings()`, `_apply_timestamps()` in `python/helpers/defer.py`, `python/helpers/vector_db.py`, `tests/test_file_tree_visualize.py`.

## Code Style

**Formatting:**
- Ruff is the formatter and linter. Config: `ruff.toml` at repo root.
- Line length: 88. Target Python: 3.11 (`target-version = "py311"`).
- Excluded from ruff: `venv`, `.venv`, `webui/vendor`, `claude-credentials`.
- Run: `ruff check python/ agents/ tests/ --exclude venv --exclude 'webui/vendor'` and `ruff format --check python/ agents/ tests/` (or without `--check` to fix). Project rules reference "black" in docs (e.g. CLAUDE.md); actual tooling is Ruff.

**Linting:**
- Ruff lint with per-file ignores: `tests/*` and selected helpers (`python/helpers/files.py`, `log.py`, `print_style.py`, `task_scheduler.py`) ignore E402 (module level import not at top). See `ruff.toml` [lint.per-file-ignores].

**Type hints:**
- Use type hints on public functions and methods. Examples: `def file_tree(..., output_mode: Literal["string", "flat", "nested"] = ...) -> str | list[dict]` in `python/helpers/file_tree.py`; `async def process(self, input: Input, request: Request) -> Output` in `python/helpers/api.py`. Pyright is configured in `pyrightconfig.json` with `typeCheckingMode: "off"`; include list is `python`, `agent.py`, `models.py`, `run_ui.py`, etc.

## Import Organization

**Order:**
1. `from __future__ import annotations` when forward references or postponed evaluation are used (e.g. `tests/test_concurrent_api.py`, `python/helpers/file_tree.py`).
2. Standard library (e.g. `asyncio`, `json`, `threading`, `pathlib`, `sys`).
3. Third-party (e.g. `flask`, `pytest`, `pathspec`).
4. Local application packages: `from python.helpers...`, `from agent import ...`, `from initialize import ...`.

**Path handling in tests:**
- Tests that need the repo root on `sys.path` use: `REPO_ROOT = Path(__file__).resolve().parents[1]` and `if str(REPO_ROOT) not in sys.path: sys.path.insert(0, str(REPO_ROOT))`. Then import application modules (e.g. `from python.helpers.defer import ...`). See `tests/test_concurrent_api.py`, `tests/test_file_tree_visualize.py`. Alternative: `sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` in `tests/test_fasta2a_client.py`, `tests/chunk_parser_test.py`.

**No path aliases:** Imports use full package paths like `python.helpers.*`; no `@` or custom path aliases in this codebase.

## Error Handling

**Patterns:**
- Central formatting: use `format_error(e)` from `python/helpers/errors.py` to produce trimmed tracebacks and error messages for API/user-facing output. Example: `python/helpers/api.py` catches `Exception` in `handle_request`, calls `format_error(e)` and returns 500 with that text.
- Re-raise asyncio cancellation: `python/helpers/errors.py` `handle_error()` re-raises `asyncio.CancelledError`; other exceptions can be handled or wrapped.
- Specific exceptions where possible: `TimeoutError`, `subprocess.TimeoutExpired`, `json.JSONDecodeError`, `ET.ParseError`, `OSError` in `python/helpers/defer.py`, `python/tools/security/web_scanner.py`, `python/tools/security/network_scanner.py`. Fall back to broad `except Exception` only when appropriate, and log or format with `format_error`/PrintStyle.
- Custom type: `RepairableException` in `python/helpers/errors.py` marks errors that can be surfaced to the LLM for self-repair.
- Raise with clear messages: e.g. `raise RuntimeError("Event loop is not initialized")`, `raise ValueError(f"Invalid timestamp format: {until_timestamp_str}")` in `python/helpers/defer.py`, `python/tools/wait.py`.

## Logging

**Framework:** No standard `logging` module usage in application code for user-facing output. Use `PrintStyle` from `python/helpers/print_style.py` for styled console output and errors (e.g. `PrintStyle().print(...)`, `PrintStyle.error(...)`, `PrintStyle.info(...)`). Agent and request flow use `python/helpers/log.py` (imported as `Log`) for context-aware logging.

**Patterns:**
- Use `PrintStyle.error(...)` for API or tool errors after catching exceptions.
- Use `PrintStyle().print(...)` or `PrintStyle(font_color=..., padding=...).print(...)` for normal or highlighted messages. See `python/helpers/api.py`, `python/api/api_message_async.py`, `python/tools/wait.py`, `python/tools/vision_load.py`, security tools in `python/tools/security/`.

## Comments

**When to Comment:**
- Non-obvious logic: use inline `# Reason:` to explain why, not just what (CLAUDE.md). Example in tests: `# Reason: We mock AgentContext to avoid full initialization` in `tests/test_concurrent_api.py`.
- Document parameters, return values, and behavior in docstrings rather than inline comments for public APIs.

**Docstrings:**
- Google style is required in project rules (CLAUDE.md): brief summary, `Args`, `Returns`, and optionally `Raises`/`Notes`. Example in `python/helpers/file_tree.py`: `file_tree()` has a long docstring with Parameters, Returns, and Notes. Shorter docstrings appear in `python/helpers/defer.py` (e.g. `EventLoopThread.terminate()`, `__init__`). Use docstrings for every function.

## Function Design

**Size:** Keep files under 500 lines (CLAUDE.md). Several helpers exceed this (e.g. `python/helpers/settings.py`, `python/helpers/task_scheduler.py`, `python/helpers/file_tree.py`); new code should be split into modules or helpers when approaching the limit.

**Parameters:** Prefer explicit keyword-only arguments for optional parameters after the first few (e.g. `file_tree(relative_path, *, max_depth=0, max_lines=0, ...)` in `python/helpers/file_tree.py`). Use type hints and defaults.

**Return values:** Prefer single return type; use `Union` or `|` when necessary (e.g. `str | list[dict]` for `file_tree` depending on `output_mode`). Return early on validation failures; use exceptions for real errors.

## Module Design

**Exports:** No strict `__all__` pattern observed; modules are imported by path. Public API is implied by usage from `agent.py`, `run_ui.py`, and other packages.

**Barrel files:** Not used; import from concrete modules (e.g. `from python.helpers.errors import format_error`, `from python.helpers.defer import DeferredTask, EventLoopThread`).

**Environment:** Use `python_dotenv` and project helpers (e.g. `python/helpers/dotenv.py`) for environment variables; do not hardcode secrets (CLAUDE.md).

---

*Convention analysis: 2026-02-20*
