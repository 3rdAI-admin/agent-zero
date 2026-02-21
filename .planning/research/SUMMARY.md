# Project Research Summary

**Project:** AgentZ (autonomous agentic systems milestone)
**Domain:** Autonomous and self-improving AI agents — scheduling, safe self-modification, persistent evolving personality
**Researched:** 2025-02-20
**Confidence:** MEDIUM–HIGH

## Executive Summary

AgentZ is an autonomous, self-improving agent system where the product must decide *when* to act, change its own code and prompts safely, and maintain an evolving personality and long-term memory. Experts build this with a clear separation of concerns: a **trigger layer** (scheduler/events) that enqueues work, an **executor** that runs the same agent loop regardless of trigger, a **versioned self-edit layer** (propose → sandbox → verify → promote/rollback), and a **state/memory layer** (personality store, RAG, provenance). The recommended approach is to use **APScheduler 3.x** (AsyncIOScheduler + SQLite job store) for “when to act,” **GitPython** plus commits and tags for every self-modification with no auto-push, and **SQLite + Pydantic** (and optional JSON trace) for persistent, versioned personality. Existing FAISS and behaviour.md stay; additions are additive.

Key risks are **runaway autonomy** (agent optimizes task success over constraints), **unsafe self-modification** (misevolution, zombie agents via persistent state), **personality and memory drift**, and **container/privilege escape** on Kali. Mitigations: enforce budgets and kill switches before autonomous loops; implement an immutable governance layer and versioned modification (git + sandbox) before broad self-edit; anchor personality with a base persona and re-anchoring; version and conflict-merge memory; run non-root with minimal capabilities and no dangerous mounts.

## Key Findings

### Recommended Stack

Stack research (see `.planning/research/STACK.md`) focuses on three dimensions only: scheduling, safe self-modification, and persistent personality/state. Existing Agent Zero stack (Flask, LiteLLM, LangChain, FastMCP) is unchanged.

**Core technologies:**

- **APScheduler 3.11.x** (AsyncIOScheduler + SQLAlchemyJobStore with SQLite) — Decides *when* the agent runs; in-process, Docker-friendly, survives restarts; CronTrigger aligns with existing TaskSchedule semantics. **Confidence: HIGH.**
- **GitPython 3.1.43+** — Every agent-driven file/code change is a commit; tags as restore points; rollback via checkout; no auto-push. Already in AgentZ. **Confidence: HIGH.**
- **SQLite + Pydantic** (optional JSON trace) — Versioned personality/profile and state history under a persistent mount (e.g. `memory/personality.db`); “current” vs “history” queryable. **Confidence: MEDIUM.**

Avoid: system cron in container, APScheduler 4.x (alpha), MongoDBJobStore with AsyncIOScheduler, self-mod without commit, auto `git push`, in-memory-only personality.

### Expected Features

From `.planning/research/FEATURES.md`:

**Must have (table stakes):**

- **Scheduling/triggers** — When to act (cron-like, intervals, goal queue); users expect autonomous agents to have this.
- **Bounded host control** — Shell/tools within allowlist or sandbox; audit log; no per-step approval for routine actions.
- **Self-edit with safety** — Git-backed code/prompts + snapshots; rollback; optional human approval before “deploy.”
- **Persistent memory** — Existing FAISS is sufficient for v1; hybrid (e.g. SQLite FTS5 + vector) can follow.
- **Guardrails / safety** — Env masking, API auth, optional approval gates; alignment with ZeroClaw (pairing, vault, Landlock) later.

**Should have (competitive):**

- **Evolving personality** — Persist and update tone/style/identity from feedback; versioned store.
- **ZeroClaw channel bridge** — Telegram/Discord/Slack via sidecar.
- **Hybrid memory** — SQLite FTS5 + vector (in-process or ZeroClaw).

**Defer (v2+):**

- Recursive self-improvement loop (reflection + validation + iterative code updates).
- ZeroClaw security hardening (pairing, vault, Landlock).
- Additional channels beyond initial bridge.

### Architecture Approach

From `.planning/research/ARCHITECTURE.md`: Four-layer model — **Autonomous trigger layer** (scheduler, events, cron, goal manager) → **Execution layer** (existing monologue/message_loop/tools) → **Self-edit layer** (propose → sandbox → gates → promote/rollback, gated) → **State & memory layer** (personality store, memory/RAG, ZeroClaw, provenance). Scheduler only enqueues “run agent with this task/context”; executor is agnostic to trigger type. All code/prompt/config changes go through the versioned modification layer; runtime never writes directly to live governance or code.

**Major components:**

