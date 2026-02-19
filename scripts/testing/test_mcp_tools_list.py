#!/usr/bin/env python3
"""Test MCP tools/list: SSE -> get session -> initialize -> tools/list. Run from host."""

import asyncio
import httpx
import json
import re
import sys

BASE = "https://192.168.50.7:8888"
TOKEN = "11mu_QnUJiEWloEq"


async def main():
    if len(sys.argv) >= 2:
        global TOKEN
        TOKEN = sys.argv[1]
    if len(sys.argv) >= 3:
        global BASE
        BASE = sys.argv[2].rstrip("/")

    sse_url = f"{BASE}/mcp/t-{TOKEN}/sse"
    print(f"1. Opening SSE: {sse_url}")
    messages_url = None
    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        async with client.stream("GET", sse_url, headers={"Accept": "text/event-stream"}) as r:
            if r.status_code != 200:
                print(f"   SSE failed: {r.status_code}")
                return
            async for line in r.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:].strip()
                    if "session_id=" in data:
                        # data is like /mcp/t-XXX/messages/?session_id=YYY
                        messages_url = BASE + data if data.startswith("/") else data
                        break
                if messages_url:
                    break

    if not messages_url:
        print("   Could not get messages URL from SSE")
        return
    print(f"   Messages URL: {messages_url}")

    print("2. Sending initialize + tools/list...")
    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"},
            },
        }
        r = await client.post(messages_url, json=init_req)
        if r.status_code != 200:
            print(f"   initialize failed: {r.status_code} {r.text[:200]}")
            return
        init_resp = r.json()
        if "error" in init_resp:
            print(f"   initialize error: {init_resp['error']}")
            return
        print("   initialize OK")

        tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        r = await client.post(messages_url, json=tools_req)
        if r.status_code != 200:
            print(f"   tools/list failed: {r.status_code} {r.text[:200]}")
            return
        tools_resp = r.json()
        if "error" in tools_resp:
            print(f"   tools/list error: {tools_resp['error']}")
            return
        tools = tools_resp.get("result", {}).get("tools", [])
        print(f"   tools/list OK: {len(tools)} tools")
        for t in tools[:5]:
            print(f"      - {t.get('name', '?')}")
        if len(tools) > 5:
            print(f"      ... and {len(tools) - 5} more")


if __name__ == "__main__":
    asyncio.run(main())
