#!/usr/bin/env python3
"""
AegisBoot — GitHub Milestone Manager

Creates and manages milestones via GitHub API for:
- Upstream Sync Cycles (cycle-<version>)
- Downstream Rollups (distro-v<ver>-aegis.<rev>)
- Emergency Hotfixes (hotfix-<cve_or_issue>)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def get_repo_info(repo_root: Path) -> tuple[str, str]:
    """Get owner/repo from git remote."""
    rc, stdout, _ = run_cmd(["git", "remote", "get-url", "fork"], repo_root)
    if rc != 0:
        return "", ""
    url = stdout.strip()
    # Parse https://github.com/owner/repo.git or git@github.com:owner/repo.git
    if "github.com" in url:
        parts = url.split("github.com")[-1].lstrip("/:").rstrip(".git")
        return tuple(parts.split("/")[:2])
    return "", ""


def get_gh_token() -> str:
    """Get GitHub token from environment."""
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""


def api_request(method: str, endpoint: str, data: dict = None) -> tuple[int, dict]:
    """Make GitHub API request."""
    token = get_gh_token()
    if not token:
        return -1, {"error": "No GH_TOKEN"}

    import urllib.request
    import urllib.error

    url = f"https://api.github.com{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }

    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return -1, {"error": str(e)}


def create_milestone(owner: str, repo: str, title: str, description: str, due_on: str = None) -> dict:
    """Create a milestone."""
    data = {"title": title, "description": description}
    if due_on:
        data["due_on"] = due_on
    return api_request("POST", f"/repos/{owner}/{repo}/milestones", data)


def list_milestones(owner: str, repo: str, state: str = "open") -> list:
    """List milestones."""
    code, resp = api_request("GET", f"/repos/{owner}/{repo}/milestones?state={state}&per_page=100")
    if code == 200:
        return resp
    return []


def get_milestone_number(owner: str, repo: str, title: str) -> int | None:
    """Get milestone number by title."""
    milestones = list_milestones(owner, repo, "all")
    for m in milestones:
        if m["title"] == title:
            return m["number"]
    return None


def update_milestone(owner: str, repo: str, number: int, state: str = None, description: str = None) -> dict:
    """Update milestone state."""
    data = {}
    if state:
        data["state"] = state
    if description:
        data["description"] = description
    return api_request("PATCH", f"/repos/{owner}/{repo}/milestones/{number}", data)


def extract_opencore_version(repo_root: Path) -> str:
    """Extract OpenCore version from OcMainLib.h."""
    header = repo_root / "Include" / "Acidanthera" / "Library" / "OcMainLib.h"
    if header.exists():
        import re
        content = header.read_text()
        match = re.search(r'#define\s+OPEN_CORE_VERSION\s+"([^"]+)"', content)
        if match:
            return match.group(1)
    return "1.0.8"


def create_sync_cycle_milestone(owner: str, repo: str, upstream_version: str) -> dict:
    """Create upstream sync cycle milestone."""
    title = f"cycle-{upstream_version}"
    description = f"""## Upstream Sync Cycle: {upstream_version}

Tracks continuous integration of upstream OpenCorePkg `{upstream_version}` commits.

**Scope:**
- Automated 15-min sync from `acidanthera/OpenCorePkg` master
- Patch stack validation on each sync
- Impact classification of upstream changes
- Automated release triggers for qualified merges

**Completion Criteria:**
- [ ] All upstream commits up to target release integrated
- [ ] Patch stack rebased and validated
- [ ] All CI gates passing for sync PRs
- [ ] Downstream releases generated as warranted

**Related:** [Distribution Release Policy](docs/release-policy.md)
"""
    due = (datetime.now() + timedelta(days=90)).isoformat() + "Z"
    return create_milestone(owner, repo, title, description, due)


def create_distro_milestone(owner: str, repo: str, upstream_version: str, distro_revision: int) -> dict:
    """Create downstream rollup milestone."""
    title = f"distro-v{upstream_version}-aegis.{distro_revision}"
    description = f"""## Downstream Rollup: v{upstream_version}-aegis.{distro_revision}

