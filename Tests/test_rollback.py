#!/usr/bin/env python3
"""
Unit tests for rollback.sh
"""
import unittest
import subprocess
import tempfile
import os
from pathlib import Path


class TestRollbackScript(unittest.TestCase):
    def setUp(self):
        self.script = Path(__file__).resolve().parent.parent / "scripts" / "rollback.sh"
        self.repo_root = Path(__file__).resolve().parent.parent

    def test_script_syntax(self):
        """Test that script has valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", str(self.script)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"Syntax error: {result.stderr}")

    def test_help_output(self):
        """Test that --help works."""
        result = subprocess.run(
            ["bash", str(self.script), "--help"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)
        self.assertIn("--tag", result.stdout)
        self.assertIn("--commit", result.stdout)
        self.assertIn("--dry-run", result.stdout)

    def test_dry_run_mode_with_help(self):
        """Test that --dry-run works without making changes (with --help)."""
        result = subprocess.run(
            ["bash", str(self.script), "--dry-run", "--help"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        # --help should exit 0 and show usage
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)

    def test_invalid_tag_handling(self):
        """Test that invalid tag is handled gracefully."""
        result = subprocess.run(
            ["bash", str(self.script), "--dry-run", "--tag", "invalid-tag-that-does-not-exist"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        # Should exit with error for non-existent tag
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Tag not found", result.stdout)

    def test_conflicting_options(self):
        """Test that --tag and --commit together fails."""
        result = subprocess.run(
            ["bash", str(self.script), "--tag", "v1.0.0", "--commit", "abc123"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Cannot specify both", result.stdout)


if __name__ == "__main__":
    unittest.main()