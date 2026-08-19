# ADR-001: Branch Model and Merge Strategy

## Status
Accepted

## Context
We need a clear branch model for the AegisBoot fork that:
- Keeps `main`/`master` stable and protected
- Allows automated sync branches for upstream integration
- Supports local patch development
- Enables release tagging
- Prevents history rewriting on protected branches

## Decision
**Branch Structure:**
| Branch | Purpose | Protection |
|--------|---------|------------|
| `master` | Primary branch (upstream tracking) | Force push blocked, direct push blocked, required status checks |
| `sync/upstream-<short_sha>` | Temporary sync branches (auto-created) | Auto-deleted after merge |
| `patches/<name>` | Local patch development | Force push blocked |
| `release/<version>` | Release preparation | Protected |
| `rollback/<tag>-<timestamp>` | Emergency rollback | Temporary |

**Merge Strategy:**
- All merges to `master` use **squash merge**
- Commit message format: `sync: merge upstream <sha> (<date>)`
- No fast-forward, no rebase on `master`
- Auto-merge enabled when all required checks pass

**Branch Protection Rules (on `master`):**
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Restrict who can push to matching branches (only GitHub Actions bot)
- Block force pushes
- Block deletions

## Consequences
**Positive:**
- Clean, linear history on `master`
- Every sync is traceable to a single commit
- No history rewriting on protected branch
- Automated merges are safe and auditable

**Negative:**
- Individual upstream commits are squashed (but upstream SHA preserved in commit message)
- Requires CI to pass before any merge (no emergency bypass)

## Implementation References
- `.github/workflows/sync.yml` - Creates sync branches, squash merges
- `.github/workflows/ci.yml` - Required status checks
- `.github/workflows/release-trigger.yml` - Triggers releases on merged sync PRs
- Branch protection configured via GitHub Settings