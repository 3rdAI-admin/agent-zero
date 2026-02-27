# Penetration Testing Rules of Engagement (ROE)

**Purpose:** Define authorized scope, boundaries, and conduct for penetration testing with Agent Zero. The hacker/security agent **must** follow these rules. Obtain and document explicit ROE for each engagement before testing.

---

## Authorized engagement target (this project)

**In-scope target for this project:** **`pci.th3rdai.com`**

Penetration testing under this ROE is authorized only for the above target (and any subdomains or URLs explicitly added in writing). All other hosts, IPs, and domains are **out of scope** unless the engagement lead amends the scope in writing. Agent Zero and Archon must treat **pci.th3rdai.com** as the authorized target when validating scope.

---

## 1. Authorization

- **Written authorization required.** Do not scan, probe, or test any system, network, or application without documented authorization from the asset owner or designated authority (e.g. engagement lead, client, or internal stakeholder).
- **Scope document.** Testing must be bounded by a defined scope (targets, IP ranges, domains, applications, and allowed techniques). Anything not explicitly in scope is **out of scope** unless amended in writing.
- **Agent Zero:** Always validate targets are **in-scope** before running any security tool. If no ROE or scope is provided, ask the user for authorization and scope before proceeding.

---

## 2. Scope

### In scope (only if explicitly authorized)

- **Targets:** Only hosts, IP ranges, URLs, or applications listed in the engagement scope.
- **Methods:** Only techniques and tool uses approved in the ROE (e.g. passive recon vs active scanning vs exploitation).
- **Timing:** Only during the agreed testing window (e.g. business hours, maintenance window).

### Out of scope (unless explicitly added in writing)

- Targets or systems not listed in the scope.
- Denial-of-service (DoS) or resource-exhaustion attacks, unless specifically authorized.
- Social engineering against personnel without explicit approval.
- Physical security testing without separate authorization.
- Testing of third-party or cloud assets not covered by the engagement.
- Modifying or deleting data beyond what is needed to demonstrate a finding (prefer read-only proof where possible).

---

## 3. Conduct

- **Minimize impact.** Prefer read-only checks and avoid changing or disrupting production systems. If exploitation is authorized, use the minimum steps needed to prove the finding.
- **Document actions.** Log commands, tools, and targets so activities can be reviewed and reported. Use the assessment state at `/a0/usr/projects/{project}/.a0proj/assessment/` when available.
- **Stop on escalation.** If you discover critical or unexpected risk (e.g. exposure of sensitive data, risk to safety), pause and report to the engagement owner before continuing.
- **Confidentiality.** Treat all findings, credentials, and data as confidential. Do not expose them outside the authorized reporting channel.

---

## 4. Agent Zero–specific rules

- **Validate before testing.** Before running any scan or exploit, confirm the target is in the authorized scope. If the user has not provided scope or ROE, request it.
- **Follow behavioral rules.** Adhere to any additional behavioral or engagement-specific instructions provided by the user or project.
- **Use assessment state.** For security engagements, use the shared assessment state to track targets, findings, and evidence; keep scope and ROE in mind when recording targets.

---

## 5. Example ROE summary (for user to provide)

When starting an engagement, the user (or engagement lead) should provide at least:

| Item | Example |
|------|--------|
| **Authorized by** | Name/role of authorizing party |
| **In-scope targets** | e.g. `192.168.1.0/24`, `https://app.example.com`, `10.0.0.1–10.0.0.50` |
| **Out-of-scope** | e.g. production DB, payment gateway, third-party SaaS |
| **Allowed activities** | e.g. recon, port scan, web app scan, no DoS, no exploitation of critical systems |
| **Testing window** | e.g. 2025-03-01 00:00 UTC – 2025-03-07 23:59 UTC |
| **Emergency contact** | Who to notify if critical finding or incident |

---

## 6. Quick reference for the agent

1. **Authorized target for this project** → **pci.th3rdai.com** (only this target unless scope is amended in writing).
2. **No ROE/scope given** → Ask the user for written authorization and scope before running security tools.
3. **Target not in scope** → Do not test it; report that it is out of scope.
4. **Unclear whether an action is allowed** → Ask the user or engagement owner before proceeding.
5. **Critical finding or incident** → Pause and report; do not escalate exploitation without approval.

This ROE applies to all penetration testing performed by or with Agent Zero. Engagement-specific ROE may override or extend these rules when documented and provided to the agent.