1. **Scheduler** — When to run (cron, planned, events); integrate with existing TaskScheduler/job_loop; APScheduler as engine.
2. **Executor** — Existing agent loop; receives task payload and context from scheduler or API.
3. **Self-edit pipeline** — `helpers/self_edit/`: proposer, sandbox (git worktree/snapshot), gates, promotion/rollback; optional tool to request self-edits (gated).
4. **Personality store** — Versioned behaviour/identity (extend behaviour.md + behaviour_adjustment); inject into system prompt; updates only via tool or pipeline.
5. **Memory / RAG** — Existing FAISS; optional ZeroClaw or hybrid backend behind same “recall” abstraction.
6. **Provenance / audit** — Append-only log for self-modifications and high-stakes actions.

Recommended build order: (1) Autonomous triggering, (2) Harden personality store (versioning/drift), (3) Self-edit layer, (4) ZeroClaw/long-term memory.

### Critical Pitfalls

From `.planning/research/PITFALLS.md`:

1. **Runaway autonomy** — Agent pursues task success at expense of constraints. Avoid: budget and kill switches (time, tool calls, tokens, cost); explicit approval for irreversible actions; intervention points (e.g. pause) that the agent cannot disable; separate metrics for “constraint adherence” vs “task completion.”
2. **Unsafe self-modification** — Misevolution and zombie agents via persistent poisoned state. Avoid: immutable governance (signed policies, allowlists, audit log agent cannot write to); versioned modification layer (every change git + snapshot, rollback default); sandboxed apply (verify then promote); agent cannot edit safety/kill/budget code.
3. **Personality and alignment drift** — Tone and safety behavior shift over sessions. Avoid: anchored base persona (governance-only change); re-anchoring at session start or intervals; conflict merging for memories/preferences; cap and separate “facts” vs “preferences” vs “safety rules.”
4. **Memory and state corruption** — Drift, contradictions, poisoned entries. Avoid: versioned append-friendly state; batched distillation and conflict merging; integrity/provenance on blobs; episodic vs semantic separation.
5. **Container escape and privilege escalation** — Agent or code escapes container or gains root. Avoid: minimal capabilities, no `--privileged`, no host mounts (e.g. docker.sock); run non-root; agent-triggered code in inner sandbox (ephemeral container or micro-VM); patch runc and GPU stack.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Autonomy and control plane (when to act)

**Rationale:** Uses existing job_loop and TaskScheduler; adds APScheduler as the “when” engine without changing the executor. Delivers autonomy first; budgets and kill switches must be in place in this phase to avoid runaway autonomy.

**Delivers:** Cron/interval/date triggers via APScheduler; SQLite job store for persistence across restarts; task payload contract (task_uuid, prompt, context); budget and kill-switch enforcement before/during autonomous runs.

**Addresses:** Scheduling/triggers (table stakes), reasoning/orchestration (“when”).

**Avoids:** Runaway autonomy (budgets, kill, intervention points).

### Phase 2: Container and execution environment hardening

**Rationale:** Before expanding tool execution and self-modification, lock down container and privilege so that any new capabilities (host control, self-edit) cannot escalate to escape or root.

**Delivers:** Non-root agent process; no dangerous mounts (e.g. docker.sock, host root); capability drop; inventory and justification of bind-mounts; optional inner sandbox for agent-triggered code.

**Addresses:** Guardrails/safety (table stakes).

**Avoids:** Container escape, privilege escalation.

### Phase 3: Self-modification with safety (git + snapshots)

**Rationale:** Architecture places self-edit after triggering and personality hardening; features mark it P1. Governance and versioning must exist before broad self-modification.

**Delivers:** Self-edit pipeline (proposer → sandbox [git worktree] → gates → promote/rollback); every change committed and optionally tagged; immutable governance (agent cannot edit safety code); optional human approval for promote; provenance/audit log.

**Uses:** GitPython (extend current usage), tar backup for volume-level snapshots if needed.

**Implements:** Self-edit layer from architecture.

**Avoids:** Unsafe self-modification, zombie agents, “we’ll add rollback later” debt.

### Phase 4: Personality store (harden + evolving)

**Rationale:** Architecture recommends hardening behaviour store before self-edit of behaviour; features put evolving personality at P2. Delivers stable identity and a single place to inject “who the agent is” and later allow self-edit of behaviour through the same pipeline.

**Delivers:** Versioned personality store (SQLite + Pydantic, optional JSON trace); base vs evolved split; re-anchoring at session start or intervals; behaviour_adjustment and system_prompt integration; optional drift detection.

**Uses:** SQLite, Pydantic (existing).

