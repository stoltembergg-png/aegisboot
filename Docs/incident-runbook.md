# AegisBoot — Incident Response Runbook

> **Version:** 1.0.0
> **Status:** Active
> **Last Updated:** 2026-08-19

---

## 1. Overview

This runbook provides step-by-step procedures for responding to incidents in the AegisBoot continuous distribution pipeline. It complements ADR-011 (Incident Response Process) with operational details.

---

## 2. Incident Classification

| Severity | Definition | Examples | Response SLA | Resolution SLA |
|----------|------------|----------|--------------|----------------|
| **P0 (Critical)** | Release with boot failure, security exploit, CI token exfiltration | OpenCore binary fails to boot; CVE in OpenCore; `GITHUB_TOKEN` exposed | < 1 hour | < 4 hours |
| **P1 (High)** | Security regression, script injection, broken crypto verification | SAST finding in release; secret interpolation in workflow | < 4 hours | < 24 hours |
| **P2 (Medium)** | Local privilege issues, dependency vuln without exploit | Dependabot alert (non-exploitable); local test flake | < 8 hours | < 72 hours |
| **P3 (Low)** | Hardening improvements, static analysis advisory | ShellCheck warning; documentation gap | < 24 hours | Next release |

---

## 3. Response Process

### 3.1 Detection
Incidents may be detected via:
- Automated alerts (health check, behind count, failed workflows)
- GitHub Actions failure notifications
- User reports (GitHub Issues)
- Security advisories (Dependabot, GHSA)
- Manual observation

### 3.2 Classification
1. **Assess impact** using severity matrix above
2. **Assign incident ID**: `INC-YYYYMMDD-XXX` (e.g., `INC-20260819-001`)
3. **Create GitHub Issue** from template (or security advisory for P0/P1)
4. **Notify maintainers** via GitHub mention / configured channels

### 3.3 Containment

#### P0 — Immediate Rollback
```bash
# Trigger rollback to previous release
./scripts/rollback.sh --dry-run  # Verify first
./scripts/rollback.sh            # Execute
```
- Creates rollback PR with `impact:critical` label
- Auto-triggers new release after merge
- Target: < 5 minutes to PR creation

#### P1 — Block & Investigate
- Mark affected release as "Pre-release" / deprecated
- Create investigation issue
- Begin root cause analysis

#### P2/P3 — Standard Process
- Create investigation issue
- Assign to maintainer
- Follow standard PR process for fix

### 3.4 Investigation
1. **Gather evidence**: workflow logs, commit diffs, artifact hashes
2. **Root cause analysis**:
   - `git bisect` for regressions
   - Compare SBOMs/provenance
   - Review workflow logs
3. **Document findings** in incident issue

### 3.5 Resolution
1. **Create fix PR** with minimal change
2. **Ensure all CI gates pass** (10 gates + builds)
3. **For P0/P1**: Fast-track review, `impact:critical` or `impact:major` label
4. **Merge** → auto-release triggered

### 3.6 Verification
- Confirm release artifacts generated correctly
- Verify checksums match
- Run QEMU boot test on release binary
- Confirm SBOM/provenance valid

### 3.7 Communication
- **P0/P1**: Post-mortem in GitHub Issue + Security Advisory (if applicable)
- **P2**: Update incident issue with resolution
- **P3**: Include in next release notes

### 3.8 Prevention
- Add test case for regression
- Add gate/check if gap identified
- Update documentation/runbook
- Update dependencies if applicable

---

## 4. Specific Scenarios

### 4.1 Release Boot Failure (P0)
**Symptoms**: QEMU boot test fails on release binary; user reports boot failure
**Actions**:
1. Trigger rollback: `./scripts/rollback.sh`
2. Create incident issue with boot logs
3. Bisect to find breaking commit
4. Fix or revert offending change
5. Re-release

### 4.2 Security Vulnerability in Release (P0)
**Symptoms**: CVE in OpenCore component; malicious code detected
**Actions**:
1. Mark release as deprecated (GitHub Release UI)
2. Trigger rollback
3. Create Security Advisory (GitHub Security tab)
4. Coordinate with upstream if CVE in OpenCore
6. Fix + re-release

