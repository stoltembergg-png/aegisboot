# Compatibility Policy

> **Policy Version:** 1.0.0
> **Status:** Active
> **Last Updated:** 2026-08-19

---

## 1. Purpose

This policy defines the compatibility guarantees, supported platforms, and versioning contracts for the AegisBoot downstream distribution of OpenCorePkg.

---

## 2. Upstream Compatibility

### 2.1 Version Tracking

AegisBoot tracks **exactly one upstream branch** at a time:

| AegisBoot Channel | Upstream Branch | Sync Policy |
|---|---|---|
| `stable` | `master` (release tags) | Tag-based sync |
| `staging` | `master` | Continuous (15-min cadence) |
| `edge` | `master` | Continuous (15-min cadence) |

### 2.2 Binary Compatibility

| Guarantee | Scope |
|---|---|
| **Config.plist Schema** | Full backward compatibility with upstream schema for tracked version |
| **ACPI/SSDT** | No breaking changes to ACPI patching semantics |
| **Kext Injection** | Compatible with upstream kext loading mechanism |
| **UEFI Protocols** | Strict adherence to UEFI spec and upstream implementations |
| **NVRAM Variables** | Compatible with upstream variable naming and semantics |

### 2.3 Breaking Change Handling

If upstream introduces a breaking change:
1. Sync PR labeled `impact:major`
2. Auto-merge **blocked** (requires manual approval)
3. Migration guide documented in release notes
4. Config.plist migration script provided if applicable

---

## 3. Supported Platforms

### 3.1 Build Targets (Multi-Platform CI)

| Platform | Toolchain | Target | CI Job |
|---|---|---|---|
| Linux | CLANGPDB | X64 RELEASE/DEBUG/NOOPT | `build-linux-clangpdb` |
| Linux | GCC5 | X64 RELEASE/DEBUG/NOOPT | `build-linux-gcc5` |
| Linux | CLANGDWARF | X64 RELEASE/DEBUG/NOOPT | `build-linux-clangdwarf` |
| macOS | Xcode 15+ (XCODE5) | X64 RELEASE/DEBUG/NOOPT | `build-macos` |
| Windows | VS2022 + MinGW | X64 RELEASE/DEBUG/NOOPT | `build-windows` |

### 3.2 Runtime Target Hardware

AegisBoot binaries are compatible with the **exact same hardware matrix** as upstream OpenCorePkg for the tracked version. No additional hardware support is claimed beyond upstream.

| Category | Supported |
|---|---|
| Intel CPUs | Per upstream 1.0.x support matrix |
| AMD CPUs | Per upstream 1.0.x support matrix |
| Chipsets | Per upstream 1.0.x support matrix |
| GPUs | Per upstream 1.0.x support matrix |
| WiFi/BT | Per upstream 1.0.x support matrix |
| Storage Controllers | Per upstream 1.0.x support matrix |

