# Crawl4AI RAG MCP server with Playwright Chromium pre-installed.
# Base image includes Chromium and system deps so crawl_website works.
# See: https://playwright.dev/python/docs/docker
# Repo: https://github.com/coleam00/mcp-crawl4ai-rag
ARG PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright/python:v1.49.0-noble
FROM ${PLAYWRIGHT_IMAGE}

ARG PORT=8054
ENV PORT=${PORT}

WORKDIR /app

# Clone and install MCP server (no venv; system install per upstream)
RUN apt-get update && apt-get install -y git --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv \
    && git clone --depth 1 https://github.com/coleam00/mcp-crawl4ai-rag.git . \
    && uv pip install --system -e . \
    && crawl4ai-setup

EXPOSE ${PORT}

CMD ["python", "src/crawl4ai_mcp.py"]
