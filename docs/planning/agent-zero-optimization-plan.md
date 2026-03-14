# Agent Zero Optimization Plan — Th3rdAI

**Date:** March 8, 2026
**Hardware:** Apple Silicon Mac (M-series) with 14–32B local models via Ollama
**Priority:** Privacy-first, then quality, then speed, then cost

---

## Phase 1: Ollama Optimization (Do First — Immediate Impact)

These changes will make your local models run faster and more reliably with Agent Zero.

### 1.1 — Set Ollama Environment Variables

Add these to your shell profile (`~/.zshrc` on Mac) so they apply every time:

```bash
# Keep models loaded in memory (no cold-start delays)
export OLLAMA_KEEP_ALIVE=-1

# Match performance cores on your chip
# M1/M2: 4 performance cores → set to 4
# M1 Pro/Max, M2 Pro/Max: 6–8 → set to 8
# M3 Pro/Max, M4 Pro/Max: 8–10 → set to 10
export OLLAMA_NUM_THREADS=8

# Allow larger context windows without running out of memory
# Adjust based on your unified memory:
# 32GB → 1 (load 1 model at a time)
# 64GB → 2
# 128GB → 3
export OLLAMA_MAX_LOADED_MODELS=2
```

After editing, run: `source ~/.zshrc`

### 1.2 — Create Custom Models with Larger Context

Ollama defaults to 2048 tokens — far too small for Agent Zero's agent workflows. Create custom models:

```bash
# Chat model (32B) — 32K context
ollama create qwen3-32k -f - <<EOF
FROM qwen3:32b
PARAMETER num_ctx 32768
PARAMETER temperature 0.7
EOF

# If you're on 32GB RAM, use 14B instead:
# ollama create qwen3-14b-32k -f - <<EOF
# FROM qwen3:14b
# PARAMETER num_ctx 32768
# PARAMETER temperature 0.7
# EOF

# Utility model (small & fast) — 8K context is plenty
ollama create qwen3-8b-util -f - <<EOF
FROM qwen3:8b
PARAMETER num_ctx 8192
PARAMETER temperature 0.3
EOF

# Embedding model (if not already pulled)
ollama pull nomic-embed-text
```

### 1.3 — Verify Models

```bash
ollama list
# You should see: qwen3-32k, qwen3-8b-util, nomic-embed-text
```

---

## Phase 2: Agent Zero Configuration

### 2.1 — Model Assignment in Agent Zero Settings

Open Agent Zero's web UI → Settings and configure:

| Role | Provider | Model Name | Why |
|------|----------|------------|-----|
| Chat Model | Ollama | `qwen3-32k` | Best reasoning, big context |
| Utility Model | Ollama | `qwen3-8b-util` | Fast, cheap for summaries |
| Embedding Model | Ollama | `nomic-embed-text` | Lightweight, always running |

### 2.2 — Context & Memory Settings

In Agent Zero Settings:

- **chat_model_ctx_history:** Change from `0.7` to `0.6`
  - Gives more room for system prompt + memory recall
  - Prevents agents from "forgetting" instructions mid-task
- **Enable AI memory consolidation** (should be on by default in v0.9.3+)
  - Reduces redundant memories, saves tokens
- **Enable auto memory** if not already on

### 2.3 — Migrate Secrets from Google Doc

Move all credentials from the "Agent Zero Config" Google Doc into Agent Zero's built-in secrets manager:

1. Go to Agent Zero UI → Settings → Secrets
2. Add each credential:
   - `ANTHROPIC_API_KEY` → your Anthropic key
   - `GOOGLE_API_KEY` → your Gemini key
   - `VENICE_API_KEY` → your Venice.AI key
   - `EMAIL_USER` → agentz@th3rdai.com
   - `EMAIL_PASSWORD` → your app password
   - `GITHUB_TOKEN_3rdAI_admin` → your admin PAT
   - `GITHUB_TOKEN_3rdAI_bill` → your bill PAT
   - `GOOGLE_OAUTH_CLIENT_ID` → your OAuth client ID
   - `GOOGLE_OAUTH_CLIENT_SECRET` → your OAuth secret
3. Once confirmed working, **remove credentials from the Google Doc** and replace with a note pointing to Agent Zero's secrets manager

### 2.4 — MCP Server Networking

Make sure your Docker-to-host networking is consistent. In your `docker-compose.yml` or Agent Zero MCP config:

- Inside Docker: use `host.docker.internal:11434` to reach Ollama on the host
- Inside Docker: use `host.docker.internal:8889` to reach Google Workspace MCP on the host
- For Claude Code (runs on host): use `127.0.0.1:8889`

---

## Phase 3: Repository Cleanup

Run these commands from your repo directory (`~/Docker/AgentZ` or wherever the clone lives). Best done in Claude Code so it can help if anything goes wrong.

### 3.1 — Consolidate Launch Scripts

Keep only the one that works. Likely `launch_a0.py` is the primary one:

