---
description: Run verification in parallel via subagents (tests, lint, code review)
---

# Verify With Subagents

When the user runs **/verify-with-subagents** (or asks to "verify with subagents" or "run parallel verification"), delegate verification to **three subagents in parallel** using the Task tool (`mcp_task`). Do not run all steps yourself; launch the three agents in a single turn and then summarize their results.

## 1. Launch these three subagents in parallel

**Subagent A – Shell (tests)**  
- **subagent_type:** `shell`  
- **Prompt:** In the project at /Users/james/Docker/AgentZ, run the test suite. Use: `cd /Users/james/Docker/AgentZ && . .venv/bin/activate && python -m pytest tests/ -v --ignore=tests/test_ui_ --ignore=tests/e2e --ignore=tests/rate_limiter_test.py -x 2>&1`. Report exit code, number of tests run/passed/failed, and any failure summary. Do not modify code; only run the command.

**Subagent B – Shell (lint)**  
- **subagent_type:** `shell`  
- **Prompt:** In the project at /Users/james/Docker/AgentZ, run lint and format checks. Use: `cd /Users/james/Docker/AgentZ && . .venv/bin/activate && ruff check python/ && ruff format --check python/ 2>&1` (or a focused path list if preferred). Report exit codes and any violations. Do not modify code; only run commands.

**Subagent C – General (review)**  
- **subagent_type:** `generalPurpose`  
- **Prompt:** Review the most recent security or E2E-related code changes in /Users/james/Docker/AgentZ (path traversal, XSS, API hardening, upload cleanup). List the files and one-line summary per fix. Reply with "OK" if the changes look correct, or "ISSUE: <description>" if something is wrong or missing. Do not modify code.

## 2. After all three complete

- Summarize: **Tests** (passed/failed), **Lint** (passed/failed), **Review** (OK or issues).
- If any subagent reported failures or issues, fix them (e.g. lint fixes, test fixes) and optionally re-run the failing subagent or the local script below.

## 3. Optional local script

Users can run the same **tests + ruff** checks locally in parallel (no subagents) with:

```bash
./scripts/testing/verify-e2e-fixes.sh
```

Use this when subagents are not available or for CI.
