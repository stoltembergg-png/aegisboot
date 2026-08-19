# ADR-010: Observability and Alerting

## Status
Accepted

## Context
We need visibility into the health and performance of the continuous integration system without manual monitoring.

## Decision
**Health Check (`scripts/health-check.sh`):**
- Runs every 15 min via cron (can be scheduled separately)
- Checks: upstream connectivity, HEAD SHAs, patch stack, toolchain pins, version metadata
- Output: HEALTHY / ATTENTION REQUIRED
- Exit code 0/1 for automation

**Metrics Collector (`scripts/collect-metrics.py`):**
- Outputs JSON or Prometheus exposition format
- Collects: git (HEAD, upstream, behind count), patches, build, CI, system
- CI metrics via `gh` CLI (recent runs, success rate)
- System: disk, platform, python version

**Key Metrics:**
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Sync latency | < 15 min | > 30 min |
| Pipeline duration | < 30 min | > 45 min |
| Pipeline success rate | > 98% | < 95% |
| Time to merge | < 1 hour | > 2 hours |
| Behind count | 0 | > 10 commits |
| Patch validity | 100% | < 100% |
| QEMU boot pass | 100% | < 100% |

**Alerting:**
- Sync workflow: `::warning` if behind > 10 commits
- Health check: non-zero exit triggers alert (external scheduler)
- Metrics: external Prometheus/Grafana (not implemented in-repo)

**GitHub Actions Integration:**
- Workflow run conclusions visible in Actions tab
- `release-trigger.yml` logs release decisions
- `sync.yml` logs behind count warnings

## Consequences
**Positive:**
- Comprehensive health visibility
- Automated detection of drift/failures
- Machine-readable metrics for external systems
- Low overhead (scripts are lightweight)

**Negative:**
- No built-in alerting system (requires external)
- Metrics collection depends on `gh` CLI auth
- Windows platform metrics limited

## Implementation References
- `scripts/health-check.sh` - Health check script
- `scripts/collect-metrics.py` - Metrics collector (JSON/Prometheus)
- `scripts/sync-labels.py` - Label sync for GitHub
- `.github/workflows/sync.yml` - Behind count warnings
- `docs/troubleshooting.md` - Operational guide