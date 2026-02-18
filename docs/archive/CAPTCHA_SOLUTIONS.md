# Solutions for Cloudflare CAPTCHA Issues

## Problem

Cloudflare CAPTCHA is blocking OAuth authentication. CAPTCHAs are designed to prevent automated access and can be difficult to complete.

## Solutions

### Solution 1: Use VNC to View Browser in Container (Recommended)

This lets you see and interact with a browser running in the container, making CAPTCHA completion easier.

#### Step 1: Start VNC Server

```bash
docker exec -d agent-zero start-vnc-browser
```

Or manually:
```bash
docker exec -d agent-zero bash -c "
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
fluxbox &
x11vnc -display :99 -nopw -listen 0.0.0.0 -xkb -forever -shared -rfbport 5900 &
"
```

#### Step 2: Connect VNC Viewer

**On macOS:**
- Use built-in Screen Sharing: `open vnc://localhost:5900`
- Or install a VNC client like "VNC Viewer" or "RealVNC"

**On Linux:**
```bash
vncviewer localhost:5900
# Or use Remmina, TigerVNC, etc.
```

**On Windows:**
- Use VNC Viewer, TightVNC, or RealVNC
- Connect to: `localhost:5900`

#### Step 3: Start Browser in VNC Session

Once connected to VNC:
```bash
# In a new terminal, access container
docker exec -it agent-zero bash

# Start browser
export DISPLAY=:99
chromium --no-sandbox &
```

#### Step 4: Complete OAuth in Browser

1. In the VNC browser window, navigate to the OAuth URL
2. Complete the CAPTCHA visually
3. Sign in and authorize
4. Copy the authorization code
5. Paste it back into the Claude Code terminal

### Solution 2: Use Host Browser with Better Instructions

Sometimes CAPTCHAs work better in your regular browser.

#### Step 1: Get OAuth URL

```bash
docker exec -it agent-zero claude-pro
# Copy the complete OAuth URL
```

#### Step 2: Open in Host Browser

1. **Open your regular browser** (Chrome, Firefox, Safari)
2. **Clear browser cache/cookies** for claude.ai (optional but can help)
3. **Paste the OAuth URL**
4. **Complete CAPTCHA** - take your time, be accurate
5. **Sign in** with your Claude Pro account
6. **Authorize** Claude Code

#### Step 3: Get Authorization Code

After authorizing, you'll see an authorization code. Copy it.

#### Step 4: Paste Code Back

Return to the container terminal and paste the code.

### Solution 3: Use Different Browser/Device

Sometimes CAPTCHAs are easier on different devices:

1. **Try mobile browser** - CAPTCHAs sometimes easier on mobile
2. **Try different browser** - Chrome vs Firefox vs Safari
3. **Try incognito/private mode** - Fresh session can help
4. **Try different network** - Sometimes network affects CAPTCHA difficulty

### Solution 4: Wait and Retry

CAPTCHAs can be rate-limited:

1. **Wait 10-15 minutes** between attempts
2. **Get a fresh OAuth URL** (they expire anyway)
3. **Try again** - CAPTCHA difficulty may decrease

### Solution 5: Contact Anthropic Support

If CAPTCHA keeps blocking you:

1. **Contact Anthropic support** - They may be able to help
2. **Explain the situation** - Headless container authentication
3. **Ask for alternative** - API key or different auth method

## Quick Start: VNC Method

**All-in-one command:**

```bash
# Start VNC server
docker exec -d agent-zero start-vnc-browser

# Connect VNC (macOS)
open vnc://localhost:5900

# In another terminal, start browser in container
docker exec -it agent-zero bash -c "export DISPLAY=:99 && chromium --no-sandbox &"

# Get OAuth URL
docker exec -it agent-zero claude-pro
```

## Troubleshooting

### VNC Connection Fails

**Check port is exposed:**
```bash
docker port agent-zero | grep 5900
```

**Check VNC is running:**
```bash
docker exec agent-zero ps aux | grep x11vnc
```

**Restart VNC:**
```bash
docker exec agent-zero pkill x11vnc
docker exec -d agent-zero start-vnc-browser
```

### Browser Won't Start in Container

**Try with different flags:**
```bash
chromium --no-sandbox --disable-dev-shm-usage --disable-gpu &
```

**Or use Firefox:**
```bash
firefox --no-sandbox &
```

### CAPTCHA Still Too Difficult

- **Try at different times** - CAPTCHA difficulty varies
- **Use VNC method** - Visual interaction helps
- **Try mobile device** - Sometimes easier
- **Contact support** - May need account verification

## Alternative: Use API Key Temporarily

If CAPTCHA continues to block, you can use API key authentication temporarily:

```bash
# Use API key (pay-per-use)
docker exec -it agent-zero claude -p "your prompt"
```

Then try OAuth again later when CAPTCHA might be easier.

## Port Configuration

VNC port (5900) is now exposed in docker-compose.yml. After making changes:

```bash
docker compose down
docker compose up -d
```

## Summary

**Best approach for CAPTCHA:**
1. Use VNC to view browser in container (most reliable)
2. Or use host browser with fresh session
3. Be patient and accurate with CAPTCHA
4. Try different times if it keeps failing

The VNC method gives you full visual control, making CAPTCHA completion much easier!
