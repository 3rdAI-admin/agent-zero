#!/usr/bin/env bash
# Run Crawl4AI RAG MCP server with Playwright Chromium installed (so crawl_website works).
# Build: ./scripts/docker/run_crawl4ai_rag.sh build
# Run:   ./scripts/docker/run_crawl4ai_rag.sh run
# Requires: Docker, .env with OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY (see mcp-crawl4ai-rag README).

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRAWL_DIR="${SCRIPT_DIR}/crawl4ai_rag"
IMAGE_NAME="agentz/crawl4ai-rag"
CONTAINER_NAME="crawl4ai-rag"
PORT="${CRAWL4AI_PORT:-8054}"
ENV_FILE="${ENV_FILE:-.env}"

usage() {
  echo "Usage: $0 build | run | stop | test"
  echo "  build  - Build Docker image (Playwright Chromium included)"
  echo "  run    - Run container (requires .env or set ENV_FILE)"
  echo "  stop   - Stop and remove container"
  echo "  test   - Test connection to crawl4ai-rag (container + HTTP)"
}

build() {
  docker build -t "${IMAGE_NAME}" "${CRAWL_DIR}"
}

run() {
  if [[ ! -f "${ENV_FILE}" ]]; then
    echo "Env file not found: ${ENV_FILE}. Create one with OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY. See https://github.com/coleam00/mcp-crawl4ai-rag#configuration"
    exit 1
  fi
  docker run -d --name "${CONTAINER_NAME}" \
    --env-file "${ENV_FILE}" \
    -e "PORT=${PORT}" \
    -e "HOST=0.0.0.0" \
    -e "TRANSPORT=sse" \
    -p "${PORT}:${PORT}" \
    --init \
    "${IMAGE_NAME}"
  echo "Started ${CONTAINER_NAME} on port ${PORT}. MCP URL: http://localhost:${PORT}/sse"
}

stop() {
  docker stop "${CONTAINER_NAME}" 2>/dev/null || true
  docker rm "${CONTAINER_NAME}" 2>/dev/null || true
}

test_connection() {
  echo "=== Container status ==="
  if ! docker ps -a --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}} {{.Status}} {{.Ports}}"; then
    echo "Docker not available or container missing."
    return 1
  fi
  echo ""
  echo "=== HTTP connection (timeout 5s) ==="
  if curl -sS -o /dev/null -w "HTTP %{http_code} → %{url_effective}\n" --connect-timeout 2 --max-time 5 "http://127.0.0.1:${PORT}/" 2>&1; then
    echo "OK: crawl4ai-rag is reachable at http://127.0.0.1:${PORT}/ (MCP SSE: http://127.0.0.1:${PORT}/sse)"
  else
    echo "FAIL: No response from http://127.0.0.1:${PORT}/ (is the container running?)"
    return 1
  fi
}

case "${1:-}" in
  build) build ;;
  run)   run ;;
  stop)  stop ;;
  test)  test_connection ;;
  *)     usage; exit 1 ;;
esac
