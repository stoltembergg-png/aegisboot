#!/usr/bin/env python3
"""
AegisBoot — Idempotent GitHub Label Synchronizer

Reads .github/labels.yml and creates/updates repository labels via the GitHub CLI (gh).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def parse_labels_yaml(yaml_path: Path) -> list:
    content = yaml_path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "labels" in data:
            return data["labels"]

    # Fallback simple parser if pyyaml is not present
    labels = []
    current_label = {}
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("- name:"):
            if current_label and "name" in current_label:
                labels.append(current_label)
            current_label = {"name": line.split(":", 1)[1].strip().strip('"').strip("'")}
        elif line.startswith("color:"):
            current_label["color"] = line.split(":", 1)[1].strip().strip('"').strip("'").lstrip("#")
        elif line.startswith("description:"):
            current_label["description"] = line.split(":", 1)[1].strip().strip('"').strip("'")
    if current_label and "name" in current_label:
        labels.append(current_label)
    return labels


def main():
    parser = argparse.ArgumentParser(description="Sync GitHub labels from .github/labels.yml")
    parser.add_argument("--file", default=".github/labels.yml", help="Path to labels.yml")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing gh")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    label_file = repo_root / args.file

    if not label_file.exists():
        print(f"[ERROR] Label file not found: {label_file}")
        sys.exit(1)

    labels = parse_labels_yaml(label_file)
    print(f"Loaded {len(labels)} label definitions from {label_file.name}")

    has_gh = shutil.which("gh") is not None

    for label in labels:
        name = label.get("name")
        color = label.get("color", "cccccc").lstrip("#")
        desc = label.get("description", "")

        if args.dry_run or not has_gh:
            print(f"  [DRY-RUN] Label: '{name}' | Color: #{color} | Desc: '{desc}'")
            continue

        cmd = ["gh", "label", "create", name, "--color", color, "--description", desc, "--force"]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  [OK] Synced label: {name}")
        except subprocess.CalledProcessError as e:
            print(f"  [WARN] Failed to sync label: {name} ({e})")

    print("=== Label Synchronization Complete ===")


if __name__ == "__main__":
    main()
