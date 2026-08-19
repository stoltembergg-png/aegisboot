# Build Instructions

> **Policy Version:** 1.0.0
> **Status:** Active
> **Last Updated:** 2026-08-19

---

## 1. Prerequisites

### 1.1 System Requirements

| OS | Minimum Spec | Recommended |
|---|---|---|
| Linux | Ubuntu 24.04 LTS, 8 GB RAM, 50 GB disk | 16 GB RAM, NVMe SSD |
| macOS | macOS 14+ (Sonoma), Xcode 15+ | macOS 15+, Xcode 16 |
| Windows | Windows 11, 16 GB RAM, WSL2 optional | Native VS2022 + MinGW |

### 1.2 Required Tools (Linux)

```bash
# Ubuntu 24.04
sudo apt-get update
sudo apt-get install -y \
  build-essential git python3 python3-venv \
  nasm iasl uuid-dev libssl-dev gcc-multilib \
  qemu-system-x86 ovmf \
  docker.io docker-compose-plugin
```

### 1.3 Required Tools (macOS)

```bash
# Homebrew
brew install git python3 nasm iasl qemu
brew tap FiloSottile/homebrew-musl-cross
brew install FiloSottile/musl-cross/musl-cross mingw-w64

# Xcode Command Line Tools
xcode-select --install
```

### 1.4 Required Tools (Windows)

```powershell
# Chocolatey (Admin PowerShell)
choco install git python make nasm zip iasl -y
choco install llvm -y  # For clang

# Visual Studio 2022 Build Tools
# Install: "C++ build tools", "Windows 10/11 SDK"
```

---

## 2. Repository Setup

### 2.1 Clone with Submodules

```bash
git clone https://github.com/aegisboot/aegisboot.git
cd aegisboot

# Verify remotes
git remote -v
# origin  -> https://github.com/acidanthera/OpenCorePkg.git (UPSTREAM - fetch only)
# fork    -> https://github.com/aegisboot/aegisboot.git   (OUR FORK - push)
```

### 2.2 Configure Remotes (Critical)

```bash
# Ensure origin points to UPSTREAM
git remote set-url origin https://github.com/acidanthera/OpenCorePkg.git

# Add fork remote for pushing
git remote add fork https://github.com/aegisboot/aegisboot.git

# Verify
git remote -v
```

---

## 3. Quick Build (Docker - Recommended for Linux)

### 3.1 Build All Targets

```bash
# Apply Docker AppArmor settings (required once)
src=$(curl -LfsS https://raw.githubusercontent.com/acidanthera/ocbuild/master/docker-apparmor.sh) && eval "$src"

# Build OpenDuet
docker compose run --rm build-duet

# Build OpenCore (all toolchains)
docker compose run --rm build-oc

# Artifacts in ./Binaries/
ls -la Binaries/
```

### 3.2 Build Specific Toolchain

```bash
# Linux CLANGPDB
TOOLCHAINS=CLANGPDB docker compose run --rm build-oc

# Linux GCC
TOOLCHAINS=GCC docker compose run --rm build-oc

# Linux CLANGDWARF
TOOLCHAINS=CLANGDWARF docker compose run --rm build-oc

# Docs
docker compose run --rm build-docs
```

---

## 4. Native Build (Linux / macOS / Windows)

### 4.1 Bootstrap

```bash
# Linux / macOS
src=$(curl -LfsS https://raw.githubusercontent.com/acidanthera/ocbuild/master/ci-bootstrap.sh) && eval "$src"

# Windows (Git Bash)
src=$(curl -LfsS https://raw.githubusercontent.com/acidanthera/ocbuild/master/ci-bootstrap.sh) && eval "$src"
```

### 4.2 Build Commands

```bash
# Build OpenDuet
./build_duet.tool

# Build OpenCore (RELEASE, DEBUG, NOOPT)
./build_oc.tool

# Build specific target
./build_oc.tool RELEASE
./build_oc.tool DEBUG
./build_oc.tool NOOPT
```

### 4.3 Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `TARGET` | Build target | `RELEASE` |
| `TOOLCHAINS` | Toolchain selector | Auto-detect |
| `PROJECT_TYPE` | Project type | `UEFI` |
| `WERROR` | Treat warnings as errors | `1` |
| `FORCE_INSTALL` | Force tool install | `1` |
| `HAS_OPENSSL_BUILD` | Build OpenSSL | `1` (Linux/macOS) |

---

## 5. CI/CD Pipeline (GitHub Actions)

### 5.1 Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `sync.yml` | Schedule (15m), dispatch | Upstream sync |
| `build.yml` | Push, PR, release | Multi-platform build |
| `analyze.yml` | Push, PR, release | Static analysis |
| `ci.yml` | Push, PR | Validation gates |
| `release.yml` | Tag push (`v*`) | Release packaging |

### 5.2 Running Locally (act)

```bash
# Install act
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run build workflow
act push -W .github/workflows/build.yml -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-24.04

# Run CI gates
act pull_request -W .github/workflows/ci.yml
```

---

## 6. Toolchain Pins

All builds use pinned toolchains from `toolchains/toolchain-pins.json`:

```json
{
  "compilers": {
    "llvm_clang": { "version": "21.0.0" },
    "gcc": { "version": "13.2.0" },
    "xcode": { "min_version": "15.0", "recommended": "16.0" }
  },
  "assemblers_and_compilers": {
    "nasm": { "version": "2.16.03", "sha256": "..." },
    "iasl": { "version": "20240827", "sha256": "..." }
  }
}
```

