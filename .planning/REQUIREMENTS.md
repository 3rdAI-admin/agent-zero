# Requirements — AgentZ Autonomous Agent

**Source:** PROJECT.md + research (FEATURES.md, SUMMARY.md)  
**Scope:** v1 — autonomy milestone (when + how, safe self-modification, evolving personality, ZeroClaw)  
**Last updated:** 2026-02-21

## v1 Requirements

### Autonomy (when)

- [ ] **AUTON-01** — Agent can run on a schedule (cron-like or interval); jobs persist across container restarts (e.g. APScheduler + SQLite job store).
- [ ] **AUTON-02** — Agent can be triggered by events (e.g. webhook, queue message, or internal event); trigger source is configurable.
- [ ] **AUTON-03** — Agent can process a goal queue (explicit tasks/goals enqueued by user or system); executor runs same agent loop regardless of trigger type.

### Autonomy (how) — Host control

- [ ] **AUTON-04** — Agent can run shell commands and tools within safety bounds (allowlist or sandbox); no per-step human approval for routine actions.
- [ ] **AUTON-05** — Agent can use GUI (VNC/browser) for tasks within the same safety bounds; actions are audited (e.g. append-only log).
- [ ] **AUTON-06** — Bounded host control is configurable (allowlist, deny list, or sandbox policy); agent cannot disable or bypass safety configuration.

### Self-modification (safety)

- [ ] **SELF-01** — All agent-editable code and prompts are under version control; every change is a commit; rollback = git revert/checkout.
- [ ] **SELF-02** — Before applying self-modifications, system can create a snapshot (e.g. container image or state backup); rollback = restore snapshot when needed.
- [ ] **SELF-03** — Optional human approval gate before “deploy” of agent-written changes (configurable; can be disabled for YOLO flows).
- [ ] **SELF-04** — Agent cannot edit governance/safety code (e.g. kill switch, budget checks, approval gate logic); immutable layer is enforced.
- [ ] **SELF-05** — Self-edit pipeline: propose → sandbox/verify → promote or rollback; no direct runtime writes to live code or prompts.

### Personality

- [ ] **PERS-01** — Personality (tone, style, name, identity) is persisted and versioned (e.g. SQLite + Pydantic or behaviour.md + history).
- [ ] **PERS-02** — Personality can be updated from experience or user feedback; updates are stored and optionally re-anchored to base persona to limit drift.
- [ ] **PERS-03** — Current personality is injected into system prompt; consistent across sessions where intended (no accidental reset).

### Memory & state

- [ ] **MEMORY-01** — Existing persistent memory (FAISS, bind mounts) remains; agent has long-term recall across sessions.
- [ ] **MEMORY-02** — (v1.x) Hybrid memory (e.g. SQLite FTS5 + vector) or ZeroClaw-backed memory behind same “recall” abstraction; in-scope for roadmap, may land in later phase.

### ZeroClaw integration

- [ ] **ZEROCLAW-01** — Integrate ZeroClaw with Agent Zero: design and implement bridge (e.g. sidecar or MCP) for hybrid memory and/or channel (Telegram/Discord/Slack) as per PRPs and research.
- [ ] **ZEROCLAW-02** — Document and support ZeroClaw integration path (APIs, auth, async flow); reuse concurrent API (e.g. `/api_message_async` + status poll) where applicable.

### Safety & guardrails

- [ ] **SAFETY-01** — Autonomous runs have configurable budgets (time, tool calls, tokens, or cost); agent cannot disable budgets.
- [ ] **SAFETY-02** — Kill switch or pause: user or system can stop an autonomous run; intervention point cannot be removed by agent self-edit.
- [ ] **SAFETY-03** — High-stakes and self-modification actions are logged in an append-only audit log that the agent cannot write to.

### Platform

- [ ] **PLATFORM-01** — Agent’s host is a container running Kali Debian arm64; tooling and images support this platform.
- [ ] **PLATFORM-02** — Container runs with minimal capabilities (no `--privileged` by default); agent-triggered code runs in inner sandbox where applicable.

## v2 (deferred)

- Recursive self-improvement loop (reflection + validation + iterative code updates).
- ZeroClaw security hardening (pairing, vault, Landlock).
- Additional channels beyond initial bridge.

## Out of scope

- Self-modification without audit trail or rollback.
- Per-step human approval for every host action (breaks autonomy).
- Replacing upstream Agent Zero core without migration path.
- Running third-party MCP servers inside the agent image (we document connection; AgentZ exposes its own MCP).

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| (Filled by roadmap) | | |

---
*Requirements defined from PROJECT.md and research; traceability updated when roadmap is created.*
