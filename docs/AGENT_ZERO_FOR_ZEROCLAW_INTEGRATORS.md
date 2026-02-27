# Agent Zero for ZeroClaw Integrators

This guide is for **ZeroClaw** developers integrating with **Agent Zero** (e.g. calling Agent Zero from ZeroClaw for complex tasks, or bridging channels). It covers entrypoints, authentication, example requests, and recommended constraints.

**Related:** [Connectivity](./connectivity.md) (full API reference), [MCP Client Connection](./MCP_CLIENT_CONNECTION.md), [MCP Cursor Remediation](./MCP_CURSOR_REMEDIATION.md).

---

## Base URL and protocol

- **This repo (AgentZ):** Default is **HTTP only** (`AGENT_ZERO_HTTP_ONLY=1`). Use `http://<host>:<port>` (e.g. `http://localhost:8888` or `http://192.168.50.7:8888`).
- **Token and URLs:** In Agent Zero Web UI go to **Settings → External Services** (and **Settings → MCP Server**) to get your API token and exact MCP/A2A URLs.
- **HTTPS:** If you run without HTTP-only, use `https://` and see the cert docs above for TLS verification.

---

## 1. REST API (recommended for ZeroClaw → Agent Zero)

Use this to send a task to Agent Zero and get a text response. Same token is used for API, MCP, and A2A.

### Authentication

- **Header:** `X-API-KEY: <your_api_token>`
- **Content-Type:** `application/json` for POST bodies.

### `POST /api_message`

Send a message and receive Agent Zero’s response.

| Parameter        | Type   | Required | Description |
|------------------|--------|----------|-------------|
| `message`        | string | Yes      | The task or question for Agent Zero. |
| `context_id`     | string | No       | Existing chat context ID for multi-turn. |
| `attachments`    | array  | No       | `[{ "filename": "...", "base64": "..." }]`. |
| `lifetime_hours` | number | No       | Chat context lifetime in hours (default: **24**). |

**Example (minimal):**

```bash
curl -X POST "http://localhost:8888/api_message" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: YOUR_API_TOKEN" \
  -d '{"message": "List files in the current directory.", "lifetime_hours": 24}'
```

**Example (JSON response):**

- Success: `{ "response": "...", "context_id": "..." }`
- Error: `{ "error": "..." }`

**Example (conversation continuation):**

```json
{
  "context_id": "ctx_from_previous_response",
  "message": "Now summarize that in one sentence.",
  "lifetime_hours": 24
}
```

### `POST /api_message_async` (non-blocking, recommended)

Send a message and return immediately. Poll `/api_message_status` for the result. Use this when you don't want to hold an HTTP connection open for the full agent processing loop (which can take 2+ minutes).

| Parameter        | Type   | Required | Description |
|------------------|--------|----------|-------------|
| `message`        | string | Yes      | The task or question for Agent Zero. |
| `context_id`     | string | No       | Existing chat context ID for multi-turn. |
| `attachments`    | array  | No       | `[{ "filename": "...", "base64": "..." }]`. |
| `lifetime_hours` | number | No       | Chat context lifetime in hours (default: **24**). |

**Example:**

```bash
curl -X POST "http://localhost:8888/api_message_async" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: YOUR_API_TOKEN" \
  -d '{"message": "Analyze the system logs."}'
```

**Response:** `{ "context_id": "abc123", "status": "processing" }`

### `GET/POST /api_message_status`

Poll the status of a task started via `/api_message_async`.

| Parameter     | Type   | Required | Description |
|---------------|--------|----------|-------------|
| `context_id`  | string | Yes      | The context ID from `/api_message_async`. |

**Response:** `{ "context_id": "abc123", "status": "completed", "response": "..." }`

Status values: `processing`, `completed`, `failed`, `idle`, `not_found`.

---

## 2. MCP (Model Context Protocol)

Agent Zero exposes an **MCP server** so ZeroClaw (or any MCP client) can call Agent Zero’s tools (e.g. `send_message`, `code_review`, `web_scan`) over MCP instead of only using the REST message API.

### MCP URLs (HTTP default)

- **SSE:** `http://<host>:<port>/mcp/t-<API_TOKEN>/sse`
- **Streamable HTTP:** `http://<host>:<port>/mcp/t-<API_TOKEN>/http/`

Replace `<API_TOKEN>` with the same token from Settings → External Services.

### Example client config (e.g. for ZeroClaw)

```json
{
  "mcpServers": {
    "agent-zero": {
      "type": "sse",
      "url": "http://localhost:8888/mcp/t-YOUR_API_TOKEN/sse"
    }
  }
}
```

Use `http://` when Agent Zero is running with `AGENT_ZERO_HTTP_ONLY=1`.

---

## 3. A2A (Agent-to-Agent)

For **peer-to-peer agent** communication (FastA2A protocol):

- **URL:** `http://<host>:<port>/a2a/t-<API_TOKEN>`
- Use this when ZeroClaw (or another agent runtime) implements FastA2A and should talk to Agent Zero as another agent.

See [Connectivity](./connectivity.md#a2a-agent-to-agent-connectivity) for HTTPS and certificate notes.

---

## 4. Constraints for ZeroClaw integrators

Recommended when calling Agent Zero from ZeroClaw:

| Concern            | Recommendation |
|--------------------|----------------|
| **Authentication** | Always send `X-API-KEY` for REST; use the same token in MCP and A2A URLs. |
| **Rate limits**    | Implement rate limiting on the ZeroClaw side to avoid overloading Agent Zero and to share resources fairly. |
| **Context lifetime** | Use a bounded `lifetime_hours` (e.g. default **24**) for `/api_message` to manage memory and cleanup. |
| **HTTP vs HTTPS**  | This repo defaults to HTTP; use `http://` in all URLs unless you have configured HTTPS and certs. |

---

## 5. Quick reference

| Integration      | Endpoint / URL pattern | Auth |
|------------------|------------------------|------|
| REST (sync)      | `POST /api_message`    | Header `X-API-KEY` |
| REST (async)     | `POST /api_message_async` | Header `X-API-KEY` |
| REST (poll)      | `GET/POST /api_message_status` | Header `X-API-KEY` |
| MCP (SSE)        | `http://<host>:<port>/mcp/t-<TOKEN>/sse` | Token in URL |
| MCP (HTTP)       | `http://<host>:<port>/mcp/t-<TOKEN>/http/` | Token in URL |
| A2A              | `http://<host>:<port>/a2a/t-<TOKEN>` | Token in URL |

---

## 6. See also

- [Connectivity](./connectivity.md) – Full External API, MCP, and A2A reference with more examples.
- [MCP_CLIENT_CONNECTION.md](./MCP_CLIENT_CONNECTION.md) – Connecting clients (e.g. Cursor) to Agent Zero’s MCP server.
- Agent Zero **Settings → External Services** in the Web UI for your token and URLs.
