"""
Web Scanner - Wrapper for web application scanning tools.

Supports: nikto, nuclei, whatweb, httpx
"""

import subprocess
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from python.helpers.tool_installer import ToolInstaller
from python.helpers.print_style import PrintStyle


@dataclass
class WebFinding:
    """A web vulnerability or information finding."""

    target: str
    finding_type: str
    severity: str
    title: str
    description: str
    evidence: str
    reference: str


@dataclass
class TechFingerprint:
    """Technology fingerprint result."""

    target: str
    technology: str
    version: str
    category: str
    confidence: int


class WebScanner:
    """
    Wrapper for web application scanning tools.

    Supports:
    - nikto: Web server scanner
    - nuclei: Template-based vulnerability scanner
    - whatweb: Web technology fingerprinter
    - httpx: HTTP toolkit for probing
    """

    _printer = PrintStyle(italic=True, font_color="cyan", padding=False)

    @classmethod
    def nikto_scan(
        cls,
        target: str,
        port: int = 80,
        ssl: bool = False,
        tuning: Optional[str] = None,
        timeout: int = 600,
    ) -> Tuple[bool, List[WebFinding], str]:
        """
        Run a nikto scan against a web server.

        Args:
            target: Target URL or IP
            port: Target port
            ssl: Use SSL/TLS
            tuning: Nikto tuning options (e.g., "123" for specific tests)
            timeout: Command timeout

        Returns:
            Tuple of (success, findings, raw output)
        """
        success, msg = ToolInstaller.ensure_installed("nikto")
        if not success:
            return False, [], f"Failed to install nikto: {msg}"

        # Build command
        cmd_parts = ["nikto", "-h", target, "-p", str(port), "-Format", "json"]

        if ssl:
            cmd_parts.append("-ssl")

        if tuning:
            cmd_parts.extend(["-Tuning", tuning])

        cls._printer.print(f"[WebScanner] Running: {' '.join(cmd_parts)}")

        try:
            result = subprocess.run(
                cmd_parts, capture_output=True, timeout=timeout, text=True
            )

            # Parse findings from output
            findings = cls._parse_nikto_output(target, result.stdout)

            return True, findings, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Scan timed out"
        except Exception as e:
            return False, [], str(e)

    @classmethod
    def _parse_nikto_output(cls, target: str, output: str) -> List[WebFinding]:
        """Parse nikto output into structured findings."""
        findings = []

        # Try JSON parsing first
        try:
            data = json.loads(output)
            if isinstance(data, dict) and "vulnerabilities" in data:
                for vuln in data["vulnerabilities"]:
                    findings.append(
                        WebFinding(
                            target=target,
                            finding_type="vulnerability",
                            severity=vuln.get("severity", "info"),
                            title=vuln.get("id", "Unknown"),
                            description=vuln.get("msg", ""),
                            evidence=vuln.get("url", ""),
                            reference=vuln.get("references", ""),
                        )
                    )
                return findings
        except json.JSONDecodeError:
            pass

        # Fall back to text parsing
        for line in output.split("\n"):
            if "+ " in line and ":" in line:
                # Parse nikto finding line
                parts = line.split(":", 1)
                if len(parts) == 2:
                    title = parts[0].replace("+ ", "").strip()
                    description = parts[1].strip()

                    # Determine severity from keywords
                    severity = "info"
                    if any(
                        kw in description.lower()
                        for kw in ["critical", "rce", "injection", "execute"]
                    ):
                        severity = "critical"
                    elif any(
                        kw in description.lower()
                        for kw in ["high", "vulnerability", "exploit"]
                    ):
                        severity = "high"
                    elif any(kw in description.lower() for kw in ["medium", "warning"]):
                        severity = "medium"
                    elif any(
                        kw in description.lower() for kw in ["low", "information"]
                    ):
                        severity = "low"

                    findings.append(
                        WebFinding(
                            target=target,
                            finding_type="vulnerability",
                            severity=severity,
                            title=title,
                            description=description,
                            evidence="",
                            reference="",
                        )
                    )

        return findings

    @classmethod
    def nuclei_scan(
        cls,
        target: str,
        templates: Optional[List[str]] = None,
        severity: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        timeout: int = 600,
    ) -> Tuple[bool, List[WebFinding], str]:
        """
        Run a nuclei scan with vulnerability templates.

        Args:
            target: Target URL
            templates: Specific templates to use
            severity: Filter by severity (critical, high, medium, low, info)
            tags: Filter by tags (cve, oast, tech, etc.)
            timeout: Command timeout

        Returns:
            Tuple of (success, findings, raw output)
        """
        success, msg = ToolInstaller.ensure_installed("nuclei")
        if not success:
            return False, [], f"Failed to install nuclei: {msg}"

        # Build command
        cmd_parts = ["nuclei", "-u", target, "-jsonl", "-silent"]

        if templates:
            cmd_parts.extend(["-t", ",".join(templates)])

        if severity:
            cmd_parts.extend(["-severity", ",".join(severity)])

        if tags:
            cmd_parts.extend(["-tags", ",".join(tags)])

        cls._printer.print(f"[WebScanner] Running nuclei scan on {target}")

        try:
            result = subprocess.run(
                cmd_parts, capture_output=True, timeout=timeout, text=True
            )

            # Parse JSONL output
            findings = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    findings.append(
                        WebFinding(
                            target=data.get("host", target),
                            finding_type=data.get("type", "vulnerability"),
                            severity=data.get("info", {}).get("severity", "info"),
                            title=data.get("info", {}).get("name", "Unknown"),
                            description=data.get("info", {}).get("description", ""),
                            evidence=data.get("matched-at", ""),
                            reference=", ".join(
                                data.get("info", {}).get("reference", [])
                            ),
                        )
                    )
                except json.JSONDecodeError:
                    pass

            return True, findings, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Scan timed out"
        except Exception as e:
            return False, [], str(e)

    @classmethod
    def whatweb_scan(
        cls, target: str, aggression: int = 1, timeout: int = 120
    ) -> Tuple[bool, List[TechFingerprint], str]:
        """
        Fingerprint web technologies using whatweb.

        Args:
            target: Target URL
            aggression: Aggression level 1-4
            timeout: Command timeout

        Returns:
            Tuple of (success, fingerprints, raw output)
        """
        success, msg = ToolInstaller.ensure_installed("whatweb")
        if not success:
            return False, [], f"Failed to install whatweb: {msg}"

        cmd = f"whatweb -a {aggression} --log-json=- {target}"

        cls._printer.print(f"[WebScanner] Running whatweb on {target}")

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, timeout=timeout, text=True
            )

            # Parse JSON output
            fingerprints = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    target_url = data.get("target", target)
                    plugins = data.get("plugins", {})

                    for tech_name, tech_data in plugins.items():
                        version = ""
                        if isinstance(tech_data, dict):
                            version = (
                                tech_data.get("version", [""])[0]
                                if tech_data.get("version")
                                else ""
                            )

                        fingerprints.append(
                            TechFingerprint(
                                target=target_url,
                                technology=tech_name,
                                version=str(version),
                                category="",
                                confidence=100,
                            )
                        )
                except json.JSONDecodeError:
                    pass

            return True, fingerprints, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Scan timed out"
        except Exception as e:
            return False, [], str(e)

    @classmethod
    def httpx_probe(
        cls, targets: List[str], ports: Optional[List[int]] = None, timeout: int = 120
    ) -> Tuple[bool, List[Dict], str]:
        """
        Probe HTTP services using httpx.

        Args:
            targets: List of target URLs/hosts
            ports: Ports to probe (default: 80, 443, 8080, 8443)
            timeout: Command timeout

        Returns:
            Tuple of (success, results, raw output)
        """
        success, msg = ToolInstaller.ensure_installed("httpx")
        if not success:
            return False, [], f"Failed to install httpx: {msg}"

        # Write targets to temp file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("\n".join(targets))
            targets_file = f.name

        cmd_parts = [
            "httpx",
            "-l",
            targets_file,
            "-json",
            "-silent",
            "-status-code",
            "-title",
            "-tech-detect",
            "-web-server",
        ]

        if ports:
            cmd_parts.extend(["-ports", ",".join(str(p) for p in ports)])

        cls._printer.print("[WebScanner] Running httpx probe")

        try:
            result = subprocess.run(
                cmd_parts, capture_output=True, timeout=timeout, text=True
            )

            # Parse JSON output
            results = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    results.append(data)
                except json.JSONDecodeError:
                    pass

            return True, results, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Probe timed out"
        except Exception as e:
            return False, [], str(e)
        finally:
            import os

            try:
                os.unlink(targets_file)
            except OSError:
                pass

    @classmethod
    def quick_web_scan(
        cls, target: str, timeout: int = 300
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Quick web scan combining fingerprinting and vulnerability checks.

        Args:
            target: Target URL
            timeout: Total timeout

        Returns:
            Tuple of (success, combined results, summary)
        """
        results = {"target": target, "technologies": [], "findings": [], "errors": []}

        # Run whatweb for tech fingerprinting
        cls._printer.print("[WebScanner] Phase 1: Technology fingerprinting")
        success, fingerprints, _ = cls.whatweb_scan(target, timeout=timeout // 3)
        if success:
            results["technologies"] = [
                {"name": fp.technology, "version": fp.version} for fp in fingerprints
            ]
        else:
            results["errors"].append("Tech fingerprinting failed")

        # Run nuclei with common templates
        cls._printer.print("[WebScanner] Phase 2: Vulnerability scanning")
        success, findings, _ = cls.nuclei_scan(
            target, severity=["critical", "high", "medium"], timeout=timeout * 2 // 3
        )
        if success:
            results["findings"] = [
                {"severity": f.severity, "title": f.title, "description": f.description}
                for f in findings
            ]
        else:
            results["errors"].append("Nuclei scan failed")

        # Generate summary
        summary = f"Web scan of {target}:\n"
        summary += f"- Technologies: {len(results['technologies'])}\n"
        summary += f"- Findings: {len(results['findings'])}\n"

        if results["findings"]:
            severity_counts = {}
            for f in results["findings"]:
                sev = f["severity"]
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            summary += f"- By severity: {severity_counts}\n"

        return True, results, summary
