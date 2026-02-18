# Quick Start: Using `claude-pro-yolo`

## What is `claude-pro-yolo`?

A wrapper script that runs Claude Code with YOLO mode (`--dangerously-skip-permissions`) enabled, allowing autonomous operation without confirmation prompts.

## How to Invoke

### 1. You (Direct)

```bash
docker exec agent-zero claude-pro-yolo 'your task here'
```

### 2. Agent Zero (Automatic)

Just ask Agent Zero:
```
"Use Claude Code to [your task]"
```

Agent Zero will automatically invoke `claude-pro-yolo`.

### 3. Interactive Mode

```bash
docker exec -it agent-zero claude-pro-yolo
```

## Examples

### Code Generation
```bash
claude-pro-yolo 'Write a Python function to scan ports'
```

### Code Review
```bash
claude-pro-yolo 'Review this code for security vulnerabilities'
```

### Exploit Development
```bash
claude-pro-yolo 'Create a SQL injection tester'
```

## Key Points

- ✅ **Location**: `/usr/local/bin/claude-pro-yolo`
- ✅ **YOLO Mode**: Enabled automatically
- ✅ **No Prompts**: Autonomous operation
- ✅ **Agent Zero**: Uses it automatically when you ask for Claude Code

## Full Documentation

See `HOW_TO_USE_CLAUDE_PRO_YOLO.md` for complete details.
