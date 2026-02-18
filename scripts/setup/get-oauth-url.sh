#!/bin/bash
# Extract Claude Code OAuth URL to a file for easy copying

echo "Extracting OAuth URL from Claude Code..."
echo ""

# Run the URL extractor and save to file
docker exec agent-zero claude-oauth-url > oauth-url.txt 2>&1

echo ""
echo "OAuth URL saved to: oauth-url.txt"
echo ""
echo "To view the complete URL:"
echo "  cat oauth-url.txt"
echo ""
echo "Or open it in your editor:"
echo "  open oauth-url.txt  # macOS"
echo "  xdg-open oauth-url.txt  # Linux"
echo ""
echo "IMPORTANT: Copy the ENTIRE URL (it's very long - 500+ characters)"
echo "Make sure it includes the redirect_uri parameter!"
