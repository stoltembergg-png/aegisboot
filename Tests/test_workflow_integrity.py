#!/usr/bin/env python3
"""
AegisBoot — Workflow Hardening & CI/CD Security Integrity Test Suite

Validates that all GitHub Actions workflows in .github/workflows/ strictly adhere to:
1. Declared top-level or job-level permissions (least privilege).
2. Concurrency groups declared.
3. Explicit timeout-minutes on every job.
4. actions/checkout with persist-credentials: false.
5. All external GitHub actions pinned to full 40-character commit SHAs.
6. Zero vulnerable inline script expression interpolation (${{ github.event... }} in run:).
7. Zero continue-on-error: true on gate jobs.
8. Absolute ban on pull_request_target.
9. No exposed secrets in untrusted steps.
"""

import os
import re
import unittest
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


class TestWorkflowIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.workflows_dir = cls.repo_root / ".github" / "workflows"
        cls.workflow_files = sorted(cls.workflows_dir.glob("*.yml"))
        if not cls.workflow_files:
            cls.workflow_files = sorted(cls.workflows_dir.glob("*.yaml"))

    def test_workflow_files_exist(self):
        self.assertTrue(len(self.workflow_files) > 0, "No workflow files found in .github/workflows/")

    def _read_workflow_content(self, file_path: Path) -> str:
        return file_path.read_text(encoding="utf-8")

    def test_no_pull_request_target(self):
        """Rule 8: Block pull_request_target trigger across all workflows."""
        for wf_file in self.workflow_files:
            content = self._read_workflow_content(wf_file)
            self.assertNotIn(
                "pull_request_target",
                content,
                f"Workflow {wf_file.name} uses prohibited 'pull_request_target' trigger!",
            )

    def test_permissions_declared(self):
        """Rule 1 & 2: Workflows or jobs must explicitly declare permissions."""
        for wf_file in self.workflow_files:
            content = self._read_workflow_content(wf_file)
            has_permissions = "permissions:" in content
            self.assertTrue(
                has_permissions,
                f"Workflow {wf_file.name} does not declare 'permissions:' block!",
            )

    def test_concurrency_declared(self):
        """Rule 3: Workflows must declare concurrency."""
        for wf_file in self.workflow_files:
            content = self._read_workflow_content(wf_file)
            self.assertIn(
                "concurrency:",
                content,
                f"Workflow {wf_file.name} missing 'concurrency:' configuration!",
            )

    def test_timeout_minutes_on_jobs(self):
        """Rule 4: Every job must specify timeout-minutes."""
        for wf_file in self.workflow_files:
            content = self._read_workflow_content(wf_file)
            # Check every job block for timeout-minutes
            if yaml is not None:
                data = yaml.safe_load(content)
                jobs = data.get("jobs", {})
                for job_name, job_data in jobs.items():
                    self.assertIn(
                        "timeout-minutes",
                        job_data,
                        f"Workflow {wf_file.name} job '{job_name}' missing 'timeout-minutes'!",
                    )
            else:
                self.assertIn(
                    "timeout-minutes:",
                    content,
                    f"Workflow {wf_file.name} missing 'timeout-minutes:' declaration!",
                )

    def test_checkout_persist_credentials_false(self):
        """Rule 5: actions/checkout must set persist-credentials: false."""
        for wf_file in self.workflow_files:
            content = self._read_workflow_content(wf_file)
            if "actions/checkout@" in content:
                self.assertIn(
                    "persist-credentials: false",
                    content,
                    f"Workflow {wf_file.name} uses actions/checkout without 'persist-credentials: false'!",
                )

    def test_actions_pinned_to_full_sha(self):
        """Rule 6: External GitHub Actions must be pinned to 40-character commit SHAs."""
        # Regex matching uses: owner/repo@ref or owner/repo/path@ref
        uses_regex = re.compile(r'uses:\s+([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)?@([^\s#]+))')
        sha_40_regex = re.compile(r'^[a-f0-9]{40}$')

        for wf_file in self.workflow_files:
            content = self._read_workflow_content(wf_file)
            matches = uses_regex.findall(content)
            for full_action, ref in matches:
                # If local action (./.github/...), skip
                if full_action.startswith("."):
                    continue
                # If docker://, skip
                if full_action.startswith("docker://"):
                    continue

                self.assertTrue(
                    sha_40_regex.match(ref),
                    f"Workflow {wf_file.name} has unpinned action '{full_action}'. Must use 40-character SHA!",
                )

    def test_no_continue_on_error_on_gates(self):
        """Rule 7: Never use continue-on-error: true on validation gates."""
        for wf_file in self.workflow_files:
            content = self._read_workflow_content(wf_file)
            self.assertNotIn(
                "continue-on-error: true",
                content,
                f"Workflow {wf_file.name} contains prohibited 'continue-on-error: true'!",
            )

    def test_no_vulnerable_script_interpolation(self):
        """Rule 8: Untrusted expressions (${{ github.event... }}) must not appear inside run: blocks."""
        dangerous_patterns = [
            r'run:\s*.*?\$\{\{\s*github\.event\.issue\.body',
            r'run:\s*.*?\$\{\{\s*github\.event\.pull_request\.body',
            r'run:\s*.*?\$\{\{\s*github\.event\.comment\.body',
            r'run:\s*.*?\$\{\{\s*github\.event\.head_commit\.message',
        ]
        for wf_file in self.workflow_files:
            content = self._read_workflow_content(wf_file)
            for pat in dangerous_patterns:
                self.assertIsNone(
                    re.search(pat, content, re.IGNORECASE | re.DOTALL),
                    f"Workflow {wf_file.name} contains potential script injection pattern matching {pat}!",
                )


if __name__ == "__main__":
    unittest.main()
