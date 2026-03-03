#!/usr/bin/env bash
# Monitor Agent Zero container logs while the app is running.
# Highlights lines that may indicate issues (errors, timeouts, 4xx/5xx).
# Run in a terminal; Ctrl+C to stop.
#
# Usage: ./scripts/monitor_agent_zero.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

CONTAINER_NAME="${CONTAINER_NAME:-agent-zero}"

# One-line status
if docker ps --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Agent Zero is running. Following logs (Ctrl+C to stop)."
  echo "Highlighting: Error, WARNING, timeout, 4xx/5xx, McpError, SyntaxError, Traceback"
  echo "---"
else
  echo "Container ${CONTAINER_NAME} is not running. Start it first (e.g. ./startup.sh)."
  exit 1
fi

# Strip ANSI then highlight issue lines; --line-buffered so grep doesn't block output
docker logs -f "$CONTAINER_NAME" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | while IFS= read -r line; do
  if echo "$line" | grep -qE 'Error|error:|WARNING|Warning:|timeout|Timeout|McpError|SyntaxError|Traceback|" 40[0-9] |" 50[0-9] '; then
    echo "[ISSUE] $line"
  else
    echo "$line"
  fi
done
