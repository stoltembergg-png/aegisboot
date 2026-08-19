#!/usr/bin/env python3
"""
AegisBoot — Automated Compilation Metadata & Build Manifest Generator
"""

import argparse
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


def calculate_hashes(file_path: Path) -> Dict[str, str]:
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
            sha512.update(chunk)
    return {
        "sha256": sha256.hexdigest(),
        "sha512": sha512.hexdigest(),
    }


def get_git_metadata(repo_root: Path) -> Dict[str, Any]:
    meta = {
        "commit_sha": "unknown",
        "commit_sha_short": "unknown",
        "commit_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "branch": "master",
        "is_dirty": False,
    }
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, stderr=subprocess.DEVNULL, text=True
        ).strip()
        meta["commit_sha"] = sha
        meta["commit_sha_short"] = sha[:7]
    except Exception:
        pass

    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=repo_root, stderr=subprocess.DEVNULL, text=True
        ).strip()
        meta["is_dirty"] = len(status) > 0
    except Exception:
        pass

    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root, stderr=subprocess.DEVNULL, text=True
        ).strip()
        meta["branch"] = branch
    except Exception:
        pass

    return meta


def collect_artifacts(artifacts_dir: Path) -> List[Dict[str, Any]]:
    artifacts = []
    if not artifacts_dir.exists():
        return artifacts

    for file_path in sorted(artifacts_dir.rglob("*")):
        if file_path.is_file() and not file_path.name.endswith(".json") and not file_path.name.endswith(".txt"):
            hashes = calculate_hashes(file_path)
            rel_path = str(file_path.relative_to(artifacts_dir)).replace("\\", "/")
            artifacts.append({
                "path": rel_path,
                "filename": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "sha256": hashes["sha256"],
                "sha512": hashes["sha512"],
            })
    return artifacts


def get_timestamp() -> str:
    # Use SOURCE_DATE_EPOCH for reproducible builds if present
    if "SOURCE_DATE_EPOCH" in os.environ:
        try:
            epoch = int(os.environ["SOURCE_DATE_EPOCH"])
            return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc).isoformat()
        except ValueError:
            pass
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def build_manifest(
    repo_root: Path,
    artifacts_dir: Path,
    target_profile: str,
    target_arch: str,
    toolchain: str,
) -> Dict[str, Any]:
    git_meta = get_git_metadata(repo_root)
    artifacts = collect_artifacts(artifacts_dir)

    manifest = {
        "$schema": "https://aegisboot.dev/schema/build-manifest.v1.json",
        "manifest_version": "1.0.0",
        "distribution": "AegisBoot",
        "compilation": {
            "timestamp": get_timestamp(),
            "target_profile": target_profile,
            "target_architecture": target_arch,
            "toolchain": toolchain,
            "host_os": platform.system(),
            "host_release": platform.release(),
            "host_machine": platform.machine(),
            "python_version": platform.python_version(),
        },
        "source": {
            "commit_sha": git_meta["commit_sha"],
            "commit_sha_short": git_meta["commit_sha_short"],
            "branch": git_meta["branch"],
            "is_dirty": git_meta["is_dirty"],
        },
        "artifacts_summary": {
            "count": len(artifacts),
            "total_size_bytes": sum(a["size_bytes"] for a in artifacts),
        },
        "artifacts": artifacts,
    }
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate AegisBoot compilation metadata manifest.")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parent.parent), help="Root directory")
    parser.add_argument("--artifacts-dir", default="Binaries", help="Directory containing compiled artifacts")
    parser.add_argument("--output", default="build-manifest.json", help="Output JSON path")
    parser.add_argument("--target", default=os.getenv("TARGETS", "RELEASE"), help="Target profile (RELEASE, DEBUG, NOOPT)")
    parser.add_argument("--arch", default=os.getenv("ARCHS", "X64"), help="Target architecture (X64, Ia32)")
    parser.add_argument("--toolchain", default=os.getenv("TOOLCHAINS", "CLANGPDB"), help="Toolchain identifier")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    artifacts_dir = Path(args.artifacts_dir)
    if not artifacts_dir.is_absolute():
        artifacts_dir = repo_root / artifacts_dir

    manifest = build_manifest(
        repo_root=repo_root,
        artifacts_dir=artifacts_dir,
        target_profile=args.target,
        target_arch=args.arch,
        toolchain=args.toolchain,
    )

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = repo_root / out_path

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[OK] Generated build manifest: {out_path}")
    print(f"     Target: {args.target} | Arch: {args.arch} | Toolchain: {args.toolchain}")
    print(f"     Artifacts Cataloged: {manifest['artifacts_summary']['count']} ({manifest['artifacts_summary']['total_size_bytes']} bytes)")


if __name__ == "__main__":
    main()
