# Quick Reference - File Locations

## Common Scripts

### Setup & Configuration
- `./scripts/setup/startup.sh` - Start Agent Zero
- `./scripts/setup/configure_mcp_token.sh` - Configure MCP token
- `./scripts/setup/setup_claude_oauth.sh` - Setup Claude OAuth

### Testing & Validation
- `./scripts/testing/validate.sh` - Run validation
- `./scripts/testing/test_claude_integration.sh` - Test Claude integration

### Via Symlinks (Convenience)
- `./startup.sh` → `scripts/setup/startup.sh`
- `./validate.sh` → `scripts/testing/validate.sh`

## Documentation

- Main docs: `docs/`
- Setup guides: `docs/guides/`
- Integration: `docs/integration/`
- Troubleshooting: `docs/troubleshooting/`

## Authentication & LAN Access

| Variable | Purpose | Notes |
|----------|---------|-------|
| `AUTH_LOGIN` | Web UI username | Stored in `.env` only |
| `AUTH_PASSWORD` | Web UI password | Stored in `.env` only |
| `ALLOWED_ORIGINS` | Permitted origins for CSRF | **Comma-separated** (not semicolons) |

**LAN access requires** either `AUTH_LOGIN` set or your IP in `ALLOWED_ORIGINS`.

**Default origins** (when `ALLOWED_ORIGINS` not set): `*://localhost:*`, `*://127.0.0.1:*`, `*://0.0.0.0:*`

**Example `.env`**:
```bash
AUTH_LOGIN=th3rdai
AUTH_PASSWORD=your_password
ALLOWED_ORIGINS=*://localhost:*,*://127.0.0.1:*,*://0.0.0.0:*,*://192.168.50.7:*
```

## HTTP vs HTTPS (MCP / A2A / Web UI)

| Variable | Purpose | Where |
|----------|---------|-------|
| **`AGENT_ZERO_HTTP_ONLY`** | Set to `1` to serve **HTTP only** (no TLS). Use `http://` in MCP/A2A URLs; no cert setup. **Default in this repo.** | `docker-compose.yml` `environment:` |
| `AGENT_ZERO_CERT_IPS` | LAN IPs to add to TLS cert SAN (only when not using HTTP-only) | `docker-compose.yml` `environment:` |
| `AGENT_ZERO_REGENERATE_CERT` | Set to `1` once to regenerate cert (then remove) | `docker-compose.yml` `environment:` |

- **HTTP mode** (`AGENT_ZERO_HTTP_ONLY=1`): Use `http://<host>:8888` for Web UI, MCP, and A2A. No certificate or Cursor launcher needed.
- **HTTPS mode** (env unset): Use `https://<host>:8888`. For remote MCP/A2A, add your LAN IP to `AGENT_ZERO_CERT_IPS` and optionally run `./scripts/setup/trust_agent_zero_cert.sh` and start Cursor with `./scripts/setup/cursor_with_agent_zero_cert.sh`. See [docs/MCP_CURSOR_REMEDIATION.md](docs/MCP_CURSOR_REMEDIATION.md).

## Settings Persistence

| Data | Location | Persisted via |
|------|----------|---------------|
| **Host repo (own code)** | `/git/agent-zero` in container | Bind mount `.:/git/agent-zero` (run compose from repo root) |
| Auth, API keys | `.env` | Bind mount `./.env:/a0/.env` |
| Model/agent config | `tmp/settings.json` | Bind mount `./tmp:/a0/tmp` |
| Memory & chats | `memory/` | Bind mount `./memory:/a0/memory` |
| Claude OAuth | `claude-config/` | Bind mount `./claude-config:/root/.config/claude-code` |

## See Also

- `MIGRATION_GUIDE.md` - Full migration guide
- `scripts/README.md` - Scripts directory guide
- `docs/README.md` - Documentation guide
