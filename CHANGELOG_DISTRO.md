# AegisBoot Downstream Distribution Changelog

All notable changes, downstream releases, CI/CD enhancements, and synchronized upstream commits to the **AegisBoot** distribution of OpenCorePkg are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) extended with upstream commit provenance metadata: `v<upstream_version>-aegis.<distro_revision>+<upstream_sha>`.

For upstream OpenCore release notes and component changes, please refer directly to the canonical [Upstream Changelog](file:///c:/Users/Gabriel/Desktop/aegisboot/Changelog.md).

---

## [Unreleased]

### Added
- Comprehensive automated downstream continuous distribution infrastructure.
- Automated 15-minute upstream synchronization workflow (`.github/workflows/sync.yml`).
- Rigorous PR validation matrix with 10 strict gate jobs (`.github/workflows/ci.yml`).
- Automated QEMU/OVMF UEFI boot regression testing.
- Automated CycloneDX SBOM generation and SHA-256/SHA-512 checksum manifests.
- SLSA Level 3 provenance release workflow (`.github/workflows/release.yml`).
- Idempotent administration scripts in `scripts/` (`check-env.sh`, `sync-upstream.sh`, `apply-patches.sh`, `build-distro.sh`, `verify-distro.sh`, `generate-version-metadata.py`, `sync-labels.py`, `health-check.sh`).
- Automated workflow security integrity test suite in `tests/test_workflow_integrity.py`.
- Formal governance, security, trademark branding, local patch, and upstream synchronization policies.
- Pinned toolchain specifications (`toolchains/toolchain-pins.json`).

### Upstream Tracking Baseline
- Synced with upstream `acidanthera/OpenCorePkg` @ `170b538` (OpenCore 1.0.8).
