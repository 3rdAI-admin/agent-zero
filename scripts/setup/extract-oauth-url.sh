#!/bin/bash
# Extract OAuth URL from Claude Code container
# This script runs claude-pro and extracts the complete OAuth URL

echo "=========================================="
echo "Extracting Claude Code OAuth URL"
echo "=========================================="
echo ""
echo "Starting Claude Code to generate OAuth URL..."
echo "This may take 10-15 seconds..."
echo ""

# Run claude-pro and capture output
OUTPUT=$(docker exec agent-zero bash -c "
export PATH=\"\$HOME/.local/bin:\$PATH\"
unset ANTHROPIC_API_KEY
unset API_KEY_ANTHROPIC
timeout 15 claude-pro 2>&1
" 2>&1)

# Extract the OAuth URL (look for the long URL line)
OAUTH_URL=$(echo "$OUTPUT" | grep -o 'https://claude.ai/oauth/authorize[^[:space:]]*' | head -1)

if [ -n "$OAUTH_URL" ]; then
    echo "=========================================="
    echo "COMPLETE OAUTH URL FOUND:"
    echo "=========================================="
    echo ""
    echo "$OAUTH_URL"
    echo ""
    echo "=========================================="
    echo ""
    echo "URL Length: $(echo -n "$OAUTH_URL" | wc -c) characters"
    echo ""
    
    # Check if redirect_uri is present
    if echo "$OAUTH_URL" | grep -q "redirect_uri="; then
        echo "✅ redirect_uri parameter is present"
    else
        echo "❌ WARNING: redirect_uri parameter is MISSING!"
        echo "   The URL may have been truncated."
    fi
    
    echo ""
    echo "Saving to oauth-url-complete.txt..."
    echo "$OAUTH_URL" > oauth-url-complete.txt
    echo ""
    echo "✅ Complete URL saved to: oauth-url-complete.txt"
    echo ""
    echo "Next steps:"
    echo "1. Copy the URL above (or from oauth-url-complete.txt)"
    echo "2. Open it in your browser"
    echo "3. Complete CAPTCHA and sign in"
    echo "4. Authorize Claude Code"
    echo "5. Copy the authorization code"
    echo "6. Paste it back into the container terminal"
else
    echo "❌ Could not extract OAuth URL from output"
    echo ""
    echo "Full output:"
    echo "$OUTPUT" | tail -20
    echo ""
    echo "Try running manually:"
    echo "  docker exec -it agent-zero claude-pro"
fi
