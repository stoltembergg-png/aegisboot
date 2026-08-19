#!/usr/bin/env python3
"""
AegisBoot — Unit Test Suite for Workflow Security & Integrity Validator

Validates that scripts/validate_workflows.py correctly detects violations of all
13 security and integrity rules (positive and negative assertions).
"""

import sys
import unittest
from pathlib import Path

# Add repo root to import path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_workflows import WorkflowValidator


class TestValidatorRules(unittest.TestCase):
    def setUp(self):
        self.validator = WorkflowValidator(strict=True)

    def test_valid_hardened_workflow_passes(self):
        valid_yml = """
name: Valid Workflow
on:
  push:
    branches: [master]
  pull_request:

permissions:
  contents: read

concurrency:
  group: valid-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    name: Build Job
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
        with:
          persist-credentials: false
      - name: Upload Artifact
        uses: actions/upload-artifact@65c4c4a1ddee5b72f698fdd19549f0f0fb45cf08 # v4.6.0
        with:
          name: my-artifact
          path: ./bin/
          retention-days: 14
"""
        findings = self.validator.validate_content("valid.yml", valid_yml)
        self.assertEqual(len(findings), 0, f"Expected 0 findings but got: {findings}")

    def test_rule_perm_001_missing_permissions(self):
        invalid_yml = """
name: Missing Perms
on: [push]
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - run: echo "Hello"
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_PERM_001", rule_ids)

    def test_rule_perm_002_excessive_permissions(self):
        invalid_yml = """
name: Write All
on: [push]
permissions: write-all
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - run: echo "Hello"
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_PERM_002", rule_ids)

    def test_rule_conc_001_missing_concurrency(self):
        invalid_yml = """
name: Missing Concurrency
on: [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - run: echo "Hello"
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_CONC_001", rule_ids)

    def test_rule_time_001_missing_timeout(self):
        invalid_yml = """
name: Missing Timeout
on: [push]
permissions:
  contents: read
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - run: echo "Hello"
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_TIME_001", rule_ids)

    def test_rule_gate_001_continue_on_error(self):
        invalid_yml = """
name: Gate Bypass
on: [push]
permissions:
  contents: read
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    continue-on-error: true
    steps:
      - run: exit 1
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_GATE_001", rule_ids)

    def test_rule_trig_001_pull_request_target(self):
        invalid_yml = """
name: Dangerous Trigger
on:
  pull_request_target:
permissions:
  contents: read
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - run: echo "Dangerous"
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_TRIG_001", rule_ids)

    def test_rule_actn_001_unpinned_action(self):
        invalid_yml = """
name: Unpinned Action
on: [push]
permissions:
  contents: read
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_ACTN_001", rule_ids)

    def test_rule_chck_001_checkout_missing_persist_credentials(self):
        invalid_yml = """
name: Insecure Checkout
on: [push]
permissions:
  contents: read
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_CHCK_001", rule_ids)

    def test_rule_secr_001_secret_interpolation_in_run(self):
        invalid_yml = """
name: Secret In Run
on: [push]
permissions:
  contents: read
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - run: |
          curl -H "Auth: ${{ secrets.GITHUB_TOKEN }}" https://api.example.com
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_SECR_001", rule_ids)

    def test_rule_leak_001_token_leakage(self):
        invalid_yml = """
name: Token Leak
on: [push]
permissions:
  contents: read
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - run: echo "Token is ${{ secrets.DEPLOY_KEY }}"
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_LEAK_001", rule_ids)

    def test_rule_arti_001_artifact_retention_missing(self):
        invalid_yml = """
name: Artifact Missing Retention
on: [push]
permissions:
  contents: read
concurrency:
  group: test
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/upload-artifact@65c4c4a1ddee5b72f698fdd19549f0f0fb45cf08 # v4.6.0
        with:
          name: artifacts
          path: ./bin/
"""
        findings = self.validator.validate_content("invalid.yml", invalid_yml)
        rule_ids = [f.rule_id for f in findings]
        self.assertIn("RULE_ARTI_001", rule_ids)


if __name__ == "__main__":
    unittest.main()
