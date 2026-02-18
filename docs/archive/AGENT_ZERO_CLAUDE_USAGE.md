# How Agent Zero Uses Claude Code

## Overview

Agent Zero can interact with Claude Code (installed in the same container) using its built-in `code_execution_tool`. This allows Agent Zero to leverage Claude Code's AI-powered coding assistance as part of its autonomous task execution.

## How It Works

### Basic Mechanism

Agent Zero uses the `code_execution_tool` with `runtime: "terminal"` to execute shell commands, including Claude Code:

```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro 'your question or task'"
    }
}
```

## Practical Examples

### Example 1: Code Generation

**User asks Agent Zero:**
> "Generate a Python script to parse JSON files using Claude Code"

**Agent Zero's response:**
```json
{
    "thoughts": [
        "User wants a Python JSON parser script",
        "I'll use Claude Code to generate the code",
        "Then execute it to verify it works"
    ],
    "headline": "Generating JSON parser using Claude Code",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro 'Write a Python function that reads a JSON file, parses it, and returns the data as a dictionary. Include error handling for invalid JSON and file not found errors.'"
    }
}
```

### Example 2: Code Review

**User asks Agent Zero:**
> "Review this code for security vulnerabilities: [code snippet]"

**Agent Zero's response:**
```json
{
    "thoughts": [
        "User wants security review",
        "Claude Code can analyze code for vulnerabilities",
        "I'll pass the code to Claude Code for analysis"
    ],
    "headline": "Security review using Claude Code",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro 'Review this Python code for security vulnerabilities and suggest fixes: [code]'"
    }
}
```

### Example 3: Debugging

**User asks Agent Zero:**
> "Debug this error: ImportError: No module named 'requests'"

**Agent Zero's response:**
```json
{
    "thoughts": [
        "ImportError indicates missing module",
        "I'll ask Claude Code for debugging help",
        "Then install the missing package"
    ],
    "headline": "Debugging import error with Claude Code",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro 'How do I fix ImportError: No module named requests in Python? Provide installation command and verify it works.'"
    }
}
```

## Complete Workflow Example

**User asks Agent Zero:**
> "Create a web scraper that extracts product prices from an e-commerce site"

**Agent Zero's multi-step approach:**

1. **Ask Claude Code for design:**
```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro 'Design a Python web scraper using requests and BeautifulSoup that extracts product names and prices from an e-commerce website. Include error handling and rate limiting.'"
    }
}
```

2. **Execute the generated code:**
```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "python",
        "session": 1,
        "code": "[code from Claude Code's response]"
    }
}
```

3. **Refine if needed:**
```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro 'Improve this scraper to handle dynamic content and add retry logic: [code]'"
    }
}
```

## Key Points

### 1. Use `claude-pro` (Not `claude`)
- `claude-pro` uses your Pro subscription (OAuth) - **no API costs**
- `claude` uses API keys - **costs per use**
- Always specify `claude-pro` in your instructions to Agent Zero

### 2. Session Management
- Use different `session` numbers for different conversations
- Session 0: Claude Code interactions
- Session 1: Python code execution
- Session 2: Other terminal commands

### 3. Output Handling
- Claude Code's output is captured by Agent Zero
- Agent Zero can parse and use Claude Code's responses
- Large outputs may be truncated - check logs if needed

### 4. Interactive Sessions
For longer conversations with Claude Code:

```json
// Start interactive session
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro"
    }
}

// Send follow-up (using input_tool)
{
    "tool_name": "input_tool",
    "tool_args": {
        "session": 0,
        "keyboard": "Can you explain this part in more detail?"
    }
}
```

## Best Practices for Users

When asking Agent Zero to use Claude Code:

1. **Be explicit**: "Use Claude Code to..." or "Ask Claude Code..."
2. **Specify `claude-pro`**: Remind Agent Zero to use `claude-pro` not `claude`
3. **Provide context**: Include relevant code, error messages, or requirements
4. **Request specific format**: Ask for executable code, explanations, or reviews

## Example User Prompts

✅ **Good prompts:**
- "Use Claude Code (claude-pro) to generate a REST API client in Python"
- "Ask Claude Code to review this function for performance issues: [code]"
- "Have Claude Code help debug this error: [error message]"

❌ **Less effective:**
- "Use Claude" (unclear - which command?)
- "Generate code" (doesn't specify Claude Code)
- "Fix this" (no context about using Claude Code)

## Troubleshooting

### Claude Code Not Found
If Agent Zero reports `claude-pro: command not found`:

```bash
# Check installation
docker exec agent-zero bash -c 'export PATH="$HOME/.local/bin:$PATH" && which claude-pro'

# Reinstall if needed
docker exec agent-zero bash -c 'curl -fsSL https://claude.ai/install.sh | bash'
```

### OAuth Issues
If Claude Code prompts for authentication:
- OAuth tokens are stored in `/root/.config/claude-code/` (volume-mounted)
- Re-authenticate via VNC if tokens expire
- See `CLAUDE_CODE_AUTH.md` for authentication steps

### Output Truncation
If Claude Code's response is cut off:
- Check Agent Zero logs: `docker logs agent-zero`
- Use `runtime: "output"` to wait for complete response
- Break complex requests into smaller parts

## Summary

Agent Zero integrates Claude Code seamlessly by:
1. **Invoking Claude Code** via `code_execution_tool` with terminal runtime
2. **Capturing responses** and using them in subsequent tool calls
3. **Combining capabilities** - Claude Code generates code, Agent Zero executes it
4. **Managing sessions** - separate sessions for different tasks

This creates a powerful workflow where Agent Zero can:
- Get AI-powered code suggestions from Claude Code
- Execute and test the generated code
- Iterate and refine based on results
- Complete complex tasks autonomously

## Next Steps

1. **Test the integration**: Ask Agent Zero to use Claude Code for a simple task
2. **Monitor usage**: Check logs to see how Agent Zero invokes Claude Code
3. **Refine prompts**: Adjust your instructions based on results
4. **Combine tools**: Use Claude Code with other Agent Zero tools for complex workflows
