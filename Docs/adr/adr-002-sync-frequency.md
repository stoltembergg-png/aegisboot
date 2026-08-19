# ADR-002: Sync Frequency and Detection Method

## Status
Accepted

## Context
We need to continuously track upstream OpenCorePkg commits and create sync PRs automatically. The sync must be frequent enough to stay current but not so frequent as to overwhelm CI or GitHub API limits.

## Decision
**Sync Frequency:** Every 15 minutes (`*/15 * * * *` cron)

**Detection Method:**
1. GitHub Actions scheduled workflow (`.github/workflows/sync.yml`)
2. Fetch from `upstream` remote (`git fetch upstream master --tags`)
3. Compare local `HEAD` with `upstream/master` SHA
4. If different, proceed with sync branch creation

**Deduplication:**
- Check existing PRs for same sync branch name (`sync/upstream-<sha>`)
- Update existing PR via force-push to sync branch instead of creating duplicate
- Close stale sync PRs when new upstream commits detected

**Behind Count Tracking:**
- Calculate `git rev-list --count HEAD..upstream/master`
- Include in PR body for visibility
- Alert if behind > 10 commits

## Consequences
**Positive:**
- Near real-time sync (max 15 min latency)
- Low GitHub API usage (single fetch + compare per run)
- Automatic deduplication prevents PR spam
- Behind count provides operational visibility

**Negative:**
- 15-min cron has minimum granularity (GitHub Actions limitation)
- If upstream force-pushes, sync may temporarily diverge (mitigated by behind count alert)

## Implementation References
- `.github/workflows/sync.yml` - Cron trigger, fetch, compare, branch creation
- `scripts/sync-upstream.sh` - Local sync analysis script
- `scripts/health-check.sh` - Monitors behind count