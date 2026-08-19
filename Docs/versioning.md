# AegisBoot — Versioning & Metadata Specification

---

## 1. Specification Overview

Every build and release of AegisBoot is uniquely identified by structured version metadata that provides unambiguous cryptographic traceability to upstream OpenCorePkg.

### Version Format
```
v<UPSTREAM_MAJOR>.<UPSTREAM_MINOR>.<UPSTREAM_PATCH>-aegis.<DISTRO_REV>+<UPSTREAM_SHA>
```

- `UPSTREAM_MAJOR.UPSTREAM_MINOR.UPSTREAM_PATCH`: The base OpenCore version string extracted from `Include/Acidanthera/Library/OcMainLib.h` (macro `OPEN_CORE_VERSION`).
- `aegis.<DISTRO_REV>`: Downstream distribution revision index.
- `+<UPSTREAM_SHA>`: The short 7-character hexadecimal SHA of the upstream git commit.

---

## 2. Machine-Readable Metadata Schema (`distro-version.json`)

The script `scripts/generate-version-metadata.py` produces a JSON manifest conforming to this schema:

```json
{
  "$schema": "https://aegisboot.dev/schema/distro-version.v1.json",
  "distribution": {
    "name": "AegisBoot",
    "description": "Continuous Integration Downstream Distribution of OpenCorePkg",
    "version": "1.0.8-aegis.1+170b538",
    "distro_revision": 1,
    "build_timestamp": "2026-08-19T04:49:41Z",
    "channel": "stable"
  },
  "upstream": {
    "repository": "https://github.com/acidanthera/OpenCorePkg.git",
    "branch": "master",
    "version": "1.0.8",
    "commit_sha": "170b538b7e28b8cf44eb896b7978f8bc01d12345",
    "commit_sha_short": "170b538",
    "commit_date": "2026-08-19T00:00:00Z"
  },
  "toolchain_pins": {
    "nasm": "2.16.03",
    "iasl": "20240827",
    "llvm_version": "21",
    "edk2_rc": "edk2-stable202511"
  },
  "patches": [
    {
      "file": "Patches/0001-MdeModulePkg-SataControllerDxe-Add-support-for-drive.patch",
      "status": "applied",
      "upstream_status": "submitted"
    }
  ]
}
```
