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

LAST_CONTAINER_SCHEME="http"

container_endpoint_code() {
    local path="$1"
    local code="000"
    local scheme
    for scheme in http https; do
        if [ "$scheme" = "https" ]; then
            code=$(docker exec "$CONTAINER_NAME" curl -sk -o /dev/null -w '%{http_code}' --max-time 3 "${scheme}://localhost:80${path}" 2>/dev/null || echo "000")
        else
            code=$(docker exec "$CONTAINER_NAME" curl -s -o /dev/null -w '%{http_code}' --max-time 3 "${scheme}://localhost:80${path}" 2>/dev/null || echo "000")
        fi
        if [ "$code" != "000" ]; then
            LAST_CONTAINER_SCHEME="$scheme"
            echo "$code"
            return 0
        fi
    done
    echo "000"
}

container_endpoint_body() {
    local path="$1"
    if [ "${LAST_CONTAINER_SCHEME:-http}" = "https" ]; then
        docker exec "$CONTAINER_NAME" curl -sk --max-time 3 "https://localhost:80${path}" 2>/dev/null || true
    else
        docker exec "$CONTAINER_NAME" curl -s --max-time 3 "http://localhost:80${path}" 2>/dev/null || true
    fi
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

print_ready_status() {
    local code="$1"
    local body="$2"

    if [[ -z "$body" ]]; then
        echo -e "  Ready:      ${YELLOW}unknown${NC}"
        return
    fi

    READY_BODY_ENV="$body" python3 - "$code" <<'PY'
import json
import os
import sys

code = sys.argv[1]
try:
    payload = json.loads(os.environ.get("READY_BODY_ENV", ""))
except Exception:
    print("  Ready:      unknown")
    raise SystemExit(0)

ready = bool(payload.get("ready"))
phases = payload.get("phases", {}) if isinstance(payload, dict) else {}
blocking = [
    name
    for name, phase in phases.items()
    if isinstance(phase, dict)
    and phase.get("required")
    and phase.get("status") != "ready"
]
degraded = [
    name
    for name, phase in phases.items()
    if isinstance(phase, dict)
    and not phase.get("required")
    and phase.get("status") == "failed"
]

if ready:
    print("  Ready:      ready")
else:
    reason = ", ".join(blocking) if blocking else f"http {code}"
    print(f"  Ready:      not ready ({reason})")

if degraded:
    print(f"  Degraded:   {', '.join(degraded)}")
PY
}

print_runtime_state_status() {
    local body="$1"

    if [[ -z "$body" ]]; then
        echo "  Runtime:    unavailable"
        return
    fi

    RUNTIME_STATE_ENV="$body" python3 - <<'PY'
import json
import os

try:
    payload = json.loads(os.environ.get("RUNTIME_STATE_ENV", ""))
except Exception:
    print("  Runtime:    unavailable")
    raise SystemExit(0)

paths = payload.get("paths", {})
seed = payload.get("seed", {})
env = payload.get("env", {})
runtime = payload.get("runtime", {})
models = payload.get("models", {})
mcp = payload.get("mcp", {})
drift = payload.get("drift", {})

live_path = paths.get("effective_settings_path", "(unknown)")
seed_path = paths.get("repo_seed_settings_path", "(unknown)")
seed_source = seed.get("source", "default_settings")
override_count = env.get("override_count", 0)
override_suffix = ""
if override_count:
    override_suffix = f" ({override_count} override key(s))"

print(f"  Runtime:    live={live_path}")
print(f"  Seed:       {seed_source} @ {seed_path}")
print(
    "  Env:        root={root_present} usr={user_present}{suffix}".format(
        root_present="yes" if env.get("root_env_present") else "no",
        user_present="yes" if env.get("user_env_present") else "no",
        suffix=override_suffix,
    )
)
print(
    "  Derived:    {fields}".format(
        fields=", ".join(runtime.get("runtime_derived_fields", [])) or "(none)"
    )
)

live_models = models.get("live", {})
seed_models = models.get("seed", {})
print(
    "  Models:     live chat={chat} | util={utility} | browser={browser}".format(
        chat=live_models.get("chat", "(unset)"),
        utility=live_models.get("utility", "(unset)"),
        browser=live_models.get("browser", "(unset)"),
    )
)
if models.get("drift_fields"):
    print(
        "  Model drift: fields={fields}".format(
            fields=", ".join(models.get("drift_fields", []))
        )
    )
    print(
        "  Model seed:  chat={chat} | util={utility} | browser={browser}".format(
            chat=seed_models.get("chat", "(unset)"),
            utility=seed_models.get("utility", "(unset)"),
            browser=seed_models.get("browser", "(unset)"),
        )
    )

live_servers = ", ".join(mcp.get("live_server_names", [])) or "(none)"
seed_servers = ", ".join(mcp.get("seed_server_names", [])) or "(none)"
print(f"  MCP:        live={live_servers}")
if mcp.get("drift_fields"):
    print("  MCP drift:  fields={fields}".format(fields=", ".join(mcp.get("drift_fields", []))))
    print(f"  MCP seed:   {seed_servers}")

for warning in drift.get("warnings", []):
    print(f"  Warning:    {warning}")
PY
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
container_endpoint_code "/health" >/dev/null
READY_CODE=$(container_endpoint_code "/ready")
READY_BODY=$(container_endpoint_body "/ready")
echo -e "  Container:  ${GREEN}running${NC} ($STATUS)"
echo -e "  Health:     $([ "$HEALTH_STATUS" = "healthy" ] && echo -e "${GREEN}healthy${NC}" || echo -e "${YELLOW}${HEALTH_STATUS}${NC}")"
print_ready_status "$READY_CODE" "$READY_BODY"
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

# Runtime truth and drift warnings from the live container.
echo -e "  ${CYAN}Runtime State:${NC}"
RUNTIME_STATE_JSON=$(docker exec "$CONTAINER_NAME" /bin/sh -lc 'PYTHONPATH=/a0 /opt/venv-a0/bin/python -c "import json, sys; sys.argv.append(\"--dockerized=true\"); from python.helpers import runtime; runtime.initialize(); from python.helpers.runtime_state_report import build_runtime_state_report; print(json.dumps(build_runtime_state_report()))"' 2>/dev/null || true)
print_runtime_state_status "$RUNTIME_STATE_JSON"
echo ""

# Access
echo -e "  ${CYAN}Web UI:${NC}     ${LAST_CONTAINER_SCHEME}://localhost:${HOST_PORT}"
echo -e "  ${CYAN}VNC:${NC}        vnc://localhost:5901"
echo ""
echo -e "  Logs:       ${DOCKER_COMPOSE_CMD[*]} logs -f agent-zero"
echo -e "  Stop:       ${DOCKER_COMPOSE_CMD[*]} down"
echo ""
