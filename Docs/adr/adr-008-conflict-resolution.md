# ADR-008: Conflict Resolution Process

## Status
Accepted

## Context
Upstream changes may conflict with local patches or fork modifications. We need a process that never masks conflicts and ensures transparent, auditable resolution.

## Decision
**Conflict Types:**
| Type | Description | Resolution |
|------|-------------|------------|
| Textual | Same file, different lines | Manual merge with justification |
| Structural | File moved/renamed | Verify patch applicability |
| Semantic | Logic changed, no text conflict | Manual review |
| Build | DSC/DEC/FDF conflicts | Review dependencies |

**Resolution Process:**
1. **Detection:** Sync workflow runs `apply-patches.sh --check` → fails if conflicts
2. **Blocking:** PR labeled `sync:conflict`, `status:needs-manual-review`, auto-merge blocked
3. **Issue Creation:** GitHub Issue from `.github/ISSUE_TEMPLATE/sync_issue.yml` with upstream SHA
4. **Human Resolution:** Maintainer resolves in sync branch with explicit commits
5. **Verification:** CI re-runs, all gates pass
6. **Documentation:** Resolution commit message explains conflict and rationale

**Rules:**
- **Never mask conflicts** — no force-push to "resolve"
- **No silent divergence** — every conflict visible in PR
- **Justification required** — each resolution commit has explanation
- **Audit trail** — resolution is separate commit, reviewable
- **Critical files** — Core library conflicts require extra scrutiny

**Sync Branch Handling:**
- Force-push allowed on `sync/upstream-<sha>` branches (temporary)
- Resolution commits pushed to same sync branch
- PR updated automatically
- Auto-merge re-enabled when gates pass

## Consequences
**Positive:**
- No hidden conflicts
- Full audit trail
- Clear accountability
- Prevents silent divergence

**Negative:**
- Requires human intervention for conflicts
- May delay sync (mitigated by alerting)

## Implementation References
- `docs/upstream-sync-policy.md` - Conflict handling section
- `scripts/apply-patches.sh` - Detects patch conflicts
- `.github/workflows/sync.yml` - Blocks auto-merge on conflict
- `.github/ISSUE_TEMPLATE/sync_issue.yml` - Issue template for conflicts
- `docs/upstream-conflict-resolution.md` - Detailed runbook