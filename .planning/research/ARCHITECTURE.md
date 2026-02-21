# Architecture Research: Autonomous Self-Improving Agent Systems

**Domain:** Autonomous and self-improving agent systems (when/how to act, safe self-modification, evolving personality, long-term memory)
**Researched:** 2025-02-20
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AUTONOMOUS TRIGGER LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  Scheduler  │  │   Events    │  │   Cron/      │  │   Goal      │       │
│  │  (when)     │  │  (triggers) │  │   Planned   │  │   Manager   │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         │                │                │                │              │
├─────────┴────────────────┴────────────────┴────────────────┴──────────────┤
│                          EXECUTION LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  Executor (agent loop: monologue → message_loop → tools → response)  │  │
│  │  Extensions: system_prompt, message_loop_*, tool_execute_*, etc.     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                     SELF-EDIT LAYER (optional, gated)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  Propose    │→ │  Sandbox/   │→ │  Verify &   │→ │  Promote /   │       │
│  │  (diffs)    │  │  Git        │  │  Gates      │  │  Rollback    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
├─────────────────────────────────────────────────────────────────────────────┤
│                          STATE & MEMORY LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Personality │  │  Memory /    │  │  ZeroClaw /  │  │  Provenance  │    │
│  │  Store       │  │  RAG         │  │  Long-term   │  │  (audit)     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Scheduler** | Decides *when* the agent runs (cron, planned times, idle/wake). | Cron + planned-task queue; tick loop (e.g. `job_loop.scheduler_tick()`). |
| **Executor** | Runs the agent loop: prompt build → LLM → tool dispatch → response/break_loop. | Single “monologue” loop with inner “message_loop” and tool execution. |
| **Self-edit layer** | Proposes, sandboxes, verifies, and promotes code/prompt/config changes; enables rollback. | Versioned worktree or snapshots; gates (tests, safety checks); promotion/rollback state machine. |
| **Personality store** | Holds evolving identity/behaviour (rules, style, constraints) and feeds system prompt. | File or DB (e.g. `behaviour.md`); updated only via tool or controlled pipeline to limit drift. |
| **Memory / RAG** | Short- and long-term context: recall, embeddings, document store. | Vector store + semantic search; optional external memory (ZeroClaw). |
| **Provenance / audit** | Append-only log of who changed what and why; supports rollback and compliance. | Hash-chained log, optional external anchoring; immutable outside agent runtime. |

## Recommended Project Structure (AgentZ)

Existing layout; additions for autonomy and self-improvement:

```
python/
├── helpers/
│   ├── task_scheduler.py    # Scheduler: cron + planned + adhoc (existing)
│   ├── job_loop.py          # Tick loop that drives scheduler (existing)
│   ├── extension.py         # Extension points (existing)
│   └── self_edit/           # NEW: self-modification pipeline
│       ├── proposer.py      # Propose diffs (prompts, tools, config)
│       ├── sandbox.py       # Git worktree / snapshot, run tests
│       ├── gates.py         # Verification and safety gates
│       └── promotion.py     # Promote / rollback state machine
├── extensions/              # Existing hooks
│   ├── system_prompt/       # _20_behaviour_prompt.py = personality inject
│   ├── message_loop_*/
│   └── monologue_*/
├── tools/
│   ├── scheduler.py         # Tool: schedule/plan/run tasks (existing)
│   ├── behaviour_adjustment.py  # Tool: update behaviour.md (existing personality)
│   └── self_edit_tool.py    # NEW: optional tool to request self-edits (gated)
agents/                      # Profile-specific extensions (existing)
memory/                      # Per-profile: behaviour.md, memory DB (existing)
tmp/scheduler/               # TaskScheduler persistence (existing)
.planning/research/          # This document
```

### Structure Rationale

- **Scheduler + job_loop:** Keep “when to act” in one place; executor stays unaware of trigger source (cron vs event vs API).
- **Self-edit in helpers/self_edit/:** Isolated from the main agent loop; all mutations go through proposer → sandbox → gates → promotion so the runtime never writes directly to live code/policy.
- **Personality store:** Already implemented as `memory/<profile>/behaviour.md` + `behaviour_adjustment` tool + `_20_behaviour_prompt`; extend with versioning/drift detection if needed.
- **ZeroClaw:** Integrate as another memory backend (long-term, possibly external); same “recall” abstraction as existing memory/RAG.

## Architectural Patterns

### Pattern 1: Scheduler–Executor Decoupling

**What:** Scheduler only enqueues “run agent with this task/context”; executor runs the same loop whether triggered by user, cron, or event.
**When to use:** Any autonomous or scheduled agent.
**Trade-offs:** Clear separation of “when” vs “what”; executor stays reusable and testable without time/event logic.

