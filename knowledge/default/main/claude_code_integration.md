# Claude Code Integration with Agent Zero

## Overview

Claude Code and Agent Zero work together bidirectionally for comprehensive task automation, including security assessments. Claude Code is installed in the container and can both be invoked by Agent Zero and invoke Agent Zero through MCP.

## Availability

- **Command**: `claude-pro-yolo` (recommended for autonomous operation)
- **Location**: `/home/claude/.local/bin/claude`
- **Wrapper**: `/usr/local/bin/claude-pro-yolo` (runs as non-root user with YOLO mode)
- **PATH**: Configured in `.bashrc` and `.profile`

## Usage Note (Root User Limitation)

**IMPORTANT**: The `--dangerously-skip-permissions` flag cannot be used when running as root. Use `claude-pro-yolo` wrapper instead for autonomous operation.

**Use YOLO wrapper for autonomous operation:**
```bash
claude-pro-yolo 'your task here'
```

**Standard invocation (may prompt for permissions):**
```bash
claude-pro 'your task here'
```

**Note**: `claude-pro-yolo` runs Claude Code as a non-root user with YOLO mode enabled, allowing autonomous operation without confirmation prompts.

## Agent Zero → Claude Code

Agent Zero can invoke Claude Code using the `code_execution_tool` with `runtime: "terminal"`:

**Use `claude-pro-yolo` for autonomous operation:**
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

**Standard invocation (may prompt):**
```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro 'your question or task'"
    }
}
```

### When to Use Claude Code

- **Code analysis and review** - Static analysis, vulnerability detection
- **Complex code generation** - Scripts, exploits, automation
- **Report writing** - Documentation, findings reports
- **Debugging** - Analyzing errors, logs, crash dumps
- **Architecture decisions** - Design patterns, implementation strategies

## Claude Code → Agent Zero (MCP)

Claude Code can invoke Agent Zero's capabilities through MCP:

**MCP Server URL**: `http://localhost:8888/mcp/t-{token}/sse`

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `send_message` | Send a task to Agent Zero |
| `network_scan` | Run nmap/masscan scans |
| `web_scan` | Run nikto/nuclei web scans |
| `code_review` | Run semgrep/bandit SAST |
| `get_assessment_state` | Get security assessment state |
| `update_finding` | Add/update security findings |
| `add_target` | Add target to assessment |

### When to Use Agent Zero (via MCP)

- **Network operations** - Scanning, enumeration, service detection
- **Web testing** - Browser automation, form submission, authentication
- **Tool execution** - Running security tools (nmap, nikto, etc.)
- **File operations** - Reading/writing files in the container
- **Shell commands** - System administration, package management

## Shared State

Both agents share assessment state at:
```
/a0/usr/projects/{project}/.a0proj/assessment/
├── assessment_state.json
└── evidence/
```

## Key Points

1. **Always use `claude-pro-yolo`**: Enables autonomous operation (YOLO mode) without confirmation prompts
2. **Uses Pro subscription**: OAuth authentication, no API costs
3. **PATH is set**: Agent Zero's code_execution_tool includes `~/.local/bin`
4. **OAuth persists**: Credentials stored in `./claude-credentials/` (volume-mounted)
5. **Bidirectional**: Both can invoke each other's capabilities
6. **Wrapper script**: `claude-pro-yolo` runs as non-root user with `CLAUDE_CONFIG_DIR` set
7. **Environment variable**: `CLAUDE_CONFIG_DIR=/home/claude/.claude` ensures credential persistence

## Example Workflows

### Security Code Review
```bash
# Agent Zero delegates to Claude Code (use claude-pro-yolo for autonomous operation)
claude-pro-yolo 'Review /app/src for security vulnerabilities. Focus on authentication, input validation, and SQL queries. Output findings in JSON format.'
```

### Network Reconnaissance
```bash
# Agent Zero handles directly, or Claude Code uses MCP:
# MCP call: network_scan(target="10.0.0.0/24", ports="1-1000")
```

### Generate and Execute Script
```bash
# Generate with Claude Code (use claude-pro-yolo for autonomous operation)
claude-pro-yolo 'Write a Python script to parse Nmap XML output and extract open ports'

# Agent Zero then executes the generated script
```

### Full Assessment Workflow
1. Agent Zero: Initialize assessment, run recon
2. Claude Code (via MCP): Request network scan
3. Agent Zero: Execute scan, update state
4. Claude Code: Analyze results, identify targets
5. Agent Zero: Run vulnerability scans
6. Claude Code: Generate report

## Authentication

OAuth credentials are stored in `/home/claude/.claude/` (volume-mounted to `./claude-credentials` on host).

**Key configuration:**
- `CLAUDE_CONFIG_DIR=/home/claude/.claude` (set in docker-compose.yml)
- Credentials file: `./claude-credentials/.credentials.json`
- Settings file: `./claude-credentials/settings.json`

**If authentication is needed:**
1. Connect to VNC at `localhost:5901` (password: `vnc123`)
2. Open terminal and run: `su - claude && claude /login`
3. Complete OAuth flow in browser
4. Credentials persist across container restarts

## Best Practices

- Always use `claude-pro-yolo` for autonomous operation (enables YOLO mode)
- Use `claude-pro` for standard invocation (may prompt for permissions)
- Use `claude-pro-yolo` when Agent Zero needs autonomous operation
- Be specific in prompts to Claude Code
- Use the shared assessment state for security engagements
- Delegate appropriately: Claude Code for analysis, Agent Zero for execution
