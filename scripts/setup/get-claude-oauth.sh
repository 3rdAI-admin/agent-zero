#!/bin/bash
# Interactive script to get Claude Code OAuth URL
# Run this script and it will guide you through the process

echo "=========================================="
echo "Claude Code OAuth URL Extractor"
echo "=========================================="
echo ""
echo "This script will help you get the complete OAuth URL."
echo ""
echo "STEP 1: Starting Claude Code in the container..."
echo ""

# Start claude-pro in the container and capture output
docker exec -it agent-zero bash -c "
export PATH=\"\$HOME/.local/bin:\$PATH\"
unset ANTHROPIC_API_KEY
unset API_KEY_ANTHROPIC
claude-pro
" 2>&1 | tee claude-output.txt

echo ""
echo "=========================================="
echo "Extracting OAuth URL from output..."
echo "=========================================="
echo ""

# Extract the OAuth URL
OAUTH_URL=$(grep -o 'https://claude.ai/oauth/authorize[^[:space:]]*' claude-output.txt | head -1)

if [ -n "$OAUTH_URL" ]; then
    echo "✅ OAuth URL found!"
    echo ""
    echo "=========================================="
    echo "COMPLETE OAUTH URL:"
    echo "=========================================="
    echo ""
    echo "$OAUTH_URL"
    echo ""
    echo "=========================================="
    echo ""
    echo "URL Length: $(echo -n "$OAUTH_URL" | wc -c) characters"
    echo ""
    
    # Verify redirect_uri is present
    if echo "$OAUTH_URL" | grep -q "redirect_uri="; then
        echo "✅ redirect_uri parameter is present"
        echo "✅ URL appears to be complete"
    else
        echo "❌ WARNING: redirect_uri parameter is MISSING!"
        echo "   The URL may have been truncated."
        echo "   Check claude-output.txt for the full output"
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
    echo "3. Complete CAPTCHA and sign in with your Claude Pro account"
    echo "4. Authorize Claude Code"
    echo "5. Copy the authorization code"
    echo "6. Return to the container terminal and paste the code"
else
    echo "❌ Could not automatically extract OAuth URL"
    echo ""
    echo "Please check claude-output.txt for the OAuth URL"
    echo "Look for a line starting with: https://claude.ai/oauth/authorize"
    echo ""
    echo "The URL should be very long (500+ characters)"
    echo "Make sure you copy the ENTIRE URL including all parameters"
fi
