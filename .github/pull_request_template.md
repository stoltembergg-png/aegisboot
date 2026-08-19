## Description
<!-- Provide a clear summary of the changes introduced in this PR. -->

---

## Type of Change
- [ ] `sync`: Automated Upstream Sync from `acidanthera/OpenCorePkg`
- [ ] `ci`: Workflow Hardening, CI/CD, or Security Gates
- [ ] `scripts`: Automation, Tooling, or Packaging Scripts
- [ ] `patches`: Local Patch Stack Modification (`Patches/`)
- [ ] `toolchain`: Compiler, Docker, or Dependency Pin Update
- [ ] `docs`: Governance, Branding, or Documentation Update
- [ ] `fix`: Bug Fix

---

## Upstream Reference (For Sync & Tracking PRs)
- **Upstream SHA:** `{{UPSTREAM_SHA}}`
- **Upstream Tag/Branch:** `origin/master`
- **Upstream Commit URL:** `https://github.com/acidanthera/OpenCorePkg/commit/{{UPSTREAM_SHA}}`

---

## Impact Classification
- [ ] `impact:none` — Docs/Comments only (No release needed)
- [ ] `impact:patch` — Bugfix / Small enhancement
- [ ] `impact:minor` — New feature / Significant enhancement
- [ ] `impact:major` — Architectural or breaking change
- [ ] `impact:critical` — Urgent security fix or critical boot resolution
- [ ] `impact:infrastructure` — CI/CD / Docker environment only

---

## CI Gate & Security Checklist
- [ ] Workflow Integrity tests pass (`python -m unittest tests/test_workflow_integrity.py`).
- [ ] Formatting standards met (Uncrustify / Linters).
- [ ] Static analysis clean (ShellCheck, Prospector, ocvalidate).
- [ ] Multi-platform build passes (Linux, macOS, Windows).
- [ ] QEMU/OVMF boot regression test passes.
- [ ] Patch stack clean (`scripts/apply-patches.sh --check`).
- [ ] No secrets, tokens, or private keys in diff.
- [ ] DCO `Signed-off-by` line present in all commits.
