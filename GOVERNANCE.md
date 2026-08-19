# AegisBoot — Project Governance & Autonomous Operations

---

## 1. Roles and Responsibilities

The AegisBoot project operates under a hybrid governance model combining human maintainers and autonomous automation agents:

| Role | Entity | Responsibilities |
|---|---|---|
| **Lead Maintainer** | Gabriel Stoltemberg | Repository architecture, branch protection rules, strategic alignment, emergency interventions, cryptographic key management. |
| **Security Officer** | Designated Maintainer | Vulnerability triage, secret rotation, SLSA provenance verification, security advisories. |
| **Autonomous Sync Bot** | GitHub Actions (`@aegis-bot`) | Upstream commit polling (15m), sync branch management, automated PR creation, gate evaluation, automated labeling, artifact building. |
| **Reviewers & Contributors** | Community | Code reviews for CI/CD tooling, documentation enhancements, bug reports, and upstream sync testing. |

---

## 2. Decision-Making Process

### 2.1 Standard Automated Syncs
- Routine upstream commits that pass 100% of CI validation gates (build, static analysis, QEMU boot test, patch rebase) are merged automatically via squash merge.
- Automated commit format: `sync: merge upstream <upstream_sha> (<upstream_date>)`.

### 2.2 Patch Management & Structural Changes
- Any new local patch in `Patches/` or modification to CI/CD workflows requires:
  1. A structured Pull Request.
  2. Passing all CI gates (formatting, static analysis, unit/integration tests, QEMU boot test).
  3. Formal review and approval from the Lead Maintainer.

### 2.3 Upstream Merge Conflicts & Exceptions
- In the event of a merge conflict or upstream structural breaking change:
  1. The automated sync bot labels the PR as `sync:conflict` and `status:needs-manual-review`.
  2. Auto-merge is immediately blocked.
  3. Human maintainers resolve the conflict transparently in a dedicated commit with documented rationale.
  4. Force-pushing to `main` is strictly prohibited by branch protection rules.

---

## 3. Escalation and Rollback Framework

If an integrated build causes boot regressions or security defects:
1. **Severity Classification:** P0 (Critical boot failure) vs P1 (Tooling break).
2. **Containment:** If a tagged release is compromised, the release is immediately marked as deprecated/yanked, and a known-good release is redeployed within < 5 minutes.
3. **Transparency:** A post-mortem incident report is published in the release notes or security advisory.
