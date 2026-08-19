# ADR-013: Auto-Merge Policy

## Status
Accepted

## Context
We want to minimize manual intervention for routine upstream syncs while ensuring no broken code reaches `master`.

## Decision
**Auto-Merge Conditions (ALL must be true):**
1. ✅ All required CI checks pass (10 gates in `ci.yml` + build + analyze)
2. ✅ No merge conflicts exist
3. ✅ Patch stack verification passes (`apply-patches.sh --check`)
4. ✅ QEMU/OVMF boot test passes
5. ✅ Branch protection satisfied (no direct push, force push blocked)
6. ✅ PR has `status:ready-to-merge` label (set by CI on full pass)

**Auto-Merge Execution:**
- GitHub native auto-merge enabled on repository
- PR author: GitHub Actions bot (`github-actions[bot]`)
- Strategy: Squash merge
- Commit message: `sync: merge upstream <sha> (<date>)`

**Labels Flow:**
- PR created → `sync:upstream,impact:<classified>`
- Gates running → `status:gate-failed` if any fail
- All gates pass → CI sets `status:ready-to-merge`, removes `status:gate-failed`
- Auto-merge triggers → PR merged → `sync:auto-merged` label added

**Merge Blocks (Auto-merge DISABLED if):**
- Any check red or pending
- Merge conflicts detected
- Patch stack verification fails
- QEMU boot test fails
- Behind count > 10 (warning only, not block)
- PR labeled `status:needs-manual-review`

**Manual Override:**
- Maintainer can manually merge after review
- Emergency hotfix PRs: manual review required
- Rollback PRs: manual review required (`impact:critical`)

## Consequences
**Positive:**
- Zero manual intervention for routine syncs
- Safety: multiple independent gates must pass
- Audit trail: every auto-merge logged
- Fast: merge within minutes of last gate passing

**Negative:**
- No emergency bypass (by design)
- Requires all gates to be reliable (no flaky tests)
- GitHub Actions bot appears as merge author

## Implementation References
- `.github/workflows/sync.yml` - Creates PR, applies labels
- `.github/workflows/ci.yml` - Gates that must pass
- `.github/workflows/release-trigger.yml` - Auto-release after merge
- GitHub Settings → General → Auto-merge (enabled)
- GitHub Settings → Branches → Branch protection rules