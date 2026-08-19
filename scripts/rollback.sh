#!/usr/bin/env bash
# ==============================================================================
# AegisBoot — Automated Rollback Engine
# ==============================================================================
# Supports rollback to previous release tag or specific commit
# Usage: ./scripts/rollback.sh [--tag <tag>] [--commit <sha>] [--dry-run]
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

MODE="rollback"
TARGET_TAG=""
TARGET_COMMIT=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --tag)
            TARGET_TAG="$2"
            shift 2
            ;;
        --commit)
            TARGET_COMMIT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--tag <tag>] [--commit <sha>] [--dry-run]"
            echo "  --tag <tag>      Rollback to specific release tag (e.g., v1.0.8-aegis.1+abc1234)"
            echo "  --commit <sha>   Rollback to specific commit SHA"
            echo "  --dry-run        Show what would be done without executing"
            echo "  --help           Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "=== AegisBoot Rollback Engine ==="
echo "Mode: ${MODE}"
echo "Dry-run: ${DRY_RUN}"

# Determine target
if [ -n "${TARGET_TAG}" ] && [ -n "${TARGET_COMMIT}" ]; then
    echo "[ERROR] Cannot specify both --tag and --commit"
    exit 1
fi

if [ -z "${TARGET_TAG}" ] && [ -z "${TARGET_COMMIT}" ]; then
    # Auto-detect: find previous release tag
    echo "[INFO] No target specified. Finding previous release tag..."
    CURRENT_TAG=$(git describe --tags --exact-match 2>/dev/null || echo "")
    if [ -n "${CURRENT_TAG}" ]; then
        echo "[INFO] Current tag: ${CURRENT_TAG}"
    fi
    
    # Find all release tags (v*-aegis.*)
    PREVIOUS_TAG=$(git tag -l "v*-aegis.*" | sort -V | grep -B1 "^${CURRENT_TAG}$" | head -1)
    
    if [ -z "${PREVIOUS_TAG}" ] || [ "${PREVIOUS_TAG}" = "${CURRENT_TAG}" ]; then
        echo "[ERROR] No previous release tag found for rollback"
        exit 1
    fi
    
    TARGET_TAG="${PREVIOUS_TAG}"
    echo "[INFO] Auto-selected previous release: ${TARGET_TAG}"
fi

# Resolve target commit
if [ -n "${TARGET_TAG}" ]; then
    if ! git rev-parse "${TARGET_TAG}" >/dev/null 2>&1; then
        echo "[ERROR] Tag not found: ${TARGET_TAG}"
        exit 1
    fi
    TARGET_COMMIT=$(git rev-parse "${TARGET_TAG}")
    echo "[INFO] Target tag: ${TARGET_TAG} (${TARGET_COMMIT})"
elif [ -n "${TARGET_COMMIT}" ]; then
    if ! git rev-parse "${TARGET_COMMIT}" >/dev/null 2>&1; then
        echo "[ERROR] Commit not found: ${TARGET_COMMIT}"
        exit 1
    fi
    echo "[INFO] Target commit: ${TARGET_COMMIT}"
fi

CURRENT_COMMIT=$(git rev-parse HEAD)
echo "[INFO] Current HEAD: ${CURRENT_COMMIT}"
echo "[INFO] Target commit: ${TARGET_COMMIT}"

if [ "${CURRENT_COMMIT}" = "${TARGET_COMMIT}" ]; then
    echo "[INFO] Already at target commit. Nothing to do."
    exit 0
fi

# Verify target is an ancestor (we're rolling back, not forward)
if ! git merge-base --is-ancestor "${TARGET_COMMIT}" "${CURRENT_COMMIT}"; then
    echo "[WARN] Target commit is not an ancestor of current HEAD. This is a forward rollback."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create rollback branch
ROLLBACK_BRANCH="rollback/$(date -u +%Y%m%d-%H%M%S)"
if [ -n "${TARGET_TAG}" ]; then
    ROLLBACK_BRANCH="rollback/${TARGET_TAG}-$(date -u +%Y%m%d-%H%M%S)"
fi

echo "[INFO] Creating rollback branch: ${ROLLBACK_BRANCH}"

if [ "${DRY_RUN}" = "true" ]; then
    echo "[DRY-RUN] Would execute:"
    echo "  git checkout -b ${ROLLBACK_BRANCH} ${TARGET_COMMIT}"
    echo "  git push fork ${ROLLBACK_BRANCH} --force"
    echo "  gh pr create --base master --head ${ROLLBACK_BRANCH} --title 'rollback: revert to ${TARGET_TAG:-${TARGET_COMMIT:0:7}}' --label 'rollback'"
    exit 0
fi

# Execute rollback
echo "[INFO] Checking out target commit..."
git checkout -b "${ROLLBACK_BRANCH}" "${TARGET_COMMIT}"

echo "[INFO] Pushing rollback branch to fork..."
git push fork "${ROLLBACK_BRANCH}" --force

# Create PR for review
PR_TITLE="rollback: revert to ${TARGET_TAG:-${TARGET_COMMIT:0:7}}"
PR_BODY=$(cat << EOF
### Automated Rollback

This PR reverts the distribution to a known-good state.

- **Target:** ${TARGET_TAG:-${TARGET_COMMIT}}
- **Target SHA:** \`${TARGET_COMMIT}\`
- **Previous HEAD:** \`${CURRENT_COMMIT}\`
- **Rollback Branch:** \`${ROLLBACK_BRANCH}\`

#### Reason
Emergency rollback triggered due to critical regression in current release.

#### Validation Required
- [ ] All CI gates pass
- [ ] QEMU boot test passes
- [ ] Manual verification on test hardware (if available)

#### Post-Merge
After merge, a new release will be automatically triggered with incremented revision.
EOF
)

echo "[INFO] Creating rollback PR..."
gh pr create \
    --base master \
    --head "${ROLLBACK_BRANCH}" \
    --title "${PR_TITLE}" \
    --body "${PR_BODY}" \
    --label "rollback,impact:critical"

echo "[OK] Rollback PR created. Review and merge to complete rollback."
echo "[INFO] After merge, release-trigger.yml will automatically create a new release."