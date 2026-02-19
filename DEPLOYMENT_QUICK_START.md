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
- `./claude-config` - Claude Code OAuth config
- `./claude-credentials` - Claude Code credential tokens
- `./claude-keyring` - Claude keyring data
- `./claude-gnome-keyring` - GNOME keyring data

## LAN Access

To access Agent Zero from another device on your network:

1. **Set authentication** in `.env` (required for non-localhost access):
   ```bash
   AUTH_LOGIN=your_username
   AUTH_PASSWORD=your_password
   ```

2. **Add your LAN IP** to `ALLOWED_ORIGINS` in `.env` (comma-separated):
   ```bash
   ALLOWED_ORIGINS=*://localhost:*,*://127.0.0.1:*,*://0.0.0.0:*,*://192.168.x.x:*
   ```

3. Open `http://<host-IP>:8888` from any device on the LAN.

> Without `AUTH_LOGIN` set or your IP in `ALLOWED_ORIGINS`, you'll get: `"Origin not allowed when login is disabled"`

## HTTPS / TLS for Remote Clients

Agent Zero serves HTTPS inside the container. For remote MCP or A2A clients connecting via `https://<LAN-IP>:8888`, add your host LAN IP to the TLS certificate:

1. In `docker-compose.yml`, set `AGENT_ZERO_CERT_IPS` to your host LAN IP:
   ```yaml
   environment:
     - AGENT_ZERO_CERT_IPS=192.168.x.x
   ```
2. Uncomment `AGENT_ZERO_REGENERATE_CERT=1`, restart, then re-comment it.

## Troubleshooting

**"Origin not allowed" error?**
Set `AUTH_LOGIN` and `AUTH_PASSWORD` in `.env`, or add your IP to `ALLOWED_ORIGINS` (comma-separated, not semicolons). Restart the container.

**Container won't start?**
```bash
docker compose logs agent-zero
```

**Port in use?**
Edit `.env` and change `HOST_PORT=8888` to another port.

## Performance (if Agent Zero feels slow)

1. **Give Docker enough memory**  
   The container is configured to use up to **16GB** RAM. In **Docker Desktop → Settings → Resources → Memory**, set at least **16GB** (20GB+ recommended). Apply & Restart.

2. **Reservations**  
   `docker-compose.yml` reserves **8GB** and **2 CPUs** for the container so it doesn’t get starved when the host is busy. If you have RAM to spare, you can raise the `limits.memory` and `reservations.memory` values there.

3. **In the Web UI (Settings)**  
   - Use a **faster or lighter model** (e.g. a “mini” variant) for chat if you don’t need the heaviest model.  
   - Lower **Context window space for chat history** (e.g. from 0.7 to 0.5) to send fewer tokens per request.  
   - Ensure **rate limits** (requests/tokens per minute) aren’t set so low that the agent is always waiting.

4. **Restart after changing Docker resources**  
   After changing Docker Desktop memory/CPU, run `docker compose down && docker compose up -d` so the container gets the new limits.

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
