#!/usr/bin/env bash
# create-project.sh - Context Engineering template compatibility.
# Agent Zero uses projects under /a0/usr; for new project from template use PRPs workflow.
set -e
if [ -z "${1:-}" ]; then
  echo "Usage: $0 <project-path> [--all]"
  echo "Agent Zero: create project dir and use PRPs/workflow. See /new-project and /generate-prp."
  exit 1
fi
mkdir -p "$1"
echo "Created $1. Add INITIAL.md and use /generate-prp for execution plan."
exit 0
