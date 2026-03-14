#!/usr/bin/env bash
# Run Google Workspace MCP server in streamable-HTTP mode on the host.
# MCP clients (e.g. Agent Zero in Docker) can connect at http://host.docker.internal:8889/mcp
#
# Prerequisites: uv/uvx (pip install uv or brew install uv), Python 3.10+
# OAuth: Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in .env or export them.
#
# Usage: ./scripts/run_workspace_mcp.sh [port]
# Default port: 8889 (override via WORKSPACE_MCP_PORT or first argument)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PORT="${1:-${WORKSPACE_MCP_PORT:-8889}}"
export WORKSPACE_MCP_PORT="$PORT"

if [[ -f "$REPO_ROOT/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$REPO_ROOT/.env"
  set +a
fi

if [[ -z "$GOOGLE_OAUTH_CLIENT_ID" || -z "$GOOGLE_OAUTH_CLIENT_SECRET" ]]; then
  echo "Warning: GOOGLE_OAUTH_CLIENT_ID or GOOGLE_OAUTH_CLIENT_SECRET not set."
  echo "Add them to $REPO_ROOT/.env or export before running."
  echo "Create a Desktop OAuth client at https://console.cloud.google.com/ (APIs & Services → Credentials)."
  read -r -p "Continue anyway? [y/N] " cont
  case "$cont" in
    [yY]) ;;
    *) exit 1 ;;
  esac
fi

if ! command -v uvx &>/dev/null; then
  echo "uvx not found. Install uv: pip install uv (or brew install uv)."
  exit 1
fi

echo "Starting Google Workspace MCP (streamable HTTP) on port $PORT ..."
echo "Connect MCP clients to: http://localhost:$PORT/mcp (or http://host.docker.internal:$PORT/mcp from Docker)"
echo "First tool use will open a browser for OAuth on this host."
echo ""

exec uvx workspace-mcp --transport streamable-http
