# Quick Deployment Guide

Deploy Agent Zero on another computer with Docker Desktop in minutes.

## Prerequisites

- Docker Desktop installed and running
- 20GB+ memory allocated to Docker Desktop
- Ports 8888 and 5901 available

## Deployment Steps

### 1. Transfer Agent Zero to Target Computer

**Option A: Git Clone**
```bash
git clone <repository-url> agent-zero
cd agent-zero
```

**Option B: Copy Directory**
```bash
# Copy entire AgentZ directory to target computer
# Then:
cd agent-zero
```

### 2. Run Deployment Script

```bash
./deploy.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Configure environment
- ✅ Build Docker image
- ✅ Start container
- ✅ Verify deployment

### 3. Access Agent Zero

After deployment completes, you'll see:

```
Web UI:     http://localhost:8888
VNC:        vnc://localhost:5901 (password: vnc123)
Username:   [your username]
Password:   [your password]
```

## What's Next?

1. **Open Web UI**: http://localhost:8888
2. **Login** with provided credentials
3. **Configure Model Provider** in Settings
4. **(Optional) Setup Claude Code**: `./scripts/setup/setup_claude_oauth.sh`

## Data Persistence

The `.env` file (containing auth credentials and API keys) is bind-mounted into the container, so your login and API keys survive `docker compose down && up` and image rebuilds. Other persistent data:

- `./memory` - Agent memory and chats
- `./knowledge` - Knowledge base files
- `./logs` - Log files
- `./claude-config` - Claude Code OAuth tokens

## Troubleshooting

**Container won't start?**
```bash
docker compose logs agent-zero
```

**Port in use?**
Edit `.env` and change `HOST_PORT=8888` to another port.

**Need help?**
See `docs/guides/DEPLOYMENT.md` for detailed guide.

## Quick Commands

```bash
# View logs
docker compose logs -f agent-zero

# Stop
docker compose down

# Restart
docker compose restart agent-zero

# Validate
./scripts/testing/validate.sh
```

---

**That's it!** Agent Zero is now deployed and ready to use.
