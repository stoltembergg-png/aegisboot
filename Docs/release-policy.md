# Release Policy

> **Policy Version:** 1.0.0
> **Status:** Active
> **Last Updated:** 2026-08-19

---

## 1. Release Philosophy

AegisBoot releases are **downstream continuous distributions** that track upstream OpenCorePkg commits. Every release is fully traceable to an upstream SHA and passes 100% of CI validation gates.

---

## 2. Release Triggers

A downstream release is created when:

1. **Upstream Sync Merge:** A `sync:upstream` PR passes all CI gates and merges to `main`
2. **Impact Classification:** The merged sync PR is labeled with `impact:patch`, `impact:minor`, `impact:major`, or `impact:critical`
3. **Gate Completion:** All validation gates pass (build, static analysis, QEMU boot test, patch verification, security scans)

**No release is created for:**
- `impact:none` (documentation only)
- `impact:infrastructure` (CI/CD/tooling only)

---

## 3. Versioning Scheme

All AegisBoot releases follow this SemVer-extended format:

```
v<upstream_version>-aegis.<distro_revision>+<upstream_sha_short>
```

| Component | Source | Example |
|---|---|---|
| `v<upstream_version>` | Extracted from `OcMainLib.h` (`OPEN_CORE_VERSION`) | `v1.0.8` |
| `aegis.<distro_revision>` | Incremented per downstream release for same upstream version | `aegis.1`, `aegis.2` |
| `<upstream_sha_short>` | First 7 chars of upstream commit SHA | `170b538` |

**Examples:**
- `v1.0.8-aegis.1+170b538` — First downstream release of OpenCore 1.0.8
- `v1.0.8-aegis.2+170b538` — Second downstream release (same upstream, new CI fix)
- `v1.0.9-aegis.1+abc1234` — First downstream release of OpenCore 1.0.9

---

## 4. Release Channels

| Channel | Tag Pattern | Stability | Use Case |
|---|---|---|---|
| `edge` | `v*-aegis.*-edge` | Nightly / Experimental | Developers, CI testing |
| `staging` | `v*-aegis.*-staging` | Pre-release / Canary | Early adopters, validation |
| `stable` | `v*-aegis.*` | Production | General distribution |

---

## 5. Release Artifacts

Every stable release **must** include:

| Artifact | Format | Purpose |
|---|---|---|
| `OpenCore-<version>-RELEASE.zip` | Binary ZIP | Production binaries (RELEASE target) |
| `OpenCore-<version>-DEBUG.zip` | Binary ZIP | Debug binaries (DEBUG target) |
| `OpenCore-<version>-NOOPT.zip` | Binary ZIP | No-optimization binaries |
| `distro-version.json` | JSON | Machine-readable version metadata |
| `SHA256SUMS.txt` | Text | SHA-256 checksums |
| `SHA512SUMS.txt` | Text | SHA-512 checksums |
| `OpenCorePkg-cyclonedx.json` | JSON | CycloneDX 1.5 SBOM |
| `provenance.json` | JSON | SLSA Level 3 provenance (when available) |

---

## 6. Release Process

### Automated (Standard)

1. Sync PR merges with qualifying impact label
2. CI pipeline runs full validation matrix
3. Tag is pushed: `v<upstream_version>-aegis.<N>+<sha>`
4. `.github/workflows/release.yml` triggers on tag
5. Build, package, verify, SBOM, provenance
6. GitHub Release published automatically

### Manual (Emergency / Hotfix)

```bash
# From main branch at desired commit
git tag v1.0.8-aegis.3+170b538
git push origin v1.0.8-aegis.3+170b538
```

---

## 7. Rollback / Yank Policy

If a release is found to have critical defects:

1. **Yank:** Mark release as "Pre-release" and add `[YANKED]` to title
2. **Redeploy:** Push a new downstream revision (e.g., `v1.0.8-aegis.4+170b538`) with fix
3. **Document:** Add incident note to CHANGELOG_DISTRO.md

---

## 8. Release Notes

Release notes are auto-generated from:
- Upstream commit log since last downstream release
- Local CI/CD changes (from `CHANGELOG_DISTRO.md`)
- Patch stack changes
- Impact classification labels

Maintainers may edit before publishing.

---

## 9. Cryptographic Signing (Future)

When implemented:
- Releases signed with maintainer GPG key
- Signatures published alongside artifacts
- Verification instructions in release description

---

## 10. Compliance Checklist

Before any release is published:

- [ ] All CI gates green (100%)
- [ ] Upstream SHA recorded in `distro-version.json`
- [ ] Patch stack verified clean
- [ ] SHA256/SHA512 checksums generated
- [ ] CycloneDX SBOM generated
- [ ] Version tag follows exact format
- [ ] CHANGELOG_DISTRO.md updated
- [ ] Release channel label applied