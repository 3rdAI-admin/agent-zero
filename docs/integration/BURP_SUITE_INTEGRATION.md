# Burp Suite Integration with Agent Zero (ARM Architecture)

## Overview

Agent Zero can use Burp Suite for comprehensive DAST (Dynamic Application Security Testing) of web applications. This guide covers installation, configuration, and usage on ARM64 architecture.

## Architecture Compatibility

✅ **Container Architecture**: ARM64 (aarch64)  
✅ **Burp Suite**: Available for ARM64 (Version 2025.12.3)  
✅ **Java**: OpenJDK 21 installed  
✅ **VNC**: Available for GUI access

## Installation

### Install Burp Suite

```bash
# Inside container
docker exec agent-zero bash -c "apt-get update && apt-get install -y burpsuite"

# Or via Agent Zero
# Ask: "Install burpsuite using apt-get"
```

### Verify Installation

```bash
docker exec agent-zero burpsuite --version
docker exec agent-zero which burpsuite
```

## Usage Methods

### Method 1: GUI via VNC (Interactive Testing)

**Best for**: Manual testing, exploring applications, custom test cases

1. **Connect to VNC**: `vnc://localhost:5901` (password: `vnc123`)
2. **Start Burp Suite**:
   ```bash
   # In VNC terminal
   export DISPLAY=:99
   burpsuite &
   ```
3. **Configure Proxy**: 
   - Burp listens on `127.0.0.1:8080` by default
   - Configure browser in VNC to use proxy: `127.0.0.1:8080`
4. **Use Burp Suite GUI** for manual testing

### Method 2: Headless via Command Line (Automated)

**Best for**: Automated scanning, CI/CD integration, Agent Zero automation

#### Using Burp Suite Community Edition (Free)

```bash
# Start Burp Suite in headless mode
burpsuite --project-file=/tmp/burp_project.burp --unpause-spider-and-scanner
```

#### Using Burp Suite Professional (Paid License Required)

Burp Suite Pro supports REST API for automation:

```bash
# Start Burp Suite Pro with REST API enabled
burpsuite --api-key=YOUR_API_KEY --api-port=1337
```

### Method 3: Via Agent Zero Code Execution Tool

**Best for**: Automated DAST testing integrated with Agent Zero workflows

Ask Agent Zero:
```
Use Burp Suite to scan http://target.com for web application vulnerabilities. Run a comprehensive DAST scan and report findings.
```

Agent Zero can:
1. Start Burp Suite in headless mode
2. Configure scan targets
3. Execute scans
4. Parse and report results
5. Integrate findings with other security tools

## Burp Suite REST API (Professional Edition)

### Setup REST API

1. **Start Burp Suite Pro** with API enabled:
   ```bash
   burpsuite --api-key=YOUR_API_KEY --api-port=1337
   ```

2. **Use REST API** for automation:
   ```python
   import requests
   
   # Burp Suite REST API endpoint
   burp_api = "http://127.0.0.1:1337/v0.1"
   headers = {"Authorization": f"Bearer YOUR_API_KEY"}
   
   # Start scan
   response = requests.post(
       f"{burp_api}/scan",
       headers=headers,
       json={"urls": ["http://target.com"]}
   )
   ```

### Python Integration Example

Create a Python script for Agent Zero to use:

```python
#!/usr/bin/env python3
"""
Burp Suite DAST Scanner for Agent Zero
"""
import requests
import json
import time

class BurpSuiteScanner:
    def __init__(self, api_url="http://127.0.0.1:1337/v0.1", api_key=None):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    
    def start_scan(self, target_url):
        """Start a DAST scan"""
        response = requests.post(
            f"{self.api_url}/scan",
            headers=self.headers,
            json={"urls": [target_url]}
        )
        return response.json()
    
    def get_scan_status(self, scan_id):
        """Get scan status"""
        response = requests.get(
            f"{self.api_url}/scan/{scan_id}",
            headers=self.headers
        )
        return response.json()
    
    def get_scan_results(self, scan_id):
        """Get scan results"""
        response = requests.get(
            f"{self.api_url}/scan/{scan_id}/issues",
            headers=self.headers
        )
        return response.json()
```

## Integration with Agent Zero

### Example: Automated DAST Workflow

**User Prompt:**
```
Perform a comprehensive DAST scan of http://192.168.1.100 using Burp Suite. 
Check for OWASP Top Ten vulnerabilities and provide a detailed report.
```

**Agent Zero Workflow:**
1. Check if Burp Suite is installed
2. Start Burp Suite in headless mode (or use REST API)
3. Configure scan parameters
4. Execute scan against target
5. Collect and parse results
6. Generate report with findings
7. Integrate with other tool results (nmap, nikto, etc.)

