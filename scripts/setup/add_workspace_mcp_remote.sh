#!/usr/bin/env bash
# Add the Google Workspace MCP remote server to Agent Zero's settings so the
# container connects to workspace-mcp running on the host at host.docker.internal:8889.
#
# Prerequisites:
#   1. Run workspace-mcp on the host first: ./scripts/setup/run_workspace_mcp.sh
#   2. Agent Zero container running (so we can docker exec and write to /a0/usr/settings.json)
#
# Usage: ./scripts/setup/add_workspace_mcp_remote.sh [port]
# Default port: 8889

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8889}"
MCP_URL="http://host.docker.internal:${PORT}/mcp"

echo "=========================================="
echo "Add Google Workspace MCP (remote) to Agent Zero"
echo "=========================================="
echo ""
echo "Remote URL: $MCP_URL"
echo ""

docker exec agent-zero python3 << PYTHON_SCRIPT
import json
import os

SETTINGS_FILE = "/a0/usr/settings.json"

google_workspace_entry = {
    "description": "Gmail, Drive, Docs, Sheets, Slides, Calendar, Tasks (remote workspace-mcp on host)",
    "url": "$MCP_URL",
    "type": "streamable-http"
}

if not os.path.exists(SETTINGS_FILE):
    print("Creating new settings file at " + SETTINGS_FILE)
    settings = {"mcp_servers": json.dumps({"mcpServers": {"google_workspace": google_workspace_entry}}, indent=2)}
else:
    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)

raw = settings.get("mcp_servers", "{}")
if isinstance(raw, str):
    try:
        mcp_obj = json.loads(raw)
    except json.JSONDecodeError:
        mcp_obj = {"mcpServers": {}}
else:
    mcp_obj = raw if isinstance(raw, dict) else {"mcpServers": {}}

if "mcpServers" not in mcp_obj:
    mcp_obj["mcpServers"] = {}
mcp_obj["mcpServers"]["google_workspace"] = google_workspace_entry
settings["mcp_servers"] = json.dumps(mcp_obj, indent=2)

with open(SETTINGS_FILE, "w") as f:
    json.dump(settings, f, indent=4)

print("Added google_workspace remote MCP server to settings.")
print("URL:", "$MCP_URL")
PYTHON_SCRIPT

echo ""
echo "=========================================="
echo "Done"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Ensure workspace-mcp is running on the host: ./scripts/setup/run_workspace_mcp.sh"
echo "  2. Restart Agent Zero or reload settings so it connects to the new MCP server."
echo "  3. In the Web UI, Settings → MCP/A2A → External MCP Servers should show google_workspace."
echo "  4. First tool use from Agent Zero may trigger OAuth in a browser on the host."
echo ""
