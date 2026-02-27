# Crawl4AI RAG: Playwright Chromium Not Found

## Symptom

When using the **crawl4ai-rag** MCP tool `crawl_website` (or other tools that use a browser), the server returns:

```
BrowserType.launch: Executable doesn't exist at /root/.cache/ms-playwright/chromium-1208/chrome-linux/chrome
Looks like Playwright was just installed or updated.
Please run the following command to download new browsers:
    playwright install
```

## Cause

The [mcp-crawl4ai-rag](https://github.com/coleam00/mcp-crawl4ai-rag) server uses Playwright for crawling. The upstream Docker image and many Python installs do **not** install the browser binaries, so the first crawl fails until Chromium is installed.

## Fix

### Option A: Fix existing Docker container

If crawl4ai-rag is already running in Docker (e.g. on `192.168.50.7:8054`):

1. Find the container:
   ```bash
   docker ps | grep crawl4ai
   ```

2. Install Chromium inside the running container:
   ```bash
   docker exec -it <container_id_or_name> playwright install chromium
   ```

3. Retry the crawl from Cursor (e.g. “crawl4ai-rag crawl_website https://github.com/openagen/zeroclaw”).

**Note:** The install is lost when the container is recreated. Use Option B or C for a permanent fix.

### Option B: Run with our image (Playwright pre-installed)

This repo provides a Dockerfile that builds crawl4ai-rag **with** Chromium installed. From the AgentZ repo root:

```bash
# Build (requires Docker and network)
./scripts/docker/run_crawl4ai_rag.sh build

# Run (uses .env in current dir or copy from mcp-crawl4ai-rag)
./scripts/docker/run_crawl4ai_rag.sh run
```

Then point Cursor MCP at the URL (e.g. `http://192.168.50.7:8054/sse` if port 8054 is published). See [run_crawl4ai_rag.sh](../../scripts/docker/run_crawl4ai_rag.sh) for env vars and ports.

### Option C: Fix non-Docker (uv / venv) install

If you run the server with `uv run src/crawl4ai_mcp.py` (no Docker):

1. In the same environment where the server runs:
   ```bash
   cd /path/to/mcp-crawl4ai-rag
   uv run playwright install chromium
   # or, if using a venv:
   .venv/bin/python -m playwright install chromium
   ```

2. Restart the MCP server and retry the crawl.

## Verify

- **Docker:** `docker exec <container> ls /root/.cache/ms-playwright/` (or equivalent) should show a `chromium-*` directory.
- **Local:** `ls ~/.cache/ms-playwright/` (or `$PLAYWRIGHT_BROWSERS_PATH` if set) should list Chromium.

After Chromium is installed, `crawl_website` and other browser-based tools should succeed.