**Never** override toolchain versions in CI. Local overrides allowed for development only.

---

## 7. Build Artifacts

### 7.1 Output Structure

```
Binaries/
├── OpenCore-1.0.8-RELEASE.zip
├── OpenCore-1.0.8-DEBUG.zip
├── OpenCore-1.0.8-NOOPT.zip
├── OpenDuetPkg-1.0.8-RELEASE.zip
├── build-manifest.json        # Per-toolchain manifest
├── distro-version.json        # Version metadata
├── SHA256SUMS.txt
├── SHA512SUMS.txt
└── OpenCorePkg-cyclonedx.json # SBOM
```

### 7.2 Build Manifest Schema

```json
{
  "build": {
    "timestamp": "2026-08-19T12:00:00Z",
    "target": "RELEASE",
    "arch": "X64",
    "toolchain": "CLANGPDB",
    "commit_sha": "170b538b...",
    "commit_sha_short": "170b538"
  },
  "artifacts": [
    { "name": "OpenCore-1.0.8-RELEASE.zip", "sha256": "...", "size": 1234567 }
  ]
}
```

---

## 8. Verification

### 8.1 Validate Build

```bash
# Run verification script
./scripts/verify-distro.sh

# Manual checksum verification
cd Binaries
sha256sum -c SHA256SUMS.txt
sha512sum -c SHA512SUMS.txt
```

### 8.2 Validate Config.plist

```bash
# Using ocvalidate from build
./Binaries/ocvalidate Docs/Sample.plist
./Binaries/ocvalidate Docs/SampleCustom.plist
```

### 8.3 QEMU Boot Test

```bash
# Install QEMU + OVMF
sudo apt-get install -y qemu-system-x86 ovmf

# Run boot test
python tests/test_qemu_boot.py
```

---

## 9. Development Workflow

### 9.1 Local Patch Development

```bash
# 1. Create feature branch
git checkout -b feat/my-patch main

# 2. Make changes to OpenCore source (in UDK/ after bootstrap)

# 3. Generate patch
git diff UDK/ > Patches/000X-my-patch.patch

# 4. Add metadata headers to patch file
# (Upstream-Status, Upstream-Issue, Signed-off-by)

# 5. Test patch application
./scripts/apply-patches.sh --check

# 6. Run full CI locally (act or push to fork)
```

### 9.2 Script Development

```bash
# All scripts in scripts/ must:
# - Use #!/usr/bin/env bash with set -euo pipefail
# - Pass shellcheck: shellcheck -x scripts/*.sh
# - Be idempotent (safe to run multiple times)
# - Have --check mode for validation

# Test
./scripts/check-env.sh
python -m unittest discover -s tests
```

---

## 10. Reproducible Builds

### 10.1 Drift Detection

```bash
# Run dual-pass build comparison
./scripts/check-build-drift.sh

# Output: build-drift-report.json
# Exit code: 0 = reproducible, 1 = drift detected
```

### 10.2 Requirements for Reproducibility

- Pinned toolchains (`toolchain-pins.json`)
- Pinned Docker base images (by digest)
- Fixed timestamps (via `SOURCE_DATE_EPOCH`)
- Deterministic file ordering

---

## 11. Clean Build

```bash
# Remove all build artifacts
rm -rf Binaries/ UDK/ Build/ Conf/

# Clean Docker
docker compose down -v
docker system prune -f

# Fresh build
./build_duet.tool && ./build_oc.tool
```

---

## 12. Common Build Targets

| Target | Command | Output |
|---|---|---|
| OpenDuet | `./build_duet.tool` | `Binaries/OpenDuetPkg-*.zip` |
| OpenCore RELEASE | `./build_oc.tool RELEASE` | `Binaries/OpenCore-*-RELEASE.zip` |
| OpenCore DEBUG | `./build_oc.tool DEBUG` | `Binaries/OpenCore-*-DEBUG.zip` |
| OpenCore NOOPT | `./build_oc.tool NOOPT` | `Binaries/OpenCore-*-NOOPT.zip` |
| Docs | `docker compose run build-docs` | `Binaries/Docs-*.zip` |

---

## 13. Environment Validation

```bash
# Check all prerequisites
./scripts/check-env.sh

# Expected output:
# [OK] git: 2.45.0
# [OK] python3: 3.12.3
# [OK] nasm: 2.16.03
# [OK] iasl: 20240827
# [OK] docker: 27.0.0
# [OK] Toolchain pins: toolchains/toolchain-pins.json
# [OK] Patch stack: 5 patches verified
# [OK] Environment ready for AegisBoot builds
```

---

## 14. Troubleshooting Quick Reference

| Problem | Solution |
|---|---|
| `git: command not found` | Install git |
| `nasm: not found` | Install nasm |
| Docker permission denied | Add user to docker group |
| Build fails in UDK/ | `rm -rf UDK/ && ./build_oc.tool` |
| Patch apply fails | Check `scripts/apply-patches.sh --check` |
| QEMU boot hangs | Increase timeout, check OVMF path |

---

## 15. References

- [EDK II Build Specification](https://github.com/tianocore/edk2/blob/master/Conf/tools_def.txt)
- [Acidanthera ocbuild](https://github.com/acidanthera/ocbuild)
- [OpenCorePkg Build Instructions](https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/BUILD.md)
- [AegisBoot Toolchain Pins](toolchains/toolchain-pins.json)

---

## 16. Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-08-19 | Initial build instructions |