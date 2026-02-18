#!/bin/bash
# Agent Zero Deployment Script
# Deploys Agent Zero on a new computer with Docker Desktop

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Logging functions
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

log_step() {
    echo -e "\n${CYAN}═══════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════${NC}\n"
}

# Banner
echo -e "${CYAN}"
cat << "EOF"
    ___                  ______              
   /   |  ____  ____    / ____/___  ________
  / /| | / __ \/ __ \  / __/ / __ \/ ___/ _ \
 / ___ |/ /_/ / /_/ / / /___/ / / / /__/  __/
/_/  |_/ .___/ .___/ /_____/_/ /_/\___/\___/
      /_/   /_/                             
EOF
echo -e "${NC}"
echo -e "${CYAN}Agent Zero Deployment Script${NC}"
echo ""

# Step 1: Check Prerequisites
log_step "Step 1: Checking Prerequisites"

log_info "Checking Docker installation..."
if ! command -v docker >/dev/null 2>&1; then
    log_error "Docker is not installed or not in PATH."
    log_info "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    log_error "Docker daemon is not running."
    log_info "Please start Docker Desktop and try again."
    exit 1
fi

log_success "Docker is installed and running"

# Check Docker Compose
log_info "Checking Docker Compose..."
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD=(docker compose)
    log_success "Docker Compose plugin detected"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD=(docker-compose)
    log_success "Docker Compose binary detected"
else
    log_error "Docker Compose not found."
    log_info "Docker Desktop should include Docker Compose. Please update Docker Desktop."
    exit 1
fi

# Check available resources
log_info "Checking system resources..."
TOTAL_MEM=$(docker info 2>/dev/null | grep -i "Total Memory" | awk '{print $3}' || echo "unknown")
if [ "$TOTAL_MEM" != "unknown" ]; then
    log_info "Docker available memory: $TOTAL_MEM"
    log_warning "Agent Zero requires 16GB memory limit. Ensure Docker Desktop has sufficient memory allocated."
    log_info "Docker Desktop → Settings → Resources → Memory (recommend 20GB+)"
fi

# Step 2: Check Port Availability
log_step "Step 2: Checking Port Availability"

DEFAULT_PORT=8888
read -p "Enter port for Web UI [$DEFAULT_PORT]: " HOST_PORT
HOST_PORT=${HOST_PORT:-$DEFAULT_PORT}

if lsof -Pi :$HOST_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "Port $HOST_PORT is already in use"
    read -p "Continue anyway? (y/N): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
else
    log_success "Port $HOST_PORT is available"
fi

if lsof -Pi :5901 -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "Port 5901 (VNC) is already in use"
else
    log_success "Port 5901 (VNC) is available"
fi

export HOST_PORT

# Step 3: Environment Configuration
log_step "Step 3: Environment Configuration"

if [ ! -f ".env" ]; then
    log_info "Creating .env file..."
    
    # Generate default credentials
    DEFAULT_USER="admin"
    DEFAULT_PASS=$(openssl rand -base64 12 2>/dev/null || echo "changeme123")
    
    read -p "Enter Web UI username [$DEFAULT_USER]: " AUTH_USER
    AUTH_USER=${AUTH_USER:-$DEFAULT_USER}
    
    read -sp "Enter Web UI password (or press Enter for random): " AUTH_PASS
    echo ""
    if [ -z "$AUTH_PASS" ]; then
        AUTH_PASS=$(openssl rand -base64 16 2>/dev/null || echo "changeme123")
        log_info "Generated random password"
    fi
    
    # Create .env file
    cat > .env << EOF
# Agent Zero Configuration
HOST_PORT=$HOST_PORT
AUTH_LOGIN=$AUTH_USER
AUTH_PASSWORD=$AUTH_PASS

# Model Provider Configuration
# Uncomment and configure your model provider:
# CHAT_MODEL_PROVIDER=ollama
# CHAT_MODEL_NAME=qwen3:latest
# CHAT_MODEL_API_BASE=http://localhost:11434

# Optional: RFC Password for development features
# RFC_PASSWORD=$(openssl rand -base64 32 2>/dev/null || echo "")
EOF
    
    log_success ".env file created"
    log_warning "IMPORTANT: Save these credentials!"
    log_info "Username: $AUTH_USER"
    log_info "Password: $AUTH_PASS"
    echo ""
else
    log_info ".env file already exists, using existing configuration"
    # Update HOST_PORT if different
    if grep -q "^HOST_PORT=" .env; then
        sed -i.bak "s/^HOST_PORT=.*/HOST_PORT=$HOST_PORT/" .env
    else
        echo "HOST_PORT=$HOST_PORT" >> .env
    fi
fi

# Step 4: Create Required Directories
log_step "Step 4: Creating Required Directories"

REQUIRED_DIRS=("memory" "knowledge" "logs" "tmp" "claude-config" "claude-credentials" "claude-keyring" "claude-gnome-keyring")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log_success "Created directory: $dir"
    else
        log_info "Directory exists: $dir"
    fi
