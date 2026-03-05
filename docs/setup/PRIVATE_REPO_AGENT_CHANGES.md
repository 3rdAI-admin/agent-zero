# Private Repo for Agent Zero Self-Changes and Upgrades

This guide sets up a **separate private Git repository** used for agent-driven code changes and upgrades, with a designated collaborator.

## 1. Create the private repository

Create a new **private** repository (do not initialize with a README if you will push this repo into it).

### GitHub (automated)

From the Agent Zero repo root, with a token that has `repo` and `admin:org` (for org repos):

```bash
export GITHUB_TOKEN=ghp_xxx
./scripts/setup/create-agent-zero-private-repo.sh
```

This creates **3rdAI-admin/agent-zero-private** (private), adds the `self` remote, and adds **3rdAI-bill** (bill@th3rdai.com) as a collaborator with admin access. Override with `GITHUB_OWNER` or `GITHUB_COLLABORATOR_USERNAME` if needed.

### GitHub (manual)

1. Go to [GitHub New Repository](https://github.com/new) (or under org **3rdAI-admin**).
2. **Repository name:** e.g. `agent-zero-private` or `agent-zero-self`.
3. **Visibility:** **Private**.
4. Leave **Add a README file** unchecked (this repo already has content).
5. Click **Create repository**.

### GitLab / other

- Create a new **private** project, empty (no initial commit).
- Note the clone URL (HTTPS or SSH), e.g. `https://github.com/YOUR_ORG/agent-zero-private.git`.

---

## 2. Add collaborator (full access)

### GitHub

1. Open the new repo → **Settings** → **Collaborators** (or **Collaborators and teams**).
2. Click **Add people**.
3. Add **bill@th3rdai.com**.
4. Choose **Role:** **Admin** (full access: push, pull, settings, add collaborators).

### GitLab

1. **Project** → **Members** → **Invite members**.
2. Add **bill@th3rdai.com**, role **Maintainer** or **Owner** for full access.

---

## 3. Add the private repo as a remote (this repo)

From the **Agent Zero** repo root (this codebase):

```bash
# Replace with your actual private repo URL
PRIVATE_REPO_URL="https://github.com/YOUR_ORG/agent-zero-private.git"

git remote add self "$PRIVATE_REPO_URL"
git remote -v
```

- **Remote name:** `self` (used below; you can use another name and substitute it).
- Use HTTPS if you use credentials; use SSH if you use keys, e.g. `git@github.com:YOUR_ORG/agent-zero-private.git`.

---

## 4. Push this repo to the private repo (one-time)

If the private repo is empty and you want it to mirror this codebase:

```bash
git push -u self main
```

To push all branches and tags:

```bash
git push self --all
git push self --tags
```

---

## 5. Using the private repo for agent changes and upgrades

- **Human / CI:** Keep using `origin` (or `upstream`) for your normal workflow.
- **Agent-driven changes:** Use the `self` remote so all self-changes live in one place and don’t clutter the main repo until reviewed.

Suggested workflow:

1. Agent (or you) creates a branch for a change, e.g. `agent/upgrade-xyz` or `self/describe-change`.
2. Make commits on that branch.
3. Push the branch to the private repo:  
   `git push self agent/upgrade-xyz`
4. **bill@th3rdai.com** (or you) reviews in the private repo and can merge there or merge into this repo via pull request / manual merge.

Optional: restrict the agent to only push to `self` (not to `origin`) via tool config or allowlists so production/main stays under human control.

---

## 5b. Using the repo to communicate improvements to Agent Zero (two-way)

The private repo can be used as a **two-way channel**: you (or Cursor) push improvement requests; Agent Zero pulls, reads them, and pushes back its changes.

**Human / admin (3rdAI-admin):**

1. Set **GITHUB_TOKEN** in `.env` to your 3rdAI-admin token (repo access).
2. Edit **inbox/IMPROVEMENTS_FROM_HUMAN.md** with dated tasks, priorities, or constraints.
3. Commit and push to `self` using the **admin** script (so your token is used, not the agent’s):
   ```bash
   git add inbox/IMPROVEMENTS_FROM_HUMAN.md
   git commit -m "Inbox: add improvement requests"
   ./scripts/setup/git-self-admin.sh push self main
   ```

**Agent Zero:** The agent is instructed to pull from `self` and read **inbox/IMPROVEMENTS_FROM_HUMAN.md** when doing self-improvement or upgrades, and to treat listed items as requested work. The agent uses **GITHUB_TOKEN_3rdAI_bill** (or **GITHUB_TOKEN_3rdAI_bill or GITHUB_TOKEN_SELF**) via `./scripts/setup/git-self.sh` for its own push/pull.

| Who            | Token / script |
|----------------|----------------|
| You / Cursor   | **GITHUB_TOKEN** → `./scripts/setup/git-self-admin.sh` |
| Agent Zero     | **GITHUB_TOKEN_3rdAI_bill** or **GITHUB_TOKEN_3rdAI_bill or GITHUB_TOKEN_SELF** → `./scripts/setup/git-self.sh`   |

---

## 6. Quick reference

| Remote   | Purpose |
|----------|--------|
| `origin` | Your primary clone (3rdAI-admin/agent-zero). |
| `upstream` | Upstream Agent Zero (agent0ai/agent-zero). |
| `self`  | Private repo **3rdAI-bill/agent-zero-private-repo** ([GitHub](https://github.com/3rdAI-bill/agent-zero-private-repo)) for agent self-changes and upgrades. |

---

## 7. Agent Zero access (confirm and use)

**Remote:** The `self` remote points to **3rdAI-bill/agent-zero-private-repo**. Use a 3rdAI-bill token in `.env` for push/pull (self-improvement, upgrades, and updates).

**Add the token to `.env` (either name works):**

```bash
# 3rdAI-bill token for the self remote (agent-zero-private-repo)
GITHUB_TOKEN_3rdAI_bill=ghp_xxxxxxxxxxxx
# or: GITHUB_TOKEN_SELF=ghp_xxx
```

**Push/pull using the helper scripts:**

- **Agent Zero** (uses `GITHUB_TOKEN_3rdAI_bill` or `GITHUB_TOKEN_3rdAI_bill or GITHUB_TOKEN_SELF`):
  ```bash
  ./scripts/setup/git-self.sh push self main
  ./scripts/setup/git-self.sh pull self main
  ./scripts/setup/git-self.sh fetch self
  ```
- **You / admin** (uses `GITHUB_TOKEN` for inbox and admin pushes):
  ```bash
  ./scripts/setup/git-self-admin.sh push self main
  ./scripts/setup/git-self-admin.sh pull self main
  ```

**Confirm access:**

```bash
./scripts/setup/git-self.sh ls-remote self
```

If you see refs (e.g. `HEAD`, `refs/heads/main`), access is OK.

**Let Agent Zero push/pull for self-improvement:** When Agent Zero runs git against `self` (for upgrades/updates), it must use **GITHUB_TOKEN_3rdAI_bill or GITHUB_TOKEN_SELF**. That token is specifically for Agent Zero’s self-improvement use, not for general admin.

1. **GITHUB_TOKEN_3rdAI_bill or GITHUB_TOKEN_SELF** must be in the environment where the agent runs (e.g. **Settings → Secrets** or the `.env` loaded by the process).
2. The agent should use the script so the correct token is used: `./scripts/setup/git-self.sh push self main` (or pull/fetch as needed).

Once **GITHUB_TOKEN_3rdAI_bill or GITHUB_TOKEN_SELF** is set and the agent uses the script for `self`, Agent Zero has access to the private repo for self-improvement, upgrades, and updates.

## 8. Security notes

- Keep the private repo **private** so only you and the collaborator (3rdAI-bill) can see agent-proposed changes.
- Use **branch protection** on `main` in the private repo if you want (e.g. require PR + review before merge).
- For future safe self-modification (SELF-*), the plan is: propose → sandbox/verify → promote; the `self` remote is a good target for the “propose” and “promote” steps once that pipeline is implemented.
