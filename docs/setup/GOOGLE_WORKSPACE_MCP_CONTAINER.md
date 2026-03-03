# Google Workspace MCP container

Agent Zero can use the [Google Workspace MCP](https://workspacemcp.com/) server (Gmail, Drive, Docs, Sheets, Calendar, Tasks, etc.) in two ways: **containerized** (recommended with Docker Compose) or **on the host**.

## Container service: `workspace_mcp`

When you run `docker compose up`, the **`workspace_mcp`** service starts alongside Agent Zero. No need to run a separate script on the host after one-time OAuth setup.

| Item | Value |
|------|--------|
| **Service name** | `workspace_mcp` |
| **Container name** | `workspace_mcp` |
| **URL (from Agent Zero)** | `http://workspace_mcp:8889/mcp` |
| **Type** | `streamable-http` |
| **Port** | 8889 (internal; not exposed to host by default) |
| **Multi-user** | OAuth 2.1 enabled (`MCP_ENABLE_OAUTH21=true`); clients can pass `Authorization: Bearer <token>` to use different Google accounts. |

### First-time setup (OAuth)

1. Add to `.env` (from [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials, Desktop OAuth client):
   - `GOOGLE_OAUTH_CLIENT_ID`
   - `GOOGLE_OAUTH_CLIENT_SECRET`

2. On the host, run the workspace-mcp script once so a browser can complete Google sign-in:
   ```bash
   ./scripts/setup/run_workspace_mcp.sh
   ```
   Use a tool (e.g. list emails) to trigger OAuth, then stop the script (Ctrl+C).

3. Copy credentials for the container and restrict permissions:
   ```bash
   mkdir -p workspace-mcp-credentials
   cp -r ~/.google_workspace_mcp/* workspace-mcp-credentials/
   chmod 700 workspace-mcp-credentials
   ```

4. Start the stack: `docker compose up -d`

5. In Agent Zero: **Settings → MCP/A2A → External MCP Servers → Open**. Add:
   ```json
   "google_workspace": {
     "description": "Gmail, Drive, Docs, Sheets, Calendar (container)",
     "url": "http://workspace_mcp:8889/mcp",
     "type": "streamable-http"
   }
   ```

### Optional: expose port 8889 on the host

To reach the MCP server from the host (e.g. for debugging), add under the `workspace_mcp` service in `docker-compose.yml`:

```yaml
ports:
  - "8889:8889"
```

Then you can use `http://localhost:8889/mcp` or `http://host.docker.internal:8889/mcp`.

## Host-run alternative

If you prefer the MCP server on the host (e.g. for easier OAuth in a browser):

1. Run on the host: `./scripts/setup/run_workspace_mcp.sh` (default port 8889).
2. In Agent Zero, add a server with URL: `http://host.docker.internal:8889/mcp` and type `streamable-http`.

Optional: `./scripts/setup/add_workspace_mcp_remote.sh` inserts this server into settings automatically.

## Multi-user (OAuth 2.1)

The container runs with **OAuth 2.1 multi-user** enabled. Multiple Google accounts are supported: each client sends `Authorization: Bearer <token>` so the server uses the correct user’s credentials. Obtain tokens via the server’s OAuth 2.1 flow or set `EXTERNAL_OAUTH21_PROVIDER=true` and validate tokens from your own IdP. Details: [workspacemcp.com/docs](https://workspacemcp.com/docs).

## Security

- The container runs as **non-root** user `mcp`; credentials are at `/home/mcp/.google_workspace_mcp`.
- Restrict the host credentials dir: `chmod 700 workspace-mcp-credentials`.
- For bearer tokens (multi-user), use **HTTPS** in production and store tokens in a secrets manager. Restrict port 8889 with a firewall if exposed. See **[docker/workspace-mcp/SECURITY.md](../../docker/workspace-mcp/SECURITY.md)** and **[docker/workspace-mcp/PRODUCTION.md](../../docker/workspace-mcp/PRODUCTION.md)** for details, TLS/reverse-proxy examples (Caddy/nginx), and a production checklist.

## See also

- **[Quick setup: single vs multi-credential (remote hosts)](./QUICKSETUP.md)** — Client config examples for local and remote hosts
- [MCP Setup guide](../guides/mcp-setup.md) — Full MCP configuration, stdio option, and tool tiers
- [docker/workspace-mcp/README.md](../../docker/workspace-mcp/README.md) — Dockerfile and build notes
- [scripts/setup/README.md](../../scripts/setup/README.md) — Host scripts (run_workspace_mcp.sh, add_workspace_mcp_remote.sh)
