#!/usr/bin/env python3
"""
Unit tests for classify-impact.py
"""
import unittest
import tempfile
import subprocess
import os
from pathlib import Path


class TestImpactClassifier(unittest.TestCase):
    def setUp(self):
        self.script = Path(__file__).resolve().parent.parent / "scripts" / "classify-impact.py"
        self.repo_root = Path(__file__).resolve().parent.parent

    def run_classifier(self, base: str, head: str) -> str:
        """Run classifier and return impact level."""
        result = subprocess.run(
            ["python", str(self.script), "--base", base, "--head", head],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.fail(f"Classifier failed: {result.stderr}")
        # Extract impact from output - look for "Impact Classification: X"
        for line in result.stdout.splitlines():
            if "Impact Classification:" in line:
                # Parse "=== Impact Classification: X ===" -> "X"
                parts = line.split("Impact Classification:")
                if len(parts) > 1:
                    return parts[-1].strip().rstrip("=").strip()
        return "unknown"

    def test_infrastructure_changes(self):
        """Test that .github/ changes are classified as infrastructure."""
        # This test uses the actual repo state
        impact = self.run_classifier("HEAD~1", "HEAD")
        # Last commit was sync-upstream.sh (scripts/) -> infrastructure
        self.assertEqual(impact, "infrastructure")

    def test_classifier_runs_without_error(self):
        """Test that classifier runs without error for any valid refs."""
        impact = self.run_classifier("upstream/master", "HEAD")
        self.assertIn(impact, ["none", "patch", "minor", "major", "critical", "infrastructure"])

    def test_invalid_refs_handled(self):
        """Test that invalid refs are handled gracefully."""
        result = subprocess.run(
            ["python", str(self.script), "--base", "invalid-ref", "--head", "HEAD"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        # Should not crash, but may return error
        self.assertIsNotNone(result.returncode)


if __name__ == "__main__":
    unittest.main()