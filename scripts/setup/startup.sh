#!/bin/bash
# Agent Zero Startup Script
# This script checks for running instances, stops them, updates files, and starts the app

# Don't use set -e, we want to handle errors gracefully

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Ensure Docker + Compose are available
log_info "Checking Docker installation..."
if ! command -v docker >/dev/null 2>&1; then
    log_error "Docker is not installed or not in PATH."
    exit 1
fi

if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD=(docker-compose)
else
    log_error "Docker Compose plugin/binary not found."
    exit 1
fi
log_success "Docker Compose detected: ${DOCKER_COMPOSE_CMD[*]} "

# Step 2: Determine host port (default to 8888, allow override via environment or .env)
DEFAULT_HOST_PORT=8888
if [ -z "${HOST_PORT:-}" ] && [ -f ".env" ]; then
    ENV_PORT=$(grep -E '^HOST_PORT=' .env | tail -n 1 | cut -d '=' -f2-)
    if [ -n "$ENV_PORT" ]; then
        HOST_PORT="$ENV_PORT"
    fi
fi
HOST_PORT="${HOST_PORT:-$DEFAULT_HOST_PORT}"
export HOST_PORT
log_info "Using HOST_PORT=$HOST_PORT"

# Step 3: Stop any existing stack
log_info "Stopping existing Agent Zero containers (if any)..."
"${DOCKER_COMPOSE_CMD[@]}" ps --services >/dev/null 2>&1
if [ $? -eq 0 ]; then
    "${DOCKER_COMPOSE_CMD[@]}" down >/dev/null 2>&1 && log_success "Previous stack stopped" || log_info "Nothing to stop"
else
    log_info "Compose project not initialized yet; skipping stop step."
fi

# Step 4: Build fresh image
log_info "Building Agent Zero Docker image..."
if "${DOCKER_COMPOSE_CMD[@]}" build agent-zero; then
    log_success "Image built successfully"
else
    log_error "Docker image build failed"
    exit 1
fi

# Step 5: Start stack
log_info "Starting Agent Zero container..."
if "${DOCKER_COMPOSE_CMD[@]}" up -d agent-zero; then
    log_success "Container started"
else
    log_error "Failed to start container"
    exit 1
fi

# Step 6: Wait for container to be ready
log_info "Waiting for container to initialize..."
sleep 5

# Step 7: Check VNC services status
log_info "Checking VNC services status..."
if docker exec agent-zero supervisorctl status 2>/dev/null | grep -q "xvfb\|x11vnc\|fluxbox"; then
    log_success "VNC services are running"
else
    log_warning "VNC services may not be running yet. They should start automatically."
    log_info "To check VNC status: docker exec agent-zero supervisorctl status"
fi

# Step 8: Show status + endpoints
log_info "Container status:"
"${DOCKER_COMPOSE_CMD[@]}" ps agent-zero

HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
[ -z "$HOST_IP" ] && HOST_IP=$(ipconfig getifaddr en0 2>/dev/null)
[ -z "$HOST_IP" ] && HOST_IP="localhost"
echo ""
log_success "═══════════════════════════════════════"
log_success "Agent Zero Docker stack is running!"
log_success "═══════════════════════════════════════"
echo ""
log_info "Web UI:  http://$HOST_IP:${HOST_PORT}"
log_info "A2A:     http://$HOST_IP:${HOST_PORT}/a2a"
log_info "VNC:     vnc://$HOST_IP:5901 (password: vnc123)"
echo ""
log_info "Features:"
log_info "  • VNC Desktop Access (for GUI applications and CAPTCHA completion)"
log_info "  • Claude Code Integration (OAuth configured)"
log_info "  • Security Tools (nmap, metasploit, etc.)"
log_info "  • Network Scanning Capabilities (NET_RAW, NET_ADMIN, SYS_ADMIN)"
echo ""
log_info "Useful commands:"
log_info "  ${DOCKER_COMPOSE_CMD[*]} logs -f agent-zero          # view logs"
log_info "  ${DOCKER_COMPOSE_CMD[*]} down                         # stop container"
log_info "  docker exec -it agent-zero bash                       # shell access"
log_info "  docker exec agent-zero supervisorctl status          # check services"
log_info "  docker exec agent-zero claude-pro                    # use Claude Code"
log_info "  HOST_PORT=9000 ${DOCKER_COMPOSE_CMD[*]} up -d agent-zero  # override port"
echo ""
log_info "VNC Access:"
log_info "  macOS: Open Finder → Go → Connect to Server → vnc://localhost:5901"
log_info "  Linux: vncviewer localhost:5901"
log_info "  Windows: Use VNC Viewer → localhost:5901"
log_info "  Password: vnc123"
echo ""

