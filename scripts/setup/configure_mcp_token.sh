#!/bin/bash
# Configure MCP Token for Agent Zero

set -e

echo "=========================================="
echo "Configuring MCP Token for Agent Zero"
echo "=========================================="
echo ""

# Run Python script inside container to generate and set token
docker exec agent-zero bash -c "cd /a0 && python3 << 'PYTHON_SCRIPT'
import json
import hashlib
import base64
import os

# Read .env file to get credentials
def get_env_value(key, default=''):
    env_file = '/a0/.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    if k == key:
                        return v.strip('\"').strip(\"'\")
    return os.getenv(key, default)

# Get runtime ID (from persistent file or generate)
runtime_id_file = '/a0/usr/runtime_id'
if os.path.exists(runtime_id_file):
    with open(runtime_id_file, 'r') as f:
        runtime_id = f.read().strip()
else:
    runtime_id = 'default-runtime-id'

# Get credentials
username = get_env_value('AUTH_LOGIN', '')
password = get_env_value('AUTH_PASSWORD', '')

if not username or not password:
    print('⚠️  Warning: AUTH_LOGIN or AUTH_PASSWORD not found in .env')
    print('   Token will be generated with empty credentials')

# Generate token (same as create_auth_token)
hash_bytes = hashlib.sha256(f'{runtime_id}:{username}:{password}'.encode()).digest()
token = base64.urlsafe_b64encode(hash_bytes).decode().replace('=', '')[:16]

# Read current settings
settings_file = '/a0/tmp/settings.json'
try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except:
    settings = {}

# Update token
old_token = settings.get('mcp_server_token', '')
settings['mcp_server_token'] = token

# Save settings
with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print(f'✅ MCP token configured')
print(f'   Token: {token}')
print(f'   Previous token: {old_token if old_token else \"(empty)\"}')
print(f'')
print(f'📋 MCP Connection URLs:')
print(f'   SSE:  http://localhost:8888/mcp/t-{token}/sse')
print(f'   HTTP: http://localhost:8888/mcp/t-{token}/http/')
print(f'')
print(f'📝 Claude Code Configuration (add to mcp.json):')
print(f'{{')
print(f'    \"mcpServers\": {{')
print(f'        \"agent-zero\": {{')
print(f'            \"type\": \"sse\",')
print(f'            \"url\": \"http://localhost:8888/mcp/t-{token}/sse\"')
print(f'        }}')
print(f'    }}')
print(f'}}')
PYTHON_SCRIPT
"

echo ""
echo "=========================================="
echo "Configuration Complete"
echo "=========================================="
echo ""
echo "⚠️  Note: You may need to restart Agent Zero for the MCP server"
echo "   to pick up the new token, or the token will be updated automatically"
echo "   when settings are reloaded."
echo ""
echo "To verify:"
echo "  1. Check Web UI: http://localhost:8888 → Settings → MCP Server"
echo "  2. Test endpoint: curl http://localhost:8888/mcp/t-TOKEN/sse"
echo ""
