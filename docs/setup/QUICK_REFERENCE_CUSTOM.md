# Quick Reference - File Locations

## Common Scripts

### Setup & Configuration
- `./startup.sh` - Start Agent Zero (GitHub check, graceful stop, start, health wait, status + settings)
- `./scripts/setup/configure_mcp_token.sh` - Configure MCP token
- `./scripts/setup/setup_claude_oauth.sh` - Setup Claude OAuth

### Model Presets & Status
- `./MODELS.sh <preset>` - Switch model preset (e.g. `ollama`, `ollama-dual`, `ollama-glm-claude`). Use `A0_USR_PATH=/path/to/volume ./MODELS.sh ollama` to write to volume.
- `./MODELS.sh --status` - Show container status and current model settings (same as end of startup).
- `./restart.sh` - Restart container and wait for `/health` (use after MODELS.sh or .env change).
- `./scripts/show_status.sh` - Container, health, Web UI, VNC, Settings (chat/util/browser), access URLs.

### Archon task sync (REST API)
- **`ARCHON_API_URL`** — Optional; default `http://localhost:8181`. Archon must be running (e.g. `./start_all.sh --archon`).
- `python scripts/archon_api_tasks.py list` — List all tasks.
- `python scripts/archon_api_tasks.py list --project-id 610ae854-2244-4cb8-a291-1e31561377ab` — List A0 SIP project tasks.
- `python scripts/archon_api_tasks.py create --project-id UUID --title "..." [--description "..." [--feature "..."]]` — Create a task.
- `python scripts/archon_api_tasks.py update TASK_ID --status done [--description "..."]` — Update a task (status: todo | doing | review | done).

### Testing & Validation
- `./scripts/testing/validate.sh` - Run validation
- `./scripts/testing/test_claude_integration.sh` - Test Claude integration

### Google Workspace MCP (container)
- **Service:** `workspace_mcp` — Gmail, Drive, Docs, Sheets, Calendar. URL: `http://workspace_mcp:8889/mcp`, type: `streamable-http`.
- **First-time:** Run `./scripts/setup/run_workspace_mcp.sh` on host once for OAuth, then `cp -r ~/.google_workspace_mcp/* workspace-mcp-credentials/` and `docker compose up -d`. See [docs/setup/GOOGLE_WORKSPACE_MCP_CONTAINER.md](docs/setup/GOOGLE_WORKSPACE_MCP_CONTAINER.md).

### Health
- **`GET /health`** - No-auth health check (200 OK). Used by Docker healthcheck and `restart.sh`; avoids 302s from unauthenticated curl.

## Documentation

- Main docs: `docs/`
- Setup guides: `docs/guides/`
- Integration: `docs/integration/`
- Troubleshooting: `docs/troubleshooting/`

## Authentication & LAN Access

| Variable | Purpose | Notes |
|----------|---------|-------|
| `AUTH_LOGIN` | Web UI username | Stored in `.env` only |
| `AUTH_PASSWORD` | Web UI password | Stored in `.env` only |
| `ALLOWED_ORIGINS` | Permitted origins for CSRF | **Comma-separated** (not semicolons) |

**LAN access requires** either `AUTH_LOGIN` set or your IP in `ALLOWED_ORIGINS`.

**Default origins** (when `ALLOWED_ORIGINS` not set): `*://localhost:*`, `*://127.0.0.1:*`, `*://0.0.0.0:*`

**Example `.env`**:
```bash
AUTH_LOGIN=th3rdai
AUTH_PASSWORD=your_password
ALLOWED_ORIGINS=*://localhost:*,*://127.0.0.1:*,*://0.0.0.0:*,*://192.168.50.7:*
```

## HTTP vs HTTPS (MCP / A2A / Web UI)

| Variable | Purpose | Where |
|----------|---------|-------|
| **`AGENT_ZERO_HTTP_ONLY`** | Set to `1` to serve **HTTP only** (no TLS). Use `http://` in MCP/A2A URLs; no cert setup. **Default in this repo.** | `docker-compose.yml` `environment:` |
| `AGENT_ZERO_CERT_IPS` | LAN IPs to add to TLS cert SAN (only when not using HTTP-only) | `docker-compose.yml` `environment:` |
| `AGENT_ZERO_REGENERATE_CERT` | Set to `1` once to regenerate cert (then remove) | `docker-compose.yml` `environment:` |

- **HTTP mode** (`AGENT_ZERO_HTTP_ONLY=1`): Use `http://<host>:8888` for Web UI, MCP, and A2A. No certificate or Cursor launcher needed.
- **HTTPS mode** (env unset): Use `https://<host>:8888`. For remote MCP/A2A, add your LAN IP to `AGENT_ZERO_CERT_IPS` and optionally run `./scripts/setup/trust_agent_zero_cert.sh` and start Cursor with `./scripts/setup/cursor_with_agent_zero_cert.sh`. See [docs/MCP_CURSOR_REMEDIATION.md](docs/MCP_CURSOR_REMEDIATION.md).
- **Browser microphone:** Browsers allow microphone only in secure contexts (HTTPS or **http://localhost**). If you open the Web UI at `http://<LAN-IP>:8888`, the mic will be blocked. Use **http://localhost:8888** on the same machine, or enable HTTPS (comment out `AGENT_ZERO_HTTP_ONLY=1` in docker-compose) and run **`docker compose up -d --force-recreate agent-zero`** so the container gets the new env, then open **https://&lt;host&gt;:8888** (accept the self-signed cert once).
- **Cloudflare (Flare) tunnel:** Works when the app is in **HTTP** mode: the tunnel connects to `http://localhost:80` inside the container. If you enable HTTPS, the app serves TLS on port 80, so the built-in Flare tunnel (flaredantic) will fail to connect unless the tunnel code is updated to use an HTTPS origin with `noTLSVerify` (not currently supported by flaredantic). For remote access with HTTPS enabled, use a **separate** cloudflared run (e.g. `cloudflared tunnel --url https://localhost:80 --no-tls-verify`) or keep HTTP mode and use the in-app Flare tunnel.

## Settings Persistence

| Data | Location | Persisted via |
|------|----------|---------------|
| **Host repo (own code)** | `/git/agent-zero` in container | Bind mount `.:/git/agent-zero` (run compose from repo root) |
| Auth, API keys | `.env` | Bind mount `./.env:/a0/.env` |
| Model/agent config | `tmp/settings.json` | Bind mount `./tmp:/a0/tmp` |
| Memory & chats | `memory/` | Bind mount `./memory:/a0/memory` |
| Claude OAuth | `claude-config/` | Bind mount `./claude-config:/root/.config/claude-code` |

## See Also

- `docs/status/RESPONSES.md` - Claude ↔ Cursor handoff (decisions, implemented, remediations)
- `conf/models/A0_OLLAMA.md` - Ollama presets, GLM :32k, MODELS.sh --status
- `MIGRATION_GUIDE.md` - Full migration guide
- `scripts/README.md` - Scripts directory guide
- `docs/README.md` - Documentation guide
