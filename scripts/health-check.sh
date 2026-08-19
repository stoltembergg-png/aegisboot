#!/usr/bin/env bash
# ==============================================================================
# AegisBoot — Distribution Health & Divergence Monitor
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
UPSTREAM_URL="${UPSTREAM_URL:-https://github.com/acidanthera/OpenCorePkg.git}"

echo "=== AegisBoot Health Check ==="
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date)"

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
if [ -f "${SCRIPT_DIR}/generate-version-metadata.py" ]; then
  python3 "${SCRIPT_DIR}/generate-version-metadata.py" --output /dev/null >/dev/null 2>&1 && echo "Version Metadata Engine: OK" || echo "Version Metadata Engine: FAILED"
fi

echo ""
if [ $HEALTH_STATUS -eq 0 ]; then
  echo "=== Health Check Status: HEALTHY ==="
  exit 0
else
  echo "=== Health Check Status: ATTENTION REQUIRED ==="
  exit 1
fi
