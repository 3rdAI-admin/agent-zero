#!/bin/bash
# Focused reliability validation for runtime truth, readiness, and failure semantics.

set +e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
    HOST_PYTHON="$REPO_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    HOST_PYTHON="python3"
else
    HOST_PYTHON="python"
fi

echo "=========================================="
echo "Reliability Validation"
echo "=========================================="
echo ""

echo -e "${BLUE}[Phase 1] Reliability pytest suite (host)${NC}"
if "$HOST_PYTHON" -m pytest tests/test_reliability_*.py -v --tb=short; then
    echo -e "${GREEN}✅ Host reliability pytest suite passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Host reliability pytest suite failed${NC}"
    ((FAILED++))
fi
echo ""

echo -e "${BLUE}[Phase 2] Detailed reliability regressions (host)${NC}"
if "$HOST_PYTHON" -m pytest \
    tests/test_preload.py \
    tests/test_mcp_tool_validation.py \
    tests/test_code_execution_guards.py \
    tests/test_runtime_state_report.py \
    tests/test_startup_readiness.py \
    tests/test_subordinate_timeout.py \
    tests/test_response_tool_compat.py \
    -v --tb=short; then
    echo -e "${GREEN}✅ Detailed host reliability regressions passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Detailed host reliability regressions failed${NC}"
    ((FAILED++))
fi
echo ""

echo -e "${BLUE}[Phase 3] Live runtime truth checks (container)${NC}"
if docker ps --filter name=agent-zero --format "{{.Names}}" 2>/dev/null | grep -q "^agent-zero$"; then
    SETTINGS_CHECK=$(docker exec agent-zero /bin/sh -lc \
        'cd /a0 && PYTHONPATH=/a0 /opt/venv-a0/bin/python -c "from python.helpers import dotenv, runtime, settings; runtime.initialize(); dotenv.load_dotenv(); settings.reload_settings(); print(settings.SETTINGS_FILE)"' \
        2>/dev/null)
    TOKEN_CHECK=$(docker exec agent-zero /bin/sh -lc \
        'cd /a0 && PYTHONPATH=/a0 /opt/venv-a0/bin/python -c "from python.helpers import dotenv, runtime, settings; runtime.initialize(); dotenv.load_dotenv(); settings.reload_settings(); print(settings.get_settings()[\"mcp_server_token\"])"' \
        2>/dev/null)

    if [[ "$SETTINGS_CHECK" == "/a0/usr/settings.json" && -n "$TOKEN_CHECK" ]]; then
        echo -e "${GREEN}✅ Live container uses /a0/usr/settings.json and derives MCP token at runtime${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ Live runtime truth check failed${NC}"
        echo "   settings path: ${SETTINGS_CHECK:-<missing>}"
        echo "   token present: $([[ -n "$TOKEN_CHECK" ]] && echo yes || echo no)"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠️  agent-zero container not running; skipping live runtime truth checks${NC}"
    ((SKIPPED++))
fi
echo ""

echo -e "${BLUE}[Phase 4] Reliability pytest suite (inside container via uv)${NC}"
if docker ps --filter name=agent-zero --format "{{.Names}}" 2>/dev/null | grep -q "^agent-zero$"; then
    if docker exec agent-zero /bin/sh -lc \
        'if ! /opt/venv-a0/bin/python -c "import pytest, pytest_asyncio, pytest_mock" >/dev/null 2>&1; then uv pip install --python /opt/venv-a0/bin/python pytest pytest-asyncio pytest-mock >/dev/null; fi && cd /git/agent-zero && PYTHONPATH=/git/agent-zero:/a0 /opt/venv-a0/bin/python -m pytest tests/test_reliability_*.py -v --tb=short' \
        ; then
        echo -e "${GREEN}✅ Container reliability pytest suite passed${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ Container reliability pytest suite failed${NC}"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠️  agent-zero container not running; skipping container reliability pytest suite${NC}"
    ((SKIPPED++))
fi
echo ""

echo -e "${BLUE}[Phase 5] App venv parity (container)${NC}"
if docker ps --filter name=agent-zero --format "{{.Names}}" 2>/dev/null | grep -q "^agent-zero$"; then
    if docker exec agent-zero /bin/sh -lc \
        'cd /a0 && PYTHONPATH=/a0 /opt/venv-a0/bin/python -c "import google.auth, googleapiclient; print(google.auth.__version__)"' \
        ; then
        echo -e "${GREEN}✅ App venv resolves google-auth and googleapiclient${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ App venv parity check failed${NC}"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠️  agent-zero container not running; skipping app venv parity check${NC}"
    ((SKIPPED++))
fi
echo ""

echo "=========================================="
echo "Reliability Validation Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}✅ Reliability validation passed${NC}"
    exit 0
fi

echo -e "${RED}❌ Reliability validation failed${NC}"
exit 1
