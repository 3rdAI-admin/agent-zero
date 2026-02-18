# Complete Agent Zero Setup Guide

## Overview

This guide covers the complete setup of Agent Zero with all integrated features:
- **VNC Desktop Access** - GUI environment for CAPTCHA completion and visual tasks
- **Claude Code Integration** - AI-powered coding assistance
- **Security Tools** - Network scanning and penetration testing capabilities
- **Network Configuration** - LAN access for security testing

## Quick Start

### 1. Prerequisites

- Docker Desktop installed and running
- Port 8888 available (or configure custom port)
- Port 5901 available (for VNC access)

### 2. Initial Setup

```bash
# Clone or navigate to Agent Zero directory
cd /path/to/AgentZ

# Start Agent Zero
docker compose up -d

# Or use the startup script
./startup.sh
```

### 3. Access Points

- **Web UI**: http://localhost:8888
- **VNC Desktop**: `vnc://localhost:5901` (password: `vnc123`)
- **A2A API**: http://localhost:8888/a2a

## Features

### ✅ VNC Desktop Access

**Purpose**: GUI environment for:
- Completing CAPTCHA challenges (Claude Code OAuth)
- Running GUI applications
- Visual debugging and testing

**Access**:
- Address: `vnc://localhost:5901`
- Password: `vnc123`
- Auto-starts with container

**Applications Available**:
- Terminals: `lxterminal`, `xterm`
- Browser: `chromium`
- Editors: `mousepad`, `gedit`, `nano`, `vim`

**Keyboard Shortcuts**:
- `Shift+Ctrl+C` - Copy
- `Shift+Ctrl+V` - Paste
- Right-click - Context menu

**Documentation**: See [VNC Access Guide](VNC_ACCESS.md)

### ✅ Claude Code Integration

**Purpose**: AI-powered coding assistance integrated with Agent Zero

**How It Works**:
1. Agent Zero invokes Claude Code via `code_execution_tool`
2. Claude Code generates code, reviews code, or provides technical assistance
3. Agent Zero captures response and can execute generated code

**Usage**:
Ask Agent Zero: "Use Claude Code to [your task]"

**Example**:
```
You: "Use Claude Code to write a Python function that validates email addresses"
Agent Zero: [invokes claude-pro, gets code, executes it, shows results]
```

**Authentication**:
- Uses OAuth (Pro subscription) - no API costs
- Config persisted in `./claude-config` (volume-mounted)
- Complete OAuth via VNC if needed

**Documentation**: See [Claude Code Integration](CLAUDE_CODE_INTEGRATION.md)

### ✅ Security Tools

**Purpose**: Network scanning and penetration testing

**Installed Tools**:
- Network scanning: `nmap`, `masscan`, `netdiscover`
- Web security: `nikto`, `sqlmap`, `gobuster`, `wfuzz`
- Vulnerability scanners: `openvas-scanner`, `lynis`
- Password tools: `john`, `hashcat`, `hydra`
- Exploitation: `metasploit-framework`

**Network Configuration**:
- Bridge mode with extended capabilities
- `NET_RAW`, `NET_ADMIN`, `SYS_ADMIN` for raw sockets
- Host gateway access: `host.docker.internal`

**Documentation**: See [Security Setup](../SECURITY_SETUP.md)

### ✅ Network Access

**Configuration**:
- Port 8888: Web UI (configurable via `HOST_PORT`)
- Port 5901: VNC server
- Bridge networking with capabilities for LAN scanning

**Host Access**:
- `host.docker.internal` - Access host network services
- Full LAN access for security scanning

## Configuration Files

### docker-compose.yml

**Key Settings**:
```yaml
ports:
  - "${HOST_PORT:-8888}:80"  # Web UI
  - "5901:5900"              # VNC server

volumes:
  - ./.env:/a0/.env                            # Auth & API keys (persistent)
  - ./claude-config:/root/.config/claude-code  # Claude Code OAuth

cap_add:
  - NET_RAW      # Network scanning
  - NET_ADMIN    # Advanced networking
  - SYS_ADMIN    # Security tools
```

### Environment Variables

**`.env` file** (bind-mounted into container at `/a0/.env`):
```bash
HOST_PORT=8888          # Web UI port
BRANCH=local            # Git branch for build
AUTH_LOGIN=th3rdai      # Web UI username
AUTH_PASSWORD=...       # Web UI password
# API keys (API_KEY_OPENAI, API_KEY_ANTHROPIC, etc.)
```

> **Note**: The `.env` file is volume-mounted so that authentication credentials
> and API keys persist across container recreations (`docker compose down && up`).

## Common Tasks

### Start Agent Zero

```bash
# Using docker compose
docker compose up -d

# Using startup script
./startup.sh
```

