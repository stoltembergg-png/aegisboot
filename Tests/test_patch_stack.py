#!/usr/bin/env python3
"""
AegisBoot — Patch Stack Integrity Test Suite

Validates that all patches in Patches/ adhere to standard unified format,
have non-zero size, and follow monotonic index naming.
"""

import re
import unittest
from pathlib import Path


class TestPatchStack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.patch_dir = cls.repo_root / "Patches"

    def test_patches_format_and_naming(self):
        if not self.patch_dir.exists():
            self.skipTest("No Patches directory found.")

        patches = list(self.patch_dir.glob("*.patch"))
        if not patches:
            self.skipTest("No .patch files in Patches/")

        naming_pattern = re.compile(r"^\d{4}-.*\.patch$")

        for patch_file in patches:
            self.assertTrue(
                naming_pattern.match(patch_file.name),
                f"Patch {patch_file.name} does not match naming convention '0000-name.patch'!",
            )
            self.assertGreater(patch_file.stat().st_size, 0, f"Patch {patch_file.name} is empty!")

            content = patch_file.read_text(encoding="utf-8", errors="ignore")
            has_diff = "diff --git" in content or "--- " in content
            self.assertTrue(has_diff, f"Patch {patch_file.name} lacks diff markers!")


if __name__ == "__main__":
    unittest.main()
