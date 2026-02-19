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

## HTTPS / TLS (Remote MCP/A2A Clients)

| Variable | Purpose | Where |
|----------|---------|-------|
| `AGENT_ZERO_CERT_IPS` | LAN IPs to add to TLS cert SAN | `docker-compose.yml` `environment:` |
| `AGENT_ZERO_REGENERATE_CERT` | Set to `1` to regenerate cert (then remove) | `docker-compose.yml` `environment:` |

Remote clients connecting via `https://<LAN-IP>:8888` need the host IP in the cert. After changing `AGENT_ZERO_CERT_IPS`, uncomment `AGENT_ZERO_REGENERATE_CERT=1`, restart, then re-comment it.

## Settings Persistence

| Data | Location | Persisted via |
|------|----------|---------------|
| Auth, API keys | `.env` | Bind mount `./.env:/a0/.env` |
| Model/agent config | `tmp/settings.json` | Bind mount `./tmp:/a0/tmp` |
| Memory & chats | `memory/` | Bind mount `./memory:/a0/memory` |
| Claude OAuth | `claude-config/` | Bind mount `./claude-config:/root/.config/claude-code` |

## See Also

- `MIGRATION_GUIDE.md` - Full migration guide
- `scripts/README.md` - Scripts directory guide
- `docs/README.md` - Documentation guide
