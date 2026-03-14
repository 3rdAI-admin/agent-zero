#!/usr/bin/env bash
# Push the Google Workspace MCP bundle to an *existing* GitHub repo.
# Use this if you created the repo manually (e.g. github.com/OWNER/google-workspace-mcp).
#
# Usage:
#   GITHUB_REPO_URL=https://github.com/3rdAI-admin/google-workspace-mcp.git ./scripts/setup/push-google-workspace-mcp-bundle.sh
#   # or
#   export GITHUB_TOKEN=ghp_xxx
#   GITHUB_REPO_URL=https://github.com/YOUR_USER/google-workspace-mcp.git ./scripts/setup/push-google-workspace-mcp-bundle.sh
#
# Requires: GITHUB_REPO_URL (clone URL), GITHUB_TOKEN for push.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUNDLE_DIR="$SCRIPT_DIR/google-workspace-mcp-repo"
cd "$REPO_ROOT"

for envfile in .env usr/.env; do
  [ -f "$envfile" ] && set -a && source "$envfile" && set +a
done

REPO_URL="${GITHUB_REPO_URL:?Set GITHUB_REPO_URL e.g. https://github.com/3rdAI-bill/google-workspace-mcp.git}"
# Use agentz@th3rdai.com (3rdAI-bill) credentials when pushing to that account
# Prefer GITHUB_TOKEN_3rdAI_bill (underscore; set in .env), then GITHUB_TOKEN_SELF
if [ -n "$GITHUB_USE_BILL_CREDENTIALS" ] || echo "$REPO_URL" | grep -q '3rdAI-bill'; then
  TOKEN="${GITHUB_TOKEN_3rdAI_bill:-${GITHUB_TOKEN_SELF:-$GITHUB_TOKEN}}"
else
  TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}"
fi
TOKEN="$(echo "$TOKEN" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
if [ -z "$TOKEN" ]; then
  echo "Error: For 3rdAI-bill repo set GITHUB_TOKEN_3rdAI_bill or GITHUB_TOKEN_SELF in .env."
  exit 1
fi

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

# Clone (use token for private repo)
if [[ "$REPO_URL" =~ ^https://github.com/([^/]+)/([^/.]+)(\.git)?$ ]]; then
  OWNER="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
  CLONE_URL="https://x-access-token:${TOKEN}@github.com/${OWNER}/${REPO}.git"
else
  echo "Could not parse GITHUB_REPO_URL."
  exit 1
fi
if ! git clone "$CLONE_URL" "$WORK_DIR/repo" 2>/dev/null; then
  echo "Clone failed (private repo? token must have read access)."
  echo "Confirm: 1) Repo exists at $REPO_URL  2) GITHUB_TOKEN_3rdAI_bill or GITHUB_TOKEN_SELF has access to it."
  echo "Fine-grained tokens: add this repository under Resource access."
  exit 1
fi
cd "$WORK_DIR/repo"
git checkout -b main 2>/dev/null || true

rsync -a --exclude='.git' "$BUNDLE_DIR/" ./
chmod +x scripts/run_workspace_mcp.sh 2>/dev/null || true

git add -A
if git diff --cached --quiet; then
  echo "No changes to commit (bundle already matches)."
  exit 0
fi
git commit -m "Initial commit: Google Workspace MCP server (Docker, host script, docs)"
git push "https://x-access-token:${TOKEN}@github.com/${OWNER}/${REPO}.git" main

echo "Pushed to $REPO_URL"
