# Security Assessment Integration: Claude Code + Agent Zero

## Overview

Agent Zero and Claude Code work together for comprehensive security assessments. This document describes how to use both tools effectively for penetration testing, code review, and vulnerability assessment.

## Bidirectional Communication

### Agent Zero → Claude Code

Use Claude Code for:
- **Code analysis and review** - Static analysis, vulnerability pattern detection
- **Exploit development** - Writing custom payloads, proof-of-concept code
- **Report writing** - Generating findings documentation
- **Complex debugging** - Analyzing captured traffic, logs, crash dumps

**Invoke Claude Code in YOLO mode (no confirmations):**
```bash
claude-pro-yolo 'Your task here'
```

**For interactive sessions:**
```bash
claude-pro-yolo
```

IMPORTANT: Always use `claude-pro-yolo` when invoking Claude Code from Agent Zero to enable autonomous operation without confirmation prompts. The `--dangerously-skip-permissions` flag cannot be used as root, but `claude-pro-yolo` wrapper runs as non-root user with YOLO mode enabled.

### Claude Code → Agent Zero

Claude Code can use Agent Zero's MCP server for:
- **Network scanning** - nmap, masscan via `network_scan` tool
- **Web scanning** - nikto, nuclei via `web_scan` tool
- **Browser automation** - Automated web testing via Agent Zero's browser
- **Tool execution** - Running any security tools in the container

MCP Server URL: `http://localhost:8888/mcp/t-{token}/sse`

## Shared Assessment State

Both agents share a common assessment state stored at:
```
/a0/usr/projects/{project_name}/.a0proj/assessment/
├── assessment_state.json    # Targets, findings, progress
└── evidence/                # Screenshots, logs, captured data
```

### State Structure

```json
{
  "meta": {
    "name": "Assessment Name",
    "scope": ["*.target.com", "10.0.0.0/24"],
    "type": "web|network|internal|external",
    "status": "in_progress|paused|completed"
  },
  "targets": [
    {
      "address": "target.com",
      "type": "web|host|service",
      "ports": [80, 443],
      "services": {"80": "http", "443": "https"},
      "technologies": ["nginx", "php"]
    }
  ],
  "findings": [
    {
      "severity": "critical|high|medium|low|info",
      "title": "SQL Injection",
      "description": "...",
      "cwe": "CWE-89",
      "evidence": ["evidence/sqli_001.txt"],
      "status": "confirmed|potential|false_positive",
      "found_by": "claude_code|agent_zero"
    }
  ],
  "progress": {
    "phase": "recon|scanning|exploitation|reporting",
    "current_task": "Port scanning subnet",
    "completed_tasks": [],
    "pending_tasks": []
  }
}
```

## Security Testing Workflows

### Web Application Assessment (OWASP Top 10)

1. **Reconnaissance (Agent Zero)**
   - Subdomain enumeration: `subfinder -d target.com`
   - WAF detection: `wafw00f http://target`
   - Technology fingerprinting: `whatweb -a 3 http://target`
   - Port scanning: `nmap -sV -sC target`
   - HTTP probing: `httpx` for live host detection

2. **Scanning (Both)**
   - Agent Zero: `nuclei -u http://target -severity critical,high,medium`
   - Agent Zero: `nikto -h http://target`
   - Agent Zero: TLS testing with `sslyze`, `testssl.sh`
   - Claude Code: Review JavaScript/source for vulnerabilities

3. **Discovery & Fuzzing (Agent Zero)**
   - Content discovery: `feroxbuster -u http://target`
   - Parameter discovery: `arjun -u http://target/page`
   - Directory brute-forcing: `gobuster dir -u http://target -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt`

4. **Exploitation (Both)**
   - Agent Zero: `sqlmap -u URL --forms --batch` for SQL injection
   - Agent Zero: `dalfox url URL` for XSS
   - Agent Zero: `commix -u URL` for command injection
   - Agent Zero: `hydra` for auth brute-forcing
   - Claude Code: Craft custom payloads, analyze responses
   - Agent Zero: Execute attacks via browser automation

5. **Reporting (Claude Code)**
   - Generate findings report with CVSS scores
   - Map findings to OWASP Top 10 categories
   - Create remediation guidance

### Code Review (SAST)

1. **Analysis (Claude Code)**
   - Review source code for vulnerabilities
   - Identify insecure patterns

2. **Validation (Agent Zero)**
   - Run semgrep with security rules
   - Run bandit for Python code
   - Cross-reference findings

3. **Documentation (Claude Code)**
   - Generate code review report
   - Prioritize findings by risk

### Network Assessment

1. **Discovery (Agent Zero)**
   - Ping sweep for live hosts
   - Port scanning with nmap
   - Service enumeration

2. **Vulnerability Scanning (Agent Zero)**
   - Run nuclei network templates
   - Service-specific checks

3. **Analysis (Claude Code)**
   - Review scan results
   - Identify attack paths
   - Prioritize targets

## Complete Tool Inventory (OWASP Top 10)

