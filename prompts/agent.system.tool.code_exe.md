### code_execution_tool

execute terminal commands python nodejs code for computation or software tasks
place code in "code" arg; escape carefully and indent properly
select "runtime" arg: "terminal" "python" "nodejs" "output" "reset"
select "session" number, 0 default, others for multitasking
if code runs long, use "output" to wait, "reset" to kill process
use "pip" "npm" "apt-get" in "terminal" to install packages
to output, use print() or console.log()
if tool outputs error, adjust code before retrying; 
important: check code for placeholders or demo data; replace with real variables; don't reuse snippets
don't use with other tools except thoughts; wait for response before using others
check dependencies before running code
output may end with [SYSTEM: ...] information comming from framework, not terminal

**Claude Code Integration**: Claude Code (claude-pro) is installed and available in this container. Use it for AI-powered code generation, code review, debugging assistance, and technical questions.

**Usage**: Use `claude-pro-yolo` wrapper for autonomous operation (YOLO mode enabled):
```
claude-pro-yolo 'your task here'
```

**IMPORTANT**: Always use `claude-pro-yolo` (not `claude-pro --dangerously-skip-permissions`) when running as root. The `--dangerously-skip-permissions` flag cannot be used as root, but `claude-pro-yolo` wrapper runs Claude Code as a non-root user with YOLO mode enabled.

Example use cases:
- Code review: `claude-pro-yolo 'Review this code for security vulnerabilities'`
- Code generation: `claude-pro-yolo 'Write a Python function to parse Nmap XML'`
- Analysis: `claude-pro-yolo 'Analyze this error log and identify the root cause'`

Always use `claude-pro-yolo` for autonomous operation without confirmation prompts. Claude Code can generate code that you can then execute using this tool's python or nodejs runtime.
usage:

1 execute python code

~~~json
{
    "thoughts": [
        "Need to do...",
        "I can use...",
        "Then I can...",
    ],
    "headline": "Executing Python code to check current directory",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "python",
        "session": 0,
        "code": "import os\nprint(os.getcwd())",
    }
}
~~~

2 execute terminal command
~~~json
{
    "thoughts": [
        "Need to do...",
        "Need to install...",
    ],
    "headline": "Installing zip package via terminal",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "apt-get install zip",
    }
}
~~~

2.1 wait for output with long-running scripts
~~~json
{
    "thoughts": [
        "Waiting for program to finish...",
    ],
    "headline": "Waiting for long-running program to complete",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "output",
        "session": 0,
    }
}
~~~

2.2 reset terminal
~~~json
{
    "thoughts": [
        "code_execution_tool not responding...",
    ],
    "headline": "Resetting unresponsive terminal session",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "reset",
        "session": 0,
    }
}
~~~

3 use Claude Code for code review/generation (YOLO mode)
~~~json
{
    "thoughts": [
        "Need expert code analysis...",
        "Claude Code can help with this...",
    ],
    "headline": "Using Claude Code to review code for vulnerabilities",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "session": 0,
        "code": "claude-pro-yolo 'Review this Python code for security vulnerabilities and suggest fixes: def login(user, pwd): return db.query(f\"SELECT * FROM users WHERE user={user} AND pass={pwd}\")'"
    }
}
~~~
