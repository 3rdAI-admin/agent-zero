# YOLO Mode Authentication Setup

## Current Status

✅ **YOLO Mode Setup**: Complete  
✅ **Wrapper Script**: `/usr/local/bin/claude-pro-yolo` working  
✅ **claude user**: Created and configured  
⚠️ **Authentication**: Needs setup

## Authentication Required

Claude Code needs OAuth authentication. The wrapper shares config from root user, but if root user hasn't authenticated, you need to set it up.

### Option 1: Authenticate Root User (Shared)

1. **Connect via VNC**: `vnc://localhost:5901` (password: `vnc123`)
2. **Open terminal** (right-click → Terminal)
3. **Run**: `claude-pro`
4. **Complete OAuth** flow in browser
5. **Config saved** to `/root/.config/claude-code` (shared with claude user)

### Option 2: Authenticate Claude User Directly

1. **Connect via VNC**: `vnc://localhost:5901` (password: `vnc123`)
2. **Open terminal**
3. **Switch to claude user**: `su - claude`
4. **Run**: `claude-pro`
5. **Complete OAuth** flow
6. **Config saved** to `/home/claude/.config/claude-code`

### Option 3: Use Volume-Mounted Config

If you have OAuth config on the host at `./claude-config`, it's mounted to:
- `/root/.config/claude-code` (root user)
- `/home/claude/.config/claude-code` (claude user, via docker-compose)

## Testing After Authentication

```bash
# Test YOLO mode
docker exec agent-zero claude-pro-yolo 'Write a simple Python hello world function'

# Should work without "Invalid API key" error
```

## Quick Test

```bash
# Check if authenticated
docker exec agent-zero bash -c "ls -la /root/.config/claude-code/"

# If empty, need authentication
# If has files, should work
```

## Summary

✅ **Setup Complete**: YOLO mode wrapper ready  
✅ **User Created**: claude user configured  
⚠️ **Authentication**: Required before use  
✅ **Ready**: Once authenticated, YOLO mode will work
