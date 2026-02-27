# ZeroClaw Integration Analysis for Agent Zero

**Date**: 2026-02-20
**Revised**: 2026-02-20
**Status**: Research Complete — Implementation Not Started (Archon Task ID: 77e5edf9-1b35-423e-8a77-bbbfe44a818d)
**Feature**: zeroclaw-integration
**Prerequisites Completed**: Concurrent API handling (Archon: 835f888b)

## Executive Summary

ZeroClaw is a Rust-native autonomous AI agent framework (MIT licensed) that offers several capabilities complementary to Agent Zero. This document analyzes integration opportunities, architectural compatibility, and recommends a phased approach.

## ZeroClaw Profile

| Attribute | Value |
|-----------|-------|
| Repo | github.com/zeroclaw-labs/zeroclaw |
| License | MIT |
| Language | Rust |
| Binary Size | 3.4MB compressed, 8.8MB uncompressed |
| Memory Usage | <5MB RAM idle |
| Startup | <10ms warm start |
| Install | `brew install zeroclaw` or `./bootstrap.sh` |
| Docker | `./bootstrap.sh --docker` |

### Core Architecture

ZeroClaw uses a **trait-based pluggable architecture** with 8 core traits:

1. **Provider** - LLM backend (29+ integrations: Claude, OpenAI, Ollama, OpenRouter, etc.)
2. **Channel** - Input/output (CLI, Telegram, Discord, Slack, iMessage, Matrix, Signal, etc.)
3. **Tool** - Capabilities (shell, file, memory, git, browser, HTTP, composio, cron)
4. **Memory** - Storage (SQLite hybrid: FTS5 keyword + vector embeddings)
5. **RuntimeAdapter** - Execution environment (Docker, Landlock, native)
6. **SecurityPolicy** - Access control (pairing, allowlists, sandboxing, encrypted secrets)
7. **Identity** - Agent identity management
8. **Tunnel** - Secure network tunneling

---

## Agent Zero Current Architecture (Comparison)

| Component | Agent Zero | ZeroClaw | Gap/Opportunity |
|-----------|-----------|----------|-----------------|
| **Language** | Python | Rust | Complementary - Rust for performance-critical ops |
| **Memory** | FAISS vector DB + LangChain embeddings | SQLite FTS5 + vector (no deps) | ZeroClaw is self-contained, zero-dependency |
| **Tools** | Python Tool class, auto-discovered | Rust trait-based, pluggable | Similar pattern, different runtime |
| **Security** | Docker caps, env masking, API key auth | Pairing, Landlock sandbox, encrypted vault | ZeroClaw has stronger security primitives |
| **Channels** | Web UI, MCP, A2A | CLI, Telegram, Discord, Slack, Signal, etc. | ZeroClaw has 12+ channels Agent Zero lacks |
| **Extensions** | Python hooks (20+ hook points) | Trait-based providers | Agent Zero is more flexible (hooks vs traits) |
| **LLM Support** | LiteLLM abstraction (many providers) | 29+ native providers | Comparable coverage |
| **Browser** | browser-use library | Built-in browser tool | Agent Zero more mature here |
| **Code Exec** | Python/Node/shell with SSH support | Shell tool with Landlock | Agent Zero more capable |

---

## Integration Opportunities (Ranked by Value)

### 1. Channel Integrations (HIGH VALUE, MEDIUM EFFORT)

**What**: Add Telegram, Discord, Slack, Matrix, Signal messaging channels
**Why**: Agent Zero currently only has Web UI, MCP, and A2A. Adding messaging channels would dramatically expand usability.
**How**:
- Option A: Run ZeroClaw as a sidecar container that bridges messages to Agent Zero via A2A or MCP
- Option B: Port ZeroClaw's channel implementations to Python as Agent Zero extensions
- Option C: Use ZeroClaw's webhook channel to forward messages to Agent Zero's `/api_message` endpoint

