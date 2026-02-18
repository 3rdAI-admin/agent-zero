# Claude Code Integration with Agent Zero

## Overview

Agent Zero is fully integrated with Claude Code, allowing the agent to leverage Claude Code's AI-powered coding assistance as part of its autonomous task execution. This integration enables Agent Zero to generate code, review code, debug issues, and get technical assistance using Claude Code's Pro subscription (OAuth-based, no API costs).

## Architecture

### Components

1. **Claude Code**: Installed at `/home/claude/.local/bin/claude`
   - Wrapper: `/usr/local/bin/claude-pro-yolo` (runs as non-root with YOLO mode)
   - Uses Pro subscription via OAuth (no API costs)
   - OAuth credentials persisted in `./claude-credentials/` (volume-mounted)

2. **Agent Zero**: Uses `code_execution_tool` to invoke Claude Code
   - Tool prompt includes Claude Code documentation
   - PATH configured to include `~/.local/bin`
   - Can capture and use Claude Code responses

3. **Integration Layer**:
   - `claude-pro-yolo` wrapper enables autonomous operation
   - `CLAUDE_CONFIG_DIR` environment variable for credential persistence
   - Knowledge base documents integration patterns

## How It Works

### Agent Zero Invokes Claude Code

When you ask Agent Zero to use Claude Code, it executes:

```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro-yolo 'your question or task'"
    }
}
```

**IMPORTANT**: Always use `claude-pro-yolo` (not `claude-pro --dangerously-skip-permissions`) when running as root. The wrapper handles running as a non-root user with YOLO mode enabled.

### Complete Workflow

1. **User asks Agent Zero**: "Use Claude Code to write a Python function..."
2. **Agent Zero recognizes**: Claude Code is available (from tool prompt)
3. **Agent Zero invokes**: `claude-pro-yolo 'Write a Python function...'`
4. **Wrapper executes**: Runs as `claude` user with `CLAUDE_CONFIG_DIR` set
5. **Claude Code executes**: Returns code or explanation
6. **Agent Zero captures**: Response is captured by `code_execution_tool`
7. **Agent Zero executes**: Can run generated code using `runtime: "python"`
8. **Results reported**: Back to user

## Usage Examples

### Example 1: Code Generation

**User Prompt:**
> "Use Claude Code to generate a Python script that reads a CSV file and creates a summary report"

**Agent Zero's Actions:**
1. Invokes: `claude-pro-yolo 'Generate a Python script that reads a CSV file and creates a summary report with statistics'`
2. Captures Claude Code's response
3. Optionally executes the generated code
4. Reports results

### Example 2: Code Review

**User Prompt:**
> "Use Claude Code to review this Python function for security issues: [code]"

**Agent Zero's Actions:**
1. Invokes: `claude-pro-yolo 'Review this Python function for security vulnerabilities: [code]'`
2. Captures Claude Code's security analysis
3. Reports findings to user

### Example 3: Security Assessment

**User Prompt:**
> "Use Claude Code to analyze nmap scan results"

**Agent Zero's Actions:**
1. Invokes: `claude-pro-yolo 'Analyze these nmap results and identify potential vulnerabilities: [scan output]'`
2. Gets analysis from Claude Code
3. Can follow up with additional scans based on findings

## Configuration

### Docker Compose Setup

The integration requires these volume mounts and environment variables in `docker-compose.yml`:

```yaml
services:
  agent-zero:
    environment:
      # Critical: This enables credential persistence
      - CLAUDE_CONFIG_DIR=/home/claude/.claude
    volumes:
      # Claude Code credentials (OAuth tokens)
      - ./claude-credentials:/home/claude/.claude
      # Claude Code config
      - ./claude-config:/home/claude/.config/claude-code
```

### The claude-pro-yolo Wrapper

Located at `/usr/local/bin/claude-pro-yolo`, this wrapper:

1. Runs Claude Code as the `claude` user (not root)
2. Sets `CLAUDE_CONFIG_DIR` to the persistent volume
3. Enables `--dangerously-skip-permissions` (YOLO mode)
4. Passes all arguments to Claude Code

```bash
#!/bin/bash
CLAUDE_USER="claude"
CLAUDE_HOME="/home/$CLAUDE_USER"
export CLAUDE_CONFIG_DIR="$CLAUDE_HOME/.claude"

exec runuser -u "$CLAUDE_USER" -- env \
    HOME="$CLAUDE_HOME" \
    PATH="$CLAUDE_HOME/.local/bin:$PATH" \
    CLAUDE_CONFIG_DIR="$CLAUDE_CONFIG_DIR" \
    claude-pro --dangerously-skip-permissions -p "$@"
```

## Authentication

### OAuth Setup

