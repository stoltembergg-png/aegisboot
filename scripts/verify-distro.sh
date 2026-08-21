#!/usr/bin/env bash
# ==============================================================================
# AegisBoot — Artifact Integrity & Checksum Verification Engine
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BIN_DIR="${ROOT_DIR}/Binaries"

cd "${ROOT_DIR}"

echo "=== AegisBoot Artifact Verification ==="

if [ ! -d "${BIN_DIR}" ]; then
  echo "Creating Binaries directory..."
  mkdir -p "${BIN_DIR}"
fi

# 1. Run ocvalidate if binary is present
OCVALIDATE_BIN=""
for candidate in \
  "${BIN_DIR}/ocvalidate" \
  "${ROOT_DIR}/Utilities/ocvalidate/ocvalidate" \
  "$(command -v ocvalidate 2>/dev/null || true)"; do
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then
    OCVALIDATE_BIN="$candidate"
    break
  fi
done

if [ -n "${OCVALIDATE_BIN}" ]; then
  echo "Found ocvalidate: ${OCVALIDATE_BIN}"
  if [ -f "Docs/Sample.plist" ]; then
    echo -n "  Validating Docs/Sample.plist... "
    if "${OCVALIDATE_BIN}" Docs/Sample.plist >/dev/null; then
      echo "OK"
    else
      echo "FAILED"
      exit 1
    fi
  fi
  if [ -f "Docs/SampleCustom.plist" ]; then
    echo -n "  Validating Docs/SampleCustom.plist... "
    if "${OCVALIDATE_BIN}" Docs/SampleCustom.plist >/dev/null; then
      echo "OK"
    else
      echo "FAILED"
      exit 1
    fi
  fi
else
  echo "ocvalidate not found in tree yet. Skipping plist schema validation."
fi

# 2. Generate Checksums if ZIP binaries exist
shopt -s nullglob
ZIP_FILES=("${BIN_DIR}"/*.zip)
shopt -u nullglob

if [ ${#ZIP_FILES[@]} -gt 0 ]; then
  echo "Generating cryptographic checksums for ${#ZIP_FILES[@]} binary package(s)..."
  cd "${BIN_DIR}"

  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum ./*.zip > SHA256SUMS.txt
    echo "  [OK] Generated SHA256SUMS.txt"
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 ./*.zip > SHA256SUMS.txt
    echo "  [OK] Generated SHA256SUMS.txt"
  fi

  if command -v sha512sum >/dev/null 2>&1; then
    sha512sum ./*.zip > SHA512SUMS.txt
    echo "  [OK] Generated SHA512SUMS.txt"
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 512 ./*.zip > SHA512SUMS.txt
    echo "  [OK] Generated SHA512SUMS.txt"
  fi
  cd "${ROOT_DIR}"
else
  echo "No ZIP packages found in ${BIN_DIR}. Checksum generation skipped."
fi

echo "=== Artifact Verification Complete ==="