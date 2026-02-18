"""
Assessment State Manager for Security Assessments

Provides shared state infrastructure for Claude Code and Agent Zero
to collaborate on security assessments with thread-safe file operations.
"""

import json
import os
import uuid
import fcntl
from datetime import datetime
from typing import Literal, TypedDict, Optional, List
from contextlib import contextmanager

from python.helpers import files
from python.helpers.print_style import PrintStyle


# Type definitions for assessment state
class TargetData(TypedDict, total=False):
    id: str
    type: Literal["web", "host", "service", "network"]
    address: str
    status: Literal["discovered", "scanning", "tested", "complete"]
    ports: List[int]
    services: dict  # port -> service name mapping
    technologies: List[str]
    notes: str


class FindingData(TypedDict, total=False):
    id: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    title: str
    description: str
    evidence: List[str]  # paths to evidence files
    cwe: str
    cvss: float
    affected: List[str]  # affected targets/URLs
    remediation: str
    status: Literal["confirmed", "potential", "false_positive"]
    found_by: Literal["claude_code", "agent_zero", "manual"]
    timestamp: str


class ProgressData(TypedDict, total=False):
    phase: Literal["recon", "scanning", "exploitation", "reporting", "complete"]
    current_task: str
    completed_tasks: List[str]
    pending_tasks: List[str]


class MetaData(TypedDict, total=False):
    id: str
    name: str
    scope: List[str]  # in-scope targets/networks
    out_of_scope: List[str]  # explicitly excluded
    type: Literal["web", "network", "internal", "external", "full"]
    started: str
    status: Literal["in_progress", "paused", "completed"]
    methodology: str


class ContextData(TypedDict, total=False):
    notes: str
    decisions: List[str]
    credentials: List[str]  # references only, not actual creds


class AssessmentStateData(TypedDict, total=False):
    meta: MetaData
    targets: List[TargetData]
    findings: List[FindingData]
    progress: ProgressData
    context: ContextData


# Constants
ASSESSMENT_DIR = "assessment"
ASSESSMENT_STATE_FILE = "assessment_state.json"
EVIDENCE_DIR = "evidence"


