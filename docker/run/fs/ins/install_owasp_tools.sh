#!/bin/bash
set -e

echo "====================INSTALLING OWASP TOP 10 PENETRATION TESTING TOOLS===================="

# Ensure Go environment is available for Go-based tools
export GOPATH=/root/go
export PATH=$PATH:/root/go/bin:/usr/local/go/bin

# Update package list once
apt-get update

# ============================================================================
# SECTION 1: APT Packages
# ============================================================================

echo "--- Installing APT-based security tools ---"

# A03 Injection Testing
echo "Installing sqlmap (SQL injection)..."
apt-get install -y --no-install-recommends sqlmap || echo "WARN: sqlmap install failed"

echo "Installing commix (command injection)..."
apt-get install -y --no-install-recommends commix || echo "WARN: commix install failed"

echo "Installing wfuzz (web fuzzer)..."
apt-get install -y --no-install-recommends wfuzz || echo "WARN: wfuzz install failed"

# A01 Broken Access Control
echo "Installing feroxbuster (recursive content discovery)..."
apt-get install -y --no-install-recommends feroxbuster || echo "WARN: feroxbuster install failed"

# A02 Cryptographic Failures
echo "Installing sslscan (TLS/SSL scanner)..."
apt-get install -y --no-install-recommends sslscan || echo "WARN: sslscan install failed"

# A07 Authentication Failures
echo "Installing hydra (password brute-forcing)..."
apt-get install -y --no-install-recommends hydra || echo "WARN: hydra install failed"

echo "Installing john (password cracking)..."
apt-get install -y --no-install-recommends john || echo "WARN: john install failed"

# Reconnaissance & Enumeration
echo "Installing dnsrecon (DNS enumeration)..."
apt-get install -y --no-install-recommends dnsrecon || echo "WARN: dnsrecon install failed"

echo "Installing enum4linux-ng (SMB enumeration)..."
apt-get install -y --no-install-recommends enum4linux-ng || echo "WARN: enum4linux-ng install failed"

# Supporting Tools
echo "Installing jq (JSON processing)..."
apt-get install -y --no-install-recommends jq || echo "WARN: jq install failed"

echo "Installing wafw00f (WAF detection)..."
apt-get install -y --no-install-recommends wafw00f || echo "WARN: wafw00f install failed"

# Wordlists (critical for fuzzing/brute-force tools)
echo "Installing seclists (wordlists)..."
apt-get install -y --no-install-recommends seclists || echo "WARN: seclists install failed"

echo "--- APT packages complete ---"

# ============================================================================
# SECTION 2: Pip Packages
# ============================================================================

echo "--- Installing pip-based security tools ---"

# A02 Cryptographic Failures
echo "Installing sslyze (TLS/SSL analysis)..."
pip install --no-cache-dir --break-system-packages --force-reinstall --no-deps sslyze || echo "WARN: sslyze install failed"
# Install sslyze deps that don't conflict with system cryptography
pip install --no-cache-dir --break-system-packages nassl tls-parser pydantic 2>/dev/null || true

# Hidden parameter discovery
echo "Installing arjun (HTTP parameter discovery)..."
pip install --no-cache-dir --break-system-packages arjun || echo "WARN: arjun install failed"

# A07 Authentication - JWT testing
echo "Installing jwt-tool..."
pip install --no-cache-dir --break-system-packages jwt-tool || echo "WARN: jwt-tool install failed"

# SAST tools (reinstall if missing from install_additional.sh)
echo "Installing semgrep (static analysis)..."
pip install --no-cache-dir --break-system-packages semgrep 2>/dev/null || echo "WARN: semgrep install failed"

echo "Installing bandit (Python security linter)..."
pip install --no-cache-dir --break-system-packages bandit 2>/dev/null || echo "WARN: bandit install failed"

echo "--- Pip packages complete ---"

# ============================================================================
# SECTION 3: Go Tools (compile from source)
# ============================================================================

echo "--- Installing Go-based security tools ---"

