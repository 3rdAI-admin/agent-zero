# PRP: Agent Zero Extended Framework – PRD Compliance Verification

**Source PRD:** [PRDs/agent-zero-extended-framework.md](../PRDs/agent-zero-extended-framework.md)  
**Version:** 1.0  
**Date:** 2026-02-21  
**Status:** Ready for execution

---

## Goal

Verify that the AgentZ codebase and documentation **fully satisfy** the Product Requirements Document (PRD) for the Agent Zero Extended Framework. Close any gaps (docs, scripts, or configuration) and establish executable validation gates so future changes can be checked against the PRD.

## Why

- The PRD defines the product scope, requirements, and success criteria; implementation already exists in this fork.
- A compliance pass ensures docs and scripts stay aligned with the PRD and gives a clear baseline for onboarding and `/validate-project`.
- Executable validation gates enable one-pass confidence when executing this PRP or future feature PRPs.

## What

- **Audit:** Map each PRD requirement (FR-1–FR-9, NFR-1–NFR-5, Success Criteria) to existing files and behavior.
- **Gaps:** Add or fix documentation, startup script references, or validation steps where the PRD is not fully met.
- **Validation:** Run Docker build/up, healthcheck, existing validation scripts, and (where applicable) ruff/pytest; fix any failures.

### Success Criteria

- [ ] Every FR and NFR has a documented implementation location or explicit “N/A / deferred” note.
- [ ] `./startup.sh` from repo root builds and starts the agent-zero container; healthcheck passes.
- [ ] `docs/QUICK_REFERENCE.md` and `docs/COMPLETE_SETUP_GUIDE.md` exist and are linked from `docs/DOCUMENTATION_INDEX.md`; PRD-relevant topics (MCP, HTTP-only, VNC, security tools) are covered.
- [ ] `scripts/testing/validate.sh` (or `validate_thorough.sh`) runs and passes when the container is up.
- [ ] Python lint/format and unit tests run per validate-project (ruff, optional mypy, pytest with documented exclusions).

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ
- file: PRDs/agent-zero-extended-framework.md
  why: Source of all requirements and success criteria

- file: PLANNING.md
  why: Architecture, conventions, constraints (500 lines, .env, Docker)

- file: docker-compose.yml
  why: Service name, ports, healthcheck, env (AGENT_ZERO_HTTP_ONLY, HOST_PORT), volumes, cap_add

- file: Dockerfile
  why: Base image, install steps, OWASP tools (install_owasp_tools.sh), CMD

- file: run_ui.py
  why: HTTP vs HTTPS (AGENT_ZERO_HTTP_ONLY), host/port, ssl_ctx

- file: startup.sh
  why: Single entrypoint: checks for running instance → graceful stop → start → health check → status; optionally checks GitHub for Agent Zero / ZeroClaw updates. Does not build by default (use docker compose build separately if needed).

- file: docs/DOCUMENTATION_INDEX.md
  why: Required docs list (QUICK_REFERENCE, COMPLETE_SETUP_GUIDE, connectivity, MCP)

- file: scripts/testing/validate.sh
  why: Phases: container, Web UI, supervisor, VNC, Claude, MCP, security tools

- file: .claude/commands/validate-project.md
  why: Lint (ruff), mypy, format, pytest, E2E (curl Web UI)
```

### External References

- [Agent Zero upstream](https://github.com/agent0ai/agent-zero) – README, docs/ for compatibility scope.
- [Docker Compose healthcheck](https://docs.docker.com/compose/compose-file/05-services/#healthcheck) – interval, timeout, retries, start_period.
- [Ruff](https://docs.astral.sh/ruff/) – check and format; config in `ruff.toml`.

### Known Gotchas

- **Healthcheck:** Compose uses `curl -fsS http://localhost` (container port 80). With `AGENT_ZERO_HTTP_ONLY=1`, server is HTTP; ensure curl in image uses `http://localhost` (no port if 80). If healthcheck fails, check `run_ui.py` binding and curl availability in container.
- **Pytest:** Some tests are skipped in validate-project (rate_limiter_test, chunk_parser_test, test_fasta2a_client, email_parser_test) due to API keys, LLM/imports, or optional deps (e.g. html2text). Do not remove exclusions without updating validate-project.
- **Pytest collection / venv:** Before running pytest, install dev deps so collection succeeds: `pip install -r requirements.txt -r requirements.dev.txt`. Missing html2text (or other requirements.dev.txt deps) can cause collection errors; validate-project excludes `email_parser_test.py` when not needed, but full coverage requires a complete venv.
- **No pyproject.toml:** Project uses `requirements.txt` and `requirements.dev.txt`; use `pip install -r requirements.txt -r requirements.dev.txt` and `python -m pytest` (not `uv run pytest` unless uv is adopted later).
- **Repo root:** All compose and `./startup.sh` must run from repo root so `.:/git/agent-zero` and `.env` resolve.

