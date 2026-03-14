# Google Workspace MCP server (Gmail, Drive, Docs, Sheets, Calendar, etc.) in streamable-HTTP mode.
# Agent Zero can connect at http://workspace_mcp:8889/mcp when both run in the same Docker Compose stack.
# First-time OAuth: run the host script once, then copy ~/.google_workspace_mcp to ./workspace-mcp-credentials (see README).

FROM python:3.12-slim

ENV WORKSPACE_MCP_PORT=8889
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir workspace-mcp

EXPOSE 8889

# Credentials live in /root/.google_workspace_mcp; mount host dir at that path.
# Env GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET must be set (e.g. from .env).
CMD ["workspace-mcp", "--transport", "streamable-http"]
