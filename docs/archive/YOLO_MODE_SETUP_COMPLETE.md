# YOLO Mode Setup Complete ✅

## Solution Implemented

Created a wrapper script `claude-pro-yolo` that runs Claude Code as a non-root user, enabling YOLO mode (`--dangerously-skip-permissions`).

## Components

### 1. Non-Root User
- **User**: `claude` (uid 1000)
- **Purpose**: Run Claude Code without root privileges
- **Home**: `/home/claude`

### 2. Wrapper Script
- **Location**: `/usr/local/bin/claude-pro-yolo`
- **Function**: Runs Claude Code as `claude` user with YOLO mode
- **Persistent**: Added to `docker/run/fs/usr/local/bin/claude-pro-yolo`

### 3. Installation Script Update
- **File**: `docker/run/fs/ins/install_additional.sh`
- **Added**: Automatic setup of claude user and YOLO mode wrapper

### 4. Docker Compose Update
- **Added**: Volume mount for claude user OAuth config
- **Location**: `./claude-config:/home/claude/.config/claude-code`

## Usage

### Basic Usage
```bash
# Instead of (won't work as root):
claude-pro --dangerously-skip-permissions 'your task'

# Use (works!):
claude-pro-yolo 'your task'
```

### With Agent Zero
```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro-yolo 'your task here'"
    }
}
```

## Authentication

The wrapper shares OAuth authentication from root user via symlink:
- `/home/claude/.config/claude-code` → `/root/.config/claude-code`

**If authentication is needed:**
1. Connect via VNC: `vnc://localhost:5901` (password: `vnc123`)
2. Open terminal
3. Run: `su - claude`
4. Run: `claude-pro` and complete OAuth flow

## Testing

### Test YOLO Mode
```bash
docker exec agent-zero claude-pro-yolo --version
# Expected: 2.1.19 (Claude Code)
```

### Test Code Generation
```bash
docker exec agent-zero claude-pro-yolo 'Write a simple Python hello world function'
```

### Verify User
```bash
docker exec agent-zero id claude
# Expected: uid=1000(claude) gid=1000(claude)
```

## Current Status

✅ **claude user**: Created (uid 1000)  
✅ **Claude Code**: Installed for claude user  
✅ **Wrapper script**: `/usr/local/bin/claude-pro-yolo`  
✅ **YOLO mode**: Enabled (runs as non-root)  
✅ **OAuth sharing**: Symlinked to root config  
⚠️ **Authentication**: May need setup if OAuth config is empty

## Next Steps

1. **Authenticate** (if needed):
   - Use VNC to authenticate claude user
   - Or authenticate root user (shared via symlink)

2. **Update Agent Zero prompts** to use `claude-pro-yolo`

3. **Test integration** via Agent Zero web UI

## Files Modified

1. ✅ `docker/run/fs/usr/local/bin/claude-pro-yolo` - Wrapper script (new)
2. ✅ `docker/run/fs/ins/install_additional.sh` - Added YOLO setup
3. ✅ `docker-compose.yml` - Added volume mount for claude user

## Verification

Run these commands to verify setup:
```bash
# Check user exists
docker exec agent-zero id claude

# Check Claude Code installed
docker exec agent-zero ls -la /home/claude/.local/bin/claude*

# Test wrapper
docker exec agent-zero claude-pro-yolo --version

# Test YOLO mode (may need auth)
docker exec agent-zero claude-pro-yolo 'test'
```

## Summary

✅ **YOLO Mode Fixed**: Wrapper script enables `--dangerously-skip-permissions`  
✅ **Non-Root Execution**: Runs as `claude` user  
✅ **Persistent Setup**: Included in installation script  
✅ **Ready**: YOLO mode available for Agent Zero integration

**Status**: 🎉 **YOLO MODE FIXED AND READY**