---

## Implementation Blueprint

### Approach

1. **Audit matrix** – One artifact (table or checklist) mapping each PRD requirement to a file/path or “verified / N/A”.
2. **Doc and script checks** – Ensure QUICK_REFERENCE, COMPLETE_SETUP_GUIDE, connectivity, MCP docs exist and reference startup, HTTP-only, and healthcheck; ensure `startup.sh` is the single start entrypoint documented.
3. **Run gates** – Execute Docker build, `./startup.sh` (or `docker compose up -d`), wait for healthy, run `scripts/testing/validate.sh`; run ruff (and optionally mypy/pytest) per validate-project; fix any failures.
4. **PRD update** – Optionally add a “Verification” section or update PRD status to “In Review” once compliance is documented.

### Multi-Agent Task Breakdown

| Task ID | Scope | Assignable unit | Acceptance |
|--------|--------|------------------|------------|
| Task 1 | PRD compliance audit | Agent/Pass 1 | Audit table or checklist added (e.g. to PRPs/ or docs/); every FR/NFR and success criterion has a location or N/A. |
| Task 2 | Docs and startup alignment | Agent/Pass 2 | QUICK_REFERENCE and COMPLETE_SETUP_GUIDE exist, linked in DOCUMENTATION_INDEX; they reference `./startup.sh`, HOST_PORT, HTTP-only; README or QUICK_REFERENCE mentions startup.sh at repo root. |
| Task 3 | Docker and validation scripts | Agent/Pass 3 | `docker compose build agent-zero` and `./startup.sh` (or `docker compose up -d agent-zero`) succeed; container becomes healthy; `scripts/testing/validate.sh` run from host passes (or failures documented with remediation). |
| Task 4 | Lint and unit tests | Agent/Pass 4 | `ruff check` and `ruff format --check` on python/ agents/ tests/ pass (or excludes documented); `python -m pytest tests/ -v` with validate-project exclusions passes or known failures documented. |
| Task 5 | PRD verification section or status | Agent/Pass 5 | PRD has a short “Verification” subsection or status note (e.g. “Verified 2026-02-21” or “In Review”); or VERIFICATION.md in PRDs/ summarizing compliance. |

### List of Tasks (in order)

```yaml
Task 1 – PRD compliance audit:
  CREATE or UPDATE a compliance artifact (e.g. docs/PRD_COMPLIANCE.md or section in PRPs/):
    - For each FR-1..FR-9: document where it is implemented (file + brief location).
    - For each NFR-1..NFR-5: same.
    - For each Success Criterion: how it is verified (script or manual step).
  REFERENCE: PRDs/agent-zero-extended-framework.md sections 3 and 3.3.

Task 2 – Docs and startup alignment:
  READ: docs/QUICK_REFERENCE.md, docs/COMPLETE_SETUP_GUIDE.md, docs/DOCUMENTATION_INDEX.md.
  ENSURE: Both guides exist; DOCUMENTATION_INDEX links them; content references:
    - Starting the stack: ./startup.sh or docker compose up -d agent-zero from repo root.
    - HOST_PORT (default 8888), HTTP-only (AGENT_ZERO_HTTP_ONLY=1), MCP URL pattern.
  FIX: Add or correct any missing references (e.g. startup.sh in Quick Start or Setup).

Task 3 – Docker and validation scripts:
  RUN from repo root:
    - docker compose build agent-zero
    - ./startup.sh  (or docker compose up -d agent-zero)
  WAIT for container health: docker ps shows healthy or wait up to start_period (60s).
  RUN: ./scripts/testing/validate.sh
  ACCEPT: All phases pass, or document failures and add remediation steps to PRP or docs.

Task 4 – Lint and unit tests:
  SETUP (required for pytest): pip install -r requirements.txt -r requirements.dev.txt; pip install ruff. Ensures html2text and other test deps are present so pytest collection does not fail.
  RUN:
    - ruff check python/ agents/ tests/ --exclude venv --exclude 'webui/vendor'
    - ruff format --check python/ agents/ tests/ --exclude venv --exclude 'webui/vendor'
    - python -m pytest tests/ -v --tb=short --ignore=tests/rate_limiter_test.py --ignore=tests/chunk_parser_test.py --ignore=tests/test_fasta2a_client.py
  FIX: Resolve new lint/format/test failures introduced by changes; otherwise document known failures.

Task 5 – PRD verification section or status:
  UPDATE PRDs/agent-zero-extended-framework.md:
    - Add a short "Verification" subsection (e.g. after 5. References) with date and summary, OR
    - Set Status to "In Review" and add one-line note that compliance was verified.
  OR CREATE PRDs/VERIFICATION.md with one-page summary of compliance and validation commands.
```

