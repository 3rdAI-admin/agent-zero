# Product Requirements Document (PRD)

**Product / Feature:** Agent Zero Extended Framework (AgentZ)  
**Version:** 1.0  
**Date:** 2025-02-18  
**Status:** Draft

---

## 1. Overview

### 1.1 Purpose
AgentZ is an extended fork of [Agent Zero](https://github.com/agent0ai/agent-zero): a personal, organic agentic AI framework that runs in Docker. This fork adds VNC desktop access, Claude Code integration, OWASP-oriented security tooling, configurable HTTPS/TLS for remote MCP and A2A clients, and enhanced network capabilities so the agent can act as a general-purpose assistant, penetration-testing collaborator, and coding partner while remaining transparent, customizable, and extensible.

### 1.2 Goals
- Provide a single Docker-based runtime that supports Web UI, VNC desktop, and headless/API usage.
- Enable secure remote access (HTTPS with configurable SANs, or HTTP-only mode) for MCP clients (e.g. Cursor) and A2A.
- Integrate Claude Code (e.g. `claude-pro-yolo`) and OWASP-style security tools (nmap, nikto, sqlmap, etc.) for research and security workflows.
- Maintain compatibility with upstream Agent Zero where possible (projects, memory, knowledge, prompts, tools) while documenting fork-specific behavior.

### 1.3 Non-Goals
- Replacing or forking upstream Agent Zero’s core agent loop or default tool set; extensions are additive.
- Hosting or managing third-party MCP servers (e.g. Archon, crawl4ai-rag); AgentZ exposes its own MCP and documents how to connect external ones.
- Long-term divergence of core agent behavior from upstream without clear justification in this PRD or PLANNING.md.

---

## 2. Background & Problem

### 2.1 Problem Statement
Users and security researchers need an agentic framework that can use the full machine (browser, terminal, GUI when required), integrate with modern AI coding tools (e.g. Claude Code), and run security tooling in an isolated environment. Upstream Agent Zero provides the agent core and Web UI but does not ship VNC, Claude Code integration, or a security-focused tool set. Running these separately is brittle and harder to document; a single, well-documented fork reduces setup friction and supports reproducible workflows (e.g. MCP in Cursor, pen-testing with Claude Code + Agent Zero).

### 2.2 User / Stakeholder
- **Primary users:** Developers and security researchers who run Agent Zero in Docker and want VNC, Claude Code, MCP connectivity, and OWASP-style tools in one image.
- **Stakeholders:** Operators who need clear setup docs (QUICK_REFERENCE, COMPLETE_SETUP_GUIDE, connectivity, MCP), and anyone integrating Cursor or other MCP clients with Agent Zero.

---

## 3. Requirements

### 3.1 Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Run Agent Zero Web UI inside Docker, with configurable host port (default 8888). | Must |
| FR-2 | Provide VNC desktop access (e.g. port 5901) for GUI tasks and CAPTCHA completion. | Must |
| FR-3 | Support Claude Code integration (e.g. OAuth, `claude-pro-yolo` wrapper) from inside the container. | Must |
| FR-4 | Expose Agent Zero over HTTPS with configurable LAN IP SANs, or HTTP-only mode, for remote MCP/A2A. | Must |
| FR-5 | Provide health endpoint (HTTP or HTTPS per mode) for orchestration and MCP client checks. | Must |
| FR-6 | Include OWASP-oriented security tools (e.g. nmap, nikto, nuclei, sqlmap, metasploit where applicable) in the image. | Should |
| FR-7 | Document MCP server configuration (URL, transport, Cursor settings) and optional cert trust (e.g. NODE_EXTRA_CA_CERTS). | Must |
| FR-8 | Support Projects: isolated workspaces with own prompts, memory, and secrets. | Must (from upstream) |
| FR-9 | Persist memory, knowledge, logs, and config (e.g. `.env`, `memory/`, `knowledge/`, `logs/`, `tmp/`, `claude-config/`, `claude-credentials/`) via bind mounts or documented paths. | Must |

### 3.2 Non-Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Container runs with documented capabilities (e.g. NET_RAW, NET_ADMIN, SYS_ADMIN) only when required for security tools. | Should |
| NFR-2 | No secrets hardcoded; use `.env` and `python-dotenv`. | Must |
| NFR-3 | Code style: Python (Black, Ruff), type hints, Pydantic, FastAPI; files under 500 lines where practical. | Should |
| NFR-4 | Critical setup and connectivity steps documented (QUICK_REFERENCE, COMPLETE_SETUP_GUIDE, connectivity, MCP docs). | Must |
| NFR-5 | Optional one-time cert export and trust script for self-signed HTTPS (macOS keychain or NODE_EXTRA_CA_CERTS). | Could |

### 3.3 Success Criteria
- [ ] `docker compose up` (or project startup script) brings up Web UI and VNC; health check passes.
- [ ] MCP client (e.g. Cursor) can connect to Agent Zero MCP (HTTP or HTTPS per config) and list tools.
- [ ] Claude Code can authenticate and run inside the container per documented flow.
- [ ] Security tools (e.g. nmap, nikto) are available in the container and documented.
- [ ] New contributors can follow QUICK_REFERENCE and COMPLETE_SETUP_GUIDE to a working setup.

---

## 4. Scope & Constraints

### 4.1 In Scope
- Docker image build (Dockerfile, docker-compose), Web UI, VNC, supervisord process layout.
- HTTP-only mode and HTTPS with configurable SANs; healthcheck and MCP URL documentation.
- Claude Code integration (config mount, OAuth, wrapper); OWASP tool installation and docs.
- Scripts: startup, cert trust, MCP connectivity checks; docs: QUICK_REFERENCE, COMPLETE_SETUP_GUIDE, connectivity, MCP_CLIENT_CONNECTION, MCP_CURSOR_REMEDIATION, DEPLOYMENT_QUICK_START, DOCUMENTATION_INDEX.

### 4.2 Out of Scope
- Changing upstream Agent Zero core agent logic or default tools beyond configuration and extensions.
- Running or maintaining Archon, crawl4ai-rag, or other third-party MCP servers; only documenting how to point Cursor at AgentZ (and optionally others).
- Native (non-Docker) installation as the primary path; documented as alternative only.

### 4.3 Constraints & Assumptions
- **Constraints:** Must run in Docker; upstream base image may change; MCP and A2A clients may require HTTP or HTTPS depending on environment.
- **Assumptions:** Users have Docker and (for Claude Code) valid OAuth; Cursor or other MCP clients are configured per project/user MCP docs.

---

## 5. References & Context

- **Upstream:** [agent0ai/agent-zero](https://github.com/agent0ai/agent-zero)
- **Docs (in repo):** [docs/DOCUMENTATION_INDEX.md](../docs/DOCUMENTATION_INDEX.md), [docs/QUICK_REFERENCE.md](../docs/QUICK_REFERENCE.md), [docs/COMPLETE_SETUP_GUIDE.md](../docs/COMPLETE_SETUP_GUIDE.md), [docs/connectivity.md](../docs/connectivity.md), [docs/MCP_CLIENT_CONNECTION.md](../docs/MCP_CLIENT_CONNECTION.md), [docs/MCP_CURSOR_REMEDIATION.md](../docs/MCP_CURSOR_REMEDIATION.md)
- **Planning:** [PLANNING.md](../PLANNING.md)
- **Related PRDs / PRPs:** [PRPs/agent-zero-extended-framework-prd-compliance.md](../PRPs/agent-zero-extended-framework-prd-compliance.md) – execution plan to verify PRD compliance and run validation gates.

---

## 6. Approval & Next Steps

- **Approved by:** _TBD_
- **Next step:** Review this PRD; for new features, add requirements to INITIAL.md and generate a feature-specific PRD. Then run **`/generate-prp`** (pointing at this PRD or a new one) to create an execution plan with multi-agent task breakdown. Optionally run **`/generate-validate`** to create or update **`/validate-project`** before **`/execute-prp`** → **`/validate-project`** → **`/summarize`**.
