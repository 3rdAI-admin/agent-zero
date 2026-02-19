#!/usr/bin/env python3
"""
Test MCP Connection to Agent Zero
This script tests the MCP connection from Claude Code perspective
"""

import asyncio
import httpx
import sys
import json

async def test_mcp_connection(base_url: str, token: str, verify: bool = False):
    """Test MCP connection to Agent Zero. Use verify=False for self-signed cert."""
    # MCP SSE endpoint; Agent Zero serves HTTPS only
    base_url = base_url.rstrip("/")
    if not base_url.startswith("http"):
        base_url = "https://" + base_url.lstrip("/")
    sse_url = f"{base_url}/mcp/t-{token}/sse"

    print(f"Testing MCP connection to: {sse_url}")
    print(f"TLS verify: {verify}")
    print("-" * 60)

    async with httpx.AsyncClient(timeout=30.0, verify=verify) as client:
        try:
            # SSE endpoint never closes; use stream and read first event only
            print("\n[Test 1] Opening SSE stream and reading first event...")
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
            }
            async with client.stream("GET", sse_url, headers=headers) as response:
                print(f"   Status: {response.status_code}")
                if response.status_code == 401:
                    print("   ❌ Invalid token (401)")
                    return False
                if response.status_code == 404:
                    print("   ❌ MCP endpoint not found")
                    return False
                if response.status_code != 200:
                    print(f"   ❌ Unexpected status: {response.status_code}")
                    return False
                # Read until we get the first event (endpoint)
                async for line in response.aiter_lines():
                    if line:
                        print(f"   📡 {line[:80]}{'...' if len(line) > 80 else ''}")
                        if line.startswith("event: endpoint") or "session_id" in line:
                            print("   ✅ SSE connection OK (first event received)")
                            return True
                print("   ⚠️  No event received before stream end")
                return False
                
        except httpx.ConnectError:
            print("   ❌ Connection failed - is Agent Zero running?")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

def get_mcp_token_from_settings():
    """Try to get MCP token from settings file"""
    try:
        with open("/a0/tmp/settings.json", "r") as f:
            settings = json.load(f)
            token = settings.get("mcp_server_token", "")
            if token:
                return token
    except Exception:
        pass
    return None

async def main():
    print("=" * 60)
    print("Agent Zero MCP Connection Test")
    print("=" * 60)
    
    # Get connection details: base_url and token (default HTTPS localhost)
    base_url = "https://localhost:8888"
    token = None
    if len(sys.argv) >= 2:
        token = sys.argv[1]
    if len(sys.argv) >= 3:
        base_url = sys.argv[2]
    if not token:
        # Try to read from container settings
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "exec", "agent-zero", "cat", "/a0/tmp/settings.json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                settings = json.loads(result.stdout)
                token = settings.get("mcp_server_token", "")
        except Exception:
            pass

    if not token:
        print("\n⚠️  MCP token not provided")
        print("\nTo get your MCP token:")
        print("1. Log into Agent Zero Web UI (https://localhost:8888)")
        print("2. Go to Settings > MCP Server")
        print("3. Copy the token from the MCP Server URL")
        print("\nUsage:")
        print("  python3 test_mcp_connection.py TOKEN [BASE_URL]")
        print("  Example: python3 test_mcp_connection.py 11mu_QnUJiEWloEq https://192.168.50.7:8888")
        return

    # Test connection (verify=False for self-signed cert)
    success = await test_mcp_connection(base_url, token, verify=False)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ MCP Connection Test: PASSED")
        print("\nNext steps:")
        print("1. Configure Claude Code with this MCP server URL:")
        print(f"   {base_url}/mcp/t-{token}/sse")
        print("\n2. Add to Claude Code's mcp.json:")
        print(json.dumps({
            "mcpServers": {
                "agent-zero": {
                    "type": "sse",
                    "url": f"{base_url}/mcp/t-{token}/sse"
                }
            }
        }, indent=2))
    else:
        print("❌ MCP Connection Test: FAILED")
        print("\nTroubleshooting:")
        print("1. Verify Agent Zero is running: docker ps | grep agent-zero")
        print("2. Check Web UI: curl -k https://localhost:8888")
        print("3. Verify token is correct (from Settings > MCP Server)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
