# AegisBoot — Release Policy

---

## 1. Release Channels & Cadence

AegisBoot provides three distinct release channels to balance immediate upstream sync tracking with production stability:

```
┌─────────────────────────────────────────────────────────────┐
│                    AEGISBOOT RELEASE CHANNELS               │
└─────────────────────────────────────────────────────────────┘
  │
  ├── 1. EDGE / NIGHTLY
  │   - Frequency: On every upstream commit integrated into main.
  │   - Target: Automated CI testing, hardware lab validation, early adopters.
  │   - Stability: Bleeding edge (all CI gates passed).
  │
  ├── 2. STAGING / CANARY
  │   - Frequency: Weekly rollups or upon major upstream PR integration.
  │   - Target: Extended compatibility testing, multi-system smoke tests.
  │   - Stability: High confidence.
  │
  └── 3. STABLE / TAGGED
      - Frequency: Monthly or synchronized with official upstream OpenCore releases.
      - Target: Production boot environments.
      - Stability: Maximum stability with full SBOM, SLSA provenance, and signed digests.
```

---

## 2. Versioning Scheme

AegisBoot employs a Semantic Versioning 2.0.0 scheme with explicit upstream traceability metadata:

```
v<UPSTREAM_VERSION>-aegis.<DISTRO_REVISION>+<UPSTREAM_COMMIT_SHA>
```

- `UPSTREAM_VERSION`: Canonical OpenCore version (e.g. `1.0.8`) parsed from `Include/Acidanthera/Library/OcMainLib.h`.
- `DISTRO_REVISION`: Integer incremented for downstream packaging, CI, or toolchain updates applied against the same upstream version.
- `UPSTREAM_COMMIT_SHA`: 7-character short SHA of the upstream commit on which this build is based.

**Examples:**
- `v1.0.8-aegis.1+170b538`
- `v1.0.8-aegis.2+558a2fd`
- `v1.0.9-aegis.1+a1b2c3d`

---

## 3. Release Artifacts & Supply-Chain Metadata

Every official AegisBoot release produces a standard set of cryptographic artifacts:

| Artifact | Format | Description |
|---|---|---|
| `AegisBoot-<ver>-RELEASE.zip` | ZIP | Production OpenCore EFI binaries with optimizations and disabled debug logs. |
| `AegisBoot-<ver>-DEBUG.zip` | ZIP | Diagnostics OpenCore EFI binaries with full serial and screen logging. |
| `AegisBoot-<ver>-NOOPT.zip` | ZIP | Unoptimized OpenCore EFI binaries for deep kernel/UEFI debugging. |
| `distro-version.json` | JSON | Machine-readable version metadata, commit SHAs, build timestamps, and toolchain pins. |
| `OpenCorePkg-<ver>-cyclonedx.json`| JSON | CycloneDX Software Bill of Materials (SBOM) listing all components. |
| `provenance.json` | JSON | SLSA Level 3 Provenance statement linking build to source repository commit. |
| `SHA256SUMS.txt` | Text | SHA-256 digests of all release ZIP archives. |
| `SHA512SUMS.txt` | Text | SHA-512 digests of all release ZIP archives. |

---

## 4. Rollback and Deprecation Procedure

If a critical defect or boot failure is identified in a published release:
1. **Deprecation Notice:** The GitHub Release is immediately updated with a prominent `[CRITICAL WARNING / YANKED]` disclaimer in the title and release body.
2. **Rollback Release:** An emergency point release based on the previous known-good commit is cut within < 15 minutes.
3. **Artifact Retention:** Defective binaries are retained for post-mortem forensic analysis but flagged as untrusted.
