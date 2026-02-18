# How Claude Code Uses Agent Zero

## Overview

Claude Code connects to Agent Zero through **MCP (Model Context Protocol)**, allowing Claude Code to invoke Agent Zero's capabilities as tools. This creates a bidirectional integration where:

- **Agent Zero → Claude Code**: Agent Zero can execute Claude Code commands via terminal
- **Claude Code → Agent Zero**: Claude Code can use Agent Zero's tools via MCP

## Connection Method: MCP Server

Agent Zero exposes an **MCP Server** that Claude Code connects to. The server provides Agent Zero's capabilities as tools that Claude Code can invoke.

### MCP Server Endpoints

Agent Zero's MCP server runs on the same URL and port as the Web UI (default: `http://localhost:8888`):

- **SSE Endpoint**: `/mcp/t-{token}/sse` (Server-Sent Events)
- **HTTP Endpoint**: `/mcp/t-{token}/http/` (Streamable HTTP)

### Getting Your MCP Token

The token is automatically generated from your Agent Zero username and password. You can find it:

1. **Via Web UI**: Go to `Settings > MCP Server > MCP Server` - your personalized connection URLs are displayed there
2. **Via API**: The token is the same as your API token (generated from credentials)

**Note**: The token changes if you update your Agent Zero credentials.

## Configuration

### Step 1: Get Your Connection URL

1. Log into Agent Zero Web UI at `http://localhost:8888`
2. Navigate to `Settings > MCP Server`
3. Copy your MCP Server URL (it will look like: `http://localhost:8888/mcp/t-YOUR_TOKEN/sse`)

### Step 2: Configure Claude Code

Add Agent Zero as an MCP server in Claude Code's configuration. The exact method depends on how Claude Code is configured, but typically you'll add it to a `mcp.json` or similar config file:

```json
{
    "mcpServers": {
        "agent-zero": {
            "type": "sse",
            "url": "http://localhost:8888/mcp/t-YOUR_TOKEN/sse"
        }
    }
}
```

**For remote access** (if Agent Zero is on a different machine):

```json
{
    "mcpServers": {
        "agent-zero": {
            "type": "sse",
            "url": "http://YOUR_AGENT_ZERO_IP:8888/mcp/t-YOUR_TOKEN/sse"
        }
    }
}
```

## Available MCP Tools

Once connected, Claude Code can use these Agent Zero tools:

### Communication Tools

| Tool | Description |
|------|-------------|
| `send_message` | Send a task or message to Agent Zero. Can start new conversations or continue existing ones. **This provides A2A-like conversational interface** - Agent Zero processes your message naturally and responds conversationally. |
| `finish_chat` | Finish a persistent chat session with Agent Zero. |

### Security Assessment Tools

| Tool | Description |
|------|-------------|
| `network_scan` | Run nmap/masscan network scans for port discovery, service detection, and OS fingerprinting |
| `web_scan` | Run nikto/nuclei web vulnerability scans |
| `code_review` | Run static code analysis (SAST) using semgrep and bandit |
| `get_assessment_state` | Get the current security assessment state (targets, findings, progress) |
| `update_finding` | Add or update security findings in the assessment |
| `add_target` | Add a target to the security assessment scope |

## How It Works

### 1. Claude Code Initiates Connection

When Claude Code starts, it connects to Agent Zero's MCP server using the configured URL.

### 2. Tool Discovery

Agent Zero's MCP server exposes its available tools with descriptions and parameters. Claude Code discovers these tools automatically.

### 3. Tool Invocation

When you ask Claude Code to perform a task that requires Agent Zero's capabilities, Claude Code:

1. **Identifies the appropriate tool** (e.g., `network_scan` for scanning a network)
2. **Formulates the request** with the correct parameters
3. **Sends the request** to Agent Zero via MCP
4. **Receives the response** and presents it to you

### 4. Shared State

For security assessments, both agents share state at:
```
/a0/usr/projects/{project}/.a0proj/assessment/
├── assessment_state.json    # Targets, findings, progress
└── evidence/                # Screenshots, logs, captured data
```

