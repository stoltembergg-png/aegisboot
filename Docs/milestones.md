# AegisBoot — Milestones & Release Lifecycle Policy

---

## 1. Milestone Taxonomy

AegisBoot organizes development, upstream tracking, and release deliverables using a structured milestone taxonomy:

| Milestone Type | Naming Format | Purpose & SLA |
|---|---|---|
| **Upstream Sync Cycle** | `cycle-<upstream_version>` (e.g. `cycle-1.0.8`) | Tracks the active upstream minor release development cycle. Closes when upstream releases `v1.0.9`. |
| **Downstream Rollup** | `distro-v<ver>-aegis.<rev>` (e.g. `distro-v1.0.8-aegis.1`) | Tracks specific downstream CI/CD features, security hardening, and tooling bundles. |
| **Emergency Hotfix** | `hotfix-<cve_or_issue>` | Time-bounded milestone (< 24h SLA) for urgent CVE fixes or critical boot regressions. |

---

## 2. Milestone Progression & Transition Gates

A milestone is eligible for completion and closure only when:
1. **100% Gate Success:** All pull requests associated with the milestone have passed the complete CI gate matrix.
2. **Zero Unresolved Conflicts:** All upstream master commits up to the target SHA are cleanly integrated.
3. **Artifact Completeness:** All release packages (`RELEASE`, `DEBUG`, `NOOPT`, SBOM, SLSA provenance, `SHA256SUMS.txt`) are generated and verified.
4. **Documentation Alignment:** `CHANGELOG_DISTRO.md` and version metadata are updated.
