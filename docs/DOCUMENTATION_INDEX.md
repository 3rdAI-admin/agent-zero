# Agent Zero Documentation Index

## Quick Start

- **[Quick Reference](./QUICK_REFERENCE.md)** - Command cheat sheet and quick access
- **[Complete Setup Guide](./COMPLETE_SETUP_GUIDE.md)** - Full setup with all features
- **[Setup Summary](./guides/SETUP_SUMMARY.md)** - Current setup status and verification

## Core Documentation

### Installation & Setup
- **[Installation Guide](./installation.md)** - Basic installation instructions (upstream Docker image)
- **[Native Installation](./NATIVE_INSTALLATION.md)** - Installation without Docker (native Kali, port 8000)
- **[Complete Setup Guide](./COMPLETE_SETUP_GUIDE.md)** - Full feature setup (VNC, Claude Code, Security)
- **[Google Account & Gmail Setup](./setup/GOOGLE_ACCOUNT_SETUP.md)** - Google Gemini API key and Gmail (email) credentials; persistence of settings
- **[Google Workspace MCP container](./setup/GOOGLE_WORKSPACE_MCP_CONTAINER.md)** - Containerized Gmail/Drive/Docs/Sheets/Calendar MCP; service `workspace_mcp`, URL `http://workspace_mcp:8889/mcp`

### Features & Integration
- **[VNC Desktop Access](./VNC_ACCESS.md)** - GUI environment setup and usage
- **[Claude Code Integration](./CLAUDE_CODE_INTEGRATION.md)** - AI coding assistant integration
- **[Security Tools Setup](./guides/SECURITY_SETUP.md)** - Network scanning and pen testing tools
- **[Connectivity](./connectivity.md)** - External API, MCP server, A2A protocol

### Usage
- **[Usage Guide](./usage.md)** - How to use Agent Zero
- **[Architecture](./architecture.md)** - System architecture and design
- **[Extensibility](./extensibility.md)** - Creating custom extensions

### Development
- **[Development Setup](./setup/dev-setup.md)** - Local dev environment (IDE, venv, RFC, Docker)
- **[Codebase Index](../.planning/codebase/CODEBASE_INDEX.md)** - Entry points, API modules, tools, extension points (quick lookup)
- **[Testing and CI](./guides/TESTING_AND_CI.md)** - Local verification script, CI workflow, E2E testing
- **[MCP Setup](./mcp_setup.md)** - Model Context Protocol configuration

### Troubleshooting
- **[Troubleshooting](./troubleshooting.md)** - Common issues and solutions
- **[VNC Troubleshooting](./troubleshooting/VNC_TROUBLESHOOTING.md)** - VNC-specific issues

## Feature-Specific Guides

### VNC Desktop
- **[VNC Access Guide](./VNC_ACCESS.md)** - Complete VNC documentation
- **[VNC Troubleshooting](./troubleshooting/VNC_TROUBLESHOOTING.md)** - VNC issues and fixes
- **[VNC Password Fix](./troubleshooting/VNC_PASSWORD_FIX.md)** - Password configuration

### Claude Code
- **[Claude Code Integration](./CLAUDE_CODE_INTEGRATION.md)** - Complete integration guide
- **[How to Use claude-pro-yolo](./guides/HOW_TO_USE_CLAUDE_PRO_YOLO.md)** - YOLO mode guide
- **[Setup Claude OAuth](./guides/SETUP_CLAUDE_OAUTH.md)** - OAuth authentication setup

### Security Tools
- **[Security Setup](./guides/SECURITY_SETUP.md)** - Security tools installation
- **[Penetration Testing ROE](./guides/PEN_TESTING_ROE.md)** - Rules of engagement for pen testing (Agent Zero + Archon)
- **[Quick Start Security](./guides/QUICK_START_SECURITY.md)** - Security testing quick start
- **[Burp Suite Integration](./integration/BURP_SUITE_INTEGRATION.md)** - Burp Suite DAST testing (ARM64)

### Integration
- **[Agent Zero + Claude Integration](./integration/AGENT_ZERO_CLAUDE_INTEGRATION.md)** - Technical integration
- **[Agent Zero for ZeroClaw Integrators](./AGENT_ZERO_FOR_ZEROCLAW_INTEGRATORS.md)** - API, MCP, A2A entrypoints and constraints for ZeroClaw
- **[Integration Confirmed](./integration/INTEGRATION_CONFIRMED.md)** - Integration verification
- **[Integration Test Results](./integration/INTEGRATION_TEST_RESULTS.md)** - Test results

## Documentation by Task

### I want to...
- **Set up Agent Zero**: [Complete Setup Guide](./COMPLETE_SETUP_GUIDE.md)
- **Access the desktop**: [VNC Access Guide](./VNC_ACCESS.md)
- **Use Claude Code**: [Claude Code Integration](./CLAUDE_CODE_INTEGRATION.md)
- **Run security scans**: [Security Setup](./guides/SECURITY_SETUP.md)
- **Follow pen test ROE (Agent Zero / Archon)**: [Penetration Testing ROE](./guides/PEN_TESTING_ROE.md)
- **Connect remotely (API/MCP/A2A)**: [Connectivity](./connectivity.md)
- **Use Google Workspace MCP (Gmail, Drive, etc.) in Docker**: [Google Workspace MCP container](./setup/GOOGLE_WORKSPACE_MCP_CONTAINER.md) · [MCP Setup](./guides/mcp-setup.md)
- **Integrate ZeroClaw with Agent Zero**: [Agent Zero for ZeroClaw Integrators](./AGENT_ZERO_FOR_ZEROCLAW_INTEGRATORS.md)
- **MCP in Cursor (HTTP/HTTPS, cert fix)**: [MCP Cursor Remediation](./MCP_CURSOR_REMEDIATION.md) · [MCP Client Connection](./MCP_CLIENT_CONNECTION.md)
- **Troubleshoot issues**: [Troubleshooting](./troubleshooting.md)
- **Find a command**: [Quick Reference](./QUICK_REFERENCE.md)
- **Understand architecture**: [Architecture](./architecture.md)
- **Extend functionality**: [Extensibility](./extensibility.md)
- **Coordinate Archon tasks with Agent Zero (A0 SIP)**: [A0 SIP Workflow](./guides/A0_SIP_WORKFLOW.md)
- **Run tests or verify before a PR**: [Testing and CI](./guides/TESTING_AND_CI.md)

## Archive

Historical and superseded documentation is in [archive/](./archive/). These documents are retained for reference but may describe outdated workflows.

## External Resources

- [Agent Zero Website](https://agent-zero.ai)
- [GitHub Repository](https://github.com/agent0ai/agent-zero)
- [Discord Community](https://discord.gg/B8KZKNsPpj)
- [DeepWiki Documentation](https://deepwiki.com/agent0ai/agent-zero)
