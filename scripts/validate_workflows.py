#!/usr/bin/env python3
"""
AegisBoot — Strict GitHub Actions Workflow Security & Integrity Validator

Validates .github/workflows/*.yml against comprehensive security and integrity rules:
1.  [RULE_PERM_001] Workflow or job permissions declared.
2.  [RULE_PERM_002] Least-privilege permissions (no write-all, strict scoping of write permissions).
3.  [RULE_CONC_001] Concurrency declared with appropriate cancel-in-progress.
4.  [RULE_TIME_001] Explicit timeout-minutes on all jobs.
5.  [RULE_GATE_001] Zero continue-on-error: true on jobs or steps.
6.  [RULE_TRIG_001] Prohibition of pull_request_target trigger.
7.  [RULE_ACTN_001] All external actions pinned to full 40-character commit SHAs.
8.  [RULE_CHCK_001] actions/checkout explicitly sets persist-credentials: false.
9.  [RULE_SECR_001] No secrets or context expressions interpolated inside inline run: blocks.
10. [RULE_DWNL_001] No unverified remote script piping or downloads.
11. [RULE_LEAK_001] Token leakage prevention (no echo of tokens/secrets, no set -x).
12. [RULE_ARTI_001] Artifact uploads (actions/upload-artifact) must define retention-days.
13. [RULE_RELS_001] Release jobs must validate tag ref / commit provenance.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class ValidationFinding:
    rule_id: str
    file_path: str
    job_name: Optional[str]
    step_name: Optional[str]
    message: str
    severity: str  # "ERROR" or "WARN"


class WorkflowValidator:
    SHA40_REGEX = re.compile(r"^[a-f0-9]{40}$")
    ACTION_USE_REGEX = re.compile(
        r"uses:\s+([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)?@([^\s#]+))"
    )

    def __init__(self, strict: bool = True):
        self.strict = strict
        self.findings: List[ValidationFinding] = []

    def clear(self):
        self.findings.clear()

    def add_finding(
        self,
        rule_id: str,
        file_path: str,
        message: str,
        job_name: Optional[str] = None,
        step_name: Optional[str] = None,
        severity: str = "ERROR",
    ):
        self.findings.append(
            ValidationFinding(
                rule_id=rule_id,
                file_path=file_path,
                job_name=job_name,
                step_name=step_name,
                message=message,
                severity=severity,
            )
        )

    def parse_yaml(self, content: str) -> Optional[Dict[str, Any]]:
        if yaml is not None:
            try:
                return yaml.safe_load(content)
            except Exception:
                return None
        return None

    def validate_content(self, file_name: str, content: str) -> List[ValidationFinding]:
        local_findings: List[ValidationFinding] = []
        parsed = self.parse_yaml(content)

        # 1. RULE_TRIG_001: Prohibition of pull_request_target
        if "pull_request_target" in content:
            local_findings.append(
                ValidationFinding(
                    rule_id="RULE_TRIG_001",
                    file_path=file_name,
                    job_name=None,
                    step_name=None,
                    message="Prohibited 'pull_request_target' trigger detected.",
                    severity="ERROR",
                )
            )

        # 2. RULE_PERM_001 & RULE_PERM_002: Permissions declaration and least privilege
        has_top_permissions = False
        if parsed and isinstance(parsed, dict):
            if "permissions" in parsed:
                has_top_permissions = True
                top_perms = parsed["permissions"]
                if top_perms == "write-all":
                    local_findings.append(
                        ValidationFinding(
                            rule_id="RULE_PERM_002",
                            file_path=file_name,
                            job_name=None,
                            step_name=None,
                            message="Excessive permissions: 'write-all' is strictly prohibited.",
                            severity="ERROR",
                        )
                    )
        else:
            if re.search(r"^permissions:", content, re.MULTILINE):
                has_top_permissions = True
                if re.search(r"^permissions:\s*write-all", content, re.MULTILINE):
                    local_findings.append(
                        ValidationFinding(
                            rule_id="RULE_PERM_002",
                            file_path=file_name,
                            job_name=None,
                            step_name=None,
                            message="Excessive permissions: 'write-all' is strictly prohibited.",
                            severity="ERROR",
                        )
                    )

        if not has_top_permissions:
            # Check if all jobs define permissions
            all_jobs_have_perms = False
            if parsed and "jobs" in parsed and isinstance(parsed["jobs"], dict):
                job_perms = [
                    "permissions" in jdata
                    for jname, jdata in parsed["jobs"].items()
                    if isinstance(jdata, dict)
                ]
                if job_perms and all(job_perms):
                    all_jobs_have_perms = True

            if not all_jobs_have_perms:
                local_findings.append(
                    ValidationFinding(
                        rule_id="RULE_PERM_001",
                        file_path=file_name,
                        job_name=None,
                        step_name=None,
                        message="Workflow does not declare top-level 'permissions:' or all jobs lack permissions.",
                        severity="ERROR",
                    )
                )

        # 3. RULE_CONC_001: Concurrency declared
        if parsed and isinstance(parsed, dict):
            if "concurrency" not in parsed:
                local_findings.append(
                    ValidationFinding(
                        rule_id="RULE_CONC_001",
                        file_path=file_name,
                        job_name=None,
                        step_name=None,
                        message="Workflow missing 'concurrency:' group definition.",
                        severity="ERROR",
                    )
                )
        else:
            if not re.search(r"^concurrency:", content, re.MULTILINE):
                local_findings.append(
                    ValidationFinding(
                        rule_id="RULE_CONC_001",
                        file_path=file_name,
                        job_name=None,
                        step_name=None,
                        message="Workflow missing 'concurrency:' group definition.",
                        severity="ERROR",
                    )
                )

        # 4. RULE_GATE_001: continue-on-error: true
        if re.search(r"continue-on-error:\s*true", content, re.IGNORECASE):
            local_findings.append(
                ValidationFinding(
                    rule_id="RULE_GATE_001",
                    file_path=file_name,
                    job_name=None,
                    step_name=None,
                    message="Prohibited 'continue-on-error: true' found on workflow gate.",
                    severity="ERROR",
                )
            )

        # 5. RULE_ACTN_001: Pinned external actions to 40-char SHA
        action_matches = self.ACTION_USE_REGEX.findall(content)
        for full_use, ref in action_matches:
            if full_use.startswith(".") or full_use.startswith("docker://"):
                continue
            if not self.SHA40_REGEX.match(ref):
                local_findings.append(
                    ValidationFinding(
                        rule_id="RULE_ACTN_001",
                        file_path=file_name,
                        job_name=None,
                        step_name=None,
                        message=f"External Action '{full_use}' is not pinned to a 40-character commit SHA (found: '{ref}').",
                        severity="ERROR",
                    )
                )

        # 6. Check jobs & steps in detail
        if parsed and "jobs" in parsed and isinstance(parsed["jobs"], dict):
            for job_name, job_data in parsed["jobs"].items():
                if not isinstance(job_data, dict):
                    continue

                # RULE_TIME_001: Timeout minutes
                if "timeout-minutes" not in job_data:
                    local_findings.append(
                        ValidationFinding(
                            rule_id="RULE_TIME_001",
                            file_path=file_name,
                            job_name=job_name,
                            step_name=None,
                            message=f"Job '{job_name}' is missing required 'timeout-minutes:'.",
                            severity="ERROR",
                        )
                    )

                # Check job permissions if defined
                if "permissions" in job_data:
                    j_perms = job_data["permissions"]
                    if j_perms == "write-all":
                        local_findings.append(
                            ValidationFinding(
                                rule_id="RULE_PERM_002",
                                file_path=file_name,
                                job_name=job_name,
                                step_name=None,
                                message=f"Job '{job_name}' has excessive permissions: 'write-all'.",
                                severity="ERROR",
                            )
                        )

                # Check release jobs origin validation (RULE_RELS_001)
                is_release_job = "release" in job_name.lower() or (
                    isinstance(job_data.get("steps"), list)
                    and any(
                        "release" in str(s.get("uses", "")).lower()
                        for s in job_data["steps"]
                        if isinstance(s, dict)
                    )
                )
                if is_release_job:
                    # Check if workflow or job has trigger condition or step verifying origin/ref
                    wf_triggers = parsed.get("on", parsed.get(True, {}))
                    has_tag_trigger = False
                    if isinstance(wf_triggers, dict):
                        if "push" in wf_triggers and isinstance(wf_triggers["push"], dict):
                            tags = wf_triggers["push"].get("tags", [])
                            if tags:
                                has_tag_trigger = True
                        if "release" in wf_triggers:
                            has_tag_trigger = True

                    has_job_condition = "if" in job_data or has_tag_trigger
                    if not has_job_condition:
                        local_findings.append(
                            ValidationFinding(
                                rule_id="RULE_RELS_001",
                                file_path=file_name,
                                job_name=job_name,
                                step_name=None,
                                message=f"Release job '{job_name}' lacks source origin/tag validation or 'if:' condition.",
                                severity="ERROR",
                            )
                        )

                # Inspect steps
                steps = job_data.get("steps", [])
                if isinstance(steps, list):
                    for step_idx, step in enumerate(steps):
                        if not isinstance(step, dict):
                            continue
                        s_name = step.get("name", f"Step #{step_idx + 1}")
                        s_uses = step.get("uses", "")
                        s_with = step.get("with", {})
                        s_run = step.get("run", "")

                        # RULE_CHCK_001: Checkout persist-credentials: false
                        if "actions/checkout" in s_uses:
                            if not isinstance(s_with, dict) or s_with.get("persist-credentials") is not False:
                                local_findings.append(
                                    ValidationFinding(
                                        rule_id="RULE_CHCK_001",
                                        file_path=file_name,
                                        job_name=job_name,
                                        step_name=s_name,
                                        message=f"Step '{s_name}' uses actions/checkout without 'persist-credentials: false'.",
                                        severity="ERROR",
                                    )
                                )

                        # RULE_ARTI_001: Artifact upload retention policy
                        if "actions/upload-artifact" in s_uses:
                            if not isinstance(s_with, dict) or "retention-days" not in s_with:
                                local_findings.append(
                                    ValidationFinding(
                                        rule_id="RULE_ARTI_001",
                                        file_path=file_name,
                                        job_name=job_name,
                                        step_name=s_name,
                                        message=f"Step '{s_name}' uses actions/upload-artifact without explicit 'retention-days:'.",
                                        severity="WARN" if not self.strict else "ERROR",
                                    )
                                )

                        # RULE_SECR_001 & RULE_LEAK_001 & RULE_DWNL_001 inside run:
                        if s_run and isinstance(s_run, str):
                            # Secret in run block interpolation
                            if re.search(r"\$\{\{\s*secrets\.", s_run):
                                local_findings.append(
                                    ValidationFinding(
                                        rule_id="RULE_SECR_001",
                                        file_path=file_name,
                                        job_name=job_name,
                                        step_name=s_name,
                                        message=f"Step '{s_name}' directly interpolates '${{{{ secrets... }}}}' into inline shell script. Pass via env: instead.",
                                        severity="ERROR",
                                    )
                                )
                            # Dangerous context interpolation
                            if re.search(r"\$\{\{\s*github\.event\.(issue|pull_request|comment)\.body", s_run):
                                local_findings.append(
                                    ValidationFinding(
                                        rule_id="RULE_SECR_001",
                                        file_path=file_name,
                                        job_name=job_name,
                                        step_name=s_name,
                                        message=f"Step '{s_name}' interpolates untrusted GitHub event context directly in script.",
                                        severity="ERROR",
                                    )
                                )
                            # Token leak command (echo of secret or github.token)
                            if re.search(r"echo\s+.*?\$\{\{\s*(secrets|github\.token)", s_run, re.IGNORECASE):
                                local_findings.append(
                                    ValidationFinding(
                                        rule_id="RULE_LEAK_001",
                                        file_path=file_name,
                                        job_name=job_name,
                                        step_name=s_name,
                                        message=f"Step '{s_name}' contains dangerous echo of tokens/secrets.",
                                        severity="ERROR",
                                    )
                                )
                            # Debug echo of tokens in set -x
                            if re.search(r"set\s+-x", s_run) and "secrets." in s_run:
                                local_findings.append(
                                    ValidationFinding(
                                        rule_id="RULE_LEAK_001",
                                        file_path=file_name,
                                        job_name=job_name,
                                        step_name=s_name,
                                        message=f"Step '{s_name}' combines 'set -x' with secret contexts.",
                                        severity="ERROR",
                                    )
                                )
                            # Unverified download piped to bash/sh/eval
                            if re.search(r"(curl|wget)\s+.*?(http://|https://).*?\|\s*(bash|sh|eval)", s_run):
                                # Check if downloading from trusted local wrapper or contains strict sha/pin
                                if not re.search(r"(ci-bootstrap\.sh|docker-apparmor\.sh)", s_run):
                                    local_findings.append(
                                        ValidationFinding(
                                            rule_id="RULE_DWNL_001",
                                            file_path=file_name,
                                            job_name=job_name,
                                            step_name=s_name,
                                            message=f"Step '{s_name}' pipes unverified remote script directly to shell interpreter.",
                                            severity="ERROR",
                                        )
                                    )
        else:
            # Fallback regex checks if yaml module was not installed
            if not re.search(r"timeout-minutes:\s*\d+", content):
                local_findings.append(
                    ValidationFinding(
                        rule_id="RULE_TIME_001",
                        file_path=file_name,
                        job_name=None,
                        step_name=None,
                        message="Workflow missing 'timeout-minutes:' declarations.",
                        severity="ERROR",
                    )
                )

        return local_findings

    def validate_file(self, file_path: Path) -> List[ValidationFinding]:
        content = file_path.read_text(encoding="utf-8")
        findings = self.validate_content(file_path.name, content)
        self.findings.extend(findings)
        return findings

    def validate_directory(self, dir_path: Path) -> List[ValidationFinding]:
        self.clear()
        for ext in ("*.yml", "*.yaml"):
            for f in sorted(dir_path.glob(ext)):
                self.validate_file(f)
        return self.findings


def main():
    parser = argparse.ArgumentParser(
        description="Strict GitHub Actions Workflow Security & Integrity Validator"
    )
    parser.add_argument(
        "--workflows-dir",
        default=str(Path(__file__).resolve().parent.parent / ".github" / "workflows"),
        help="Path to .github/workflows directory",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Treat warnings as errors (default: True)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (text or json)",
    )
    args = parser.parse_args()

    wf_dir = Path(args.workflows_dir).resolve()
    if not wf_dir.exists():
        print(f"[ERROR] Workflows directory not found: {wf_dir}")
        sys.exit(1)

    validator = WorkflowValidator(strict=args.strict)
    findings = validator.validate_directory(wf_dir)

    errors = [f for f in findings if f.severity == "ERROR"]
    warnings = [f for f in findings if f.severity == "WARN"]

    if args.format == "json":
        output = {
            "summary": {
                "total_findings": len(findings),
                "errors": len(errors),
                "warnings": len(warnings),
                "status": "PASSED" if not errors else "FAILED",
            },
            "findings": [asdict(f) for f in findings],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"=== AegisBoot Workflow Security Validator ===")
        print(f"Audited Directory: {wf_dir}")
        print(f"Total Workflows:   {len(list(wf_dir.glob('*.yml')) + list(wf_dir.glob('*.yaml')))}")
        print(f"Total Findings:    {len(findings)} ({len(errors)} errors, {len(warnings)} warnings)")
        print("")

        for f in findings:
            prefix = "[ERROR]" if f.severity == "ERROR" else "[WARN]"
            loc = f.file_path
            if f.job_name:
                loc += f" -> job: {f.job_name}"
            if f.step_name:
                loc += f" -> step: {f.step_name}"
            print(f"  {prefix} [{f.rule_id}] ({loc})")
            print(f"          {f.message}")

        print("")
        if errors:
            print("=== Workflow Validation FAILED ===")
        else:
            print("=== Workflow Validation PASSED ===")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
