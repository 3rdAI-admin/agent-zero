# Claude Code OAuth Authentication for Pro Subscription

## Overview

To use your Claude Pro subscription (instead of API key which costs per-use), you need to complete OAuth authentication. This guide helps you authenticate in a headless Docker container.

## Method 1: Manual OAuth Flow (Recommended)

### Step 1: Start OAuth Authentication

Run Claude Code without API key to trigger OAuth:

```bash
docker exec -it agent-zero claude-oauth
```

Or manually:
```bash
docker exec -it agent-zero bash
unset ANTHROPIC_API_KEY
unset API_KEY_ANTHROPIC
claude
```

### Step 2: Get OAuth URL

Claude Code will display an OAuth URL like:
```
https://claude.ai/oauth/authorize?code=true&client_id=...
```

**Copy this entire URL.**

### Step 3: Open URL in Host Browser

1. **Open a web browser** on your host machine (outside Docker)
2. **Paste the OAuth URL** into the address bar
3. **Complete Cloudflare CAPTCHA** if prompted
4. **Sign in** with your Claude Pro account
5. **Authorize** Claude Code

### Step 4: Get Authorization Code

After authorizing, you'll see:
- An authorization code on the page, OR
- The code in the redirect URL (look for `code=...`)

**Copy this authorization code** (usually 6-8 characters).

### Step 5: Paste Code in Container

1. **Return to the container terminal**
2. **Paste the code** at the prompt:
   ```
   Paste code here if prompted >
   ```
3. **Press Enter**

### Step 6: Verify Authentication

Claude Code should now be authenticated with your Pro subscription!

## Method 2: Using Browser in Container (Advanced)

If you want to use a browser inside the container:

### Setup Virtual Display

```bash
docker exec -it agent-zero bash

# Start virtual display
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Start window manager
fluxbox &

# Start VNC server (optional - to view from host)
x11vnc -display :99 -nopw -listen 0.0.0.0 -xkb -forever -shared &
```

### Access Browser via VNC

1. **Connect VNC viewer** from host to `localhost:5900`
2. **Open browser** in the VNC session
3. **Complete OAuth** flow in the browser

### Or Use Headless Browser Script

```bash
docker exec -it agent-zero claude-auth-browser
```

This automatically sets up the virtual display and starts Claude Code.

## Method 3: Transfer Authentication from Host

If you have Claude Code working on your host machine:

```bash
# On host machine, copy Claude Code config
docker cp ~/.config/claude-code agent-zero:/root/.config/claude-code

# Or copy just the auth token
docker cp ~/.config/claude-code/auth.json agent-zero:/root/.config/claude-code/
```

## Switching Between API Key and OAuth

### Use OAuth (Pro Subscription):
```bash
docker exec -it agent-zero claude-oauth
# Or manually unset API key:
unset ANTHROPIC_API_KEY
claude
```

### Use API Key (Pay-per-use):
```bash
docker exec -it agent-zero claude
# API key is automatically set by wrapper
```

## Troubleshooting

### Cloudflare CAPTCHA Issues

**Problem:** Can't complete CAPTCHA in headless container

**Solution:** 
1. Use Method 1 (manual OAuth from host browser)
2. Complete CAPTCHA on host machine
3. Copy authorization code back to container

### OAuth URL Expires

**Problem:** OAuth URL expired

**Solution:** Run `claude-oauth` again to get a fresh URL

### Authentication Not Persisting

**Problem:** Need to re-authenticate after container restart

**Solution:** 
- Claude Code config is stored in `/root/.config/claude-code/`
- This directory persists if you mount it as a volume
- Add to docker-compose.yml:
  ```yaml
  volumes:
    - ./claude-config:/root/.config/claude-code
  ```

### Check Current Authentication Method

```bash
# Check if using API key
docker exec agent-zero env | grep ANTHROPIC

# Check Claude Code config
docker exec agent-zero ls -la /root/.config/claude-code/
```

## Making OAuth Persistent

To ensure OAuth authentication persists across container restarts:

1. **Mount Claude Code config directory:**
   ```yaml
   # In docker-compose.yml
   volumes:
     - ./claude-config:/root/.config/claude-code
   ```

2. **Or copy config after authentication:**
   ```bash
   docker cp agent-zero:/root/.config/claude-code ./claude-config
   ```

## Quick Reference

**Start OAuth authentication:**
```bash
docker exec -it agent-zero claude-oauth
```

**Use browser-assisted auth:**
```bash
docker exec -it agent-zero claude-auth-browser
```

**Check authentication status:**
```bash
docker exec agent-zero claude -p "test"
```

**Clear authentication (start fresh):**
```bash
docker exec agent-zero rm -rf /root/.config/claude-code
```

## Important Notes

- **OAuth uses your Pro subscription** - no per-use API costs
- **API key method** - charges per API call
- **Choose one method** - OAuth or API key, not both
- **OAuth persists** - once authenticated, stays authenticated
- **Container restarts** - OAuth persists if config directory is mounted