**Reference:** [OpenCore Supported Hardware](https://dortania.github.io/OpenCore-Install-Guide/hardware.html)

---

## 4. macOS Version Compatibility

AegisBoot builds are compatible with the **same macOS versions** as the tracked upstream OpenCore version.

| Upstream OpenCore | macOS Minimum | macOS Maximum (Tested) |
|---|---|---|
| 1.0.8 | 10.13 High Sierra | macOS 15 Sequoia (beta) |
| 1.0.x | Per upstream docs | Per upstream docs |

**No downstream modifications** to macOS version compatibility.

---

## 5. Configuration Compatibility

### 5.1 Config.plist

- **Schema Version:** Matches upstream exactly
- **New Keys:** Only added when upstream adds them
- **Deprecated Keys:** Kept for backward compatibility per upstream
- **Validation:** `ocvalidate` from same upstream version

### 5.2 ACPI Samples

- `Docs/Sample.plist` and `Docs/SampleCustom.plist` tracked from upstream
- No downstream modifications to samples
- Lint validation in CI ensures format compliance

---

## 6. Toolchain Compatibility

### 6.1 Pinned Toolchains

All builds use **pinned, reproducible toolchains** defined in `toolchains/toolchain-pins.json`:

| Component | Version Pinning |
|---|---|
| LLVM/Clang | Exact version (e.g., 21.0.0) |
| GCC | Exact version (e.g., 13.2.0) |
| Xcode | Minimum + Recommended (e.g., 15.0 / 16.0) |
| NASM | Exact version + SHA256 |
| iasl (ACPI) | Exact version + SHA256 |
| Python | >= 3.10 |
| QEMU | >= 8.2.0 |
| OVMF | 2024.02 |

### 6.2 Reproducibility

- Same source + same toolchain pins = **bit-for-bit identical binaries**
- Verified by `scripts/check-build-drift.sh` in CI
- Docker images for Linux builds are pinned by digest

---

## 7. Dependency Compatibility

### 7.1 EDK II Base

AegisBoot uses the **same EDK II baseline** as upstream:
- `edk2-stable202511` (or whatever upstream specifies)
- No downstream EDK II modifications

### 7.2 ocbuild

Bootstrap and build infrastructure from `acidanthera/ocbuild` at pinned commit.

---

## 8. Version Compatibility Matrix

| AegisBoot Release | Upstream OpenCore | EDK II Baseline | Toolchain Spec |
|---|---|---|---|
| v1.0.8-aegis.1+170b538 | 1.0.8 | edk2-stable202511 | toolchain-pins.json v1.0.0 |
| v1.0.8-aegis.2+170b538 | 1.0.8 | edk2-stable202511 | toolchain-pins.json v1.0.0 |
| v1.0.9-aegis.1+abc1234 | 1.0.9 | (per upstream) | (updated) |

---

## 9. Deprecation Policy

| Item | Notice Period | Removal |
|---|---|---|
| Build target | 2 release cycles | Next major |
| CI workflow | 1 release cycle | Next release |
| Script/tool | 1 release cycle | Next release |
| Patch (upstream merged) | Immediate | On next sync |

---

## 10. Forward Compatibility (Future Upstream)

When upstream releases new major version:
1. AegisBoot creates `staging` channel tracking new upstream
2. Parallel validation for minimum 2 weeks
3. `stable` channel migrates after:
   - All CI gates pass
   - No critical regressions in QEMU boot tests
   - Community validation period (optional)
4. Old `stable` becomes `legacy` (security-only for 90 days)

---

## 11. Compatibility Testing

### 10.1 Automated (CI)

| Test | Frequency | Scope |
|---|---|---|
| Multi-platform build | Every PR | All 5 toolchains |
| Static analysis | Every PR | Shell, Python, C |
| QEMU/OVMF boot | Every PR | UEFI boot flow |
| Config.plist validation | Every PR | `ocvalidate` |
| Build drift detection | Every PR | Reproducibility |

### 10.2 Manual (Release Gate)

| Test | Scope |
|---|---|
| Real hardware smoke test | Maintainer hardware |
| Config.plist migration | Common configs |
| Kext injection | Popular kexts (Lilu, WhateverGreen, etc.) |
| Vault/secure boot | If applicable |

---

## 12. Non-Goals (Explicitly NOT Guaranteed)

- Compatibility with **non-upstream** forks or patches
- Support for **deprecated** macOS versions dropped by upstream
- Hardware support **beyond** upstream's published matrix
- Binary compatibility with **other downstream** distributions
- Stability of **unstable/edge** channel builds

---

## 13. Reporting Compatibility Issues

Use the **Bug Report template** (`.github/ISSUE_TEMPLATE/bug_report.yml`) with:
- AegisBoot version (`v1.0.8-aegis.1+170b538`)
- Upstream OpenCore version tested against
- Hardware/platform details
- Config.plist (sanitized)
- Steps to reproduce

---

## 14. Compliance Checklist

For each release:

- [ ] All 5 build targets pass
- [ ] QEMU/OVMF boot test passes
- [ ] `ocvalidate` passes for samples
- [ ] Build drift check passes (reproducibility)
- [ ] Toolchain pins match `toolchain-pins.json`
- [ ] Config.plist schema matches upstream
- [ ] No downstream ACPI/kext modifications
- [ ] Release notes document any upstream breaking changes

---

## 15. Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-08-19 | Initial policy |