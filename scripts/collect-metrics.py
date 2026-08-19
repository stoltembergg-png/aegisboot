#!/usr/bin/env python3
"""
AegisBoot — Metrics Collector

Collects structured metrics for external monitoring systems (Prometheus, Datadog, etc.)
Outputs JSON or Prometheus exposition format.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def get_git_info(repo_root: Path) -> dict:
    """Extract git repository metrics."""
    metrics = {}
    
    # Current HEAD
    rc, stdout, _ = run_cmd(["git", "rev-parse", "HEAD"], repo_root)
    if rc == 0:
        metrics["git_head_sha"] = stdout.strip()
        metrics["git_head_short"] = stdout.strip()[:7]
    
    # Upstream HEAD
    rc, stdout, _ = run_cmd(["git", "rev-parse", "upstream/master"], repo_root)
    if rc == 0:
        metrics["upstream_head_sha"] = stdout.strip()
        metrics["upstream_head_short"] = stdout.strip()[:7]
    
    # Behind count
    rc, stdout, _ = run_cmd(["git", "rev-list", "--count", "HEAD..upstream/master"], repo_root)
    if rc == 0:
        metrics["behind_count"] = int(stdout.strip())
    
    # Current tag
    rc, stdout, _ = run_cmd(["git", "describe", "--tags", "--exact-match"], repo_root)
    if rc == 0:
        metrics["current_tag"] = stdout.strip()
    else:
        metrics["current_tag"] = "none"
    
    # Total tags
    rc, stdout, _ = run_cmd(["git", "tag", "-l", "v*-aegis.*"], repo_root)
    if rc == 0:
        metrics["total_releases"] = len(stdout.strip().splitlines()) if stdout.strip() else 0
    
    return metrics


def get_patch_stack_info(repo_root: Path) -> dict:
    """Get patch stack metrics."""
    patches_dir = repo_root / "Patches"
    if not patches_dir.exists():
        return {"patch_count": 0, "patches_valid": 0, "patches_invalid": 0}
    
    patch_files = list(patches_dir.glob("*.patch"))
    valid = 0
    invalid = 0
    
    for patch in patch_files:
        rc, _, _ = run_cmd(["git", "apply", "--stat", str(patch)], repo_root)
        if rc == 0:
            valid += 1
        else:
            invalid += 1
    
    return {
        "patch_count": len(patch_files),
        "patches_valid": valid,
        "patches_invalid": invalid,
    }


def get_build_metrics(repo_root: Path) -> dict:
    """Get build-related metrics."""
    bin_dir = repo_root / "Binaries"
    if not bin_dir.exists():
        return {"binaries_count": 0, "has_checksums": False, "has_sbom": False, "has_provenance": False}
    
    zip_files = list(bin_dir.glob("*.zip"))
    has_sha256 = (bin_dir / "SHA256SUMS.txt").exists()
    has_sha512 = (bin_dir / "SHA512SUMS.txt").exists()
    has_sbom = (bin_dir / "OpenCorePkg-cyclonedx.json").exists()
    has_provenance = (bin_dir / "provenance.json").exists()
    has_version_meta = (bin_dir / "distro-version.json").exists()
    
    return {
        "binaries_count": len(zip_files),
        "has_checksums": has_sha256 and has_sha512,
        "has_sbom": has_sbom,
        "has_provenance": has_provenance,
        "has_version_metadata": has_version_meta,
    }


def get_ci_metrics(repo_root: Path) -> dict:
    """Get CI workflow metrics (requires gh CLI)."""
    metrics = {}
    
    # Check if gh is available
    rc, _, _ = run_cmd(["which", "gh"], repo_root)
    if rc != 0:
        return {"gh_available": False}
    
    # Recent workflow runs (last 24h)
    rc, stdout, _ = run_cmd([
        "gh", "run", "list",
        "--limit", "20",
        "--json", "conclusion,status,name,createdAt"
    ], repo_root)
    
    if rc == 0:
        try:
            runs = json.loads(stdout)
            total = len(runs)
            success = sum(1 for r in runs if r.get("conclusion") == "success")
            failed = sum(1 for r in runs if r.get("conclusion") == "failure")
            in_progress = sum(1 for r in runs if r.get("status") == "in_progress")
            
            metrics["gh_available"] = True
            metrics["recent_runs_total"] = total
            metrics["recent_runs_success"] = success
            metrics["recent_runs_failed"] = failed
            metrics["recent_runs_in_progress"] = in_progress
            metrics["recent_success_rate"] = round(success / total * 100, 2) if total > 0 else 0
        except Exception:
            metrics["gh_available"] = True
            metrics["error"] = "failed_to_parse"
    else:
        metrics["gh_available"] = True
        metrics["error"] = "gh_command_failed"
    
    return metrics


def get_system_metrics() -> dict:
    """Get basic system metrics."""
    import platform
    import shutil
    
    metrics = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
    }
    
    # Disk usage
    try:
        total, used, free = shutil.disk_usage("/")
        metrics["disk_total_gb"] = round(total / (1024**3), 2)
        metrics["disk_used_gb"] = round(used / (1024**3), 2)
        metrics["disk_free_gb"] = round(free / (1024**3), 2)
        metrics["disk_usage_percent"] = round(used / total * 100, 2)
    except Exception:
        pass
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Collect AegisBoot metrics")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parent.parent), help="Repository root")
    parser.add_argument("--format", choices=["json", "prometheus"], default="json", help="Output format")
    parser.add_argument("--output", help="Output file (default: stdout)")
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    
    # Collect all metrics
    all_metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git": get_git_info(repo_root),
        "patches": get_patch_stack_info(repo_root),
        "build": get_build_metrics(repo_root),
        "ci": get_ci_metrics(repo_root),
        "system": get_system_metrics(),
    }
    
    # Output
    if args.format == "json":
        output = json.dumps(all_metrics, indent=2)
    else:
        # Prometheus exposition format
        lines = []
        def flatten(obj, prefix=""):
            for k, v in obj.items():
                key = f"{prefix}{k}".replace(".", "_").replace("-", "_")
                if isinstance(v, dict):
                    flatten(v, f"{key}_")
                elif isinstance(v, bool):
                    lines.append(f"{key} {1 if v else 0}")
                elif isinstance(v, (int, float)):
                    lines.append(f"{key} {v}")
                elif isinstance(v, str):
                    # Escape for prometheus label
                    escaped = v.replace('\\', '\\\\').replace('"', '\\"')
                    lines.append(f'{key} "{escaped}"')
        
        flatten(all_metrics)
        output = "\n".join(lines)
    
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"[OK] Metrics written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()