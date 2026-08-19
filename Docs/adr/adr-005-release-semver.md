# ADR-005: Release SemVer for Fork

## Status
Accepted

## Context
The fork needs its own versioning scheme that:
- Tracks upstream version precisely
- Allows more frequent releases than upstream
- Is sortable and SemVer-compatible
- Provides exact traceability to upstream commit

## Decision
**Version Format:** `v<upstream_version>-aegis.<distro_revision>+<upstream_sha_short>`

**Components:**
| Component | Source | Example |
|-----------|--------|---------|
| `v<upstream_version>` | `OcMainLib.h` → `OPEN_CORE_VERSION` | `v1.0.8` |
| `aegis.<distro_revision>` | Incremented per downstream release for same upstream version | `aegis.1`, `aegis.2` |
| `<upstream_sha_short>` | First 7 chars of upstream commit SHA | `170b538` |

**Examples:**
- `v1.0.8-aegis.1+170b538` — First downstream release of OpenCore 1.0.8
- `v1.0.8-aegis.2+170b538` — Second downstream release (same upstream, CI fix)
- `v1.0.9-aegis.1+abc1234` — First downstream release of OpenCore 1.0.9

**Release Channels:**
| Channel | Tag Pattern | Stability |
|---------|-------------|-----------|
| `edge` | `v*-aegis.*-edge` | Nightly/Experimental |
| `staging` | `v*-aegis.*-staging` | Pre-release/Canary |
| `stable` | `v*-aegis.*` | Production |

**Release Artifacts (every stable release):**
- `OpenCore-<version>-RELEASE.zip`
- `OpenCore-<version>-DEBUG.zip`
- `OpenCore-<version>-NOOPT.zip`
- `distro-version.json` (machine-readable metadata)
- `SHA256SUMS.txt`, `SHA512SUMS.txt`
- `OpenCorePkg-cyclonedx.json` (CycloneDX SBOM)
- `provenance.json` (SLSA Level 3 provenance)

## Consequences
**Positive:**
- Exact traceability: every release → upstream SHA → fork SHA
- More frequent releases than upstream (when warranted)
- SemVer compatible (sortable, parsable)
- Clear channel separation

**Negative:**
- Long version strings
- Requires tooling to extract components

## Implementation References
- `docs/release-policy.md` - Full release policy
- `scripts/generate-version-metadata.py` - Generates `distro-version.json`
- `.github/workflows/release-trigger.yml` - Generates tag, pushes to fork
- `.github/workflows/release.yml` - Builds artifacts, generates SBOM/provenance