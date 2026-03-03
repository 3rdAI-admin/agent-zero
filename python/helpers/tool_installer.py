"""
Tool Installer - On-demand installation of security tools at runtime.

Provides automatic installation of security tools when first needed,
with caching to avoid redundant installation checks.
"""

import subprocess
import shutil
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from python.helpers.print_style import PrintStyle


@dataclass
class ToolConfig:
    """Configuration for a security tool."""

    name: str
    check_cmd: str  # Command to check if installed (e.g., "nmap --version")
    install_cmd: str  # Command to install the tool
    install_type: str  # apt, pip, go, npm, script
    description: str
    required_deps: list[str]  # Other tools that must be installed first


class ToolInstaller:
    """
    Manages on-demand installation of security tools.

    Tools are installed when first needed and cached to avoid
    redundant checks within the same session.
    """

    # Tool configurations
    TOOLS: Dict[str, ToolConfig] = {
        # Network scanning tools
        "nmap": ToolConfig(
            name="nmap",
            check_cmd="nmap --version",
            install_cmd="apt-get install -y nmap",
            install_type="apt",
            description="Network exploration and security auditing",
            required_deps=[],
        ),
        "masscan": ToolConfig(
            name="masscan",
            check_cmd="masscan --version",
            install_cmd="apt-get install -y masscan",
            install_type="apt",
            description="Fast port scanner",
            required_deps=[],
        ),
        "netcat": ToolConfig(
            name="netcat",
            check_cmd="nc -h",
            install_cmd="apt-get install -y netcat-openbsd",
            install_type="apt",
            description="Network utility for TCP/UDP connections",
            required_deps=[],
        ),
        # Web scanning tools
        "nikto": ToolConfig(
            name="nikto",
            check_cmd="nikto -Version",
            install_cmd="apt-get install -y nikto",
            install_type="apt",
            description="Web server scanner",
            required_deps=[],
        ),
        "whatweb": ToolConfig(
            name="whatweb",
            check_cmd="whatweb --version",
            install_cmd="apt-get install -y whatweb",
            install_type="apt",
            description="Web scanner and fingerprinter",
            required_deps=[],
        ),
        "nuclei": ToolConfig(
            name="nuclei",
            check_cmd="nuclei -version",
            install_cmd="go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
            install_type="go",
            description="Fast vulnerability scanner",
            required_deps=["golang"],
        ),
        "httpx": ToolConfig(
            name="httpx",
            check_cmd="httpx -version",
            install_cmd="go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
            install_type="go",
            description="HTTP toolkit",
            required_deps=["golang"],
        ),
        # SAST tools
        "semgrep": ToolConfig(
            name="semgrep",
            check_cmd="semgrep --version",
            install_cmd="pip install semgrep",
            install_type="pip",
            description="Static analysis tool",
            required_deps=[],
        ),
        "bandit": ToolConfig(
            name="bandit",
            check_cmd="bandit --version",
            install_cmd="pip install bandit",
            install_type="pip",
            description="Python security linter",
            required_deps=[],
        ),
        "eslint": ToolConfig(
            name="eslint",
            check_cmd="eslint --version",
            install_cmd="npm install -g eslint eslint-plugin-security",
            install_type="npm",
            description="JavaScript linter with security rules",
            required_deps=["nodejs"],
        ),
        # Reconnaissance tools
        "subfinder": ToolConfig(
            name="subfinder",
            check_cmd="subfinder -version",
            install_cmd="go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
            install_type="go",
            description="Subdomain discovery tool",
            required_deps=["golang"],
        ),
        "amass": ToolConfig(
            name="amass",
            check_cmd="amass -version",
            install_cmd="go install -v github.com/owasp-amass/amass/v4/...@master",
            install_type="go",
            description="In-depth attack surface mapping",
            required_deps=["golang"],
        ),
        "theharvester": ToolConfig(
            name="theharvester",
            check_cmd="theHarvester -h",
            install_cmd="apt-get install -y theharvester",
            install_type="apt",
            description="OSINT gathering tool",
            required_deps=[],
        ),
        # A03 Injection tools
        "sqlmap": ToolConfig(
            name="sqlmap",
            check_cmd="sqlmap --version",
            install_cmd="apt-get install -y sqlmap",
            install_type="apt",
            description="Automatic SQL injection and database takeover",
            required_deps=[],
        ),
        "commix": ToolConfig(
            name="commix",
            check_cmd="commix --version",
            install_cmd="apt-get install -y commix",
            install_type="apt",
            description="Command injection exploiter",
            required_deps=[],
        ),
        "wfuzz": ToolConfig(
            name="wfuzz",
            check_cmd="wfuzz --version",
            install_cmd="apt-get install -y wfuzz",
            install_type="apt",
            description="Web application fuzzer",
            required_deps=[],
        ),
        "dalfox": ToolConfig(
            name="dalfox",
            check_cmd="dalfox version",
            install_cmd="go install -v github.com/hahwul/dalfox/v2@latest",
            install_type="go",
            description="XSS scanning and parameter analysis",
            required_deps=["golang"],
        ),
        # A01 Broken Access Control tools
        "gobuster": ToolConfig(
            name="gobuster",
            check_cmd="gobuster version",
            install_cmd="go install -v github.com/OJ/gobuster/v3@latest",
            install_type="go",
            description="Directory/DNS/VHost brute-forcing",
            required_deps=["golang"],
        ),
        "feroxbuster": ToolConfig(
            name="feroxbuster",
            check_cmd="feroxbuster --version",
            install_cmd="apt-get install -y feroxbuster",
            install_type="apt",
            description="Recursive content discovery",
            required_deps=[],
        ),
        "ffuf": ToolConfig(
            name="ffuf",
            check_cmd="ffuf -V",
            install_cmd="go install -v github.com/ffuf/ffuf/v2@latest",
            install_type="go",
            description="Fast web fuzzer",
            required_deps=["golang"],
        ),
        # A02 Cryptographic Failures tools
        "sslyze": ToolConfig(
            name="sslyze",
            check_cmd="sslyze --version",
            install_cmd="pip install --break-system-packages sslyze",
            install_type="pip",
            description="TLS/SSL configuration analysis",
            required_deps=[],
        ),
        "sslscan": ToolConfig(
            name="sslscan",
            check_cmd="sslscan --version",
            install_cmd="apt-get install -y sslscan",
            install_type="apt",
            description="TLS/SSL cipher and protocol scanner",
            required_deps=[],
        ),
        "testssl": ToolConfig(
            name="testssl",
            check_cmd="testssl.sh --version",
            install_cmd="git clone --depth 1 https://github.com/drwetter/testssl.sh.git /opt/testssl && chmod +x /opt/testssl/testssl.sh && ln -sf /opt/testssl/testssl.sh /usr/local/bin/testssl.sh",
            install_type="script",
            description="TLS/SSL testing tool",
            required_deps=[],
        ),
        # A07 Authentication Failures tools
        "hydra": ToolConfig(
            name="hydra",
            check_cmd="hydra -h",
            install_cmd="apt-get install -y hydra",
            install_type="apt",
            description="Network login brute-forcer",
            required_deps=[],
        ),
        "john": ToolConfig(
            name="john",
            check_cmd="john --help",
            install_cmd="apt-get install -y john",
            install_type="apt",
            description="Password cracker",
            required_deps=[],
        ),
        "jwt-tool": ToolConfig(
            name="jwt-tool",
            check_cmd="python3 -c 'import jwt_tool'",
            install_cmd="pip install --break-system-packages jwt-tool",
            install_type="pip",
            description="JWT token testing and exploitation",
            required_deps=[],
        ),
        # Additional reconnaissance tools
        "dnsrecon": ToolConfig(
            name="dnsrecon",
            check_cmd="dnsrecon -h",
            install_cmd="apt-get install -y dnsrecon",
            install_type="apt",
            description="DNS enumeration and reconnaissance",
            required_deps=[],
        ),
        "wafw00f": ToolConfig(
            name="wafw00f",
            check_cmd="wafw00f --version",
            install_cmd="apt-get install -y wafw00f",
            install_type="apt",
            description="Web Application Firewall detection",
            required_deps=[],
        ),
        "arjun": ToolConfig(
            name="arjun",
            check_cmd="arjun --help",
            install_cmd="pip install --break-system-packages arjun",
            install_type="pip",
            description="Hidden HTTP parameter discovery",
            required_deps=[],
        ),
        # Dependencies
        "golang": ToolConfig(
            name="golang",
            check_cmd="go version",
            install_cmd="apt-get install -y golang-go && export GOPATH=$HOME/go && export PATH=$PATH:$GOPATH/bin",
            install_type="apt",
            description="Go programming language runtime",
            required_deps=[],
        ),
        "nodejs": ToolConfig(
            name="nodejs",
            check_cmd="node --version",
            install_cmd="apt-get install -y nodejs npm",
            install_type="apt",
            description="Node.js runtime",
            required_deps=[],
        ),
    }

    # Cache of installed tools (per session)
    _installed_cache: Dict[str, bool] = {}

    # Printer for logging
    _printer = PrintStyle(italic=True, font_color="yellow", padding=False)

    @classmethod
    def is_installed(cls, tool_name: str) -> bool:
        """
        Check if a tool is installed.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if installed, False otherwise
        """
        # Check cache first
        if tool_name in cls._installed_cache:
            return cls._installed_cache[tool_name]

        # Check if tool exists in our registry
        if tool_name not in cls.TOOLS:
            # Try checking PATH directly
            result = shutil.which(tool_name) is not None
            cls._installed_cache[tool_name] = result
            return result

        tool = cls.TOOLS[tool_name]

        try:
            # Run check command
            proc = subprocess.run(
                tool.check_cmd, shell=True, capture_output=True, timeout=10
            )
            installed = proc.returncode == 0
            cls._installed_cache[tool_name] = installed
            return installed
        except (subprocess.TimeoutExpired, Exception):
            cls._installed_cache[tool_name] = False
            return False

    @classmethod
    def install(cls, tool_name: str, force: bool = False) -> Tuple[bool, str]:
        """
        Install a tool.

        Args:
            tool_name: Name of the tool to install
            force: Force reinstallation even if already installed

        Returns:
            Tuple of (success, message)
        """
        if tool_name not in cls.TOOLS:
            return False, f"Unknown tool: {tool_name}"

        # Check if already installed
        if not force and cls.is_installed(tool_name):
            return True, f"{tool_name} is already installed"

        tool = cls.TOOLS[tool_name]

        # Install dependencies first
        for dep in tool.required_deps:
            if not cls.is_installed(dep):
                cls._printer.print(f"[Installer] Installing dependency: {dep}")
                success, msg = cls.install(dep)
                if not success:
                    return False, f"Failed to install dependency {dep}: {msg}"

        cls._printer.print(f"[Installer] Installing {tool_name}...")

        try:
            # Set up environment for Go tools
            env = os.environ.copy()
            if tool.install_type == "go":
                gopath = os.path.expanduser("~/go")
                env["GOPATH"] = gopath
                env["PATH"] = f"{env.get('PATH', '')}:{gopath}/bin"

            # Update apt cache if needed
            if tool.install_type == "apt":
                subprocess.run(
                    "apt-get update",
                    shell=True,
                    capture_output=True,
                    timeout=120,
                    env=env,
                )

            # Run install command
            result = subprocess.run(
                tool.install_cmd,
                shell=True,
                capture_output=True,
                timeout=300,  # 5 minute timeout for installations
                env=env,
                text=True,
            )

            if result.returncode == 0:
                # Clear cache to force re-check
                cls._installed_cache.pop(tool_name, None)

                # Verify installation
                if cls.is_installed(tool_name):
                    cls._printer.print(
                        f"[Installer] Successfully installed {tool_name}"
                    )
                    return True, f"Successfully installed {tool_name}"
                else:
                    return (
                        False,
                        f"Installation completed but {tool_name} not found in PATH",
                    )
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                cls._printer.print(
                    f"[Installer] Failed to install {tool_name}: {error_msg}"
                )
                return False, f"Installation failed: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Installation timed out"
        except Exception as e:
            return False, f"Installation error: {str(e)}"

    @classmethod
    def ensure_installed(cls, tool_name: str) -> Tuple[bool, str]:
        """
        Ensure a tool is installed, installing it if necessary.

        Args:
            tool_name: Name of the tool to ensure

        Returns:
            Tuple of (success, message)
        """
        if cls.is_installed(tool_name):
            return True, f"{tool_name} is available"

        cls._printer.print(f"[Installer] {tool_name} not found, installing...")
        return cls.install(tool_name)

    @classmethod
    def ensure_multiple(cls, tool_names: list[str]) -> Dict[str, Tuple[bool, str]]:
        """
        Ensure multiple tools are installed.

        Args:
            tool_names: List of tool names to ensure

        Returns:
            Dictionary mapping tool names to (success, message) tuples
        """
        results = {}
        for tool in tool_names:
            results[tool] = cls.ensure_installed(tool)
        return results

    @classmethod
    def get_tool_info(cls, tool_name: str) -> Optional[ToolConfig]:
        """
        Get information about a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            ToolConfig if found, None otherwise
        """
        return cls.TOOLS.get(tool_name)

    @classmethod
    def list_tools(cls) -> Dict[str, dict]:
        """
        List all known tools and their installation status.

        Returns:
            Dictionary of tool info with installation status
        """
        result = {}
        for name, config in cls.TOOLS.items():
            result[name] = {
                "description": config.description,
                "install_type": config.install_type,
                "installed": cls.is_installed(name),
                "required_deps": config.required_deps,
            }
        return result

    @classmethod
    def get_tool_path(cls, tool_name: str) -> Optional[str]:
        """
        Get the full path to a tool's executable.

        Args:
            tool_name: Name of the tool

        Returns:
            Full path if found, None otherwise
        """
        # Check common Go binary path
        if tool_name in cls.TOOLS and cls.TOOLS[tool_name].install_type == "go":
            gopath = os.path.expanduser("~/go/bin")
            go_path = os.path.join(gopath, tool_name)
            if os.path.exists(go_path):
                return go_path

        return shutil.which(tool_name)

    @classmethod
    def clear_cache(cls):
        """Clear the installation cache."""
        cls._installed_cache.clear()
        cls._printer.print("[Installer] Cache cleared")


def ensure_tool(tool_name: str) -> Tuple[bool, str]:
    """
    Convenience function to ensure a tool is installed.

    Args:
        tool_name: Name of the tool

    Returns:
        Tuple of (success, message)
    """
    return ToolInstaller.ensure_installed(tool_name)


def run_tool(tool_name: str, args: str, timeout: int = 300) -> Tuple[bool, str, str]:
    """
    Run a tool, ensuring it's installed first.

    Args:
        tool_name: Name of the tool to run
        args: Arguments to pass to the tool
        timeout: Timeout in seconds

    Returns:
        Tuple of (success, stdout, stderr)
    """
    # Ensure tool is installed
    success, msg = ToolInstaller.ensure_installed(tool_name)
    if not success:
        return False, "", msg

    # Get tool path
    tool_path = ToolInstaller.get_tool_path(tool_name) or tool_name

    try:
        result = subprocess.run(
            f"{tool_path} {args}",
            shell=True,
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)
