#!/usr/bin/env python3
"""
Test MCP Connection to Agent Zero
This script tests the MCP connection from Claude Code perspective
"""

import asyncio
import httpx
import sys
import json

async def test_mcp_connection(base_url: str, token: str):
    """Test MCP connection to Agent Zero"""
    
    # MCP SSE endpoint
    sse_url = f"{base_url}/mcp/t-{token}/sse"
    
    print(f"Testing MCP connection to: {sse_url}")
    print("-" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test 1: Check if endpoint exists
            print("\n[Test 1] Checking MCP endpoint...")
            response = await client.get(sse_url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ MCP endpoint is accessible")
            elif response.status_code == 401:
                print("   ⚠️  Authentication required (this is expected)")
            elif response.status_code == 404:
                print("   ❌ MCP endpoint not found")
                return False
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
            
            # Test 2: Try to connect via SSE (simplified check)
            print("\n[Test 2] Testing SSE connection...")
            try:
                # SSE connections require streaming, so we'll just check headers
                headers = {
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache"
                }
                async with client.stream("GET", sse_url, headers=headers) as response:
                    if response.status_code == 200:
                        print("   ✅ SSE connection successful")
                        # Try to read first line
                        async for line in response.aiter_lines():
                            if line:
                                print(f"   📡 Received: {line[:100]}...")
                                break
                        return True
                    else:
                        print(f"   ⚠️  SSE connection returned: {response.status_code}")
                        return False
            except Exception as e:
                print(f"   ⚠️  SSE connection error: {e}")
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
    
    # Get connection details
    base_url = "http://localhost:8888"
    token = None
    
    # Try to get token from environment or settings
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
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
        print("1. Log into Agent Zero Web UI at http://localhost:8888")
        print("2. Go to Settings > MCP Server")
        print("3. Copy the token from the MCP Server URL")
        print("\nOr provide token as argument:")
        print("  python3 test_mcp_connection.py YOUR_TOKEN")
        print("\nThe token is also generated from your username/password")
        print("and can be found in Settings > External Services > API Token")
        return
    
    # Test connection
    success = await test_mcp_connection(base_url, token)
    
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
        print("2. Check Web UI is accessible: curl http://localhost:8888")
        print("3. Verify token is correct (from Settings > MCP Server)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
