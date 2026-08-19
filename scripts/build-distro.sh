#!/usr/bin/env bash
# ==============================================================================
# AegisBoot — Idempotent Distribution Build Orchestrator
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

TARGETS="${TARGETS:-RELEASE}"
ARCHS="${ARCHS:-X64}"
TOOLCHAINS="${TOOLCHAINS:-}"
USE_DOCKER=0
SKIP_DUET=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGETS="$2"
      shift 2
      ;;
    --arch)
      ARCHS="$2"
      shift 2
      ;;
    --toolchain)
      TOOLCHAINS="$2"
      shift 2
      ;;
    --docker)
      USE_DOCKER=1
      shift
      ;;
    --skip-duet)
      SKIP_DUET=1
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

export TARGETS ARCHS TOOLCHAINS
export FORCE_INSTALL=1
export HAS_OPENSSL_BUILD=1
export WERROR=1

cd "${ROOT_DIR}"

echo "=== AegisBoot Build Orchestrator ==="
echo "Target(s):    ${TARGETS}"
echo "Arch(s):      ${ARCHS}"
echo "Toolchain(s): ${TOOLCHAINS:-default}"
echo "Docker mode:  ${USE_DOCKER}"

if [ "${USE_DOCKER}" = "1" ]; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "[ERROR] Docker is required for --docker mode."
    exit 1
  fi
  echo "Executing build inside Docker container..."
  if [ "${SKIP_DUET}" != "1" ]; then
    docker compose run --rm build-duet
  fi
  docker compose run --rm build-oc
else
  # Native build execution
  if [ "${SKIP_DUET}" != "1" ] && [ -f "./build_duet.tool" ]; then
    echo "Executing build_duet.tool..."
    ./build_duet.tool
  fi

  if [ -f "./build_oc.tool" ]; then
    echo "Executing build_oc.tool..."
    ./build_oc.tool
  fi
fi

echo "=== Build Orchestration Complete ==="
if [ -d "Binaries" ]; then
  echo "Generated Artifacts:"
  ls -lh Binaries/
fi
