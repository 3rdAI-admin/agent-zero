#!/usr/bin/env bash
# Create a private GitHub repo for Agent Zero self-changes and add a collaborator.
# Uses GitHub REST API. Requires GITHUB_TOKEN or GH_TOKEN with repo scope (admin:org for org repos).
#
# Usage:
#   export GITHUB_TOKEN=ghp_xxx
#   ./scripts/setup/create-agent-zero-private-repo.sh
#
# Optional:
#   GITHUB_OWNER=3rdAI-admin     # default
#   GITHUB_REPO_NAME=agent-zero-private
#   GITHUB_COLLABORATOR_USERNAME=3rdAI-bill   # default; GitHub login for bill@th3rdai.com
#
# See: docs/setup/PRIVATE_REPO_AGENT_CHANGES.md

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}"
# Trim leading/trailing whitespace (e.g. from .env)
TOKEN="$(echo "$TOKEN" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
if [ -z "$TOKEN" ]; then
  echo "Error: GITHUB_TOKEN or GH_TOKEN is required."
  echo "Create a token at https://github.com/settings/tokens with 'repo' and 'admin:org' (for org repos)."
  exit 1
fi
# Verify token (avoids cryptic 401 later)
AUTH_CODE="$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/user)"
if [ "$AUTH_CODE" -eq 401 ]; then
  echo "Error: GitHub token is invalid or expired (401 Unauthorized)."
  echo "  - Check .env: no extra quotes or spaces around GITHUB_TOKEN."
  echo "  - Create a new token at https://github.com/settings/tokens with scopes: repo, admin:org."
  echo "  - Use a classic token (starts with ghp_) or fine-grained with repo + org permissions."
  exit 1
fi

REPO_NAME="${GITHUB_REPO_NAME:-agent-zero-private}"
OWNER="${GITHUB_OWNER:-3rdAI-admin}"
COLLAB_USERNAME="${GITHUB_COLLABORATOR_USERNAME:-3rdAI-bill}"

API_HEADERS=(-H "Accept: application/vnd.github+json" -H "Authorization: Bearer $TOKEN" -H "X-GitHub-Api-Version: 2022-11-28")

# Create repo under org
CREATE_URL="https://api.github.com/orgs/${OWNER}/repos"
echo "Creating private repository: ${OWNER}/${REPO_NAME}"
RESPONSE="$(curl -s -w "\n%{http_code}" -X POST "$CREATE_URL" "${API_HEADERS[@]}" \
  -d "{\"name\":\"${REPO_NAME}\",\"private\":true,\"description\":\"Private repo for Agent Zero self-changes and upgrades\",\"auto_init\":false}")"
HTTP_BODY="$(echo "$RESPONSE" | sed '$d')"
HTTP_CODE="$(echo "$RESPONSE" | tail -n 1)"

if [ "$HTTP_CODE" -eq 201 ]; then
  echo "Created repository: ${OWNER}/${REPO_NAME}"
  REPO_HTML_URL="$(echo "$HTTP_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('html_url',''))" 2>/dev/null || true)"
  REPO_CLONE_URL="https://github.com/${OWNER}/${REPO_NAME}.git"
  echo "URL: ${REPO_HTML_URL:-$REPO_CLONE_URL}"
elif [ "$HTTP_CODE" -eq 404 ]; then
  echo "Org ${OWNER} not found or token cannot create org repos (404). Creating under your user account instead..."
  RESPONSE="$(curl -s -w "\n%{http_code}" -X POST "https://api.github.com/user/repos" "${API_HEADERS[@]}" \
    -d "{\"name\":\"${REPO_NAME}\",\"private\":true,\"description\":\"Private repo for Agent Zero self-changes and upgrades\",\"auto_init\":false}")"
  HTTP_BODY="$(echo "$RESPONSE" | sed '$d')"
  HTTP_CODE="$(echo "$RESPONSE" | tail -n 1)"
  if [ "$HTTP_CODE" -eq 201 ]; then
    OWNER="$(echo "$HTTP_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('owner',{}).get('login',''))" 2>/dev/null || true)"
    [ -z "$OWNER" ] && OWNER="$(curl -s -H "Authorization: Bearer $TOKEN" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin).get('login',''))" 2>/dev/null)"
    echo "Created repository: ${OWNER}/${REPO_NAME}"
    REPO_HTML_URL="$(echo "$HTTP_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('html_url',''))" 2>/dev/null || true)"
    REPO_CLONE_URL="https://github.com/${OWNER}/${REPO_NAME}.git"
    echo "URL: ${REPO_HTML_URL:-$REPO_CLONE_URL}"
  else
    echo "Failed to create user repo (HTTP $HTTP_CODE)"
    echo "$HTTP_BODY" | python3 -m json.tool 2>/dev/null || echo "$HTTP_BODY"
    exit 1
  fi
else
  echo "Failed to create repository (HTTP $HTTP_CODE)"
  echo "$HTTP_BODY" | python3 -m json.tool 2>/dev/null || echo "$HTTP_BODY"
  if [ "$HTTP_CODE" -eq 401 ]; then
    echo ""
    echo "Fix: Use a valid token with 'repo' and 'admin:org'. Check for typos or spaces in .env GITHUB_TOKEN."
  elif [ "$HTTP_CODE" -eq 404 ]; then
    echo ""
    echo "Fix: Token must be from a user who is a member of ${OWNER} with permission to create repos, or use GITHUB_OWNER=<your-username> to create under your account."
  fi
  exit 1
fi

# Add collaborator (requires GitHub username; API does not accept email)
if [ -n "$COLLAB_USERNAME" ]; then
  echo "Adding collaborator: $COLLAB_USERNAME (admin)"
  COLLAB_CODE="$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
    "https://api.github.com/repos/${OWNER}/${REPO_NAME}/collaborators/${COLLAB_USERNAME}" \
    "${API_HEADERS[@]}" -d '{"permission":"admin"}')"
  if [ "$COLLAB_CODE" -eq 204 ] || [ "$COLLAB_CODE" -eq 201 ]; then
    echo "Collaborator $COLLAB_USERNAME added with admin access."
  else
    echo "Note: Could not add collaborator (HTTP $COLLAB_CODE). Add bill@th3rdai.com manually: repo → Settings → Collaborators."
  fi
else
  echo ""
  echo "To add another collaborator: GITHUB_COLLABORATOR_USERNAME=<username> $0"
  echo "Or: ${REPO_HTML_URL:-https://github.com/$OWNER/$REPO_NAME}/settings/access → Add people."
fi

# Add 'self' remote if not present
if ! git remote get-url self 2>/dev/null; then
  git remote add self "$REPO_CLONE_URL"
  echo ""
  echo "Added remote 'self' -> $REPO_CLONE_URL"
  echo "Push this repo (one-time): git push -u self main"
else
  echo ""
  echo "Remote 'self' already exists. To point it at the new repo: git remote set-url self $REPO_CLONE_URL"
fi
