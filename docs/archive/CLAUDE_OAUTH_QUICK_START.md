# Quick Start: Claude Code OAuth Setup

## Fastest Method: VNC

### Step 1: Connect to VNC
```bash
# macOS
open vnc://localhost:5901

# Linux
vncviewer localhost:5901

# Windows: Use VNC Viewer, connect to localhost:5901
```
**Password**: `vnc123`

### Step 2: Authenticate
1. **Right-click** desktop → **Terminal**
2. Run: `claude-pro`
3. **Copy OAuth URL** shown
4. **Open browser** in VNC (right-click → Browser)
5. **Paste URL**, complete CAPTCHA, sign in
6. **Copy authorization code**
7. **Paste code** back in terminal
8. **Press Enter**

### Step 3: Test
```bash
docker exec agent-zero claude-pro-yolo 'Say hello'
```

## Alternative: Terminal + Host Browser

### Step 1: Start Authentication
```bash
docker exec -it agent-zero claude-pro
```

### Step 2: Complete OAuth
1. **Copy OAuth URL** from terminal
2. **Open in host browser**
3. **Complete CAPTCHA** and sign in
4. **Copy authorization code**
5. **Paste in container terminal**
6. **Press Enter**

### Step 3: Test
```bash
docker exec agent-zero claude-pro-yolo 'Say hello'
```

## Quick Check

```bash
# Check if authenticated
docker exec agent-zero ls -la /root/.config/claude-code/

# If directory has files, you're authenticated!
```

## Helper Script

```bash
./setup_claude_oauth.sh
```

## Full Documentation

See `SETUP_CLAUDE_OAUTH.md` for complete guide.
