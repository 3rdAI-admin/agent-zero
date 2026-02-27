#!/bin/bash
# Unified startup script for all Docker services
# Boot order: Supabase → Archon → Agent Zero
#
# Usage:
#   ./start_all.sh              # Start everything
#   ./start_all.sh --archon     # Supabase + Archon only
#   ./start_all.sh --agentz     # Agent Zero only
#   ./start_all.sh --supabase   # Supabase only
#   ./start_all.sh --status     # Show status of all services
#   ./start_all.sh --stop       # Stop everything (preserves data)
#   ./start_all.sh --help       # Show help

set -e

ARCHON_DIR="/Users/james/Docker/Archon"
AGENTZ_DIR="/Users/james/Docker/AgentZ"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }

wait_healthy() {
    local name="$1"
    local max_wait="${2:-120}"
    local elapsed=0
    while [ $elapsed -lt $max_wait ]; do
        status=$(docker inspect --format='{{.State.Health.Status}}' "$name" 2>/dev/null || echo "missing")
        case "$status" in
            healthy) ok "$name is healthy"; return 0;;
            unhealthy) fail "$name is unhealthy"; return 1;;
            *) sleep 3; elapsed=$((elapsed + 3));;
        esac
    done
    warn "$name did not become healthy within ${max_wait}s"
    return 1
}

start_supabase() {
    echo ""
    echo "=== Starting Supabase ==="
    cd "$ARCHON_DIR"

    # Check if already running
    if docker ps --filter "name=supabase_kong_Archon" --format '{{.Status}}' 2>/dev/null | grep -q "Up"; then
        ok "Supabase is already running"
        return 0
    fi

    # Stop cleanly if in a broken state, then start
    supabase stop 2>/dev/null || true
    supabase start 2>&1 | grep -E "^(Started|API URL|DB URL|Studio URL)" || true
    ok "Supabase started"
}

start_archon() {
    echo ""
    echo "=== Starting Archon ==="

    # Verify Supabase network exists
    if ! docker network inspect supabase_network_Archon >/dev/null 2>&1; then
        fail "supabase_network_Archon not found. Start Supabase first."
        return 1
    fi

    cd "$ARCHON_DIR"
    docker compose up -d 2>&1
    ok "Archon containers started"

    echo "  Waiting for archon-server to become healthy..."
    wait_healthy "archon-server" 90
    wait_healthy "archon-mcp" 90
}

start_agentz() {
    echo ""
    echo "=== Starting Agent Zero ==="
    cd "$AGENTZ_DIR"
    docker compose up -d 2>&1
    ok "Agent Zero container started"

    echo "  Waiting for agent-zero to become healthy..."
    wait_healthy "agent-zero" 120
}

show_status() {
    echo ""
    echo "=== Service Status ==="
    echo ""
    echo "Supabase:"
    docker ps --filter "name=supabase_kong_Archon" --filter "name=supabase_db_Archon" \
        --format "  {{.Names}}\t{{.Status}}" 2>/dev/null || echo "  (not running)"
    echo ""
    echo "Archon:"
    docker ps --filter "name=archon" \
        --format "  {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  (not running)"
    echo ""
    echo "Agent Zero:"
    docker ps --filter "name=agent-zero" \
        --format "  {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  (not running)"
    echo ""
}

stop_all() {
    echo ""
    echo "=== Stopping All Services ==="
    echo "  (Data is preserved in bind mounts and Docker volumes)"
    echo ""

    echo "Stopping Agent Zero..."
    cd "$AGENTZ_DIR" && docker compose down 2>/dev/null && ok "Agent Zero stopped" || warn "Agent Zero was not running"

    echo "Stopping Archon..."
    cd "$ARCHON_DIR" && docker compose down 2>/dev/null && ok "Archon stopped" || warn "Archon was not running"

    echo "Stopping Supabase..."
    cd "$ARCHON_DIR" && supabase stop 2>/dev/null && ok "Supabase stopped" || warn "Supabase was not running"

    echo ""
    ok "All services stopped. Data is preserved."
}

show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  (no option)      Start everything: Supabase → Archon → Agent Zero"
    echo "  --archon          Start Supabase + Archon only"
    echo "  --agentz          Start Agent Zero only"
    echo "  --supabase        Start Supabase only"
    echo "  --status          Show status of all services"
    echo "  --stop            Stop everything (preserves all data)"
    echo "  --help, -h        Show this help"
    echo ""
    echo "Service ports:"
    echo "  Agent Zero Web UI:  http://localhost:8888"
    echo "  Agent Zero VNC:     vnc://localhost:5901"
    echo "  Archon UI:          http://localhost:3737"
    echo "  Archon Server API:  http://localhost:8181"
    echo "  Archon MCP:         http://localhost:8051"
    echo "  Supabase Studio:    http://localhost:54323"
}

# Main
case "${1:-all}" in
    all|--all)
        echo "=== Starting All Services ==="
        start_supabase
        start_archon
        start_agentz
        show_status
        echo "=== All services started ==="
        ;;
    --archon)
        start_supabase
        start_archon
        show_status
        ;;
    --agentz)
        start_agentz
        show_status
        ;;
    --supabase)
        start_supabase
        show_status
        ;;
    --status|-s)
        show_status
        ;;
    --stop)
        stop_all
        ;;
    --help|-h)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