done

# Step 5: Stop Existing Containers
log_step "Step 5: Stopping Existing Containers (if any)"

if docker ps -a --format "{{.Names}}" | grep -q "^agent-zero$"; then
    log_info "Stopping existing Agent Zero container..."
    "${DOCKER_COMPOSE_CMD[@]}" down 2>/dev/null || docker stop agent-zero 2>/dev/null || true
    docker rm agent-zero 2>/dev/null || true
    log_success "Existing container stopped"
else
    log_info "No existing container found"
fi

# Step 6: Build Docker Image
log_step "Step 6: Building Docker Image"

log_info "This may take several minutes on first build..."
log_info "Building Agent Zero image..."

if "${DOCKER_COMPOSE_CMD[@]}" build --progress=plain agent-zero; then
    log_success "Docker image built successfully"
else
    log_error "Docker image build failed"
    log_info "Check Docker Desktop resources and try again"
    exit 1
fi

# Step 7: Start Container
log_step "Step 7: Starting Container"

log_info "Starting Agent Zero container..."
if "${DOCKER_COMPOSE_CMD[@]}" up -d agent-zero; then
    log_success "Container started"
else
    log_error "Failed to start container"
    exit 1
fi

# Step 8: Wait for Services
log_step "Step 8: Waiting for Services to Initialize"

log_info "Waiting for container to be ready (this may take 30-60 seconds)..."
sleep 10

MAX_WAIT=60
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if docker exec agent-zero curl -s -f http://localhost:80 >/dev/null 2>&1; then
        log_success "Web UI is ready!"
        break
    fi
    echo -n "."
    sleep 2
    WAITED=$((WAITED + 2))
done
echo ""

if [ $WAITED -ge $MAX_WAIT ]; then
    log_warning "Web UI may still be initializing. Check logs: docker logs agent-zero"
fi

# Step 9: Verify Deployment
log_step "Step 9: Verifying Deployment"

# Check container status
if docker ps --format "{{.Names}}" | grep -q "^agent-zero$"; then
    log_success "Container is running"
else
    log_error "Container is not running"
    log_info "Check logs: docker logs agent-zero"
    exit 1
fi

# Check services
log_info "Checking services..."
SERVICES_RUNNING=0
if docker exec agent-zero supervisorctl status run_ui 2>/dev/null | grep -q "RUNNING"; then
    log_success "Agent Zero service: RUNNING"
    SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
else
    log_warning "Agent Zero service: Starting..."
fi

if docker exec agent-zero supervisorctl status x11vnc 2>/dev/null | grep -q "RUNNING"; then
    log_success "VNC service: RUNNING"
    SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
else
    log_warning "VNC service: Starting..."
fi

# Step 10: Display Access Information
log_step "Step 10: Deployment Complete!"

# Get host IP
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    HOST_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    HOST_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
else
    HOST_IP="localhost"
fi

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Agent Zero is Deployed!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
log_success "Access Information:"
echo ""
echo -e "  ${CYAN}Web UI:${NC}     http://localhost:$HOST_PORT"
echo -e "  ${CYAN}LAN Access:${NC}  http://$HOST_IP:$HOST_PORT"
echo -e "  ${CYAN}VNC Desktop:${NC} vnc://localhost:5901 (password: vnc123)"
echo -e "  ${CYAN}VNC LAN:${NC}     vnc://$HOST_IP:5901 (password: vnc123)"
echo ""
log_success "Credentials:"
AUTH_USER=$(grep "^AUTH_LOGIN=" .env | cut -d'=' -f2)
AUTH_PASS=$(grep "^AUTH_PASSWORD=" .env | cut -d'=' -f2)
echo -e "  ${CYAN}Username:${NC} $AUTH_USER"
echo -e "  ${CYAN}Password:${NC} $AUTH_PASS"
echo ""
log_success "Useful Commands:"
echo ""
echo "  # View logs"
echo "  ${DOCKER_COMPOSE_CMD[*]} logs -f agent-zero"
echo ""
echo "  # Stop Agent Zero"
echo "  ${DOCKER_COMPOSE_CMD[*]} down"
echo ""
echo "  # Restart Agent Zero"
echo "  ${DOCKER_COMPOSE_CMD[*]} restart agent-zero"
echo ""
echo "  # Shell access"
echo "  docker exec -it agent-zero bash"
echo ""
echo "  # Check services"
echo "  docker exec agent-zero supervisorctl status"
echo ""
echo "  # Run validation"
echo "  ./scripts/testing/validate.sh"
echo ""
log_warning "Next Steps:"
echo ""
echo "  1. Open Web UI: http://localhost:$HOST_PORT"
echo "  2. Log in with credentials above"
echo "  3. Configure model provider in Settings"
echo "  4. (Optional) Setup Claude Code OAuth: ./scripts/setup/setup_claude_oauth.sh"
echo ""
log_info "For detailed documentation, see: docs/README.md"
echo ""
