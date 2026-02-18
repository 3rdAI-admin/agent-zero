# Browser Installation in Agent Zero Container

## Installed Browsers

✅ **Chromium v144.0.7559.59** - Installed and ready
✅ **Firefox ESR v140.7.0** - Installed and ready  
✅ **Xvfb (Virtual Display)** - Installed for headless operation
✅ **X11VNC** - Installed for remote desktop access
✅ **Fluxbox** - Lightweight window manager

## Using Browsers in Headless Container

### Option 1: Headless Mode (Recommended)

**Chromium Headless:**
```bash
chromium --headless --disable-gpu --no-sandbox --remote-debugging-port=9222 https://example.com
```

**Firefox Headless:**
```bash
firefox --headless https://example.com
```

### Option 2: Virtual Display (Xvfb)

For applications that need a display:

```bash
# Start virtual display
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Run browser
chromium https://example.com &
```

### Option 3: VNC Access (View Browser GUI)

```bash
# Start virtual display and VNC server
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
x11vnc -display :99 -nopw -listen localhost -xkb -forever -shared &

# Connect from host machine using VNC viewer to localhost:5900
```

## Claude Code Authentication - Better Solution

**Good News:** Claude Code is already authenticated using your API key! No browser needed for OAuth.

The wrapper script at `/usr/local/bin/claude` automatically sets the API key, so Claude Code uses API authentication instead of OAuth.

**Verify it's working:**
```bash
docker exec -it agent-zero claude -p "Hello"
```

If you see OAuth prompts, the API key might not be loading. Check:
```bash
docker exec -it agent-zero env | grep ANTHROPIC
```

## Browser Tools for Web Testing

The installed browsers can be used for:

**Web Application Testing:**
```bash
# Screenshot a webpage
chromium --headless --disable-gpu --screenshot https://target.com

# Test JavaScript execution
chromium --headless --disable-gpu --dump-dom https://target.com

# Browser automation with Selenium/Playwright
# (Playwright is already installed in Agent Zero)
```

**Security Testing:**
```bash
# Test web application with browser
chromium --headless --disable-gpu https://target.com

# Capture network traffic
chromium --headless --disable-gpu --remote-debugging-port=9222 https://target.com
```

## Troubleshooting

**If browser won't start:**
```bash
# Check if display is set
echo $DISPLAY

# Start virtual display if needed
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```

**If you need GUI access:**
```bash
# Install VNC server (already installed)
x11vnc -display :99 -nopw -listen 0.0.0.0 -xkb -forever -shared

# Connect from host using VNC viewer
# Address: localhost:5900 (or container IP:5900)
```

## Claude Code - No Browser Needed!

**Important:** Claude Code authentication is handled via API key, not OAuth browser flow. The browsers are installed for other web testing purposes, not for Claude Code authentication.

**Current Status:**
- ✅ Claude Code authenticated via API key
- ✅ No OAuth needed
- ✅ Works without browser
- ✅ Browsers available for web application testing