**Recommendation**: **Option A** (sidecar) — lowest effort, leverages ZeroClaw's native channel support, maintains clean separation. Use `/api_message_async` + `/api_message_status` for non-blocking integration (avoids the 2+ minute HTTP timeout that affected the blocking `/api_message` endpoint).

```
[Telegram/Discord/Slack] → ZeroClaw (channel adapter) → Agent Zero (/api_message_async + polling)
```

**Prerequisite**: Concurrent API request handling (completed — per-context EventLoopThread isolation, async endpoints). See Archon task 835f888b.

### 2. SQLite Hybrid Memory (HIGH VALUE, HIGH EFFORT)

**What**: SQLite-based memory with FTS5 full-text search + vector embeddings in a single file
**Why**: Agent Zero's FAISS-based memory requires LangChain embeddings cache, separate index files, and an external embedding model. ZeroClaw's approach is self-contained with zero external dependencies.
**How**:
- Option A: Add as alternative memory backend alongside FAISS (configurable via settings)
- Option B: Wrap ZeroClaw memory as an MCP resource that Agent Zero queries
- Option C: Port the SQLite FTS5+vector approach to Python (sqlite3 + numpy)

**Recommendation**: **Option C** — Python's sqlite3 module supports FTS5 natively. Build `python/helpers/memory_sqlite.py` as an alternative Memory class that can be selected via config. Keep FAISS as default for backward compatibility.

**Key benefit**: No external embedding service needed for keyword search. FTS5 handles text matching while vector handles semantic search.

**Gotchas (discovered during codebase analysis)**:
- The `Memory` class in `python/helpers/memory.py` is **tightly coupled to FAISS** — it directly instantiates `MyFaiss` (custom FAISS subclass) with no abstraction layer
- Memory areas (MAIN, FRAGMENTS, SOLUTIONS, INSTRUMENTS) use FAISS-specific index files (`index.faiss`, `index.pkl`)
- `MemoryConsolidator` depends on FAISS similarity search internals
- **Step 0 (not in original estimate)**: Extract a `MemoryBackend` abstract interface from the existing FAISS implementation before building the SQLite backend
- Estimated effort revised: **5-8 days** (up from 3-5) to account for the abstraction layer

### 3. Security Hardening (MEDIUM VALUE, MEDIUM EFFORT)

**What**: Encrypted secrets vault, pairing codes for client authentication, Landlock sandboxing
**Why**: Agent Zero currently relies on environment variable masking and Docker capabilities. ZeroClaw has more granular security controls.
**How**:
- **Encrypted Secrets**: Replace `.env` plaintext with encrypted vault (e.g., `age` encryption)
- **Pairing Codes**: Add one-time pairing flow for MCP/A2A clients (beyond API key)
- **Landlock**: Linux kernel sandboxing (available inside Docker containers running Linux)

**Recommendation**: Start with **encrypted secrets vault** — highest security ROI. Then add pairing for MCP clients.

### 4. Rust Tool Sidecar (MEDIUM VALUE, LOW EFFORT)

**What**: Run ZeroClaw alongside Agent Zero for performance-critical operations
**Why**: Rust tools execute in <10ms vs Python's startup overhead. Useful for bulk file operations, git analysis, hardware monitoring.
**How**: Add ZeroClaw as a Docker Compose service, expose via MCP, Agent Zero calls it as an MCP tool provider.

```yaml
# docker-compose.yml addition
zeroclaw:
  image: zeroclaw:latest
  environment:
    - ZEROCLAW_PROVIDER=anthropic
  volumes:
    - ./zeroclaw-config:/root/.config/zeroclaw
  ports:
    - "8890:8080"
```

**Recommendation**: Low effort to prototype. Add ZeroClaw container, configure Agent Zero's MCP servers to include it.

### 5. Trait-Based Tool Architecture (LOW VALUE, HIGH EFFORT)

