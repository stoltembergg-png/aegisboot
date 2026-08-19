#!/usr/bin/env python3
"""
AegisBoot — Unit Tests for Build Manifest Generator
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

# Add repo root to import path
REPO_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_build_manifest import build_manifest, calculate_hashes


class TestBuildManifest(unittest.TestCase):
    def test_calculate_hashes(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(b"Hello World AegisBoot Deterministic Test\n")
            tf_path = Path(tf.name)

        try:
            hashes = calculate_hashes(tf_path)
            self.assertIn("sha256", hashes)
            self.assertIn("sha512", hashes)
            self.assertEqual(len(hashes["sha256"]), 64)
            self.assertEqual(len(hashes["sha512"]), 128)
        finally:
            tf_path.unlink()

    def test_build_manifest_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            art_dir = Path(tmpdir) / "artifacts"
            art_dir.mkdir()
            (art_dir / "OpenCore.efi").write_bytes(b"MZ\x00\x00FAKE_EFI_BINARY_PAYLOAD")
            (art_dir / "OpenRuntime.efi").write_bytes(b"MZ\x00\x00FAKE_RUNTIME_PAYLOAD")

            manifest = build_manifest(
                repo_root=REPO_ROOT,
                artifacts_dir=art_dir,
                target_profile="RELEASE",
                target_arch="X64",
                toolchain="CLANGPDB",
            )

            self.assertEqual(manifest["distribution"], "AegisBoot")
            self.assertEqual(manifest["compilation"]["target_profile"], "RELEASE")
            self.assertEqual(manifest["compilation"]["target_architecture"], "X64")
            self.assertEqual(manifest["compilation"]["toolchain"], "CLANGPDB")
            self.assertEqual(manifest["artifacts_summary"]["count"], 2)

            filenames = [a["filename"] for a in manifest["artifacts"]]
            self.assertIn("OpenCore.efi", filenames)
            self.assertIn("OpenRuntime.efi", filenames)


if __name__ == "__main__":
    unittest.main()
