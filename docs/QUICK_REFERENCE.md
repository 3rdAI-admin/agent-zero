# Agent Zero Quick Reference

## Access Points

| Service | Address | Credentials |
|---------|---------|-------------|
| **Web UI** | http://localhost:8888 | - |
| **VNC Desktop** | `vnc://localhost:5901` | Password: `vnc123` |
| **A2A API** | http://localhost:8888/a2a | - |

## Common Commands

### Container Management

```bash
# Start
docker compose up -d
# OR
./startup.sh

# Stop
docker compose down

# Restart
docker compose restart agent-zero

# View logs
docker compose logs -f agent-zero

# Shell access
docker exec -it agent-zero bash
```

### Service Management

```bash
# Check all services
docker exec agent-zero supervisorctl status

# Restart Agent Zero
docker exec agent-zero supervisorctl restart run_ui

# Restart VNC
docker exec agent-zero supervisorctl restart xvfb fluxbox x11vnc

# Check VNC services
docker exec agent-zero supervisorctl status | grep -E "(vnc|xvfb|fluxbox)"
```

### Claude Code

```bash
# Check version
docker exec agent-zero claude-pro-yolo --version

# Use Claude Code (YOLO mode - autonomous operation)
docker exec agent-zero claude-pro-yolo "your question"

# Check installation
docker exec agent-zero which claude-pro-yolo

# Test authentication
docker exec agent-zero claude-pro-yolo "What is 2+2?"
```

### VNC Access

```bash
# macOS
open vnc://localhost:5901

# Linux
vncviewer localhost:5901

# Check VNC port
docker port agent-zero | grep 5900
```

## Agent Zero Usage

### Using Claude Code

**Via Web UI**:
```
Ask: "Use Claude Code to write a Python function that calculates factorial"
```

**Via Terminal** (YOLO mode for autonomous operation):
```bash
docker exec agent-zero claude-pro-yolo "Write a Python function..."
```

### Using Security Tools

```bash
# Network scan
docker exec agent-zero nmap -sn 192.168.1.0/24

# Web vulnerability scan
docker exec agent-zero nikto -h http://target

# SQL injection test
docker exec agent-zero sqlmap -u http://target/page?id=1
```

## File Locations

### Host → Container Mapping

| Host | Container | Purpose |
|------|-----------|---------|
| `./memory` | `/a0/memory` | Agent Zero memory |
| `./knowledge` | `/a0/knowledge` | Knowledge base |
| `./logs` | `/a0/logs` | Log files |
| `./tmp` | `/a0/tmp` | Temporary files |
| `./claude-credentials` | `/home/claude/.claude` | Claude Code OAuth credentials |
| `./claude-config` | `/home/claude/.config/claude-code` | Claude Code config |

### Important Container Paths

| Path | Purpose |
|------|---------|
| `/a0` | Agent Zero root directory |
| `/home/claude/.local/bin/claude` | Claude Code binary |
| `/usr/local/bin/claude-pro-yolo` | Claude Code wrapper (YOLO mode) |
| `/home/claude/.claude/` | Claude Code config (persistent) |
| `/home/claude/.claude/.credentials.json` | OAuth tokens |
| `/root/.vnc/passwd` | VNC password file |
| `/etc/supervisor/conf.d/vnc.conf` | VNC service config |
| `/root/.fluxbox/keys` | Keyboard shortcuts |
| `/root/.fluxbox/menu` | Right-click menu |

## Troubleshooting Quick Fixes

### VNC Not Working

```bash
# Restart VNC services
docker exec agent-zero supervisorctl restart xvfb fluxbox x11vnc

# Check port
docker exec agent-zero netstat -tlnp | grep 5900
```

### Claude Code Not Found

```bash
# Check wrapper exists
docker exec agent-zero which claude-pro-yolo

# Reinstall (as claude user)
docker exec agent-zero runuser -u claude -- bash -c 'curl -fsSL https://claude.ai/install.sh | bash'
```

### Claude Code Authentication Issues

```bash
# Check credentials file
ls -la ./claude-credentials/.credentials.json

# Re-authenticate via VNC
# 1. Connect to vnc://localhost:5901 (password: vnc123)
# 2. Open terminal: su - claude && claude /login
# 3. Complete OAuth in browser
```

### Agent Zero Not Responding

```bash
# Restart service
docker exec agent-zero supervisorctl restart run_ui

# Check logs
docker exec agent-zero tail -50 /a0/logs/*.log
```

### Port Conflicts

```bash
# Check what's using port 8888
lsof -i :8888

# Check what's using port 5901
lsof -i :5901

# Use different port
HOST_PORT=9000 docker compose up -d
```

## Keyboard Shortcuts (VNC)

| Shortcut | Action |
|----------|--------|
| `Shift+Ctrl+C` | Copy |
| `Shift+Ctrl+V` | Paste |
| Right-click | Context menu |

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `HOST_PORT` | `8888` | Web UI port on host |
| `BRANCH` | `local` | Git branch for build |
| `CLAUDE_CONFIG_DIR` | `/home/claude/.claude` | Claude Code credential storage |

## Useful Scripts

### startup.sh
Complete startup script that:
- Checks Docker installation
- Stops existing containers
- Builds fresh image
- Starts container
- Shows status and access info

### Quick Test Commands

```bash
# Test VNC
open vnc://localhost:5901  # macOS

# Test Claude Code
docker exec agent-zero claude-pro-yolo "What is 2+2?"

# Test Agent Zero Web UI
curl http://localhost:8888

# Test security tools
docker exec agent-zero nmap --version

# Check CLAUDE_CONFIG_DIR
docker exec agent-zero bash -c 'echo $CLAUDE_CONFIG_DIR'
```

## Documentation Links

- [Complete Setup Guide](COMPLETE_SETUP_GUIDE.md)
- [VNC Access](VNC_ACCESS.md)
- [Claude Code Integration](CLAUDE_CODE_INTEGRATION.md)
- [Installation](installation.md)
- [Usage](usage.md)
