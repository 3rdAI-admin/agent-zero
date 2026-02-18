# Claude Code Installation & Usage Guide

## Installation Status

✅ **Claude Code v2.1.19** successfully installed in Agent Zero container

## Installation Details

- **Location:** `/root/.local/bin/claude`
- **Symlink:** `/usr/local/bin/claude` (accessible system-wide)
- **PATH:** Configured in `/root/.bashrc` and `/root/.profile`
- **Version:** 2.1.19

## What is Claude Code?

Claude Code is an AI-powered coding assistant that runs in your terminal. It provides:
- Interactive coding assistance
- Code generation and explanation
- Terminal-based AI coding support
- Integration with your development workflow

## Usage

### Basic Commands

```bash
# Show version
claude --version

# Show help
claude --help

# Start interactive session
claude

# Non-interactive mode (print output)
claude -p "your prompt here"

# Add directories for tool access
claude --add-dir /path/to/directory
```

### First-Time Setup

On first use, Claude Code will prompt you to authenticate:
1. Run `claude` in the terminal
2. Follow the OAuth authentication flow
3. Log in with your Anthropic account or Claude subscription
4. Your API key is securely stored locally

**Requirements:**
- Claude subscription (Pro, Max, Teams, or Enterprise)
- Or Claude Console account
- Internet connection

### Using with Agent Zero

You can use Claude Code via Agent Zero's code execution tool:

**Example prompts:**
```
Run Claude Code to help with a coding task
```

```
Use Claude Code to generate Python code for network scanning
```

```
Ask Claude Code to explain a security concept
```

### Integration Examples

**Via Terminal:**
```bash
# Interactive coding session
claude

# Quick code generation
claude -p "Write a Python script to scan ports using nmap"

# Code explanation
claude -p "Explain how SQL injection works"
```

**Via Agent Zero:**
```
Use Claude Code to help write a penetration testing script
```

## Features

- **Interactive Mode:** Chat with Claude in your terminal
- **Code Generation:** Generate code snippets and scripts
- **Code Explanation:** Get explanations of code and concepts
- **Directory Access:** Grant access to specific directories for context
- **Non-Interactive Mode:** Use `-p/--print` for scripted usage

## Configuration

Claude Code stores its configuration and authentication in:
- `~/.config/claude-code/` (configuration)
- Authentication tokens are stored securely locally

## Troubleshooting

**If `claude` command not found:**
```bash
export PATH="$HOME/.local/bin:$PATH"
claude --version
```

**If authentication fails:**
- Ensure you have a valid Claude subscription
- Check internet connectivity
- Verify Anthropic account credentials

**Check installation:**
```bash
which claude
claude --version
```

## Additional Resources

- Official Documentation: https://code.claude.com/docs
- Anthropic Docs: https://docs.anthropic.com/en/docs/claude-code
- Installation Guide: https://claude.ai/install.sh

## Status

✅ **Claude Code is installed and ready to use**  
✅ **Accessible via `claude` command**  
✅ **Ready for authentication on first use**

---

**Installed:** January 25, 2026  
**Version:** 2.1.19  
**Container:** agent-zero
