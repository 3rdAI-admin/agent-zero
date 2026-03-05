#!/usr/bin/env bash
# Run git commands against the 'self' remote using a 3rdAI-bill token.
# This token is for Agent Zero's self-improvement, upgrades, and updates (push/pull to agent-zero-private-repo).
#
# Usage:
#   ./scripts/setup/git-self.sh push self main
#   ./scripts/setup/git-self.sh pull self main
#   ./scripts/setup/git-self.sh fetch self
#
# Requires in .env: GITHUB_TOKEN_3rdAI_bill or GITHUB_TOKEN_SELF (Agent Zero's credential for the self remote).

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Load repo .env then usr/.env (Secrets / Settings may write to usr/.env)
for envfile in .env usr/.env; do
  [ -f "$envfile" ] && set -a && source "$envfile" && set +a
done

TOKEN="${GITHUB_TOKEN_3rdAI_bill:-${GITHUB_TOKEN_SELF:-}}"
TOKEN="$(echo "$TOKEN" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
if [ -z "$TOKEN" ]; then
  echo "Error: A token is required for the self remote."
  echo "Add to .env: GITHUB_TOKEN_3rdAI_bill=ghp_xxx  (or GITHUB_TOKEN_SELF)"
  exit 1
fi

exec git -c credential.helper='!f() { echo "username=token"; echo "password='"$TOKEN"'"; }; f' "$@"