if command -v go &>/dev/null; then
    # A05 Security Misconfiguration + A10 SSRF
    echo "Installing nuclei (template-based vuln scanner)..."
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest || echo "WARN: nuclei install failed"

    # HTTP toolkit
    echo "Installing httpx (HTTP probing)..."
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest || echo "WARN: httpx install failed"

    # Subdomain discovery
    echo "Installing subfinder (subdomain discovery)..."
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest || echo "WARN: subfinder install failed"

    # A01 Broken Access Control
    echo "Installing gobuster (directory/DNS brute-forcing)..."
    go install -v github.com/OJ/gobuster/v3@latest || echo "WARN: gobuster install failed"

    echo "Installing ffuf (fast web fuzzer)..."
    go install -v github.com/ffuf/ffuf/v2@latest || echo "WARN: ffuf install failed"

    # A03 Injection - XSS
    echo "Installing dalfox (XSS scanner)..."
    go install -v github.com/hahwul/dalfox/v2@latest || echo "WARN: dalfox install failed"

    # Ensure Go binaries are in PATH
    if [ -d /root/go/bin ]; then
        for binary in /root/go/bin/*; do
            if [ -f "$binary" ] && [ ! -L "/usr/local/bin/$(basename $binary)" ]; then
                ln -sf "$binary" "/usr/local/bin/$(basename $binary)" 2>/dev/null || true
            fi
        done
    fi
else
    echo "WARN: Go not installed, skipping Go-based tools (nuclei, httpx, subfinder, gobuster, ffuf, dalfox)"
fi

echo "--- Go tools complete ---"

# ============================================================================
# SECTION 4: testssl.sh (git clone)
# ============================================================================

echo "--- Installing testssl.sh ---"

if [ ! -f /opt/testssl/testssl.sh ]; then
    git clone --depth 1 https://github.com/drwetter/testssl.sh.git /opt/testssl 2>/dev/null || echo "WARN: testssl.sh clone failed"
    if [ -f /opt/testssl/testssl.sh ]; then
        chmod +x /opt/testssl/testssl.sh
        ln -sf /opt/testssl/testssl.sh /usr/local/bin/testssl.sh
        echo "testssl.sh installed"
    fi
else
    echo "testssl.sh already installed"
fi

echo "--- testssl.sh complete ---"

# ============================================================================
# SECTION 5: Nuclei Templates Update
# ============================================================================

echo "--- Updating nuclei templates ---"

if command -v nuclei &>/dev/null; then
    nuclei -update-templates 2>/dev/null || echo "WARN: nuclei template update failed (will update on first run)"
fi

echo "--- Nuclei templates complete ---"

# ============================================================================
# SECTION 6: Verification
# ============================================================================

echo ""
echo "==================== OWASP TOOL VERIFICATION ===================="
echo ""

verify_tool() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null 2>&1; then
        echo "[OK] $name"
    else
        echo "[MISSING] $name"
    fi
}

echo "--- A01 Broken Access Control ---"
verify_tool "dirb" "which dirb"
verify_tool "gobuster" "which gobuster"
verify_tool "feroxbuster" "which feroxbuster"
verify_tool "ffuf" "which ffuf"

echo "--- A02 Cryptographic Failures ---"
verify_tool "sslyze" "python3 -c 'import sslyze'"
verify_tool "sslscan" "which sslscan"
verify_tool "testssl.sh" "which testssl.sh"

echo "--- A03 Injection ---"
verify_tool "sqlmap" "which sqlmap"
verify_tool "commix" "which commix"
verify_tool "wfuzz" "which wfuzz"
verify_tool "dalfox" "which dalfox"

echo "--- A05 Security Misconfiguration ---"
verify_tool "nikto" "which nikto"
verify_tool "nuclei" "which nuclei"
verify_tool "whatweb" "which whatweb"

echo "--- A07 Authentication Failures ---"
verify_tool "hydra" "which hydra"
verify_tool "john" "which john"

echo "--- Reconnaissance ---"
verify_tool "nmap" "which nmap"
verify_tool "masscan" "which masscan"
verify_tool "httpx" "which httpx"
verify_tool "subfinder" "which subfinder"
verify_tool "dnsrecon" "which dnsrecon"
verify_tool "wafw00f" "which wafw00f"
verify_tool "arjun" "which arjun"

echo "--- SAST ---"
verify_tool "semgrep" "which semgrep"
verify_tool "bandit" "which bandit"

echo "--- Supporting ---"
verify_tool "jq" "which jq"
verify_tool "seclists" "test -d /usr/share/seclists"

echo ""
echo "====================OWASP TOP 10 TOOLS INSTALLATION COMPLETE===================="
