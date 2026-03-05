# Google Workspace MCP server

This repository contains the **Google Workspace MCP** server setup: Docker image, compose, and host-run script. Use it with [Agent Zero](https://github.com/agent0ai/agent-zero) or any MCP client that supports streamable HTTP.

- **Upstream:** [workspacemcp.com](https://workspacemcp.com/) — Gmail, Drive, Docs, Sheets, Slides, Calendar, Tasks.
- **Transport:** streamable HTTP (default port 8889).

## Quick start (Docker)

1. **OAuth credentials** — Create a Desktop OAuth client in [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials. Copy Client ID and Secret.

2. **Configure env:**
   ```bash
   cp .env.example .env
   # Edit .env: set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET
   ```

3. **First-time OAuth (browser on host):**
   ```bash
   ./scripts/run_workspace_mcp.sh
   ```
   Use a tool (e.g. list emails) to trigger sign-in; after authorizing, stop (Ctrl+C).

4. **Copy credentials for the container:**
   ```bash
   mkdir -p workspace-mcp-credentials
   cp -r ~/.google_workspace_mcp/* workspace-mcp-credentials/
   chmod 700 workspace-mcp-credentials
   ```

5. **Start the server:**
   ```bash
   docker compose up -d
   ```

6. **Connect from your MCP client** (e.g. Agent Zero):
   - **Same Docker network:** `http://workspace_mcp:8889/mcp` (type: `streamable-http`)
   - **From host:** `http://localhost:8889/mcp` (add `ports: - "8889:8889"` under the service in `docker-compose.yml` if needed)
   - **From another host (Agent Zero in Docker):** `http://host.docker.internal:8889/mcp`

## Host-only (no Docker)

```bash
export GOOGLE_OAUTH_CLIENT_ID=...
export GOOGLE_OAUTH_CLIENT_SECRET=...
# or use .env: source .env before running
./scripts/run_workspace_mcp.sh
```

Requires `uvx` (install [uv](https://docs.astral.sh/uv/): `pip install uv` or `brew install uv`).

## Multi-user (OAuth 2.1)

The container runs with `MCP_ENABLE_OAUTH21=true`. Multiple Google accounts: each client sends `Authorization: Bearer <token>`. See [workspacemcp.com/docs](https://workspacemcp.com/docs) for token issuance.

## Security

- Restrict credentials: `chmod 700 workspace-mcp-credentials`
- See [SECURITY.md](SECURITY.md) and [PRODUCTION.md](PRODUCTION.md) for TLS, firewall, and production checklist.