```bash
# Check which one is actually used
grep -r "launch_a0" docker-compose.yml Dockerfile startup.sh

# Once confirmed, remove the extras
git rm launch_a0_direct.py
git rm launch_a0_fixed.py
```

### 3.2 — Organize Root-Level Markdown Files

Move planning/status docs out of the root into organized folders:

```bash
# Create an organized structure
mkdir -p docs/planning
mkdir -p docs/status

# Move planning docs
git mv PLANNING.md docs/planning/
git mv IMPROVE.md docs/planning/
git mv FIXMODELS.md docs/planning/

# Move status/summary docs
git mv ASSESSMENT.md docs/status/
git mv REORGANIZATION_SUMMARY.md docs/status/
git mv SIP_PROJECT_UPDATE.md docs/status/
git mv RESPONSES.md docs/status/
git mv e2e-test-report.md docs/status/

# Move setup/deployment docs
git mv DEPLOYMENT_QUICK_START.md docs/
git mv CONTAINER_RESTARTED.md docs/
git mv QUICK_REFERENCE.md docs/
git mv INITIAL.md docs/
git mv INITIAL_EXAMPLE.md docs/

# Keep at root (these are expected there):
# - README.md
# - CLAUDE.md (Claude Code expects this)
# - LICENSE
# - TASK.md (if actively used by agents)
# - A0_AGENTZ.md, A0_ANTHROPIC.md, A0_OLLAMA.md, A0_VENICEAI.md
#   (these appear to be model configs — could also move to conf/)
```

### 3.3 — Consider Moving Model Config Files

```bash
# If A0_*.md files are model configuration references:
git mv A0_AGENTZ.md conf/
git mv A0_ANTHROPIC.md conf/
git mv A0_OLLAMA.md conf/
git mv A0_VENICEAI.md conf/
```

### 3.4 — Clean Up Redundant Requirement Files

```bash
# Check what's different
diff requirements.txt requirements2.txt

# If requirements2.txt is outdated or a duplicate, remove it
git rm requirements2.txt
```

### 3.5 — Commit the Cleanup

```bash
git add -A
git commit -m "chore: organize repo structure, remove redundant files

- Consolidated launch scripts (kept launch_a0.py)
- Moved planning/status docs into docs/ subfolders
- Moved model configs into conf/
- Removed duplicate requirements file
- Root now contains only essential files"

git push origin main
```

---

## Phase 4: Advanced Optimizations (When Ready)

These are longer-term improvements to explore once the basics are solid.

### 4.1 — Hybrid Model Routing (Cloud Fallback)

For tasks where quality really matters (complex code generation, critical decisions), you can configure Agent Zero to use a cloud model as a fallback. Keep the chat model on local Ollama for privacy, but configure a secondary profile:

- Create a **subordinate agent profile** (v0.9.3+ feature) that uses Anthropic Claude for high-stakes tasks
- The primary agent stays fully local
- Only escalate to cloud when the local model can't handle it

### 4.2 — Prompt Optimization for Smaller Models

Local models are more sensitive to prompt quality. Consider:

- Simplifying the system prompt in `prompts/default/agent.system.md`
- Reducing verbose instructions that waste context tokens
- Adding explicit tool-use examples for your specific workflows
- Testing with Agent Zero's built-in Skills system for structured, reusable capabilities

### 4.3 — Model Evaluation

Once your setup is stable, test different models to find the sweet spot for your hardware:

| Model | Size | Best For | Notes |
|-------|------|----------|-------|
| `qwen3:32b` | 32B | General reasoning | Best overall local quality |
| `deepseek-r1:32b` | 32B | Complex reasoning | Slower but very thorough |
| `qwen3:14b` | 14B | Balanced speed/quality | Good for 32GB Macs |
| `codellama:34b` | 34B | Code-heavy tasks | If your work is mostly coding |
| `llama3.1:8b` | 8B | Fast utility tasks | Great as utility model |

### 4.4 — Scheduled Model Preloading

If you use Agent Zero at specific times, create a simple cron job to preload your models before you start work:

```bash
# Add to crontab (crontab -e):
# Preload chat model at 8:50 AM on weekdays
50 8 * * 1-5 curl -s http://localhost:11434/api/generate -d '{"model":"qwen3-32k","prompt":"hello","stream":false}' > /dev/null
```

---

## Checklist

- [ ] Set Ollama environment variables in ~/.zshrc
- [ ] Create custom models with larger context windows
- [ ] Configure Agent Zero model assignments
- [ ] Adjust chat_model_ctx_history to 0.6
- [ ] Enable AI memory consolidation
- [ ] Migrate secrets from Google Doc to Agent Zero secrets manager
- [ ] Fix MCP networking (host.docker.internal)
- [ ] Remove redundant launch scripts
- [ ] Organize root-level markdown files
- [ ] Move model configs to conf/
- [ ] Remove duplicate requirements file
- [ ] Commit and push cleanup
- [ ] Test full workflow end-to-end
