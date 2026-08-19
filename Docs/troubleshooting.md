# AegisBoot — Troubleshooting Guide

This document lists common build, sync, and validation issues encountered in AegisBoot along with actionable resolutions.

---

## 1. Build Failures

### Issue 1.1: `nasm: fatal: unable to open include file` or Version Mismatch
- **Cause:** Outdated NASM version or incomplete search path.
- **Resolution:** Verify NASM version with `nasm -v`. Ensure version is `>= 2.15.05` (preferably `2.16.03`). On Ubuntu:
  ```bash
  sudo apt install nasm
  ```

### Issue 1.2: `iasl: command not found` / ASL Compilation Error
- **Cause:** ACPICA compiler missing from system path.
- **Resolution:** Install ACPICA tools:
  - Linux: `sudo apt install iasl`
  - macOS: `brew install acpica`

### Issue 1.3: EDK II Submodule / AUDK Download Timeout
- **Cause:** GitHub network transient latency during `ci-bootstrap.sh` execution.
- **Resolution:** Re-run the idempotent build script:
  ```bash
  FORCE_INSTALL=1 ./scripts/build-distro.sh
  ```

---

## 2. Upstream Synchronization Failures

### Issue 2.1: Merge Conflict on Sync Branch (`sync/upstream-*`)
- **Cause:** Upstream commit modified a structure or configuration schema overlapping with downstream tooling.
- **Resolution:**
  1. Inspect the conflict report generated in the sync PR.
  2. Run `git checkout sync/upstream` and check conflicted files with `git status`.
  3. Resolve conflicts preserving upstream semantics.
  4. Run `./scripts/apply-patches.sh --check` to verify local patches.
  5. Commit resolution with message: `fix(sync): resolve upstream conflict in <component>`.

### Issue 2.2: Patch Rebase Failure (`Patches/000X-...patch`)
- **Cause:** Upstream has merged or refactored the subsystem targeted by the patch.
- **Resolution:**
  1. Check if upstream already incorporated the fix (`git log -S "<symbol>"`).
  2. If incorporated, delete the redundant `.patch` file from `Patches/`.
  3. If still needed, rebase the patch using `git format-patch` against latest `origin/master`.

---

## 3. QEMU / OVMF Boot Test Failures

### Issue 3.1: QEMU Hangs or Panics on OVMF Boot
- **Cause:** Missing OVMF binary or corrupted virtual FAT directory image.
- **Resolution:**
  1. Ensure OVMF firmware package is installed: `sudo apt install ovmf qemu-system-x86`.
  2. Verify that `OpenCore.efi` and mandatory drivers (`OpenRuntime.efi`, `ResetNvramEntry.efi`) are present in the staged EFI partition:
  ```bash
  python3 tests/test_qemu_boot.py
  ```

---

## 4. Secret Scanner or Linter Alerts

### Issue 4.1: Gitleaks Flagged a False Positive
- **Cause:** Hash, UUID, or sample certificate in `Docs/` or `Utilities/` triggered regex pattern.
- **Resolution:**
  - Verify that no private key or token was actually exposed.
  - Add the specific SHA or fingerprint to `.gitleaksignore` with an explicit reason comment.
