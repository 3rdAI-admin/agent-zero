# Planning - Agent Zero (AgentZ)

## Project Overview

Agent Zero is a personal, organic agentic AI framework that runs in Docker. This fork extends the upstream [agent0ai/agent-zero](https://github.com/agent0ai/agent-zero) with:
- VNC desktop access for GUI tasks and CAPTCHA completion
- Claude Code integration (`claude-pro-yolo` wrapper)
- OWASP security tools (nmap, sqlmap, nikto, metasploit, etc.)
- HTTPS/TLS with configurable LAN IP SANs for remote MCP/A2A clients
- Enhanced network capabilities (bridge mode with `NET_RAW`, `NET_ADMIN`, `SYS_ADMIN`)

## Architecture

### Runtime
- **Container**: Docker, built from `agent0ai/agent-zero-base:latest` + local overlays
- **Image**: `agent-zero:local` (built via `docker compose build`)
- **Web UI**: HTTPS on container port 80, mapped to host `${HOST_PORT:-8888}`
- **VNC**: Port 5900 (container) mapped to 5901 (host)
- **Process manager**: supervisord (runs `run_ui`, VNC services, etc.)

### Key Directories
| Host | Container | Purpose |
|------|-----------|---------|
| `.env` | `/a0/.env` | Auth & API keys |
| `./memory` | `/a0/memory` | Persistent agent memory |
| `./knowledge` | `/a0/knowledge` | Knowledge base |
| `./logs` | `/a0/logs` | Session logs |
| `./tmp` | `/a0/tmp` | Settings, temp files |
| `./claude-config` | `/root/.config/claude-code` & `/home/claude/.config/claude-code` | Claude OAuth config |
| `./claude-credentials` | `/home/claude/.claude` | Claude credential tokens |

### Code Structure
- `python/api/` - FastAPI API endpoints
- `python/helpers/` - Core helper modules
- `python/tools/` - Agent tools (code execution, browser, search, security, etc.)
- `python/extensions/` - Extension hooks (system prompt, memory, streaming, etc.)
- `agents/` - Agent configurations and examples
- `prompts/` - System prompts and templates
- `webui/` - Frontend SvelteKit application
- `docker/` - Docker build overlays and scripts
- `scripts/` - Setup and testing scripts
- `tests/` - Pytest test suite
- `docs/` - Documentation (guides/, integration/, troubleshooting/, archive/)

## Style & Conventions
- **Language**: Python (backend), SvelteKit (frontend)
- **Formatter**: Black (88 chars), PEP8
- **Linter**: Ruff
- **Testing**: Pytest (tests/ directory)
- **Docstrings**: Google style
- **Type hints**: Required on all new code
- **Validation**: Pydantic
- **API framework**: FastAPI (via run_ui.py)

## Governance & security
- **Penetration testing ROE:** [docs/guides/PEN_TESTING_ROE.md](docs/guides/PEN_TESTING_ROE.md) — Rules of engagement for all pen testing (authorization, scope, conduct). **Agent Zero** (hacker agent) and **Archon** (task/workflow context) must follow this ROE. Shared reference: [docs/guides/ROE_AGENT_ZERO_AND_ARCHON.md](docs/guides/ROE_AGENT_ZERO_AND_ARCHON.md).

## Constraints
- Files must stay under 500 lines
- Use `.venv` or project venv for Python commands
- Never hardcode secrets — use `.env` and `python-dotenv`
- Always run Agent Zero in Docker (isolated environment)
