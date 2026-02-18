# OWASP Top Ten Web Application Security Testing Tools

This document lists all installed tools for testing against the OWASP Top Ten (2021) vulnerabilities.

## Installed Tools by OWASP Top Ten Category

### A01:2021 – Broken Access Control

**Tools:**
- **OWASP ZAP** (`zaproxy`) - Automated security testing for finding vulnerabilities
- **Burp Suite** (`burpsuite`) - Web vulnerability scanner and proxy
- **Nuclei** (`nuclei`) - Fast vulnerability scanner with custom templates
- **ffuf** (`ffuf`) - Fast web fuzzer for directory/file discovery
- **feroxbuster** (`feroxbuster`) - Fast recursive content discovery tool

**Usage Examples:**
```bash
# OWASP ZAP baseline scan
zaproxy -quickurl http://target.com -quickprogress

# Burp Suite (GUI - requires X11 forwarding or headless mode)
burpsuite

# Nuclei scan for access control issues
nuclei -u http://target.com -t /usr/share/nuclei-templates/authorization/

# Directory brute forcing
ffuf -w /usr/share/wordlists/dirb/common.txt -u http://target.com/FUZZ
```

### A02:2021 – Cryptographic Failures

**Tools:**
- **sslscan** (`sslscan`) - SSL/TLS scanner
- **sslyze** (`sslyze`) - SSL/TLS configuration analyzer
- **testssl.sh** (`testssl.sh`) - Comprehensive SSL/TLS testing
- **Nuclei** - SSL/TLS vulnerability templates

**Usage Examples:**
```bash
# SSL/TLS scanning
sslscan target.com:443
sslyze target.com:443
testssl.sh target.com

# Nuclei SSL checks
nuclei -u https://target.com -t /usr/share/nuclei-templates/ssl/
```

### A03:2021 – Injection

**Tools:**
- **SQLMap** (`sqlmap`) - SQL injection testing
- **NoSQLMap** (`nosqlmap`) - NoSQL injection testing
- **Commix** (`commix`) - Command injection testing
- **SSRFmap** (`ssrfmap`) - Server-Side Request Forgery testing
- **Nuclei** - Injection vulnerability templates

**Usage Examples:**
```bash
# SQL injection testing
sqlmap -u "http://target.com/page?id=1" --batch --dbs

# NoSQL injection
nosqlmap -u http://target.com/api/login

# Command injection
commix -u "http://target.com/page?cmd=test"

# SSRF testing
ssrfmap -r request.txt -p url

# Nuclei injection checks
nuclei -u http://target.com -t /usr/share/nuclei-templates/injections/
```

### A04:2021 – Insecure Design

**Tools:**
- **OWASP ZAP** - Design flaw detection
- **Burp Suite** - Business logic testing
- **Nuclei** - Design vulnerability templates

**Usage:**
- Manual testing with ZAP/Burp Suite
- Custom Nuclei templates for design flaws

### A05:2021 – Security Misconfiguration

**Tools:**
- **Nikto** (`nikto`) - Web server scanner
- **Nuclei** - Misconfiguration templates
- **retire.js** (`retire`) - Outdated JavaScript library detection
- **WhatWeb** (`whatweb`) - Web technology identifier

**Usage Examples:**
```bash
# Web server misconfiguration scan
nikto -h http://target.com

# Technology detection
whatweb http://target.com

# Outdated component detection
retire --js --jspath /path/to/webapp

# Nuclei misconfiguration checks
nuclei -u http://target.com -t /usr/share/nuclei-templates/misconfiguration/
```

### A06:2021 – Vulnerable and Outdated Components

**Tools:**
- **retire.js** (`retire`) - JavaScript library vulnerability scanner
- **Nuclei** - Component vulnerability templates
- **Amass** (`amass`) - Attack surface mapping
- **Subfinder** (`subfinder`) - Subdomain discovery

**Usage Examples:**
```bash
# JavaScript library vulnerabilities
retire --js --jspath /path/to/webapp

# Component scanning with Nuclei
nuclei -u http://target.com -t /usr/share/nuclei-templates/cves/

# Attack surface mapping
amass enum -d target.com
subfinder -d target.com
```

### A07:2021 – Identification and Authentication Failures

**Tools:**
- **Hydra** (`hydra`) - Login brute forcer
- **Medusa** (`medusa`) - Parallel login cracker
- **Burp Suite** - Authentication testing
- **OWASP ZAP** - Authentication bypass testing
- **Nuclei** - Authentication vulnerability templates

**Usage Examples:**
```bash
# Login brute forcing
hydra -l admin -P passwords.txt http-post-form://target.com/login:user=^USER^&pass=^PASS^:failed

# Nuclei auth checks
nuclei -u http://target.com -t /usr/share/nuclei-templates/authentication/
```

