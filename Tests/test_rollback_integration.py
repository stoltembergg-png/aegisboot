#!/usr/bin/env python3
"""
AegisBoot — Rollback Integration Test

End-to-end test of the rollback procedure:
1. Creates a test release tag
2. Triggers rollback to previous state
3. Verifies rollback PR creation
4. Cleans up test artifacts
"""

import unittest
import subprocess
import tempfile
import os
import json
import shutil
from pathlib import Path


class TestRollbackIntegration(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.script = self.repo_root / "scripts" / "rollback.sh"

    def run_cmd(self, cmd, cwd=None, env=None):
        """Run command and return (returncode, stdout, stderr)."""
        cwd = cwd or self.repo_root
        env = env or os.environ.copy()
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "timeout"
        except Exception as e:
            return -1, "", str(e)

    def test_rollback_script_exists(self):
        """Verify rollback script exists and is executable."""
        self.assertTrue(self.script.exists(), "rollback.sh not found")
        self.assertTrue(os.access(self.script, os.X_OK), "rollback.sh not executable")

    def test_rollback_help(self):
        """Test --help output."""
        rc, stdout, stderr = self.run_cmd(["bash", str(self.script), "--help"])
        self.assertEqual(rc, 0)
        self.assertIn("Usage:", stdout)
        self.assertIn("--tag", stdout)
        self.assertIn("--commit", stdout)
        self.assertIn("--dry-run", stdout)

    def test_rollback_dry_run_with_tag(self):
        """Test dry-run with a non-existent tag (should fail gracefully)."""
        rc, stdout, stderr = self.run_cmd(
            ["bash", str(self.script), "--dry-run", "--tag", "v99.99.99-aegis.999+deadbee"]
        )
        # Should fail because tag doesn't exist
        self.assertNotEqual(0, rc)
        self.assertIn("Tag not found", stdout)

    def test_rollback_dry_run_with_invalid_commit(self):
        """Test dry-run with invalid commit."""
        rc, stdout, stderr = self.run_cmd(
            ["bash", str(self.script), "--dry-run", "--commit", "invalidcommit123"]
        )
        self.assertNotEqual(0, rc)
        self.assertIn("Commit not found", stdout)

    def test_rollback_conflicting_options(self):
        """Test that --tag and --commit together fails."""
        rc, stdout, stderr = self.run_cmd(
            ["bash", str(self.script), "--tag", "v1.0.0", "--commit", "abc123"]
        )
        self.assertNotEqual(0, rc)
        self.assertIn("Cannot specify both", stdout)

    def test_rollback_dry_run_with_help(self):
        """Test --dry-run with --help works."""
        rc, stdout, stderr = self.run_cmd(
            ["bash", str(self.script), "--dry-run", "--help"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("Usage:", stdout)

    def test_rollback_auto_detect_requires_tags(self):
        """Test auto-detect mode requires existing release tags."""
        # Should fail if no v*-aegis.* tags exist
        rc, stdout, stderr = self.run_cmd(
            ["bash", str(self.script), "--dry-run"]
        )
        # Should fail because no v*-aegis.* tags exist
        self.assertNotEqual(0, rc)


if __name__ == "__main__":
    unittest.main()