**Example (AgentZ):**
- `job_loop.run_loop()` calls `scheduler_tick()`; `TaskScheduler.tick()` starts tasks whose time has come and runs them (e.g. via `DeferredTask` / existing run path). Executor is the existing `Agent.monologue()` + tools.

### Pattern 2: Versioned Modification Layer (Self-Edit)

**What:** All agent-driven code/prompt/config changes go through: propose → sandbox (e.g. git worktree or snapshot) → verify (tests + safety gates) → promote or rollback. Runtime cannot write directly to governance or live code.
**When to use:** When the agent can change prompts, tools, or config and you need safety and rollback.
**Trade-offs:** Enables recursive self-improvement (Gödel-style) with bounded risk; adds latency and complexity. SWARM-style: immutable governance, compositional safety monitor, versioned modification layer, mutable runtime only via that layer.

**Example (conceptual):**
```python
# Self-edit flow: propose → sandbox → gates → promote
async def apply_self_edit(agent, change_spec):
    with sandbox_worktree() as worktree:
        apply_diff(worktree, change_spec)
        if not await run_gates(worktree):  # tests + safety
            return Rejected(worktree.log)
        return await promote(worktree)  # or rollback on failure
```

### Pattern 3: Personality Store as Explicit State

**What:** Persist “who the agent is” (rules, style, constraints) in a dedicated store; inject into system prompt every turn. Updates only via a defined path (e.g. behaviour_adjustment tool or controlled pipeline) to reduce identity drift.
**When to use:** When you want consistent personality over long conversations; research shows LLMs drift without explicit state.
**Trade-offs:** Reduces drift; requires versioning/auditing if the agent can change it.

**Example (AgentZ):** `behaviour.md` + `read_rules(agent)` in `_20_behaviour_prompt`; `UpdateBehaviour` tool calls `update_behaviour()` (LLM merge). For “evolving personality,” keep this and add optional versioning or drift checks.

## Data Flow

### Autonomous Trigger → Execution

```
[Scheduler.tick() / Event / API]
    ↓
Enqueue task (task_uuid, prompt, context)
    ↓
Executor: Agent.monologue() with task context
    ↓
message_loop: prepare_prompt → get_system_prompt (includes personality) → call_chat_model → process_tools
    ↓
Tool result (e.g. break_loop=True) → return to scheduler/caller
```

### Self-Edit Flow

```
[Agent or tool requests change]
    ↓
Proposer: produce diff (prompts/tools/config)
    ↓
Sandbox: apply in worktree/snapshot; run tests
    ↓
Gates: safety checks, policy tier, capacity cap (optional)
    ↓
Promote: merge to live / tag snapshot — or Rollback
    ↓
Provenance: append-only log (who, what, when, result)
```

### Personality and Memory

```
System prompt build:
  message_loop_prompts_before → get_system_prompt() → behaviour (personality) + base system
  → message_loop_prompts_after (e.g. recall memories, datetime)
  → history + extras → LLM

After turn:
  monologue_end extensions (e.g. memorize fragments)
  behaviour_adjustment tool (if invoked): read_rules → LLM merge → write behaviour.md
```

### Key Data Flows

1. **Trigger → run:** Scheduler or event produces a task; executor runs the same agent loop with that task’s prompt/context.
2. **Self-edit:** Propose → sandbox → verify → promote/rollback; provenance log is append-only and outside agent write path.
3. **Personality:** Read from store at prompt build; write only via behaviour tool or dedicated pipeline.

## Build Order for Adding to an Existing Agent Framework

Recommended order so each step is usable and the next builds on it without rework:

| Order | Component | Rationale |
|-------|-----------|-----------|
| 1 | **Autonomous triggering** | Use existing TaskScheduler + job_loop; add event-driven triggers (e.g. webhooks, queue) so “when” is rich. Executor unchanged. |
| 2 | **Personality store (harden)** | AgentZ already has behaviour.md + behaviour_adjustment. Add versioning or drift detection so “evolving personality” is observable and rollbackable. |
| 3 | **Self-edit layer** | Add proposer → sandbox (git/snapshots) → gates → promote/rollback. Start with prompts/behaviour only; then optional tool/config. Keeps safety before broader self-modification. |
| 4 | **ZeroClaw / long-term memory** | Integrate as memory backend; same “recall” abstraction as existing RAG. Improves context for both user and autonomous runs. |

**Phase ordering rationale:**

- Triggering first: autonomy without touching the core loop or persistence.
- Personality next: stable identity and a single place to inject “who the agent is” before any self-edit of behaviour.
- Self-edit third: needs governance and provenance from day one; sandbox + gates before allowing code/tool changes.
- ZeroClaw last: improves context everywhere but does not change control flow or safety boundaries.

