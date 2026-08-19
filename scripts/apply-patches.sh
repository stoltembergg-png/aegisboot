#!/usr/bin/env bash
# ==============================================================================
# AegisBoot — Idempotent Patch Stack Manager
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PATCH_DIR="${ROOT_DIR}/Patches"
TARGET_DIR="${ROOT_DIR}"

if [ -d "${ROOT_DIR}/UDK" ]; then
  TARGET_DIR="${ROOT_DIR}/UDK"
fi

MODE="apply"
if [ "${1:-}" = "--check" ]; then
  MODE="check"
fi

echo "=== AegisBoot Patch Stack Manager (Mode: ${MODE}) ==="
echo "Target working tree: ${TARGET_DIR}"

if [ ! -d "${PATCH_DIR}" ]; then
  echo "No Patches directory found. Nothing to do."
  exit 0
fi

shopt -s nullglob
PATCH_FILES=("${PATCH_DIR}"/*.patch)
shopt -u nullglob

if [ ${#PATCH_FILES[@]} -eq 0 ]; then
  echo "No .patch files found in ${PATCH_DIR}. Patch stack is clean."
  exit 0
fi

echo "Found ${#PATCH_FILES[@]} patch file(s):"

TOTAL_FAILED=0

for patch in "${PATCH_FILES[@]}"; do
  patch_name="$(basename "$patch")"
  echo -n "  Checking [${patch_name}]... "

  # If UDK directory exists, test live application in UDK tree
  if [ -d "${ROOT_DIR}/UDK" ]; then
    if ! (cd "${TARGET_DIR}" && git apply --check "$patch" 2>/dev/null); then
      if (cd "${TARGET_DIR}" && git apply --reverse --check "$patch" 2>/dev/null); then
        echo "ALREADY_APPLIED"
        continue
      else
        echo "REJECTED / CONFLICT (in UDK)"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        continue
      fi
    fi

    if [ "${MODE}" = "apply" ]; then
      if (cd "${TARGET_DIR}" && git apply "$patch" 2>/dev/null); then
        echo "APPLIED_SUCCESS"
      else
        echo "FAILED_TO_APPLY"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
      fi
    else
      echo "CLEAN (UDK)"
    fi
  else
    # Validate patch file structure and diff statistics
    if git apply --stat "$patch" >/dev/null 2>&1; then
      echo "SYNTAX_VALID (Pre-UDK bootstrap)"
    else
      echo "INVALID_PATCH_FORMAT"
      TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
  fi
done

echo ""
if [ $TOTAL_FAILED -eq 0 ]; then
  echo "=== Patch Stack Verification PASSED ==="
  exit 0
else
  echo "=== Patch Stack Verification FAILED (${TOTAL_FAILED} issues) ==="
  exit 1
fi
