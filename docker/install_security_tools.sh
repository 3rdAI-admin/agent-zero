#!/bin/bash
# Install security and penetration testing tools for Agent Zero
# This script can be run inside the container or added to Dockerfile

set -e

echo "====================INSTALLING SECURITY TOOLS===================="

apt-get update

# Network scanning and enumeration tools
apt-get install -y --no-install-recommends \
    nmap \
    masscan \
    netdiscover \
    arp-scan \
    netcat-openbsd \
    socat

# Web application security testing
apt-get install -y --no-install-recommends \
    nikto \
    dirb \
    gobuster \
    wfuzz \
    sqlmap \
    whatweb

# Vulnerability scanners
apt-get install -y --no-install-recommends \
    openvas-scanner \
    lynis \
    chkrootkit

# Password and hash tools
apt-get install -y --no-install-recommends \
    john \
    hashcat \
    hydra \
    medusa

# Wireless tools (if needed)
apt-get install -y --no-install-recommends \
    aircrack-ng \
    reaver \
    bully

# Exploitation frameworks
apt-get install -y --no-install-recommends \
    metasploit-framework \
    exploitdb

# Information gathering
apt-get install -y --no-install-recommends \
    dnsenum \
    dnsrecon \
    dnsutils \
    whois \
    theharvester \
    recon-ng

# SSL/TLS testing
apt-get install -y --no-install-recommends \
    sslscan \
    sslyze \
    testssl.sh

# Network analysis
apt-get install -y --no-install-recommends \
    wireshark \
    tcpdump \
    ettercap-text-only \
    driftnet

# Forensics and analysis
apt-get install -y --no-install-recommends \
    binwalk \
    foremost \
    volatility3 \
    autopsy

# Python security tools
apt-get install -y --no-install-recommends \
    python3-pip

pip3 install --no-cache-dir \
    requests \
    scapy \
    python-nmap \
    impacket \
    paramiko \
    cryptography

# Cleanup
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "====================SECURITY TOOLS INSTALLATION COMPLETE===================="
echo "Available tools:"
echo "  - Network scanning: nmap, masscan, netdiscover"
echo "  - Web testing: nikto, dirb, gobuster, sqlmap"
echo "  - Password attacks: john, hashcat, hydra"
echo "  - Exploitation: metasploit-framework"
echo "  - Information gathering: theharvester, recon-ng"
echo "  - SSL/TLS: sslscan, sslyze, testssl.sh"
echo ""
echo "You can now use these tools via Agent Zero's code execution tool."
