#!/usr/bin/env bash
# Create a private GitHub repo for the Google Workspace MCP server code and push the bundled content.
# Uses GitHub REST API. Requires GITHUB_TOKEN or GH_TOKEN with repo scope (admin:org for org repos).
#
# Usage:
#   export GITHUB_TOKEN=ghp_xxx   # or set in .env
#   ./scripts/setup/create-google-workspace-mcp-repo.sh
#
# Optional:
#   GITHUB_OWNER=3rdAI-admin
#   GITHUB_REPO_NAME=google-workspace-mcp
#   GITHUB_COLLABORATOR_USERNAME=3rdAI-bill
#
# The script creates the repo, then copies content from scripts/setup/google-workspace-mcp-repo/
# into a fresh clone, commits, and pushes.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUNDLE_DIR="$SCRIPT_DIR/google-workspace-mcp-repo"
cd "$REPO_ROOT"

# Load .env for GITHUB_TOKEN
for envfile in .env usr/.env; do
  [ -f "$envfile" ] && set -a && source "$envfile" && set +a
done

TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}"
TOKEN="$(echo "$TOKEN" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
if [ -z "$TOKEN" ]; then
  echo "Error: GITHUB_TOKEN or GH_TOKEN is required."
  echo "Set in .env or: export GITHUB_TOKEN=ghp_xxx"
  exit 1
fi

AUTH_CODE="$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/user)"
if [ "$AUTH_CODE" -eq 401 ]; then
  echo "Error: GitHub token is invalid or expired (401)."
  exit 1
fi

REPO_NAME="${GITHUB_REPO_NAME:-google-workspace-mcp}"
OWNER="${GITHUB_OWNER:-3rdAI-admin}"
COLLAB_USERNAME="${GITHUB_COLLABORATOR_USERNAME:-3rdAI-bill}"
# Use agentz@th3rdai.com (3rdAI-bill) credentials when creating under that user
USE_BILL="${GITHUB_USE_BILL_CREDENTIALS:-}"
[ "$OWNER" = "3rdAI-bill" ] && USE_BILL=1
if [ -n "$USE_BILL" ] && [ -n "${GITHUB_TOKEN_SELF:-}" ]; then
  TOKEN="$(echo "$GITHUB_TOKEN_SELF" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
fi
API_HEADERS=(-H "Accept: application/vnd.github+json" -H "Authorization: Bearer $TOKEN" -H "X-GitHub-Api-Version: 2022-11-28")

if [ ! -d "$BUNDLE_DIR" ]; then
  echo "Error: Bundle directory not found: $BUNDLE_DIR"
  exit 1
fi

# When owner is 3rdAI-bill, create under authenticated user (no org API)
if [ "$OWNER" = "3rdAI-bill" ]; then
  echo "Creating private repository under 3rdAI-bill (user): ${REPO_NAME}"
  RESPONSE="$(curl -s -w "\n%{http_code}" -X POST "https://api.github.com/user/repos" "${API_HEADERS[@]}" \
    -d "{\"name\":\"${REPO_NAME}\",\"private\":true,\"description\":\"Google Workspace MCP server — Docker and host setup for Gmail, Drive, Docs, Sheets, Calendar\",\"auto_init\":false}")"
  HTTP_BODY="$(echo "$RESPONSE" | sed '$d')"
  HTTP_CODE="$(echo "$RESPONSE" | tail -n 1)"
  if [ "$HTTP_CODE" -eq 201 ]; then
    OWNER="$(echo "$HTTP_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('owner',{}).get('login',''))" 2>/dev/null || true)"
  fi
else
  # Create repo under org
  CREATE_URL="https://api.github.com/orgs/${OWNER}/repos"
  echo "Creating private repository: ${OWNER}/${REPO_NAME}"
  RESPONSE="$(curl -s -w "\n%{http_code}" -X POST "$CREATE_URL" "${API_HEADERS[@]}" \
    -d "{\"name\":\"${REPO_NAME}\",\"private\":true,\"description\":\"Google Workspace MCP server — Docker and host setup for Gmail, Drive, Docs, Sheets, Calendar\",\"auto_init\":false}")"
  HTTP_BODY="$(echo "$RESPONSE" | sed '$d')"
  HTTP_CODE="$(echo "$RESPONSE" | tail -n 1)"
  if [ "$HTTP_CODE" -eq 404 ]; then
    echo "Org ${OWNER} not found. Creating under user account..."
    RESPONSE="$(curl -s -w "\n%{http_code}" -X POST "https://api.github.com/user/repos" "${API_HEADERS[@]}" \
      -d "{\"name\":\"${REPO_NAME}\",\"private\":true,\"description\":\"Google Workspace MCP server — Docker and host setup\",\"auto_init\":false}")"
    HTTP_BODY="$(echo "$RESPONSE" | sed '$d')"
    HTTP_CODE="$(echo "$RESPONSE" | tail -n 1)"
    [ "$HTTP_CODE" -eq 201 ] && OWNER="$(echo "$HTTP_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('owner',{}).get('login',''))" 2>/dev/null || true)"
  fi
fi

if [ "$HTTP_CODE" -ne 201 ]; then
  echo "Failed to create repository (HTTP $HTTP_CODE)"
  echo "$HTTP_BODY" | python3 -m json.tool 2>/dev/null || echo "$HTTP_BODY"
  echo ""
  echo "If using 3rdAI-bill: ensure GITHUB_TOKEN_SELF has 'repo' scope (create repo). Or create the repo manually at https://github.com/new (owner 3rdAI-bill, name ${REPO_NAME}), then run:"
  echo "  GITHUB_REPO_URL=https://github.com/3rdAI-bill/${REPO_NAME}.git ./scripts/setup/push-google-workspace-mcp-bundle.sh"
  exit 1
fi

REPO_CLONE_URL="https://github.com/${OWNER}/${REPO_NAME}.git"
echo "Created: https://github.com/${OWNER}/${REPO_NAME}"

# Add collaborator
if [ -n "$COLLAB_USERNAME" ]; then
  COLLAB_CODE="$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
    "https://api.github.com/repos/${OWNER}/${REPO_NAME}/collaborators/${COLLAB_USERNAME}" \
    "${API_HEADERS[@]}" -d '{"permission":"admin"}')"
  if [ "$COLLAB_CODE" -eq 204 ] || [ "$COLLAB_CODE" -eq 201 ]; then
    echo "Collaborator $COLLAB_USERNAME added (admin)."
  fi
fi

# Clone, copy bundle, commit, push (use token for push)
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

git clone "$REPO_CLONE_URL" "$WORK_DIR/repo"
cd "$WORK_DIR/repo"

# Empty repo has no branch; ensure we're on main
git checkout -b main 2>/dev/null || true

rsync -a --exclude='.git' "$BUNDLE_DIR/" ./
chmod +x scripts/run_workspace_mcp.sh 2>/dev/null || true

git add -A
git status
git commit -m "Initial commit: Google Workspace MCP server (Docker, host script, docs)"
# Push using token (avoid embedding in URL on echo; use credential helper or token in URL)
git push "https://x-access-token:${TOKEN}@github.com/${OWNER}/${REPO_NAME}.git" main

echo ""
echo "Done. Repo: https://github.com/${OWNER}/${REPO_NAME}"
echo "To clone: git clone $REPO_CLONE_URL"
