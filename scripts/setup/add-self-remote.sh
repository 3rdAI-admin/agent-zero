#!/usr/bin/env bash
# Add the private "self" remote for agent-driven changes and upgrades.
# Run after creating the private repo and adding the collaborator.
# See: docs/setup/PRIVATE_REPO_AGENT_CHANGES.md

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if git remote get-url self 2>/dev/null; then
  echo "Remote 'self' already exists: $(git remote get-url self)"
  echo "To change it: git remote set-url self <new-url>"
  exit 0
fi

if [ -n "$1" ]; then
  PRIVATE_REPO_URL="$1"
else
  echo "Private repo URL (e.g. https://github.com/YOUR_ORG/agent-zero-private.git):"
  read -r PRIVATE_REPO_URL
fi

if [ -z "$PRIVATE_REPO_URL" ]; then
  echo "No URL provided. Usage: $0 [PRIVATE_REPO_URL]"
  exit 1
fi

git remote add self "$PRIVATE_REPO_URL"
echo "Added remote: self -> $PRIVATE_REPO_URL"
echo ""
echo "Push this repo to the private repo (one-time):"
echo "  git push -u self main"
echo ""
echo "See docs/setup/PRIVATE_REPO_AGENT_CHANGES.md for full workflow."
