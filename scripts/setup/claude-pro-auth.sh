#!/bin/bash
# Claude Pro OAuth Authentication Helper
# This script helps you authenticate Claude Code with your Pro subscription

echo "=========================================="
echo "Claude Pro OAuth Authentication"
echo "=========================================="
echo ""
echo "This will authenticate Claude Code to use your Claude Pro subscription"
echo "instead of the API key (which charges per-use)."
echo ""
echo "Steps:"
echo "1. Starting Claude Code OAuth..."
echo "2. Copy the OAuth URL that appears"
echo "3. Open it in your browser (on your HOST machine)"
echo "4. Complete Cloudflare CAPTCHA if shown"
echo "5. Sign in with your Claude Pro account"
echo "6. Authorize Claude Code"
echo "7. Copy the authorization code"
echo "8. Paste it back into this terminal"
echo ""
echo "Press Enter to start..."
read

docker exec -it agent-zero claude-pro

echo ""
echo "=========================================="
echo "Authentication Complete!"
echo "=========================================="
echo ""
echo "Your Claude Pro subscription is now active."
echo "Authentication is saved and will persist across container restarts."
echo ""
echo "To use Claude Code with Pro subscription:"
echo "  docker exec -it agent-zero claude-pro"
echo ""
