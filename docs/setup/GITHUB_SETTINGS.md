# GitHub settings (project memory)

Reference for AI and maintainers. **Do not commit token values** — they live in `.env` only.

## Token identity

- **`GITHUB_TOKEN_3rdAI_bill`** in `.env` is the same as the **AgentZeroSIP** Personal Access Token (GitHub → Settings → Developer settings → Personal access tokens).
- **AgentZeroSIP** = "Agent Zero Self-Improvement Project"; used for pushes by Agent Zero to 3rdAI-bill repos.
- Optional alias in `.env`: **`GITHUB_TOKEN_SELF`** (scripts use `GITHUB_TOKEN_3rdAI_bill` or `GITHUB_TOKEN_SELF`).

## Repos and remotes

| Repo / remote | Purpose |
|---------------|--------|
| **origin** | `3rdAI-admin/agent-zero` — main Agent Zero codebase. |
| **self** | `3rdAI-bill/agent-zero-private-repo` — private repo for agent self-improvement; push via `./scripts/setup/git-self.sh`. |
| **3rdAI-bill/ollama** | Standalone Docker Compose for Ollama (CPU/GPU); created from AgentZ, lives at `/Users/james/Docker/ollama`. |

## Pushing as 3rdAI-bill (AgentZeroSIP)

Scripts such as `scripts/setup/git-self.sh` load `.env` and run git with a credential helper that supplies `GITHUB_TOKEN_3rdAI_bill`. For other repos (e.g. ollama), push using the token from `.env` in the URL so the correct token is used:

```bash
# From host; token from AgentZ .env
cd /path/to/repo
source /Users/james/Docker/AgentZ/.env  # or set -a && source .env && set +a
git push https://3rdAI-bill:"${GITHUB_TOKEN_3rdAI_bill}"@github.com/3rdAI-bill/REPO_NAME.git main
```

Example for the ollama repo:

```bash
cd /Users/james/Docker/ollama
# Load token from AgentZ .env, then:
git push https://3rdAI-bill:"${GITHUB_TOKEN_3rdAI_bill}"@github.com/3rdAI-bill/ollama.git main
```

If you get **403**, the token may lack `repo` (or fine-grained “code” read/write) for that repository; ensure AgentZeroSIP has access to the target repo.

## See also

- [Private repo and git-self setup](PRIVATE_REPO_AGENT_CHANGES.md)
- [Ollama Docker repo](https://github.com/3rdAI-bill/ollama) (compose, GPU override, NVIDIA toolkit script)
