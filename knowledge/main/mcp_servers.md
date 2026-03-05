# Available MCP Servers — Already Configured

DO NOT create new MCP server entries or ask user to configure. The servers below are already set up.

## Connected MCP Servers

| Server | Type | URL | Tools | Status |
|--------|------|-----|-------|--------|
| archon | streamable-http | http://archon-mcp:8051/mcp | 14 tools (task management, Supabase integration) | Active |
| google_workspace | streamable-http | http://workspace_mcp:8889/mcp | Gmail, Drive, Docs, Sheets, Calendar, Tasks | Active (container) |
| crawl4ai_rag | streamable-http | (configured in user settings) | 5 tools (web crawling, RAG) | Active |

## Archon Tools

Archon provides task management and database integration:

- **Task management**: create_task, list_tasks, update_task, complete_task, delete_task
- **Database**: query_supabase, insert_supabase, update_supabase, delete_supabase
- **Integration**: sync_to_ide8, handoff_to_ide, get_task_dependencies
- **Project**: list_projects, create_project, update_project

Full list: 14 tools available via MCP connection

## Crawl4AI RAG Tools

Crawl4AI provides web scraping and content extraction:

- **crawl_website**: Fetch and parse web content with AI-powered extraction
- **extract_structured_data**: Extract JSON from HTML using selectors
- **search_content**: Full-text search across crawled content
- **get_page_metadata**: Extract title, description, og:tags
- **follow_links**: Recursively crawl linked pages

Full list: 5 tools available via MCP connection

## Google Workspace MCP

Google Workspace MCP provides Gmail, Drive, Docs, Sheets, Slides, Calendar, and Tasks. Service `workspace_mcp` runs in the same Docker Compose stack; URL `http://workspace_mcp:8889/mcp`. First-time OAuth: run `./scripts/setup/run_workspace_mcp.sh` on the host, then copy `~/.google_workspace_mcp` to `./workspace-mcp-credentials`. See [docs/setup/GOOGLE_WORKSPACE_MCP_CONTAINER.md](../../docs/setup/GOOGLE_WORKSPACE_MCP_CONTAINER.md).

## Configuration

MCP server configuration is stored in:

- **System-wide**: `.mcp.json` (root of project; used by agent-zero)
- **User-specific**: `/a0/usr/settings.json` (per-user MCP servers)

Example `.mcp.json` (archon + google_workspace):
```json
{
  "mcpServers": {
    "archon": {
      "type": "streamable-http",
      "url": "http://archon-mcp:8051/mcp",
      "init_timeout": 30,
      "tool_timeout": 120
    },
    "google_workspace": {
      "type": "streamable-http",
      "url": "http://workspace_mcp:8889/mcp",
      "init_timeout": 30,
      "tool_timeout": 120
    }
  }
}
```

## Network Requirements

- **archon-mcp**: Requires agent-zero container to join `archon_app-network` (configured in docker-compose.yml)
- **workspace_mcp**: Same Docker Compose default network; service name `workspace_mcp`, port 8889
- **crawl4ai_rag**: Accessible via standard Docker networking or localhost

## Important

- **NEVER** ask user to add new MCP server entries (they're already configured)
- **NEVER** recreate Archon/crawl4ai tools manually (use MCP tools instead)
- **NEVER** try to install MCP servers (they run in separate containers)
- If MCP connection fails, check:
  - Docker network: `docker network ls | grep archon`
  - Container status: `docker ps | grep archon-mcp`
  - Logs: `docker logs archon-mcp`

## Troubleshooting

**"MCP error -32001: Request timed out"**
- Check init_timeout (default 30s) and tool_timeout (default 120s) in .mcp.json
- Verify MCP server container is running and healthy
- Check Docker network connectivity

**"ExceptionGroup: unhandled errors in a TaskGroup"**
- Verify URL scheme matches server type (http for streamable-http)
- Check server is accessible: `curl -X POST http://archon-mcp:8051/mcp`
- Ensure Docker networks are correctly joined
