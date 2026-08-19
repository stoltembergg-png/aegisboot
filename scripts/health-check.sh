#!/usr/bin/env bash
# ==============================================================================
# AegisBoot — Distribution Health & Divergence Monitor
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
UPSTREAM_URL="${UPSTREAM_URL:-https://github.com/acidanthera/OpenCorePkg.git}"

# Detect Python interpreter (cross-platform)
# Priority: 1) .venv in repo, 2) python3 (if not Windows Store alias), 3) python
PYTHON_CMD=""

# Check for repo virtualenv first
if [ -f "${ROOT_DIR}/.venv/Scripts/python.exe" ]; then
  PYTHON_CMD="${ROOT_DIR}/.venv/Scripts/python.exe"
elif [ -f "${ROOT_DIR}/.venv/bin/python" ]; then
  PYTHON_CMD="${ROOT_DIR}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  # Verify python3 is not Windows Store alias
  if python3 -c "import sys; sys.exit(0)" 2>/dev/null; then
    PYTHON_CMD="python3"
  fi
fi

# Fallback to python
if [ -z "${PYTHON_CMD}" ] && command -v python >/dev/null 2>&1; then
  if python -c "import sys; sys.exit(0)" 2>/dev/null; then
    PYTHON_CMD="python"
  fi
fi

echo "=== AegisBoot Health Check ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date)"
echo "Python: ${PYTHON_CMD:-NOT FOUND}"

cd "${ROOT_DIR}"

HEALTH_STATUS=0

# 1. Check upstream connectivity
echo -n "Upstream Connectivity (${UPSTREAM_URL}): "
if git ls-remote --heads "${UPSTREAM_URL}" master >/dev/null 2>&1; then
  echo "OK"
else
  echo "FAILED (Network or Remote Unreachable)"
  HEALTH_STATUS=1
fi

# 2. Check latest upstream commit SHA
LATEST_UPSTREAM_SHA=$(git ls-remote "${UPSTREAM_URL}" refs/heads/master 2>/dev/null | awk '{print $1}' || echo "unknown")
echo "Latest Upstream Master SHA: ${LATEST_UPSTREAM_SHA}"

# 3. Check local commit SHA
LOCAL_HEAD=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
echo "Current Distribution HEAD:  ${LOCAL_HEAD}"

# 4. Check patch stack status
echo "Patch Stack Status:"
if [ -f "${SCRIPT_DIR}/apply-patches.sh" ]; then
  "${SCRIPT_DIR}/apply-patches.sh" --check || HEALTH_STATUS=1
fi

# 5. Check toolchain pins
if [ -f "${ROOT_DIR}/toolchains/toolchain-pins.json" ]; then
  echo "Toolchain Pins: OK"
else
  echo "Toolchain Pins: MISSING"
  HEALTH_STATUS=1
fi

# 6. Verify version metadata generation
if [ -f "${SCRIPT_DIR}/generate-version-metadata.py" ] && [ -n "${PYTHON_CMD}" ]; then
  # Use relative path from ROOT_DIR
  "${PYTHON_CMD}" scripts/generate-version-metadata.py --output /dev/null >/dev/null 2>&1 && echo "Version Metadata Engine: OK" || echo "Version Metadata Engine: FAILED"
elif [ -z "${PYTHON_CMD}" ]; then
  echo "Version Metadata Engine: SKIPPED (Python not found)"
fi

echo ""
if [ $HEALTH_STATUS -eq 0 ]; then
  echo "=== Health Check Status: HEALTHY ==="
  exit 0
else
  echo "=== Health Check Status: ATTENTION REQUIRED ==="
  exit 1
fi