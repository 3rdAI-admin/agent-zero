#!/usr/bin/env bash
# VS Code setup shim for Context Engineering template validation.
# Agent Zero: copy .vscode/settings from repo or run from IDE.
set -e
[ -d ".vscode" ] || mkdir -p .vscode
echo "VS Code setup: .vscode/ present. Configure as needed."
exit 0
