"""
Code Scanner - Wrapper for static application security testing (SAST) tools.

Supports: semgrep, bandit (Python), eslint-security (JavaScript)
"""

import subprocess
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from python.helpers.tool_installer import ToolInstaller
from python.helpers.print_style import PrintStyle


@dataclass
class CodeFinding:
    """A code security finding."""
    file: str
    line: int
    column: int
    severity: str
    rule_id: str
    message: str
    code_snippet: str
    cwe: str
    fix_recommendation: str


class CodeScanner:
    """
    Wrapper for SAST (Static Application Security Testing) tools.

    Supports:
    - semgrep: Multi-language static analysis
    - bandit: Python security linter
    - eslint: JavaScript linter with security plugins
    """

    _printer = PrintStyle(italic=True, font_color="cyan", padding=False)

    # Severity mapping for normalization
    SEVERITY_MAP = {
        # Semgrep
        "ERROR": "high",
        "WARNING": "medium",
        "INFO": "low",
        # Bandit
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low",
        # ESLint
        "2": "high",
        "1": "medium",
        "0": "info"
    }

    @classmethod
    def semgrep_scan(
        cls,
        path: str,
        config: str = "auto",
        severity: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        timeout: int = 300
    ) -> Tuple[bool, List[CodeFinding], str]:
        """
        Run semgrep static analysis.

        Args:
            path: Path to scan (file or directory)
            config: Semgrep config (auto, p/security-audit, p/owasp-top-ten, etc.)
            severity: Filter by severity
            exclude: Patterns to exclude
            timeout: Command timeout

        Returns:
            Tuple of (success, findings, raw output)
        """
        success, msg = ToolInstaller.ensure_installed("semgrep")
        if not success:
            return False, [], f"Failed to install semgrep: {msg}"

        # Build command
        cmd_parts = ["semgrep", "--json", "--config", config, path]

        if severity:
            for sev in severity:
                cmd_parts.extend(["--severity", sev.upper()])

        if exclude:
            for pattern in exclude:
                cmd_parts.extend(["--exclude", pattern])

        cls._printer.print(f"[CodeScanner] Running semgrep on {path}")

        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            # Parse JSON output
            findings = []
            try:
                data = json.loads(result.stdout)
                for result_item in data.get("results", []):
                    severity = cls.SEVERITY_MAP.get(
                        result_item.get("extra", {}).get("severity", "INFO"),
                        "info"
                    )

                    # Extract CWE if available
                    cwe = ""
                    metadata = result_item.get("extra", {}).get("metadata", {})
                    if "cwe" in metadata:
                        cwe_list = metadata["cwe"]
                        if isinstance(cwe_list, list):
                            cwe = ", ".join(cwe_list)
                        else:
                            cwe = str(cwe_list)

                    findings.append(CodeFinding(
                        file=result_item.get("path", ""),
                        line=result_item.get("start", {}).get("line", 0),
                        column=result_item.get("start", {}).get("col", 0),
                        severity=severity,
                        rule_id=result_item.get("check_id", ""),
                        message=result_item.get("extra", {}).get("message", ""),
                        code_snippet=result_item.get("extra", {}).get("lines", ""),
                        cwe=cwe,
                        fix_recommendation=result_item.get("extra", {}).get("fix", "")
                    ))
            except json.JSONDecodeError:
                pass

            return True, findings, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Scan timed out"
        except Exception as e:
            return False, [], str(e)

    @classmethod
    def bandit_scan(
        cls,
        path: str,
        severity: str = "low",
        confidence: str = "low",
        exclude: Optional[List[str]] = None,
        timeout: int = 300
    ) -> Tuple[bool, List[CodeFinding], str]:
        """
        Run bandit Python security analysis.

        Args:
            path: Path to scan (file or directory)
            severity: Minimum severity (low, medium, high)
            confidence: Minimum confidence (low, medium, high)
            exclude: Directories to exclude
            timeout: Command timeout

        Returns:
            Tuple of (success, findings, raw output)
        """
        success, msg = ToolInstaller.ensure_installed("bandit")
        if not success:
            return False, [], f"Failed to install bandit: {msg}"

        # Build command
        cmd_parts = ["bandit", "-r", "-f", "json",
                     "-ll" if severity == "low" else "-l" if severity == "medium" else "",
                     "-ii" if confidence == "low" else "-i" if confidence == "medium" else "",
                     path]

        # Remove empty strings
        cmd_parts = [c for c in cmd_parts if c]

        if exclude:
            cmd_parts.extend(["--exclude", ",".join(exclude)])

        cls._printer.print(f"[CodeScanner] Running bandit on {path}")

        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            # Parse JSON output
            findings = []
            try:
                data = json.loads(result.stdout)
                for result_item in data.get("results", []):
                    severity = cls.SEVERITY_MAP.get(
                        result_item.get("issue_severity", "LOW"),
                        "low"
                    )

                    # Build CWE from test ID
                    cwe = ""
                    test_id = result_item.get("test_id", "")
                    cwe_mapping = {
                        "B101": "CWE-703",  # assert
                        "B102": "CWE-78",   # exec
                        "B103": "CWE-732",  # chmod
                        "B104": "CWE-78",   # hardcoded bind
                        "B105": "CWE-259",  # hardcoded password
                        "B106": "CWE-259",  # hardcoded password
                        "B107": "CWE-259",  # hardcoded password
                        "B108": "CWE-377",  # hardcoded tmp
                        "B110": "CWE-703",  # try except pass
                        "B112": "CWE-703",  # try except continue
                        "B201": "CWE-94",   # flask debug
                        "B301": "CWE-502",  # pickle
                        "B302": "CWE-502",  # marshal
                        "B303": "CWE-327",  # md5
                        "B304": "CWE-327",  # des
                        "B305": "CWE-327",  # cipher
                        "B306": "CWE-377",  # mktemp
                        "B307": "CWE-78",   # eval
                        "B308": "CWE-611",  # mark safe
                        "B310": "CWE-22",   # urllib urlopen
                        "B311": "CWE-330",  # random
                        "B312": "CWE-295",  # telnetlib
                        "B313": "CWE-611",  # xml parse
                        "B314": "CWE-611",  # xml parse
                        "B315": "CWE-611",  # xml parse
                        "B316": "CWE-611",  # xml parse
                        "B317": "CWE-611",  # xml parse
                        "B318": "CWE-611",  # xml parse
                        "B319": "CWE-611",  # xml parse
                        "B320": "CWE-611",  # xml parse
                        "B321": "CWE-327",  # ftplib
                        "B322": "CWE-78",   # input
                        "B323": "CWE-295",  # ssl
                        "B324": "CWE-327",  # hashlib
                        "B501": "CWE-295",  # ssl verify
                        "B502": "CWE-327",  # ssl version
                        "B503": "CWE-327",  # ssl default
                        "B504": "CWE-295",  # ssl no verify
                        "B505": "CWE-327",  # weak crypto
                        "B506": "CWE-295",  # yaml load
                        "B507": "CWE-295",  # ssh host key
                        "B601": "CWE-78",   # paramiko call
                        "B602": "CWE-78",   # subprocess popen
                        "B603": "CWE-78",   # subprocess without shell
                        "B604": "CWE-78",   # shell true
                        "B605": "CWE-78",   # os system
                        "B606": "CWE-78",   # os popen
                        "B607": "CWE-78",   # start process partial path
                        "B608": "CWE-89",   # sql injection
                        "B609": "CWE-78",   # wildcard injection
                        "B610": "CWE-94",   # django extra
                        "B611": "CWE-94",   # django raw sql
                        "B701": "CWE-79",   # jinja2 autoescape
                        "B702": "CWE-79",   # mako templates
                        "B703": "CWE-79",   # django mark safe
                    }
                    cwe = cwe_mapping.get(test_id, "")

                    findings.append(CodeFinding(
                        file=result_item.get("filename", ""),
                        line=result_item.get("line_number", 0),
                        column=result_item.get("col_offset", 0),
                        severity=severity,
                        rule_id=test_id,
                        message=result_item.get("issue_text", ""),
                        code_snippet=result_item.get("code", ""),
                        cwe=cwe,
                        fix_recommendation=""
                    ))
            except json.JSONDecodeError:
                pass

            return True, findings, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Scan timed out"
        except Exception as e:
            return False, [], str(e)

    @classmethod
    def eslint_scan(
        cls,
        path: str,
        timeout: int = 300
    ) -> Tuple[bool, List[CodeFinding], str]:
        """
        Run ESLint with security plugin on JavaScript/TypeScript.

        Args:
            path: Path to scan (file or directory)
            timeout: Command timeout

        Returns:
            Tuple of (success, findings, raw output)
        """
        success, msg = ToolInstaller.ensure_installed("eslint")
        if not success:
            return False, [], f"Failed to install eslint: {msg}"

        # Build command
        cmd = f"eslint --format json --no-eslintrc --plugin security --rule 'security/detect-object-injection: warn' --rule 'security/detect-non-literal-fs-filename: warn' --rule 'security/detect-non-literal-require: warn' --rule 'security/detect-possible-timing-attacks: warn' --rule 'security/detect-eval-with-expression: error' {path}"

        cls._printer.print(f"[CodeScanner] Running eslint on {path}")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            # Parse JSON output
            findings = []
            try:
                data = json.loads(result.stdout)
                for file_result in data:
                    file_path = file_result.get("filePath", "")
                    for message in file_result.get("messages", []):
                        severity = cls.SEVERITY_MAP.get(
                            str(message.get("severity", 0)),
                            "info"
                        )

                        findings.append(CodeFinding(
                            file=file_path,
                            line=message.get("line", 0),
                            column=message.get("column", 0),
                            severity=severity,
                            rule_id=message.get("ruleId", ""),
                            message=message.get("message", ""),
                            code_snippet="",
                            cwe="",
                            fix_recommendation=message.get("fix", {}).get("text", "") if message.get("fix") else ""
                        ))
            except json.JSONDecodeError:
                pass

            return True, findings, result.stdout

        except subprocess.TimeoutExpired:
            return False, [], "Scan timed out"
        except Exception as e:
            return False, [], str(e)

    @classmethod
    def detect_language(cls, path: str) -> List[str]:
        """
        Detect programming languages in a path.

        Args:
            path: Path to analyze

        Returns:
            List of detected languages
        """
        languages = set()
        extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".go": "go",
            ".java": "java",
            ".rb": "ruby",
            ".php": "php",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
        }

        if os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext in extensions:
                languages.add(extensions[ext])
        else:
            for root, dirs, files in os.walk(path):
                # Skip hidden and common non-source dirs
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'vendor', 'dist', 'build']]

                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in extensions:
                        languages.add(extensions[ext])

        return list(languages)

    @classmethod
    def auto_scan(
        cls,
        path: str,
        timeout: int = 600
    ) -> Tuple[bool, Dict[str, List[CodeFinding]], str]:
        """
        Automatically detect languages and run appropriate scanners.

        Args:
            path: Path to scan
            timeout: Total timeout

        Returns:
            Tuple of (success, findings by scanner, summary)
        """
        languages = cls.detect_language(path)
        cls._printer.print(f"[CodeScanner] Detected languages: {languages}")

        results = {}
        errors = []

        # Calculate per-scanner timeout
        num_scanners = 0
        if "python" in languages:
            num_scanners += 1
        if any(lang in languages for lang in ["javascript", "typescript"]):
            num_scanners += 1
        num_scanners += 1  # semgrep always runs

        per_scanner_timeout = timeout // max(num_scanners, 1)

        # Always run semgrep (multi-language)
        cls._printer.print(f"[CodeScanner] Running semgrep (multi-language)")
        success, findings, _ = cls.semgrep_scan(
            path,
            config="auto",
            timeout=per_scanner_timeout
        )
        if success:
            results["semgrep"] = findings
        else:
            errors.append("semgrep failed")

        # Run language-specific scanners
        if "python" in languages:
            cls._printer.print(f"[CodeScanner] Running bandit (Python)")
            success, findings, _ = cls.bandit_scan(path, timeout=per_scanner_timeout)
            if success:
                results["bandit"] = findings
            else:
                errors.append("bandit failed")

        if any(lang in languages for lang in ["javascript", "typescript"]):
            cls._printer.print(f"[CodeScanner] Running eslint (JavaScript/TypeScript)")
            success, findings, _ = cls.eslint_scan(path, timeout=per_scanner_timeout)
            if success:
                results["eslint"] = findings
            else:
                errors.append("eslint failed")

        # Generate summary
        total_findings = sum(len(f) for f in results.values())
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

        for scanner_findings in results.values():
            for finding in scanner_findings:
                sev = finding.severity
                if sev in severity_counts:
                    severity_counts[sev] += 1

        summary = f"Code scan of {path}:\n"
        summary += f"- Languages detected: {', '.join(languages) if languages else 'unknown'}\n"
        summary += f"- Scanners run: {', '.join(results.keys())}\n"
        summary += f"- Total findings: {total_findings}\n"
        summary += f"- By severity: {severity_counts}\n"

        if errors:
            summary += f"- Errors: {', '.join(errors)}\n"

        return len(errors) == 0, results, summary
