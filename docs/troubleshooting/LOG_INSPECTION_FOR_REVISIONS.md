# Log inspection for troubleshooting revisions

When making changes to Agent Zero (compose, mounts, MCP, TLS, scripts), use logs to confirm behavior and catch regressions.

## What to inspect

### 1. Container logs (stdout/stderr)

```bash
# Last N lines
docker logs agent-zero --tail 200

# Follow live
docker logs -f agent-zero

# Search for server errors (excludes agent "thought" text)
docker logs agent-zero 2>&1 | grep -E "ERROR|Traceback|Exception|werkzeug|SSLError"
```

**Revisions to verify:**

| Change | What to check in logs |
|--------|------------------------|
| Repo mount `.:/git/agent-zero` | From host: `docker exec agent-zero ls /git/agent-zero` — should list repo (README.md, docker-compose.yml, etc.). No log line specifically confirms mount; use `docker exec` to verify. |
| MCP / TLS cert | `ERROR [werkzeug]` + `ssl.SSLError` — usually means a client closed the connection before the server finished writing (e.g. MCP client not reading SSE stream). Not necessarily a server bug. |
| Startup script (REPO_ROOT) | Run `./scripts/setup/startup.sh` from repo root; it should `cd` to repo root and run `docker compose` there. No direct log; verify by checking that after startup, `docker exec agent-zero ls /git/agent-zero` shows the repo. |
| run_ui / Web UI | With HTTP-only (`AGENT_ZERO_HTTP_ONLY=1`): look for `Starting server at http://0.0.0.0:80 ... (AGENT_ZERO_HTTP_ONLY)`. With HTTPS: `Starting server at https://0.0.0.0:80`. Also check `Preload completed` and `success: run_ui entered RUNNING state`. If you see `WARN stopped: run_ui (terminated by SIGTERM)` followed by `spawned: 'run_ui'`, the process restarted (e.g. after cert reload). |

### 2. Session logs (on host)

- **Path:** `./logs` in the repo (e.g. `logs/log_YYYYMMDD_HHMMSS.html`).
- **Content:** Saved Web UI session output (HTML). Use for user-facing errors or agent reasoning, not for server stack traces.

### 3. Healthcheck

- With HTTP-only, healthcheck uses `curl -fsS http://localhost`. With HTTPS, it would use `https://localhost`.
- If the Web UI and MCP work, "unhealthy" is often a healthcheck configuration issue, not a failure of our revisions.

## Do I have communications with Agent Zero?

**No.** In this setup (Cursor chat with the AgentZ repo), there is no live MCP or A2A connection from this assistant to the Agent Zero container. This assistant can:

- **Read/write** files in the repo.
- **Run commands** on the host (e.g. `docker logs`, `docker exec`, `curl` to the API).
- **Inspect** container filesystem and logs.

It cannot send a prompt to Agent Zero or receive Agent Zero’s reply unless you paste that reply here or we use a script/curl to call an HTTP endpoint and you use that output.

To have an AI "talk to" Agent Zero directly, you would:

- Add Agent Zero as an **MCP server** in Cursor (or another client) and use a chat where that client has the Agent Zero MCP enabled, or
- Call the **A2A** or **HTTP API** from a script and feed the response into the conversation.

Log inspection is the main way to debug and verify revisions when you don’t have a direct agent-to-agent link.
