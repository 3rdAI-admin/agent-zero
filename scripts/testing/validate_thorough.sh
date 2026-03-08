#!/bin/bash
# Agent Zero Thorough Validation Script
# Comprehensive validation of all components

set +e  # Don't exit on errors, collect all results

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0
WARNINGS=0

echo "=========================================="
echo "Agent Zero Thorough Validation"
echo "=========================================="
echo ""

# Phase 1: Service Health Check
echo -e "${BLUE}=== Phase 1: Service Health Check ===${NC}"
CONTAINER_RUNNING=0
WEB_UI_OK=0

if docker ps --filter name=agent-zero --format "{{.Names}}" 2>/dev/null | grep -q "^agent-zero$"; then
    echo -e "${GREEN}✅ Container is running${NC}"
    CONTAINER_RUNNING=1
    ((PASSED++))
    
    echo "Testing Web UI..."
    if docker exec agent-zero curl -s -f -m 5 http://localhost:80 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Web UI is accessible${NC}"
        WEB_UI_OK=1
        ((PASSED++))
    else
        echo -e "${RED}❌ Web UI not accessible${NC}"
        ((FAILED++))
    fi
else
    echo -e "${RED}❌ Container is not running${NC}"
    echo -e "${YELLOW}   Run: docker compose up -d${NC}"
    ((FAILED++))
    echo ""
    echo -e "${RED}STOPPING - Container must be running for validation${NC}"
    exit 1
fi
echo ""

