# Agent Zero Deployment Guide

Complete guide for deploying Agent Zero on a new computer with Docker Desktop.

## Prerequisites

- **Docker Desktop** installed and running
  - Download: https://www.docker.com/products/docker-desktop
  - **Memory**: Allocate at least 20GB in Docker Desktop settings
  - **CPU**: Allocate at least 4 cores
- **Ports available**: 8888 (Web UI), 5901 (VNC)
- **Internet connection** for initial build

## Quick Deployment

### Method 1: Automated Deployment Script (Recommended)

```bash
# Clone or copy Agent Zero to target computer
git clone <repository-url> agent-zero
# OR copy the entire AgentZ directory

cd agent-zero

# Run deployment script
./deploy.sh
```

The script will:
1. ✅ Check Docker Desktop installation
2. ✅ Verify port availability
3. ✅ Create `.env` file with credentials
4. ✅ Create required directories
5. ✅ Build Docker image
6. ✅ Start container
7. ✅ Verify deployment
8. ✅ Display access information

### Method 2: Manual Deployment

```bash
# 1. Create .env file
cp .env.example .env
# Edit .env with your configuration

# 2. Create directories
mkdir -p memory knowledge logs tmp claude-config claude-credentials

# 3. Build and start
docker compose build
docker compose up -d

# 4. Verify
docker ps | grep agent-zero
```

## Deployment Script Details

### What It Does

1. **Prerequisites Check**
   - Verifies Docker Desktop is installed
   - Checks Docker daemon is running
   - Verifies Docker Compose availability
   - Checks system resources

2. **Port Configuration**
   - Prompts for Web UI port (default: 8888)
   - Checks port availability
   - Checks VNC port (5901)

3. **Environment Setup**
   - Creates `.env` file if missing
   - Prompts for username/password
   - Generates random password if not provided
   - Configures HOST_PORT

4. **Directory Creation**
   - Creates all required volume directories
   - Ensures proper permissions

5. **Container Management**
   - Stops existing containers
   - Builds fresh Docker image
   - Starts container with proper configuration

6. **Verification**
   - Waits for services to initialize
   - Checks container status
   - Verifies Web UI accessibility
   - Checks service status

7. **Access Information**
   - Displays Web UI URLs (localhost and LAN)
   - Shows VNC access information
   - Displays credentials
   - Provides useful commands

## Configuration

### Environment Variables (.env)

The deployment script creates a `.env` file with:

```bash
HOST_PORT=8888
AUTH_LOGIN=admin
AUTH_PASSWORD=your_password

# Model Provider (configure in Web UI Settings)
# CHAT_MODEL_PROVIDER=ollama
# CHAT_MODEL_NAME=qwen3:latest
# CHAT_MODEL_API_BASE=http://localhost:11434
```

### Manual Configuration

Edit `.env` file to customize:

```bash
# Web UI Port
HOST_PORT=8888

# Authentication
AUTH_LOGIN=your_username
AUTH_PASSWORD=your_secure_password

# Model Provider (optional - can configure in Web UI)
CHAT_MODEL_PROVIDER=ollama
CHAT_MODEL_NAME=qwen3:latest
CHAT_MODEL_API_BASE=http://localhost:11434
```

## Post-Deployment

### 1. Access Web UI

Open browser: `http://localhost:8888`

Login with credentials from deployment script.

### 2. Configure Model Provider

1. Go to **Settings** in Web UI
2. Configure **Chat Model** provider
3. Set API URL and model name
4. Click **Save**

### 3. (Optional) Setup Claude Code

```bash
# Setup Claude Code OAuth
./scripts/setup/setup_claude_oauth.sh

# Configure MCP token
./scripts/setup/configure_mcp_token.sh
```

### 4. Verify Deployment

```bash
# Run validation
./scripts/testing/validate.sh

# Check services
docker exec agent-zero supervisorctl status

# View logs
docker compose logs -f agent-zero
```

## Access Points

### Web UI
- **Local**: http://localhost:8888
- **LAN**: http://<your-ip>:8888

### VNC Desktop
- **Local**: `vnc://localhost:5901`
- **LAN**: `vnc://<your-ip>:5901`
- **Password**: `vnc123`

### A2A API
- **Local**: http://localhost:8888/a2a
- **LAN**: http://<your-ip>:8888/a2a

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs agent-zero

# Check Docker Desktop resources
# Settings → Resources → Memory (should be 20GB+)

# Restart Docker Desktop
```

### Port Already in Use

```bash
# Change port in .env
HOST_PORT=9000

# Restart
docker compose down
docker compose up -d
```

### Web UI Not Accessible

```bash
# Check container status
docker ps | grep agent-zero

# Check logs
docker logs agent-zero

# Wait longer (initialization takes 30-60 seconds)
docker compose logs -f agent-zero
```

### Build Fails

```bash
# Check Docker Desktop resources
# Increase memory allocation to 20GB+

# Clean build
docker compose down
docker system prune -a
docker compose build --no-cache
```

## Updating Deployment

```bash
# Pull latest changes (if git repo)
git pull

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

## Uninstalling

```bash
# Stop and remove container
docker compose down

# Remove image (optional)
docker rmi agent-zero:local

# Remove volumes (optional - deletes all data)
docker volume prune
```

## Security Considerations

1. **Change Default Password**: Use strong password in `.env`
2. **Firewall**: Configure firewall rules for exposed ports
3. **Network Access**: Only expose to trusted networks
4. **Credentials**: Keep `.env` file secure, don't commit to git

## Support

- **Documentation**: See `docs/README.md`
- **Troubleshooting**: See `docs/troubleshooting/`
- **Validation**: Run `./scripts/testing/validate.sh`
