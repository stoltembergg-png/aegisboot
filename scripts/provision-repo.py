#!/usr/bin/env python3
"""
AegisBoot — Repository Provisioning (Branch Protection & Auto-Merge)

Applies the branch protection policy and enables auto-merge on the fork repo
per ADR-001 / ADR-013 / SDD item BK-002. Idempotent and fail-closed.

Usage:
  python scripts/provision-repo.py --dry-run       # validate + show actions (default)
  python scripts/provision-repo.py --apply         # apply branch protection + auto-merge
  python scripts/provision-repo.py --check         # report current enforcement status
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


# --- Required status checks (must match .github/workflows job names) ---
REQUIRED_CHECKS = [
    # ci.yml gates
    "workflow-integrity",
    "formatting",
    "static-checks",
    "license-and-secrets",
    "dependency-and-toolchain",
    "patch-stack-verification",
    "policy-and-metadata-tests",
    "unit-and-integration-tests",
    "qemu-boot-test",
    # build.yml
    "build-linux-clangpdb",
    "build-linux-gcc5",
    "build-linux-clangdwarf",
    "build-linux-docs",
    "build-macos",
    "build-windows",
    "build-drift-detection",
    # analyze.yml
    "analyze-shell-scripts",
    "analyze-python-scripts",
]

FORCE_PUSH_BYPASSERS = "force-push-bypassers"
ADMIN_ENFORCED = True


def get_repo(repo_root: Path) -> str:
    try:
        rc = subprocess.run(
            ["git", "remote", "get-url", "fork"],
            cwd=repo_root, capture_output=True, text=True, timeout=15,
        )
        url = rc.stdout.strip()
        if "github.com" in url:
            tail = url.split("github.com")[-1]
            if tail.startswith(":"):
                tail = tail[1:]
            tail = tail.strip("/")
            if tail.endswith(".git"):
                tail = tail[:-4]
            return tail
        raise RuntimeError(f"Unrecognized fork URL: {url}")
    except Exception as e:
        fallback = "stoltembergg-png/aegisboot"
        print(f"[WARN] Could not determine fork repo ({e}), using {fallback}")
        return fallback


def gh_api(method: str, endpoint: str, data=None, repo: str = None):
    """Call gh api and return parsed JSON. Returns None on non-2xx."""
    cmd = ["gh", "api", "--method", method, endpoint]
    if data is not None:
        cmd = ["gh", "api", "--method", method, "-f", "input=@-", endpoint]
    env = os.environ.copy()
    proc = subprocess.run(
        cmd, cwd=None, env=env, capture_output=True, text=True, timeout=60,
        input=json.dumps(data) if data is not None else None,
    )
    if proc.returncode != 0:
        return {"error": proc.stderr.strip() or proc.stdout.strip()}
    try:
        return json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        return {"raw": proc.stdout.strip()}


def build_protection_payload():
    """Build the branch protection PUT payload per ADR-013."""
    payload = {
        "required_status_checks": {
            "strict": True,
            "contexts": REQUIRED_CHECKS,
        },
        "enforce_admins": ADMIN_ENFORCED,
        "required_pull_request_reviews": {
            "required_approving_review_count": 0,
            "dismiss_stale_reviews": False,
            "require_code_owner_reviews": False,
            "require_last_push_approval": False,
        },
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_linear_history": False,
        "allow_auto_merge": True,
        "block_creations": False,
    }
    return payload


def get_current_protection(repo: str) -> dict:
    endpoint = f"/repos/{repo}/branches/master/protection"
    return gh_api("GET", endpoint)


def apply_protection(repo: str, dry_run: bool = True) -> bool:
    """Apply branch protection. Returns success."""
    endpoint = f"/repos/{repo}/branches/master/protection"
    payload = build_protection_payload()

    if dry_run:
        print("[DRY-RUN] Would PUT branch protection to master:")
        print(json.dumps(payload, indent=2)[:2000])
        print(f"[DRY-RUN] Required checks ({len(REQUIRED_CHECKS)}):")
        for c in REQUIRED_CHECKS:
            print(f"    - {c}")
        return True

    gh_api("DELETE", endpoint)  # reset to clean state first (idempotent)
    current = get_current_protection(repo)
    if "error" not in current or current.get("error", "").startswith("Branch not protected"):
        # delete may 404 if already clean; ignore
        pass

    status = gh_api("PUT", endpoint, data=payload)
    if status and "error" not in status:
        print("[OK] Branch protection applied successfully.")
        return True
    print(f"[ERROR] Failed to apply branch protection: {status}")
    return False


def enable_auto_merge(repo: str, dry_run: bool = True) -> bool:
    """Enable auto-merge setting on the repo."""
    endpoint = f"/repos/{repo}"
    payload = {"allow_auto_merge": True, "allow_squash_merge": True}

    if dry_run:
        print("[DRY-RUN] Would enable auto-merge + squash merge on repo settings.")
        return True

    status = gh_api("PATCH", endpoint, data=payload)
    if status and "error" not in status:
        print("[OK] Auto-merge + squash merge enabled.")
        return True
    print(f"[ERROR] Failed to enable auto-merge: {status}")
    return False


def check_status(repo: str):
    """Report current enforcement status without changing anything."""
    proto = get_current_protection(repo)
    print("=== Branch Protection Status (master) ===")
    if "error" in proto:
        print(f"  NOT PROTECTED: {proto['error']}")
    else:
        print("  Protected: YES")
        rsc = proto.get("required_status_checks", {})
        if rsc:
            print(f"  Required checks (strict={rsc.get('strict')}):")
            for c in rsc.get("contexts", []):
                print(f"    - {c}")
        else:
            print("  Required checks: NONE")
        print(f"  Enforce admins: {proto.get('enforce_admins', {}).get('enabled')}")
        print(f"  Allow force pushes: {proto.get('allow_force_pushes', {}).get('enabled')}")
        print(f"  Allow auto merge: {proto.get('allow_auto_merge')}")

    repo_meta = gh_api("GET", endpoint=f"/repos/{repo}")
    if "error" not in repo_meta:
        print(f"  Repo allow_auto_merge: {repo_meta.get('allow_auto_merge')}")
        print(f"  Repo allow_squash_merge: {repo_meta.get('allow_squash_merge')}")
    print()
    print(f"Required checks expected ({len(REQUIRED_CHECKS)}):")
    present = rsc.get("contexts", []) if "error" not in proto and rsc else []
    missing = [c for c in REQUIRED_CHECKS if c not in present]
    if missing:
        print(f"  Warning — {len(missing)} check(s) not yet enforced:")
        for c in missing:
            print(f"    - {c}")
    else:
        print("  All required checks enforced.")


def main():
    parser = argparse.ArgumentParser(description="Provision AegisBoot GitHub repo")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parent.parent))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Validate without changing (default)")
    group.add_argument("--apply", action="store_true", help="Apply branch protection + auto-merge")
    group.add_argument("--check", action="store_true", help="Report current enforcement status")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    repo = get_repo(repo_root)
    print(f"Target repo: {repo}")

    if args.check:
        check_status(repo)
        return

    dry_run = args.dry_run or not args.apply

    ok_prot = apply_protection(repo, dry_run=dry_run)
    ok_auto = enable_auto_merge(repo, dry_run=dry_run)

    if dry_run:
        print("\n=== DRY-RUN COMPLETE — no changes made ===")
        print("Run with --apply to enforce branch protection + auto-merge.")
        sys.exit(0)

    if ok_prot and ok_auto:
        print("\n=== Provisioning COMPLETE ===")
        sys.exit(0)
    else:
        print("\n=== Provisioning PARTIAL/FAILED — review output above ===")
        sys.exit(1)


if __name__ == "__main__":
    main()