#!/usr/bin/env bash
# Verify E2E-related fixes: run pytest and ruff in parallel (same checks as
# parallel subagent verification). Use from repo root: ./scripts/testing/verify-e2e-fixes.sh

set -e

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
cd "$ROOT"

# Optional: venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

RESULTS_DIR=$(mktemp -d)
trap 'rm -rf "$RESULTS_DIR"' EXIT

echo "Running pytest and ruff in parallel..."
echo ""

# Pytest (exclude rate_limiter, UI, e2e)
(
    python -m pytest tests/ -v --ignore=tests/test_ui_ --ignore=tests/e2e --ignore=tests/rate_limiter_test.py -x 2>&1
    echo $? > "$RESULTS_DIR/pytest.exit"
) > "$RESULTS_DIR/pytest.log" 2>&1 &

# Ruff check + format on common E2E-touched areas
(
    ruff check python/helpers/files.py python/helpers/persist_chat.py python/helpers/file_browser.py \
        python/api/file_info.py python/api/image_get.py python/api/message.py python/api/api_log_get.py run_ui.py 2>&1
    R1=$?
    ruff format --check python/helpers/files.py python/helpers/persist_chat.py python/api/file_info.py \
        python/api/image_get.py python/api/message.py python/api/api_log_get.py 2>&1
    R2=$?
    [ "$R1" -eq 0 ] && [ "$R2" -eq 0 ] && echo 0 > "$RESULTS_DIR/ruff.exit" || echo 1 > "$RESULTS_DIR/ruff.exit"
) > "$RESULTS_DIR/ruff.log" 2>&1 &

wait

PYTEST_EXIT=$(cat "$RESULTS_DIR/pytest.exit" 2>/dev/null || echo 1)
RUFF_EXIT=$(cat "$RESULTS_DIR/ruff.exit" 2>/dev/null || echo 1)

echo "========== pytest =========="
tail -30 "$RESULTS_DIR/pytest.log"
echo ""
echo "========== ruff =========="
tail -20 "$RESULTS_DIR/ruff.log"
echo ""

FAILED=0
if [ "$PYTEST_EXIT" -ne 0 ]; then
    echo -e "${RED}pytest: FAILED${NC}"
    FAILED=1
else
    echo -e "${GREEN}pytest: PASSED${NC}"
fi
if [ "$RUFF_EXIT" -ne 0 ]; then
    echo -e "${RED}ruff: FAILED${NC}"
    FAILED=1
else
    echo -e "${GREEN}ruff: PASSED${NC}"
fi

if [ "$FAILED" -eq 0 ]; then
    echo -e "\n${GREEN}All checks passed.${NC}"
    exit 0
else
    echo -e "\n${RED}Some checks failed. See logs above.${NC}"
    exit 1
fi
