"""
Network Scanner - Wrapper for network scanning tools (nmap, masscan).

Provides structured scanning with assessment state integration.
"""

import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from python.helpers.tool_installer import ToolInstaller, run_tool
from python.helpers.print_style import PrintStyle


@dataclass
class PortResult:
    """Result for a single port scan."""
    port: int
    protocol: str
    state: str
    service: str
    version: str
    banner: str


@dataclass
class HostResult:
    """Result for a single host scan."""
    address: str
    hostname: str
    state: str
    ports: List[PortResult]
    os_matches: List[str]
    mac_address: str


class NetworkScanner:
    """
    Wrapper for network scanning tools.

    Supports:
    - nmap: Full-featured network scanner
    - masscan: Fast port scanner for large networks
    """

    _printer = PrintStyle(italic=True, font_color="cyan", padding=False)

    @classmethod
    def nmap_scan(
        cls,
        target: str,
        ports: str = "1-1000",
        scan_type: str = "tcp",
        timing: int = 4,
        service_detection: bool = True,
        os_detection: bool = False,
        scripts: Optional[List[str]] = None,
        timeout: int = 600
    ) -> Tuple[bool, List[HostResult], str]:
        """
        Run an nmap scan against a target.

        Args:
            target: Target IP, hostname, or CIDR range
            ports: Port specification (e.g., "22,80,443" or "1-1000")
            scan_type: Type of scan (tcp, syn, udp, ack, fin)
            timing: Timing template 0-5 (higher = faster)
            service_detection: Enable service/version detection
            os_detection: Enable OS detection (requires root)
            scripts: NSE scripts to run
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success, list of HostResult, raw output)
        """
        # Ensure nmap is installed
        success, msg = ToolInstaller.ensure_installed("nmap")
        if not success:
            return False, [], f"Failed to install nmap: {msg}"

        # Build nmap command
        cmd_parts = ["nmap", "-oX", "-"]  # XML output to stdout

        # Scan type
        scan_flags = {
            "tcp": "-sT",
            "syn": "-sS",
            "udp": "-sU",
            "ack": "-sA",
            "fin": "-sF",
            "connect": "-sT"
        }
        cmd_parts.append(scan_flags.get(scan_type, "-sT"))

        # Port specification
        if ports:
            cmd_parts.extend(["-p", ports])

        # Timing
        cmd_parts.append(f"-T{min(max(timing, 0), 5)}")

        # Service detection
        if service_detection:
            cmd_parts.append("-sV")

        # OS detection
        if os_detection:
            cmd_parts.append("-O")

        # Scripts
        if scripts:
            cmd_parts.extend(["--script", ",".join(scripts)])

        # Target
        cmd_parts.append(target)

        cls._printer.print(f"[NetworkScanner] Running: {' '.join(cmd_parts)}")

        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            if result.returncode != 0 and not result.stdout:
                return False, [], result.stderr or "Scan failed"

            # Parse XML output
            hosts = cls._parse_nmap_xml(result.stdout)

            return True, hosts, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Scan timed out"
        except Exception as e:
            return False, [], str(e)

    @classmethod
    def _parse_nmap_xml(cls, xml_output: str) -> List[HostResult]:
        """Parse nmap XML output into structured results."""
        hosts = []

        try:
            root = ET.fromstring(xml_output)

            for host_elem in root.findall(".//host"):
                # Get host state
                status = host_elem.find("status")
                state = status.get("state", "unknown") if status is not None else "unknown"

                # Get addresses
                address = ""
                mac_address = ""
                for addr in host_elem.findall("address"):
                    addr_type = addr.get("addrtype", "")
                    if addr_type == "ipv4" or addr_type == "ipv6":
                        address = addr.get("addr", "")
                    elif addr_type == "mac":
                        mac_address = addr.get("addr", "")

                # Get hostname
                hostname = ""
                hostnames = host_elem.find("hostnames")
                if hostnames is not None:
                    hostname_elem = hostnames.find("hostname")
                    if hostname_elem is not None:
                        hostname = hostname_elem.get("name", "")

                # Get ports
                ports = []
                ports_elem = host_elem.find("ports")
                if ports_elem is not None:
                    for port_elem in ports_elem.findall("port"):
                        port_num = int(port_elem.get("portid", 0))
                        protocol = port_elem.get("protocol", "tcp")

                        state_elem = port_elem.find("state")
                        port_state = state_elem.get("state", "unknown") if state_elem is not None else "unknown"

                        service_elem = port_elem.find("service")
                        service = ""
                        version = ""
                        if service_elem is not None:
                            service = service_elem.get("name", "")
                            product = service_elem.get("product", "")
                            ver = service_elem.get("version", "")
                            version = f"{product} {ver}".strip()

                        # Get banner from scripts
                        banner = ""
                        for script in port_elem.findall("script"):
                            if script.get("id") == "banner":
                                banner = script.get("output", "")
                                break

                        ports.append(PortResult(
                            port=port_num,
                            protocol=protocol,
                            state=port_state,
                            service=service,
                            version=version,
                            banner=banner
                        ))

                # Get OS matches
                os_matches = []
                os_elem = host_elem.find("os")
                if os_elem is not None:
                    for osmatch in os_elem.findall("osmatch"):
                        os_matches.append(osmatch.get("name", ""))

                hosts.append(HostResult(
                    address=address,
                    hostname=hostname,
                    state=state,
                    ports=ports,
                    os_matches=os_matches[:3],  # Top 3 matches
                    mac_address=mac_address
                ))

        except ET.ParseError as e:
            cls._printer.print(f"[NetworkScanner] XML parse error: {e}")

        return hosts

    @classmethod
    def masscan_scan(
        cls,
        target: str,
        ports: str = "1-1000",
        rate: int = 1000,
        timeout: int = 300
    ) -> Tuple[bool, List[Dict], str]:
        """
        Run a masscan scan for fast port discovery.

        Args:
            target: Target IP or CIDR range
            ports: Port specification
            rate: Packets per second (careful with high values)
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success, list of results, raw output)
        """
        success, msg = ToolInstaller.ensure_installed("masscan")
        if not success:
            return False, [], f"Failed to install masscan: {msg}"

        cmd = f"masscan {target} -p{ports} --rate={rate} -oJ -"

        cls._printer.print(f"[NetworkScanner] Running: {cmd}")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            # Parse JSON output
            import json
            results = []
            for line in result.stdout.strip().split("\n"):
                line = line.strip().rstrip(",")
                if line.startswith("{"):
                    try:
                        data = json.loads(line)
                        results.append(data)
                    except json.JSONDecodeError:
                        pass

            return True, results, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Scan timed out"
        except Exception as e:
            return False, [], str(e)

    @classmethod
    def ping_sweep(
        cls,
        target: str,
        timeout: int = 120
    ) -> Tuple[bool, List[str], str]:
        """
        Perform a ping sweep to discover live hosts.

        Args:
            target: Target CIDR range
            timeout: Command timeout

        Returns:
            Tuple of (success, list of live IPs, raw output)
        """
        success, msg = ToolInstaller.ensure_installed("nmap")
        if not success:
            return False, [], f"Failed to install nmap: {msg}"

        cmd = f"nmap -sn {target} -oG -"

        cls._printer.print(f"[NetworkScanner] Running ping sweep on {target}")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            # Parse grepable output
            live_hosts = []
            for line in result.stdout.split("\n"):
                if "Up" in line and "Host:" in line:
                    # Extract IP from "Host: x.x.x.x (hostname) Status: Up"
                    parts = line.split()
                    if len(parts) >= 2:
                        live_hosts.append(parts[1])

            return True, live_hosts, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Scan timed out"
        except Exception as e:
            return False, [], str(e)

    @classmethod
    def quick_scan(
        cls,
        target: str,
        timeout: int = 300
    ) -> Tuple[bool, List[HostResult], str]:
        """
        Quick scan for common ports.

        Args:
            target: Target IP or hostname
            timeout: Command timeout

        Returns:
            Tuple of (success, results, raw output)
        """
        common_ports = "21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5432,5900,8080,8443"
        return cls.nmap_scan(
            target=target,
            ports=common_ports,
            scan_type="tcp",
            timing=4,
            service_detection=True,
            timeout=timeout
        )

    @classmethod
    def vuln_scan(
        cls,
        target: str,
        ports: str = "1-1000",
        timeout: int = 900
    ) -> Tuple[bool, List[HostResult], str]:
        """
        Scan with vulnerability detection scripts.

        Args:
            target: Target IP or hostname
            ports: Port specification
            timeout: Command timeout

        Returns:
            Tuple of (success, results, raw output)
        """
        return cls.nmap_scan(
            target=target,
            ports=ports,
            scan_type="tcp",
            timing=4,
            service_detection=True,
            scripts=["vuln", "vulners"],
            timeout=timeout
        )
