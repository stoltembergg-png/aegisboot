# AegisBoot — Build Instructions

This guide provides reproducible build instructions for compiling AegisBoot across Linux, macOS, and Windows.

---

## 1. Prerequisites & Toolchain Dependencies

### Common Requirements:
- `git` (2.30+)
- `python3` (3.10+)
- `nasm` (2.16.03 recommended)
- `iasl` / ACPICA compiler
- `zip` / `unzip`

---

## 2. Linux Build (Recommended / Docker & Native)

### Option A: Using Docker (Reproducible & Isolated)
The easiest and most reproducible way to build AegisBoot on Linux:

```bash
# Build OpenDuet and OpenCore using pinned Docker environments
docker compose run build-duet
docker compose run build-oc

# Build PDF documentation
docker compose run build-docs
```

All compiled binaries will be output into the `Binaries/` directory.

### Option B: Native Linux Build
1. Install system prerequisites (Ubuntu 22.04 / 24.04):
   ```bash
   sudo apt update
   sudo apt install -y build-essential nasm iasl uuid-dev libssl-dev libx11-dev libxext-dev gcc-multilib git curl zip python3
   ```
2. Run our idempotent build orchestrator:
   ```bash
   ./scripts/build-distro.sh --target RELEASE --arch X64
   ```

---

## 3. macOS Build (Xcode & Homebrew)

1. Install Xcode and Command Line Tools:
   ```bash
   xcode-select --install
   ```
2. Install build dependencies via Homebrew:
   ```bash
   brew tap FiloSottile/homebrew-musl-cross
   brew install FiloSottile/musl-cross/musl-cross mingw-w64 nasm
   ```
3. Run the bootstrap and build tools:
   ```bash
   ./build_duet.tool
   ./build_oc.tool
   ```

---

## 4. Windows Build (VS2022 / WSL2)

### Using WSL2 (Ubuntu 24.04):
Follow the Linux instructions inside your WSL2 terminal.

### Using Visual Studio 2022:
1. Ensure the **Desktop development with C++** workload is installed.
2. Install NASM and iASL and add them to your system `PATH`.
3. Set environment variables:
   ```cmd
   set TOOLCHAINS=VS2022
   set TARGETS=RELEASE
   set ARCHS=X64
   ```
4. Execute the build scripts via a Bash shell (Git Bash or MSYS2):
   ```bash
   ./build_oc.tool
   ```

---

## 5. Artifact Verification & Metadata

After compilation, verify generated artifacts and extract downstream provenance:
```bash
./scripts/verify-distro.sh
python3 ./scripts/generate-version-metadata.py --output Binaries/distro-version.json
```
