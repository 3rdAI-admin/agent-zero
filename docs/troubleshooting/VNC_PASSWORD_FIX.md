# VNC Password Fix

## Issue
Password `vnc123` was not working for VNC connections.

## Solution Applied

Changed x11vnc configuration from using password file (`-rfbauth`) to direct password (`-passwd`).

### Updated Configuration

**File**: `/docker/run/fs/etc/supervisor/conf.d/vnc.conf`

**Changed from:**
```ini
command=/usr/bin/x11vnc -display :99 -rfbauth /root/.vnc/passwd -listen 0.0.0.0 -xkb -forever -shared -rfbport 5900
```

**Changed to:**
```ini
command=/usr/bin/x11vnc -display :99 -passwd vnc123 -listen 0.0.0.0 -xkb -forever -shared -rfbport 5900
```

## Current Status

✅ VNC server is running with password authentication
✅ Password: `vnc123`
✅ Port: `5900` (inside container) → `5901` (on host)

## Connection Details

- **Address**: `vnc://localhost:5901` (local) or `vnc://<HOST_IP>:5901` (remote)
- **Password**: `vnc123`

## Testing

To verify the password works:

```bash
# Check x11vnc is running
docker exec agent-zero ps aux | grep x11vnc

# Check port is listening
docker exec agent-zero netstat -tlnp | grep 5900

# Restart if needed
docker exec agent-zero supervisorctl restart x11vnc
```

## Notes

- The password file method (`-rfbauth`) had issues in non-interactive environments
- Using `-passwd` directly is more reliable for Docker containers
- Password is now hardcoded in the supervisor config (acceptable for containerized environments)

## Changing Password

To change the password, edit `/docker/run/fs/etc/supervisor/conf.d/vnc.conf` and change:
```
-passwd vnc123
```
to your desired password, then rebuild the container.
