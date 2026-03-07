#!/bin/bash
# Rebuild Agent Zero image and restart the container.
# Use this after code changes (e.g. models.py) so the app in /a0 picks up updates.
# Run from repo root: ./rebuild.sh

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

echo "Building agent-zero image..."
"${COMPOSE[@]}" build agent-zero

echo "Restarting container..."
"${COMPOSE[@]}" up -d agent-zero

echo ""
echo "Done. Wait for health (e.g. docker compose ps), then:"
echo "  - Web UI: http://localhost:${HOST_PORT:-8888}"
echo "  - Optional litellm test: see FIXMODELS.md Verification Steps"
