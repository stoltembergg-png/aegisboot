#!/usr/bin/env bash
# ==============================================================================
# AegisBoot — Idempotent Upstream Synchronization Engine
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
UPSTREAM_URL="${UPSTREAM_URL:-https://github.com/acidanthera/OpenCorePkg.git}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-master}"

cd "${ROOT_DIR}"

echo "=== AegisBoot Upstream Sync ==="
echo "Target upstream: ${UPSTREAM_URL} (${UPSTREAM_BRANCH})"

# 1. Ensure upstream remote exists
if ! git remote | grep -q "^origin$"; then
  echo "Adding upstream remote 'origin' -> ${UPSTREAM_URL}"
  git remote add origin "${UPSTREAM_URL}"
fi

# 2. Fetch latest upstream state
echo "Fetching origin ${UPSTREAM_BRANCH}..."
git fetch origin "${UPSTREAM_BRANCH}" --tags --quiet

LOCAL_HEAD=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
UPSTREAM_HEAD=$(git rev-parse "origin/${UPSTREAM_BRANCH}")
UPSTREAM_SHORT=$(git rev-parse --short "origin/${UPSTREAM_BRANCH}")
UPSTREAM_DATE=$(git log -1 --format=%ci "origin/${UPSTREAM_BRANCH}")

echo "Local HEAD:     ${LOCAL_HEAD}"
echo "Upstream HEAD:  ${UPSTREAM_HEAD} (${UPSTREAM_DATE})"

if [ "${LOCAL_HEAD}" = "${UPSTREAM_HEAD}" ]; then
  echo "Status: IN_SYNC (Local repository is already at latest upstream HEAD)."
  exit 0
fi

echo "Status: DIVERGED (New upstream commits detected)."
AHEAD_COUNT=$(git rev-list --count "HEAD..origin/${UPSTREAM_BRANCH}" 2>/dev/null || echo "0")
echo "Upstream is ahead by ${AHEAD_COUNT} commit(s)."

# 3. Verify local patch stack against new upstream
echo "Validating patch stack applicability against origin/${UPSTREAM_BRANCH}..."
if [ -f "${SCRIPT_DIR}/apply-patches.sh" ]; then
  "${SCRIPT_DIR}/apply-patches.sh" --check || {
    echo "[ERROR] Local patch stack failed clean check against upstream HEAD."
    exit 1
  }
fi

echo "=== Sync Analysis Complete ==="
echo "Upstream SHA: ${UPSTREAM_HEAD}"
echo "Upstream Short: ${UPSTREAM_SHORT}"
