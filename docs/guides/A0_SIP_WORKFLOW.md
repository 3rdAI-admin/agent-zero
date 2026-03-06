# A0 SIP Workflow (Archon + Agent Zero)

**A0 SIP** = Agent Zero Self-Improvement Project. This doc describes how tasks and runs are coordinated between **Archon** (task/project management) and **Agent Zero** (runtime).

## Project and repo

| Item | Value |
|------|--------|
| **Archon project ID** | `610ae854-2244-4cb8-a291-1e31561377ab` |
| **Project title** | A0 SIP (Agent Zero Self-Improvement Project) |
| **Repo path** | `/Users/james/Docker/AgentZ` (or your clone) |

## Workflow

1. **Tasks** — Stored in Archon under project `610ae854-2244-4cb8-a291-1e31561377ab`. Use Archon MCP (e.g. from Cursor) to list, create, and update tasks (`find_tasks`, `manage_task`). Status flow: `todo` → `doing` → `review` → `done`.

2. **Execution** — Agent Zero runs in Docker (or locally via `python run_ui.py`). Use the repo for code, tests, and validation. Run validation with `scripts/testing/validate.sh` (container) or `scripts/testing/verify-e2e-fixes.sh` (local pytest + ruff in parallel).

3. **Verification** — After implementing a task, run `/verify-with-subagents` (or `./scripts/testing/verify-e2e-fixes.sh`) to run tests and lint in parallel; update the Archon task to `review` then `done` when complete. **CI** runs the same verify script on push and PR to `main`/`master` (see [Testing and CI](./TESTING_AND_CI.md)).

## References

- **PRD:** `PRDs/agent-zero-extended-framework.md`
- **PRP (compliance):** `PRPs/agent-zero-extended-framework-prd-compliance.md`
- **Planning:** `PLANNING.md`
- **Task log:** `TASK.md`
- **E2E report:** `e2e-test-report.md`
