# Penetration Testing ROE — Agent Zero & Archon

This document states how the **Penetration Testing Rules of Engagement (ROE)** apply to **Agent Zero** and **Archon** when used together or separately for security engagements.

---

## Full ROE document

**Location:** [PEN_TESTING_ROE.md](./PEN_TESTING_ROE.md)

All penetration testing performed by or coordinated with Agent Zero and/or Archon must follow that ROE (authorization, scope, conduct, and agent-specific rules).

---

## Agent Zero

- **Hacker agent** system prompt includes the ROE summary and instructs the agent to follow it. Full prompt text: `agents/hacker/prompts/agent.system.main.role.md`.
- **Behavior:** Before running any security tool, the agent must validate that targets are in-scope and that authorization/scope has been provided. If no ROE or scope is given, the agent must ask the user.
- **Assessment state:** Engagements use `/a0/usr/projects/{project}/.a0proj/assessment/` for targets, findings, and evidence; scope and ROE apply when recording or testing targets.

---

## Archon

- **Task and workflow context:** When using Archon (e.g. via MCP at `http://<host>:8051/mcp`) for task management or project context, treat the ROE as **governing policy** for any penetration-testing or security-assessment tasks.
- **References:** Project planning points to the ROE in [PLANNING.md](../../PLANNING.md) (Governance & security). When creating or executing tasks that involve scanning, exploitation, or security testing, ensure the ROE is followed (written authorization, defined scope, no out-of-scope targets).
- **Single source of truth:** The canonical ROE is [PEN_TESTING_ROE.md](./PEN_TESTING_ROE.md). Archon tasks or docs that reference “pen test ROE” or “security engagement rules” should link to that file.

---

## Summary

| System    | How ROE is shared |
|-----------|--------------------|
| **Agent Zero** | ROE summary in hacker agent system prompt; full doc at `docs/guides/PEN_TESTING_ROE.md`. |
| **Archon**     | ROE linked from PLANNING.md and this file; follow ROE for any pen-test or security-assessment tasks. |

Both systems use the same [PEN_TESTING_ROE.md](./PEN_TESTING_ROE.md) as the single source of truth.
