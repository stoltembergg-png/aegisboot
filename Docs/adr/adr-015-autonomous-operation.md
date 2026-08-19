# ADR-015: Autonomous Operation Rules

## Status
Accepted

## Context
The system should operate with minimal daily human supervision. Routine sync, validation, merge, and release should be fully automated.

## Decision
**Fully Automated Operations (Zero Human Intervention):**

| Operation | Frequency | Automation | Human Intervention |
|-----------|-----------|------------|-------------------|
| Fetch upstream | 15 min | Cron workflow | None |
| Detect new commits | 15 min | Cron workflow | None |
| Create sync branch | On detect | Bot | None |
| Create PR | On detect | Bot | None |
| Run CI validation | On PR | GitHub Actions | None |
| Patch verification | On PR | Bot | None |
| Impact classification | On PR | Bot | None |
| Auto-merge | On gates pass | GitHub native | None |
| Release tagging | On merge | Bot | None |
| Build & package | On tag | GitHub Actions | None |
| SBOM generation | On release | Bot | None |
| Provenance generation | On release | Bot | None |
| GitHub Release publish | On release | Bot | None |
| Health check | 15 min | Cron | None |

**Exceptions Requiring Human Intervention:**

| Situation | Action |
|-----------|--------|
| Merge conflict | Maintainer resolves in sync branch |
| Patch fails to apply | Maintainer updates/retires patch |
| Build breaks | Maintainer investigates (upstream issue or local) |
| Release has critical bug | Maintainer triggers rollback |
| Security incident | Maintainer follows P0 runbook |
| Upstream force-push/rewrite | Maintainer coordinates recovery |
| New patch needed | Maintainer creates PR with upstream link |

**Autonomy Safeguards:**
- **Fail-closed:** Any gate failure blocks merge/release
- **Audit trail:** Every action logged in GitHub (Actions, PRs, commits)
- **Transparency:** All bot actions visible (labels, comments, PRs)
- **No silent failures:** Failed workflows create visible red runs
- **Idempotency:** All scripts safe to re-run
- **Deduplication:** No duplicate PRs, tags, or releases

**Monitoring for Autonomy Health:**
- Health check script (15 min) → alerts on degradation
- Metrics collector → feeds external monitoring
- Failed workflow count → alert if > threshold
- Behind count → alert if > 10 commits

## Consequences
**Positive:**
- True continuous integration (15-min sync loop)
- Minimal maintainer burden (exceptions only)
- Predictable, consistent behavior
- Full auditability

**Negative:**
- No human judgment in routine path (by design)
- Requires robust gates (no flaky tests)
- Upstream breaking changes may require manual sync recovery

## Implementation References
- `.github/workflows/sync.yml` - 15-min cron, auto-PR
- `.github/workflows/ci.yml` - 10 gates
- `.github/workflows/release-trigger.yml` - Auto-release
- `.github/workflows/release.yml` - Build, SBOM, provenance, publish
- `scripts/health-check.sh` - Health monitoring
- `scripts/collect-metrics.py` - Metrics for external monitoring
- `scripts/rollback.sh` - Emergency rollback
- `docs/troubleshooting.md` - Operational guide for exceptions