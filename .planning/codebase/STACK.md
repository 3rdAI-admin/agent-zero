# Technology Stack

**Analysis Date:** 2025-02-20

## Languages

**Primary:**
- Python 3.11.13 – Agent core, API, tools, helpers, tests (`.python-version`; `pyrightconfig.json` references 3.12 for type checking)

**Secondary:**
- Not detected (JavaScript in `webui/` is vendor/legacy; no Node/TS app at repo root)

## Runtime

**Environment:**
- CPython 3.11.x (`.python-version`: 3.11.13)

**Package Manager:**
- pip (requirements-driven)
- Lockfile: Not detected at repo root (no `requirements.lock`, `uv.lock`, or `poetry.lock` in workspace)

## Frameworks

**Core:**
- Flask 3.0.3 (async) – Web UI and API server (`run_ui.py`, `python/helpers/api.py`)
- LiteLLM 1.79.3 – Unified LLM completion/embedding across providers (`models.py`, `requirements2.txt`)
- LangChain (langchain-core 0.3.49, langchain-community 0.3.19) – Prompts, messages, vector store, document loaders (`agent.py`, `python/helpers/vector_db.py`, `python/helpers/document_query.py`)

**Protocols / Servers:**
- FastMCP 2.3.4 – MCP server exposed at `/mcp` (`python/helpers/mcp_server.py`)
- FastA2A 0.5.0 – Agent-to-agent protocol at `/a2a` (`python/helpers/fasta2a_server.py`, `python/helpers/fasta2a_client.py`)

**Testing:**
- pytest 8.4.2+ – Test runner (`requirements.dev.txt`)
- pytest-asyncio 1.2.0+ – Async tests
- pytest-mock 3.15.1+ – Mocking

**Build/Dev:**
- Ruff – Linting/formatting (`ruff.toml`: target py311, line-length 88)
- Pyright – Type checking (`pyrightconfig.json`: typeCheckingMode off, pythonVersion 3.12)
- Docker – Build and run (`Dockerfile`, `docker-compose.yml`); base image `agent0ai/agent-zero-base:latest`

## Key Dependencies

**Critical:**
- openai 1.99.5 – Client used via LiteLLM for OpenAI-compatible endpoints (`models.py`, `requirements2.txt`)
- pydantic 2.11.7 – Validation and settings (`python/helpers/task_scheduler.py`, `python/helpers/browser_agent.py`, MCP/FastA2A schemas)
- python-dotenv 1.1.0 – Environment loading from `.env` (`python/helpers/dotenv.py`, `models.py`, `run_ui.py`)
- nest-asyncio 1.6.0 – Nested event loop support (`agent.py`)

**LLM / Embeddings:**
- sentence-transformers 3.0.1 – Local embedding models
- tiktoken 0.8.0 – Token counting
- browser-use 0.5.11 – Browser automation (with monkeypatch in `models.py`)

**Vector / RAG:**
- faiss-cpu >=1.11.0 – In-memory vector index (`python/helpers/vector_db.py`, `python/helpers/memory.py`)
- langchain-unstructured 0.1.6 (all-docs) – Document loaders
- unstructured 0.16.23 (all-docs), unstructured-client 0.31.0 – Document processing

**Infrastructure:**
- docker 7.1.0 – Docker SDK
- a2wsgi 1.10.8 – WSGI/ASGI bridging for Flask + MCP/A2A
- playwright 1.52.0 – Browser automation
- paramiko 3.5.0 – SSH (`python/helpers/shell_ssh.py`)
- GitPython 3.1.43 – Git operations

**Other:**
- pymupdf 1.25.3, pypdf 6.0.0, pdf2image 1.17.0 – PDF handling
- openai-whisper 20240930 – STT (`python/helpers/whisper.py`)
- kokoro >=0.9.2 – TTS
- duckduckgo-search 6.1.12 – Search fallback
- imapclient 3.0.1+, exchangelib 5.4.3+ – Email (IMAP/Exchange) (`python/helpers/email_client.py`)
- crontab 1.0.1 – Scheduling
- markdown 3.7, markdownify 1.1.0 – Markdown handling

## Configuration

**Environment:**
- `.env` at repo root; loaded via `python/helpers/dotenv.py` (`load_dotenv()`, `get_dotenv_value()`). Path from `get_abs_path(".env")`.
- Key configs: `AUTH_LOGIN`, `AUTH_PASSWORD`, `FLASK_SECRET_KEY`, `AGENT_ZERO_HTTP_ONLY`, `AGENT_ZERO_CERT_IPS`, `TUNNEL_API_PORT`, `TZ`, `TOKENIZERS_PARALLELISM`, plus provider API keys (e.g. `ANTHROPIC_API_KEY`) and model settings in UI-backed settings.

**Build:**
- `ruff.toml` – Ruff lint/format
- `pyrightconfig.json` – Pyright (include/exclude, pythonVersion)
- `conf/model_providers.yaml` – LLM provider definitions (LiteLLM provider IDs, names, optional kwargs)
- Docker: `Dockerfile`, `docker/run/fs/`, `docker/install_*` scripts; `docker-compose.yml` for env_file, ports, volumes, healthcheck

## Platform Requirements

**Development:**
- Python 3.11; virtual env (e.g. `.venv`) per project rules
- Optional: Playwright browsers, system libs for PDF/OCR (pytesseract, pdf2image), VNC for CAPTCHA

**Production:**
- Docker (agent-zero image); ports 80 (UI), 5900 (VNC), 9000–9009 (tunnel, MCP, etc.); env_file `.env`; mounts for memory, knowledge, logs, tmp, claude-config

---

*Stack analysis: 2025-02-20*
