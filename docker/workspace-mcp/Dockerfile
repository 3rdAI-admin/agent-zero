# Google Workspace MCP server (Gmail, Drive, Docs, Sheets, Calendar, etc.) in streamable-HTTP mode.
# Runs as non-root user 'mcp'. Credentials mount at /home/mcp/.google_workspace_mcp (see README).
# First-time OAuth: run host script once, then copy into workspace-mcp-credentials on host.

FROM python:3.12-slim

ENV WORKSPACE_MCP_PORT=8889
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir workspace-mcp

# Run as non-root: credentials and process isolation.
RUN adduser --disabled-password --gecos "" --uid 1000 mcp \
    && mkdir -p /home/mcp/.google_workspace_mcp \
    && chown -R mcp:mcp /home/mcp/.google_workspace_mcp

ENV HOME=/home/mcp
USER mcp
WORKDIR /home/mcp

EXPOSE 8889

# Mount host credentials at /home/mcp/.google_workspace_mcp. Set GOOGLE_OAUTH_CLIENT_ID/SECRET via env.
CMD ["workspace-mcp", "--transport", "streamable-http"]
