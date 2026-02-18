#!/bin/bash
# Quick OAuth Setup Helper for Claude Code

set -e

echo "=========================================="
echo "Claude Code OAuth Authentication Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check current status
echo -e "${BLUE}Checking current authentication status...${NC}"
ROOT_CONFIG=$(docker exec agent-zero bash -c "ls -A /root/.config/claude-code 2>/dev/null" | wc -l)
CLAUDE_CONFIG=$(docker exec agent-zero bash -c "ls -A /home/claude/.config/claude-code 2>/dev/null" | wc -l)

if [ "$ROOT_CONFIG" -gt 0 ]; then
    echo -e "${GREEN}✅ Root user: Authenticated${NC}"
    AUTH_NEEDED=false
else
    echo -e "${YELLOW}⚠️  Root user: Not authenticated${NC}"
    AUTH_NEEDED=true
fi

if [ "$CLAUDE_CONFIG" -gt 0 ]; then
    echo -e "${GREEN}✅ Claude user: Authenticated${NC}"
else
    echo -e "${YELLOW}⚠️  Claude user: Not authenticated${NC}"
fi

echo ""

if [ "$AUTH_NEEDED" = true ]; then
    echo -e "${BLUE}Authentication Setup Options:${NC}"
    echo ""
    echo "Method 1: VNC (Recommended - Easiest)"
    echo "  1. Connect to VNC: vnc://localhost:5901 (password: vnc123)"
    echo "  2. Right-click desktop → Terminal"
    echo "  3. Run: claude-pro"
    echo "  4. Complete OAuth in browser"
    echo ""
    echo "Method 2: Terminal + Host Browser"
    echo "  1. Run: docker exec -it agent-zero claude-pro"
    echo "  2. Copy OAuth URL"
    echo "  3. Open in host browser"
    echo "  4. Complete OAuth and paste code back"
    echo ""
    echo "Would you like to start authentication now? (y/n)"
    read -r response
    
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        echo ""
        echo -e "${BLUE}Starting Claude Code authentication...${NC}"
        echo "Choose method:"
        echo "  1) VNC (recommended)"
        echo "  2) Terminal + Host Browser"
        read -r method
        
        if [ "$method" = "1" ]; then
            echo ""
            echo "Opening VNC connection..."
            echo "After connecting:"
            echo "  1. Right-click → Terminal"
            echo "  2. Run: claude-pro"
            echo "  3. Complete OAuth in browser"
            echo ""
            # Try to open VNC (platform-specific)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                open vnc://localhost:5901
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                echo "Please connect manually: vnc://localhost:5901"
            else
                echo "Please connect manually: vnc://localhost:5901"
            fi
        else
            echo ""
            echo "Starting Claude Code in container..."
            echo "Follow the prompts to complete OAuth"
            docker exec -it agent-zero claude-pro
        fi
    fi
else
    echo -e "${GREEN}✅ Authentication appears to be set up!${NC}"
    echo ""
    echo "Testing authentication..."
    docker exec agent-zero claude-pro-yolo 'Say hello' 2>&1 | head -5
    echo ""
    echo "If you see 'Invalid API key', authentication may need to be refreshed."
fi

echo ""
echo "=========================================="
echo "Setup Complete"
echo "=========================================="
echo ""
echo "Test authentication:"
echo "  docker exec agent-zero claude-pro-yolo 'Say hello'"
echo ""
echo "For detailed instructions, see: SETUP_CLAUDE_OAUTH.md"
echo ""
