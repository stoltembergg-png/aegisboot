# AegisBoot — Compatibility Policy

---

## 1. Supported Hardware Architectures

AegisBoot preserves all target architectures supported by upstream OpenCorePkg:

| Architecture | Identifier | Build Status | Primary Target |
|---|---|---|---|
| **x86_64** | `X64` | Primary / Fully Validated | Modern 64-bit Intel and AMD UEFI systems |
| **IA-32** | `Ia32` | Primary / Fully Validated | Legacy 32-bit UEFI firmware and older Apple hardware |
| **AArch64** | `AArch64` | Experimental | ARM64 UEFI development environments and VMs |

---

## 2. UEFI Specification Compliance

- **Supported UEFI Versions:** UEFI Specification 2.1 through 2.10, PI 1.7+.
- **Firmware Environments:** Native Apple EFI, standard PC UEFI (AMI, Insyde, Phoenix), OpenDuet legacy emulation, and virtualized firmware (OVMF / EDK II in QEMU / KVM / VMware / Hyper-V).

---

## 3. macOS Version Compatibility Matrix

AegisBoot maintains complete runtime and booter compatibility across the entire spectrum of macOS versions supported by upstream:

| OS Family | Version Range | Notes |
|---|---|---|
| **macOS 15 Sequoia / Future (macOS 26+)** | Modern | Full APFS, Secure Boot, Preboot, and kernel injection support. |
| **macOS 11 Big Sur — 14 Sonoma** | Modern | Full APFS snapshot boot, kernel collection patching, SIP integration. |
| **macOS 10.13 High Sierra — 10.15 Catalina** | Stable | APFS loading, Lilu kernel extension routing. |
| **Mac OS X 10.4 Tiger — 10.12 Sierra** | Legacy | Supported via legacy booter quirks and OpenDuet. |

---

## 4. Configuration Schema Integrity (`config.plist`)

> [!IMPORTANT]
> **Zero Schema Deviation:** AegisBoot will **never** introduce non-standard or proprietary XML configuration keys that fail validation in upstream `ocvalidate`.

- Every downstream build validates `Docs/Sample.plist` and `Docs/SampleCustom.plist` against the compiled `ocvalidate` binary.
- All OpenCore configuration structures, NVRAM variables, quirks, and boot arguments remain 100% interoperable with upstream tools (OpenCore Configurator, ProperTree, ocvalidate).
