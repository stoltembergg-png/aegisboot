#!/usr/bin/env python3
"""
AegisBoot — Validate CycloneDX SBOM structure
"""
import json
import sys
from pathlib import Path


def validate_sbom(sbom_path: Path) -> bool:
    try:
        with open(sbom_path) as f:
            sbom = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to parse SBOM: {e}")
        return False

    if sbom.get('bomFormat') != 'CycloneDX':
        print(f"[ERROR] Invalid bomFormat: {sbom.get('bomFormat')}")
        return False

    if 'metadata' not in sbom:
        print("[ERROR] Missing 'metadata' in SBOM")
        return False

    print("[OK] CycloneDX SBOM validated successfully")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sbom", required=True, help="Path to SBOM file")
    args = parser.parse_args()

    sbom_path = Path(args.sbom)
    if not sbom_path.exists():
        print(f"[ERROR] SBOM file not found: {sbom_path}")
        sys.exit(1)

    if validate_sbom(sbom_path):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()