class AssessmentState:
    """
    Manages security assessment state stored in project directory.
    Provides thread-safe read/write operations with file locking.
    """

    def __init__(self, project_name: str):
        """
        Initialize assessment state for a project.

        Args:
            project_name: Name of the Agent Zero project
        """
        self.project_name = project_name
        self._printer = PrintStyle(italic=True, font_color="cyan", padding=False)

    def _get_assessment_dir(self) -> str:
        """Get the assessment directory path for this project."""
        from python.helpers.projects import get_project_meta_folder
        return get_project_meta_folder(self.project_name, ASSESSMENT_DIR)

    def _get_state_file_path(self) -> str:
        """Get the path to the assessment state JSON file."""
        return os.path.join(self._get_assessment_dir(), ASSESSMENT_STATE_FILE)

    def _get_evidence_dir(self) -> str:
        """Get the evidence directory path for this project."""
        return os.path.join(self._get_assessment_dir(), EVIDENCE_DIR)

    @contextmanager
    def _file_lock(self, filepath: str, mode: str = 'r+'):
        """
        Context manager for file locking to ensure thread-safe operations.

        Args:
            filepath: Path to the file to lock
            mode: File open mode
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Create file if it doesn't exist
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                json.dump(self._get_default_state(), f, indent=2)

        f = open(filepath, mode)
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            yield f
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            f.close()

    def _get_default_state(self) -> AssessmentStateData:
        """Get default empty assessment state."""
        return AssessmentStateData(
            meta=MetaData(
                id=str(uuid.uuid4()),
                name="",
                scope=[],
                out_of_scope=[],
                type="web",
                started=datetime.utcnow().isoformat() + "Z",
                status="in_progress",
                methodology="OWASP WSTG"
            ),
            targets=[],
            findings=[],
            progress=ProgressData(
                phase="recon",
                current_task="",
                completed_tasks=[],
                pending_tasks=[]
            ),
            context=ContextData(
                notes="",
                decisions=[],
                credentials=[]
            )
        )

    def ensure_directories(self) -> None:
        """Ensure assessment and evidence directories exist."""
        assessment_dir = self._get_assessment_dir()
        evidence_dir = self._get_evidence_dir()

        files.create_dir(assessment_dir)
        files.create_dir(evidence_dir)

        self._printer.print(f"[Assessment] Directories ensured: {assessment_dir}")

    def load(self) -> AssessmentStateData:
        """
        Load assessment state from file.

        Returns:
            Current assessment state data
        """
        state_file = self._get_state_file_path()

        if not os.path.exists(state_file):
            self._printer.print("[Assessment] No state file found, returning default")
            return self._get_default_state()

        try:
            with self._file_lock(state_file, 'r') as f:
                data = json.load(f)
                self._printer.print(f"[Assessment] Loaded state: {len(data.get('findings', []))} findings")
                return data
        except json.JSONDecodeError as e:
            self._printer.print(f"[Assessment] Error parsing state file: {e}")
            return self._get_default_state()

    def save(self, state: AssessmentStateData) -> bool:
        """
        Save assessment state to file.

        Args:
            state: Assessment state data to save

        Returns:
            True if save successful, False otherwise
        """
        self.ensure_directories()
        state_file = self._get_state_file_path()

        try:
            with self._file_lock(state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            self._printer.print(f"[Assessment] Saved state: {len(state.get('findings', []))} findings")
            return True
        except Exception as e:
            self._printer.print(f"[Assessment] Error saving state: {e}")
            return False

    def initialize(self, name: str, scope: List[str],
                   assessment_type: str = "web",
                   methodology: str = "OWASP WSTG") -> AssessmentStateData:
        """
        Initialize a new assessment.

        Args:
            name: Assessment name
            scope: List of in-scope targets/networks
            assessment_type: Type of assessment (web, network, internal, external, full)
            methodology: Assessment methodology to follow

        Returns:
            Initialized assessment state
        """
        state = self._get_default_state()
        state["meta"]["name"] = name
        state["meta"]["scope"] = scope
        state["meta"]["type"] = assessment_type
        state["meta"]["methodology"] = methodology
        state["meta"]["started"] = datetime.utcnow().isoformat() + "Z"

        self.save(state)
        self._printer.print(f"[Assessment] Initialized: {name} ({assessment_type})")
        return state

    def add_target(self, target: TargetData) -> Optional[str]:
        """
        Add a target to the assessment.

        Args:
            target: Target data to add

        Returns:
            Target ID if successful, None otherwise
        """
        state = self.load()

        # Generate ID if not provided
        if "id" not in target or not target["id"]:
            target["id"] = str(uuid.uuid4())

        # Set default status
        if "status" not in target:
            target["status"] = "discovered"

        # Check for duplicates by address
        existing = next((t for t in state["targets"] if t.get("address") == target.get("address")), None)
        if existing:
            # Update existing target
            existing.update(target)
            self._printer.print(f"[Assessment] Updated target: {target.get('address')}")
        else:
            state["targets"].append(target)
            self._printer.print(f"[Assessment] Added target: {target.get('address')}")

        self.save(state)
        return target["id"]

    def add_finding(self, finding: FindingData) -> Optional[str]:
        """
        Add a security finding to the assessment.

        Args:
            finding: Finding data to add

        Returns:
            Finding ID if successful, None otherwise
        """
        state = self.load()

        # Generate ID if not provided
        if "id" not in finding or not finding["id"]:
            finding["id"] = str(uuid.uuid4())

        # Set timestamp if not provided
        if "timestamp" not in finding:
            finding["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Set default status
        if "status" not in finding:
            finding["status"] = "potential"

        state["findings"].append(finding)
        self.save(state)

        self._printer.print(f"[Assessment] Added finding: {finding.get('title')} ({finding.get('severity')})")
        return finding["id"]

    def update_finding(self, finding_id: str, updates: dict) -> bool:
        """
        Update an existing finding.

        Args:
            finding_id: ID of the finding to update
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        state = self.load()

        finding = next((f for f in state["findings"] if f.get("id") == finding_id), None)
        if not finding:
            self._printer.print(f"[Assessment] Finding not found: {finding_id}")
            return False

        finding.update(updates)
        self.save(state)

        self._printer.print(f"[Assessment] Updated finding: {finding_id}")
        return True

    def update_progress(self, phase: Optional[str] = None,
                        current_task: Optional[str] = None,
                        completed_task: Optional[str] = None,
                        pending_task: Optional[str] = None) -> bool:
        """
        Update assessment progress.

        Args:
            phase: New phase (recon, scanning, exploitation, reporting, complete)
            current_task: Current task description
            completed_task: Task to mark as completed
            pending_task: Task to add to pending list

        Returns:
            True if successful, False otherwise
        """
        state = self.load()

        if phase:
            state["progress"]["phase"] = phase

        if current_task is not None:
            state["progress"]["current_task"] = current_task

        if completed_task:
            if completed_task not in state["progress"]["completed_tasks"]:
                state["progress"]["completed_tasks"].append(completed_task)
            # Remove from pending if present
            if completed_task in state["progress"]["pending_tasks"]:
                state["progress"]["pending_tasks"].remove(completed_task)

        if pending_task:
            if pending_task not in state["progress"]["pending_tasks"]:
                state["progress"]["pending_tasks"].append(pending_task)

        self.save(state)
        self._printer.print(f"[Assessment] Progress updated: {state['progress']['phase']}")
        return True

    def add_note(self, note: str) -> bool:
        """
        Add a note to the assessment context.

        Args:
            note: Note to add

        Returns:
            True if successful, False otherwise
        """
        state = self.load()

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        formatted_note = f"[{timestamp}] {note}"

        if state["context"]["notes"]:
            state["context"]["notes"] += f"\n{formatted_note}"
        else:
            state["context"]["notes"] = formatted_note

        self.save(state)
        return True

    def add_decision(self, decision: str) -> bool:
        """
        Record a decision made during the assessment.

        Args:
            decision: Decision to record

        Returns:
            True if successful, False otherwise
        """
        state = self.load()

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        formatted_decision = f"[{timestamp}] {decision}"

        state["context"]["decisions"].append(formatted_decision)
        self.save(state)

        self._printer.print(f"[Assessment] Decision recorded")
        return True

    def is_in_scope(self, target: str) -> bool:
        """
        Check if a target is in scope for the assessment.

        Args:
            target: Target address/URL to check

        Returns:
            True if in scope, False otherwise
        """
        state = self.load()
        scope = state.get("meta", {}).get("scope", [])
        out_of_scope = state.get("meta", {}).get("out_of_scope", [])

        # Check explicit out of scope first
        for excluded in out_of_scope:
            if excluded in target or target in excluded:
                return False

        # Check if in scope
        for allowed in scope:
            # Simple substring matching - could be enhanced with CIDR/glob support
            if allowed in target or target in allowed:
                return True
            # Wildcard support
            if allowed.startswith("*."):
                domain = allowed[2:]
                if target.endswith(domain):
                    return True

        return False

    def save_evidence(self, filename: str, content: str) -> Optional[str]:
        """
        Save evidence to the evidence directory.

        Args:
            filename: Name for the evidence file
            content: Content to save

        Returns:
            Path to saved file if successful, None otherwise
        """
        self.ensure_directories()
        evidence_dir = self._get_evidence_dir()

        # Add timestamp to filename to prevent overwrites
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"

        filepath = os.path.join(evidence_dir, unique_filename)

        try:
            with open(filepath, 'w') as f:
                f.write(content)
            self._printer.print(f"[Assessment] Saved evidence: {unique_filename}")
            return filepath
        except Exception as e:
            self._printer.print(f"[Assessment] Error saving evidence: {e}")
            return None

    def get_summary(self) -> dict:
        """
        Get a summary of the assessment state.

        Returns:
            Summary dictionary with counts and status
        """
        state = self.load()

        findings = state.get("findings", [])
        findings_by_severity = {}
        for finding in findings:
            severity = finding.get("severity", "info")
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1

        return {
            "name": state.get("meta", {}).get("name", "Unknown"),
            "status": state.get("meta", {}).get("status", "unknown"),
            "phase": state.get("progress", {}).get("phase", "unknown"),
            "targets_count": len(state.get("targets", [])),
            "findings_count": len(findings),
            "findings_by_severity": findings_by_severity,
            "scope": state.get("meta", {}).get("scope", []),
        }


def get_assessment_state(project_name: str) -> AssessmentState:
    """
    Get an AssessmentState instance for a project.

    Args:
        project_name: Name of the Agent Zero project

    Returns:
        AssessmentState instance
    """
    return AssessmentState(project_name)
