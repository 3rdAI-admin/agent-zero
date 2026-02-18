# Complete Guide: Setting Up Claude Code OAuth Authentication

## Overview

Claude Code requires OAuth authentication to use your Claude Pro subscription. This guide covers all methods to set up authentication for both root user and the `claude` user (used by `claude-pro-yolo`).

## Current Configuration

✅ **Volume Mounts**: Configured in `docker-compose.yml`
- `./claude-config:/root/.config/claude-code` (root user)
- `./claude-config:/home/claude/.config/claude-code` (claude user)

✅ **Config Sharing**: The `claude-pro-yolo` wrapper shares OAuth config from root user

## Method 1: Authenticate via VNC (Easiest - Recommended)

This method uses the VNC desktop to complete OAuth in a browser.

### Step 1: Connect to VNC

**On macOS**:
```bash
open vnc://localhost:5901
# Password: vnc123
```

**On Linux**:
```bash
vncviewer localhost:5901
# Or use Remmina, TigerVNC, etc.
# Password: vnc123
```

**On Windows**:
- Use VNC Viewer, TightVNC, or RealVNC
- Connect to: `localhost:5901`
- Password: `vnc123`

### Step 2: Open Terminal in VNC

1. **Right-click** on the VNC desktop
2. Select **Terminal** (or **lxterminal**)
3. Terminal window opens

### Step 3: Authenticate Root User (Shared)

**Option A: Authenticate as root (recommended - shared with claude user)**
```bash
# In VNC terminal:
claude-pro
```

**Option B: Authenticate as claude user directly**
```bash
# In VNC terminal:
su - claude
claude-pro
```

### Step 4: Complete OAuth Flow

1. **Claude Code displays OAuth URL**:
   ```
   Browser didn't open? Use the url below to sign in (c to copy)
   https://claude.ai/oauth/authorize?code=true&client_id=...
   ```

2. **Open browser in VNC**:
   - Right-click desktop → Browser (Chromium)
   - Or run: `chromium --no-sandbox &`

3. **Paste OAuth URL** in browser

4. **Complete CAPTCHA** (if prompted)

5. **Sign in** with your Claude Pro account

6. **Authorize** Claude Code

7. **Copy authorization code** from the page

8. **Paste code** back into the terminal where Claude Code is waiting

9. **Press Enter**

### Step 5: Verify Authentication

```bash
# Test root user
claude-pro 'Say hello'

# Test claude user (via YOLO wrapper)
claude-pro-yolo 'Say hello'
```

## Method 2: Manual OAuth Flow (Terminal + Host Browser)

This method uses your host browser but requires copying URLs and codes.

### Step 1: Start Authentication

```bash
docker exec -it agent-zero bash
claude-pro
```

### Step 2: Get OAuth URL

Claude Code will display:
```
Browser didn't open? Use the url below to sign in (c to copy)
https://claude.ai/oauth/authorize?code=true&client_id=...
```

**Copy the entire URL** (it may be long and wrap across lines - get it all).

### Step 3: Open in Host Browser

1. **Open your regular browser** (Chrome, Firefox, Safari)
2. **Paste the OAuth URL**
3. **Complete CAPTCHA** if prompted
4. **Sign in** with your Claude Pro account
5. **Authorize** Claude Code

### Step 4: Get Authorization Code

After authorizing, you'll see:
- An authorization code on the page (usually 6-8 characters), OR
- The code in the redirect URL (look for `code=...`)

**Copy this authorization code.**

### Step 5: Paste Code in Container

1. **Return to container terminal** where Claude Code is waiting
2. **Paste the authorization code** at the prompt
3. **Press Enter**

### Step 6: Verify

```bash
claude-pro 'Say hello'
# Should work without "Invalid API key" error
```

## Method 3: Authenticate Both Users Separately

If you want to authenticate root and claude users separately:

### Authenticate Root User

```bash
docker exec -it agent-zero bash
claude-pro
# Complete OAuth flow
```

### Authenticate Claude User

```bash
docker exec -it agent-zero bash
su - claude
claude-pro
# Complete OAuth flow
```

## Method 4: Use Existing OAuth Config (If Available)

If you already have OAuth config on your host:

### Step 1: Check Host Directory

```bash
ls -la ./claude-config/
# Should contain OAuth tokens/config files
```

