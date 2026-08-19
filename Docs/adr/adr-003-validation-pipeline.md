# ADR-003: Validation Pipeline Architecture

## Status
Accepted

## Context
Every upstream sync and local change must pass rigorous validation before merging to `master`. The pipeline must catch build failures, regressions, security issues, and policy violations.

## Decision
**10-Gate Validation Pipeline (`.github/workflows/ci.yml`):**

| Gate | Job | Purpose | Required |
|------|-----|---------|----------|
| 1 | `workflow-integrity` | Workflow security hardening (pinned actions, no `pull_request_target`, permissions, etc.) | ✅ |
| 2 | `formatting` | Python/shell syntax, py_compile, bash -n | ✅ |
| 3 | `static-checks` | ShellCheck, plist XML validation | ✅ |
| 4 | `license-and-secrets` | Secret scanning (ghp_, private keys), license file check | ✅ |
| 5 | `dependency-and-toolchain` | Toolchain pins JSON schema validation | ✅ |
| 6 | `patch-stack-verification` | Local patches apply cleanly to upstream | ✅ |
| 7 | `policy-and-metadata-tests` | Distribution policies, version metadata, patch stack unit tests | ✅ |
| 8 | `unit-and-integration-tests` | ACPIe, Kext injection test suites | ✅ |
| 9 | `qemu-boot-test` | OVMF UEFI boot regression test | ✅ |
| 10 | `analyze` (separate workflow) | ShellCheck, Prospector, Coverity, doc lint | ✅ |

**Build Validation (`.github/workflows/build.yml`):**
- 5 platform builds: Linux CLANGPDB, CLANGDWARF, GCC; macOS XCODE5; Windows VS2022
- All must pass for release

**Multi-platform CI:**
- All gates run on `ubuntu-24.04` except macOS/Windows build jobs
- QEMU/OVMF boot test on Linux runner

## Consequences
**Positive:**
- Comprehensive coverage: security, build, test, policy
- Fast feedback: gates run in parallel where possible
- No merge without full validation
- Reproducible builds via pinned toolchains

**Negative:**
- Pipeline duration ~20-30 minutes
- Resource intensive (5 build platforms + QEMU)
- QEMU boot test adds ~5-10 min

## Implementation References
- `.github/workflows/ci.yml` - 10 gates
- `.github/workflows/build.yml` - 5 platform builds
- `.github/workflows/analyze.yml` - Static analysis
- `.github/workflows/sync.yml` - Triggers CI on sync PRs