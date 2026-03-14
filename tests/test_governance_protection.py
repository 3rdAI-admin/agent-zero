"""Tests for governance directory protection (Phase 2f, SAFETY-03).

Ensures agent-initiated file operations cannot write to usr/governance/.
"""

import pytest

from python.helpers import files


class TestIsGovernancePath:
    """is_governance_path correctly identifies governance paths."""

    def test_audit_log_is_governance(self):
        """Expected use: audit.jsonl inside governance dir is protected."""
        path = files.get_abs_path("usr/governance/audit.jsonl")
        assert files.is_governance_path(path) is True

    def test_budgets_file_is_governance(self):
        """Expected use: run_budgets.json is protected."""
        path = files.get_abs_path("usr/governance/run_budgets.json")
        assert files.is_governance_path(path) is True

    def test_nested_governance_path(self):
        """Edge case: nested path inside governance is protected."""
        path = files.get_abs_path("usr/governance/subdir/policy.yml")
        assert files.is_governance_path(path) is True

    def test_governance_dir_itself(self):
        """Edge case: the governance directory itself is protected."""
        path = files.get_abs_path("usr/governance")
        assert files.is_governance_path(path) is True

    def test_regular_file_not_governance(self):
        """Expected use: regular files outside governance are not protected."""
        path = files.get_abs_path("usr/chats/test.txt")
        assert files.is_governance_path(path) is False

    def test_similar_name_not_governance(self):
        """Edge case: usr/governance_backup is NOT inside usr/governance."""
        path = files.get_abs_path("usr/governance_backup/file.txt")
        assert files.is_governance_path(path) is False


class TestCheckGovernanceWrite:
    """check_governance_write raises ValueError for governance paths."""

    def test_raises_for_governance_path(self):
        """Expected use: writing to governance dir raises ValueError."""
        path = files.get_abs_path("usr/governance/audit.jsonl")
        with pytest.raises(ValueError, match="governance directory"):
            files.check_governance_write(path)

    def test_passes_for_regular_path(self):
        """Expected use: writing to regular path does not raise."""
        path = files.get_abs_path("usr/workdir/output.txt")
        files.check_governance_write(path)  # Should not raise


class TestWriteFileGovernanceBlock:
    """write_file, write_file_bin, write_file_base64 block governance writes."""

    def test_write_file_blocked(self, tmp_path):
        """Failure case: write_file to governance raises ValueError."""
        with pytest.raises(ValueError, match="governance directory"):
            files.write_file("usr/governance/evil.txt", "payload")

    def test_write_file_bin_blocked(self):
        """Failure case: write_file_bin to governance raises ValueError."""
        with pytest.raises(ValueError, match="governance directory"):
            files.write_file_bin("usr/governance/evil.bin", b"payload")

    def test_write_file_base64_blocked(self):
        """Failure case: write_file_base64 to governance raises ValueError."""
        import base64

        content = base64.b64encode(b"payload").decode()
        with pytest.raises(ValueError, match="governance directory"):
            files.write_file_base64("usr/governance/evil.b64", content)

    def test_delete_dir_blocked(self):
        """Failure case: delete_dir on governance raises ValueError."""
        with pytest.raises(ValueError, match="governance directory"):
            files.delete_dir("usr/governance")
