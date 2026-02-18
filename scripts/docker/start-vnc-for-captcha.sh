#!/bin/bash
# Start VNC server for CAPTCHA completion
# This allows you to view and interact with a browser in the container

echo "=========================================="
echo "Starting VNC Server for CAPTCHA"
echo "=========================================="
echo ""

# Start VNC server in container
docker exec -d agent-zero start-vnc-browser

sleep 2

echo "✅ VNC server started"
echo ""
echo "=========================================="
echo "Connect to VNC:"
echo "=========================================="
echo ""
echo "On macOS:"
echo "  open vnc://localhost:5901"
echo ""
echo "Or use VNC Viewer:"
echo "  Address: localhost:5901"
echo "  (No password needed)"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Connect to VNC (see above)"
echo ""
echo "2. Start browser in container:"
echo "   docker exec -it agent-zero bash -c 'export DISPLAY=:99 && chromium --no-sandbox &'"
echo ""
echo "3. Get OAuth URL:"
echo "   docker exec -it agent-zero claude-pro"
echo ""
echo "4. In VNC browser window:"
echo "   - Paste OAuth URL"
echo "   - Complete CAPTCHA visually"
echo "   - Sign in and authorize"
echo "   - Copy authorization code"
echo ""
echo "5. Paste code back into terminal"
echo ""
echo "VNC is running. Press Ctrl+C to stop this script (VNC keeps running)."
echo ""

# Keep script running
wait
