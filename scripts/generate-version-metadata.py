#!/usr/bin/env python3
"""
AegisBoot — Automated Version Metadata Generator

Extracts OpenCore version from OcMainLib.h, git commit details, toolchain pins,
and patch stack status, outputting a machine-readable JSON manifest conforming
to the AegisBoot distribution schema.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def get_git_info(repo_root: Path) -> dict:
    info = {
        "commit_sha": "unknown",
        "commit_sha_short": "unknown",
        "commit_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "branch": "master",
        "remote_origin": "https://github.com/acidanthera/OpenCorePkg.git",
    }
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        info["commit_sha"] = sha
        info["commit_sha_short"] = sha[:7]
    except Exception:
        pass

    try:
        date_str = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if date_str:
            info["commit_date"] = date_str
    except Exception:
        pass

    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if branch:
            info["branch"] = branch
    except Exception:
        pass

    try:
        remote = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if remote:
            info["remote_origin"] = remote
    except Exception:
        pass

    return info


def extract_opencore_version(repo_root: Path) -> str:
    header_path = repo_root / "Include" / "Acidanthera" / "Library" / "OcMainLib.h"
    if not header_path.exists():
        return "1.0.8"

    content = header_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'#define\s+OPEN_CORE_VERSION\s+"([^"]+)"', content)
    if match:
        return match.group(1)
    return "1.0.8"


def get_patch_stack_info(repo_root: Path) -> list:
    patches_dir = repo_root / "Patches"
    if not patches_dir.exists():
        return []

    patches = []
    for patch_file in sorted(patches_dir.glob("*.patch")):
        patch_info = {
            "name": patch_file.name,
            "path": f"Patches/{patch_file.name}",
            "size_bytes": patch_file.stat().st_size,
        }
        content = patch_file.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"Upstream-Status:\s*([^\r\n]+)", content, re.IGNORECASE)
        patch_info["upstream_status"] = match.group(1).strip() if match else "pending"
        patches.append(patch_info)
    return patches


def load_toolchain_pins(repo_root: Path) -> dict:
    pin_file = repo_root / "toolchains" / "toolchain-pins.json"
    if pin_file.exists():
        try:
            with open(pin_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def main():
    parser = argparse.ArgumentParser(description="Generate AegisBoot version metadata JSON.")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parent.parent), help="Root directory of the repository")
    parser.add_argument("--output", default="distro-version.json", help="Output file path for JSON metadata")
    parser.add_argument("--revision", type=int, default=1, help="Downstream distribution revision index")
    parser.add_argument("--channel", default="stable", choices=["edge", "staging", "stable"], help="Release channel")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    oc_ver = extract_opencore_version(repo_root)
    git_info = get_git_info(repo_root)
    patch_info = get_patch_stack_info(repo_root)
    toolchain_info = load_toolchain_pins(repo_root)

    full_version_tag = f"v{oc_ver}-aegis.{args.revision}+{git_info['commit_sha_short']}"

    manifest = {
        "$schema": "https://aegisboot.dev/schema/distro-version.v1.json",
        "distribution": {
            "name": "AegisBoot",
            "description": "Continuous Integration Downstream Distribution of OpenCorePkg",
            "version": full_version_tag,
            "distro_revision": args.revision,
            "channel": args.channel,
            "build_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        "upstream": {
            "repository": git_info["remote_origin"],
            "branch": git_info["branch"],
            "version": oc_ver,
            "commit_sha": git_info["commit_sha"],
            "commit_sha_short": git_info["commit_sha_short"],
            "commit_date": git_info["commit_date"],
        },
        "toolchain_pins": toolchain_info,
        "patch_stack": {
            "count": len(patch_info),
            "patches": patch_info,
        },
    }

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = repo_root / out_path

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[OK] Generated version metadata manifest: {out_path}")
    print(f"     Distribution Version: {full_version_tag}")
    print(f"     Upstream OpenCore:    {oc_ver} ({git_info['commit_sha_short']})")
    print(f"     Patches Tracked:      {len(patch_info)}")


if __name__ == "__main__":
    main()
