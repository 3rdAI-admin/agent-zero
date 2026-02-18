# Agent Zero - Complete Setup with VNC, Claude Code & Security Tools

## 🎯 Quick Start

```bash
# Start Agent Zero with all features
./startup.sh

# Access points:
# - Web UI: http://localhost:8888
# - VNC Desktop: vnc://localhost:5901 (password: vnc123)
```

## ✨ Features

### ✅ VNC Desktop Environment
- **Full GUI desktop** accessible via VNC
- **Applications**: Chromium browser, terminals, text editors
- **Purpose**: CAPTCHA completion, GUI applications, visual tasks
- **Access**: `vnc://localhost:5901` (password: `vnc123`)

### ✅ Claude Code Integration
- **AI-powered coding assistant** integrated with Agent Zero
- **Usage**: Ask Agent Zero "Use Claude Code to [task]"
- **Authentication**: OAuth (Pro subscription) - no API costs
- **Persistent**: Config survives container restarts

### ✅ Security Tools
- **Network scanning**: nmap, masscan, netdiscover
- **Web security**: nikto, sqlmap, gobuster, wfuzz
- **Vulnerability scanners**: openvas-scanner, lynis
- **Exploitation**: metasploit-framework
- **Network access**: Full LAN scanning capabilities

## 📚 Documentation

### Essential Guides
- **[Complete Setup Guide](./docs/COMPLETE_SETUP_GUIDE.md)** - Full setup with all features ⭐ START HERE
- **[Quick Reference](./docs/QUICK_REFERENCE.md)** - Command cheat sheet
- **[Documentation Index](./DOCUMENTATION_INDEX.md)** - All documentation organized

### Feature Guides
- **[VNC Desktop Access](./docs/VNC_ACCESS.md)** - GUI environment setup
- **[Claude Code Integration](./docs/CLAUDE_CODE_INTEGRATION.md)** - AI coding assistant
- **[Security Tools](./SECURITY_SETUP.md)** - Pen testing setup

### Core Documentation
- **[Installation](./docs/installation.md)** - Basic installation
- **[Usage Guide](./docs/usage.md)** - How to use Agent Zero
- **[Architecture](./docs/architecture.md)** - System design
- **[Troubleshooting](./docs/troubleshooting.md)** - Common issues

## 🚀 Getting Started

### 1. Start Agent Zero
```bash
./startup.sh
```

### 2. Access Web UI
Open browser: http://localhost:8888

### 3. Access VNC Desktop (if needed)
```bash
# macOS
open vnc://localhost:5901

# Linux
vncviewer localhost:5901
```
Password: `vnc123`

### 4. Use Claude Code
Ask Agent Zero: "Use Claude Code to write a Python hello world script"

## 🔧 Configuration

### Ports
- **8888**: Web UI (configurable via `HOST_PORT`)
- **5901**: VNC server

### Volumes
- `./memory` - Agent Zero memory
- `./knowledge` - Knowledge base
- `./logs` - Log files
- `./tmp` - Temporary files
- `./claude-config` - Claude Code OAuth tokens

### Network
- Bridge mode with extended capabilities
- `NET_RAW`, `NET_ADMIN`, `SYS_ADMIN` for security tools
- Host gateway access for LAN scanning

## 📖 Usage Examples

### Using Claude Code via Agent Zero
```
You: "Use Claude Code to generate a REST API client in Python"
Agent Zero: [invokes claude-pro, gets code, executes it, shows results]
```

### Running Security Scans
```bash
# Network scan
docker exec agent-zero nmap -sn 192.168.1.0/24

# Web vulnerability scan
docker exec agent-zero nikto -h http://target-ip
```

### VNC Desktop Tasks
1. Connect: `vnc://localhost:5901`
2. Right-click → Terminal
3. Run commands, open browser, edit files

## 🛠️ Troubleshooting

### VNC Not Accessible
```bash
docker exec agent-zero supervisorctl restart xvfb fluxbox x11vnc
```

### Claude Code Not Found
```bash
docker exec agent-zero claude-pro --version
docker exec agent-zero supervisorctl restart run_ui
```

### Port Conflicts
```bash
# Use different port
HOST_PORT=9000 docker compose up -d
```

See [Troubleshooting Guide](./docs/troubleshooting.md) for more.

## 📋 Status

✅ **VNC Desktop** - Configured and running  
✅ **Claude Code** - Installed and integrated  
✅ **Security Tools** - Available  
✅ **Network Access** - Configured  
✅ **All Features** - Ready for use

## 🔗 Links

- **Web UI**: http://localhost:8888
- **VNC**: `vnc://localhost:5901`
- **Documentation**: [Complete Setup Guide](./docs/COMPLETE_SETUP_GUIDE.md)
- **Quick Reference**: [Command Cheat Sheet](./docs/QUICK_REFERENCE.md)

## 📝 Next Steps

1. **Read**: [Complete Setup Guide](./docs/COMPLETE_SETUP_GUIDE.md)
2. **Test**: Access Web UI and VNC desktop
3. **Try**: Ask Agent Zero to use Claude Code
4. **Explore**: Run security scans on your network

**Everything is set up and ready to use!** 🎉