Claude Code uses OAuth authentication (Pro subscription):

1. **Config Directory**: `/home/claude/.claude/` (volume-mounted to `./claude-credentials/`)
2. **Environment Variable**: `CLAUDE_CONFIG_DIR=/home/claude/.claude`
3. **Credentials File**: `./claude-credentials/.credentials.json`
4. **Persistent**: OAuth tokens survive container restarts

### Initial Authentication

If OAuth authentication is needed:

1. Connect to VNC: `localhost:5901` (password: `vnc123`)
2. Open terminal (right-click → Terminal)
3. Run: `su - claude && claude /login`
4. Complete OAuth flow in browser
5. Credentials saved to `./claude-credentials/.credentials.json`

### Verifying Authentication

```bash
# Check credentials file exists
ls -la ./claude-credentials/.credentials.json

# Test Claude Code
docker exec agent-zero claude-pro-yolo "What is 2+2?"
```

## Best Practices

### For Users

1. **Be explicit**: "Use Claude Code to..." or "Ask Claude Code..."
2. **Use `claude-pro-yolo`**: Always use the wrapper for autonomous operation
3. **Provide context**: Include relevant code, errors, or requirements
4. **Request format**: Ask for executable code, explanations, or reviews

### For Agent Zero

1. **Always use `claude-pro-yolo`**: Enables YOLO mode without confirmation prompts
2. **Be specific**: Include context and requirements in prompts
3. **Combine tools**: Use Claude Code output with code execution
4. **Monitor output**: Check logs for full Claude Code responses

## Troubleshooting

### Invalid API Key / Need to Login

**Symptom**: `Invalid API key · Please run /login`

**Solution**:
1. Connect to VNC at `localhost:5901`
2. Open terminal and run: `su - claude && claude /login`
3. Complete OAuth in browser
4. Verify: `docker exec agent-zero claude-pro-yolo "test"`

### Credentials Not Persisting

**Symptom**: Need to re-authenticate after container restart

**Solution**:
1. Verify `CLAUDE_CONFIG_DIR` is set in docker-compose.yml
2. Check volume mount: `./claude-credentials:/home/claude/.claude`
3. Verify credentials file: `ls ./claude-credentials/.credentials.json`

### Permission Denied

**Symptom**: Cannot run with `--dangerously-skip-permissions` as root

**Solution**: Use `claude-pro-yolo` wrapper instead of `claude-pro --dangerously-skip-permissions`

### Onboarding Wizard Appears

**Symptom**: Theme selection or setup prompts appear

**Solution**: The `install_security_tools.sh` script creates bypass settings. If needed manually:
```bash
docker exec agent-zero bash -c 'cat > /home/claude/.claude/settings.json << EOF
{
  "hasCompletedOnboarding": true,
  "theme": "dark",
  "preferredNotifChannel": "status_bar"
}
EOF'
```

## Verification

### Quick Test

```bash
# 1. Check wrapper exists
docker exec agent-zero which claude-pro-yolo

# 2. Check CLAUDE_CONFIG_DIR
docker exec agent-zero bash -c 'echo $CLAUDE_CONFIG_DIR'

# 3. Test Claude Code
docker exec agent-zero claude-pro-yolo "What is 2+2? Reply with just the number."

# 4. Check credentials persist
ls -la ./claude-credentials/.credentials.json
```

### Expected Behavior

When you ask Agent Zero to use Claude Code:
1. ✅ Agent Zero recognizes Claude Code is available
2. ✅ Agent Zero invokes `claude-pro-yolo` via `code_execution_tool`
3. ✅ Wrapper runs as `claude` user with YOLO mode
4. ✅ Claude Code executes and returns response
5. ✅ Credentials persist across container restarts

## File Locations

| File/Directory | Purpose |
|----------------|---------|
| `/usr/local/bin/claude-pro-yolo` | Wrapper script for autonomous operation |
| `/home/claude/.local/bin/claude` | Claude Code binary |
| `/home/claude/.claude/` | Config directory (mounted volume) |
| `./claude-credentials/` | Host-side persistent credentials |
| `./claude-credentials/.credentials.json` | OAuth tokens |
| `./claude-credentials/settings.json` | User settings |

## Summary

✅ **Claude Code installed** and accessible via `claude-pro-yolo`
✅ **YOLO mode enabled** through wrapper script
✅ **OAuth persistent** via `CLAUDE_CONFIG_DIR` and volume mount
✅ **Onboarding bypassed** via settings.json
✅ **Integration complete** and ready for use

Agent Zero can now leverage Claude Code's AI capabilities as part of its autonomous task execution, creating a powerful workflow for code generation, review, debugging, security analysis, and technical assistance.
