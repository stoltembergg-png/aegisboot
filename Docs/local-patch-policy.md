# Local Patch Stack Policy

> **Policy Version:** 1.0.0
> **Status:** Active
> **Last Updated:** 2026-08-19

---

## 1. Purpose

This policy governs the management, application, and lifecycle of local patches maintained in the AegisBoot distribution. Local patches are **temporary, minimal, and upstream-tracked** — they exist only until the changes are adopted upstream.

---

## 2. Principles

| Principle | Enforcement |
|---|---|
| **Minimal Surface** | Only patches that cannot be contributed upstream immediately |
| **Upstream Tracking** | Every patch has `Upstream-Status` header |
| **Transparency** | Patches are visible, versioned, and auditable |
| **No Silent Divergence** | Conflicts are surfaced, never masked |
| **Automated Verification** | CI validates patch applicability on every sync |

---

## 3. Patch Lifecycle

```
┌─────────────────┐
│   CREATION      │  → Need identified (bug fix, hardware quirk, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SUBMISSION    │  → PR to upstream (acidanthera/OpenCorePkg)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LOCAL MAINT    │  → Stored in Patches/ with tracking metadata
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 UPSTREAM  CONFLICT
 MERGED     / BREAK
    │         │
    ▼         ▼
┌─────────────────┐
│   RETIREMENT    │  → Remove from Patches/ after upstream merge
└─────────────────┘
```

---

## 4. Patch Format Requirements

Every patch in `Patches/` **must**:

1. **Be a valid `git format-patch` output** (single commit, proper headers)
2. **Include `Upstream-Status` header** with one of:
   - `Submitted` — Sent to upstream, awaiting review
   - `Accepted` — Upstream accepted, waiting for merge
   - `Backport` — Backport of upstream commit to older base
   - `Workaround` — Temporary workaround, upstream issue tracked
   - `Pending` — Default for new patches
3. **Reference upstream issue/PR** in commit message body:
   ```
   Upstream-Issue: https://github.com/acidanthera/OpenCorePkg/issues/XXXX
   Upstream-PR: https://github.com/acidanthera/OpenCorePkg/pull/XXXX
   ```
4. **Be numbered sequentially** (e.g., `0001-`, `0002-`, etc.)
5. **Target the correct upstream path** (apply to `UDK/` subdirectory when applicable)

### Example Patch Header

```
From 170b538b7e28b8cf44eb896b7978f8bc01d12345 Mon Sep 17 00:00:00 2001
From: Contributor Name <email@example.com>
Date: Mon, 19 Aug 2026 12:00:00 +0000
Subject: [PATCH] Library/OcFileLib: Fix MBR read alignment for large disks

This resolves boot failure on disks with 4Kn sectors where MBR
reads were misaligned.

Upstream-Status: Submitted [https://github.com/acidanthera/OpenCorePkg/pull/XXXX]
Upstream-Issue: https://github.com/acidanthera/OpenCorePkg/issues/XXXX
Signed-off-by: Contributor Name <email@example.com>
---
 Library/OcFileLib/OcFileLib.c | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```

---

## 5. Patch Directory Structure

```
Patches/
├── 0001-<component>-<short-description>.patch
├── 0002-<component>-<short-description>.patch
├── 0003-<component>-<short-description>.patch
├── ...
├── README.md          # Index of patches with status
└── series             # Optional: ordered list for quilt/git-am
```

**Naming Convention:** `<NNNN>-<subsystem>-<kebab-case-description>.patch`

---

## 6. Patch Application

### 6.1 Idempotent Application Script

Use `./scripts/apply-patches.sh` with modes:

```bash
# Check only (runs in CI)
./scripts/apply-patches.sh --check

# Apply patches (local development)
./scripts/apply-patches.sh
```

### 6.2 Behavior

| Scenario | `--check` Mode | Apply Mode |
|---|---|---|
| Patch applies cleanly | `CLEAN` / `APPLIED_SUCCESS` | Applies |
| Patch already applied | `ALREADY_APPLIED` | Skips |
| Patch conflicts | `REJECTED / CONFLICT` | Fails, exits 1 |
| Invalid patch format | `INVALID_PATCH_FORMAT` | Fails, exits 1 |

### 6.3 UDK Directory Handling

If `UDK/` directory exists (post-bootstrap), patches are validated/applied there.
If not, syntax-only validation is performed.

---

## 7. Adding a New Patch

### 7.1 Process

