#!/usr/bin/env python3
"""
Unit tests for manage-milestones.py
"""
import unittest
import subprocess
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestManageMilestones(unittest.TestCase):
    def setUp(self):
        self.script = Path(__file__).resolve().parent.parent / "scripts" / "manage-milestones.py"
        self.repo_root = Path(__file__).resolve().parent.parent

    def test_script_syntax(self):
        """Test that script has valid Python syntax."""
        result = subprocess.run(
            ["python", "-m", "py_compile", str(self.script)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"Syntax error: {result.stderr}")

    def test_help_output(self):
        """Test that --help works."""
        result = subprocess.run(
            ["python", str(self.script), "--help"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())
        self.assertIn("sync-cycle", result.stdout)
        self.assertIn("distro", result.stdout)
        self.assertIn("hotfix", result.stdout)
        self.assertIn("list", result.stdout)
        self.assertIn("close", result.stdout)

    def test_sync_cycle_requires_version(self):
        """Test that sync-cycle requires --version."""
        result = subprocess.run(
            ["python", str(self.script), "sync-cycle"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--version", result.stderr.lower())

    def test_distro_requires_version_and_revision(self):
        """Test that distro requires --version and --revision."""
        result = subprocess.run(
            ["python", str(self.script), "distro"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--version", result.stderr.lower())

    def test_hotfix_requires_id(self):
        """Test that hotfix requires --id."""
        result = subprocess.run(
            ["python", str(self.script), "hotfix"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--id", result.stderr.lower())

    def test_list_milestones(self):
        """Test that list command works (returns 0 even without token)."""
        result = subprocess.run(
            ["python", str(self.script), "list"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

    def test_close_requires_title(self):
        """Test that close requires --title."""
        result = subprocess.run(
            ["python", str(self.script), "close"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--title", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()