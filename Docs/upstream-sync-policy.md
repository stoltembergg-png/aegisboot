# Upstream Synchronization Policy

> **Policy Version:** 1.0.0
> **Status:** Active
> **Last Updated:** 2026-08-19

---

## 1. Purpose

This policy defines how AegisBoot continuously tracks, validates, and integrates commits from the upstream OpenCorePkg repository (`acidanthera/OpenCorePkg`).

---

## 2. Remote Configuration

| Remote Name | URL | Purpose |
|---|---|---|
| `origin` | `https://github.com/acidanthera/OpenCorePkg.git` | **Upstream source** — fetch only, never push |
| `fork` | `https://github.com/aegisboot/aegisboot.git` | **Our fork** — push sync branches, PRs, releases |

**Critical Rule:** `origin` MUST point to upstream. Our fork is a separate remote (`fork`). Never push directly to `origin`.

---

## 3. Sync Cadence

| Trigger | Frequency | Description |
|---|---|---|
| Scheduled | Every 15 minutes (`*/15 * * * *`) | GitHub Actions cron workflow |
| Manual Dispatch | On-demand | Workflow dispatch via GitHub UI/API |
| Webhook (Future) | Real-time | GitHub webhook from upstream (when available) |

---

## 4. Sync Process

### 4.1 Detection

```bash
git fetch origin master --tags
LOCAL_SHA=$(git rev-parse HEAD)
UPSTREAM_SHA=$(git rev-parse origin/master)
```

- If `LOCAL_SHA == UPSTREAM_SHA`: Already in sync, exit cleanly
- If different: New commits detected, proceed to sync

### 4.2 Pre-Sync Validation

Before creating sync PR, verify:

1. **Patch Stack Applicability:** All patches in `Patches/` apply cleanly against `origin/master`
   - Run: `./scripts/apply-patches.sh --check`
   - If ANY patch fails: Block sync, label PR `sync:conflict`, require manual intervention

2. **No Local Uncommitted Changes:** Working tree must be clean

### 4.3 Sync Branch Creation

```bash
SYNC_BRANCH="sync/upstream-${UPSTREAM_SHA:0:7}"
git checkout -B "$SYNC_BRANCH" origin/master
git push fork "$SYNC_BRANCH" --force
```

**Branch Naming:** `sync/upstream-<short_sha>` (e.g., `sync/upstream-170b538`)

### 4.4 Pull Request Creation

```bash
gh pr create \
  --base main \
  --head "$SYNC_BRANCH" \
  --title "sync(upstream): merge upstream ${UPSTREAM_SHORT} (${UPSTREAM_DATE})" \
  --body "<template>" \
  --label "sync:upstream,impact:minor"
```

**PR Requirements:**
- Base: `main` (protected branch)
- Head: `sync/upstream-<sha>`
- Title: Conventional commit format with upstream SHA and date
- Body: Includes upstream SHA link, date, validation checklist
- Labels: `sync:upstream` + impact classification

### 4.5 Deduplication

- If a PR already exists for the same sync branch: **Do not create duplicate**
- Check: `gh pr list --head "$SYNC_BRANCH" --json number`
- Update existing PR if needed (force-push to sync branch)

---

## 5. CI Validation Gates

Every sync PR MUST pass ALL gates before merge:

| Gate | Workflow | Required |
|---|---|---|
| Multi-platform Build | `build.yml` | ✅ |
| Static Analysis | `analyze.yml` | ✅ |
| CI Validation Gates | `ci.yml` (all jobs) | ✅ |
| QEMU/OVMF Boot Test | `ci.yml` → `qemu-boot-test` | ✅ |
| Patch Stack Verification | `ci.yml` → `patch-stack-verification` | ✅ |
| Policy & Metadata Tests | `ci.yml` → `policy-and-metadata-tests` | ✅ |

**No exceptions. No bypasses.**

---

## 6. Impact Classification

The sync PR is automatically labeled with impact based on changed files:

| Label | Trigger |
|---|---|
| `impact:none` | Only docs, comments, whitespace |
| `impact:patch` | Bug fixes, small lib changes |
| `impact:minor` | New drivers, features, enhancements |
| `impact:major` | Breaking API changes, arch shifts |
| `impact:critical` | Security fixes, boot regressions |
| `impact:infrastructure` | CI, Docker, toolchain only |

