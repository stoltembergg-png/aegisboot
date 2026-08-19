#!/usr/bin/env python3
"""
Unit tests for collect-metrics.py
"""
import unittest
import subprocess
import tempfile
import os
import json
from pathlib import Path


class TestCollectMetrics(unittest.TestCase):
    def setUp(self):
        self.script = Path(__file__).resolve().parent.parent / "scripts" / "collect-metrics.py"
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
        self.assertIn("--format", result.stdout)
        self.assertIn("--output", result.stdout)

    def test_json_output(self):
        """Test that JSON output works."""
        result = subprocess.run(
            ["python", str(self.script), "--format", "json"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        # Should be valid JSON
        data = json.loads(result.stdout)
        self.assertIn("timestamp", data)
        self.assertIn("git", data)
        self.assertIn("patches", data)
        self.assertIn("build", data)
        self.assertIn("ci", data)
        self.assertIn("system", data)

    def test_prometheus_output(self):
        """Test that Prometheus output works."""
        result = subprocess.run(
            ["python", str(self.script), "--format", "prometheus"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        # Should contain metric lines
        self.assertIn("git_head_sha", result.stdout)
        self.assertIn("patches_patch_count", result.stdout)

    def test_output_file(self):
        """Test writing to output file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
        try:
            result = subprocess.run(
                ["python", str(self.script), "--format", "json", "--output", temp_path],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)
            # Verify file was created and has valid JSON
            with open(temp_path) as f:
                data = json.load(f)
            self.assertIn("timestamp", data)
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()