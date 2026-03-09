# Startup Dependencies

This document classifies Agent Zero startup dependencies so operators can tell which missing services should block startup and which should only warn.

## Classification

### Required

- `agent-zero`
  - Core application container.
  - Must start and pass `/health` and `/ready`.
- Persistent runtime data mounts
  - `/a0/usr`, `/a0/.env`, and runtime data directories used by the app.
  - If these are missing or mis-mounted, startup may succeed with the wrong state or fail outright.
- Default Docker Compose network
  - Required for the container itself to start.

### Optional

- `ollama`
  - Optional local model backend.
  - Agent Zero must still start when it is unavailable.
  - Missing `ollama` should produce a warning, not a startup failure.
- `workspace_mcp`
  - Optional Google Workspace MCP sidecar.
  - Missing `workspace_mcp` should produce a warning, not a startup failure.
- `archon_app-network`
  - Optional external Docker network used for direct Archon container-to-container access.
  - Startup should not fail if the network is absent.
  - When present, `startup.sh` attaches `agent-zero` to it after the container starts.

### External Or Selected-Only

- Remote MCP servers configured in `mcp_servers`
  - Validate only when selected by the active runtime config.
- Remote model backends selected by current model settings
  - Examples: Venice, Anthropic, Google, Agent Zero API, remote Ollama hosts.
  - These do not block core app startup.

## Current Startup Behavior

- `docker compose up -d agent-zero` starts only the core service.
- `scripts/setup/startup.sh` then:
  - attaches `archon_app-network` if it exists
  - warns if `ollama` is not running
  - warns if `workspace_mcp` is not running
  - continues waiting on core liveness/readiness either way

## Operator Guidance

- Use `/health` for liveness and `/ready` for startup readiness.
- Use `scripts/show_status.sh` to see runtime drift and readiness state after startup.
- Start optional services separately when needed:
  - `docker compose up -d ollama`
  - `docker compose up -d workspace_mcp`
