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

### First-time setup (OAuth)

1. Add to `.env` (from [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials, Desktop OAuth client):
   - `GOOGLE_OAUTH_CLIENT_ID`
   - `GOOGLE_OAUTH_CLIENT_SECRET`

2. On the host, run the workspace-mcp script once so a browser can complete Google sign-in:
   ```bash
   ./scripts/setup/run_workspace_mcp.sh
   ```
   Use a tool (e.g. list emails) to trigger OAuth, then stop the script (Ctrl+C).

3. Copy credentials for the container:
   ```bash
   mkdir -p workspace-mcp-credentials
   cp -r ~/.google_workspace_mcp/* workspace-mcp-credentials/
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

## See also

- [MCP Setup guide](../guides/mcp-setup.md) — Full MCP configuration, stdio option, and tool tiers
- [docker/workspace-mcp/README.md](../../docker/workspace-mcp/README.md) — Dockerfile and build notes
- [scripts/setup/README.md](../../scripts/setup/README.md) — Host scripts (run_workspace_mcp.sh, add_workspace_mcp_remote.sh)
