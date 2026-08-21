#!/usr/bin/env python3
"""
AegisBoot — Automated Impact Classifier

Analyzes git diff and classifies impact level for sync PRs.
Impact levels: none, patch, minor, major, critical, infrastructure
"""

import argparse
import re
import subprocess
import sys
import os
from pathlib import Path


CRITICAL_PATHS = [
    r"Library/OcMainLib",
    r"Library/OcBootManagementLib",
    r"Library/OcAppleBootPolicyLib",
    r"Library/OcGuardLib",
    r"Library/OcCryptoLib",
    r"Library/OcFileLib",
    r"Library/OcDebugLogLib",
    r"Library/OcConsoleLib",
    r"Library/OcAppleKernelLib",
    r"Library/OcConfigurationLib",
    r"Library/OcKextLib",
    r"Library/OcACPILib",
    r"Library/OcSmbiosLib",
    r"Library/OcVariableLib",
    r"Library/OcStringLib",
    r"Library/OcDevicePathLib",
    r"Library/OcMiscLib",
    r"Library/OcSerializeLib",
    r"Library/OcXmlLib",
    r"Library/OcAcpiTableLib",
    r"Library/OcPciLib",
    r"Library/OcTimerLib",
    r"Library/OcRtcLib",
    r"Library/OcHashLib",
    r"Library/OcCompressionLib",
    r"Library/OcDecompressLib",
]

SECURITY_PATHS = [
    r"Library/OcAppleSecureBootLib",
    r"Library/OcVaultLib",
    r"Library/OcCryptoLib",
    r"Library/OcVerifyLib",
]

MAJOR_PATHS = [
    r"Include/.*\.h",
    r"Library/.*Lib\.c",
    r"Platform/.*",
    r"Drivers/.*",
    r"Universal/.*",
    r"UDK/.*",
]

INFRASTRUCTURE_PATHS = [
    r"\.github/.*",
    r"scripts/.*",
    r"toolchains/.*",
    r"Tests/.*",
    r"Dockerfiles/.*",
    r"docker-compose\.ya?ml",
    r"docker-apparmor\.sh",
    r"build_.*\.tool",
    r"Uncrustify\.yml",
    r"Docs/.*",
    r"CHANGELOG.*\.md",
]

DOCS_PATHS = [
    r"Docs/.*",
    r"README\.md",
    r"\.md$",
    r"CHANGELOG.*\.md",
]


def run_git_diff(base: str, head: str) -> str:
    """Run git diff between base and head."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base}..{head}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] git diff failed: {e}", file=sys.stderr)
        return ""


def classify_file(filepath: str) -> str:
    """Classify a single file path."""
    # Documentation only
    for pattern in DOCS_PATHS:
        if re.search(pattern, filepath, re.IGNORECASE):
            return "none"

    # Infrastructure/CI only
    for pattern in INFRASTRUCTURE_PATHS:
        if re.search(pattern, filepath, re.IGNORECASE):
            return "infrastructure"

    # Security-related
    for pattern in SECURITY_PATHS:
        if re.search(pattern, filepath, re.IGNORECASE):
            return "critical"

    # Critical core libraries
    for pattern in CRITICAL_PATHS:
        if re.search(pattern, filepath, re.IGNORECASE):
            return "critical"

    # Major changes (new drivers, platforms, breaking API changes)
    for pattern in MAJOR_PATHS:
        if re.search(pattern, filepath, re.IGNORECASE):
            return "minor"  # Default to minor for code changes

    return "patch"


def classify_impact(base: str, head: str) -> str:
    """Classify overall impact from git diff."""
    diff_output = run_git_diff(base, head)
    if not diff_output.strip():
        return "none"

    files = diff_output.strip().split("\n")
    impacts = []

    for f in files:
        f = f.strip()
        if not f:
            continue
        impact = classify_file(f)
        impacts.append(impact)

    # Priority order: critical > major > minor > patch > infrastructure > none
    priority = {
        "critical": 5,
        "major": 4,
        "minor": 3,
        "patch": 2,
        "infrastructure": 1,
        "none": 0,
    }

    max_impact = max(impacts, key=lambda x: priority.get(x, 0))
    return max_impact


def main():
    parser = argparse.ArgumentParser(description="Classify impact of git changes")
    parser.add_argument("--base", required=True, help="Base commit/branch (e.g., origin/master)")
    parser.add_argument("--head", required=True, help="Head commit/branch (e.g., sync/upstream-xxx)")
    parser.add_argument("--output", help="Output file for impact label")
    args = parser.parse_args()

    impact = classify_impact(args.base, args.head)
    print(f"\n=== Impact Classification: {impact} ===")

    if args.output:
        with open(args.output, "w") as f:
            f.write(impact)
        print(f"Impact written to {args.output}")

    # Output for GitHub Actions using environment files (modern approach)
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"impact={impact}\n")
    else:
        # Fallback for older runners (deprecated)
        print(f"::set-output name=impact::{impact}")

    sys.exit(0)


if __name__ == "__main__":
    main()