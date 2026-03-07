#!/usr/bin/env bash
# Restart the Agent Zero container (no rebuild).
# Use after running MODELS.sh or changing .env so the app picks up new settings.
# Run from repo root: ./restart.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# Keep .env backed up and restore it if it was accidentally removed.
# shellcheck source=/dev/null
source "$REPO_ROOT/scripts/lib/ensure_env.sh"
ensure_env_file "$REPO_ROOT"

if ! [ -f "docker-compose.yml" ]; then
    echo "Error: Run from AgentZ repo root (where docker-compose.yml lives)."
    exit 1
fi

if docker compose version >/dev/null 2>&1; then
    COMPOSE=(docker compose)
else
    COMPOSE=(docker-compose)
fi

echo "Restarting agent-zero..."
"${COMPOSE[@]}" restart agent-zero

echo ""
echo "Waiting for Web UI to respond (up to 90s)..."
PORT="${HOST_PORT:-8888}"
MAX_WAIT=90
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -fsS -o /dev/null -w "%{http_code}" "http://localhost:${PORT}/health" 2>/dev/null | grep -qE '^[23]'; then
        echo "Web UI ready after ${ELAPSED}s."
        break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
done
if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo "Timeout waiting for UI. Check: docker compose ps"
fi

echo ""
echo "Done. Web UI: http://localhost:${PORT}"
