#!/usr/bin/env bash
# Export Agent Zero's self-signed cert and trust it so MCP/A2A clients (e.g. Cursor)
# stop failing with "self signed certificate". Run once after Agent Zero is up.
#
# Usage: from repo root, ./scripts/setup/trust_agent_zero_cert.sh
# Requires: Docker, agent-zero container running (or will prompt to start it).

set -e

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CERT_DEST="$REPO_ROOT/tmp/agent-zero-server.crt"
CONTAINER="${AGENT_ZERO_CONTAINER:-agent-zero}"

echo "=============================================="
echo "Agent Zero TLS cert – export and trust"
echo "=============================================="
echo ""

# Ensure container is running
if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    echo "Container '$CONTAINER' is not running."
    echo "Start it from repo root: docker compose up -d agent-zero"
    exit 1
fi

# Ensure cert exists in container (and includes LAN IP if AGENT_ZERO_CERT_IPS is set)
if ! docker exec "$CONTAINER" test -f /etc/ssl/agent-zero/server.crt 2>/dev/null; then
    echo "Certificate not found in container. Ensure Agent Zero has finished initializing."
    exit 1
fi

mkdir -p "$REPO_ROOT/tmp"
docker cp "$CONTAINER:/etc/ssl/agent-zero/server.crt" "$CERT_DEST"
echo "Exported certificate to: $CERT_DEST"
echo ""

# macOS: add to login keychain and trust for SSL (so system apps can use it)
if [[ "$(uname)" == "Darwin" ]]; then
    if security add-trusted-cert -d -r trustAsRoot -p ssl "$CERT_DEST" 2>/dev/null; then
        echo "Added cert to macOS login keychain and set trust for SSL."
    else
        echo "Could not add to keychain (you may need to do it manually):"
        echo "  Open Keychain Access → drag $CERT_DEST in → double-click cert → Trust → Always Trust for SSL."
    fi
else
    echo "On non-macOS, trust the cert in your app or set SSL_CERT_FILE / NODE_EXTRA_CA_CERTS (see below)."
fi
echo ""

# Cursor/Node use NODE_EXTRA_CA_CERTS to add extra CAs without replacing system bundle
echo "----------------------------------------------"
echo "For Cursor MCP to trust Agent Zero:"
echo "  Run Cursor with the cert as extra CA:"
echo ""
echo "  export NODE_EXTRA_CA_CERTS=\"$CERT_DEST\""
echo "  open -a Cursor"
echo ""
echo "Or use the launcher script (same effect):"
echo "  ./scripts/setup/cursor_with_agent_zero_cert.sh"
echo "----------------------------------------------"
echo ""
echo "Done. Reload MCP in Cursor (or restart Cursor) after starting it with NODE_EXTRA_CA_CERTS."
