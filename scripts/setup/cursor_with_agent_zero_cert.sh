#!/usr/bin/env bash
# Launch Cursor with Agent Zero's self-signed cert trusted (NODE_EXTRA_CA_CERTS)
# so MCP and A2A connections to https://<host>:8888 work without "self signed certificate" errors.
#
# Run trust_agent_zero_cert.sh once first to export the cert.
# Usage: ./scripts/setup/cursor_with_agent_zero_cert.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CERT_FILE="$REPO_ROOT/tmp/agent-zero-server.crt"

if [[ ! -f "$CERT_FILE" ]]; then
    echo "Certificate not found at $CERT_FILE"
    echo "Run once from repo root: ./scripts/setup/trust_agent_zero_cert.sh"
    exit 1
fi

export NODE_EXTRA_CA_CERTS="$CERT_FILE"
echo "Starting Cursor with NODE_EXTRA_CA_CERTS=$CERT_FILE"
exec open -a Cursor "$@"
