# AegisBoot — Local Patch Policy

---

## 1. Purpose & Guiding Principles

AegisBoot strives for minimal divergence from upstream OpenCorePkg. The `Patches/` directory is reserved exclusively for essential EDK II / AUDK package adjustments and temporary downstream stabilization fixes.

### Principles:
1. **Upstream First:** Any patch that can be integrated upstream into `acidanthera/OpenCorePkg` or `tianocore/edk2` must be submitted upstream before or concurrently with downstream inclusion.
2. **Standard Format:** Patches must be generated using `git format-patch` with standard email headers, author attribution, and clear commit messages.
3. **Traceability:** Every patch file must declare its upstream tracking status.

---

## 2. Patch File Header Requirements

Every patch in `Patches/` must include standard git metadata and an `Upstream-Status` header:

```patch
From: Author Name <author@example.com>
Date: Mon, 19 Aug 2026 00:00:00 +0000
Subject: [PATCH] ComponentName: Summary of change

Detailed description explaining the technical problem, why this fix
is necessary, and what architectures/environments it affects.

Upstream-Status: Submitted [URL] | Pending | Downstream-Only | In-Review
Signed-off-by: Author Name <author@example.com>
---
```

---

## 3. Patch Lifecycle

```
[ Identified Issue ]
        │
        ▼
[ Create Unified Patch in Patches/ ] ──▶ [ Submit Upstream PR ]
        │                                        │
        ▼                                        ▼
[ CI Verification: apply-patches.sh ]     [ Upstream Review ]
        │                                        │
        ▼                                        ▼
[ Deployed in Downstream Builds ]         [ Upstream Merged! ]
                                                 │
                                                 ▼
                                        [ Remove Patch from Patches/ ]
                                        (Downstream returns to 100% upstream)
```

---

## 4. Automated Patch Validation

Every Pull Request and upstream sync execution runs `scripts/apply-patches.sh --check` to assert that:
1. All patches apply cleanly without rejects or fuzzy offset errors.
2. No duplicate patches exist that have already been integrated into the upstream tree.
3. Patch file naming follows the monotonic index convention: `0001-...patch`, `0002-...patch`.
