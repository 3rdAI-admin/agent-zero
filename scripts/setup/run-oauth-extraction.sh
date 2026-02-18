#!/bin/bash
# Run OAuth URL extraction from host machine
# This will extract the OAuth URL from the container and save it locally

echo "=========================================="
echo "Extracting Claude Code OAuth URL"
echo "=========================================="
echo ""

# Run the extraction script in the container
docker exec agent-zero claude-extract-url

echo ""
echo "Copying URL from container to host..."
docker cp agent-zero:/tmp/oauth-url.txt ./oauth-url-complete.txt 2>/dev/null

if [ -f ./oauth-url-complete.txt ]; then
    echo ""
    echo "=========================================="
    echo "COMPLETE OAUTH URL:"
    echo "=========================================="
    echo ""
    cat ./oauth-url-complete.txt
    echo ""
    echo "=========================================="
    echo ""
    echo "✅ URL saved to: oauth-url-complete.txt"
    echo ""
    echo "Next steps:"
    echo "1. Copy the URL above (or from oauth-url-complete.txt)"
    echo "2. Open it in your browser"
    echo "3. Complete CAPTCHA and sign in"
    echo "4. Authorize Claude Code"
    echo "5. Copy the authorization code"
    echo "6. Run: docker exec -it agent-zero claude-pro"
    echo "7. Paste the code when prompted"
else
    echo ""
    echo "❌ Could not extract URL automatically"
    echo ""
    echo "Please access the container directly:"
    echo "  docker exec -it agent-zero bash"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "  unset ANTHROPIC_API_KEY"
    echo "  claude-pro"
    echo ""
    echo "Then copy the OAuth URL manually"
fi
