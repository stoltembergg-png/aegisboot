# AegisBoot — Branding, Trademark & Naming Policy

---

## 1. Legal Disclaimer & Independence

> [!IMPORTANT]
> **AegisBoot is an independent downstream distribution and automated continuous integration system.**
> **It is NOT an official release, product, endorsement, or representation of Acidanthera or Apple Inc.**

- **OpenCore** is an open-source UEFI bootloader developed and maintained by the [Acidanthera team](https://github.com/acidanthera).
- **Apple, macOS, Mac, MacBook, Mac Pro, and iMac** are trademarks of Apple Inc., registered in the U.S. and other countries.
- AegisBoot is maintained independently by downstream contributors to provide automated CI/CD builds, supply-chain validation, and accelerated downstream release cycles.

---

## 2. Naming Guidelines for Downstream Releases & Artifacts

To prevent any confusion between official upstream Acidanthera releases and AegisBoot downstream builds, all distribution assets must adhere strictly to these naming guidelines:

### 2.1 Release Titles & Tags
- Downstream release tags **must** include the downstream identifier:
  - Format: `v<upstream_version>-aegis.<distro_revision>+<upstream_sha_short>`
  - Example: `v1.0.8-aegis.1+170b538`
- Release names on GitHub or distribution mirrors must clearly display the downstream context:
  - Example: `AegisBoot v1.0.8-aegis.1 (Downstream CI Distribution of OpenCorePkg 1.0.8)`

### 2.2 Binary Packages & Filenames
- Binary ZIP bundles produced by downstream pipelines must include the distribution moniker:
  - Example: `AegisBoot-1.0.8-RELEASE.zip`, `AegisBoot-1.0.8-DEBUG.zip`
  - Or contain full version metadata manifests (`distro-version.json`, `SHA256SUMS.txt`).

### 2.3 Prohibited Claims
Under no circumstances may maintainers, contributors, or third-party redistributors:
- Describe AegisBoot builds as *"Official OpenCore Releases"*.
- Represent AegisBoot maintainers as official members or spokespersons of the Acidanthera team.
- Claim direct support or warranty from the upstream Acidanthera team for AegisBoot downstream modifications or build pipeline artifacts.

---

## 3. Support & Bug Reporting Rules

1. **Issues related to AegisBoot CI/CD, automation scripts, Docker environments, or downstream packaging** must be filed directly in the [AegisBoot Issue Tracker](https://github.com/aegisboot/aegisboot/issues).
2. **Do NOT open issues on the upstream Acidanthera repository for downstream packaging errors, custom CI failures, or unsupported downstream configurations.**
3. **Core OpenCore bugs:** If a reproducible bug in core OpenCore C codebase is verified against vanilla upstream OpenCore master, follow the upstream [Acidanthera contribution guidelines](https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/FORUMS.md) respectfully.
