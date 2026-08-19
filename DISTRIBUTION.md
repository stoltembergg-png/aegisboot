# AegisBoot — Continuous Distribution Architecture of OpenCorePkg

> **Core Tenet:** *Stay upstream-compatible. Ship faster. Validate harder. Diverge minimally.*

---

## 1. Upstream Relationship & Philosophy

**AegisBoot** is an automated, continuously integrated downstream distribution and tracking fork of [`acidanthera/OpenCorePkg`](https://github.com/acidanthera/OpenCorePkg).

### 1.1 Source of Truth
- The primary source of truth for the codebase is upstream `acidanthera/OpenCorePkg` (`master` branch and tagged releases).
- AegisBoot does not aim to reinvent or replace OpenCore. Its objective is to provide a **rigorously tested, continuously integrated downstream distribution** that tracks upstream changes in near real-time, subjecting every commit to deep automated validation (multi-platform compilation, static analysis, QEMU/OVMF boot testing, and supply-chain auditing).
- Releases are made independently and more frequently as soon as validated changes land, avoiding long waits between official upstream release cycles while maintaining exact cryptographic provenance back to upstream commit SHAs.

### 1.2 Non-Divergence Pledge
AegisBoot adheres to a strict non-divergence policy:
1. **Zero arbitrary modifications:** No changes are made to core OpenCore UEFI drivers, libraries, or configuration schemas for cosmetic or personal preferences.
2. **Upstream-first contribution:** Any bug fixes, performance improvements, or hardware quirks identified within this distribution are contributed directly upstream to `acidanthera/OpenCorePkg`.
3. **Transparent Patch Stack:** Any temporary local patches maintained downstream reside in `Patches/`, formatted as clean `git format-patch` series with upstream tracking metadata, and are retired immediately once adopted upstream.
4. **Transparent Conflict Resolution:** Sync conflicts are never masked, hidden, or resolved by force-pushing. Every merge is fully auditable.

---

## 2. Distribution Model

```
┌─────────────────────────────────────────────────────────────┐
│                 UPSTREAM: acidanthera/OpenCorePkg           │
└──────────────────────────────┬──────────────────────────────┘
                               │ Fetch (Automated 15-min cadence)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  AEGISBOOT SYNC ENGINE                      │
│                                                             │
│  - Automated branch generation: sync/upstream-<sha>         │
│  - Conflict pre-detection & non-masking evaluation          │
│  - Local patch rebase validation                            │
└──────────────────────────────┬──────────────────────────────┘
                               │ Pull Request & CI Trigger
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               RIGOROUS CI/CD VALIDATION GATES               │
│                                                             │
│  1. Workflow & Supply-Chain Integrity                       │
│  2. Code Formatting (Uncrustify / Linters)                  │
│  3. Static Analysis (ShellCheck, Prospector, ocvalidate)    │
│  4. Multi-Platform Compilation (CLANGPDB, GCC5, XCODE5)     │
│  5. Unit & Integration Test Suites (Utilities, ACPI, Kext)  │
│  6. Automated QEMU/OVMF UEFI Boot Regression                │
│  7. Secret & License Compliance Scanning                    │
│  8. Binary Integrity & SHA-256/512 Digest Verification      │
└──────────────────────────────┬──────────────────────────────┘
                               │ All Gates Pass (100% Green)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 MAIN BRANCH (Protected)                     │
└──────────────────────────────┬──────────────────────────────┘
                               │ Tagged Release / Edge Pipeline
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                DISTRIBUTION RELEASE ARTIFACTS               │
│                                                             │
│  - OpenCore Binaries (DEBUG, RELEASE, NOOPT)                │
│  - CycloneDX SBOM (Software Bill of Materials)              │
│  - SLSA Level 3 Provenance & Checksum Manifests             │
│  - Machine-readable version metadata (distro-version.json)  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Key Distribution Attributes

| Attribute | Specification |
|---|---|
| **Upstream Remote** | `origin` -> `https://github.com/acidanthera/OpenCorePkg.git` |
| **Default Branch** | `master` / `main` (Protected against direct pushes and force pushes) |
| **Sync Cadence** | Automated poll every 15 minutes + on-demand dispatch |
| **Build Reproducibility** | Pinned toolchains (`toolchains/toolchain-pins.json`) and Docker builds |
| **Traceability** | Every release tracks `v<upstream>-aegis.<rev>+<upstream_sha>` |
| **Supply Chain Security** | CycloneDX SBOM + SLSA Provenance + SHA256/SHA512 checksums |
| **License** | Inherited from upstream (BSD 3-Clause / Apple Public Source License / Apache 2.0 where specified) |
