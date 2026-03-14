#!/usr/bin/env bash
# Root setup shim for Context Engineering template validation.
# Agent Zero setup: use scripts/setup/startup.sh or deploy.sh for full setup.
set -e
echo "Agent Zero: use scripts/setup/startup.sh or ./deploy.sh for setup."
if [ -x "scripts/setup/startup.sh" ]; then exec scripts/setup/startup.sh "$@"; fi
exit 0
