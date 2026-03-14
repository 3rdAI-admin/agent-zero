# Security — Google Workspace MCP container

## Implemented

- **Non-root process:** The container runs as user `mcp` (UID 1000), not root. Credentials are mounted at `/home/mcp/.google_workspace_mcp`.
- **No secrets in image:** `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are provided at runtime via `.env` (gitignored). The credentials directory is bind-mounted from the host and is gitignored.
- **Network:** By default the service only exposes port 8889 on the Docker network (no host port), so only containers on the same network can reach it.

## What you should do

### Credentials directory (host)

Restrict who can read the credentials directory on the host:

```bash
chmod 700 workspace-mcp-credentials
```

If the container user is UID 1000, ensure the directory is owned or readable by that user (e.g. `chown 1000:1000 workspace-mcp-credentials` on Linux if needed).

### Bearer tokens (multi-user)

- **In transit:** Use HTTPS for the MCP endpoint so `Authorization: Bearer <token>` is not sent in clear text. Put the server behind a reverse proxy (e.g. nginx, Caddy) with TLS, or expose it only on a private network.
- **At rest:** Store bearer tokens in a secrets manager or environment variables, not in committed config files. Prefer short-lived tokens.

### Exposing port 8889 to the host

If you add `ports: - "8889:8889"` to reach the server from the host or from another machine:

- Restrict access with a firewall (e.g. allow only specific IPs or a VPN).
- Prefer not exposing the port to the public internet; use a VPN or private network for remote clients.

### TLS (production)

For production or untrusted networks, terminate TLS in front of the MCP server. Example with Caddy (place in front of the container):

- Run Caddy with a config that proxies `https://mcp.example.com` to `http://workspace_mcp:8889` (or `http://localhost:8889` if Caddy is on the host).
- Clients then use `https://mcp.example.com/mcp` with type `streamable-http`.

See [PRODUCTION.md](PRODUCTION.md) for HTTPS (Caddy/nginx), firewall, and production checklist.
