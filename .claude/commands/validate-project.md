---
description: Comprehensive validation for Agent Zero codebase (project-specific)
---

# Validate Project (Agent Zero)

> **Generated for this codebase:** Agent Zero – Python agentic framework (python/, agents/, webui), Docker stack, pytest in tests/. Run from repo root. Use **/validate-project** (not /validate) to run this project's validation.

**Execute ONLY the validation in this file.** Do not run another project's validation.

**Setup (once):** Create and use a virtual environment (e.g. `python -m venv .venv` then `pip install -r requirements.txt -r requirements.dev.txt`). Use the **project venv** for Phase 2 and Phase 4 so deps (e.g. simpleeval) are available—e.g. `.venv/bin/python` (or `venv/bin/python` if your venv is named `venv`). Optional: `pip install ruff` for Phase 1 and 3. For E2E (Phase 5), Docker must be available; use `./startup.sh` or `docker compose up -d` from repo root to start the stack.

## Phase 1: Linting

Run ruff on application and test code (skip if ruff not installed):

`ruff check python/ agents/ tests/ --exclude venv --exclude 'webui/vendor'`

## Phase 2: Type Checking

Optional. Run mypy if installed (warnings acceptable; ensure no critical errors). Use project venv so type stubs match runtime:

`.venv/bin/python -m mypy python/ --ignore-missing-imports --no-error-summary 2>/dev/null || true`
(If your venv is named `venv`, use `venv/bin/python` instead.)

## Phase 3: Style Checking

Verify formatting with ruff (skip if ruff not installed):

`ruff format --check python/ agents/ tests/ --exclude venv --exclude 'webui/vendor'`

## Phase 4: Unit Testing

Run pytest from repo root **using the project venv** so runtime deps (e.g. simpleeval) are available. Exclude tests that require API keys or run LLM calls at import time (email_parser_test needs html2text; install from requirements.txt or requirements.dev.txt for full coverage):

`.venv/bin/python -m pytest tests/ -v --tb=short --ignore=tests/rate_limiter_test.py --ignore=tests/chunk_parser_test.py --ignore=tests/test_fasta2a_client.py --ignore=tests/email_parser_test.py`
(If your venv is named `venv`, use `venv/bin/python` instead.)

## Phase 5: End-to-End Testing (Docker)

User workflow from docs: start stack (or use existing running container) → Web UI reachable → optional full stack validation → cleanup if you started the stack.

### Option A – Start stack and verify Web UI

From repo root:

`docker compose up -d`

Wait for Web UI to respond (default port 8888; 200 or 302 is success):

`timeout 90 bash -c 'until CODE=$(curl -fsS -o /dev/null -w "%{http_code}" "http://localhost:${HOST_PORT:-8888}"); echo "$CODE" | grep -qE "200|302"; do sleep 3; done'`

Verify Web UI:

`curl -fsS -o /dev/null -w "%{http_code}" "http://localhost:${HOST_PORT:-8888}"`

Expect 200 or 302. Non-2xx indicates failure.

### Option B – Full stack validation (container already running)

If the agent-zero container is already up (e.g. after Option A or `./startup.sh`), run the project validation script:

`./scripts/testing/validate.sh`

This checks: container health, Web UI, supervisor services (run_ui, xvfb, fluxbox, x11vnc), VNC, Claude Code, volume mounts, MCP token, security tools (nmap, nikto), resource limits.

### Cleanup (only if you started the stack in this run)

`docker compose down`

(Omitting `-v` preserves memory, knowledge, logs, and tmp per README.)

## Summary

Report results for each phase: **Pass**, **Fail**, or **Skipped** (with reason). If all runnable phases pass, state: "All validation passed. Ready for deployment or next steps."

## Journal Entry (required after validation)

1. Ensure `journal/` exists: `mkdir -p journal`
2. Append one line to `journal/$(date +%Y-%m-%d).md`:  
   `HH:MM | Pass/Fail | E:N W:M | P1:... P2:... P3:... P4:... P5:... | optional note`  
   Use 24-hour time, E = errors, W = warnings, P1–P5 = phase outcomes (OK / Skip / Fail).
3. Update `journal/README.md` with one line per date for that day's latest outcome (e.g. `YYYY-MM-DD | validate-project | Pass` or `Fail`).
