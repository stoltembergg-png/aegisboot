#!/usr/bin/env python3
"""
AegisBoot — Build Comparison & Reproducibility Verification Engine
"""

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FileDiffResult:
    relative_path: str
    status: str  # "MATCH", "HASH_MISMATCH", "SIZE_MISMATCH", "MISSING_IN_A", "MISSING_IN_B"
    size_a: Optional[int]
    size_b: Optional[int]
    sha256_a: Optional[str]
    sha256_b: Optional[str]
    drift_details: Optional[str] = None


def hash_file(file_path: Path) -> Dict[str, str]:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return {"sha256": sha256.hexdigest(), "size": file_path.stat().st_size}


def scan_dir(dir_path: Path) -> Dict[str, Dict[str, Any]]:
    files = {}
    if not dir_path.exists():
        return files

    for file_path in sorted(dir_path.rglob("*")):
        if file_path.is_file() and not file_path.name.endswith(".json") and not file_path.name.endswith(".txt"):
            rel_path = str(file_path.relative_to(dir_path)).replace("\\", "/")
            file_meta = hash_file(file_path)
            files[rel_path] = {
                "path": rel_path,
                "size": file_meta["size"],
                "sha256": file_meta["sha256"],
            }
    return files


def load_manifest_or_dir(target_path: Path) -> Dict[str, Dict[str, Any]]:
    if target_path.is_file() and target_path.name.endswith(".json"):
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        files = {}
        for a in data.get("artifacts", []):
            files[a["path"]] = {
                "path": a["path"],
                "size": a["size_bytes"],
                "sha256": a["sha256"],
            }
        return files
    return scan_dir(target_path)


def compare_builds(target_a: Path, target_b: Path) -> Dict[str, Any]:
    files_a = load_manifest_or_dir(target_a)
    files_b = load_manifest_or_dir(target_b)

    all_keys = sorted(set(files_a.keys()) | set(files_b.keys()))
    diffs: List[FileDiffResult] = []

    matches = 0
    mismatches = 0

    for key in all_keys:
        if key not in files_a:
            diffs.append(FileDiffResult(
                relative_path=key,
                status="MISSING_IN_A",
                size_a=None,
                size_b=files_b[key]["size"],
                sha256_a=None,
                sha256_b=files_b[key]["sha256"],
                drift_details="File exists only in Build B",
            ))
            mismatches += 1
        elif key not in files_b:
            diffs.append(FileDiffResult(
                relative_path=key,
                status="MISSING_IN_B",
                size_a=files_a[key]["size"],
                size_b=None,
                sha256_a=files_a[key]["sha256"],
                sha256_b=None,
                drift_details="File exists only in Build A",
            ))
            mismatches += 1
        else:
            fa = files_a[key]
            fb = files_b[key]
            if fa["sha256"] == fb["sha256"]:
                diffs.append(FileDiffResult(
                    relative_path=key,
                    status="MATCH",
                    size_a=fa["size"],
                    size_b=fb["size"],
                    sha256_a=fa["sha256"],
                    sha256_b=fb["sha256"],
                    drift_details="Bit-for-bit identical",
                ))
                matches += 1
            else:
                status = "SIZE_MISMATCH" if fa["size"] != fb["size"] else "HASH_MISMATCH"
                detail = f"Sizes differ: {fa['size']} vs {fb['size']} bytes" if fa["size"] != fb["size"] else "Binary content differs (hashes mismatch)"
                diffs.append(FileDiffResult(
                    relative_path=key,
                    status=status,
                    size_a=fa["size"],
                    size_b=fb["size"],
                    sha256_a=fa["sha256"],
                    sha256_b=fb["sha256"],
                    drift_details=detail,
                ))
                mismatches += 1

    total_files = len(all_keys)
    reproducibility_pct = (matches / total_files * 100.0) if total_files > 0 else 100.0

    has_missing = any(d.status in ("MISSING_IN_A", "MISSING_IN_B") for d in diffs)
    has_size_mismatch = any(d.status == "SIZE_MISMATCH" for d in diffs)

    if mismatches == 0:
        drift_class = "REPRODUCIBLE"
    elif has_missing:
        drift_class = "STRUCTURAL_DRIFT"
    elif has_size_mismatch:
        drift_class = "SIZE_DRIFT"
    else:
        drift_class = "BINARY_DRIFT"

    report = {
        "$schema": "https://aegisboot.dev/schema/diff-report.v1.json",
        "comparison_summary": {
            "target_a": str(target_a),
            "target_b": str(target_b),
            "total_artifacts": total_files,
            "matching_artifacts": matches,
            "mismatching_artifacts": mismatches,
            "reproducibility_percentage": round(reproducibility_pct, 2),
            "drift_classification": drift_class,
            "is_identical": mismatches == 0,
        },
        "diffs": [asdict(d) for d in diffs],
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Compare two AegisBoot builds to evaluate reproducibility and drift.")
    parser.add_argument("--build-a", required=True, help="Path to first build directory or manifest")
    parser.add_argument("--build-b", required=True, help="Path to second build directory or manifest")
    parser.add_argument("--output", default="diff-report.json", help="Output path for JSON diff report")
    parser.add_argument("--strict", action="store_true", help="Exit with non-zero code if any drift is detected")
    args = parser.parse_args()

    target_a = Path(args.build_a).resolve()
    target_b = Path(args.build_b).resolve()

    if not target_a.exists():
        print(f"[ERROR] Target A path does not exist: {target_a}")
        sys.exit(1)
    if not target_b.exists():
        print(f"[ERROR] Target B path does not exist: {target_b}")
        sys.exit(1)

    report = compare_builds(target_a, target_b)
    summary = report["comparison_summary"]

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("=== AegisBoot Build Comparison Report ===")
    print(f"Target A:          {summary['target_a']}")
    print(f"Target B:          {summary['target_b']}")
    print(f"Total Artifacts:   {summary['total_artifacts']}")
    print(f"Bit-for-Bit Match: {summary['matching_artifacts']}/{summary['total_artifacts']} ({summary['reproducibility_percentage']}%)")
    print(f"Classification:    {summary['drift_classification']}")
    print(f"Diff Report JSON:  {out_path}")
    print("")

    if not summary["is_identical"]:
        print("Mismatched / Drifted Artifacts:")
        for d in report["diffs"]:
            if d["status"] != "MATCH":
                print(f"  - [{d['status']}] {d['relative_path']}: {d['drift_details']}")
        print("")

    if args.strict and not summary["is_identical"]:
        print("[FAIL] Strict reproducibility check failed: build drift detected.")
        sys.exit(1)
    else:
        print("[SUCCESS] Build comparison completed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
