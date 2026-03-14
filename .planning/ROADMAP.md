# Roadmap — AgentZ Autonomous Agent

**Source:** [REQUIREMENTS.md](./REQUIREMENTS.md) (v1) + [research/SUMMARY.md](./research/SUMMARY.md)  
**Last updated:** 2026-03-06

## Overview

This roadmap maps all v1 requirements from REQUIREMENTS.md to phases. Phase order follows research: autonomy first, then container hardening, self-modification, personality, and memory/ZeroClaw. Each phase has clear deliverables and requirement coverage.

## Phases

### Phase 1: Autonomy (when to act)

**Rationale:** Agent decides when to act (schedules, events, goal queue) without changing the executor. Budgets and kill switch are in scope to avoid runaway autonomy.

**Requirements:** AUTON-01, AUTON-02, AUTON-03; SAFETY-01, SAFETY-02

**Deliverables:**

- Cron-like or interval scheduling (e.g. APScheduler + SQLite job store); jobs persist across container restarts.
- Event triggers (webhook, queue, or internal); configurable trigger source.
- Goal queue: explicit tasks/goals enqueued by user or system; executor runs same agent loop for all trigger types.
- Configurable budgets (time, tool calls, tokens, or cost); agent cannot disable.
- Kill switch or pause: user or system can stop an autonomous run; intervention point cannot be removed by agent.

**Dependencies:** None (builds on existing agent loop and job_loop/TaskScheduler patterns).

**Reference:** Research SUMMARY Phase 1; A0 SIP — scheduling/triggers.

---

### Phase 2: Container and execution hardening

**Rationale:** Lock down container and execution before expanding host control and self-modification. Ensures no privilege escalation or escape.

**Requirements:** PLATFORM-01, PLATFORM-02; AUTON-04, AUTON-05, AUTON-06; SAFETY-03

**Deliverables:**

- Agent’s host is a container running Kali Debian arm64; tooling and images support this platform.
- Container runs with minimal capabilities (no `--privileged` by default); agent-triggered code runs in inner sandbox where applicable.
- Agent can run shell commands and tools within safety bounds (allowlist or sandbox); no per-step human approval for routine actions.
- Agent can use GUI (VNC/browser) within same safety bounds; actions audited (e.g. append-only log).
- Bounded host control is configurable (allowlist, deny list, or sandbox policy); agent cannot disable or bypass safety configuration.
- High-stakes and self-modification actions logged in an append-only audit log that the agent cannot write to.

**Dependencies:** None.

**Reference:** Research SUMMARY Phase 2; A0 SIP Phase 2 (Security Enhancements) — vault, pairing, audit logging.

---

### Phase 3: Self-modification (safety)

**Rationale:** All agent-editable code and prompts under version control; every change is a commit; rollback = git revert/checkout. Optional human approval before “deploy.” Governance code is immutable.

**Requirements:** SELF-01, SELF-02, SELF-03, SELF-04, SELF-05

**Deliverables:**

- All agent-editable code and prompts under version control; every change is a commit; rollback = git revert/checkout.
- Before applying self-modifications, system can create a snapshot (e.g. container image or state backup); rollback = restore snapshot when needed.
- Optional human approval gate before “deploy” of agent-written changes (configurable; can be disabled for YOLO flows).
- Agent cannot edit governance/safety code (kill switch, budget checks, approval gate logic); immutable layer enforced.
- Self-edit pipeline: propose → sandbox/verify → promote or rollback; no direct runtime writes to live code or prompts.

**Dependencies:** Phase 2 (audit log and hardened execution).

**Reference:** Research SUMMARY Phase 3.

---

### Phase 4: Personality (persisted and evolving)

**Rationale:** Personality (tone, style, name, identity) is persisted and versioned; can be updated from experience or user feedback; current personality is injected into system prompt consistently.

**Requirements:** PERS-01, PERS-02, PERS-03

**Deliverables:**

- Personality persisted and versioned (e.g. SQLite + Pydantic or behaviour.md + history).
- Personality can be updated from experience or user feedback; updates stored and optionally re-anchored to base persona to limit drift.
- Current personality injected into system prompt; consistent across sessions where intended (no accidental reset).

**Dependencies:** None (can overlap with Phase 3; research recommends personality hardening before self-edit of behaviour).

**Reference:** Research SUMMARY Phase 4.

---

### Phase 5: Memory and ZeroClaw integration

**Rationale:** Existing persistent memory remains; hybrid memory (e.g. SQLite FTS5 + vector) or ZeroClaw-backed memory behind same “recall” abstraction. ZeroClaw bridge for channels and APIs.

**Requirements:** MEMORY-01, MEMORY-02; ZEROCLAW-01, ZEROCLAW-02

