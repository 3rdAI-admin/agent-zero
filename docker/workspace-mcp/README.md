# Google Workspace MCP (containerized)

This service runs the [Google Workspace MCP](https://workspacemcp.com/) server in streamable-HTTP mode so Agent Zero can use Gmail, Drive, Docs, Sheets, Calendar, and related tools.

## When to use

- **Container (this service):** Use when you run Agent Zero with `docker compose up`. Agent Zero connects to `http://workspace_mcp:8889/mcp` on the same Docker network. No need to run a script on the host.
- **Host script:** Use `./scripts/setup/run_workspace_mcp.sh` when Agent Zero is in Docker but you prefer the MCP server on the host (e.g. for easier OAuth in a browser). Agent Zero then uses `http://host.docker.internal:8889/mcp`.

## First-time OAuth (container)

The MCP server needs Google OAuth tokens. The container runs as non-root user `mcp` and reads credentials from `/home/mcp/.google_workspace_mcp`, which is bind-mounted from `./workspace-mcp-credentials` on the repo root. Restrict host permissions: `chmod 700 workspace-mcp-credentials` (see [SECURITY.md](SECURITY.md)).

1. **One-time setup on the host** (so a browser can complete OAuth):
   - Ensure `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are in `.env` (from [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials, Desktop OAuth client).
   - Run: `./scripts/setup/run_workspace_mcp.sh`
   - When prompted, use a tool (e.g. list emails) so the server opens a browser to sign in with Google. After authorizing, the server will store tokens in `~/.google_workspace_mcp/`.
   - Stop the script (Ctrl+C).

2. **Copy credentials into the directory used by the container:**
   ```bash
   mkdir -p workspace-mcp-credentials
   cp -r ~/.google_workspace_mcp/* workspace-mcp-credentials/
   ```

3. **Start the stack** (including `workspace_mcp`):
   ```bash
   docker compose up -d
   ```

4. **In Agent Zero (Settings → MCP):** Add a server with:
   - **URL:** `http://workspace_mcp:8889/mcp`
   - **Type:** `streamable-http`

Subsequent `docker compose up` will reuse the same credentials; re-copy only if you re-authenticate on the host or clear `workspace-mcp-credentials/`.

## Multi-user (OAuth 2.1)

The service runs with **OAuth 2.1 multi-user** enabled (`MCP_ENABLE_OAUTH21=true`). Multiple Google accounts can be used at once: each MCP client sends an `Authorization: Bearer <token>` header so the server can associate requests with a user and that user's credentials.

- **Single account (no header):** You can still use one account by completing the legacy first-time OAuth flow above; some clients may work without a bearer token in default/legacy mode.
- **Multiple accounts:** Each user obtains a bearer token (via the server’s OAuth 2.1 flow or your external IdP). In Agent Zero, add the server with a `headers` object containing the token, e.g. `"headers": { "Authorization": "Bearer <token>" }`. See [workspacemcp.com/docs](https://workspacemcp.com/docs) for token issuance and session storage options.

## Environment

- `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` (from `.env`) are required for OAuth.
- `WORKSPACE_MCP_PORT=8889` is set in the Dockerfile and compose; the service listens on 8889 inside the network.
- `MCP_ENABLE_OAUTH21=true` enables OAuth 2.1 multi-user (bearer-token auth).

## Optional: expose port on the host

To reach the MCP server from the host (e.g. for debugging), add under `workspace_mcp` in `docker-compose.yml`:

```yaml
ports:
  - "8889:8889"
```

Then you can use `http://localhost:8889/mcp` or `http://host.docker.internal:8889/mcp` from Agent Zero if you prefer. Restrict port 8889 with a firewall when exposing to the network; see [SECURITY.md](SECURITY.md).
