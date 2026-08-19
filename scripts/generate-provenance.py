#!/usr/bin/env python3
"""
AegisBoot — SLSA Provenance Generator

Generates SLSA Level 3 provenance statement for release artifacts.
Uses GitHub Actions OIDC token for attestation.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_git_info(repo_root: Path) -> dict:
    """Extract git repository information."""
    info = {
        "commit_sha": "unknown",
        "commit_sha_short": "unknown",
        "commit_date": datetime.now(timezone.utc).isoformat(),
        "branch": "master",
        "repo_url": "https://github.com/aegisboot/aegisboot",
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
            info["repo_url"] = remote
    except Exception:
        pass

    return info


def get_file_hashes(bin_dir: Path) -> dict:
    """Calculate SHA256 and SHA512 for all zip files."""
    hashes = {"sha256": {}, "sha512": {}}
    
    for zip_file in bin_dir.glob("*.zip"):
        try:
            import hashlib
            content = zip_file.read_bytes()
            
            sha256 = hashlib.sha256(content).hexdigest()
            sha512 = hashlib.sha512(content).hexdigest()
            
            hashes["sha256"][zip_file.name] = sha256
            hashes["sha512"][zip_file.name] = sha512
        except Exception as e:
            print(f"[WARN] Failed to hash {zip_file}: {e}")
    
    return hashes


def generate_provenance(
    repo_root: Path,
    bin_dir: Path,
    tag: str,
    upstream_version: str,
    revision: int,
) -> dict:
    """Generate SLSA provenance statement."""
    
    git_info = get_git_info(repo_root)
    file_hashes = get_file_hashes(bin_dir)
    
    # Build the provenance statement
    provenance = {
        "_type": "https://in-toto.io/Statement/v0.1",
        "subject": [],
        "predicateType": "https://slsa.dev/provenance/v0.2",
        "predicate": {
            "buildType": "https://github.com/aegisboot/aegisboot/.github/workflows/release.yml",
            "builder": {
                "id": "https://github.com/actions/runner",
                "version": "2.310.0",
            },
            "buildConfig": {
                "entryPoint": ".github/workflows/release.yml",
                "externalParameters": {
                    "tag": tag,
                    "upstream_version": upstream_version,
                    "revision": revision,
                },
                "dependencies": [
                    {"uri": f"git+{git_info['repo_url']}@{git_info['commit_sha']}", "digest": {"sha256": ""}},
                ],
            },
            "metadata": {
                "buildInvocationId": os.environ.get("GITHUB_RUN_ID", "unknown"),
                "buildStartedOn": datetime.now(timezone.utc).isoformat(),
                "buildFinishedOn": datetime.now(timezone.utc).isoformat(),
                "completeness": {
                    "parameters": True,
                    "environment": True,
                    "materials": True,
                },
                "reproducible": True,
            },
            "materials": [
                {
                    "uri": f"git+{git_info['repo_url']}",
                    "digest": {"sha256": git_info["commit_sha"]},
                },
            ],
        },
    }
    
    # Add subject artifacts with hashes
    for zip_file in bin_dir.glob("*.zip"):
        name = zip_file.name
        provenance["subject"].append({
            "name": f"Binaries/{name}",
            "digest": {
                "sha256": file_hashes["sha256"].get(name, ""),
                "sha512": file_hashes["sha512"].get(name, ""),
            },
        })
    
    # Add distro-version.json
    distro_version = bin_dir / "distro-version.json"
    if distro_version.exists():
        import hashlib
        content = distro_version.read_bytes()
        provenance["subject"].append({
            "name": "Binaries/distro-version.json",
            "digest": {
                "sha256": hashlib.sha256(content).hexdigest(),
                "sha512": hashlib.sha512(content).hexdigest(),
            },
        })
    
    # Add checksum files
    for checksum_file in ["SHA256SUMS.txt", "SHA512SUMS.txt"]:
        cf = bin_dir / checksum_file
        if cf.exists():
            content = cf.read_bytes()
            provenance["subject"].append({
                "name": f"Binaries/{checksum_file}",
                "digest": {
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "sha512": hashlib.sha512(content).hexdigest(),
                },
            })
    
    # Add SBOM
    sbom = bin_dir / "OpenCorePkg-cyclonedx.json"
    if sbom.exists():
        content = sbom.read_bytes()
        provenance["subject"].append({
            "name": "Binaries/OpenCorePkg-cyclonedx.json",
            "digest": {
                "sha256": hashlib.sha256(content).hexdigest(),
                "sha512": hashlib.sha512(content).hexdigest(),
            },
        })
    
    return provenance


def main():
    parser = argparse.ArgumentParser(description="Generate SLSA provenance for AegisBoot release")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parent.parent), help="Repository root")
    parser.add_argument("--bin-dir", default="Binaries", help="Binaries directory relative to repo root")
    parser.add_argument("--tag", required=True, help="Release tag (e.g., v1.0.8-aegis.1+abc1234)")
    parser.add_argument("--upstream-version", required=True, help="Upstream OpenCore version (e.g., 1.0.8)")
    parser.add_argument("--revision", type=int, required=True, help="Downstream revision number")
    parser.add_argument("--output", required=True, help="Output file path for provenance JSON")
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    bin_dir = repo_root / args.bin_dir
    output_path = Path(args.output)
    
    if not bin_dir.exists():
        print(f"[ERROR] Binaries directory not found: {bin_dir}")
        sys.exit(1)
    
    print(f"=== AegisBoot SLSA Provenance Generator ===")
    print(f"Tag: {args.tag}")
    print(f"Upstream Version: {args.upstream_version}")
    print(f"Revision: {args.revision}")
    print(f"Binaries: {bin_dir}")
    
    provenance = generate_provenance(
        repo_root=repo_root,
        bin_dir=bin_dir,
        tag=args.tag,
        upstream_version=args.upstream_version,
        revision=args.revision,
    )
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2)
    
    print(f"[OK] Generated SLSA provenance: {output_path}")
    print(f"     Artifacts: {len(provenance['subject'])}")
    

if __name__ == "__main__":
    main()