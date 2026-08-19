# ADR-009: QEMU Boot Test Strategy

## Status
Accepted

## Context
We need automated UEFI boot regression testing to catch boot failures before release. The test must run in GitHub Actions on Linux runners.

## Decision
**Test Approach:**
- QEMU + OVMF firmware on `ubuntu-24.04` runner
- Test runs in `ci.yml` → `qemu-boot-test` job
- Uses real OpenCore binaries when available, dummy EFI fallback
- Timeout: 10 seconds (enough for initial boot sequence)

**Implementation (`tests/test_qemu_boot.py`):**
1. Find OVMF firmware in standard paths
2. Locate OpenCore binaries in `Binaries/` (RELEASE > DEBUG > NOOPT)
3. Extract EFI structure from zip, stage FAT drive image
4. Launch QEMU with OVMF, FAT drive, serial console
5. Capture output, check for OpenCore banner
6. Graceful skip if QEMU/OVMF not available

**Test Criteria (Pass):**
- QEMU launches without immediate crash
- OpenCore banner detected in serial output (when real binaries used)
- No kernel panic or UEFI error in first 10 seconds

**CI Integration:**
- Runs on every PR and push to `master`
- Required gate in `ci.yml`
- 20-minute timeout
- Installs QEMU + OVMF via apt

## Consequences
**Positive:**
- Catches boot regressions early
- Runs on every sync PR
- Graceful degradation (skip if no binaries/QEMU)
- Fast feedback (~10-15 seconds)

**Negative:**
- Requires QEMU + OVMF installation (adds ~30s to CI)
- Linux-only (no macOS/Windows boot test)
- Dummy EFI test is limited (real hardware not tested)

## Implementation References
- `tests/test_qemu_boot.py` - Test harness
- `.github/workflows/ci.yml` → `qemu-boot-test` job
- `docs/build-instructions.md` - Local QEMU test instructions
- `docs/troubleshooting.md` - QEMU debugging guide