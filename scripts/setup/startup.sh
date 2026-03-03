#!/bin/bash
# Agent Zero startup: check GitHub updates → check running instance → graceful shutdown → start → health check → status.
# Run from repo root (where docker-compose.yml and .env live).

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# Docker Compose command
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD=(docker compose)
else
    DOCKER_COMPOSE_CMD=(docker-compose)
fi

CONTAINER_NAME="agent-zero"
HOST_PORT="${HOST_PORT:-8888}"
STOP_TIMEOUT=30
HEALTH_WAIT_MAX=90
GITHUB_TIMEOUT=8

info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail()  { echo -e "${RED}[FAIL]${NC} $1"; }

is_running() {
    docker ps --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" 2>/dev/null | grep -q "^${CONTAINER_NAME}$"
}

# ─── 0. Check GitHub for updates (best-effort, non-fatal) ───────────────────
check_github_updates() {
    info "Checking GitHub for updates (Agent Zero / ZeroClaw)..."
    UPDATES=""
    # Agent Zero: compare with origin and optionally upstream (agent0ai/agent-zero)
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
        REMOTE=$(git config --get branch."${BRANCH}".remote 2>/dev/null || echo "origin")
        TRACKING="${REMOTE}/${BRANCH}"
        if git rev-parse "${TRACKING}" >/dev/null 2>&1; then
            if command -v timeout >/dev/null 2>&1; then timeout "${GITHUB_TIMEOUT}" git fetch --quiet "$REMOTE" 2>/dev/null; else git fetch --quiet "$REMOTE" 2>/dev/null; fi || true
            BEHIND=$(git rev-list --count HEAD.."${TRACKING}" 2>/dev/null || echo "0")
            AHEAD=$(git rev-list --count "${TRACKING}"..HEAD 2>/dev/null || echo "0")
            if [ "${BEHIND}" -gt 0 ] 2>/dev/null; then
                UPDATES="${UPDATES}  Agent Zero: ${YELLOW}${BEHIND} commit(s) behind ${TRACKING}${NC}"
            elif [ "${AHEAD}" -gt 0 ] 2>/dev/null; then
                UPDATES="${UPDATES}  Agent Zero: ${GREEN}up to date (${AHEAD} ahead of ${TRACKING})${NC}"
            else
                UPDATES="${UPDATES}  Agent Zero: ${GREEN}up to date with ${TRACKING}${NC}"
            fi
        else
            if command -v timeout >/dev/null 2>&1; then timeout "${GITHUB_TIMEOUT}" git fetch --quiet origin 2>/dev/null; else git fetch --quiet origin 2>/dev/null; fi || true
            UPDATES="${UPDATES}  Agent Zero: ${CYAN}on ${BRANCH} (no tracking)${NC}"
        fi
        # If upstream remote exists (e.g. agent0ai/agent-zero), show how we compare
        if git remote get-url upstream >/dev/null 2>&1; then
            if command -v timeout >/dev/null 2>&1; then timeout "${GITHUB_TIMEOUT}" git fetch --quiet upstream 2>/dev/null; else git fetch --quiet upstream 2>/dev/null; fi || true
            UPSTREAM_MAIN="upstream/main"
            if ! git rev-parse "$UPSTREAM_MAIN" >/dev/null 2>&1; then
                UPSTREAM_MAIN="upstream/master"
            fi
            if git rev-parse "$UPSTREAM_MAIN" >/dev/null 2>&1; then
                BEHIND_UP=$(git rev-list --count HEAD.."$UPSTREAM_MAIN" 2>/dev/null || echo "0")
                if [ "${BEHIND_UP}" -gt 0 ] 2>/dev/null; then
                    UPDATES="${UPDATES}\n  Upstream:   ${YELLOW}${BEHIND_UP} commit(s) behind upstream/main${NC}"
                else
                    UPDATES="${UPDATES}\n  Upstream:   ${GREEN}up to date with upstream${NC}"
                fi
            fi
        fi
    else
        UPDATES="${UPDATES}  Agent Zero: ${CYAN}not a git repo, skip${NC}"
    fi
    # ZeroClaw: latest release or latest commit on main via GitHub API
    if command -v curl >/dev/null 2>&1; then
        ZEROCLAW_RELEASE=$(curl -s --max-time "${GITHUB_TIMEOUT}" -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/repos/zeroclaw-labs/zeroclaw/releases/latest" 2>/dev/null)
        if [ -n "$ZEROCLAW_RELEASE" ] && echo "$ZEROCLAW_RELEASE" | grep -q '"tag_name"'; then
            ZEROCLAW_TAG=$(echo "$ZEROCLAW_RELEASE" | tr -d '\n' | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
            UPDATES="${UPDATES}\n  ZeroClaw:   ${CYAN}latest release ${ZEROCLAW_TAG}${NC}"
        else
            ZEROCLAW_COMMIT=$(curl -s --max-time "${GITHUB_TIMEOUT}" -H "Accept: application/vnd.github.v3+json" \
                "https://api.github.com/repos/zeroclaw-labs/zeroclaw/commits/main" 2>/dev/null)
            if [ -n "$ZEROCLAW_COMMIT" ] && echo "$ZEROCLAW_COMMIT" | grep -q '"sha"'; then
                ZEROCLAW_SHA=$(echo "$ZEROCLAW_COMMIT" | tr -d '\n' | sed -n 's/.*"sha"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1 | cut -c1-7)
                UPDATES="${UPDATES}\n  ZeroClaw:   ${CYAN}main @ ${ZEROCLAW_SHA}${NC}"
            else
                UPDATES="${UPDATES}\n  ZeroClaw:   ${YELLOW}could not reach GitHub${NC}"
            fi
        fi
    else
        UPDATES="${UPDATES}\n  ZeroClaw:   ${YELLOW}curl not available${NC}"
    fi
    echo -e "$UPDATES"
}

check_github_updates || true
echo ""

# ─── 1. Check for running instance ─────────────────────────────────────────
info "Checking for running Agent Zero..."
if is_running; then
    ok "Running instance found; shutting down gracefully (timeout ${STOP_TIMEOUT}s)..."
    "${DOCKER_COMPOSE_CMD[@]}" stop -t "$STOP_TIMEOUT" agent-zero 2>/dev/null || docker stop -t "$STOP_TIMEOUT" "$CONTAINER_NAME" 2>/dev/null || true
    # Allow a moment for the container to fully stop
    sleep 2
    if is_running; then
        warn "Container still running after stop; forcing..."
        docker kill "$CONTAINER_NAME" 2>/dev/null || true
        sleep 1
    fi
    ok "Stopped."
else
    info "No running instance."
fi

# ─── 2. Start ─────────────────────────────────────────────────────────────
info "Starting Agent Zero..."
if ! "${DOCKER_COMPOSE_CMD[@]}" up -d agent-zero; then
    fail "Failed to start. Check: ${DOCKER_COMPOSE_CMD[*]} logs agent-zero"
    exit 1
fi
ok "Start command issued."

# ─── 3. Health check ──────────────────────────────────────────────────────
info "Waiting for health (max ${HEALTH_WAIT_MAX}s)..."
WAITED=0
HEALTH_STATUS=""
while [ $WAITED -lt $HEALTH_WAIT_MAX ]; do
    if ! is_running; then
        fail "Container exited unexpectedly."
        docker logs --tail 30 "$CONTAINER_NAME" 2>/dev/null || true
        exit 1
    fi
    HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "no-healthcheck")
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        ok "Container is healthy."
        break
    fi
    # Also accept: Web UI /health responds (in case healthcheck not yet updated)
    if docker exec "$CONTAINER_NAME" curl -fsS -o /dev/null --max-time 3 http://localhost:80/health 2>/dev/null; then
        ok "Web UI responding."
        break
    fi
    echo -n "."
    sleep 3
    WAITED=$((WAITED + 3))
done
echo ""

if [ $WAITED -ge $HEALTH_WAIT_MAX ]; then
    warn "Health check did not pass within ${HEALTH_WAIT_MAX}s. Container may still be starting."
    warn "Check: docker logs $CONTAINER_NAME"
fi

# ─── 4. Status (container, health, settings, access) ─────────────────────
export CONTAINER_NAME HOST_PORT
"$REPO_ROOT/scripts/show_status.sh" || exit 1
