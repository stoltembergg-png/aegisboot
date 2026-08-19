#!/usr/bin/env python3
"""
AegisBoot — Version Metadata Generator Test Suite

Validates that generate-version-metadata.py extracts versions accurately,
embeds git commit details, and outputs schema-compliant JSON.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestVersionMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.script_path = cls.repo_root / "scripts" / "generate-version-metadata.py"

    def test_script_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_json = Path(tmpdir) / "distro-version.json"
            cmd = [
                sys.executable,
                str(self.script_path),
                "--repo-root",
                str(self.repo_root),
                "--output",
                str(out_json),
                "--revision",
                "1",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Script failed: {res.stderr}")
            self.assertTrue(out_json.exists(), "Output JSON file was not generated!")

            with open(out_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check schema keys
            self.assertIn("distribution", data)
            self.assertIn("upstream", data)
            self.assertIn("toolchain_pins", data)
            self.assertIn("patch_stack", data)

            distro = data["distribution"]
            self.assertEqual(distro["name"], "AegisBoot")
            self.assertEqual(distro["distro_revision"], 1)
            self.assertTrue(distro["version"].startswith("v1.0."))

            upstream = data["upstream"]
            self.assertEqual(upstream["version"], "1.0.8")
            self.assertTrue(len(upstream["commit_sha"]) >= 7)


if __name__ == "__main__":
    unittest.main()