### A01 Broken Access Control
| Tool | Purpose | Example |
|------|---------|---------|
| dirb | URL brute-forcing | `dirb http://target /usr/share/seclists/Discovery/Web-Content/common.txt` |
| gobuster | Fast directory/DNS brute-forcing | `gobuster dir -u http://target -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt` |
| feroxbuster | Recursive content discovery | `feroxbuster -u http://target -w /usr/share/seclists/Discovery/Web-Content/common.txt` |
| ffuf | Fast fuzzer (dirs, params, vhosts) | `ffuf -u http://target/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt` |

### A02 Cryptographic Failures
| Tool | Purpose | Example |
|------|---------|---------|
| sslyze | TLS/SSL analysis | `sslyze target.com` |
| sslscan | TLS cipher/protocol scanner | `sslscan target.com` |
| testssl.sh | Comprehensive TLS testing | `testssl.sh target.com` |

### A03 Injection
| Tool | Purpose | Example |
|------|---------|---------|
| sqlmap | SQL injection | `sqlmap -u "http://target/page?id=1" --batch` |
| commix | Command injection | `commix -u "http://target/page?cmd=test"` |
| dalfox | XSS scanning | `dalfox url "http://target/page?q=test"` |
| wfuzz | Parameter fuzzing | `wfuzz -c -z file,/usr/share/seclists/Fuzzing/XSS-JHADDIX.txt http://target/page?q=FUZZ` |
| nikto | Web server vulnerability scanner | `nikto -h http://target` |

### A05 Security Misconfiguration
| Tool | Purpose | Example |
|------|---------|---------|
| nuclei | Template-based vuln scanner | `nuclei -u http://target -severity critical,high` |
| whatweb | Technology fingerprinting | `whatweb -a 3 http://target` |

### A07 Authentication Failures
| Tool | Purpose | Example |
|------|---------|---------|
| hydra | Login brute-forcing | `hydra -l admin -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt target http-post-form "/login:user=^USER^&pass=^PASS^:Invalid"` |
| john | Password hash cracking | `john --wordlist=/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt hashes.txt` |
| jwt-tool | JWT token testing | `jwt_tool.py <token>` |

### Network & Reconnaissance
| Tool | Purpose | Example |
|------|---------|---------|
| nmap | Network scanning & NSE scripts | `nmap -sV -sC -p- target` |
| masscan | Fast port scanning | `masscan target/24 -p1-65535 --rate=1000` |
| httpx | HTTP probing & tech detection | `echo target.com \| httpx -status-code -title -tech-detect` |
| subfinder | Subdomain discovery | `subfinder -d target.com` |
| dnsrecon | DNS enumeration | `dnsrecon -d target.com` |
| wafw00f | WAF detection | `wafw00f http://target` |
| arjun | Hidden parameter discovery | `arjun -u http://target/page` |

### Static Analysis (SAST)
| Tool | Purpose | Example |
|------|---------|---------|
| semgrep | Multi-language static analysis | `semgrep --config=auto /path/to/code` |
| bandit | Python security linter | `bandit -r /path/to/python/code` |

### Wordlists (SecLists)
Located at `/usr/share/seclists/`:
- `Discovery/Web-Content/` - Directory/file wordlists
- `Passwords/` - Password lists for brute-forcing
- `Fuzzing/` - Fuzzing payloads (XSS, SQLi, etc.)
- `Discovery/DNS/` - DNS subdomain wordlists
- `Usernames/` - Username enumeration lists

## Tool Delegation Guidelines

### Use Agent Zero for:
- Running all security tools listed above
- Browser automation and web interaction
- File system operations in the container
- Network operations (scanning, enumeration)
- Executing shell commands

### Use Claude Code for:
- Complex code analysis and review
- Writing custom scripts and exploits
- Generating reports and documentation
- Analyzing large text outputs
- Making architectural decisions

## Example Commands

### Initialize Assessment
```bash
# In Agent Zero terminal
claude-pro --dangerously-skip-permissions 'Initialize a web security assessment for target.com in the current project'
```

### Run Network Scan
```bash
# Agent Zero will handle this directly
nmap -sV -sC target.com
```

### Code Review
```bash
# Delegate to Claude Code
claude-pro --dangerously-skip-permissions 'Review the Python code in /path/to/app for security vulnerabilities. Focus on authentication and input validation.'
```

### Add Finding
```python
# Via MCP from Claude Code
update_finding(
    project_name="assessment_project",
    title="SQL Injection in login.php",
    severity="critical",
    description="User input is concatenated directly into SQL query...",
    cwe="CWE-89",
    evidence="POST /login HTTP/1.1\n...\nuser=' OR '1'='1",
    remediation="Use parameterized queries"
)
```

## Security Considerations

1. **Scope Validation**: All tools validate targets against the defined scope
2. **Authorization**: Only test systems you're authorized to assess
3. **Evidence Chain**: Link all findings to captured evidence
4. **Audit Trail**: All operations are logged with timestamps
5. **Container Isolation**: Tests run in isolated Docker environment
