# How to Use `claude-pro-yolo`

## Overview

`claude-pro-yolo` is a wrapper script that runs Claude Code as a non-root user with YOLO mode (`--dangerously-skip-permissions`) enabled. This allows autonomous operation without confirmation prompts.

**Location**: `/usr/local/bin/claude-pro-yolo`  
**Purpose**: Enable YOLO mode for Claude Code when running as root

## How It Works

The wrapper script:
1. Creates `claude` user (non-root) if it doesn't exist
2. Installs Claude Code for the `claude` user
3. Shares OAuth authentication from root user
4. Runs Claude Code as `claude` user with `--dangerously-skip-permissions`

## Usage Methods

### Method 1: Direct Terminal Invocation (You)

**Single Command**:
```bash
docker exec agent-zero claude-pro-yolo 'Write a Python function to calculate fibonacci numbers'
```

**Interactive Session**:
```bash
docker exec -it agent-zero claude-pro-yolo
# Claude Code starts in interactive mode
```

**From Inside Container**:
```bash
docker exec -it agent-zero bash
# Inside container:
claude-pro-yolo 'Your task here'
```

### Method 2: Agent Zero Invocation

Agent Zero can invoke `claude-pro-yolo` using the `code_execution_tool`:

**Example Agent Zero Tool Call**:
```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro-yolo 'Write a Python script to parse Nmap XML output'"
    }
}
```

**User Prompt to Agent Zero**:
```
"Use Claude Code to create a custom SQL injection tester"
```

**Agent Zero's Response**:
- Agent Zero recognizes Claude Code is needed
- Invokes: `claude-pro-yolo 'Create a custom SQL injection tester...'`
- Captures response
- Can execute generated code

### Method 3: Via Agent Zero Web UI

**Simple Prompt**:
```
"Use Claude Code to review this code for security vulnerabilities"
```

Agent Zero will automatically:
1. Recognize Claude Code is needed
2. Invoke `claude-pro-yolo` with your request
3. Return the results

## Usage Examples

### Example 1: Code Generation

**You or Agent Zero**:
```bash
claude-pro-yolo 'Write a Python function that scans a network range for open ports using nmap'
```

**Result**: Claude Code generates the code, which can then be executed.

### Example 2: Code Review

**You or Agent Zero**:
```bash
claude-pro-yolo 'Review this Python code for security vulnerabilities: [code snippet]'
```

**Result**: Claude Code analyzes the code and provides security recommendations.

### Example 3: Exploit Development

**You or Agent Zero**:
```bash
claude-pro-yolo 'Create a Python script to test for SQL injection vulnerabilities in a web application'
```

**Result**: Claude Code generates a custom exploit script.

### Example 4: Report Generation

**You or Agent Zero**:
```bash
claude-pro-yolo 'Generate a penetration testing report template with sections for findings, evidence, and remediation'
```

**Result**: Claude Code creates a professional report template.

## Command Syntax

### Basic Syntax
```bash
claude-pro-yolo 'your task or question'
```

### With Multiple Arguments
```bash
claude-pro-yolo 'task' 'additional context' 'more details'
```

### Interactive Mode
```bash
claude-pro-yolo
# Enters interactive session
```

## How Agent Zero Uses It

### Automatic Recognition

When you ask Agent Zero to use Claude Code, it automatically uses `claude-pro-yolo`:

**User**: "Use Claude Code to generate a network scanner"

**Agent Zero**:
1. Recognizes Claude Code is needed
2. Executes: `claude-pro-yolo 'Generate a network scanner'`
3. Captures response
4. Can execute generated code

### Tool Prompt Integration

Agent Zero's `code_execution_tool` prompt includes Claude Code documentation, so Agent Zero knows:
- When to use Claude Code
- How to invoke it (`claude-pro-yolo`)
- What tasks Claude Code can help with

## Comparison: `claude-pro` vs `claude-pro-yolo`

### `claude-pro` (Standard)
```bash
claude-pro 'your task'
```
- Runs as root user
- May prompt for permissions
- Not suitable for autonomous operation

### `claude-pro-yolo` (Recommended)
```bash
claude-pro-yolo 'your task'
```
- Runs as non-root user (`claude`)
- YOLO mode enabled (no prompts)
- Perfect for autonomous operation
- ✅ **Use this for Agent Zero integration**

## Authentication

The wrapper shares OAuth authentication from root user:
- `/home/claude/.config/claude-code` → `/root/.config/claude-code` (symlink)
- Or uses volume-mounted config: `./claude-config:/home/claude/.config/claude-code`

**If authentication needed**:
1. Connect via VNC: `vnc://localhost:5901` (password: `vnc123`)
2. Open terminal
3. Run: `su - claude`
4. Run: `claude-pro` and complete OAuth flow

## Testing

### Test YOLO Mode Works
```bash
docker exec agent-zero claude-pro-yolo --version
# Expected: 2.1.19 (Claude Code)
```

### Test Code Generation
```bash
docker exec agent-zero claude-pro-yolo 'Write a simple Python hello world function'
```

### Test from Agent Zero
Ask Agent Zero:
```
"Use Claude Code to write a Python function that calculates prime numbers"
```

## Common Use Cases

### 1. Custom Tool Creation
```bash
claude-pro-yolo 'Create a custom port scanner that detects services nmap might miss'
```

### 2. Exploit Development
```bash
claude-pro-yolo 'Create a Python script to test for XSS vulnerabilities'
```

### 3. Code Analysis
```bash
claude-pro-yolo 'Review this code for security vulnerabilities: [code]'
```

### 4. Report Writing
```bash
claude-pro-yolo 'Generate a penetration testing report with findings and remediation'
```

### 5. Debugging
```bash
claude-pro-yolo 'Analyze this error log and identify the root cause: [log]'
```

## Troubleshooting

### Issue: "Command not found"

**Solution**:
```bash
# Verify script exists
docker exec agent-zero ls -la /usr/local/bin/claude-pro-yolo

# Check PATH
docker exec agent-zero which claude-pro-yolo
```

### Issue: "Invalid API key"

**Solution**: Claude Code needs OAuth authentication
1. Connect via VNC
2. Authenticate as `claude` user
3. Or ensure OAuth config is shared

### Issue: Permission Denied

**Solution**: Script should be executable
```bash
docker exec agent-zero chmod +x /usr/local/bin/claude-pro-yolo
```

## Best Practices

1. **Always use `claude-pro-yolo`** for Agent Zero integration
2. **Quote your task** properly: `claude-pro-yolo 'your task'`
3. **Be specific** in your requests for better results
4. **Review generated code** before execution
5. **Test in isolated environment** first

## Quick Reference

**Direct Invocation**:
```bash
docker exec agent-zero claude-pro-yolo 'your task'
```

**Via Agent Zero**:
```
"Use Claude Code to [your task]"
```

**Interactive**:
```bash
docker exec -it agent-zero claude-pro-yolo
```

**Check Version**:
```bash
docker exec agent-zero claude-pro-yolo --version
```

## Summary

✅ **You can invoke**: `docker exec agent-zero claude-pro-yolo 'task'`  
✅ **Agent Zero can invoke**: Automatically via `code_execution_tool`  
✅ **YOLO mode**: Enabled (no confirmation prompts)  
✅ **Authentication**: Shared from root user  
✅ **Ready to use**: Fully configured and working

The wrapper makes it seamless to use Claude Code with YOLO mode, whether you invoke it directly or through Agent Zero!