### Step 2: Verify Volume Mount

The `docker-compose.yml` mounts:
- `./claude-config:/root/.config/claude-code`
- `./claude-config:/home/claude/.config/claude-code`

### Step 3: Restart Container (if needed)

```bash
docker restart agent-zero
```

### Step 4: Test

```bash
docker exec agent-zero claude-pro-yolo 'Say hello'
```

## Verification Steps

### Check Authentication Status

```bash
# Check root user config
docker exec agent-zero ls -la /root/.config/claude-code/

# Check claude user config
docker exec agent-zero ls -la /home/claude/.config/claude-code/

# If directories have files (not empty), authentication is likely set up
```

### Test Authentication

```bash
# Test root user
docker exec agent-zero claude-pro 'Say hello'

# Test claude user (YOLO mode)
docker exec agent-zero claude-pro-yolo 'Say hello'

# Should work without "Invalid API key" error
```

## Troubleshooting

### Issue: "Invalid API key · Please run /login"

**Solution**: OAuth authentication needed
1. Follow Method 1 (VNC) or Method 2 (Terminal + Browser)
2. Complete OAuth flow
3. Verify config files exist

### Issue: OAuth URL Truncated

**Solution**: 
- The URL may wrap across multiple lines
- Copy the entire URL including all parameters
- Look for the full URL starting with `https://claude.ai/oauth/authorize`

### Issue: Authorization Code Not Working

**Solution**:
1. Make sure you copied the entire code
2. Check you're signed into the correct Claude Pro account
3. Generate a new OAuth URL (codes expire after a few minutes)
4. Try authenticating again

### Issue: Config Not Shared Between Users

**Solution**:
1. Check symlink exists:
   ```bash
   docker exec agent-zero ls -la /home/claude/.config/claude-code
   ```
2. If not a symlink, create it:
   ```bash
   docker exec agent-zero bash -c "rm -rf /home/claude/.config/claude-code && ln -sf /root/.config/claude-code /home/claude/.config/claude-code"
   ```
3. Or ensure volume mount is active (restart container)

### Issue: VNC Not Accessible

**Solution**:
1. Check VNC is running:
   ```bash
   docker exec agent-zero ps aux | grep x11vnc
   ```
2. Check port mapping:
   ```bash
   docker port agent-zero | grep 5901
   ```
3. Restart VNC if needed:
   ```bash
   docker exec agent-zero supervisorctl restart vnc
   ```

## Quick Setup Script

Create a helper script to automate the process:

```bash
#!/bin/bash
# setup_claude_oauth.sh

echo "Setting up Claude Code OAuth authentication..."
echo ""
echo "Method 1: VNC (Recommended)"
echo "1. Connect to VNC: vnc://localhost:5901 (password: vnc123)"
echo "2. Open terminal"
echo "3. Run: claude-pro"
echo "4. Complete OAuth in browser"
echo ""
echo "Method 2: Terminal + Host Browser"
echo "1. Run: docker exec -it agent-zero claude-pro"
echo "2. Copy OAuth URL"
echo "3. Open in host browser"
echo "4. Complete OAuth"
echo "5. Paste code back"
echo ""
echo "After authentication, test with:"
echo "  docker exec agent-zero claude-pro-yolo 'Say hello'"
```

## Persistence

Once authenticated, OAuth tokens are stored in:
- `/root/.config/claude-code/` (root user)
- `/home/claude/.config/claude-code/` (claude user, shared via volume mount)

**These persist**:
- ✅ Across container restarts (volume-mounted)
- ✅ Across container rebuilds (if volume persists)
- ✅ Shared between root and claude users (via volume mount)

## Summary

### Recommended Method: VNC

1. Connect: `vnc://localhost:5901` (password: `vnc123`)
2. Open terminal
3. Run: `claude-pro`
4. Complete OAuth in browser
5. Done! ✅

### Quick Test

```bash
docker exec agent-zero claude-pro-yolo 'Say hello'
```

If this works without "Invalid API key" error, authentication is complete!

## Next Steps

After authentication:
- ✅ Use `claude-pro-yolo` for autonomous operation
- ✅ Agent Zero can invoke Claude Code automatically
- ✅ Claude Code can use Agent Zero via MCP
- ✅ Full bidirectional integration ready