1. **Create the fix** in a feature branch
2. **Test thoroughly** (build, QEMU boot, regression tests)
3. **Format as patch:** `git format-patch -1 --stdout > Patches/000X-....patch`
4. **Add metadata headers** (Upstream-Status, Upstream-Issue, Signed-off-by)
5. **Submit to upstream** (create PR at acidanthera/OpenCorePkg)
6. **Open PR in AegisBoot** with:
   - Type: `patches`
   - Link to upstream PR
   - Justification for local maintenance
7. **CI validates** patch applies cleanly

### 7.2 Review Requirements

- Lead Maintainer approval required
- Must pass all CI gates
- Upstream PR link mandatory
- Clear retirement plan documented

---

## 8. Patch Rebase & Maintenance

### 8.1 On Upstream Sync

Every upstream sync triggers:
1. `apply-patches.sh --check` runs in CI
2. If ANY patch fails:
   - Sync PR labeled `sync:conflict`, `area:patches`
   - Auto-merge blocked
   - Issue created for maintainer

### 8.2 Manual Rebase

```bash
# From main branch
git checkout main
git fetch origin master

# Create rebase workspace
git checkout -b rebase-patches origin/master

# Apply each patch sequentially
for patch in Patches/*.patch; do
  git am "$patch" || { echo "CONFLICT in $patch"; git am --abort; exit 1; }
done

# Result: patches rebased onto new upstream HEAD
# Create PR with rebased patches
```

### 8.3 Retirement

When upstream merges the patch:
1. Remove patch file from `Patches/`
2. Update `Patches/README.md`
3. Commit: `patch: retire <patch-name> — merged upstream as <upstream-sha>`
4. PR with type `patches`, label `impact:patch`

---

## 9. Patch Stack Verification in CI

The `patch-stack-verification` job in `.github/workflows/ci.yml` runs on every PR:

```yaml
- name: Check Patch Clean Applicability
  run: ./scripts/apply-patches.sh --check
```

**This gate is REQUIRED.** Failure blocks merge.

---

## 10. Prohibited Patterns

| Anti-Pattern | Why Forbidden | Alternative |
|---|---|---|
| Direct commits to OpenCore source | Bypasses tracking | Use `Patches/` + `apply-patches.sh` |
| Patches without Upstream-Status | No visibility | Always add header |
| Patches for cosmetic changes | Divergence | Don't patch; upstream or skip |
| Force-pushing to resolve conflicts | History destruction | Resolve in sync branch commits |
| Modifying upstream files in-place | Untraceable | Patch-only workflow |

---

## 11. Compliance Checklist

For every patch in `Patches/`:

- [ ] Valid `git format-patch` format
- [ ] `Upstream-Status` header present
- [ ] `Upstream-Issue` or `Upstream-PR` reference
- [ ] `Signed-off-by` line (DCO)
- [ ] Sequential numbering (0001, 0002, ...)
- [ ] Applies cleanly to current `origin/master` (CI verified)
- [ ] Documented in `Patches/README.md`
- [ ] Retirement plan noted (target upstream PR)

---

## 12. Patch Index (Patches/README.md)

Maintain a living index:

```markdown
# AegisBoot Local Patch Stack

| # | Patch File | Status | Upstream Ref | Target Retirement |
|---|---|---|---|---|
| 1 | 0001-MdeModulePkg-SataControllerDxe-Add-support-for-drive.patch | Pending | #XXXX | v1.0.9 |
| 2 | 0002-MdeModulePkg-AtaAtapiPassThru-Add-support-for-drives.patch | Submitted | PR #XXXX | v1.0.9 |
| 3 | 0003-MdeModulePkg-AtaAtapiPassThru-Reduce-timeout.patch | Submitted | PR #XXXX | v1.0.9 |
| 5 | 0005-ShellPkg-Devices-shell-command-support-misaligned-de.patch | Workaround | Issue #XXXX | TBD |
| 7 | 0007-ShellPkg-Allow-DEBUG-shell-to-start-with-too-many-fi.patch | Workaround | Issue #XXXX | TBD |
```

---

## 13. Emergency Patch Override

In critical situations (boot regression, security):

1. Create patch with `Upstream-Status: Workaround`
2. Add `Critical: true` marker in commit body
3. Fast-track PR with Lead Maintainer approval
4. **Must** submit to upstream within 48 hours
5. Track retirement aggressively

---

## 14. Tooling Reference

| Script | Purpose |
|---|---|
| `scripts/apply-patches.sh` | Idempotent apply/check |
| `scripts/sync-upstream.sh` | Validates patches on sync |
| `tests/test_patch_stack.py` | Unit tests for patch logic |

---

## 15. Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-08-19 | Initial policy |