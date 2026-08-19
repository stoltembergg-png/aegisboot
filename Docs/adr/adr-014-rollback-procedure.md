# ADR-014: Rollback Procedure

## Status
Accepted

## Context
When a release has a critical defect (boot failure, security issue), we need a fast, reliable way to revert to a known-good state.

## Decision
**Rollback Trigger:**
- P0 incident: boot failure in release, security exploit
- Manual trigger by maintainer via `scripts/rollback.sh`

**Rollback Process:**
1. **Auto-detect target:** `scripts/rollback.sh` finds previous release tag (`v*-aegis.*` sorted by version)
2. **Create rollback branch:** `rollback/<tag>-<timestamp>`
3. **Checkout target commit:** `git checkout -b <branch> <tag>`
4. **Push to fork:** `git push fork <branch> --force`
5. **Create PR:** Base `master`, head rollback branch, labels `rollback,impact:critical`
6. **Auto-release after merge:** `release-trigger.yml` detects merged rollback PR, creates new release with incremented revision

**Rollback Time Target:** < 5 minutes from trigger to PR creation

**Rollback Constraints:**
- Only to previous release tags (not arbitrary commits)
- Creates new release (version bump) — does not delete old release
- Old release marked as deprecated in GitHub (manual step)
- Rollback PR requires manual review/merge (safety)

**Emergency Hotfix Alternative:**
If rollback is too disruptive, maintainer can:
1. Create hotfix patch in `Patches/`
2. Fast-track PR with `impact:critical`
3. Auto-release after merge

**Rollback Testing:**
- Tested monthly via `scripts/rollback.sh --dry-run`
- Documented in `docs/troubleshooting.md`

## Consequences
**Positive:**
- Fast, automated rollback to known-good state
- New release automatically created after rollback
- No manual git operations required
- Audit trail via PR and release

**Negative:**
- Version number increments (can't "un-release")
- Old release artifacts remain (marked deprecated)
- Requires manual PR merge (safety gate)

## Implementation References
- `scripts/rollback.sh` - Rollback engine
- `docs/troubleshooting.md` - Rollback section
- `.github/workflows/release-trigger.yml` - Auto-release after rollback merge
- `docs/incident-template.md` - Post-mortem template