## Example Workflows

### Example 1: Network Scanning

**You ask Claude Code:**
> "Scan the network 192.168.1.0/24 for open ports"

**Claude Code:**
1. Recognizes this requires Agent Zero's `network_scan` tool
2. Invokes: `network_scan(target="192.168.1.0/24", ports="1-1000")`
3. Agent Zero runs nmap and returns results
4. Claude Code analyzes and presents the findings

### Example 2: Web Application Testing

**You ask Claude Code:**
> "Test https://example.com for vulnerabilities"

**Claude Code:**
1. Uses `web_scan` tool: `web_scan(target="https://example.com", scan_type="quick")`
2. Agent Zero runs nikto/nuclei scans
3. Results are returned to Claude Code
4. Claude Code generates a summary report

### Example 3: Code Review

**You ask Claude Code:**
> "Review the code in /app/src for security issues"

**Claude Code:**
1. Uses `code_review` tool: `code_review(path="/app/src", language="auto")`
2. Agent Zero runs semgrep and bandit
3. Findings are returned
4. Claude Code provides detailed analysis

### Example 4: Task Delegation

**You ask Claude Code:**
> "Ask Agent Zero to install nmap and scan localhost"

**Claude Code:**
1. Uses `send_message` tool to send: "Install nmap and scan localhost"
2. Agent Zero receives the message, installs nmap, runs the scan
3. Agent Zero returns the results
4. Claude Code presents the findings

## Bidirectional Integration

The integration works both ways:

### Agent Zero → Claude Code

Agent Zero can invoke Claude Code via terminal:
```bash
claude-pro-yolo 'Review this code for security vulnerabilities'
```

### Claude Code → Agent Zero

Claude Code can invoke Agent Zero via MCP:
```json
{
    "tool": "network_scan",
    "parameters": {
        "target": "192.168.1.1",
        "ports": "1-1000"
    }
}
```

## Benefits

1. **Specialized Capabilities**: Claude Code leverages Agent Zero's security tools (nmap, nikto, etc.)
2. **Automated Workflows**: Claude Code can orchestrate complex security assessments
3. **Shared Context**: Both agents work with the same assessment state
4. **Seamless Integration**: Tools appear native to Claude Code

## Troubleshooting

### Connection Issues

- **Verify Agent Zero is running**: `docker ps | grep agent-zero`
- **Check the token**: Ensure you're using the correct token from Settings
- **Network access**: If connecting remotely, ensure port 8888 is accessible
- **URL format**: Ensure the URL includes `/mcp/t-{token}/sse` or `/mcp/t-{token}/http/`

### Tool Not Available

- **Check MCP connection**: Verify Claude Code successfully connected to Agent Zero
- **Tool discovery**: Ensure Agent Zero's MCP server is exposing the tools
- **Scope validation**: Some tools require targets to be in-scope for the assessment

## Why MCP Instead of A2A?

You might wonder: "Why use MCP instead of Agent Zero's native A2A protocol?"

**Answer**: Claude Code only supports MCP, not FastA2A. However, MCP provides the best of both worlds:

- **Granular Tools**: Direct access to specific capabilities (`network_scan`, `web_scan`, etc.)
- **A2A-Like Interface**: The `send_message` tool provides conversational, A2A-like interaction
- **Flexibility**: Choose granular tools for specific operations or `send_message` for complex workflows

See **[MCP vs A2A Comparison](./MCP_VS_A2A_COMPARISON.md)** for detailed analysis.

## Summary

Claude Code uses Agent Zero by:

1. **Connecting** to Agent Zero's MCP server via SSE or HTTP
2. **Discovering** available tools automatically
3. **Invoking** tools when needed:
   - **Granular tools** (network scans, web scans, code reviews) for direct, structured results
   - **`send_message`** for conversational, A2A-like interaction
4. **Receiving** results and presenting them to you
5. **Sharing** assessment state for collaborative security work

This integration allows Claude Code to leverage Agent Zero's specialized security testing capabilities while maintaining its own strengths in code analysis and reasoning.
