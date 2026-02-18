#!/bin/bash
# Generate a self-signed SSL certificate for the Agent Zero web UI.
# Enables HTTPS so browsers allow microphone/WebRTC access.
# Idempotent: skips generation if cert already exists.

CERT_DIR="/etc/ssl/agent-zero"
CERT_FILE="$CERT_DIR/server.crt"
KEY_FILE="$CERT_DIR/server.key"

if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "SSL certificate already exists at $CERT_DIR, skipping generation."
    exit 0
fi

echo "Generating self-signed SSL certificate..."

mkdir -p "$CERT_DIR"

openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -days 365 \
    -subj "/CN=agent-zero" \
    -addext "subjectAltName=DNS:localhost,DNS:agent-zero,DNS:host.docker.internal,IP:127.0.0.1,IP:0.0.0.0"

chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo "SSL certificate generated at $CERT_DIR"