---

## Validation Gates (Must Be Executable)

### Level 1: Docker build and start

```bash
cd /Users/james/Docker/AgentZ
docker compose build agent-zero
./startup.sh
# Wait until container is healthy (e.g. docker ps shows (healthy))
docker ps --filter name=agent-zero
```

### Level 2: Validation script

```bash
./scripts/testing/validate.sh
# Expect: All phases pass (or document skips/failures)
```

### Level 3: Lint and format (from repo root, with venv active)

```bash
ruff check python/ agents/ tests/ --exclude venv --exclude 'webui/vendor'
ruff format --check python/ agents/ tests/ --exclude venv --exclude 'webui/vendor'
```

### Level 4: Unit tests

Ensure venv has dev deps first: `pip install -r requirements.txt -r requirements.dev.txt`. Then:

```bash
python -m pytest tests/ -v --tb=short --ignore=tests/rate_limiter_test.py --ignore=tests/chunk_parser_test.py --ignore=tests/test_fasta2a_client.py --ignore=tests/email_parser_test.py
```

(Exclusions match validate-project; omit `--ignore=tests/email_parser_test.py` only if html2text is installed and you want that test.)

### Level 5: E2E (optional, container must be up)

```bash
curl -fsS -o /dev/null -w "%{http_code}" "http://localhost:${HOST_PORT:-8888}"
# Expect: 200 or 302
```

---

## Final Validation Checklist

- [ ] PRD compliance audit artifact exists and covers all FR, NFR, Success Criteria.
- [ ] QUICK_REFERENCE and COMPLETE_SETUP_GUIDE exist and reference startup, port, HTTP-only.
- [ ] `docker compose build agent-zero` and `./startup.sh` succeed; container healthy.
- [ ] `./scripts/testing/validate.sh` passes (or failures documented).
- [ ] `ruff check` and `ruff format --check` pass on python/ agents/ tests/.
- [ ] Pytest passes with validate-project exclusions (or known failures documented).
- [ ] PRD updated with verification note or PRDs/VERIFICATION.md created.

---

## Anti-Patterns to Avoid

- Do not change upstream agent logic or default tools; this PRP is verification and docs only.
- Do not remove pytest exclusions from validate-project without updating both PRP and validate-project.
- Do not hardcode host ports or paths; use HOST_PORT and repo-relative paths.
- Do not mark PRD requirements as “done” without a clear implementation reference.

---

## Quality Checklist

- [x] All necessary context included (PRD, PLANNING, docker-compose, run_ui, startup, validate.sh, validate-project).
- [x] Validation gates are executable by AI (bash commands from repo root).
- [x] References existing patterns (validate.sh phases, validate-project phases).
- [x] Clear implementation path (audit → docs → Docker/validate → lint/tests → PRD update).
- [x] Error handling documented (healthcheck gotcha, pytest exclusions, known failures).

**Confidence score (1–10 for one-pass implementation):** 8. Implementation exists; success depends on current state of container, venv, and test stability. Audit and doc tasks are low-risk; Docker and test steps may need one remediation pass if environment differs.

---

## Revision History

### Revision 1 (2026-02-21)

**Trigger:** validate-project partial run (journal 2026-02-20): Phase 4 (pytest) failed with collection error due to missing html2text in venv.

**Root cause:** The PRP did not require or document that a full venv setup (`pip install -r requirements.txt -r requirements.dev.txt`) must be done before running pytest. Validate-project excludes `email_parser_test.py` when html2text is missing, but collection can still fail if other dev deps are missing; the plan assumed “run pytest with these ignores” without an explicit “install dev deps first” step.

**Changes:**
- **Known Gotchas:** Added pytest collection/venv gotcha: install `requirements.txt` and `requirements.dev.txt` before pytest; noted email_parser_test and html2text. Expanded Pytest bullet to include email_parser_test and optional deps.
- **Task 4 (List of Tasks):** SETUP line now says “required for pytest” and “Ensures html2text and other test deps are present so pytest collection does not fail.”
- **Validation Gates Level 4:** Added prerequisite sentence and `--ignore=tests/email_parser_test.py` to the example command so it matches validate-project; noted when to omit that ignore.
- **All Needed Context (startup.sh):** Updated description to match current behavior: check for running instance → graceful stop → start → health check → status; optional GitHub check for Agent Zero / ZeroClaw updates; does not build by default.
