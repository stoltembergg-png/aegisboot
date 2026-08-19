# Contributing to AegisBoot

Thank you for your interest in contributing to **AegisBoot**! We welcome contributions to our automation infrastructure, test suites, packaging pipelines, and technical documentation.

---

## 1. Upstream-First Philosophy

> [!IMPORTANT]
> **Core OpenCore Bug Fixes and Features belong upstream.**

- AegisBoot is a downstream continuous distribution. We maintain a zero-divergence policy for core bootloader code.
- If you have written a patch, new UEFI driver, kernel quirk, or bug fix intended for OpenCore itself, please submit your pull request directly to the upstream project: [`acidanthera/OpenCorePkg`](https://github.com/acidanthera/OpenCorePkg).
- Once your change is merged upstream, AegisBoot will automatically sync, validate, and package it within 15 minutes!

---

## 2. Downstream Accepted Contributions

We actively accept contributions in the following areas:
- **CI/CD Workflows:** Hardening, security scanning, performance optimizations, multi-architecture build improvements.
- **Automation Scripts:** Upstream sync engines, patch management tools, SBOM generators, health monitors.
- **Testing & Verification:** QEMU/OVMF boot regression test cases, static analysis rules, schema audits, unit tests.
- **Documentation & Governance:** Policies, troubleshooting guides, build instructions, architectural runbooks.
- **Packaging & Toolchains:** Docker build environments, toolchain pin updates, reproducible build manifests.

---

## 3. Workflow & Pull Request Guidelines

### 3.1 Branching Strategy
- Do not submit PRs directly to protected upstream tracking branches.
- Create a feature or fix branch from `main`:
  - `feat/<feature-name>`
  - `fix/<bug-fix-name>`
  - `ci/<workflow-name>`
  - `docs/<doc-name>`

### 3.2 Commit Conventions
We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard with UEFI/distro-specific scopes:
- `ci(workflows): pin actions to full commit sha`
- `feat(scripts): add automated SBOM generation in CycloneDX format`
- `docs(policy): update upstream synchronization SLA`
- `test(qemu): add OVMF serial boot assertion for x86_64`
- `fix(distro): fix script idempotency in check-env.sh`

### 3.3 Developer Certificate of Origin (DCO)
All commits must be signed-off with your real name and email (via `git commit -s`), certifying compliance with the Developer Certificate of Origin 1.1:
```
Signed-off-by: Your Name <your.email@example.com>
```

---

## 4. Code & Scripting Standards

### 4.1 Shell Scripts (`scripts/*.sh`)
- Must use `#!/usr/bin/env bash` with `set -euo pipefail`.
- Must pass `shellcheck` with zero warnings (`shellcheck -x scripts/*.sh`).
- Must be strictly idempotent (safe to run multiple times without unintended side effects or duplicate modifications).

### 4.2 Python Scripts (`scripts/*.py`, `tests/*.py`)
- Python 3.10+ compatible.
- Clean formatting and typing compliance (must pass `flake8` and `mypy` where configured).
- Standard library preferred for bootstrap scripts to minimize external dependencies.

### 4.3 C Code (EDK II / OpenCore)
- All C source files must adhere to the EDK II C Coding Standard Specification and Acidanthera conventions.
- Must pass Uncrustify formatting matching `Uncrustify.yml`.

---

## 5. CI Gate Validation Checklist

Every Pull Request is subjected to automated validation gates. Ensure your changes pass all local checks before opening a PR:
- [ ] `./scripts/check-env.sh` passes on your development system.
- [ ] `python -m unittest discover -s tests` passes 100% of test suites.
- [ ] No secrets, tokens, or private keys included.
- [ ] Documentation updated to reflect changes.
