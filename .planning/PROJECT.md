# AgentZ Autonomous Agent

## What This Is

An autonomous agent that runs inside a Kali Debian arm64 container, with persistent memory, full control of its host (commands, tools, GUI), the ability to improve itself (including core logic), and a personality that evolves from experience and feedback. It is built by extending Agent Zero (AgentZ) and integrating ZeroClaw for hybrid memory and security-oriented capabilities. The agent decides both **when** to act (schedules, events, goals) and **how** (shell, tools, browser, VNC).

## Core Value

The agent must be able to act autonomously and improve itself **safely**: every self-modification is traceable (git) and recoverable (snapshots). If that guarantee breaks, the system is not acceptable.

## Requirements

### Validated

<!-- Shipped and confirmed in codebase. -->

- ✓ Web UI and REST API (Flask; message, poll, history, async message/status) — existing
- ✓ MCP server at `/mcp` and A2A at `/a2a` — existing
- ✓ Agent context, monologue loop, tool dispatch (code, shell, browser, memory, search, etc.) — existing
- ✓ Projects with isolated prompts, memory, and config — existing
- ✓ Docker runtime: VNC, supervisord, HTTPS/HTTP mode, healthcheck — existing
- ✓ Concurrent API (fire-and-forget + status poll) for integrations — existing
- ✓ Claude Code integration and OWASP-style tools in image — existing
- ✓ Extensions (hooks) and profile-specific tools — existing
- ✓ Memory/knowledge persistence via bind mounts; in-memory vector/RAG (FAISS) — existing
- ✓ Multi-provider LLM (LiteLLM), embeddings, optional browser-use — existing

### Active

<!-- Current scope. Building toward these. -->

- [ ] **Autonomy (when):** Agent decides when to act — triggered by schedules, events, or explicit goals (e.g. job loop, cron-like, or goal queue).
- [ ] **Autonomy (how):** Agent controls host via shell, tools, and GUI (VNC/browser) without requiring approval for every step (within safety bounds).
- [ ] **Full self-modification:** Agent can change core agent logic (prompts, code, tools) with **safety/rollback**: (1) Git-backed — all agent-editable code/prompts under version control; changes are commits; rollback = revert; optional human approval before “deploy”. (2) Snapshots — before applying self-modifications, system creates checkpoint (e.g. image or state backup); rollback = restore.
- [ ] **Evolving personality:** Personality (tone, style, name) can be updated from experience or user feedback; persisted and consistent across sessions where intended.
- [ ] **ZeroClaw integration:** Leverage ZeroClaw with Agent Zero — hybrid memory (e.g. SQLite + vector), security model, and any other agreed capabilities from ZeroClaw research/PRPs.
- [ ] **Kali Debian arm64 host:** Agent’s host is a container running Kali Debian arm64; agent has the capabilities needed to control and improve that environment.

### Out of Scope

- Replacing upstream Agent Zero’s core loop without a clear migration path — extensions and integration are preferred.
- Self-modification without audit trail or rollback — safety is non-negotiable.
- Fixed, non-evolving personality as the long-term design — we want evolution from experience/feedback.
- Running or maintaining third-party MCP servers (e.g. Archon, crawl4ai-rag) inside the agent image — we document how to connect external ones; AgentZ exposes its own MCP.

## Context

- **Brownfield:** AgentZ fork already provides Web UI, VNC, MCP/A2A, concurrent API, tools, extensions, and Docker image. ZeroClaw integration has been researched (PRPs, docs); priorities include SQLite hybrid memory, security hardening, channel bridge.
- **PRD/PRP:** `PRDs/agent-zero-extended-framework.md` and `PRPs/agent-zero-extended-framework-prd-compliance.md` define product scope and verification; Archon A0 SIP project tracks tasks.
- **Codebase map:** `.planning/codebase/` holds STACK, ARCHITECTURE, STRUCTURE, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS for planning.

## Constraints

- **Platform:** Host is a container running Kali Debian arm64; tooling and images must support this.
- **Safety:** Self-modification must be git-backed (code/prompts) and support snapshots for full environment/state rollback; no “unsafe-only” mode for production.
- **Compatibility:** Maintain compatibility with upstream Agent Zero where possible (projects, memory, knowledge, prompts, tools); document fork-specific behavior.
- **Secrets:** No hardcoded secrets; use `.env` and `python-dotenv`.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Autonomy = when + how | Agent should both decide when to act and how (commands, tools, GUI). | — Pending |
| Safety = git + snapshots | Git for code/prompts (audit, revert); snapshots for full state rollback. | — Pending |
| Personality evolves | Personality can be updated from experience or user feedback. | — Pending |
| ZeroClaw + Agent Zero | Leverage ZeroClaw (e.g. hybrid memory) with existing Agent Zero. | — Pending |

---
*Last updated: 2026-02-21 after new-project initialization*