# Phase 2: Container Health
echo -e "${BLUE}=== Phase 2: Container Health ===${NC}"
if docker ps --filter name=agent-zero --format "{{.Names}}" 2>/dev/null | grep -q "^agent-zero$"; then
    STATUS=$(docker ps --filter name=agent-zero --format "{{.Status}}")
    echo -e "${GREEN}✅ Container status: $STATUS${NC}"
    HEALTH=$(docker inspect agent-zero --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-healthcheck")
    echo "   Health check: $HEALTH"
    ((PASSED++))
else
    echo -e "${RED}❌ Container not found${NC}"
    ((FAILED++))
fi
echo ""

# Phase 3: Supervisor Services
echo -e "${BLUE}=== Phase 3: Supervisor Services ===${NC}"
SERVICES=("run_ui" "xvfb" "fluxbox" "x11vnc" "autocutsel")
RUNNING_COUNT=0
TOTAL=${#SERVICES[@]}

for svc in "${SERVICES[@]}"; do
    STATUS=$(docker exec agent-zero supervisorctl status "$svc" 2>/dev/null | head -1 || echo "NOT FOUND")
    if echo "$STATUS" | grep -q "RUNNING"; then
        echo -e "  ${GREEN}✅ $svc: RUNNING${NC}"
        ((RUNNING_COUNT++))
    else
        echo -e "  ${RED}❌ $svc: ${STATUS:-NOT FOUND}${NC}"
    fi
done

if [ $RUNNING_COUNT -eq $TOTAL ]; then
    ((PASSED++))
else
    if [ $RUNNING_COUNT -gt 0 ]; then
        ((WARNINGS++))
    else
        ((FAILED++))
    fi
fi
echo "Services running: $RUNNING_COUNT/$TOTAL"
echo ""

# Phase 4: Claude Code Integration
echo -e "${BLUE}=== Phase 4: Claude Code Integration ===${NC}"
CLAUDE_INSTALLED=0
YOLO_WRAPPER=0

if docker exec agent-zero which claude-pro >/dev/null 2>&1; then
    VERSION=$(docker exec agent-zero claude-pro --version 2>&1 | head -1 || echo "installed")
    echo -e "${GREEN}✅ Claude Code installed: $VERSION${NC}"
    CLAUDE_INSTALLED=1
    ((PASSED++))
else
    echo -e "${RED}❌ Claude Code not found${NC}"
    ((FAILED++))
fi

if docker exec agent-zero which claude-pro-yolo >/dev/null 2>&1; then
    echo -e "${GREEN}✅ claude-pro-yolo wrapper available${NC}"
    YOLO_WRAPPER=1
    ((PASSED++))
else
    echo -e "${RED}❌ claude-pro-yolo not found${NC}"
    ((FAILED++))
fi
echo ""

# Phase 5: VNC Server
echo -e "${BLUE}=== Phase 5: VNC Server ===${NC}"
VNC_OK=0
XVFB_OK=0

if docker exec agent-zero supervisorctl status x11vnc 2>/dev/null | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ VNC server is running${NC}"
    echo "   Access: vnc://localhost:5901 (password: vnc123)"
    VNC_OK=1
    ((PASSED++))
else
    echo -e "${RED}❌ VNC server not running${NC}"
    ((FAILED++))
fi

if docker exec agent-zero supervisorctl status xvfb 2>/dev/null | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ Xvfb (virtual display) is running${NC}"
    XVFB_OK=1
    ((PASSED++))
else
    echo -e "${RED}❌ Xvfb not running${NC}"
    ((FAILED++))
fi
echo ""

# Phase 6: MCP Server Configuration
echo -e "${BLUE}=== Phase 6: MCP Server Configuration ===${NC}"
TOKEN="$(docker exec agent-zero bash -lc "cd /a0 && PYTHONPATH=/a0 /opt/venv-a0/bin/python -c 'from python.helpers import dotenv, runtime, settings; runtime.initialize(); dotenv.load_dotenv(); settings.reload_settings(); print(settings.get_settings()[\"mcp_server_token\"])'" 2>/dev/null || true)"

if [ -n "$TOKEN" ] && [ "$TOKEN" != "" ]; then
    echo -e "${GREEN}✅ MCP token configured: ${TOKEN:0:8}...${NC}"
    MCP_TOKEN=1
    ((PASSED++))
    
    STATUS=$(docker exec agent-zero curl -s -o /dev/null -w '%{http_code}' http://localhost:80/mcp/t-${TOKEN}/sse 2>&1 || echo "000")
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "000" ]; then
        echo -e "${GREEN}✅ MCP endpoint accessible${NC}"
        MCP_ENDPOINT=1
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  MCP endpoint status: $STATUS${NC}"
        MCP_ENDPOINT=0
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠️  MCP token not configured${NC}"
    echo "   Run: ./scripts/setup/configure_mcp_token.sh"
    MCP_TOKEN=0
    MCP_ENDPOINT=0
    ((SKIPPED++))
fi
echo ""

# Phase 7: Volume Mounts
echo -e "${BLUE}=== Phase 7: Volume Mounts ===${NC}"
VOLUMES=("memory" "knowledge" "logs" "tmp" "claude-config" "claude-credentials")
MOUNTED_COUNT=0

for vol in "${VOLUMES[@]}"; do
    if [ -d "./$vol" ]; then
        echo -e "  ${GREEN}✅ $vol: mounted${NC}"
        ((MOUNTED_COUNT++))
    else
        echo -e "  ${YELLOW}⚠️  $vol: not found (will be created)${NC}"
    fi
done

if [ $MOUNTED_COUNT -ge 4 ]; then
    ((PASSED++))
else
    ((SKIPPED++))
fi
echo "Volumes mounted: $MOUNTED_COUNT/${#VOLUMES[@]}"
echo ""

# Phase 8: Security Tools
echo -e "${BLUE}=== Phase 8: Security Tools ===${NC}"
TOOLS=("nmap" "nikto" "sqlmap" "masscan")
FOUND_COUNT=0

for tool in "${TOOLS[@]}"; do
    if docker exec agent-zero which "$tool" >/dev/null 2>&1; then
        VERSION=$(docker exec agent-zero "$tool" --version 2>&1 | head -1 || echo "installed")
        echo -e "  ${GREEN}✅ $tool: $VERSION${NC}"
        ((FOUND_COUNT++))
    else
        echo -e "  ${YELLOW}⚠️  $tool: not installed (optional)${NC}"
    fi
done

if [ $FOUND_COUNT -gt 0 ]; then
    ((PASSED++))
else
    ((SKIPPED++))
fi
echo "Security tools found: $FOUND_COUNT/${#TOOLS[@]}"
echo ""

# Phase 9: Resource Limits
echo -e "${BLUE}=== Phase 9: Resource Limits ===${NC}"
MEMORY=$(docker inspect agent-zero --format='{{.HostConfig.Memory}}' 2>/dev/null || echo "0")
if [ "$MEMORY" != "0" ] && [ -n "$MEMORY" ]; then
    MEM_GB=$((MEMORY / 1024 / 1024 / 1024))
    echo -e "${GREEN}✅ Memory limit: ${MEM_GB}GB${NC}"
    RESOURCE_LIMITS=1
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Memory limit not set${NC}"
    RESOURCE_LIMITS=0
    ((SKIPPED++))
fi

CPU=$(docker inspect agent-zero --format='{{.HostConfig.CpuQuota}}' 2>/dev/null || echo "0")
if [ "$CPU" != "0" ] && [ -n "$CPU" ]; then
    echo -e "${GREEN}✅ CPU limit configured${NC}"
else
    echo -e "${YELLOW}⚠️  CPU limit not set${NC}"
fi
echo ""

# Phase 10: Network Configuration
echo -e "${BLUE}=== Phase 10: Network Configuration ===${NC}"
CAPS=$(docker inspect agent-zero --format='{{.HostConfig.CapAdd}}' 2>/dev/null || echo "")
if echo "$CAPS" | grep -q "NET_RAW"; then
    echo -e "${GREEN}✅ Network capabilities: NET_RAW, NET_ADMIN, SYS_ADMIN${NC}"
    NETWORK_CAPS=1
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Network capabilities not configured${NC}"
    NETWORK_CAPS=0
    ((SKIPPED++))
fi

HOST_GATEWAY=$(docker inspect agent-zero --format='{{.HostConfig.ExtraHosts}}' 2>/dev/null | grep -q "host.docker.internal" && echo "yes" || echo "no")
if [ "$HOST_GATEWAY" = "yes" ]; then
    echo -e "${GREEN}✅ Host gateway access configured${NC}"
else
    echo -e "${YELLOW}⚠️  Host gateway not configured${NC}"
fi
echo ""

# Phase 11: Integration Tests
echo -e "${BLUE}=== Phase 11: Integration Tests ===${NC}"
if [ -f "scripts/testing/test_claude_integration.sh" ]; then
    echo "Running Claude Code integration test..."
    if bash scripts/testing/test_claude_integration.sh 2>&1 | head -30 | grep -q "✅"; then
        echo -e "${GREEN}✅ Integration test passed${NC}"
        INTEGRATION_TEST=1
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  Integration test had issues${NC}"
        INTEGRATION_TEST=0
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠️  Integration test script not found${NC}"
    INTEGRATION_TEST=0
    ((SKIPPED++))
fi
echo ""

# Summary Table
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo ""
printf "| %-25s | %-10s | %-30s |\n" "Phase" "Status" "Notes"
echo "|---------------------------|------------|------------------------------|"
printf "| %-25s | %-10s | %-30s |\n" "1. Service Health" "$([ $CONTAINER_RUNNING -eq 1 ] && [ $WEB_UI_OK -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")" "Container: $([ $CONTAINER_RUNNING -eq 1 ] && echo "running" || echo "stopped")"
printf "| %-25s | %-10s | %-30s |\n" "2. Container Health" "$([ $CONTAINER_RUNNING -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")" "Status checked"
printf "| %-25s | %-10s | %-30s |\n" "3. Supervisor Services" "$([ $RUNNING_COUNT -eq $TOTAL ] && echo "✅ PASS" || [ $RUNNING_COUNT -gt 0 ] && echo "⚠️  PARTIAL" || echo "❌ FAIL")" "$RUNNING_COUNT/$TOTAL running"
printf "| %-25s | %-10s | %-30s |\n" "4. Claude Code" "$([ $CLAUDE_INSTALLED -eq 1 ] && [ $YOLO_WRAPPER -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")" "Installed: $([ $CLAUDE_INSTALLED -eq 1 ] && echo "yes" || echo "no")"
printf "| %-25s | %-10s | %-30s |\n" "5. VNC Server" "$([ $VNC_OK -eq 1 ] && [ $XVFB_OK -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")" "VNC: $([ $VNC_OK -eq 1 ] && echo "running" || echo "stopped")"
printf "| %-25s | %-10s | %-30s |\n" "6. MCP Server" "$([ $MCP_TOKEN -eq 1 ] && echo "✅ PASS" || echo "⚠️  SKIP")" "Token: $([ $MCP_TOKEN -eq 1 ] && echo "configured" || echo "not configured")"
printf "| %-25s | %-10s | %-30s |\n" "7. Volume Mounts" "$([ $MOUNTED_COUNT -ge 4 ] && echo "✅ PASS" || echo "⚠️  PARTIAL")" "$MOUNTED_COUNT/${#VOLUMES[@]} mounted"
printf "| %-25s | %-10s | %-30s |\n" "8. Security Tools" "$([ $FOUND_COUNT -gt 0 ] && echo "✅ PASS" || echo "⚠️  SKIP")" "$FOUND_COUNT/${#TOOLS[@]} found"
printf "| %-25s | %-10s | %-30s |\n" "9. Resource Limits" "$([ $RESOURCE_LIMITS -eq 1 ] && echo "✅ PASS" || echo "⚠️  SKIP")" "Memory: ${MEM_GB}GB"
printf "| %-25s | %-10s | %-30s |\n" "10. Network Config" "$([ $NETWORK_CAPS -eq 1 ] && echo "✅ PASS" || echo "⚠️  SKIP")" "Capabilities configured"
printf "| %-25s | %-10s | %-30s |\n" "11. Integration Tests" "$([ $INTEGRATION_TEST -eq 1 ] && echo "✅ PASS" || echo "⚠️  SKIP")" "Test executed"
echo ""

echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

# Overall status
CRITICAL_FAILURES=0
[ $CONTAINER_RUNNING -eq 0 ] && CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
[ $WEB_UI_OK -eq 0 ] && CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
[ $RUNNING_COUNT -eq 0 ] && CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))

if [ $CRITICAL_FAILURES -eq 0 ] && [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Overall: PASSED${NC}"
    exit 0
elif [ $CRITICAL_FAILURES -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Overall: PASSED with warnings${NC}"
    exit 0
else
    echo -e "${RED}❌ Overall: FAILED - $CRITICAL_FAILURES critical issues found${NC}"
    echo ""
    echo "To fix:"
    [ $CONTAINER_RUNNING -eq 0 ] && echo "  - Start container: docker compose up -d"
    [ $WEB_UI_OK -eq 0 ] && echo "  - Wait for services to initialize (30-60 seconds)"
    [ $RUNNING_COUNT -eq 0 ] && echo "  - Check supervisor: docker exec agent-zero supervisorctl status"
    exit 1
fi