### A08:2021 – Software and Data Integrity Failures

**Tools:**
- **OWASP ZAP** - Integrity checking
- **Nuclei** - Integrity vulnerability templates

**Usage:**
- Manual testing with ZAP
- Custom Nuclei templates

### A09:2021 – Security Logging and Monitoring Failures

**Tools:**
- **OWASP ZAP** - Logging analysis
- **Burp Suite** - Monitoring testing
- **Nuclei** - Logging vulnerability templates

**Usage:**
- Manual testing and analysis
- Custom Nuclei templates

### A10:2021 – Server-Side Request Forgery (SSRF)

**Tools:**
- **SSRFmap** (`ssrfmap`) - SSRF exploitation framework
- **Nuclei** - SSRF vulnerability templates
- **Burp Suite** - SSRF testing

**Usage Examples:**
```bash
# SSRF testing
ssrfmap -r request.txt -p url

# Nuclei SSRF checks
nuclei -u http://target.com -t /usr/share/nuclei-templates/ssrf/
```

## Cross-Category Tools

### XSS (Cross-Site Scripting) Testing

**Tools:**
- **XSStrike** (`xsstrike`) - Advanced XSS detection
- **Dalfox** (`dalfox`) - Fast XSS finder
- **Nuclei** - XSS templates

**Usage Examples:**
```bash
# XSS testing
xsstrike -u "http://target.com/page?param=test"
dalfox url http://target.com/page?param=test

# Nuclei XSS checks
nuclei -u http://target.com -t /usr/share/nuclei-templates/xss/
```

### Directory/File Discovery

**Tools:**
- **ffuf** (`ffuf`) - Fast web fuzzer
- **feroxbuster** (`feroxbuster`) - Recursive content discovery
- **gobuster** (`gobuster`) - Directory/file brute forcer
- **dirb** (`dirb`) - Web content scanner

**Usage Examples:**
```bash
# Directory brute forcing
ffuf -w /usr/share/wordlists/dirb/common.txt -u http://target.com/FUZZ
feroxbuster -u http://target.com -w /usr/share/wordlists/dirb/common.txt
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt
dirb http://target.com
```

### API Testing

**Tools:**
- **Burp Suite** - API security testing
- **OWASP ZAP** - API scanning
- **Nuclei** - API vulnerability templates
- **ffuf** - API endpoint fuzzing

## Complete Testing Workflow

### 1. Reconnaissance
```bash
# Subdomain discovery
amass enum -d target.com
subfinder -d target.com

# Technology detection
whatweb http://target.com
```

### 2. Discovery
```bash
# Directory/file discovery
ffuf -w wordlist.txt -u http://target.com/FUZZ
feroxbuster -u http://target.com
```

### 3. Vulnerability Scanning
```bash
# Automated scanning
zaproxy -quickurl http://target.com -quickprogress
nikto -h http://target.com
nuclei -u http://target.com -t /usr/share/nuclei-templates/
```

### 4. Manual Testing
```bash
# Start Burp Suite proxy
burpsuite
# Configure browser to use proxy: 127.0.0.1:8080
```

### 5. Specific Vulnerability Testing
```bash
# SQL injection
sqlmap -u "http://target.com/page?id=1" --batch

# XSS
xsstrike -u "http://target.com/page?param=test"
dalfox url http://target.com/page?param=test

# SSRF
ssrfmap -r request.txt -p url

# Command injection
commix -u "http://target.com/page?cmd=test"
```

## Tool Locations

- **System Tools:** `/usr/bin/` or `/usr/sbin/`
- **Custom Tools:** `/opt/` (nosqlmap, ssrfmap, xsstrike, dalfox)
- **Wrapper Scripts:** `/usr/local/bin/` (nosqlmap, ssrfmap, xsstrike)
- **Nuclei Templates:** `/usr/share/nuclei-templates/`
- **Wordlists:** `/usr/share/wordlists/`

## Using with Agent Zero

You can ask Agent Zero to:

1. **Perform OWASP Top Ten testing:**
   ```
   Test http://target.com for OWASP Top Ten vulnerabilities including SQL injection, XSS, and authentication issues
   ```

2. **Run specific scans:**
   ```
   Run a Nikto scan against http://target.com to check for security misconfigurations
   ```

3. **Test for specific vulnerabilities:**
   ```
   Test http://target.com/api/login for SQL injection vulnerabilities using SQLMap
   ```

4. **Comprehensive assessment:**
   ```
   Perform a complete OWASP Top Ten security assessment of http://target.com including all injection types, authentication, and misconfiguration testing
   ```

## Additional Resources

- [OWASP Top Ten](https://owasp.org/Top10/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
- [Burp Suite Documentation](https://portswigger.net/burp/documentation)
