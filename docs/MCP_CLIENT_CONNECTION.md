# Connecting MCP Clients to Agent Zero

This guide is for any application (PCI-DSS Assistant, Cursor, Claude Code, or custom MCP clients) that connects to Agent Zero’s MCP server.

## Requirements

| Item | Value |
|------|--------|
| **Scheme** | `https` only (not `http`) |
| **URL (SSE)** | `https://<host>:8888/mcp/t-<TOKEN>/sse` |
| **Token** | From Agent Zero Web UI → Settings → MCP Server (exact, case-sensitive) |
| **TLS** | Server uses a **self-signed certificate** — see below |

## Why connections fail

### 1. TLS certificate verification (most common)

Agent Zero serves HTTPS with a **self-signed** certificate. Many MCP clients verify the server certificate by default and **reject** the connection, which shows up as “Connection failed” or “SSL error.”

**Fix in the client:**

- **Option A:** Disable TLS verification for the Agent Zero host (e.g. “Allow insecure”, “Skip certificate verification”, or the equivalent in your app).
- **Option B:** If the client supports custom CAs, export the server cert from the container and add it as trusted:
  ```bash
  docker cp agent-zero:/etc/ssl/agent-zero/server.crt ./agent-zero-server.crt
  ```
  Then configure the client to trust `agent-zero-server.crt` for `https://<host>:8888`.

If you cannot change the client (e.g. no “insecure” option), the only option is to make the client trust the cert (Option B) or run a reverse proxy in front of Agent Zero that presents a trusted certificate.

**Works on localhost but not remote host:** The default cert only includes localhost/127.0.0.1. When the client connects to `https://192.168.50.7:8888`, the cert does not match that IP. Add your host LAN IP to the cert: set `AGENT_ZERO_CERT_IPS=192.168.50.7` in docker-compose environment (or .env), then `docker compose down && docker compose up -d` so the cert is regenerated with that IP. See `docker/run/fs/exe/generate_ssl_cert.sh`.

### 2. Wrong token

The token in the URL must match exactly (case-sensitive). For example `11mu_QnU**i**EWloEq` (lowercase `i`) is valid; `11mu_QnU**I**EWloEq` (capital `I`) returns 401 and is often reported as “connection failed.”

Get the current token from:

- Agent Zero Web UI → **Settings → MCP Server**, or  
- Inside the container: `docker exec agent-zero cat /a0/tmp/settings.json` (see `mcp_server_token`; if empty, use the token shown in the Web UI).

### 3. Using HTTP instead of HTTPS

The server only responds on **HTTPS**. Plain `http://...:8888/...` gets an empty reply and looks like a connection failure. Always use `https://` in the client URL.

### 4. Connection OK but "0 tools" / tools not loading

If the SSE stream connects (e.g. "SSE stream active") but **Discovered Remote Tools** shows **0 tools** and **Error** for agent-zero:

- **URL path must be `/mcp/`** – A typo like `/scp/` instead of `/mcp/` will break tool discovery. Use `https://<host>:8888/mcp/t-<TOKEN>/sse`.
- **Token** – Use the exact token (e.g. `11mu_QnUJiEWloEq` with lowercase **m** and **i**). A wrong character (e.g. `11nu_` or `11mu_QnUJIEWloEq`) can cause 401 or invalid session.
- **Session ID** – The server assigns a `session_id` in the first SSE event (`data: /mcp/t-.../messages/?session_id=...`). The client **must** use that exact messages URL (including that `session_id`) for all JSON-RPC calls (initialize, tools/list). If the client uses a different or fixed session_id, the server returns 400 "Invalid session ID" and no tools.
- **Responses are on the SSE stream** – For the MCP SSE transport, the server responds to POSTs to the messages URL with **202 Accepted** and sends the actual JSON-RPC response (e.g. `tools/list` result) as **SSE events**. The client must keep the SSE connection open and read those events to get the tool list. If the client only reads the HTTP response body of the POST, it will see "Accepted" and never receive the tools (result: 0 tools / Error).

Server logs may show `ssl.SSLError` when writing if the client closes the SSE connection before the server finishes sending the tool-list response (e.g. client timeout or not reading from the stream).

### 5. Wrong host or network

Use a host that can reach Agent Zero:

- Same machine: `https://localhost:8888/...` or `https://127.0.0.1:8888/...`
- LAN: `https://192.168.50.7:8888/...` (replace with the actual IP of the host running Agent Zero)

If the client runs in Docker or on another server, ensure that host can route to the Agent Zero host and port 8888.

## Verify server from the host

Run the test from the **same environment** where your MCP client runs (same host or same Docker/container).

**Option A – Shell:** `./scripts/setup/check_agent_zero_mcp.sh`

**Option B – Python (TLS verify off):**  
`python3 scripts/testing/test_mcp_connection.py 11mu_QnUJiEWloEq https://192.168.50.7:8888`  
(Use `https://localhost:8888` if the client runs on the same machine as Agent Zero.)

If Option B passes from the PCI app host but the app still fails, the issue is in the app (config, timeout, or SSE handling). If this passes, the server is fine; any remaining “connection failed” in the client is due to TLS verification, token, or URL/host (see above).

## Summary checklist for client config

- [ ] URL uses **https** (not http).
- [ ] URL is `https://<host>:8888/mcp/t-<TOKEN>/sse` (for SSE transport).
- [ ] Token is exact and case-sensitive (from Web UI or container settings).
- [ ] Client is configured to **skip TLS verification** for this host, or to trust the server’s self-signed cert.
- [ ] `<host>` is an address the client can reach (e.g. localhost or the LAN IP of the Agent Zero host).