**Classification logic runs in CI.** Human override allowed.

---

## 7. Auto-Merge Policy

**Auto-merge executes ONLY when:**

1. ✅ All required CI gates pass (100% green)
2. ✅ No merge conflicts exist
3. ✅ Patch stack verification passes
4. ✅ QEMU boot test passes
5. ✅ Branch protection rules satisfied (no direct push, force push blocked)
6. ✅ PR has `status:ready-to-merge` label (set by CI on full pass)

**Merge Strategy:** Squash merge
**Commit Message:** `sync: merge upstream <sha> (<date>)`

---

## 8. Conflict Handling

### 8.1 Detection

Conflicts detected if:
- `git merge-tree` shows conflicts
- Patch stack verification fails (`apply-patches.sh --check` returns non-zero)
- CI build fails due to upstream API changes

### 8.2 Response

1. **Block auto-merge immediately** — label PR `sync:conflict`, `status:needs-manual-review`
2. **Create GitHub Issue** from `.github/ISSUE_TEMPLATE/sync_issue.yml` with upstream SHA
3. **Human maintainer resolves** — create resolution commits on sync branch
4. **Never force-push to `main`** — branch protection prevents this
5. **Resolution commits must:**
   - Have clear commit messages explaining the conflict
   - Reference upstream commit(s) involved
   - Preserve upstream semantics (no arbitrary divergence)

### 8.3 Documentation

Every conflict resolution is recorded in:
- PR commit history
- `CHANGELOG_DISTRO.md` (under "Upstream Conflict Resolutions")
- GitHub Issue for tracking

---

## 9. Recording State

After successful merge, the following SHAs are recorded:

| Variable | Description | Recorded In |
|---|---|---|
| `upstream_base_sha` | Fork's HEAD before sync | PR metadata, `distro-version.json` |
| `upstream_head_sha` | Upstream commit merged (`origin/master`) | PR title, `distro-version.json`, git history |
| `fork_head_sha` | Fork's HEAD after merge | `distro-version.json`, git history |

**Behind Detection:**
```bash
BEHIND=$(git rev-list --count HEAD..origin/master)
if [ "$BEHIND" -gt 0 ]; then
  echo "WARNING: Fork is behind upstream by $BEHIND commit(s)"
  # Alert if beyond acceptable window (e.g., > 10 commits)
fi
```

---

## 10. Idempotency Guarantees

The sync workflow is fully idempotent:

- **Repeated runs with same upstream SHA** produce identical result
- **No duplicate PRs** created for same sync branch
- **Force-push to sync branch** updates existing PR (safe)
- **Clean exit** if already in sync
- **Patch check** runs every time, always validates against current upstream HEAD

---

## 11. Monitoring & Alerting

| Metric | Threshold | Action |
|---|---|---|
| Sync latency | > 30 min | Alert: workflow may be stuck |
| Behind count | > 10 commits | Alert: sync falling behind |
| Patch failure rate | > 0 | Alert: patch needs update |
| CI failure rate (sync PRs) | > 5% | Alert: systemic issue |

---

## 12. Emergency Procedures

### Upstream Force-Push / Rebase

If upstream rewrites history:
1. Detect: `LOCAL_SHA` not ancestor of `UPSTREAM_SHA`
2. Block auto-sync
3. Alert maintainers immediately
4. Manual reconciliation required

### Critical Security Fix in Upstream

If upstream releases critical fix:
1. Manual dispatch sync workflow immediately
2. Skip 15-min wait
3. Expedite through CI (priority queue if available)
4. Release within 1 hour of upstream fix

---

## 13. Compliance Checklist

Every sync operation must satisfy:

- [ ] `origin` points to `acidanthera/OpenCorePkg`
- [ ] `fork` remote configured for push
- [ ] Fetch from `origin` only (never push to `origin`)
- [ ] Sync branch named `sync/upstream-<sha>`
- [ ] PR created against `main` (not `master`)
- [ ] Patch stack verified clean before PR
- [ ] All CI gates pass before merge
- [ ] Squash merge strategy used
- [ ] `upstream_base_sha`, `upstream_head_sha`, `fork_head_sha` recorded
- [ ] Behind count checked and alerted if > threshold
- [ ] No duplicate PR for same upstream SHA
- [ ] Workflow idempotent (safe to re-run)