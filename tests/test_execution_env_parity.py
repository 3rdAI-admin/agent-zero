"""Tests for execution-environment package parity.

Verifies that the Docker build artifacts configure the code execution
environment to use the same Python venv as the main Agent Zero runtime.

These are static checks against repo files — they don't require a running
container.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# The canonical Agent Zero venv path, used by setup_venv.sh and supervisord.
EXPECTED_VENV = "/opt/venv-a0"


class TestVenvParity:
    """Ensure shell profiles activate the correct venv."""

    def test_root_bashrc_activates_correct_venv(self):
        bashrc = PROJECT_ROOT / "docker" / "run" / "fs" / "per" / "root" / ".bashrc"
        content = bashrc.read_text()
        assert f"source {EXPECTED_VENV}/bin/activate" in content, (
            f".bashrc should activate {EXPECTED_VENV}, got:\n{content}"
        )

    def test_root_bashrc_does_not_activate_wrong_venv(self):
        bashrc = PROJECT_ROOT / "docker" / "run" / "fs" / "per" / "root" / ".bashrc"
        content = bashrc.read_text()
        # /opt/venv (without -a0) is the wrong venv
        lines = [
            ln
            for ln in content.splitlines()
            if not ln.strip().startswith("#") and "source /opt/venv/bin/activate" in ln
        ]
        assert len(lines) == 0, "Found activation of /opt/venv (wrong venv) in .bashrc"

    def test_setup_venv_activates_correct_venv(self):
        setup = PROJECT_ROOT / "docker" / "run" / "fs" / "ins" / "setup_venv.sh"
        content = setup.read_text()
        # The last non-comment activate line should be venv-a0
        active_lines = [
            ln.strip()
            for ln in content.splitlines()
            if "source" in ln and "activate" in ln and not ln.strip().startswith("#")
        ]
        assert any(EXPECTED_VENV in ln for ln in active_lines), (
            f"setup_venv.sh should activate {EXPECTED_VENV}, "
            f"active lines: {active_lines}"
        )

    def test_google_packages_in_requirements(self):
        """Google API packages should be declared in requirements.txt."""
        reqs = (PROJECT_ROOT / "requirements.txt").read_text()
        assert "google-auth" in reqs, "google-auth missing from requirements.txt"
        assert "google-api-python-client" in reqs, (
            "google-api-python-client missing from requirements.txt"
        )
