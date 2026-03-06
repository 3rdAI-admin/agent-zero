# Phase 2: Container and execution hardening — audit

**Date:** 2026-03-06  
**Status:** Audit complete; implementation in progress.

## Container audit

### Base image
- **Image:** `agent0ai/agent-zero-base:latest` (from `docker/base/Dockerfile`) → `kalilinux/kali-rolling`.
- **User:** Not set in Dockerfile → container runs as **root** (PLATFORM-02: "agent-triggered code in inner sandbox" and minimal caps; non-root recommended for production).

### docker-compose.yml (agent-zero service)

| Item | Current | Phase 2 target (ROADMAP) |
|------|---------|---------------------------|
| **privileged** | Not set (good) | No `--privileged` ✓ |
| **cap_add** | `NET_RAW`, `NET_ADMIN`, `SYS_ADMIN` | Minimal capabilities; drop SYS_ADMIN if possible; NET_RAW needed for nmap. |
| **User** | (root) | Prefer non-root user when feasible. |
| **Mounts** | Repo at `/git/agent-zero`, `A0_volume` at `/a0/usr`, `.env`, memory, knowledge, logs, tmp, claude-config, playwright-browsers | No `docker.sock` or host root ✓. Bind mounts are for persistence; document that agent can read/write repo and usr. |
| **Networks** | default + archon_app-network | OK. |

### Recommendations
1. **Document** that `cap_add: NET_RAW, NET_ADMIN` are for security-scanning tools (nmap); consider removing `SYS_ADMIN` if not required by OWASP tools.
2. **Non-root:** Add a dedicated user in the image and run the main process as that user (optional in Phase 2; can be Phase 2.1).
3. **Inner sandbox:** Agent-triggered code runs in the same container via `code_execution_tool` (bash). A future inner sandbox (e.g. ephemeral container or micro-VM) is out of scope for initial Phase 2; bounded host control (allowlist/deny) is in scope.

## Execution audit

### Tool execution path
- **code_execution_tool** → `execute_terminal_command` / `execute_python_code` / `execute_nodejs_code` → `terminal_session` → `LocalInteractiveSession` → `TTYSession(runtime.get_terminal_executable())` → `/bin/bash`.
- **No allowlist/deny** — any command is executed (AUTON-04/06: bounded host control needed).
- **No audit log** — tool executions and high-stakes actions are not written to an append-only log (SAFETY-03).

### High-stakes entry points
- Autonomy trigger: `POST /api/autonomy_trigger` (run task / enqueue goal).
- Autonomy kill: `POST /api/autonomy_kill` (stop task(s)).
- Tool execution: every `tool.execute()` in `agent.process_tools()`.

## Implemented in Phase 2

1. **Append-only audit log** (`python/helpers/audit_log.py`) — writes to `usr/governance/audit.log` (or `AGENTZ_AUDIT_LOG_PATH`); agent has no tool to write to this file. Logs: tool executions (tool_name, sanitized args, timestamp, context), autonomy trigger/kill.
2. **Bounded host control** (`python/helpers/host_control.py` + `usr/governance/host_control.json`) — policy: `permissive` (default) | `allowlist` | `deny`; terminal commands checked in code_execution_tool before execution. Env: `AGENTZ_HOST_CONTROL_POLICY`, `AGENTZ_HOST_CONTROL_ALLOWLIST`, `AGENTZ_HOST_CONTROL_DENYLIST`. Example: `usr/governance/host_control.json.example`.
3. **Phase 2 audit doc** — this file; plus optional docker-compose comment or override for minimal capabilities.

## References

- `.planning/ROADMAP.md` — Phase 2 deliverables.
- `.planning/REQUIREMENTS.md` — PLATFORM-01/02, AUTON-04/05/06, SAFETY-03.
- `.planning/research/SUMMARY.md` — Phase 2 rationale (non-root, no dangerous mounts, capability drop).
