# ADR-004: Impact Classification Rules

## Status
Accepted

## Context
We need automated classification of upstream sync impact to determine if a release should be triggered. The classification must be deterministic and based on changed file paths.

## Decision
**Impact Levels (priority order):**

| Level | Value | Triggers Release | Criteria |
|-------|-------|------------------|----------|
| Critical | 5 | ✅ | Security fixes, boot regressions, core library changes (OcMainLib, OcGuardLib, OcCryptoLib, etc.) |
| Major | 4 | ✅ | Breaking API changes, new drivers, architecture shifts |
| Minor | 3 | ✅ | New features, significant enhancements, new drivers |
| Patch | 2 | ✅ | Bug fixes, small enhancements |
| Infrastructure | 1 | ❌ | CI/CD, Docker, tooling, docs only |
| None | 0 | ❌ | Documentation, comments, whitespace only |

**Classification Algorithm (`scripts/classify-impact.py`):**
1. Run `git diff --name-only HEAD..upstream/master`
2. For each file, match against path patterns in priority order:
   - Security/core libs → Critical
   - Breaking API paths → Major
   - New feature paths → Minor
   - Bug fix paths → Patch
   - CI/tooling/docs → Infrastructure
   - Docs only → None
3. Return highest priority level found

**Path Patterns:**
- Critical: `Library/OcMainLib`, `Library/OcGuardLib`, `Library/OcCryptoLib`, `Library/OcAppleSecureBootLib`, `Library/OcVaultLib`
- Major: `Include/*.h`, `Library/*Lib.c`, `Platform/*`, `Drivers/*`
- Minor: New files in `Drivers/`, `Library/`, `Platform/`
- Patch: Modified files in `Library/`, `Platform/` (not matching critical)
- Infrastructure: `.github/*`, `scripts/*`, `toolchains/*`, `tests/*`, `Dockerfiles/*`, `docs/*`
- None: `*.md`, `CHANGELOG*`, `README*`

## Consequences
**Positive:**
- Fully automated, no human judgment needed
- Deterministic and repeatable
- Release only when warranted
- Clear audit trail in PR body

**Negative:**
- Path-based heuristic may misclassify (mitigated by priority ordering)
- Requires maintenance when new critical paths added

## Implementation References
- `scripts/classify-impact.py` - Classification algorithm
- `.github/workflows/sync.yml` - Integrates classifier, applies label
- `.github/workflows/release-trigger.yml` - Uses impact label for release decision