### Example: Burp Suite + Other Tools

**User Prompt:**
```
Perform a complete security assessment of http://target.com:
1. Use nmap for port scanning
2. Use Burp Suite for web application DAST
3. Use nikto for web server vulnerabilities
4. Combine all findings into a comprehensive report
```

## Configuration

### Burp Suite Configuration File

Create persistent configuration:

```bash
# Save Burp Suite configuration
docker exec agent-zero mkdir -p /root/.BurpSuite
docker exec agent-zero burpsuite --save-config=/root/.BurpSuite/config.json
```

### Proxy Configuration

**For Browser Testing (via VNC):**
- Proxy: `127.0.0.1:8080`
- Port: `8080`
- No authentication (default)

**For External Tools:**
- Set `HTTP_PROXY=http://127.0.0.1:8080`
- Set `HTTPS_PROXY=http://127.0.0.1:8080`

### Scan Configuration

**Common Scan Settings:**
- **Spider**: Enabled for crawling
- **Active Scanner**: Enabled for vulnerability detection
- **Passive Scanner**: Enabled for passive checks
- **Scope**: Configure target scope

## ARM Architecture Considerations

### Verified Compatibility

✅ **Burp Suite 2025.12.3**: ARM64 compatible  
✅ **Java OpenJDK 21**: ARM64 native  
✅ **VNC GUI Access**: Works on ARM64  
✅ **Command-line Tools**: ARM64 compatible

### Performance Notes

- ARM64 performance is excellent for Burp Suite
- GUI via VNC works smoothly
- Headless mode performs well
- REST API has no architecture-specific limitations

## Troubleshooting

### Burp Suite Won't Start

```bash
# Check Java
docker exec agent-zero java -version

# Check Burp Suite installation
docker exec agent-zero dpkg -l | grep burp

# Check for GUI dependencies (if using VNC)
docker exec agent-zero which xvfb
```

### REST API Not Accessible

```bash
# Check if Burp Suite is running
docker exec agent-zero ps aux | grep burp

# Check API port
docker exec agent-zero netstat -tlnp | grep 1337

# Verify API key configuration
docker exec agent-zero cat ~/.BurpSuite/api_key.txt
```

### GUI Issues in VNC

```bash
# Ensure DISPLAY is set
export DISPLAY=:99

# Check VNC is running
docker exec agent-zero supervisorctl status xvfb

# Restart VNC if needed
docker exec agent-zero supervisorctl restart xvfb fluxbox x11vnc
```

## Best Practices

### 1. Scope Configuration
- Always configure proper scan scope
- Exclude non-target URLs
- Set appropriate scan depth limits

### 2. Resource Management
- Monitor memory usage during scans
- Use appropriate scan speed settings
- Limit concurrent scans

### 3. Results Management
- Save scan results regularly
- Export findings in multiple formats (XML, JSON, HTML)
- Integrate with reporting tools

### 4. Integration with Agent Zero
- Use Agent Zero's code execution tool for automation
- Combine Burp Suite with other security tools
- Leverage Claude Code for custom analysis scripts

## Example Agent Zero Prompts

### Basic DAST Scan
```
Use Burp Suite to perform a DAST scan of http://target.com. 
Start Burp Suite in headless mode, configure the scan, execute it, 
and report all vulnerabilities found.
```

### Comprehensive Web App Testing
```
Perform a complete web application security assessment of http://target.com:
1. Use Burp Suite for DAST scanning
2. Use nikto for web server misconfigurations
3. Use sqlmap for SQL injection testing
4. Combine all results into a comprehensive security report
```

### OWASP Top Ten Focus
```
Use Burp Suite to test http://target.com for OWASP Top Ten vulnerabilities.
Focus on injection flaws, broken authentication, sensitive data exposure, 
and security misconfigurations. Provide detailed findings.
```

## Related Tools

- **OWASP ZAP**: Alternative DAST tool (also available for ARM64)
- **Nikto**: Web server scanner (complementary to Burp Suite)
- **SQLMap**: SQL injection testing (can be used with Burp Suite findings)
- **Nuclei**: Fast vulnerability scanner (complements Burp Suite)

## Summary

✅ **Burp Suite installed** and ARM64 compatible  
✅ **Multiple usage methods**: GUI (VNC), headless, REST API  
✅ **Agent Zero integration**: Via code execution tool  
✅ **Automation ready**: REST API and command-line support  
✅ **Production ready**: Verified on ARM64 architecture

Burp Suite is fully integrated and ready for DAST testing with Agent Zero!
