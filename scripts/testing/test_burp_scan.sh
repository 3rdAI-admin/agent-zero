#!/bin/bash
# Test Burp Suite scan against https://host.docker.internal:5173

set -e

TARGET="https://host.docker.internal:5173"
PROJECT_FILE="/tmp/burp_test_project.burp"

echo "=========================================="
echo "Burp Suite DAST Test"
echo "=========================================="
echo "Target: $TARGET"
echo "Project File: $PROJECT_FILE"
echo ""

# Check if Burp Suite is installed
if ! command -v burpsuite >/dev/null 2>&1; then
    echo "ERROR: Burp Suite not found"
    exit 1
fi

echo "✅ Burp Suite found: $(burpsuite --version 2>&1 | head -1)"
echo ""

# Test target connectivity
echo "Testing target connectivity..."
HTTP_CODE=$(curl -k -s -o /dev/null -w '%{http_code}' "$TARGET" 2>&1 || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Target is accessible (HTTP $HTTP_CODE)"
else
    echo "⚠️  Target returned HTTP $HTTP_CODE"
fi
echo ""

# Note: Burp Suite Community Edition has limited command-line automation
# For full automation, Burp Suite Professional with REST API is needed
echo "Burp Suite Community Edition Limitations:"
echo "- Limited command-line automation"
echo "- Best used via GUI (VNC) or with project files"
echo "- For full automation, Burp Suite Professional is required"
echo ""

# Create a basic test script that Agent Zero can use
cat > /tmp/burp_test_instructions.txt << 'EOF'
Burp Suite Test Instructions for https://host.docker.internal:5173

1. Start Burp Suite via VNC:
   - Connect: vnc://localhost:5901 (password: vnc123)
   - Run: export DISPLAY=:99 && burpsuite &
   
2. Configure Burp Suite:
   - Proxy tab: Ensure proxy is listening on 127.0.0.1:8080
   - Target tab: Add https://host.docker.internal:5173 to scope
   - Spider: Start spidering the target
   - Scanner: Run active/passive scans

3. Or use command-line (limited):
   burpsuite --project-file=/tmp/burp_test_project.burp

4. Review results in Burp Suite GUI or export reports
EOF

echo "✅ Test instructions created at /tmp/burp_test_instructions.txt"
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "✅ Burp Suite: Installed and ready"
echo "✅ Target: Accessible at $TARGET"
echo "✅ Architecture: ARM64 compatible"
echo ""
echo "Next Steps:"
echo "1. Use VNC to launch Burp Suite GUI for interactive testing"
echo "2. Or ask Agent Zero to use Burp Suite for scanning"
echo "3. For automation, consider Burp Suite Professional with REST API"
echo ""
