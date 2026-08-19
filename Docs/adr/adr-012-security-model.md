# ADR-012: Security Threat Model

## Status
Accepted

## Context
The AegisBoot supply chain and CI/CD pipeline must be hardened against common attack vectors while maintaining automation.

## Decision
**Threat Model & Mitigations:**

| Threat | Likelihood | Impact | Mitigation |
|--------|------------|--------|------------|
| Malicious upstream commit | Low | Critical | Full validation pipeline before merge; no auto-merge without gates |
| Corrupted artifacts | Low | High | SHA256/SHA512 checksums on all releases; verification in `verify-distro.sh` |
| Secrets in repository | Low | Critical | `gitleaks` + secret scanning in CI; `persist-credentials: false` on all checkouts |
| Unauthorized merge | Low | Critical | Branch protection: required checks, no direct push, no force push |
| Supply chain attack | Low | High | CycloneDX SBOM + SLSA provenance on every release; pinned toolchains |
| Conflicts masked | Medium | High | Patch verification blocks sync; no force-push to master |
| Token exfiltration | Low | Critical | `GITHUB_TOKEN` minimal scope; `persist-credentials: false`; no `pull_request_target` |
| CI injection | Low | High | No `${{ github.event.* }}` in `run:`; all inputs via `env:`; pinned actions |

**CI/CD Hardening Rules (enforced by `scripts/validate_workflows.py`):**
1. All workflows declare `permissions:` explicitly (least privilege)
2. External actions pinned to 40-char commit SHA
3. `actions/checkout` has `persist-credentials: false`
4. No `pull_request_target` trigger anywhere
5. No `${{ github.event.* }}` interpolated in `run:` blocks
6. Every job has `timeout-minutes`
6. No `continue-on-error: true` on validation gates
7. Concurrency groups defined to cancel stale runs

**Secrets Management:**
- `GITHUB_TOKEN` (auto-provided) only — no PATs in workflows
- Release signing keys: future work (GPG/Sigstore)
- No secrets in repository (enforced by secret scanning)

**Dependency Security:**
- Toolchain versions pinned in `toolchains/toolchain-pins.json`
- Actions pinned to commit SHA
- Docker base images pinned by digest (in docker-compose)
- `Dependabot` alerts enabled (GitHub native)

## Consequences
**Positive:**
- Defense in depth across supply chain
- Automated enforcement of security rules
- Minimal blast radius from compromised token
- Audit trail for all security-relevant events

**Negative:**
- More restrictive CI (no `pull_request_target`, strict permissions)
- Requires diligent pin maintenance
- Manual intervention needed for action updates

## Implementation References
- `scripts/validate_workflows.py` - 10 security rules
- `.github/workflows/*.yml` - All workflows compliant
- `toolchains/toolchain-pins.json` - Pinned dependencies
- `scripts/verify-distro.sh` - Artifact verification
- `SECURITY.md` - Security policy and reporting