**Deliverables:**

- Existing persistent memory (FAISS, bind mounts) remains; agent has long-term recall across sessions.
- (v1.x) Hybrid memory (e.g. SQLite FTS5 + vector) or ZeroClaw-backed memory behind same “recall” abstraction; may land in later sub-phase.
- Integrate ZeroClaw with Agent Zero: design and implement bridge (e.g. sidecar or MCP) for hybrid memory and/or channel (Telegram/Discord/Slack) per PRPs and research.
- Document and support ZeroClaw integration path (APIs, auth, async flow); reuse concurrent API (e.g. `/api_message_async` + status poll) where applicable.

**Dependencies:** Phase 1 (async/API) is done; Phase 2 security improves integration safety.

**Reference:** Research SUMMARY Phase 5; A0 SIP Phase 1 (SQLite Hybrid Memory), Phase 3 (Channel Bridge), Phase 4 (Rust Tool Sidecar).

---

## Traceability: Requirement → Phase

| Requirement | Phase | Description |
|-------------|-------|-------------|
| AUTON-01 | 1 | Schedule (cron-like/interval); jobs persist across restarts |
| AUTON-02 | 1 | Event triggers (webhook, queue, internal); configurable |
| AUTON-03 | 1 | Goal queue; executor same for all trigger types |
| AUTON-04 | 2 | Shell/tools within safety bounds; no per-step approval |
| AUTON-05 | 2 | GUI (VNC/browser) within bounds; audited |
| AUTON-06 | 2 | Bounded host control configurable; agent cannot bypass |
| SELF-01 | 3 | All agent-editable code/prompts under version control |
| SELF-02 | 3 | Snapshot before self-mod; rollback = restore |
| SELF-03 | 3 | Optional human approval before deploy |
| SELF-04 | 3 | Agent cannot edit governance/safety code |
| SELF-05 | 3 | Self-edit pipeline: propose → sandbox → promote/rollback |
| PERS-01 | 4 | Personality persisted and versioned |
| PERS-02 | 4 | Personality updated from experience/feedback; re-anchor |
| PERS-03 | 4 | Current personality in system prompt; consistent |
| MEMORY-01 | 5 | Existing FAISS/mounts; long-term recall |
| MEMORY-02 | 5 | (v1.x) Hybrid memory or ZeroClaw behind recall abstraction |
| ZEROCLAW-01 | 5 | ZeroClaw bridge (sidecar/MCP); memory and/or channels |
| ZEROCLAW-02 | 5 | Document and support ZeroClaw APIs, auth, async |
| SAFETY-01 | 1 | Configurable budgets; agent cannot disable |
| SAFETY-02 | 1 | Kill switch/pause; agent cannot remove |
| SAFETY-03 | 2 | Append-only audit log; agent cannot write |
| PLATFORM-01 | 2 | Container Kali Debian arm64; tooling supports |
| PLATFORM-02 | 2 | Minimal capabilities; inner sandbox where applicable |

---

## Archon task alignment (A0 SIP)

Archon project **610ae854-2244-4cb8-a291-1e31561377ab** tasks are aligned to this roadmap. Use **feature** or **task_order** to filter by phase.

| Roadmap phase | Archon feature         | task_order | Tasks |
|---------------|------------------------|------------|--------|
| **1** Autonomy (when) | roadmap-1-autonomy     | 10 | Roadmap Phase 1: Autonomy (when to act) |
| **2** Container hardening | roadmap-2-security | 20 | Phase 2: Security Enhancements (vault, pairing, audit) |
| **3** Self-modification | (no task yet)          | 30 | — |
| **4** Personality | (no task yet)             | 40 | — |
| **5** Memory & ZeroClaw | roadmap-5-memory, roadmap-5-channels, roadmap-5-sidecar | 51, 52, 53 | Phase 1: SQLite Hybrid Memory; Phase 3: Channel Bridge; Phase 4: Rust Tool Sidecar |

**Suggested execution order by roadmap:** 10 → 20 → 51 → 52 → 53 (then add Phase 3 and Phase 4 tasks when scoped).

---

## Phase order and next steps

1. **Phase 1** — Autonomy (when) + budgets + kill switch  
2. **Phase 2** — Container hardening + host control + audit  
3. **Phase 3** — Self-modification (git + snapshots + pipeline)  
4. **Phase 4** — Personality store (versioned, evolving)  
5. **Phase 5** — Memory + ZeroClaw (hybrid memory, channel bridge, docs)

**Next step:** Execute Roadmap Phase 1 (task_order 10) or break it down with `/gsd:plan-phase` 1.

---
*Generated from REQUIREMENTS.md and research/SUMMARY.md. Archon alignment 2026-03-06. Update when phases or tasks change.*
