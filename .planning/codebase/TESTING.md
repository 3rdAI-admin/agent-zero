# Testing Patterns

**Analysis Date:** 2026-02-20

## Test Framework

**Runner:**
- Pytest 8.4.2+ (see `requirements.dev.txt`).
- No `pytest.ini` or `[tool.pytest]` in repo; no `pyproject.toml` at root. Options are passed via CLI.

**Plugins:**
- pytest-asyncio 1.2.0+ for async tests.
- pytest-mock 3.15.1+ available (unittest.mock patterns used; no pytest-mock-specific usage observed in current tests).
- html2text 2024.2.26+ (required for some tests, e.g. email_parser_test; install from `requirements.dev.txt`).

**Run Commands:**
```bash
# From repo root, with project venv activated
python -m pytest tests/ -v --tb=short

# With exclusions (per validate-project): skip tests that need API keys or have heavy deps
python -m pytest tests/ -v --tb=short --ignore=tests/rate_limiter_test.py --ignore=tests/chunk_parser_test.py --ignore=tests/test_fasta2a_client.py --ignore=tests/email_parser_test.py
```

Validation doc: `.claude/commands/validate-project.md` (Phase 4). No built-in watch or coverage commands in repo; add `pytest-watch` or `pytest-cov` if needed.

## Test File Organization

**Location:**
- Primary: `tests/` at repository root. Tests mirror main app by topic, not by strict path mirror (e.g. `tests/test_concurrent_api.py` exercises `python/helpers/defer.py` and agent context/API behavior).
- Script-style or manual tests: `scripts/testing/` (e.g. `test_mcp_connection.py`, `test_server.py`, `test_mcp_tools_list.py`, `test_mcp_tools_confirm.py`). These are run on demand, not as part of the default pytest run.

**Naming:**
- Two patterns: `test_*.py` (e.g. `test_concurrent_api.py`, `test_file_tree_visualize.py`, `test_fasta2a_client.py`) and `*_test.py` (e.g. `chunk_parser_test.py`, `email_parser_test.py`, `rate_limiter_test.py`). Prefer `test_*.py` for consistency with discovery and docs.

**Structure:**
```
tests/
├── test_concurrent_api.py   # EventLoopThread, DeferredTask, AgentContext, ApiMessageStatus
├── test_file_tree_visualize.py  # file_tree scenarios (skip in auto runs)
├── test_fasta2a_client.py   # FastA2A connectivity (often ignored in CI)
├── chunk_parser_test.py     # models.ChatGenerationResult (parametrize)
├── email_parser_test.py     # disabled/skip
└── rate_limiter_test.py     # often ignored in CI
```

No `conftest.py` in `tests/`; shared setup is done inline (e.g. sys.path, try/finally cleanup).

## Test Structure

**Suite organization:**
- Group tests in classes by behavior. Example from `tests/test_concurrent_api.py`:

```python
class TestEventLoopThreadIsolation:
    """Verify that per-context thread names produce independent instances."""

    def test_different_names_give_different_instances(self):
        """Two different thread names should create separate EventLoopThread instances."""
        ...
    def test_same_name_gives_same_instance(self):
        ...
```

- Module-level docstring describes what is verified (e.g. "Per-context EventLoopThread isolation", "EventLoopThread singleton cleanup", "AgentContext.last_result / last_error", "ApiMessageStatus endpoint responses").
- Use `try`/`finally` in tests that create threads or resources to ensure cleanup (e.g. `EventLoopThread(...).terminate()`).

**Patterns:**
- Setup: Create objects (e.g. `EventLoopThread(name)`), optionally patch dependencies, then assert. No shared fixtures; each test is self-contained where possible.
- Teardown: `finally` blocks to call `terminate()`, `kill(terminate_thread=True)`, or delete temp dirs (e.g. `scenario_directory` context manager in `test_file_tree_visualize.py`).
- Assertions: Plain `assert` (e.g. `assert t1 is not t2`, `assert response["status"] == "not_found"`). No custom assertion helpers in the sampled tests.

**Async tests:**
- Mark with `@pytest.mark.asyncio`. Example in `tests/test_fasta2a_client.py`: `@pytest.mark.asyncio` on `async def test_server_connectivity()`. Async tests in `test_concurrent_api.py` use synchronous test methods that start coroutines via `DeferredTask` and wait on results.

