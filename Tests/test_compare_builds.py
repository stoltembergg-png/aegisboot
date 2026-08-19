#!/usr/bin/env python3
"""
AegisBoot — Unit Tests for Build Comparison & Reproducibility Engine
"""

import json
import tempfile
import unittest
from pathlib import Path

# Add repo root to import path
REPO_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(REPO_ROOT))

from scripts.compare_builds import compare_builds


class TestCompareBuilds(unittest.TestCase):
    def test_identical_builds_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
            path_a = Path(tmp_a)
            path_b = Path(tmp_b)

            (path_a / "OpenCore.efi").write_bytes(b"IDENTICAL_BYTES_12345")
            (path_b / "OpenCore.efi").write_bytes(b"IDENTICAL_BYTES_12345")

            (path_a / "Drivers").mkdir()
            (path_b / "Drivers").mkdir()
            (path_a / "Drivers" / "OpenRuntime.efi").write_bytes(b"RUNTIME_PAYLOAD_ABC")
            (path_b / "Drivers" / "OpenRuntime.efi").write_bytes(b"RUNTIME_PAYLOAD_ABC")

            report = compare_builds(path_a, path_b)
            summary = report["comparison_summary"]

            self.assertTrue(summary["is_identical"])
            self.assertEqual(summary["drift_classification"], "REPRODUCIBLE")
            self.assertEqual(summary["reproducibility_percentage"], 100.0)
            self.assertEqual(summary["matching_artifacts"], 2)
            self.assertEqual(summary["mismatching_artifacts"], 0)

    def test_drifted_builds_detected(self):
        with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
            path_a = Path(tmp_a)
            path_b = Path(tmp_b)

            (path_a / "OpenCore.efi").write_bytes(b"PAYLOAD_VERSION_A")
            (path_b / "OpenCore.efi").write_bytes(b"PAYLOAD_VERSION_B")

            report = compare_builds(path_a, path_b)
            summary = report["comparison_summary"]

            self.assertFalse(summary["is_identical"])
            self.assertEqual(summary["matching_artifacts"], 0)
            self.assertEqual(summary["mismatching_artifacts"], 1)
            self.assertIn("DRIFT", summary["drift_classification"])

    def test_missing_files_detected(self):
        with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
            path_a = Path(tmp_a)
            path_b = Path(tmp_b)

            (path_a / "OpenCore.efi").write_bytes(b"COMMON_PAYLOAD")
            (path_b / "OpenCore.efi").write_bytes(b"COMMON_PAYLOAD")

            (path_b / "ExtraDriver.efi").write_bytes(b"EXTRA_PAYLOAD")

            report = compare_builds(path_a, path_b)
            summary = report["comparison_summary"]

            self.assertFalse(summary["is_identical"])
            self.assertEqual(summary["drift_classification"], "STRUCTURAL_DRIFT")
            self.assertEqual(summary["matching_artifacts"], 1)
            self.assertEqual(summary["mismatching_artifacts"], 1)


if __name__ == "__main__":
    unittest.main()