Tracks downstream CI/CD features, security hardening, and tooling for OpenCore {upstream_version}.

**Scope:**
- Local patch stack maintenance
- CI/CD pipeline improvements
- Toolchain updates
- Security hardening
- Documentation updates

**Target Release:** `v{upstream_version}-aegis.{distro_revision}+<sha>`

**Completion Criteria:**
- [ ] All CI/CD features implemented and tested
- [ ] Patch stack validated against upstream
- [ ] SBOM and provenance generation working
- [ ] Release artifacts generated and verified

**Related:** [Release Policy](docs/release-policy.md)
"""
    due = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
    return create_milestone(owner, repo, title, description, due)


def create_hotfix_milestone(owner: str, repo: str, identifier: str) -> dict:
    """Create emergency hotfix milestone."""
    title = f"hotfix-{identifier}"
    description = f"""## Emergency Hotfix: {identifier}

Time-bounded milestone (< 24h SLA) for urgent CVE fix or critical boot regression.

**Scope:**
- Minimal patch to address {identifier}
- Fast-track PR with `impact:critical` label
- Automated release after merge

**SLA:** < 24 hours from creation to release

**Completion Criteria:**
- [ ] Patch created and validated
- [ ] PR passes all CI gates
- [ ] Release generated and published
- [ ] Post-mortem documented

**Related:** [Incident Response](docs/adr/adr-011-incident-response.md)
"""
    due = (datetime.now() + timedelta(hours=24)).isoformat() + "Z"
    return create_milestone(owner, repo, title, description, due)


def main():
    parser = argparse.ArgumentParser(description="Manage GitHub milestones for AegisBoot")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parent.parent))
    subparsers = parser.add_subparsers(dest="command", required=True)

    # sync-cycle
    sp = subparsers.add_parser("sync-cycle", help="Create upstream sync cycle milestone")
    sp.add_argument("--version", required=True, help="Upstream version (e.g., 1.0.8)")

    # distro
    sp = subparsers.add_parser("distro", help="Create downstream rollup milestone")
    sp.add_argument("--version", required=True, help="Upstream version")
    sp.add_argument("--revision", type=int, required=True, help="Distro revision")

    # hotfix
    sp = subparsers.add_parser("hotfix", help="Create emergency hotfix milestone")
    sp.add_argument("--id", required=True, help="CVE ID or issue identifier")

    # list
    subparsers.add_parser("list", help="List existing milestones")

    # close
    sp = subparsers.add_parser("close", help="Close a milestone")
    sp.add_argument("--title", required=True, help="Milestone title")

    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    owner, repo = get_repo_info(repo_root)
    if not owner or not repo:
        print("[ERROR] Could not determine fork remote (owner/repo)")
        sys.exit(1)

    print(f"[INFO] Target repo: {owner}/{repo}")

    if args.command == "sync-cycle":
        result = create_sync_cycle_milestone(owner, repo, args.version)
    elif args.command == "distro":
        result = create_distro_milestone(owner, repo, args.version, args.revision)
    elif args.command == "hotfix":
        result = create_hotfix_milestone(owner, repo, args.id)
    elif args.command == "list":
        milestones = list_milestones(owner, repo, "all")
        for m in milestones:
            print(f"  #{m['number']} {m['title']} [{m['state']}]")
        return
    elif args.command == "close":
        num = get_milestone_number(owner, repo, args.title)
        if num:
            result = update_milestone(owner, repo, num, state="closed")
        else:
            print(f"[ERROR] Milestone not found: {args.title}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    if "result" in locals():
        if isinstance(result, dict) and "number" in result:
            print(f"[OK] Milestone created: #{result['number']} {result['title']}")
        elif isinstance(result, dict) and "error" in result:
            print(f"[ERROR] {result['error']}")
            sys.exit(1)
        else:
            print(f"[OK] Operation completed: {result}")


if __name__ == "__main__":
    main()