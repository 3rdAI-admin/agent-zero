#!/bin/bash
# Generate a self-signed SSL certificate for the Agent Zero web UI.
# Enables HTTPS so browsers allow microphone/WebRTC access.
# Idempotent: skips generation if cert already exists.
#
# For remote MCP/A2A clients (e.g. PCI app at 192.168.50.7), add the host's
# LAN IP so the cert matches when connecting to https://192.168.50.7:8888:
#   AGENT_ZERO_CERT_IPS=192.168.50.7
# If the cert already exists, remove it (or set AGENT_ZERO_REGENERATE_CERT=1)
# and restart the container so this script runs again with the new IP(s).

CERT_DIR="/etc/ssl/agent-zero"
CERT_FILE="$CERT_DIR/server.crt"
KEY_FILE="$CERT_DIR/server.key"

# Base SAN: localhost and common names (works for same-machine clients)
SAN="DNS:localhost,DNS:agent-zero,DNS:host.docker.internal,IP:127.0.0.1,IP:0.0.0.0"

# Add LAN IP(s) for remote clients (comma-separated). Example: 192.168.50.7
if [ -n "$AGENT_ZERO_CERT_IPS" ]; then
    for ip in $(echo "$AGENT_ZERO_CERT_IPS" | tr ',' ' '); do
        ip=$(echo "$ip" | tr -d ' ')
        [ -n "$ip" ] && SAN="${SAN},IP:${ip}"
    done
fi

# Regenerate if env asks for it (e.g. after adding AGENT_ZERO_CERT_IPS)
if [ -n "$AGENT_ZERO_REGENERATE_CERT" ] && [ -f "$CERT_FILE" ]; then
    rm -f "$CERT_FILE" "$KEY_FILE"
fi

if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "SSL certificate already exists at $CERT_DIR, skipping generation."
    exit 0
fi

echo "Generating self-signed SSL certificate (SAN includes: $SAN)..."

mkdir -p "$CERT_DIR"

openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -days 365 \
    -subj "/CN=agent-zero" \
    -addext "subjectAltName=${SAN}"

chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo "SSL certificate generated at $CERT_DIR"
