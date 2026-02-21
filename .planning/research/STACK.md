# Stack Research

**Domain:** Autonomous agentic systems — scheduling, safe self-modification, persistent evolving personality (milestone add-ons to Agent Zero)
**Researched:** 2025-02-20
**Confidence:** HIGH (scheduling, git); MEDIUM (personality/state patterns)

This document covers **only** the stack dimension for (1) autonomous agent scheduling/triggering, (2) safe self-modification (git + snapshots, rollback), and (3) persistent evolving personality/state. It does not re-research the existing Agent Zero stack (Flask, LiteLLM, LangChain, FastMCP, etc.). Kali/Linux container context is called out where relevant.

---

## 1. Autonomous agent scheduling / triggering (when to act)

### Recommended stack

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **APScheduler** | **3.11.x** (stable) | In-process job scheduler; cron/interval/date triggers | Standard Python scheduler; AsyncIOScheduler fits async Agent Zero; no separate cron daemon in container; single-process, Docker-friendly; CronTrigger matches existing TaskSchedule semantics. |
| **AsyncIOScheduler** | (bundled) | Run jobs on asyncio event loop | Agent core is async; avoids thread/process pool for agent ticks. |
| **SQLAlchemyJobStore** (SQLite) | (bundled) | Persist jobs across restarts | Survives container restarts; no extra service; SQLite URL `sqlite:///tmp/scheduler/jobs.sqlite` fits existing `tmp/scheduler` mount. |

**Confidence:** HIGH — official docs, widely used in Docker/Python apps; SQLite store is the documented persistence choice when PostgreSQL is not required.

### Patterns

- **Trigger choice:** Use **CronTrigger** (or `CronTrigger.from_crontab(expr)`) for “when to act” in line with existing `TaskSchedule.to_crontab()`; use **IntervalTrigger** for heartbeat/polling; **DateTrigger** for one-off planned times.
- **Job defaults:** Set `misfire_grace_time` so missed runs (e.g. container sleep) can run late; set `max_instances=1` (or low) for agent tasks to avoid overlapping runs.
- **Persistence:** Configure one SQLAlchemyJobStore (SQLite) so scheduled jobs survive restarts. Do **not** use MongoDBJobStore with AsyncIOScheduler (known PicklingError with async).
- **Kali/container:** Prefer in-process scheduler over system cron so the container runs one main process and logs stay in app logging; no cron daemon or crontab install required.

### What to keep from current codebase

- **python-crontab (CronTab)** is still useful for **computing next run time** from a cron expression (as in `task_scheduler.py`). Keep it for `TaskSchedule.to_crontab()` and `next_run_time` display; optionally drive APScheduler from the same `TaskSchedule` model by converting to CronTrigger.
- Existing **tmp/scheduler** persistence (task state, plans) remains; APScheduler job store is additive (scheduling *when* to run; task execution/state stays in current design).

### What NOT to use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| System cron inside container | Extra daemon, signal/log complexity, not single-process | APScheduler in-process |
| APScheduler 4.x (e.g. 4.0.0a6) in production | Pre-release; API and persistence model still changing | APScheduler 3.11.x |
| MongoDBJobStore with AsyncIOScheduler | PicklingError with async scheduler | SQLAlchemyJobStore (SQLite) or MemoryJobStore for non-persistent |
| Celery Beat | Heavy (broker + worker); overkill for single-container agent | APScheduler |

### Installation (add to existing AgentZ deps)

```bash
pip install apscheduler>=3.10,<4
# SQLAlchemy required for SQLite job store (likely already present)
pip install sqlalchemy
```

---

## 2. Safe self-modification (git + snapshots, rollback)

### Recommended stack

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **GitPython** | **3.1.43+** (e.g. 3.1.46) | Programmatic git: commit, tag, diff, checkout, branch | Already in AgentZ (`python/helpers/git.py`); use for every self-modification: commit before/after, tags as restore points, optional branch-per-change; traceable and scriptable. |
| **Git (CLI)** | System (Kali/Debian) | Underlying git; hooks, `git status`, `git reset` | GitPython wraps it; use CLI for hooks or scripts (e.g. pre-commit checks). |
| **Tar + bind-mount backup** | (existing) | Point-in-time copy of key dirs | Already in `python/helpers/backup.py`; use for volume-level snapshots where host does not provide LVM/ZFS. |

**Confidence:** HIGH for GitPython (official docs, already integrated); MEDIUM for “shadow repo” pattern (Gemini-style) as optional extra.

### Patterns

- **Every change is a commit:** Before applying agent-driven file/code changes: `repo.index.add(...)`, `repo.index.commit("message")` with deterministic message (e.g. task id + timestamp). Tag significant restore points: `repo.create_tag("restore-YYYYMMDD-HHMM", ref=repo.head.commit)`.
- **Restore = checkout:** Rollback by `repo.git.checkout("restore-<tag>")` or `repo.head.reference = repo.tags["restore-..."]` plus checkout; document in a small “restore” API used by tools or UI.
- **Optional branch-per-modification:** For riskier changes, create a branch, apply there, run checks; merge to main only after validation (Geneclaw-style); rollback = discard branch and checkout main.
- **Never auto-approve destructive git:** Do not auto-approve `git push`, `git reset --hard`, or `rm` of repo paths; require explicit user/operator approval for those (safe autonomy boundary).
- **Snapshots in container:** Typical Kali Docker does not expose LVM/ZFS/btrfs to the container. Use **git as the primary snapshot mechanism** (commits + tags). For full volume snapshots, keep using tar-based backup to a bind-mounted dir; host-level LVM/btrfs is an operator option outside the container.

