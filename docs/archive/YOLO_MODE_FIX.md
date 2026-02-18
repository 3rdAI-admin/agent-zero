# YOLO Mode Fix - Non-Root User Solution

## Problem

Claude Code's `--dangerously-skip-permissions` flag cannot be used when running as root:
```
--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons
```

## Solution

Created a wrapper script `claude-pro-yolo` that runs Claude Code as a non-root user (`claude`) with YOLO mode enabled.

### Implementation

1. **Created `claude` user**: Non-root user for running Claude Code
2. **Wrapper script**: `/usr/local/bin/claude-pro-yolo`
3. **Automatic setup**: Script handles user creation, Claude Code installation, and symlink creation
4. **Shared OAuth config**: Uses same authentication as root user

### Usage

**Instead of:**
```bash
claude-pro --dangerously-skip-permissions 'your task'  # Won't work as root
```

**Use:**
```bash
claude-pro-yolo 'your task'  # Works! Runs as non-root with YOLO mode
```

### How It Works

1. Creates `claude` user if it doesn't exist
2. Installs Claude Code for the `claude` user
3. Creates `claude-pro` symlink
4. Shares OAuth config from root user
5. Runs Claude Code as `claude` user with `--dangerously-skip-permissions`

### Files Created

- **Wrapper Script**: `/usr/local/bin/claude-pro-yolo`
- **Persistent**: Added to `docker/run/fs/usr/local/bin/claude-pro-yolo` for container rebuilds

### Docker Compose Update

Added volume mount for claude user OAuth config:
```yaml
volumes:
  - ./claude-config:/root/.config/claude-code
  - ./claude-config:/home/claude/.config/claude-code  # For YOLO mode
```

### Authentication

The wrapper shares OAuth authentication from root user:
- Symlinks `/home/claude/.config/claude-code` → `/root/.config/claude-code`
- Or uses volume-mounted config if available
- If authentication needed, use VNC to authenticate as claude user

### Testing

```bash
# Test YOLO mode
docker exec agent-zero claude-pro-yolo --version

# Test code generation
docker exec agent-zero claude-pro-yolo 'Write a simple Python hello world function'
```

### Integration with Agent Zero

Update Agent Zero to use `claude-pro-yolo` instead of `claude-pro --dangerously-skip-permissions`:

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

## Status

✅ **Wrapper Created**: `claude-pro-yolo` script  
✅ **User Created**: `claude` user (non-root)  
✅ **Claude Code Installed**: For claude user  
✅ **YOLO Mode**: Enabled (runs as non-root)  
⚠️ **Authentication**: May need setup for claude user

## Next Steps

1. **Authenticate claude user** (if needed):
   - Connect via VNC: `vnc://localhost:5901`
   - Run: `su - claude`
   - Run: `claude-pro` and complete OAuth

2. **Update Agent Zero prompts** to use `claude-pro-yolo`

3. **Test integration** via Agent Zero web UI

## Alternative: Use Permission Mode

If YOLO mode isn't needed, use:
```bash
claude-pro --permission-mode dontAsk 'your task'
```

This works as root but may still prompt for some operations.
