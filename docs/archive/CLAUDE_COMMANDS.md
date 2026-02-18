# Claude Code Commands Reference

## Correct Command Syntax

### ✅ Use Pro Subscription (OAuth)
```bash
docker exec -it agent-zero claude-pro
```

### ✅ Force OAuth Authentication
```bash
docker exec -it agent-zero claude-oauth
```

### ✅ Use API Key (Pay-per-use)
```bash
docker exec -it agent-zero claude
```

## Common Mistakes

### ❌ Wrong (don't use --)
```bash
docker exec -it agent-zero --claude-pro
```

### ✅ Correct (no -- needed)
```bash
docker exec -it agent-zero claude-pro
```

## Explanation

- `docker exec -it` - Execute command in container with interactive terminal
- `agent-zero` - Container name
- `claude-pro` - Command to run (no `--` needed)

The `--` separator is only needed when you want to pass options that might conflict with docker exec options. For simple commands like `claude-pro`, it's not needed.

## Quick Test

To verify Claude Code is working:
```bash
docker exec -it agent-zero claude-pro --version
```

## Interactive vs Non-Interactive

**Interactive (for OAuth):**
```bash
docker exec -it agent-zero claude-pro
```

**Non-interactive (with prompt):**
```bash
docker exec agent-zero claude-pro -p "your prompt here"
```

## Troubleshooting

**If command not found:**
```bash
# Check if command exists
docker exec agent-zero which claude-pro

# Check PATH
docker exec agent-zero bash -c "export PATH=\"\$HOME/.local/bin:\$PATH\" && which claude-pro"
```

**If OAuth URL doesn't appear:**
- Make sure you're using `claude-pro` (not `claude`)
- Check that API keys are unset: `docker exec agent-zero env | grep ANTHROPIC`
