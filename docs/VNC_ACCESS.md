# VNC Desktop Access Guide

## Overview

Agent Zero includes a full VNC-accessible desktop environment for GUI applications, CAPTCHA completion, and interactive tasks. The desktop runs Fluxbox window manager with Chromium browser, terminals, and text editors.

## Quick Start

### Connection Details

- **Address**: `vnc://localhost:5901` (local) or `vnc://<HOST_IP>:5901` (remote)
- **Password**: `vnc123`
- **Display**: `:99` (virtual X display)

### Connect from macOS

1. **Finder Method**:
   - Open Finder
   - Press `Cmd+K` (or Go → Connect to Server)
   - Enter: `vnc://localhost:5901`
   - Enter password: `vnc123`

2. **Command Line**:
   ```bash
   open vnc://localhost:5901
   ```

### Connect from Linux

```bash
vncviewer localhost:5901
# Or
remmina vnc://localhost:5901
```

### Connect from Windows

- Use VNC Viewer (RealVNC, TightVNC, etc.)
- Connect to: `localhost:5901`
- Password: `vnc123`

## Desktop Environment

### Window Manager: Fluxbox

- **Lightweight**: Minimal resource usage
- **Right-click menu**: Access applications
- **Keyboard shortcuts**: Configured for copy/paste

### Available Applications

**Terminals:**
- `lxterminal` - Lightweight terminal emulator
- `xterm` - X terminal

**Browsers:**
- `chromium` - Web browser (with `--no-sandbox` flag)

**Text Editors:**
- `mousepad` - Lightweight GUI editor
- `gedit` - GNOME text editor
- `nano` - Terminal editor
- `vim` - Terminal editor

### Accessing Applications

1. **Right-click desktop** → Applications menu
2. **Keyboard shortcuts**:
   - `Shift+Ctrl+C` - Copy
   - `Shift+Ctrl+V` - Paste
   - Right-click - Context menu

## Services

VNC services auto-start with the container via Supervisor:

- **xvfb** - Virtual X display (`:99`)
- **fluxbox** - Window manager
- **x11vnc** - VNC server (port 5900)
- **autocutsel** - Clipboard synchronization

### Check Service Status

```bash
docker exec agent-zero supervisorctl status | grep -E "(vnc|xvfb|fluxbox)"
```

Expected output:
```
fluxbox                          RUNNING
x11vnc                           RUNNING
xvfb                             RUNNING
autocutsel                       RUNNING
```

## Common Tasks

### Open Terminal

1. Right-click desktop
2. Select: Terminal (or Applications → Shells → Bash)

### Open Browser

1. Right-click desktop
2. Select: Browser
3. Or in terminal: `chromium --no-sandbox &`

### Use Claude Code

1. Open terminal
2. Run: `claude-pro "your question"`
3. Complete OAuth if needed

### Copy/Paste

**Within VNC:**
- Select text → `Shift+Ctrl+C` to copy
- `Shift+Ctrl+V` to paste

**Between Host and Container:**
- Use file-based clipboard scripts (see Clipboard section)

## Clipboard

### Within VNC Session

- **Copy**: `Shift+Ctrl+C`
- **Paste**: `Shift+Ctrl+V`
- **Right-click**: Context menu

### Host ↔ Container

**Copy FROM Container TO Host:**
```bash
# In VNC terminal, select text and run:
copy-to-host

# From Mac terminal:
docker exec agent-zero container-to-mac
```

**Copy FROM Host TO Container:**
```bash
# From Mac terminal:
echo 'YOUR_TEXT' | docker exec -i agent-zero mac-to-container

# In VNC terminal, paste with Ctrl+V or Shift+Ctrl+V
```

## Troubleshooting

### Can't Connect to VNC

**Check port is listening:**
```bash
docker exec agent-zero netstat -tlnp | grep 5900
```

**Check VNC services:**
```bash
docker exec agent-zero supervisorctl status | grep x11vnc
```

**Restart VNC services:**
```bash
docker exec agent-zero supervisorctl restart xvfb fluxbox x11vnc
```

### Password Not Working

**Reset password:**
```bash
docker exec agent-zero bash -c 'rm -f /root/.vnc/passwd && printf "vnc123\nvnc123\ny\n" | x11vnc -storepasswd /root/.vnc/passwd && supervisorctl restart x11vnc'
```

**Or use direct password** (already configured):
- Password is set directly in supervisor config: `-passwd vnc123`
- No password file needed

### Desktop Not Visible

**Check Xvfb is running:**
```bash
docker exec agent-zero ps aux | grep Xvfb
```

**Check Fluxbox is running:**
```bash
docker exec agent-zero ps aux | grep fluxbox
```

**Restart services:**
```bash
docker exec agent-zero supervisorctl restart xvfb fluxbox
```

### Applications Not Opening

**Check DISPLAY:**
```bash
docker exec agent-zero bash -c 'export DISPLAY=:99 && xdpyinfo | head -5'
```

**Open application manually:**
```bash
docker exec agent-zero bash -c 'export DISPLAY=:99 && chromium --no-sandbox &'
```

## Configuration Files

### Supervisor Config

**File**: `/etc/supervisor/conf.d/vnc.conf`

Manages all VNC services:
- Password setup
- Xvfb virtual display
- Clipboard shortcuts
- Fluxbox window manager
- x11vnc server
- autocutsel clipboard sync

### Fluxbox Config

**Files**:
- `/root/.fluxbox/keys` - Keyboard shortcuts
- `/root/.fluxbox/menu` - Right-click menu

**Update menu:**
```bash
docker exec agent-zero nano /root/.fluxbox/menu
# Then restart fluxbox:
docker exec agent-zero supervisorctl restart fluxbox
```

## Remote Access

### From Another Machine

1. **Find host IP**:
   ```bash
   # On Mac
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. **Connect from remote machine**:
   ```
   vnc://<HOST_IP>:5901
   ```

3. **Firewall**: Ensure port 5901 is open on host firewall

### macOS Firewall

**Allow incoming connections:**
```bash
# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Allow port 5901
# System Settings → Network → Firewall → Options → Add port 5901
```

## Performance

### Optimize for Remote Access

- **Resolution**: Default is 1920x1080 (can be changed in `vnc.conf`)
- **Color depth**: 24-bit (can be reduced for slower connections)
- **Compression**: VNC uses automatic compression

### Reduce Resource Usage

If VNC is not needed:
```bash
# Stop VNC services
docker exec agent-zero supervisorctl stop xvfb fluxbox x11vnc autocutsel

# Start when needed
docker exec agent-zero supervisorctl start xvfb fluxbox x11vnc autocutsel
```

## Security Notes

- **Password**: Default is `vnc123` - change if needed
- **Network**: VNC is accessible on port 5901 (consider firewall rules)
- **Isolation**: VNC runs in container, isolated from host
- **OAuth**: Use VNC for Claude Code OAuth completion (CAPTCHA)

## Summary

✅ **VNC accessible** on port 5901  
✅ **Password**: `vnc123`  
✅ **Auto-start**: Services start with container  
✅ **Desktop**: Fluxbox with terminals, browser, editors  
✅ **Clipboard**: Copy/paste configured  
✅ **Ready for use**: Complete GUI environment

VNC provides full desktop access for GUI applications, CAPTCHA completion, and interactive tasks within the Agent Zero container.
