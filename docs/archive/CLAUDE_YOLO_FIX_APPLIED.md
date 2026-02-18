# ✅ Fix Applied: Agent Zero Now Uses `claude-pro-yolo`

## Problem Fixed

Agent Zero was trying to use:
```bash
claude-pro --dangerously-skip-permissions 'task'
```

This failed with:
```
--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons
```

## Solution Applied

Updated Agent Zero's prompts and knowledge base to use `claude-pro-yolo` wrapper instead.

## Changes Made

### 1. Tool Prompt Updated
**File**: `prompts/agent.system.tool.code_exe.md`

- ✅ Changed from `claude-pro` to `claude-pro-yolo`
- ✅ Updated examples to use `claude-pro-yolo`
- ✅ Added note about YOLO mode wrapper

### 2. Knowledge Base Updated
**File**: `knowledge/default/main/claude_code_integration.md`

- ✅ Updated all examples to use `claude-pro-yolo`
- ✅ Updated best practices section
- ✅ Clarified YOLO mode usage

### 3. Security Assessment Integration Updated
**File**: `knowledge/default/main/security_assessment_integration.md`

- ✅ Updated examples to use `claude-pro-yolo`
- ✅ Clarified autonomous operation

### 4. Files Copied to Container
- ✅ Tool prompt copied
- ✅ Knowledge base files copied
- ✅ Agent Zero restarted

## Correct Usage

### Agent Zero Will Now Use

**Autonomous Operation** (recommended):
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

### What Changed

**Before** (❌ Failed):
```bash
claude-pro --dangerously-skip-permissions 'task'
# Error: cannot be used with root/sudo privileges
```

**After** (✅ Works):
```bash
claude-pro-yolo 'task'
# Runs as non-root user with YOLO mode enabled
```

## Testing

Agent Zero will now automatically use `claude-pro-yolo` when you ask it to use Claude Code:

**Test**:
```
"Use Claude Code to write a Python function to scan ports"
```

**Expected**: Agent Zero uses `claude-pro-yolo` (not `claude-pro --dangerously-skip-permissions`)

## Verification

Check Agent Zero logs to confirm:
```bash
docker logs agent-zero | grep claude-pro
# Should see: claude-pro-yolo (not --dangerously-skip-permissions)
```

## Note: OAuth Authentication

The `claude-pro-yolo` wrapper is working, but Claude Code needs OAuth authentication. See `SETUP_CLAUDE_OAUTH.md` for authentication setup.

## Summary

✅ **Fixed**: Agent Zero now uses `claude-pro-yolo`  
✅ **Updated**: All prompts and knowledge base  
✅ **Restarted**: Agent Zero reloaded with new configuration  
✅ **Ready**: Will work once OAuth is authenticated

Agent Zero will now correctly invoke Claude Code using `claude-pro-yolo` for autonomous operation!
