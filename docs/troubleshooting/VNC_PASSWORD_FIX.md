# VNC Password Fix

## Issue
Password `vnc123` was not working for VNC connections. A previous workaround used `-passwd vnc123` on the command line, which is insecure (visible in `ps`, shell history, and config).

## Solution Applied (current)

x11vnc uses an **encrypted password file** via `-rfbauth` so the password is never on the command line.

### Configuration

**File**: `docker/run/fs/etc/supervisor/conf.d/vnc.conf`

```ini
command=/usr/bin/x11vnc -display :99 -rfbauth /root/.vnc/passwd -listen 0.0.0.0 -xkb -forever -shared -rfbport 5900
```

- `setup_vnc_password` (priority 5) runs first and creates `/root/.vnc/passwd` with `x11vnc -storepasswd` (stdin), mode 600.
- `x11vnc` (priority 30) starts after and reads the auth file; the password is not exposed in `ps` or config.

## Current Status

✅ VNC server uses `-rfbauth` (encrypted password file)  
✅ Password not on command line (secure)  
✅ Port: `5900` (inside container) → `5901` (on host)  
✅ Default password for connections: `vnc123` (set when the auth file is created)

## Connection Details

- **Address**: `vnc://localhost:5901` (local) or `vnc://<HOST_IP>:5901` (remote)
- **Password**: `vnc123` (unless you change it via `x11vnc -storepasswd` and restart)

## Testing

```bash
# Check x11vnc is running (no password in command line)
docker exec agent-zero ps aux | grep x11vnc

# Check port is listening
docker exec agent-zero netstat -tlnp | grep 5900

# Restart if needed
docker exec agent-zero supervisorctl restart x11vnc
```

## Notes

- **Security:** Always use `-rfbauth /path/to/file` instead of `-passwd <plaintext>` so the password is not visible in process list or config.
- The auth file is created by `docker/run/fs/exe/setup_vnc_password.sh` before x11vnc starts.

## Changing Password

Run inside the container to create a new auth file, then restart x11vnc:

```bash
docker exec -it agent-zero bash -c 'rm -f /root/.vnc/passwd && printf "NEWPASS\nNEWPASS\ny\n" | x11vnc -storepasswd /root/.vnc/passwd && chmod 600 /root/.vnc/passwd && supervisorctl restart x11vnc'
```
