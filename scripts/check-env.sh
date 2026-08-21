#!/usr/bin/env bash
# ==============================================================================
# AegisBoot — Idempotent Environment Prerequisite Checker
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== AegisBoot Environment Check ==="
echo "Working directory: ${ROOT_DIR}"
echo "System OS: $(uname -s 2>/dev/null || echo "Unknown")"

ERRORS=0
WARNINGS=0

check_cmd() {
  local cmd="$1"
  local required="$2"
  local min_ver="${3:-}"

  if command -v "$cmd" >/dev/null 2>&1; then
    local path
    path="$(command -v "$cmd")"
    echo "  [OK] $cmd found at: $path"
  else
    if [ "$required" = "1" ]; then
      echo "  [ERROR] Required command missing: $cmd"
      ERRORS=$((ERRORS + 1))
    else
      echo "  [WARN] Optional command missing: $cmd"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
}

echo ""
echo "Checking core build tools:"
check_cmd git 1
check_cmd python3 1
check_cmd nasm 1
check_cmd iasl 1
check_cmd make 1
check_cmd zip 1
check_cmd curl 1

echo ""
echo "Checking container & testing environments:"
check_cmd docker 0
check_cmd qemu-system-x86_64 0
check_cmd shellcheck 0
check_cmd uncrustify 0

echo ""
echo "Checking Python environment:"
if command -v python3 >/dev/null 2>&1; then
  PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
  echo "  [OK] Python version: $PY_VER"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
  echo "=== Environment Check PASSED (${WARNINGS} warnings) ==="
  exit 0
else
  echo "=== Environment Check FAILED (${ERRORS} errors, ${WARNINGS} warnings) ==="
  exit 1
fi