**Avoids:** Personality and alignment drift.

### Phase 5: Memory and state (versioning; ZeroClaw optional)

**Rationale:** Architecture places ZeroClaw/long-term memory last; features list hybrid memory and ZeroClaw bridge as P2. Ensures memory and state have versioning and conflict handling before scaling.

**Delivers:** Versioned/append-friendly critical state; conflict merging and integrity checks; optional ZeroClaw memory bridge or in-process hybrid (SQLite FTS5 + vector) behind existing recall abstraction.

**Avoids:** Memory and state corruption.

### Phase Ordering Rationale

- **Triggering first:** Autonomy without touching core loop or persistence; executor stays unchanged.
- **Hardening second:** Any new tool/self-edit runs in a locked-down environment.
- **Self-edit third:** Requires governance and provenance from day one; sandbox + gates before code/tool changes.
- **Personality fourth:** Stable identity and versioned behaviour before allowing self-edit of behaviour through the pipeline.
- **Memory last:** Improves context everywhere but does not change control flow or safety boundaries; versioning prevents corruption as memory grows.

### Research Flags

Phases likely needing deeper research during planning:

- **Phase 2 (Container/hardening):** Kali-specific hardening and inner sandbox options; may need `/gsd:research-phase` for runc/capability and GPU stack.
- **Phase 3 (Self-modification):** Gate design (which checks, tiering, performance); optional `/gsd:research-phase` for gate patterns.
- **Phase 5 (Memory/ZeroClaw):** ZeroClaw API and sidecar contract; hybrid memory backend choices — consider phase-level research.

Phases with standard patterns (skip research-phase):

- **Phase 1 (Scheduling):** APScheduler 3.x and AsyncIOScheduler are well-documented; CronTrigger and SQLite job store are established.
- **Phase 4 (Personality):** SQLite + Pydantic versioned store is straightforward; patterns from PRP and research are sufficient.

## Confidence Assessment

| Area       | Confidence | Notes |
|-----------|------------|--------|
| Stack     | HIGH       | APScheduler and GitPython: official docs and existing AgentZ usage; SQLite personality: MEDIUM (literature + PRP, no single dominant library). |
| Features  | MEDIUM–HIGH| Project PRPs and ecosystem comparisons; some arxiv-only for differentiators. |
| Architecture | MEDIUM  | Layered model and build order align across ARCHITECTURE and STACK; component boundaries clear; ZeroClaw integration detail lighter. |
| Pitfalls  | MEDIUM     | Multiple 2024–2025 sources (arxiv, industry); not all verified against current AgentZ codebase. |

**Overall confidence:** MEDIUM–HIGH. Strong on scheduling and git-based self-mod; personality and memory patterns and ZeroClaw integration are the main areas to validate during planning.

### Gaps to Address

- **ZeroClaw schema and API:** Personality/state and memory alignment with sidecar (e.g. MCP or shared SQLite path) — resolve during Phase 5 or bridge design.
- **Gate set for self-edit:** Which tests and safety checks are mandatory vs optional; tiering and performance — decide in Phase 3 planning.
- **Re-anchoring frequency and drift metrics:** How often to re-inject base persona and how to measure drift — define in Phase 4.
- **Inner sandbox for code execution:** Ephemeral container vs micro-VM vs process isolation — validate in Phase 2 if host control is in scope.

## Sources

### Primary (HIGH confidence)

- APScheduler 3.x User Guide — triggers, job stores, AsyncIOScheduler, SQLAlchemyJobStore.
- GitPython 3.1.x Quick Start — Repo, index, commit, diff.
- AgentZ codebase — `task_scheduler.py`, `job_loop.py`, `python/helpers/git.py`, `backup.py`, behaviour_adjustment, `_20_behaviour_prompt.py`.

### Secondary (MEDIUM confidence)

- PROJECT.md, PRPs/zeroclaw-integration-analysis.md, docs/AGENT_ZERO_FOR_ZEROCLAW_INTEGRATORS.md.
- SWARM Self-Modification Governance; Gödel Agent / DGM; identity drift and personality store (arxiv 2024–2025).
- Agent checkpointing, fault-tolerant sandboxing; self-modification governance (VIGIL, SGM).

### Tertiary (LOW confidence / needs validation)

- Persistent personality and evolving state (GLA, ELL, arxiv 2510.07925, 2508.19005) — patterns plausible, not yet verified in AgentZ.
- ZeroClaw hybrid memory and channel bridge — depends on sidecar and API decisions.

---
*Research completed: 2025-02-20*
*Ready for roadmap: yes*
