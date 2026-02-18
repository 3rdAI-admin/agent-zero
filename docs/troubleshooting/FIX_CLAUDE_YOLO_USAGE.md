# Fix: Agent Zero Using Wrong Claude Code Command

## Problem

Agent Zero was trying to use:
```bash
claude-pro --dangerously-skip-permissions 'task'
```

This fails with error:
```
--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons
```

## Solution

Updated Agent Zero to use `claude-pro-yolo` wrapper instead, which:
- Runs Claude Code as non-root user (`claude`)
- Enables YOLO mode automatically
- Works for autonomous operation

## Changes Made

### 1. Updated Tool Prompt
**File**: `prompts/agent.system.tool.code_exe.md`

**Changed from**:
```
claude-pro 'your task here'
```

**Changed to**:
```
claude-pro-yolo 'your task here'
```

### 2. Updated Knowledge Base
**File**: `knowledge/default/main/claude_code_integration.md`

- Updated all examples to use `claude-pro-yolo`
- Updated best practices section
- Clarified YOLO mode usage

### 3. Updated Security Assessment Integration
**File**: `knowledge/default/main/security_assessment_integration.md`

- Updated examples to use `claude-pro-yolo`
- Clarified autonomous operation requirements

## Correct Usage

### Agent Zero Invocation

**Correct** (autonomous operation):
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

**Also works** (may prompt):
```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro 'your task here'"
    }
}
```

### Direct Terminal Usage

**Correct**:
```bash
claude-pro-yolo 'Write a Python function to scan ports'
```

**Wrong** (won't work as root):
```bash
claude-pro --dangerously-skip-permissions 'task'  # ❌ Fails
```

## Testing

After these changes, Agent Zero should automatically use `claude-pro-yolo`:

```bash
# Test via Agent Zero
# Ask: "Use Claude Code to write a Python function"
# Agent Zero should use: claude-pro-yolo
```

## Service Reload

Agent Zero will pick up these changes:
- On next restart, OR
- When prompts/knowledge are reloaded

To force reload:
```bash
docker restart agent-zero
```

## Verification

Check that Agent Zero uses the correct command:

```bash
# Monitor Agent Zero logs
docker logs -f agent-zero | grep claude-pro

# Should see: claude-pro-yolo (not claude-pro --dangerously-skip-permissions)
```

## Summary

✅ **Fixed**: Updated all documentation to use `claude-pro-yolo`  
✅ **Tool Prompt**: Updated to recommend `claude-pro-yolo`  
✅ **Knowledge Base**: Updated examples and best practices  
✅ **Ready**: Agent Zero will now use correct command

Agent Zero will now automatically use `claude-pro-yolo` for autonomous Claude Code operation!