**What**: Refactor Agent Zero's tool system to use a trait/interface pattern similar to ZeroClaw
**Why**: Agent Zero's auto-discovery is already clean. ZeroClaw's traits add formal contracts but Agent Zero's hook system is more flexible.
**Recommendation**: **Skip** — Agent Zero's current Tool base class + auto-discovery + extension hooks is already well-designed. The cost of refactoring doesn't justify marginal gains.

---

## ~~Proposed Implementation Phases (Original — Superseded)~~

~~Phase 1: ZeroClaw Sidecar → Phase 2: Channel Bridge → Phase 3: SQLite Memory → Phase 4: Security~~

*Superseded by Revised Implementation Phases below, incorporating Agent Zero feedback and codebase analysis.*

## Revised Implementation Phases

### Phase 1: SQLite Hybrid Memory (5-8 days)
- **Step 0**: Extract `MemoryBackend` abstract interface from existing FAISS implementation (`python/helpers/memory.py`). Current `Memory` class is tightly coupled to `MyFaiss` with no abstraction layer.
- Build `python/helpers/memory_sqlite.py` with FTS5 + vector support implementing the new interface
- Add settings toggle: `MEMORY_BACKEND=faiss|sqlite` (FAISS remains default)
- Migration tool: export FAISS → import SQLite
- Update `MemoryConsolidator` to use backend-agnostic search interface
- Pytest tests for new memory backend
- **Deliverable**: Optional zero-dependency memory backend

### Phase 2: Security Enhancements (2-3 days)
- Encrypted secrets vault (replace plaintext `.env` for sensitive keys; current system is file-based with streaming masking via `SecretsManager` but no encryption at rest)
- MCP client pairing flow (one-time code exchange; currently only static token-based auth via `create_auth_token()`)
- Audit logging for tool executions
- **Deliverable**: Hardened security model

### Phase 3: Channel Bridge (2-3 days)
- **Prerequisite**: Concurrent API handling (completed)
- Configure ZeroClaw channels (Telegram, Discord, or Slack)
- Set up ZeroClaw → Agent Zero bridge using `/api_message_async` + `/api_message_status` (non-blocking)
- Add channel-specific context handling
- Test end-to-end: Message on Telegram → ZeroClaw → Agent Zero → response → Telegram
- **Deliverable**: Agent Zero accessible via messaging platforms

### Phase 4: Rust Tool Sidecar (1-2 days)
- Add ZeroClaw Docker container to `docker-compose.yml`
- Configure ZeroClaw MCP server
- Add ZeroClaw as MCP tool provider in Agent Zero settings
- Test basic tool delegation (shell, file, git operations)
- **Deliverable**: Agent Zero can use ZeroClaw tools via MCP

---

## Risks and Considerations

1. **Rust ↔ Python boundary**: Communication overhead via MCP/A2A adds latency. Only worth it for operations where Rust's speed matters.
2. **ZeroClaw maturity**: As a newer framework, API stability is uncertain. Pin to specific versions.
3. **Resource usage**: Adding ZeroClaw sidecar increases container footprint (~50MB RAM).
4. **OAuth token policy**: Anthropic updated OAuth token terms 2026-02-19 restricting Claude Code tokens to official use. Verify ZeroClaw's Claude provider compliance.
5. **Maintenance burden**: Two agent frameworks to maintain. Use sidecar pattern to keep them loosely coupled.
6. **Memory abstraction effort** (added in revision): FAISS coupling is deeper than initially assessed. The `Memory` class directly uses `MyFaiss` subclass, `InMemoryDocstore`, and FAISS-specific serialization (`index.faiss`/`index.pkl`). Abstracting this is a prerequisite for any alternative backend.

## Completed Prerequisites

| Prerequisite | Archon Task | Date | Impact |
|-------------|------------|------|--------|
| Concurrent API request handling | 835f888b | 2026-02-20 | Enables Phase 3 (Channel Bridge) — multiple channel users can send requests without blocking. New endpoints: `/api_message_async`, `/api_message_status`. |
| Documentation for ZeroClaw integrators | cb5395d4 | 2026-02-20 | Async endpoints documented in connectivity.md and AGENT_ZERO_FOR_ZEROCLAW_INTEGRATORS.md |

