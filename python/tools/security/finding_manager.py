"""
Finding Manager - Utilities for managing security findings.

Provides CVSS scoring, CWE mapping, and evidence management.
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from python.helpers.print_style import PrintStyle


@dataclass
class Finding:
    """A security finding with all metadata."""

    id: str
    title: str
    severity: str
    description: str
    affected: List[str]
    evidence: List[str]
    cwe: str
    cvss_score: float
    cvss_vector: str
    remediation: str
    status: str
    found_by: str
    timestamp: str
    references: List[str]


class FindingManager:
    """
    Manages security findings with classification and scoring.

    Provides:
    - CVSS score calculation
    - CWE classification
    - Finding deduplication
    - Evidence linking
    - Report generation
    """

    _printer = PrintStyle(italic=True, font_color="cyan", padding=False)

    # CVSS 3.1 Base Metrics
    CVSS_AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}  # Attack Vector
    CVSS_AC = {"L": 0.77, "H": 0.44}  # Attack Complexity
    CVSS_PR = {"N": 0.85, "L": 0.62, "H": 0.27}  # Privileges Required (unchanged scope)
    CVSS_PR_CHANGED = {
        "N": 0.85,
        "L": 0.68,
        "H": 0.5,
    }  # Privileges Required (changed scope)
    CVSS_UI = {"N": 0.85, "R": 0.62}  # User Interaction
    CVSS_S = {"U": False, "C": True}  # Scope
    CVSS_C = {"H": 0.56, "L": 0.22, "N": 0}  # Confidentiality
    CVSS_I = {"H": 0.56, "L": 0.22, "N": 0}  # Integrity
    CVSS_A = {"H": 0.56, "L": 0.22, "N": 0}  # Availability

    # Common CWE categories and their typical severities
    CWE_SEVERITY_MAP = {
        # Critical
        "CWE-78": "critical",  # OS Command Injection
        "CWE-89": "critical",  # SQL Injection
        "CWE-94": "critical",  # Code Injection
        "CWE-502": "critical",  # Deserialization
        "CWE-798": "critical",  # Hardcoded Credentials
        # High
        "CWE-79": "high",  # XSS
        "CWE-22": "high",  # Path Traversal
        "CWE-77": "high",  # Command Injection
        "CWE-287": "high",  # Auth Bypass
        "CWE-306": "high",  # Missing Auth
        "CWE-434": "high",  # Unrestricted Upload
        "CWE-611": "high",  # XXE
        "CWE-918": "high",  # SSRF
        # Medium
        "CWE-200": "medium",  # Info Exposure
        "CWE-209": "medium",  # Error Message Info
        "CWE-269": "medium",  # Improper Privilege
        "CWE-295": "medium",  # Cert Validation
        "CWE-327": "medium",  # Weak Crypto
        "CWE-352": "medium",  # CSRF
        "CWE-601": "medium",  # Open Redirect
        # Low
        "CWE-330": "low",  # Weak Random
        "CWE-532": "low",  # Log Injection
        "CWE-614": "low",  # Cookie Security
        "CWE-693": "low",  # Protection Mechanism
    }

    # CWE to OWASP Top 10 2021 mapping
    CWE_OWASP_MAP = {
        # A01 Broken Access Control
        "CWE-22": "A01",
        "CWE-23": "A01",
        "CWE-35": "A01",
        "CWE-200": "A01",
        "CWE-284": "A01",
        "CWE-285": "A01",
        "CWE-352": "A01",
        "CWE-359": "A01",
        "CWE-425": "A01",
        "CWE-601": "A01",
        "CWE-639": "A01",
        # A02 Cryptographic Failures
        "CWE-259": "A02",
        "CWE-261": "A02",
        "CWE-296": "A02",
        "CWE-310": "A02",
        "CWE-319": "A02",
        "CWE-321": "A02",
        "CWE-322": "A02",
        "CWE-323": "A02",
        "CWE-324": "A02",
        "CWE-325": "A02",
        "CWE-326": "A02",
        "CWE-327": "A02",
        "CWE-328": "A02",
        "CWE-329": "A02",
        "CWE-330": "A02",
        "CWE-331": "A02",
        "CWE-335": "A02",
        "CWE-336": "A02",
        # A03 Injection
        "CWE-20": "A03",
        "CWE-74": "A03",
        "CWE-75": "A03",
        "CWE-77": "A03",
        "CWE-78": "A03",
        "CWE-79": "A03",
        "CWE-80": "A03",
        "CWE-83": "A03",
        "CWE-87": "A03",
        "CWE-88": "A03",
        "CWE-89": "A03",
        "CWE-90": "A03",
        "CWE-91": "A03",
        "CWE-93": "A03",
        "CWE-94": "A03",
        "CWE-95": "A03",
        "CWE-96": "A03",
        "CWE-97": "A03",
        # A04 Insecure Design
        "CWE-73": "A04",
        "CWE-183": "A04",
        "CWE-209": "A04",
        "CWE-213": "A04",
        "CWE-235": "A04",
        "CWE-256": "A04",
        "CWE-257": "A04",
        "CWE-266": "A04",
        "CWE-269": "A04",
        "CWE-280": "A04",
        "CWE-311": "A04",
        "CWE-312": "A04",
        # A05 Security Misconfiguration
        "CWE-2": "A05",
        "CWE-11": "A05",
        "CWE-13": "A05",
        "CWE-15": "A05",
        "CWE-16": "A05",
        "CWE-260": "A05",
        "CWE-315": "A05",
        "CWE-520": "A05",
        "CWE-526": "A05",
        "CWE-537": "A05",
        "CWE-541": "A05",
        "CWE-547": "A05",
        # A06 Vulnerable Components
        "CWE-937": "A06",
        "CWE-1035": "A06",
        "CWE-1104": "A06",
        # A07 Auth Failures (CWE-259 also in A02; first occurrence wins)
        "CWE-255": "A07",
        "CWE-287": "A07",
        "CWE-288": "A07",
        "CWE-290": "A07",
        "CWE-294": "A07",
        "CWE-295": "A07",
        "CWE-297": "A07",
        "CWE-300": "A07",
        "CWE-302": "A07",
        "CWE-304": "A07",
        "CWE-306": "A07",
        # A08 Software and Data Integrity Failures
        "CWE-345": "A08",
        "CWE-353": "A08",
        "CWE-426": "A08",
        "CWE-427": "A08",
        "CWE-428": "A08",
        "CWE-494": "A08",
        "CWE-502": "A08",
        "CWE-565": "A08",
        "CWE-784": "A08",
        "CWE-829": "A08",
        "CWE-830": "A08",
        "CWE-913": "A08",
        # A09 Logging and Monitoring Failures
        "CWE-117": "A09",
        "CWE-223": "A09",
        "CWE-532": "A09",
        "CWE-778": "A09",
        # A10 SSRF
        "CWE-918": "A10",
    }

    @classmethod
    def calculate_cvss(
        cls,
        attack_vector: str = "N",
        attack_complexity: str = "L",
        privileges_required: str = "N",
        user_interaction: str = "N",
        scope: str = "U",
        confidentiality: str = "N",
        integrity: str = "N",
        availability: str = "N",
    ) -> Tuple[float, str, str]:
        """
        Calculate CVSS 3.1 base score.

        Args:
            attack_vector: N (Network), A (Adjacent), L (Local), P (Physical)
            attack_complexity: L (Low), H (High)
            privileges_required: N (None), L (Low), H (High)
            user_interaction: N (None), R (Required)
            scope: U (Unchanged), C (Changed)
            confidentiality: N (None), L (Low), H (High)
            integrity: N (None), L (Low), H (High)
            availability: N (None), L (Low), H (High)

        Returns:
            Tuple of (score, severity, vector_string)
        """
        # Get metric values
        av = cls.CVSS_AV.get(attack_vector, 0.85)
        ac = cls.CVSS_AC.get(attack_complexity, 0.77)
        scope_changed = cls.CVSS_S.get(scope, False)

        if scope_changed:
            pr = cls.CVSS_PR_CHANGED.get(privileges_required, 0.85)
        else:
            pr = cls.CVSS_PR.get(privileges_required, 0.85)

        ui = cls.CVSS_UI.get(user_interaction, 0.85)
        c = cls.CVSS_C.get(confidentiality, 0.0)
        i = cls.CVSS_I.get(integrity, 0.0)
        a = cls.CVSS_A.get(availability, 0.0)

        # Calculate exploitability
        exploitability = 8.22 * av * ac * pr * ui

        # Calculate impact
        isc_base = 1 - ((1 - c) * (1 - i) * (1 - a))

        if scope_changed:
            impact = 7.52 * (isc_base - 0.029) - 3.25 * pow(isc_base - 0.02, 15)
        else:
            impact = 6.42 * isc_base

        # Calculate score
        if impact <= 0:
            score = 0.0
        elif scope_changed:
            score = min(1.08 * (impact + exploitability), 10)
        else:
            score = min(impact + exploitability, 10)

        score = round(score, 1)

        # Determine severity
        if score >= 9.0:
            severity = "critical"
        elif score >= 7.0:
            severity = "high"
        elif score >= 4.0:
            severity = "medium"
        elif score > 0:
            severity = "low"
        else:
            severity = "info"

        # Build vector string
        vector = f"CVSS:3.1/AV:{attack_vector}/AC:{attack_complexity}/PR:{privileges_required}/UI:{user_interaction}/S:{scope}/C:{confidentiality}/I:{integrity}/A:{availability}"

        return score, severity, vector

    @classmethod
    def get_severity_from_cwe(cls, cwe: str) -> str:
        """
        Get typical severity for a CWE.

        Args:
            cwe: CWE identifier (e.g., "CWE-89")

        Returns:
            Severity string
        """
        # Normalize CWE format
        if not cwe.startswith("CWE-"):
            cwe = f"CWE-{cwe}"

        return cls.CWE_SEVERITY_MAP.get(cwe, "medium")

    @classmethod
    def get_owasp_category(cls, cwe: str) -> Optional[str]:
        """
        Get OWASP Top 10 2021 category for a CWE.

        Args:
            cwe: CWE identifier

        Returns:
            OWASP category (A01-A10) or None
        """
        if not cwe.startswith("CWE-"):
            cwe = f"CWE-{cwe}"

        return cls.CWE_OWASP_MAP.get(cwe)

    @classmethod
    def deduplicate_findings(
        cls, findings: List[Finding], match_fields: Optional[List[str]] = None
    ) -> List[Finding]:
        """
        Deduplicate findings based on specified fields.

        Args:
            findings: List of findings to deduplicate
            match_fields: Fields to use for matching (default: title, cwe, affected)

        Returns:
            Deduplicated list of findings
        """
        if match_fields is None:
            match_fields = ["title", "cwe"]

        seen = set()
        unique = []

        for finding in findings:
            # Build match key
            key_parts = []
            for field in match_fields:
                value = getattr(finding, field, "")
                if isinstance(value, list):
                    value = ",".join(sorted(value))
                key_parts.append(str(value).lower())

            key = "|".join(key_parts)

            if key not in seen:
                seen.add(key)
                unique.append(finding)

        cls._printer.print(
            f"[FindingManager] Deduplicated {len(findings)} -> {len(unique)} findings"
        )
        return unique

    @classmethod
    def prioritize_findings(cls, findings: List[Finding]) -> List[Finding]:
        """
        Sort findings by severity and CVSS score.

        Args:
            findings: List of findings to prioritize

        Returns:
            Sorted list of findings
        """
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

        return sorted(
            findings, key=lambda f: (severity_order.get(f.severity, 5), -f.cvss_score)
        )

    @classmethod
    def generate_summary(cls, findings: List[Finding]) -> Dict[str, Any]:
        """
        Generate a summary of findings.

        Args:
            findings: List of findings

        Returns:
            Summary dictionary
        """
        severity_counts: Dict[str, int] = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
        cwe_counts: Dict[str, int] = {}
        owasp_counts: Dict[str, int] = {}

        for finding in findings:
            # Count severities
            sev = finding.severity
            if sev in severity_counts:
                severity_counts[sev] += 1

            # Count CWEs
            if finding.cwe:
                cwe_counts[finding.cwe] = cwe_counts.get(finding.cwe, 0) + 1

                # Count OWASP categories
                owasp = cls.get_owasp_category(finding.cwe)
                if owasp:
                    owasp_counts[owasp] = owasp_counts.get(owasp, 0) + 1

        # Get top CWEs
        top_cwes = sorted(cwe_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total": len(findings),
            "by_severity": severity_counts,
            "top_cwes": dict(top_cwes),
            "owasp_categories": owasp_counts,
            "critical_count": severity_counts["critical"],
            "high_count": severity_counts["high"],
        }

    @classmethod
    def to_json(cls, findings: List[Finding]) -> str:
        """
        Convert findings to JSON.

        Args:
            findings: List of findings

        Returns:
            JSON string
        """
        return json.dumps([asdict(f) for f in findings], indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> List[Finding]:
        """
        Load findings from JSON.

        Args:
            json_str: JSON string

        Returns:
            List of findings
        """
        data = json.loads(json_str)
        return [Finding(**item) for item in data]

    @classmethod
    def generate_markdown_report(
        cls, findings: List[Finding], title: str = "Security Assessment Report"
    ) -> str:
        """
        Generate a markdown report of findings.

        Args:
            findings: List of findings
            title: Report title

        Returns:
            Markdown string
        """
        summary = cls.generate_summary(findings)
        prioritized = cls.prioritize_findings(findings)

        report = f"# {title}\n\n"
        report += f"**Generated:** {datetime.utcnow().isoformat()}Z\n\n"

        # Executive Summary
        report += "## Executive Summary\n\n"
        report += f"- **Total Findings:** {summary['total']}\n"
        report += f"- **Critical:** {summary['critical_count']}\n"
        report += f"- **High:** {summary['high_count']}\n"
        report += f"- **Medium:** {summary['by_severity']['medium']}\n"
        report += f"- **Low:** {summary['by_severity']['low']}\n\n"

        if summary["top_cwes"]:
            report += "### Top Vulnerability Types\n\n"
            for cwe, count in summary["top_cwes"].items():
                report += f"- {cwe}: {count}\n"
            report += "\n"

        # Findings by Severity
        for severity in ["critical", "high", "medium", "low", "info"]:
            sev_findings = [f for f in prioritized if f.severity == severity]
            if not sev_findings:
                continue

            report += (
                f"## {severity.title()} Severity Findings ({len(sev_findings)})\n\n"
            )

            for i, finding in enumerate(sev_findings, 1):
                report += f"### {i}. {finding.title}\n\n"
                report += f"**Severity:** {finding.severity.upper()}"
                if finding.cvss_score > 0:
                    report += f" (CVSS: {finding.cvss_score})"
                report += "\n\n"

                if finding.cwe:
                    owasp = cls.get_owasp_category(finding.cwe)
                    report += f"**CWE:** {finding.cwe}"
                    if owasp:
                        report += f" | **OWASP:** {owasp}"
                    report += "\n\n"

                report += f"**Description:** {finding.description}\n\n"

                if finding.affected:
                    report += "**Affected:**\n"
                    for affected in finding.affected:
                        report += f"- {affected}\n"
                    report += "\n"

                if finding.remediation:
                    report += f"**Remediation:** {finding.remediation}\n\n"

                if finding.references:
                    report += "**References:**\n"
                    for ref in finding.references:
                        report += f"- {ref}\n"
                    report += "\n"

                report += "---\n\n"

        return report
