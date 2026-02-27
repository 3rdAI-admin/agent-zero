# MCP Settings and Cursor Remediation

Quick reference for fixing MCP server communication in Cursor when servers show as errored or fail to connect.

## HTTP-only mode (no cert issues)

This repo sets **`AGENT_ZERO_HTTP_ONLY=1`** in docker-compose so Agent Zero serves **HTTP** only. Use **`http://`** in MCP and A2A URLs (e.g. `http://192.168.50.7:8888/mcp/t-<TOKEN>/sse`). No certificate setup or Cursor launcher needed. Restart the container after changing the env, then reload MCP.

---

## One-time fix for Agent Zero “self signed certificate” (when using HTTPS)

So that **Cursor MCP and A2A** work without ongoing TLS errors:

1. **Ensure Agent Zero is running** and its TLS cert includes your host IP (in `docker-compose.yml`: `AGENT_ZERO_CERT_IPS=192.168.50.7` or your LAN IP; if you changed it, uncomment `AGENT_ZERO_REGENERATE_CERT=1`, restart once, then comment it out again).

2. **Export and trust the cert** (from repo root):
   ```bash
   ./scripts/setup/trust_agent_zero_cert.sh
   ```
   This copies the server cert to `tmp/agent-zero-server.crt` and, on macOS, adds it to your login keychain as trusted for SSL.

3. **Start Cursor with the cert trusted** so its MCP client accepts the connection:
   ```bash
   ./scripts/setup/cursor_with_agent_zero_cert.sh
   ```
   Or manually:
   ```bash
   export NODE_EXTRA_CA_CERTS="$(pwd)/tmp/agent-zero-server.crt"
   open -a Cursor
   ```

4. **Reload MCP** in Cursor (or restart Cursor) and check that the Agent Zero server connects.

After this, use the launcher script (or the same `NODE_EXTRA_CA_CERTS` + `open -a Cursor`) whenever you want to use Cursor with Agent Zero MCP/A2A so the cert stays trusted for that process.

## Config locations

| Scope   | File |
|--------|------|
| User   | `~/.cursor/mcp.json` — Cursor reads this for all projects unless overridden. |
| Project| `.mcp.json` in repo root — can override or add servers for this project. |

## Schema consistency

Use the **same key** for transport type so Cursor parses all servers correctly:

- **URL-based servers** (Archon, crawl4ai-rag, Agent Zero): use `"transport"` and `"url"`.
  - Values: `"http"`, `"sse"`, or `"streamable-http"`.
- **Stdio servers** (e.g. Playwright): use `"command"` and `"args"` (no `transport`).

Example:

```json
{
  "mcpServers": {
    "archon": {
      "transport": "http",
      "url": "http://192.168.50.7:8051/mcp"
    },
    "agent-zero": {
      "transport": "sse",
      "url": "https://192.168.50.7:8888/mcp/t-<TOKEN>/sse"
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

Avoid mixing `"type"` and `"transport"` for the same kind of server; stick to `"transport"` for HTTP/SSE.

## If a server shows “errored” in Cursor

1. **Check Cursor MCP status**  
   Settings → Tools & MCP → inspect the server; note the exact error (connection failed, SSL, timeout, etc.).

2. **Agent Zero (HTTPS, self-signed cert)**  
   See [MCP_CLIENT_CONNECTION.md](./MCP_CLIENT_CONNECTION.md). In short:
   - Use **https** and URL `https://<host>:8888/mcp/t-<TOKEN>/sse`.
   - Token must match exactly (case-sensitive); get it from Web UI → Settings → MCP Server.
   - **If Cursor logs show `fetch failed: self signed certificate` or `SSE error: ... self signed certificate`**, use one of the fixes in the next section.

3. **Archon / crawl4ai-rag (HTTP)**  
   - Confirm the host and port are reachable from your machine (e.g. `http://192.168.50.7:8051/mcp` or `127.0.0.1`).
   - Ensure the service is running and the path is correct (`/mcp` for Archon, `/sse` for crawl4ai-rag SSE).