### 4.3 CI Token Exfiltration (P0)
**Symptoms**: Suspicious workflow runs; unauthorized access
**Actions**:
1. Revoke compromised token immediately (GitHub Settings)
3. Rotate all secrets
4. Audit workflow logs for unauthorized access
5. Force re-run of all recent workflows
6. Post-mortem

### 4.4 Upstream Breaking Change (P1)
**Symptoms**: Sync PR fails multiple gates; behind count increasing
**Actions**:
1. Label sync PR `sync:conflict`, `status:needs-manual-review`
2. Create sync issue from template
3. Analyze upstream changes
4. Update patches or adapt code
5. Re-run sync

### 4.5 Patch Stack Conflict (P1)
**Symptoms**: `apply-patches.sh --check` fails on sync
**Actions**:
1. Sync PR labeled `sync:conflict`, `area:patches`
2. Maintainer rebases conflicting patch
3. Update patch file with new base
4. Re-run validation

### 4.6 Failed Workflow (P1/P2)
**Symptoms**: Red workflow run in Actions tab
**Actions**:
1. Check workflow logs
2. If flaky: re-run workflow
3. If genuine: create fix PR
4. Monitor for recurrence

### 4.7 Dependency Vulnerability (P2)
**Symptoms**: Dependabot alert or `gh advisory`
**Actions**:
1. Assess exploitability
2. If actionable: update toolchain pin or action version
3. Test locally + CI
4. Release if warranted

---

## 5. Key Contacts & Escalation

| Role | Contact | Escalation |
|------|---------|------------|
| Lead Maintainer | @GabrielStoltemberg | Primary for all incidents |
| Security Officer | Designated maintainer | Security incidents (P0/P1) |
| Community | GitHub Discussions / Issues | User-reported issues |

---

## 6. Useful Commands

```bash
# Health check
./scripts/health-check.sh

# Rollback (dry-run first!)
./scripts/rollback.sh --dry-run
./scripts/rollback.sh

# Sync manually
./scripts/sync-upstream.sh

# View metrics
python scripts/collect-metrics.py --format json

# Validate workflows
python scripts/validate_workflows.py --strict

# Run all tests
python -m unittest discover -s tests

# Check workflow runs
gh run list --limit 20
gh run view <run-id> --log

# View milestones
python scripts/manage-milestones.py list
```

---

## 7. Post-Mortem Template

Create in GitHub Issue for P0/P1 incidents:

```markdown
# Post-Mortem: INC-YYYYMMDD-XXX

## Summary
<One paragraph summary of what happened>

## Timeline
- YYYY-MM-DD HH:MM — Detection
- YYYY-MM-DD HH:MM — Classification
- YYYY-MM-DD HH:MM — Containment
- YYYY-MM-DD HH:MM — Resolution
- YYYY-MM-DD HH:MM — Verification

## Root Cause
<Technical explanation of why it happened>

## Impact
- Affected releases: 
- Users affected:
- Duration:

## Resolution
<What was done to fix it>

## Prevention
- [ ] Test added: <description>
- [ ] Gate added: <description>
- [ ] Dependency updated: <description>
- [ ] Documentation updated: <description>

## Action Items
- [ ] <action> — @assignee — due YYYY-MM-DD
```

---

## 8. References

| Document | Link |
|----------|------|
| ADR-011 Incident Response | `docs/adr/adr-011-incident-response.md` |
| ADR-014 Rollback Procedure | `docs/adr/adr-014-rollback-procedure.md` |
| ADR-012 Security Model | `docs/adr/adr-012-security-model.md` |
| Troubleshooting Guide | `docs/troubleshooting.md` |
| Health Check Script | `scripts/health-check.sh` |
| Rollback Script | `scripts/rollback.sh` |
| GitHub Security Advisories | https://github.com/aegisboot/aegisboot/security/advisories |

---

## 9. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-08-19 | Gabriel Stoltemberg | Initial version |