### What NOT to use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Self-modification without git commit | No traceability, no rollback | Always commit (and optionally tag) after changes |
| Auto `git push` | Risk of leaking or overwriting remote | Push only with explicit approval |
| Relying on LVM/ZFS inside container | Not standard in default Kali Docker images | Git + tar backup; host-level snapshots if operator controls host |
| Custom “versioning” instead of git | Reinventing history and merge | Use GitPython + tags |

### Kali/Linux container notes

- Git is available in Debian/Kali base images; GitPython uses it. No extra system package required for basic commit/tag/checkout.
- For host-level snapshots (e.g. LVM on host volume), document as an ops option; not part of the in-container stack.

---

## 3. Persistent evolving personality / state

### Recommended stack

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **SQLite** | 3 (stdlib or via sqlite3) | Persist personality/profile and state history | Single file, no server; fits bind mount (`./memory` or dedicated path); versioned rows or separate table for “personality revisions”; queryable for “current” vs “history”. |
| **JSON files** | — | Optional: human-readable trace of personality changes | Store snapshots of profile (tone, style, name, rules) with timestamp; aligns with “traceable evolution” (e.g. GLA-style Reflect-Evolve); can be generated from SQLite or be primary for minimal MVP. |
| **Existing FAISS + memory** | (current) | Vector memory, RAG | Keep; personality “state” is separate from vector memory; ZeroClaw hybrid (SQLite + vector) can sit alongside. |
| **Pydantic** | (existing) | Model for personality schema | Define `PersonalityProfile` (name, tone, style, constraints, version, updated_at); serialize to SQLite/JSON. |

**Confidence:** MEDIUM — patterns from 2025 literature (persistent memory + user profiles; traceable JSON evolution) and from ZeroClaw PRP; no single dominant “personality store” library; SQLite + Pydantic is a standard, low-friction choice.

### Patterns

- **Personality as versioned record:** One row (or one JSON file) per “revision”; “current” = latest or a chosen revision; evolution = new row/file with reason (e.g. “feedback: user asked for more formal tone”).
- **Feedback loop:** When experience or user feedback says “change tone/style”, run validation (e.g. rules or LLM check), then write new personality revision and persist; optional “approval” step before making current.
- **ZeroClaw integration:** PRP describes hybrid memory (SQLite + vector). Use SQLite for structured personality and state; keep FAISS for vector memory; when ZeroClaw sidecar is used, align personality/state storage with whatever schema ZeroClaw expects (e.g. MCP or shared SQLite path).
- **Where to store:** Under existing persistent mount (e.g. `memory/` or `tmp/`) so it survives restarts: e.g. `memory/personality.db` and `memory/personality_history/` for JSON traces.

### What NOT to use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Only in-memory personality | Lost on restart; no evolution history | SQLite or JSON on disk under mounted dir |
| New heavy DB (Postgres/Redis) for personality only | Operational overhead in single-container agent | SQLite |
| Unversioned single “personality” file | No rollback, no audit trail | Versioned rows or dated JSON files |

### Installation

No new dependencies required for SQLite (stdlib) or JSON. Use existing Pydantic. If you add an ORM later (e.g. for ZeroClaw alignment), SQLAlchemy is already in the stack for APScheduler job store.

---

## Summary table (new / extended capabilities only)

| Dimension | Recommended | Version | Confidence |
|----------|-------------|---------|------------|
| Scheduling (when to act) | APScheduler + AsyncIOScheduler + SQLAlchemyJobStore (SQLite) | 3.11.x | HIGH |
| Safe self-modification | GitPython (extend current usage) + git commits/tags + optional tar backup | 3.1.43+ | HIGH |
| Persistent personality/state | SQLite + Pydantic + optional JSON trace | — | MEDIUM |

---

## Alternatives considered

| Category | Recommended | Alternative | Why not |
|----------|-------------|-------------|---------|
| Scheduling | APScheduler | System cron in container | Extra daemon, worse for single-process Docker |
| Scheduling | APScheduler 3.x | APScheduler 4.x | 4.x still alpha; persistence model in flux |
| Self-modification | GitPython + tags | Custom versioning | Git is standard and toolable |
| Snapshots | Git + tar | LVM/ZFS in container | Not standard in default Kali Docker |
| Personality store | SQLite + JSON | ChromaDB only | ChromaDB is for vector search; personality is structured and versioned |

---

## Version compatibility

| Package | Compatible with | Notes |
|---------|-----------------|-------|
| APScheduler 3.11.x | Python 3.8+ | AgentZ uses 3.11; no conflict |
| GitPython 3.1.x | Git 2.x | Kali/Debian ship Git 2.x |
| SQLite (stdlib) | Python 3.x | No extra package |

---

## Sources

- APScheduler 3.x User Guide — triggers, job stores, AsyncIOScheduler, SQLAlchemyJobStore: https://apscheduler.readthedocs.io/en/stable/userguide.html
- APScheduler 3.x stable (3.11.2); 4.0.0a6 pre-release: PyPI / version history
- GitPython 3.1.46 Quick Start — Repo, index, commit, diff: https://gitpython.readthedocs.io/en/stable/quickstart.html
- Agent checkpointing / safe self-modification (Geneclaw, Gemini CLI checkpointing): Web search 2025
- Docker/containerd snapshotters (LVM, btrfs, ZFS): Docker docs; “Comparing containerd Snapshotters” (Medium)
- Persistent personality / evolving state (GLA, ELL, persistent memory + user profiles): arxiv 2510.07925, 2508.19005; Web search 2025
- AgentZ codebase: `.planning/codebase/STACK.md`, `python/helpers/git.py`, `python/helpers/task_scheduler.py`, `python/helpers/backup.py`, `PRPs/zeroclaw-integration-analysis.md`

---
*Stack research for: Autonomous agent scheduling, safe self-modification, persistent evolving personality (AgentZ milestone)*  
*Researched: 2025-02-20*
