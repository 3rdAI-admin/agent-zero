#!/bin/bash
# Agent Zero Comprehensive Validation
# Runs validation phases sequentially

set +e  # Don't exit on errors, collect all results

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0

echo "=========================================="
echo "Agent Zero Validation"
echo "=========================================="
echo ""

# Phase 1: Container Health
echo -e "${BLUE}[Phase 1] Container Health${NC}"
if docker ps --filter name=agent-zero --format "{{.Names}}" 2>/dev/null | grep -q "^agent-zero$"; then
    echo -e "${GREEN}✅ Container is running${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Container is not running${NC}"
    echo "   Run: docker compose up -d"
    ((FAILED++))
    echo ""
    echo "STOPPING - Container must be running"
    exit 1
fi
echo ""

# Phase 2: Web UI
echo -e "${BLUE}[Phase 2] Web UI${NC}"
if docker exec agent-zero curl -s -f -m 5 http://localhost:80 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Web UI accessible (http://localhost:8888)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Web UI not accessible${NC}"
    ((FAILED++))
fi
echo ""

# Phase 3: Supervisor Services
echo -e "${BLUE}[Phase 3] Supervisor Services${NC}"
SERVICES=("run_ui" "xvfb" "fluxbox" "x11vnc")
RUNNING=0
for service in "${SERVICES[@]}"; do
    STATUS=$(docker exec agent-zero supervisorctl status "$service" 2>/dev/null | head -1 || echo "")
    if echo "$STATUS" | grep -q "RUNNING"; then
        echo -e "  ${GREEN}✅ $service: RUNNING${NC}"
        ((RUNNING++))
    else
        echo -e "  ${RED}❌ $service: ${STATUS:-NOT FOUND}${NC}"
    fi
done
if [ $RUNNING -eq ${#SERVICES[@]} ]; then
    ((PASSED++))
else
    ((FAILED++))
fi
echo ""

# Phase 4: VNC Server
echo -e "${BLUE}[Phase 4] VNC Server${NC}"
if docker exec agent-zero supervisorctl status x11vnc 2>/dev/null | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ VNC server running (vnc://localhost:5901)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ VNC server not running${NC}"
    ((FAILED++))
fi
echo ""

# Phase 5: Claude Code
echo -e "${BLUE}[Phase 5] Claude Code${NC}"
if docker exec agent-zero which claude-pro >/dev/null 2>&1; then
    VERSION=$(docker exec agent-zero claude-pro --version 2>&1 | head -1 || echo "installed")
    echo -e "${GREEN}✅ Claude Code: $VERSION${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Claude Code not found${NC}"
    ((FAILED++))
fi

if docker exec agent-zero which claude-pro-yolo >/dev/null 2>&1; then
    echo -e "${GREEN}✅ claude-pro-yolo wrapper available${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ claude-pro-yolo not found${NC}"
    ((FAILED++))
fi
echo ""

# Phase 6: Volume Mounts
echo -e "${BLUE}[Phase 6] Volume Mounts${NC}"
VOLUMES=("memory" "knowledge" "logs" "tmp" "claude-config")
MOUNTED=0
for vol in "${VOLUMES[@]}"; do
    if [ -d "./$vol" ]; then
        echo -e "  ${GREEN}✅ $vol${NC}"
        ((MOUNTED++))
    else
        echo -e "  ${YELLOW}⚠️  $vol (will be created)${NC}"
    fi
done
if [ $MOUNTED -ge 3 ]; then
    ((PASSED++))
else
    ((SKIPPED++))
fi
echo ""

# Phase 7: MCP Configuration
echo -e "${BLUE}[Phase 7] MCP Server${NC}"
TOKEN=$(docker exec agent-zero cat /a0/tmp/settings.json 2>/dev/null | python3 -c 'import sys, json; print(json.load(sys.stdin).get("mcp_server_token", ""))' 2>/dev/null || echo "")
if [ -n "$TOKEN" ] && [ "$TOKEN" != "" ]; then
    echo -e "${GREEN}✅ MCP token configured${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  MCP token not configured${NC}"
    ((SKIPPED++))
fi
echo ""

# Phase 8: Security Tools
echo -e "${BLUE}[Phase 8] Security Tools${NC}"
TOOLS=("nmap" "nikto")
FOUND=0
for tool in "${TOOLS[@]}"; do
    if docker exec agent-zero which "$tool" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ $tool${NC}"
        ((FOUND++))
    else
        echo -e "  ${YELLOW}⚠️  $tool (optional)${NC}"
    fi
done
if [ $FOUND -gt 0 ]; then
    ((PASSED++))
else
    ((SKIPPED++))
fi
echo ""

# Phase 9: Resource Limits
echo -e "${BLUE}[Phase 9] Resource Limits${NC}"
MEMORY=$(docker inspect agent-zero --format='{{.HostConfig.Memory}}' 2>/dev/null || echo "0")
if [ "$MEMORY" != "0" ] && [ -n "$MEMORY" ]; then
    MEM_GB=$((MEMORY / 1024 / 1024 / 1024))
    echo -e "${GREEN}✅ Memory limit: ${MEM_GB}GB${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Memory limit not set${NC}"
    ((SKIPPED++))
fi
echo ""

# Summary Table
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
printf "| %-20s | %-10s |\n" "Phase" "Status"
echo "|----------------------|-----------|"
printf "| %-20s | %-10s |\n" "1. Container" "$([ $PASSED -gt 0 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "2. Web UI" "$([ $PASSED -gt 1 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "3. Supervisor" "$([ $PASSED -gt 2 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "4. VNC" "$([ $PASSED -gt 3 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "5. Claude Code" "$([ $PASSED -gt 4 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "6. Volumes" "$([ $PASSED -gt 5 ] && echo "✅ PASS" || echo "⚠️  SKIP")"
printf "| %-20s | %-10s |\n" "7. MCP" "$([ $PASSED -gt 6 ] && echo "✅ PASS" || echo "⚠️  SKIP")"
printf "| %-20s | %-10s |\n" "8. Security Tools" "$([ $PASSED -gt 7 ] && echo "✅ PASS" || echo "⚠️  SKIP")"
printf "| %-20s | %-10s |\n" "9. Resources" "$([ $PASSED -gt 8 ] && echo "✅ PASS" || echo "⚠️  SKIP")"
echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Overall: PASSED${NC}"
    exit 0
else
    echo -e "${RED}❌ Overall: FAILED - $FAILED critical issues${NC}"
    exit 1
fi