---

## Agent Zero's Feedback (2026-02-20)

Agent Zero read this analysis via `document_query` and `code_execution_tool` and provided its prioritized assessment:

**Agent Zero's Top 3 Priorities (in order):**

1. **SQLite Hybrid Memory** (HIGH) — "Replacing or augmenting Agent Zero's memory system could significantly improve performance and reduce external dependencies."
2. **Security Model** (HIGH) — "ZeroClaw's pairing codes, sandboxing policies, and encrypted secrets vault could enhance Agent Zero's security posture."
3. **Channel System** (MEDIUM) — "Integrating ZeroClaw's Telegram, Discord, Slack, and Matrix channels would expand Agent Zero's communication capabilities."

**Agent Zero's Conflict Assessment:**
- Memory integration may require significant modifications to existing memory management code
- Security model changes may affect authentication and authorization mechanisms

**Notable difference from our analysis**: Agent Zero prioritized Security (#2) above Channels (#3), while our initial ranking had Channels as #1. Agent Zero's reasoning is sound — security hardening has broader architectural impact and should precede channel expansion.

### Revised Priority Order (incorporating Agent Zero feedback)

| Priority | Integration | Value | Effort | Phase |
|----------|------------|-------|--------|-------|
| **1** | SQLite Hybrid Memory | HIGH | HIGH | Phase 3 → **Phase 1** |
| **2** | Security Hardening | HIGH | MEDIUM | Phase 4 → **Phase 2** |
| **3** | Channel Bridge | HIGH | MEDIUM | Phase 2 → **Phase 3** |
| **4** | Rust Tool Sidecar | MEDIUM | LOW | Phase 1 → **Phase 4** |

### Cursor's Contribution (2026-02-20)

Cursor independently created [docs/AGENT_ZERO_FOR_ZEROCLAW_INTEGRATORS.md](../docs/AGENT_ZERO_FOR_ZEROCLAW_INTEGRATORS.md) documenting:
- REST API (`POST /api_message`), MCP (SSE/HTTP), and A2A entry points for ZeroClaw integrators
- Authentication patterns (X-API-KEY header, token in MCP/A2A URLs)
- Integration constraints (rate limits, context lifetime, HTTP vs HTTPS)

---

## References

- ZeroClaw GitHub: github.com/zeroclaw-labs/zeroclaw
- ZeroClaw Docs: zeroclaw.bot
- Agent Zero Architecture: See `PLANNING.md` and codebase at `/Users/james/Docker/AgentZ`
- Archon Project: A0 SIP (ID: 610ae854-2244-4cb8-a291-1e31561377ab)

---

## Revision History

### Revision 1 (2026-02-20)

**Trigger:** Post-implementation analysis — concurrent API feature completed, codebase deep-dive into memory and security systems revealed plan gaps.

**Root causes:**
1. Phase ordering contradicted the revised priority table (Agent Zero's feedback was captured but phases weren't reordered)
2. Channel Bridge plan assumed blocking `/api_message` — would have caused the same 2+ minute timeout issues we solved
3. SQLite Memory effort underestimated — FAISS is tightly coupled with no abstraction layer (no `MemoryBackend` interface)
4. Status field was stale (said "In Progress" but research was complete)

**Changes:**
- Reordered phases to match revised priority: Memory → Security → Channels → Sidecar
- Added prerequisite link to concurrent API feature (Archon 835f888b) — Channel Bridge now uses `/api_message_async`
- Added "Gotchas" to SQLite Memory section: FAISS coupling, need for abstraction layer (Step 0)
- Revised SQLite Memory estimate from 3-5 days to 5-8 days
- Added "Completed Prerequisites" section tracking concurrent API and documentation work
- Added Risk #6: Memory abstraction effort
- Updated status to "Research Complete — Implementation Not Started"
- Marked original phase ordering as superseded
