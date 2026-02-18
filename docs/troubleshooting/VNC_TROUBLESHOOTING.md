# VNC Troubleshooting Guide

## ✅ Current Status

VNC services are now **running and configured correctly**:
- ✅ xvfb (virtual display) - RUNNING
- ✅ fluxbox (window manager) - RUNNING  
- ✅ x11vnc (VNC server) - RUNNING
- ✅ autocutsel (clipboard sync) - RUNNING
- ✅ Port 5900 listening inside container
- ✅ Port mapping: 5900 → 5901 on host

## 🔧 Issue Fixed

The problem was that Supervisor wasn't loading the `vnc.conf` file because the `[include]` section was missing from `/etc/supervisor/conf.d/supervisord.conf`. This has been fixed.

## 🌐 Remote Access Issues

If you're trying to connect from a remote machine (like 192.168.50.7) and getting connection errors, check:

### 1. Host Firewall

**macOS Firewall:**
```bash
# Check if firewall is enabled
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Allow incoming connections on port 5901
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /System/Library/CoreServices/RemoteManagement/ARDAgent.app
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /System/Library/CoreServices/RemoteManagement/ARDAgent.app
```

Or manually:
1. System Settings → Network → Firewall
2. Click "Options"
3. Add port 5901 (TCP) to allowed ports

**Linux Firewall (iptables/ufw):**
```bash
# UFW
sudo ufw allow 5901/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 5901 -j ACCEPT
```

### 2. Docker Port Binding

Verify port is bound to all interfaces (0.0.0.0):
```bash
docker port agent-zero | grep 5900
# Should show: 5900/tcp -> 0.0.0.0:5901
```

If it shows `127.0.0.1:5901`, update `docker-compose.yml`:
```yaml
ports:
  - "0.0.0.0:5901:5900"  # Explicitly bind to all interfaces
```

### 3. Network Connectivity

Test from remote machine:
```bash
# From remote machine (192.168.50.7)
nc -zv <HOST_IP> 5901
telnet <HOST_IP> 5901
```

### 4. VNC Connection

**macOS:**
```bash
# Finder → Go → Connect to Server
vnc://<HOST_IP>:5901

# Or command line
open vnc://<HOST_IP>:5901
```

**Linux:**
```bash
vncviewer <HOST_IP>:5901
```

**Windows:**
- Use VNC Viewer
- Connect to: `<HOST_IP>:5901`
- Password: `vnc123`

## 🔍 Verification Commands

Check VNC services:
```bash
docker exec agent-zero supervisorctl status | grep -E "(vnc|xvfb|fluxbox)"
```

Check port listening:
```bash
docker exec agent-zero netstat -tlnp | grep 5900
```

Check port mapping:
```bash
docker port agent-zero | grep 5900
```

Test connection from host:
```bash
nc -zv localhost 5901
```

## 🚀 Quick Fix Commands

If VNC services stop:

```bash
# Restart all VNC services
docker exec agent-zero supervisorctl restart xvfb fluxbox x11vnc autocutsel

# Or restart individual service
docker exec agent-zero supervisorctl restart x11vnc

# Check status
docker exec agent-zero supervisorctl status
```

## 📝 Notes

- **Password**: `vnc123` (set in `/root/.vnc/passwd`)
- **Display**: `:99` (virtual X display)
- **Port**: `5900` inside container, `5901` on host
- **Auto-start**: VNC services start automatically via Supervisor

## 🔄 Making Changes Persistent

The supervisor config fix was applied to the running container. To make it persistent across rebuilds, ensure `/docker/run/fs/etc/supervisor/conf.d/supervisord.conf` includes:

```ini
[include]
files = /etc/supervisor/conf.d/*.conf
```

This has already been updated in the source files.