4. **Reload config**  
   After editing `~/.cursor/mcp.json` or `.mcp.json`, restart Cursor or use “Reload” for MCP so the new config is applied.

## Cursor + Agent Zero: “self signed certificate” in MCP logs

When the MCP log shows **`user-agent-zero`** or **`user-agent-zero-http`** with:

- `Client error for command fetch failed`
- `SSE error: TypeError: fetch failed: self signed certificate`
- `Error connecting to streamableHttp server, falling back to SSE` then the same SSL error

Cursor is rejecting Agent Zero’s HTTPS because the server uses a **self-signed certificate**. Try these in order:

1. **Cursor Settings**
   - Open **Settings → Tools & MCP** (or search “MCP” / “HTTP”).
   - If present, enable **“HTTP: Electron Fetch”** or **“HTTP: Fetch Additional Support”** (some users report this avoids the need to trust the cert).
   - If present, enable **“System Certificates”** so Cursor uses your system trust store.

2. **Trust the server certificate**
   - Export the cert:  
     `docker cp agent-zero:/etc/ssl/agent-zero/server.crt ./agent-zero-server.crt`
   - Add it to your **system keychain** (macOS: Keychain Access → add `agent-zero-server.crt` and set to “Always Trust” for SSL), or
   - Point Cursor at it via env (before launching Cursor):  
     `export SSL_CERT_FILE=/path/to/agent-zero-server.crt`  
     (or `SSL_CERT_DIR` to a directory containing the cert).  
   - Ensure the cert’s **CN/SAN** matches the host you use (e.g. `192.168.50.7` or the hostname). If it only has localhost, set `AGENT_ZERO_CERT_IPS=192.168.50.7` in the Agent Zero env and recreate the container so the cert is regenerated.

3. **Last resort (insecure)**  
   Launch Cursor with TLS verification disabled for the process:  
   `NODE_TLS_REJECT_UNAUTHORIZED=0 open -a Cursor`  
   (Only for local/dev; do not use on untrusted networks.)

After any change, **reload MCP** or restart Cursor and check the MCP log again.

## Cursor + Archon: “Request timed out” / “falling back to SSE” / “operation was aborted”

When the MCP log shows:

- `Creating streamableHttp transport` → `Connecting to streamableHttp server` → `Request timed out`
- `Error connecting to streamableHttp server, falling back to SSE`
- `Connecting to SSE server` → `Client error for command This operation was aborted`
- `No server info found` / `Server creation in progress`

Archon’s MCP server uses **streamable HTTP only** at `http://<host>:8051/mcp` (no SSE). Cursor tries streamable HTTP first, then falls back to SSE; the timeout or abort usually means:

1. **Archon not ready yet** – archon-mcp starts only after archon-server is healthy. Wait for `./startup.sh` (or `docker compose up`) to finish and show “Archon startup complete”, then reload MCP.
2. **Wrong URL** – Use the **streamable HTTP** URL: `http://<host>:8051/mcp` (path `/mcp`). In Cursor MCP config use `"transport": "streamable-http"` and `"url": "http://localhost:8051/mcp"` (or your host IP). Do not use `/sse` for Archon.
3. **First connection slow** – The first request can be slow while the server initializes. Reload MCP once Archon has been up for 30–60 seconds.

**Check Archon is up:** `curl -s -o /dev/null -w "%{http_code}" http://localhost:8051/health` (or your Archon host). Then reload MCP in Cursor.

## Summary

- Normalize config: use `transport` + `url` for remote servers, `command` + `args` for stdio.
- For Agent Zero: follow [MCP_CLIENT_CONNECTION.md](./MCP_CLIENT_CONNECTION.md) (HTTPS, token, TLS).
- Fix host/port and TLS in Cursor, then reload MCP.
