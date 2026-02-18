# Agent Zero + Claude Code Quick Start

## ✅ Status

Claude Code is now **installed** in the container!

## How Agent Zero Uses Claude Code

Agent Zero can invoke Claude Code using its `code_execution_tool`. Here's how it works:

### Basic Usage

When you ask Agent Zero to use Claude Code, it will execute:

```bash
claude-pro "your question or task"
```

### Example: User → Agent Zero → Claude Code

**You ask Agent Zero:**
> "Use Claude Code to write a Python function that calculates factorial"

**Agent Zero responds with:**
```json
{
    "thoughts": [
        "User wants a factorial function",
        "I'll use Claude Code to generate it",
        "Then execute the code to verify"
    ],
    "headline": "Generating factorial function with Claude Code",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro 'Write a Python function that calculates factorial of a number. Include error handling for negative numbers.'"
    }
}
```

**Claude Code responds** → Agent Zero captures the response → Agent Zero can then execute the code.

## Complete Workflow Example

**You:** "Create a web scraper using Claude Code"

**Agent Zero's actions:**

1. **Calls Claude Code:**
   ```json
   {
       "tool_name": "code_execution_tool",
       "tool_args": {
           "runtime": "terminal",
           "session": 0,
           "code": "claude-pro 'Write a Python web scraper using requests and BeautifulSoup'"
       }
   }
   ```

2. **Executes the generated code:**
   ```json
   {
       "tool_name": "code_execution_tool",
       "tool_args": {
           "runtime": "python",
           "session": 1,
           "code": "[code from Claude Code]"
       }
   }
   ```

3. **Reports results back to you**

## How to Use

### Via Agent Zero Web UI

1. Open http://localhost:8888
2. Ask Agent Zero: **"Use Claude Code (claude-pro) to [your task]"**
3. Agent Zero will automatically invoke Claude Code

### Example Prompts

✅ **Good:**
- "Use Claude Code to generate a REST API client"
- "Ask Claude Code to review this code: [code]"
- "Have Claude Code help debug: [error]"

❌ **Less clear:**
- "Use Claude" (which command?)
- "Generate code" (doesn't specify Claude Code)

## Important Notes

### 1. Use `claude-pro`
- Always specify `claude-pro` in your instructions
- Uses your Pro subscription (OAuth) - **no API costs**
- `claude` uses API keys - **costs money**

### 2. OAuth Authentication
- Claude Code needs OAuth authentication
- Config is saved in `./claude-config` (persists across restarts)
- If not authenticated, use VNC to complete OAuth:
  - Connect: `vnc://localhost:5901`
  - Open terminal
  - Run: `claude-pro`
  - Complete OAuth in browser

### 3. PATH Configuration
- Claude Code is at `/root/.local/bin/claude`
- Symlinks created at `/usr/local/bin/claude` and `/usr/local/bin/claude-pro`
- PATH updated in `.bashrc` for new shells

## Testing the Integration

**Test 1: Simple Question**
```
You: "Use Claude Code to explain what Python decorators are"
Agent Zero: [invokes claude-pro, returns explanation]
```

**Test 2: Code Generation**
```
You: "Use Claude Code to write a function that validates email addresses"
Agent Zero: [gets code from Claude Code, executes it, shows results]
```

**Test 3: Code Review**
```
You: "Use Claude Code to review this code for security issues: [paste code]"
Agent Zero: [gets review from Claude Code, reports findings]
```

## Troubleshooting

### Claude Code Not Found
```bash
# Check installation
docker exec agent-zero bash -c 'export PATH="$HOME/.local/bin:$PATH" && which claude-pro'

# If missing, reinstall
docker exec agent-zero bash -c 'curl -fsSL https://claude.ai/install.sh | bash'
```

### OAuth Required
If Claude Code prompts for authentication:
1. Connect via VNC: `vnc://localhost:5901` (password: `vnc123`)
2. Open terminal
3. Run: `claude-pro`
4. Complete OAuth flow

### Agent Zero Can't Find Claude Code
Make sure your prompt includes:
- "Use Claude Code" or "Use claude-pro"
- Agent Zero will add PATH automatically, but being explicit helps

## Summary

✅ **Claude Code is installed**
✅ **Symlinks created** (`claude` and `claude-pro`)
✅ **PATH configured**
✅ **Ready for Agent Zero to use**

**Next Steps:**
1. Complete OAuth authentication (if not done)
2. Test with Agent Zero: "Use Claude Code to [task]"
3. Monitor Agent Zero's tool calls to see how it invokes Claude Code

Agent Zero can now leverage Claude Code's AI capabilities as part of its autonomous task execution!
