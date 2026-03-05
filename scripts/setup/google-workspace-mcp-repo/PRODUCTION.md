# Production checklist — Google Workspace MCP

Use this after the [README](README.md) and [SECURITY](SECURITY.md) setup.

## Done for you

- [x] Container runs as non-root user `mcp`.
- [x] Credentials directory: run `chmod 700 workspace-mcp-credentials` on the host if you haven’t.

## Your next steps

### 1. HTTPS (recommended for remote or multi-user)

Put the MCP server behind a reverse proxy with TLS so bearer tokens are not sent in clear text.

**Example: Caddy (on the same host as Docker)**

- Install [Caddy](https://caddyserver.com/docs/install).
- If the MCP server is exposed on the host as `localhost:8889`, use a Caddyfile like:

```caddyfile
mcp.example.com {
    reverse_proxy localhost:8889
}
```

- Run Caddy (e.g. `caddy run --config Caddyfile` or via systemd). Clients then use `https://mcp.example.com/mcp` with type `streamable-http`.
- If the MCP server runs only inside Docker and you want Caddy in Docker too, add a Caddy service to `docker-compose.yml` that proxies to `http://workspace_mcp:8889` and publish Caddy’s HTTPS port (443) on the host.

**Example: nginx**

```nginx
server {
    listen 443 ssl;
    server_name mcp.example.com;
    ssl_certificate     /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    location / {
        proxy_pass http://localhost:8889;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Restrict port 8889 (if exposed)

If you added `ports: - "8889:8889"` in `docker-compose.yml`:

- **Linux (ufw):** e.g. `sudo ufw allow from 192.168.1.0/24 to any port 8889` then `sudo ufw enable`.
- **macOS:** Use the Application Firewall or restrict in your network/router so only trusted IPs can reach 8889.
- Prefer not binding 8889 to the public internet; use a VPN or private network for remote clients.

### 3. Bearer tokens (multi-user)

- Store tokens in a secrets manager or env vars; do not commit them.
- Prefer short-lived tokens and rotate them periodically.
- See [workspacemcp.com/docs](https://workspacemcp.com/docs) for OAuth 2.1 token issuance.

### 4. Optional: don’t expose 8889 to the host

If all clients run in the same Docker network (e.g. Agent Zero in the same stack), leave the service with only `expose: - "8889"` and no `ports:` so nothing is published on the host. Remote clients then reach a gateway that proxies to `workspace_mcp:8889` internally.

---

Quick ref: [SECURITY.md](SECURITY.md) · [README.md](README.md)