### Access VNC Desktop

**macOS**:
```bash
open vnc://localhost:5901
# Password: vnc123
```

**Linux**:
```bash
vncviewer localhost:5901
```

**Windows**: Use VNC Viewer → `localhost:5901`

### Use Claude Code

**Via Agent Zero Web UI**:
1. Go to http://localhost:8888
2. Ask: "Use Claude Code to [your task]"
3. Agent Zero invokes Claude Code automatically

**Via VNC Terminal**:
1. Connect to VNC
2. Open terminal
3. Run: `claude-pro "your question"`

### Run Security Scans

```bash
# Inside container
docker exec -it agent-zero bash

# Example: Network scan
nmap -sn 192.168.1.0/24

# Example: Web vulnerability scan
nikto -h http://target-ip
```

## Verification

### Check Services

```bash
# Container status
docker ps --filter name=agent-zero

# VNC services
docker exec agent-zero supervisorctl status | grep -E "(vnc|xvfb|fluxbox)"

# Claude Code
docker exec agent-zero claude-pro --version
```

### Test Integration

**Test 1: VNC Access**
- Connect: `vnc://localhost:5901`
- Password: `vnc123`
- Should see desktop

**Test 2: Claude Code**
- Ask Agent Zero: "Use Claude Code to explain Python decorators"
- Should invoke Claude Code and return explanation

**Test 3: Security Tools**
```bash
docker exec agent-zero nmap --version
docker exec agent-zero sqlmap --version
```

## Troubleshooting

### VNC Not Accessible

**Check port**:
```bash
docker port agent-zero | grep 5900
```

**Check services**:
```bash
docker exec agent-zero supervisorctl status x11vnc
```

**Restart VNC**:
```bash
docker exec agent-zero supervisorctl restart xvfb fluxbox x11vnc
```

### Claude Code Not Found

**Check installation**:
```bash
docker exec agent-zero which claude-pro
```

**Check PATH**:
```bash
docker exec agent-zero bash -c 'export PATH="$HOME/.local/bin:$PATH" && which claude-pro'
```

**Reinstall if needed**:
```bash
docker exec agent-zero bash -c 'curl -fsSL https://claude.ai/install.sh | bash'
```

### Agent Zero Can't Use Claude Code

**Check tool prompt**:
```bash
docker exec agent-zero grep "Claude Code" /a0/prompts/agent.system.tool.code_exe.md
```

**Restart Agent Zero**:
```bash
docker exec agent-zero supervisorctl restart run_ui
```

## Maintenance

### Update Agent Zero

```bash
# Pull latest image
docker compose pull

# Rebuild with latest code
docker compose build

# Restart
docker compose restart
```

### Backup Data

**Important directories and files** (volume-mounted):
- `./.env` - Authentication credentials and API keys
- `./memory` - Agent Zero memory
- `./knowledge` - Knowledge base
- `./logs` - Logs
- `./tmp` - Temporary files
- `./claude-config` - Claude Code OAuth tokens

**Backup**:
```bash
# Backup all data
tar -czf agent-zero-backup-$(date +%Y%m%d).tar.gz \
  .env memory/ knowledge/ logs/ tmp/ claude-config/
```

### Clean Up

```bash
# Stop container
docker compose down

# Remove container (keeps volumes)
docker compose rm

# Remove volumes (WARNING: deletes data)
docker compose down -v
```

## Advanced Configuration

### Custom Ports

Edit `docker-compose.yml`:
```yaml
ports:
  - "9000:80"    # Custom Web UI port
  - "5902:5900"  # Custom VNC port
```

Or use environment variable:
```bash
HOST_PORT=9000 docker compose up -d
```

### Host Network Mode

For maximum network access (removes port mapping):
```yaml
network_mode: host
# Remove ports section when using host mode
```

### Persistent Claude Code

Claude Code is installed during Docker build and persists across restarts. OAuth config is volume-mounted.

## Related Documentation

- [VNC Access Guide](VNC_ACCESS.md) - Complete VNC setup and usage
- [Claude Code Integration](CLAUDE_CODE_INTEGRATION.md) - Claude Code integration details
- [Security Setup](../SECURITY_SETUP.md) - Security tools and network configuration
- [Installation Guide](installation.md) - Basic installation
- [Usage Guide](usage.md) - Agent Zero usage

## Summary

✅ **VNC Desktop** - GUI access on port 5901  
✅ **Claude Code** - Integrated AI coding assistant  
✅ **Security Tools** - Network scanning capabilities  
✅ **Network Access** - LAN scanning enabled  
✅ **All Features** - Fully configured and ready

Agent Zero is now a complete platform for AI-assisted development, security testing, and autonomous task execution!
