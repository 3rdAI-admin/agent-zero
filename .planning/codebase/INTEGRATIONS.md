# External Integrations

**Analysis Date:** 2025-02-20

## APIs & External Services

**LLM / Chat / Embedding (via LiteLLM):**
- Multiple providers configured in `conf/model_providers.yaml`: Anthropic, OpenAI, OpenRouter, Ollama, LM Studio, Groq, Google (Gemini), HuggingFace, Mistral, DeepSeek, Azure, Venice.ai, Agent Zero Venice, CometAPI, GitHub Copilot, Sambanova, etc.
- Auth: Provider-specific env vars (e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`); optional `api_base` and `extra_headers` in provider kwargs and in settings (`chat_model_api_base`, etc.).
- Implementation: `models.py` uses `litellm.completion`, `litellm.acompletion`, `litellm.embedding`; `initialize.py` builds `ModelConfig` from `python/helpers/settings.py` (chat, util, embed, browser models).

**Search:**
- SearXNG – Self-hosted search at `http://localhost:55510/search`; called via `python/helpers/searxng.py` (aiohttp POST, `q`, `format=json`). Used by `python/tools/search_engine.py`.
- DuckDuckgo – Fallback/search via `duckduckgo-search` package (in `requirements.txt`).

**Tunnel:**
- Tunnel API – Local HTTP service on `TUNNEL_API_PORT` (default 55520); `python/api/tunnel_proxy.py` forwards to it with `requests.post`. Fallback to `python/api/tunnel.py` if service unavailable.
- Tunnel managers: Serveo, Flare (see `python/helpers/tunnel_manager.py`).

## Data Storage

**Databases:**
- None. No SQL/NoSQL client or ORM in stack; state is file-based and in-memory.

**Vector / RAG:**
- In-memory FAISS (langchain_community.vectorstores.FAISS) with optional cache-backed embeddings (`python/helpers/vector_db.py`, `python/helpers/memory.py`). Embeddings from agent’s embedding model (sentence-transformers or API). No persistent vector DB (e.g. Chroma/Qdrant) in use.

**File Storage:**
- Local filesystem only. Paths normalized via `python/helpers/files.py` (`get_abs_path`); Docker mounts for `memory`, `knowledge`, `logs`, `tmp`, repo at `/git/agent-zero`, `.env` at `/a0/.env`.

**Caching:**
- In-memory: CacheBackedEmbeddings (InMemoryByteStore) in `python/helpers/vector_db.py`; no external cache service.

## Authentication & Identity

**UI / API:**
- Custom: Optional basic auth via `.env` (`AUTH_LOGIN`, `AUTH_PASSWORD`); hashed in `python/helpers/login.py` for session check. `FLASK_SECRET_KEY` for Flask session; session cookie bound to runtime ID.
- API key for programmatic access: `mcp_server_token` from settings; validated in `run_ui.py` (`requires_api_key`, `X-API-KEY` header or JSON `api_key`).

**MCP / A2A:**
- MCP and A2A endpoints protected by same token: `mcp_server_token` (Bearer / API key). FastA2A client uses `A2A_TOKEN` env when connecting to another agent (`python/helpers/fasta2a_client.py`).

**SSH:**
- Paramiko in `python/helpers/shell_ssh.py`; credentials from settings/context (e.g. RFC password, root password for dockerized env).

## Monitoring & Observability

**Error Tracking:**
- None. No Sentry or similar; errors surfaced via logs and UI.

**Logs:**
- Python logging; level set to WARNING in `run_ui.py`. LiteLLM logging suppressed to ERROR in `models.py`. Log directory mounted as `./logs` in Docker.

## CI/CD & Deployment

**Hosting:**
- Docker Compose; single service `agent-zero` (build from `Dockerfile`, image `agent-zero:local`). Ports: `${HOST_PORT:-8888}:80`, `5901:5900` (VNC).

**CI Pipeline:**
- `.github/prompts/` present; no CI workflow files inspected; deployment is Docker-based.

## Environment Configuration

**Required env vars (representative):**
- Auth (optional): `AUTH_LOGIN`, `AUTH_PASSWORD`
- Server: `FLASK_SECRET_KEY` (or ephemeral), `AGENT_ZERO_HTTP_ONLY`, `AGENT_ZERO_CERT_IPS`, `AGENT_ZERO_REGENERATE_CERT`
- Tunnel: `TUNNEL_API_PORT`
- LLM: Provider-specific keys (e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) and optional base URLs in settings
- MCP/A2A: `mcp_server_token` stored in settings (persisted); client `A2A_TOKEN` for outbound A2A
- RFC/docker: `ROOT_PASSWORD`, `RFC_PASSWORD`, `RFC_URL`, etc. (see `python/helpers/settings.py`)

**Secrets location:**
- `.env` at repo root (and `/a0/.env` in container); settings and secrets manager in `python/helpers/settings.py` / `python/helpers/secrets.py`. Never commit secrets (forbidden files rules).

## Webhooks & Callbacks

**Incoming:**
- None. No webhook endpoints; interaction is request/response (Flask routes, MCP tools, A2A tasks).

**Outgoing:**
- None. No outbound webhook or callback configuration in codebase.

## Other Integrations

**Email:**
- IMAP: `imapclient` in `python/helpers/email_client.py` (server/credentials from callers or variables).
- Exchange: `exchangelib` (optional); same client interface, `account_type="exchange"`.

**Document processing:**
- Unstructured (langchain-unstructured, unstructured-client); `USER_AGENT` set to `@mixedbread-ai/unstructured` in `python/helpers/document_query.py`. PyMuPDF, pypdf, pdf2image, pytesseract for PDF/OCR.

**HTTP client:**
- `aiohttp` used in `python/helpers/searxng.py` and `python/helpers/document_query.py` (not listed in `requirements.txt`; likely transitive e.g. langchain-community). `requests` used in `python/api/tunnel_proxy.py` (transitive or Flask).

---

*Integration audit: 2025-02-20*
