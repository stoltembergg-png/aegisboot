#!/usr/bin/env python3
"""
AegisBoot — Distribution Governance & Policy Verification Test Suite

Validates that all governance documents, policies, branding disclaimers,
and community templates exist and contain required stipulations.
"""

import unittest
from pathlib import Path


class TestDistributionPolicies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent

    def test_root_governance_files_exist(self):
        required_files = [
            "DISTRIBUTION.md",
            "BRANDING.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "GOVERNANCE.md",
            "CHANGELOG_DISTRO.md",
            "README.md",
        ]
        for fname in required_files:
            file_path = self.repo_root / fname
            self.assertTrue(file_path.exists(), f"Required root document missing: {fname}")
            self.assertGreater(file_path.stat().st_size, 50, f"File {fname} is suspiciously empty!")

    def test_docs_directory_policies_exist(self):
        docs_policies = [
            "release-policy.md",
            "upstream-sync-policy.md",
            "local-patch-policy.md",
            "compatibility-policy.md",
            "build-instructions.md",
            "troubleshooting.md",
            "milestones.md",
            "versioning.md",
        ]
        for doc in docs_policies:
            doc_path = self.repo_root / "docs" / doc
            self.assertTrue(doc_path.exists(), f"Required policy in docs/ missing: {doc}")

    def test_branding_disclaimer_present(self):
        branding = (self.repo_root / "BRANDING.md").read_text(encoding="utf-8")
        self.assertIn("NOT an official release", branding)
        self.assertIn("Acidanthera", branding)

    def test_contributing_upstream_first_present(self):
        contributing = (self.repo_root / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("Upstream-First", contributing)
        self.assertIn("acidanthera/OpenCorePkg", contributing)

    def test_security_dual_triage_present(self):
        security = (self.repo_root / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("Vulnerability", security)
        self.assertIn("Acidanthera", security)

    def test_github_templates_exist(self):
        github_dir = self.repo_root / ".github"
        self.assertTrue((github_dir / "CODEOWNERS").exists(), "CODEOWNERS missing")
        self.assertTrue((github_dir / "labels.yml").exists(), "labels.yml missing")
        self.assertTrue((github_dir / "pull_request_template.md").exists(), "PR template missing")
        self.assertTrue((github_dir / "ISSUE_TEMPLATE" / "bug_report.yml").exists(), "bug_report.yml missing")
        self.assertTrue((github_dir / "ISSUE_TEMPLATE" / "sync_issue.yml").exists(), "sync_issue.yml missing")
        self.assertTrue((github_dir / "ISSUE_TEMPLATE" / "feature_request.yml").exists(), "feature_request.yml missing")
        self.assertTrue((github_dir / "ISSUE_TEMPLATE" / "config.yml").exists(), "issue config.yml missing")


if __name__ == "__main__":
    unittest.main()
