# AegisBoot — Upstream Synchronization Policy

---

## 1. Upstream Tracking Architecture

AegisBoot maintains a continuous tracking link to upstream [`acidanthera/OpenCorePkg`](https://github.com/acidanthera/OpenCorePkg):

- **Remote Mapping:** The `origin` remote points permanently to `https://github.com/acidanthera/OpenCorePkg.git`.
- **Target Branch:** Upstream tracking focuses on `origin/master`.
- **Tag Mirroring:** All upstream release tags (`1.0.8`, `1.0.7`, etc.) are monitored and mirrored.

---

## 2. Automated Sync Schedule & Lifecycle

Synchronization operates autonomously via `.github/workflows/sync.yml`:

```
┌─────────────────────────────────────────────────────────────┐
│                    SYNC LIFECYCLE (15m CRON)                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
               1. Fetch upstream origin/master
                               │
               2. Has upstream commit SHA changed?
                               │
                ┌──────────────┴──────────────┐
                NO                            YES
                ▼                             ▼
         [No action / Exit]       3. Create sync/upstream-<sha>
                                              │
                                  4. Test local patch stack (Patches/*.patch)
                                              │
                                  5. Run pre-flight checks & diff analysis
                                              │
                                  6. Open / Update automated Sync PR
                                              │
                                  7. Trigger CI Validation Gate Matrix
                                              │
                                  8. All Gates Green?
                                       ├── YES: Auto-merge to main (Squash)
                                       └── NO: Block & notify maintainer
```

---

## 3. Conflict Handling & Non-Masking Invariant

> [!CAUTION]
> **Conflicts must never be masked or silently bypassed.**

If upstream commits introduce breaking changes or merge conflicts with downstream automation or local patches:
1. **No Silent Force Pushes:** The sync bot will never force-push over `main` or skip conflict resolution.
2. **Issue Generation:** The sync engine automatically tags the PR as `sync:conflict` and generates an actionable summary issue.
3. **Transparent Resolution:** Maintainers resolve the conflict in a dedicated, explicit commit documenting:
   - What upstream changes caused the divergence.
   - Why the resolution chosen preserves upstream behavioral fidelity.
   - Any necessary adjustments to `Patches/` or downstream tooling.
