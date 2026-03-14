#!/usr/bin/env bash
# Run git commands against the 'self' remote using GITHUB_TOKEN (3rdAI-admin).
# Use this from the host/Cursor when you want to push improvement briefs or
# admin changes to the private repo. Agent Zero uses git-self.sh (GITHUB_TOKEN_SELF) instead.
#
# Usage:
#   ./scripts/setup/git-self-admin.sh push self main
#   ./scripts/setup/git-self-admin.sh pull self main
#   ./scripts/setup/git-self-admin.sh fetch self
#
# Requires GITHUB_TOKEN in .env (admin credential for the self remote).

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

for envfile in .env usr/.env; do
  [ -f "$envfile" ] && set -a && source "$envfile" && set +a
done

TOKEN="${GITHUB_TOKEN:-}"
TOKEN="$(echo "$TOKEN" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
if [ -z "$TOKEN" ]; then
  echo "Error: GITHUB_TOKEN is required for admin access to the self remote."
  echo "Add to .env: GITHUB_TOKEN=ghp_xxx  (3rdAI-admin token for pushing improvement briefs, etc.)"
  exit 1
fi

exec git -c credential.helper='!f() { echo "username=token"; echo "password='"$TOKEN"'"; }; f' "$@"
