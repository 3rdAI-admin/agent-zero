#!/usr/bin/env bash
# Show Agent Zero status and current model settings (container, health, Web UI, VNC, URLs, settings).
# Used by startup.sh at end of run and by MODELS.sh --status.
# Run from repo root or from scripts/ (will cd to repo root).

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

CONTAINER_NAME="${CONTAINER_NAME:-agent-zero}"
HOST_PORT="${HOST_PORT:-8888}"

if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD=(docker compose)
else
    DOCKER_COMPOSE_CMD=(docker-compose)
fi

fail() { echo -e "${RED}[FAIL]${NC} $1"; }

is_running() {
    docker ps --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" 2>/dev/null | grep -q "^${CONTAINER_NAME}$"
}

# Print settings from JSON (pipe or as first arg)
print_settings() {
    local json="$1"
    echo "$json" | python3 -c '
import json, sys
try:
    s = json.load(sys.stdin)
except Exception:
    s = {}
if not s:
    print("  (no settings)")
    sys.exit(0)
def api_base(val):
    return val if val else "(default)"
chat_p = s.get("chat_model_provider", "")
chat_n = s.get("chat_model_name", "")
chat_b = api_base(s.get("chat_model_api_base", ""))
util_p = s.get("util_model_provider", "")
util_n = s.get("util_model_name", "")
util_b = api_base(s.get("util_model_api_base", ""))
brow_p = s.get("browser_model_provider", "")
brow_n = s.get("browser_model_name", "")
brow_b = api_base(s.get("browser_model_api_base", ""))
print("  Chat:    ", chat_p, chat_n, "|", chat_b)
print("  Utility: ", util_p, util_n, "|", util_b)
print("  Browser: ", brow_p, brow_n, "|", brow_b)
' 2>/dev/null || echo "  (could not parse settings)"
}

echo ""
echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo -e "${CYAN}Agent Zero – Status${NC}"
echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo ""

if ! is_running; then
    fail "Container is not running."
    echo ""
    # Best-effort: show settings from host if available
    SETTINGS_FILE=""
    if [[ -n "$A0_USR_PATH" && -f "$A0_USR_PATH/settings.json" ]]; then
        SETTINGS_FILE="$A0_USR_PATH/settings.json"
    elif [[ -f "$REPO_ROOT/usr/settings.json" ]]; then
        SETTINGS_FILE="$REPO_ROOT/usr/settings.json"
    fi
    if [[ -n "$SETTINGS_FILE" ]]; then
        echo -e "  ${CYAN}Settings (from host):${NC}"
        print_settings "$(cat "$SETTINGS_FILE" 2>/dev/null)"
    fi
    echo ""
    exit 1
fi

# Container and health
STATUS=$(docker ps --filter "name=^${CONTAINER_NAME}$" --format "{{.Status}}" 2>/dev/null || echo "unknown")
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "no-healthcheck")
echo -e "  Container:  ${GREEN}running${NC} ($STATUS)"
echo -e "  Health:     $([ "$HEALTH_STATUS" = "healthy" ] && echo -e "${GREEN}healthy${NC}" || echo -e "${YELLOW}${HEALTH_STATUS}${NC}")"
echo ""

# Supervisor services (best-effort)
if docker exec "$CONTAINER_NAME" supervisorctl status run_ui 2>/dev/null | grep -q "RUNNING"; then
    echo -e "  Web UI:     ${GREEN}RUNNING${NC}"
else
    echo -e "  Web UI:     ${YELLOW}check supervisorctl${NC}"
fi
if docker exec "$CONTAINER_NAME" supervisorctl status x11vnc 2>/dev/null | grep -q "RUNNING"; then
    echo -e "  VNC:        ${GREEN}RUNNING${NC}"
else
    echo -e "  VNC:        ${YELLOW}check supervisorctl${NC}"
fi
echo ""

# Settings (from container - what the app actually uses)
echo -e "  ${CYAN}Settings:${NC}"
SETTINGS_JSON=$(docker exec "$CONTAINER_NAME" cat /a0/usr/settings.json 2>/dev/null || true)
if [[ -n "$SETTINGS_JSON" ]]; then
    print_settings "$SETTINGS_JSON"
else
    echo "  (could not read /a0/usr/settings.json from container)"
fi
echo ""

# Access
echo -e "  ${CYAN}Web UI:${NC}     http://localhost:${HOST_PORT}"
echo -e "  ${CYAN}VNC:${NC}        vnc://localhost:5901"
echo ""
echo -e "  Logs:       ${DOCKER_COMPOSE_CMD[*]} logs -f agent-zero"
echo -e "  Stop:       ${DOCKER_COMPOSE_CMD[*]} down"
echo ""