**Implications for roadmap:**

- Phase “Autonomy (when + how)” should cover scheduler + event triggers and clarify executor interface (task payload, context).
- Phase “Self-modification with safety” should map to self_edit layer + provenance; “evolving personality” can be behaviour store + optional self-edit of behaviour.md through the same pipeline.
- Phase “ZeroClaw memory” should define the memory API and where it plugs into message_loop_prompts_after / recall.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|---------------------------|
| Single agent, few tasks | Current design suffices: one scheduler, one executor, file-based personality and memory. |
| Many scheduled/event tasks | Queue tasks; executor pool or single executor with task queue; ensure scheduler tick and task run are non-blocking. |
| Self-edit at scale | Staged rollout (shadow → canary → full); per-agent or per-tier modification caps (e.g. SWARM-style K_max); provenance and rollback automated. |

### Scaling Priorities

1. **First bottleneck:** Scheduler tick and task execution blocking the main process. Mitigate: run tick in background (already in job_loop); run heavy tasks in worker or subprocess.
2. **Second bottleneck:** Self-edit gates and tests slowing promotions. Mitigate: parallel gate runs; cache test results; tiered gates (fast mandatory checks first).

## Anti-Patterns

### Anti-Pattern 1: Executor Knows Trigger Type

**What people do:** Branch inside the agent loop on “cron vs user vs event.”
**Why it's wrong:** Duplicates logic and makes the loop harder to test and extend.
**Do this instead:** Scheduler (or event adapter) normalizes to “run with this task/context”; executor only sees “current task and message.”

### Anti-Pattern 2: Agent Writes Directly to Live Code or Policy

**What people do:** Let the agent write to the same files that the running process uses for prompts/tools/config.
**Why it's wrong:** No rollback, no audit, high risk of broken or unsafe state.
**Do this instead:** All such changes go through a versioned modification layer (sandbox → gates → promote); runtime reads only from promoted/approved state.

### Anti-Pattern 3: Personality Only in Prompt Text, No Persistent Store

**What people do:** Put “you are X” in the system prompt with no persisted, updatable state.
**Why it's wrong:** Identity drifts over long conversations; no way to evolve or revert.
**Do this instead:** Maintain a personality store (e.g. behaviour.md) and inject it into the system prompt; update only via a defined path (tool or pipeline).

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| ZeroClaw / long-term memory | Same interface as existing memory/RAG (e.g. recall by query); optional backend swap or hybrid. | Keep recall API stable; add adapter for ZeroClaw. |
| Event sources (webhooks, queues) | Scheduler or separate “trigger adapter” turns events into tasks and enqueues them; executor unchanged. | Ensure idempotency and backoff for external triggers. |
| Git / snapshot backend | Self-edit sandbox uses worktree or snapshot API; promote = merge or copy to “live” tree. | Prefer read-only live tree; writes only in sandbox. |

### Internal Boundaries (AgentZ)

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Scheduler ↔ Executor | Task payload (prompt, context, task_uuid); executor runs monologue with that context. | Already via TaskScheduler and task run path; clarify task contract. |
| Executor ↔ Extensions | call_extensions(extension_point, …); extensions read/write loop_data, history, agent. | Self-edit must not be triggered by a normal extension without going through the modification layer. |
| Self-edit ↔ Runtime | Reads live config/prompts; writes only to sandbox; after promote, runtime sees new files on next load. | No direct write from agent process to governance or live code. |
| Personality store ↔ Executor | Read in system_prompt extension; write via behaviour_adjustment tool (and optionally self_edit pipeline). | Single source of truth for “current behaviour”; version if evolving. |

## Sources

- Gödel Agent: Self-Referential Agent Framework for Recursive Self-Improvement (arXiv:2410.04444, 2024).
- SWARM Self-Modification Governance (swarm-ai.org); four-layer architecture: immutable governance, compositional safety monitor, versioned modification layer, runtime mutability envelope.
- Modular agentic architectures: planner, executor, memory, goal manager, verifiers (e.g. arXiv:2310.00194, agentic AI surveys 2024).
- Identity drift in LLM agents (arXiv:2412.00804); personality store as explicit state to reduce drift.
- Darwin Gödel Machine / Statistical Gödel Machine: self-modification with sandboxing and validation (arXiv 2024–2025).
- AgentZ codebase: agent.py (monologue, message_loop, process_tools), task_scheduler.py, job_loop.py, extension.py, behaviour_adjustment.py, system_prompt/_20_behaviour_prompt.py.

---
*Architecture research for: autonomous self-improving agents (AgentZ milestone)*  
*Researched: 2025-02-20*
