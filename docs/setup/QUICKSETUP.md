# Google Workspace MCP — Quick setup (single vs multi-credential)

Short guide for **remote hosts** (and local clients) that want to connect to the Google Workspace MCP server. Choose **single-credential** (one Google account) or **multi-credential** (multiple accounts via OAuth 2.1 bearer tokens).

---

## Where the MCP server runs

- **Same machine as client:** Use `http://localhost:8889/mcp` (or `http://127.0.0.1:8889/mcp`).
- **Client in Docker, server on host:** Use `http://host.docker.internal:8889/mcp` (macOS/Windows) or the host IP on Linux, e.g. `http://192.168.1.10:8889/mcp`.
- **Client and server in same Docker Compose:** Use `http://workspace_mcp:8889/mcp`.
- **Client on a different machine (remote host):** Use the server machine’s IP or hostname and port **8889**, e.g. `http://192.168.1.5:8889/mcp` or `http://mcp.mycompany.local:8889/mcp`. Ensure the server has port 8889 published and the firewall allows it.

---

## Single-credential setup (one Google account)

One Google account for all clients that connect to this server. No bearer token required.

### Server side (once)

1. Set `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` (e.g. in `.env`).
2. Run the server (container or host) and complete **first-time OAuth** in a browser (e.g. run `./scripts/setup/run_workspace_mcp.sh` on the host, use a tool to trigger sign-in, then copy `~/.google_workspace_mcp/*` into the container’s credentials volume).
3. Start the server and expose port **8889** if remote hosts need to connect.

### Client side (remote or local)

Add the MCP server with **URL** and **type** only. No `headers`.

**Example: client on a remote host (server at 192.168.1.5)**

```json
{
  "mcpServers": {
    "google_workspace": {
      "description": "Gmail, Drive, Docs, Sheets, Calendar (single account)",
      "url": "http://192.168.1.5:8889/mcp",
      "type": "streamable-http"
    }
  }
}
```

**Example: client on same machine as server**

```json
"google_workspace": {
  "description": "Google Workspace (local single account)",
  "url": "http://localhost:8889/mcp",
  "type": "streamable-http"
}
```

**Example: Agent Zero in Docker, server on host**

```json
"google_workspace": {
  "url": "http://host.docker.internal:8889/mcp",
  "type": "streamable-http"
}
```

---

## Multi-credential setup (multiple Google accounts)

Multiple users/accounts: each client sends an **Authorization: Bearer &lt;token&gt;** header so the server uses the correct Google account. The server runs with **OAuth 2.1** (`MCP_ENABLE_OAUTH21=true`).

### Server side (once)

1. Same as single-credential: set `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`.
2. Ensure the server is started with **OAuth 2.1** enabled (e.g. in `docker-compose`: `MCP_ENABLE_OAUTH21=true`).
3. Expose port **8889** for remote clients.
4. Each user obtains a **bearer token** (via your IdP or the server’s OAuth 2.1 flow). See [workspacemcp.com/docs](https://workspacemcp.com/docs) for token issuance and session storage.

### Client side (remote or local)

Add the MCP server with **URL**, **type**, and **headers** containing the bearer token for the desired account.

**Example: remote host client using a specific user token**

```json
{
  "mcpServers": {
    "google_workspace": {
      "description": "Gmail, Drive, etc. (user A)",
      "url": "http://192.168.1.5:8889/mcp",
      "type": "streamable-http",
      "headers": {
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
    }
  }
}
```

**Example: second account on same remote server (different token)**

```json
"google_workspace_alice": {
  "description": "Alice's Google Workspace",
  "url": "http://192.168.1.5:8889/mcp",
  "type": "streamable-http",
  "headers": { "Authorization": "Bearer ALICE_TOKEN" }
},
"google_workspace_bob": {
  "description": "Bob's Google Workspace",
  "url": "http://192.168.1.5:8889/mcp",
  "type": "streamable-http",
  "headers": { "Authorization": "Bearer BOB_TOKEN" }
}
```

**Example: Agent Zero (Docker) with multi-user token**

```json
"google_workspace": {
  "url": "http://workspace_mcp:8889/mcp",
  "type": "streamable-http",
  "headers": { "Authorization": "Bearer YOUR_USER_TOKEN" }
}
```

Replace `YOUR_USER_TOKEN`, `ALICE_TOKEN`, `BOB_TOKEN` with real tokens from your OAuth 2.1 flow or IdP. Do not commit tokens to git.

---

## Checklist for remote hosts

| Step | Single-credential | Multi-credential |
|------|-------------------|------------------|
| Server has `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` | ✅ | ✅ |
| Server has completed first-time Google OAuth (credentials dir) | ✅ | ✅ (or per-user via OAuth 2.1) |
| Server has `MCP_ENABLE_OAUTH21=true` | Optional | ✅ |
| Port 8889 reachable from client (firewall, publish port) | ✅ | ✅ |
| Client config: `url` + `type: "streamable-http"` | ✅ | ✅ |
| Client config: `headers.Authorization: Bearer <token>` | ❌ | ✅ |

---

## Securing tokens

- **Server:** Restrict the credentials directory on the host: `chmod 700 workspace-mcp-credentials` (or `credentials/` in the standalone repo). The container runs as non-root user `mcp`.
- **Bearer tokens (multi-user):** Use **HTTPS** for the MCP URL in production so tokens are not sent in clear text; put the server behind a reverse proxy with TLS. Store tokens in a secrets manager or env, not in committed config.
- **Network:** If port 8889 is exposed, restrict it with a firewall (e.g. allow only trusted IPs or VPN). Full guidance: [docker/workspace-mcp/SECURITY.md](../../docker/workspace-mcp/SECURITY.md) (AgentZ) or the standalone repo’s SECURITY.md.

---

## Troubleshooting

- **Connection refused:** Check that the server is running and port 8889 is published and not blocked by a firewall.
- **406 Not Acceptable:** Client must use streamable HTTP; set `"type": "streamable-http"`.
- **401 / auth errors (multi-user):** Ensure the request includes `Authorization: Bearer <valid_token>` and the token is valid for the server’s OAuth 2.1 configuration.
- **Single-credential not working after enabling OAuth 2.1:** Some deployments require a bearer token for all requests when OAuth 2.1 is on; use one shared token for the single account or see [workspacemcp.com/docs](https://workspacemcp.com/docs).

---

## See also

- [Google Workspace MCP container](GOOGLE_WORKSPACE_MCP_CONTAINER.md) — Container setup and first-time OAuth
- [MCP Setup guide](../guides/mcp-setup.md) — Full MCP configuration and tool tiers
- [workspacemcp.com/docs](https://workspacemcp.com/docs) — OAuth 2.1, token issuance, and session storage
