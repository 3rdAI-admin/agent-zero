# Testing and CI

This guide describes how to run tests and verification locally and in CI for Agent Zero.

## Quick reference

| What | How |
|------|-----|
| **Local verification (pytest + ruff)** | `./scripts/testing/verify-e2e-fixes.sh` |
| **Parallel verification (AI subagents)** | Use `/verify-with-subagents` in Cursor/Claude |
| **Full E2E (browser + app)** | Use `/e2e-test` (see [E2E report](../../e2e-test-report.md)) |
| **CI (automatic)** | Runs on push/PR to `main` or `master` via [verify-e2e-fixes workflow](../../.github/workflows/verify-e2e-fixes.yml) |

## Local verification script

**Script:** `scripts/testing/verify-e2e-fixes.sh`

Runs in parallel:

- **pytest** — Unit tests, excluding rate-limiter, UI, and e2e tests (same exclusions as the E2E pass).
- **ruff** — Lint and format check.

Use this before pushing or when coordinating with the [A0 SIP workflow](./A0_SIP_WORKFLOW.md) (e.g. after implementing a task).

```bash
# From repo root, with venv activated
./scripts/testing/verify-e2e-fixes.sh
```

## CI workflow

**Workflow:** `.github/workflows/verify-e2e-fixes.yml`

- **Triggers:** Push or pull request to `main` or `master`.
- **Steps:** Checkout → Python 3.11 → create venv → install `requirements.txt`, `requirements.dev.txt`, optional `requirements2.txt`, ruff → run `./scripts/testing/verify-e2e-fixes.sh`.

No browser or E2E is run in CI; the same pytest and ruff checks as the local script are used.

**Full validation (local only):** When you run **`/validate-project`** (or the commands in `.claude/commands/validate-project.md`), full validation includes **mypy** (Phase 2) and **`./scripts/testing/validate.sh`** (Phase 5 Option B) when the Docker stack is up. CI does not run mypy or `validate.sh`; those remain local for a complete pass.

## E2E testing

Full end-to-end testing (browser, login, main UI, responsive viewports) is run via the **`/e2e-test`** command (see [.claude/commands/e2e-test.md](../../.claude/commands/e2e-test.md) or the e2e-test skill). Results and findings are documented in:

- **[E2E test report](../../e2e-test-report.md)** — Summary, phases, issues, screenshots, and recommendations.

For E2E you typically:

1. Start the app (e.g. `python run_ui.py`).
2. Run `/e2e-test` (or follow the e2e-test command/skill).
3. Review the report and screenshots in `e2e-screenshots/`.

Using a test account (`AUTH_LOGIN` / `AUTH_PASSWORD` in `usr/.env`) allows full main-UI journey coverage.

## Verify with subagents

When using Cursor or Claude with the project’s commands:

- **`/verify-with-subagents`** — Runs verification by delegating to parallel subagents (e.g. shell pytest, shell ruff, review). Same logical checks as `verify-e2e-fixes.sh`, with optional review.

See `.cursor/rules/verify-with-subagents.mdc` and `.commands/verify-with-subagents.md` for details.

## Related docs

- [A0 SIP Workflow](./A0_SIP_WORKFLOW.md) — Task flow and when to run verification.
- [E2E test report](../../e2e-test-report.md) — Full E2E results and recommendations.
- [Development setup](../setup/dev-setup.md) — Environment and dependencies for running tests.