**Parametrized tests:**
- Use `@pytest.mark.parametrize`. Example in `tests/chunk_parser_test.py`: `@pytest.mark.parametrize("example", [ex1, ex2])` with `def test_example(example: str)`.

**Skipped tests:**
- Module-level skip: `pytestmark = pytest.mark.skip(reason="...")` (e.g. `tests/test_file_tree_visualize.py` — "Visualization utility; excluded from automated test runs.").
- Per-test skip: `@pytest.mark.skip(reason="...")` (e.g. `tests/email_parser_test.py` — disabled due to external deps). Tests that are routinely excluded from CI are passed to pytest via `--ignore=...` in the validate-project command.

## Mocking

**Framework:** `unittest.mock`: `MagicMock`, `patch`. No pytest-mock fixtures (e.g. `mocker`) in the current tests.

**Patterns:**
- Patch at import path before importing the module under test. Example in `tests/test_concurrent_api.py`:

```python
with patch("agent.Agent"):
    with patch("agent.Log.Log"):
        from agent import AgentContext, AgentConfig
        _mock_config = MagicMock(spec=AgentConfig)
        ctx = AgentContext.__new__(AgentContext)
        ctx.last_result = None
        ctx.last_error = None
        assert ctx.last_result is None
```

- Use `MagicMock(spec=SomeClass)` when a type contract matters. Use `patch("module.ClassName")` to avoid loading heavy or external deps.

**What to mock:** Agent classes, Log, and other app bootstrap when testing context or API response shape in isolation. External HTTP or LLM calls should be mocked when adding unit tests.

**What NOT to mock:** The code under test (e.g. `DeferredTask`, `EventLoopThread` in `test_concurrent_api.py`). Prefer real instances for pure logic when fast and deterministic.

## Fixtures and Factories

**Test data:**
- Inline dicts and lists (e.g. response shape `{"context_id": "...", "status": "not_found", "response": None}`). No dedicated fixture files or factories in `tests/`.
- `tests/test_file_tree_visualize.py` builds scenario data in `build_scenarios()` (dataclasses `Scenario`, `Config`) and uses a temp directory context manager `scenario_directory(name)` under `tmp/tests/file_tree/visualize`.

**Location:** No `tests/fixtures/` or `tests/factories/`; data is defined inside the test module or helper functions.

## Coverage

**Requirements:** No enforced coverage target or pytest-cov config in repo. Validation runs pytest without coverage.

**View coverage (if pytest-cov is installed):**
```bash
python -m pytest tests/ -v --tb=short --cov=python --cov=agent --cov-report=term-missing
```
Not in validate-project; add when desired.

## Test Types

**Unit tests:** Current focus. Test isolated behavior: `EventLoopThread` singleton and cleanup, `DeferredTask` independence, `AgentContext` attribute defaults, API response structure (dict shape). No Flask app or server started in `test_concurrent_api.py`.

**Integration tests:** Scripts in `scripts/testing/` (e.g. MCP connection, server) are integration/manual. Some tests in `tests/` are excluded from default runs because they hit external services or have heavy dependencies (e.g. `test_fasta2a_client.py`, `email_parser_test.py`).

**E2E:** Validate-project Phase 5 uses Docker and curl to check Web UI reachability; no in-repo E2E test framework (e.g. Playwright) for the Agent Zero app itself.

## Common Patterns

**Async testing (without async test function):**
- Start a coroutine on a `DeferredTask` (which uses `EventLoopThread`), then call `result_sync(timeout)` or `kill()` in a `finally` block. Example: `TestDeferredTaskIsolation.test_tasks_on_different_threads_are_independent` in `tests/test_concurrent_api.py`.

**Error testing:**
- Response-shape tests assert on expected keys and values (e.g. `status`, `response`). No `pytest.raises` in the sampled tests; for exception paths, use `with pytest.raises(SomeError):` when adding new tests.

**Import and path:**
- Ensure repo root on `sys.path` at top of test file (e.g. `REPO_ROOT = Path(__file__).resolve().parents[1]` and `sys.path.insert(0, str(REPO_ROOT))`) before importing `python.*` or `agent` modules. Ruff E402 is ignored for `tests/*` so this pattern is allowed.

---

*Testing analysis: 2026-02-20*
