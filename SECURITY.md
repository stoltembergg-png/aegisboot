# Security Policy & Vulnerability Management

---

## 1. Scope & Reporting Channels

AegisBoot takes the security of UEFI boot environments and supply-chain automation seriously. We operate a dual-path vulnerability response process:

```
┌─────────────────────────────────────────────────────────────┐
│                 VULNERABILITY REPORT ROUTING                │
└──────────────────────────────┬──────────────────────────────┘
                               │
               Is the issue in core OpenCore C code?
                               │
                ┌──────────────┴──────────────┐
               YES                            NO (CI / Packaging / Scripts)
                ▼                             ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ UPSTREAM ACIDANTHERA CHANNEL │ │   AEGISBOOT SECURITY TEAM    │
│ Follow Acidanthera security  │ │ File GitHub Private Advisory │
│ guidelines / contact email.  │ │ or email: security@aegis.dev │
└──────────────────────────────┘ └──────────────────────────────┘
```

### 1.1 Reporting Core OpenCore Vulnerabilities
- If you have discovered a vulnerability in core OpenCore UEFI drivers, memory management, vault verification, crypto routines, or kernel patching:
- Please report it confidentially to the upstream **Acidanthera security team** following their established reporting channels.

### 1.2 Reporting AegisBoot Downstream / CI / Supply-Chain Vulnerabilities
- If you have identified an issue in our GitHub Actions workflows, secret handling, distribution packaging, script injection, SBOM generation, or Docker containers:
- Please submit a **[GitHub Private Security Advisory](https://github.com/aegisboot/aegisboot/security/advisories/new)**.
- **Do not open public GitHub issues for undisclosed security vulnerabilities.**

---

## 2. CI/CD Security Baseline & Hardening Rules

All automation pipelines and workflows in AegisBoot enforce the following security invariants:

1. **Least Privilege Permissions:**
   - All workflows specify top-level `permissions: contents: read` by default.
   - Elevated permissions (`contents: write`) are strictly restricted to tag-triggered release workflows.
2. **Pinned External Actions:**
   - External GitHub Actions must be pinned to full 40-hex-character commit SHAs (e.g. `actions/checkout@b4ffde5c... # v4.1.1`).
   - Action versions are audited periodically against official repository releases.
3. **Persist-Credentials Disabled:**
   - All `actions/checkout` steps explicitly pass `persist-credentials: false` to prevent child steps from accessing repository tokens.
4. **Script Injection Mitigation:**
   - GitHub context expressions (`${{ github.event... }}`) are never directly interpolated into inline `run:` shell blocks.
   - All inputs are safely mediated via declared `env:` variables.
5. **No `pull_request_target`:**
   - The use of `pull_request_target` is strictly prohibited across the repository to prevent untrusted PR code from executing in a privileged context.
6. **Automated Secret Scanning:**
   - Gitleaks and automated secret scanning run continuously on all PRs and pushes to block accidental token leaks.
7. **Supply Chain Integrity:**
   - Every official release artifact is accompanied by:
     - Cryptographic SHA-256 and SHA-512 checksum manifests (`SHA256SUMS.txt`, `SHA512SUMS.txt`).
     - Machine-readable CycloneDX Software Bill of Materials (SBOM).
     - SLSA (Supply-chain Levels for Software Artifacts) Level 3 Provenance statement.

---

## 3. Vulnerability Response Timeline & SLA

| Severity | Definition | Initial Response | Resolution Target |
|---|---|---|---|
| **Critical (P0)** | Remote code execution, bootloader bypass, CI token exfiltration | < 12 hours | < 48 hours |
| **High (P1)** | Security regression, script injection, broken cryptographic verification | < 24 hours | < 5 days |
| **Medium (P2)** | Local privilege issues, dependency vulnerability without exploit | < 48 hours | < 14 days |
| **Low (P3)** | Hardening improvements, static analysis advisory | < 7 days | Next release cycle |
