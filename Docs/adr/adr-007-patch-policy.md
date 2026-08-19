# ADR-007: Local Patch Stack Policy

## Status
Accepted

## Context
Local patches are temporary modifications needed until upstream merges them. We need a policy that keeps patches minimal, tracked, and automatically validated.

## Decision
**Patch Requirements:**
- Stored in `Patches/` as `.patch` files (git format-patch output)
- Sequential naming: `0001-<component>-<description>.patch`
- Must include headers:
  - `Upstream-Status`: Submitted | Accepted | Backport | Workaround | Pending
  - `Upstream-Issue` or `Upstream-PR`: Link to upstream tracking
  - `Signed-off-by`: DCO compliance

**Lifecycle:**
```
Creation → Upstream PR → Local Maintenance → Upstream Merge → Retirement
```

**Validation:**
- `scripts/apply-patches.sh --check` runs on every sync PR
- Validates all patches apply cleanly to current upstream HEAD
- Blocks sync if any patch fails (labels PR `sync:conflict`, `area:patches`)
- Pre-UDK bootstrap: syntax-only validation
- Post-UDK: live application test in UDK tree

**Retirement:**
- Remove patch file when upstream merges
- Commit: `patch: retire <name> — merged upstream as <sha>`
- Update `Patches/README.md` index

**Prohibited:**
- Direct commits to OpenCore source (use patches only)
- Patches without Upstream-Status
- Cosmetic/preference patches
- Force-push to resolve conflicts

## Consequences
**Positive:**
- Minimal patch surface
- Automatic conflict detection
- Transparent upstream tracking
- Automatic retirement workflow

**Negative:**
- Adds overhead for local changes
- Requires upstream PR for every patch

## Implementation References
- `docs/local-patch-policy.md` - Full policy
- `scripts/apply-patches.sh` - Idempotent apply/check
- `.github/workflows/ci.yml` → `patch-stack-verification` gate
- `.github/workflows/sync.yml` → Pre-sync patch check
- `Patches/` - Patch directory