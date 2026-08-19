# ADR-011: Incident Response Process

## Status
Accepted

## Context
When releases have critical defects or the pipeline breaks, we need a structured response process with clear escalation and rollback procedures.

## Decision
**Incident Classification:**

| Severity | Definition | Response Time | Resolution Target |
|----------|------------|---------------|-------------------|
| P0 (Critical) | Release with boot failure, security exploit, CI token exfiltration | < 1 hour | < 4 hours |
| P1 (High) | Security regression, script injection, broken crypto verification | < 4 hours | < 24 hours |
| P2 (Medium) | Local privilege issues, dependency vuln without exploit | < 8 hours | < 72 hours |
| P3 (Low) | Hardening improvements, static analysis advisory | < 24 hours | Next release |

**Response Process:**
1. **Detect** — Monitoring, health check, user report, failed release
2. **Classify** — Assign severity (P0-P3)
3. **Contain** — 
   - P0: Immediate rollback via `scripts/rollback.sh` (< 5 min)
   - P1: Block affected release, investigate
4. **Investigate** — Root cause analysis (git bisect, logs, diff)
5. **Fix** — Hotfix PR with minimal change, all gates
6. **Verify** — All CI gates pass, QEMU boot test passes
7. **Communicate** — Release notes, security advisory if applicable
8. **Prevent** — Add test/gate if gap identified

**Rollback Procedure (`scripts/rollback.sh`):**
- Auto-detects previous release tag
- Creates rollback branch + PR with `impact:critical` label
- Auto-triggers new release after merge
- Target: < 5 minutes to rollback PR creation

**Post-Mortem (P0/P1):**
- Published in release notes or security advisory
- Timeline, root cause, fix, prevention
- Template in `docs/incident-template.md`

## Consequences
**Positive:**
- Clear escalation path
- Fast rollback capability
- Structured learning from incidents
- Transparency via post-mortems

**Negative:**
- Requires maintainer availability for P0/P1
- Rollback creates new release (version bump)

## Implementation References
- `scripts/rollback.sh` - Automated rollback engine
- `docs/troubleshooting.md` - Incident runbook section
- `.github/workflows/release-trigger.yml` - Auto-release after rollback merge
- `docs/incident-template.md` - Post-mortem template