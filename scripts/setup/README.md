# Setup Scripts

Scripts for installation, configuration, and initial setup of Agent Zero.

## Available Scripts

- **startup.sh** - Main startup script for Agent Zero
- **configure_mcp_token.sh** - Configure MCP server token
- **configure_claude_mcp.sh** - Configure Claude Code MCP connection
- **run_workspace_mcp.sh** - Run Google Workspace MCP (Gmail, Drive, Docs, Sheets, etc.) on the host in streamable-HTTP mode. Use with **add_workspace_mcp_remote.sh** so Agent Zero in Docker can connect via `http://host.docker.internal:8889/mcp`. Alternatively, use the **containerized** Workspace MCP: `docker compose up` includes a `workspace_mcp` service; connect at `http://workspace_mcp:8889/mcp` (see docker/workspace-mcp/README.md).
- **add_workspace_mcp_remote.sh** - Add the remote Google Workspace MCP server to Agent Zero settings (run after **run_workspace_mcp.sh** and with the container up)
- **setup_claude_oauth.sh** - Setup Claude Code OAuth authentication
- **claude-pro-auth.sh** - Claude Pro authentication helper
- **claude_auth_helper.sh** - Claude authentication helper
- **get-claude-oauth.sh** - Get Claude OAuth URL
- **get-oauth-url.sh** - Extract OAuth URL
- **extract-oauth-url.sh** - Extract OAuth URL from output

## Usage

See main [README.md](../README.md) for detailed usage instructions.
