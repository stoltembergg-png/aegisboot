# Pinned Toolchains & Reproducible Build Environment

This directory defines the exact toolchain pins and cryptographic hashes required to produce bit-for-bit reproducible builds of AegisBoot.

---

## 1. Toolchain Manifest (`toolchain-pins.json`)

The [`toolchain-pins.json`](toolchain-pins.json) manifest specifies:
- **Compilers:** Pinned LLVM/Clang (21.x), GCC (13.x), Xcode (15/16).
- **Assemblers & ACPI:** NASM 2.16.03, ACPICA iASL 20240827.
- **Base EDK II:** `edk2-stable202511` with Acidanthera `ocbuild` ci-bootstrap.
- **GitHub Actions:** All external actions pinned strictly to 40-hex-character commit SHAs.

---

## 2. Toolchain Audit & Update Procedure

When updating any compiler or toolchain component:
1. Open a PR with the title: `build(toolchain): update <component> to <version>`.
2. Update [`toolchain-pins.json`](toolchain-pins.json) with the new version and SHA-256 hash.
3. Update `Dockerfiles/oc-dev/Dockerfile` if applicable.
4. Ensure all CI build matrix jobs pass on Linux, macOS, and Windows.
5. Run the QEMU/OVMF boot regression test to confirm firmware compatibility.
