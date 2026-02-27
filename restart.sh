#!/usr/bin/env bash
# Restart the Agent Zero container (no rebuild).
# Use after running MODELS.sh or changing .env so the app picks up new settings.
# Run from repo root: ./restart.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

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
echo "Done. Wait for health (e.g. docker compose ps), then:"
echo "  - Web UI: http://localhost:${HOST_PORT:-8888}"
