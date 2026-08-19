# Troubleshooting Guide

> **Policy Version:** 1.0.0
> **Status:** Active
> **Last Updated:** 2026-08-19

---

## 1. Quick Diagnostics

### 1.1 Health Check Script

```bash
# Run full environment and repository health check
./scripts/health-check.sh
```

Expected output:
```
=== AegisBoot Health Check ===
Timestamp: 2026-08-19T12:00:00Z

[OK] Git repository: clean
[OK] Origin remote: https://github.com/acidanthera/OpenCorePkg.git
[OK] Fork remote: https://github.com/aegisboot/aegisboot.git
[OK] Upstream connectivity: reachable
[OK] Local HEAD: 170b538b
[OK] Upstream HEAD: 170b538b
[OK] Sync status: IN_SYNC
[OK] Patch stack: 5 patches verified
[OK] Toolchain pins: valid
[OK] CI workflows: 5 workflows configured
[OK] Binaries directory: exists

=== Health Check PASSED ===
```

### 1.2 Environment Validation

```bash
./scripts/check-env.sh
```

---

## 2. Sync Issues

### 2.1 Sync Workflow Not Running

**Symptoms:**
- No sync PR created for > 30 minutes
- Workflow not appearing in Actions tab

**Causes & Fixes:**
| Cause | Fix |
|---|---|
| Cron disabled | Check Settings → Actions → General → "Allow GitHub Actions" |
| Workflow file syntax error | Check `.github/workflows/sync.yml` syntax with `yamllint` |
| Concurrency group stuck | Cancel running workflow in Actions tab |
| Token permissions | Ensure `GITHUB_TOKEN` has `contents: write`, `pull-requests: write` |

**Debug:**
```bash
# Manual dispatch
gh workflow run sync.yml

# Check workflow logs
gh run list --workflow=sync.yml --limit 5
gh run view <run-id> --log
```

### 2.2 Sync PR Not Created / Duplicate PRs

**Symptoms:**
- Upstream has new commits but no PR
- Multiple PRs for same upstream SHA

**Fix:**
```bash
# Check existing PRs
gh pr list --label "sync:upstream" --state open

# The sync workflow has deduplication logic:
# gh pr list --head "sync/upstream-<sha>" --json number
# If PR exists, it updates instead of creating duplicate
```

### 2.3 Patch Stack Verification Fails

**Symptoms:**
- Sync PR labeled `sync:conflict`, `area:patches`
- CI job `patch-stack-verification` fails

**Diagnosis:**
```bash
# Run locally
./scripts/apply-patches.sh --check

# Output shows which patch fails:
# Checking [0001-...]... REJECTED / CONFLICT (in UDK)
```

**Resolution:**
1. Identify conflicting patch
2. Rebase patch onto new upstream HEAD:
   ```bash
   git checkout -b rebase-patches origin/master
   git am Patches/000X-conflicting.patch
   # Resolve conflicts manually
   git am --continue
   git format-patch -1 --stdout > Patches/000X-conflicting.patch
   ```
3. Update patch metadata (Upstream-Status, etc.)
4. Push to sync branch (force-push allowed on sync branches)

### 2.4 Fork Behind Upstream (Beyond Threshold)

**Symptoms:**
- Health check shows: `WARNING: Fork is behind upstream by N commits`
- Alert triggered if behind > 10 commits

**Fix:**
```bash
# Check behind count
git fetch origin master
git rev-list --count HEAD..origin/master

# If sync workflow stuck, manual dispatch:
gh workflow run sync.yml

# If persistent, check workflow logs for failures
```

---

## 3. Build Failures

### 3.1 Build Fails on All Platforms

**Symptoms:**
- All `build.yml` jobs fail
- Usually indicates upstream source issue

**Diagnosis:**
```bash
# Check if upstream build passes
# Visit: https://github.com/acidanthera/OpenCorePkg/actions

# If upstream also fails: upstream issue, wait for fix
# If upstream passes: local environment/patch issue
```

**Common Fixes:**
| Error | Fix |
|---|---|
| `nasm: not found` | Install nasm: `apt-get install nasm` / `brew install nasm` |
| `iasl: not found` | Install iasl: `apt-get install iasl` / `brew install iasl` |
| OpenSSL build fail | Set `HAS_OPENSSL_BUILD=0` on Windows |
| Docker AppArmor | Run `docker-apparmor.sh` script |
| UDK directory corrupt | `rm -rf UDK/ && ./build_oc.tool` |

### 3.2 Build Fails on Specific Platform

**Linux CLANGPDB/GCC/CLANGDWARF:**
- Usually Docker-related
- Check `docker-apparmor.sh` ran
- Verify Docker daemon running
- Check disk space: `df -h`

**macOS XCODE5:**
- Xcode version mismatch
- Check `xcodebuild -version`
- Minimum Xcode 15.0, recommended 16.0
- Homebrew dependencies: `musl-cross`, `mingw-w64`

**Windows VS2022:**
- MSVC not in PATH
- Run from "Developer Command Prompt"
- Or use `TheMrMilchmann/setup-msvc-dev` action
- Chocolatey packages: `make`, `nasm`, `zip`, `iasl`

### 3.3 Build Drift Detected (Non-Reproducible)

**Symptoms:**
- `build-drift-detection` job fails
- `build-drift-report.json` shows differences

**Diagnosis:**
```bash
# Run locally
./scripts/check-build-drift.sh

# Check report
cat build-drift-report.json
```

**Common Causes:**
| Cause | Fix |
|---|---|
| Non-pinned toolchain | Update `toolchains/toolchain-pins.json` |
| Timestamp in binaries | Ensure `SOURCE_DATE_EPOCH` set |
| File ordering non-deterministic | Sort file lists in build scripts |
| Docker base image changed | Pin Docker image by digest |

---

## 4. Static Analysis Failures

### 4.1 ShellCheck Failures

**Symptoms:**
- `analyze.yml` → `analyze-shell-scripts` fails

**Fix:**
```bash
# Run locally
shellcheck -x scripts/*.sh

# Fix reported issues (quote variables, use [[ ]], etc.)
# Common: SC2086 (quote expansions), SC2155 (declare/assign separately)
```

### 4.2 Prospector (Python) Failures

**Symptoms:**
- `analyze.yml` → `analyze-python-scripts` fails

**Fix:**
```bash
# Run locally
pip install prospector
curl -OLf https://raw.githubusercontent.com/acidanthera/ocbuild/master/prospector/profile.yml
prospector . -P ./profile.yml
```

### 4.3 AppleModels Database Desync

**Symptoms:**
- `analyze-shell-scripts` → `Check AppleModels` fails
- `git status --porcelain` shows changes after `update_generated.py`

**Fix:**
```bash
cd AppleModels
python3 ./update_generated.py
git diff
# Commit any legitimate updates
```

### 4.4 Sample.plist Lint Failures

**Symptoms:**
- `Lint Samples` step fails
- Not in Xcode style or alphabetical order

**Fix:**
```bash
# The CI step auto-fixes, but local fix:
plutil -lint Docs/Sample.plist
/usr/libexec/PlistBuddy -c 'Save' Docs/Sample.plist
# Re-run awk formatting from analyze.yml
```

---

## 5. CI Validation Gate Failures

### 5.1 Workflow Integrity Tests Fail

**Symptoms:**
- `ci.yml` → `workflow-integrity` fails

**Fix:**
```bash
# Run locally
python -m unittest tests/test_workflow_integrity.py
python -m unittest tests/test_validator_unit.py

# Check: validate_workflows.py --strict
python scripts/validate_workflows.py --strict
```

### 5.2 Formatting Failures

**Symptoms:**
- `ci.yml` → `formatting` fails

**Fix:**
```bash
# Python syntax
python -m py_compile scripts/*.py tests/*.py

# Shell syntax
for script in scripts/*.sh; do bash -n "$script"; done
```

### 5.3 Secret Scanning Failures

**Symptoms:**
- `ci.yml` → `license-and-secrets` fails

**Fix:**
```bash
# Scan locally
grep -rnEI --exclude-dir=".git" "(ghp_[A-Za-z0-9]{36}|BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY)" .

# Remove any detected secrets
# Rotate compromised tokens immediately
```

### 5.4 Policy & Metadata Test Failures

**Symptoms:**
- `ci.yml` → `policy-and-metadata-tests` fails

**Fix:**
```bash
python -m unittest tests/test_distribution_policies.py
python -m unittest tests/test_version_metadata.py
python -m unittest tests/test_patch_stack.py
```

---

## 6. QEMU Boot Test Failures

### 6.1 QEMU/OVMF Not Found

**Symptoms:**
- `qemu-boot-test` fails at install step

**Fix:**
```bash
# Ubuntu
sudo apt-get update && sudo apt-get install -y qemu-system-x86 ovmf

# macOS
brew install qemu
# OVMF: brew install edk2-ovmf (or use built-in)

# Verify
qemu-system-x86_64 --version
ls /usr/share/ovmf/  # or /opt/homebrew/share/ovmf/
```

### 6.2 Boot Test Hangs / Times Out

**Symptoms:**
- Test runs but times out (20 min default)
- No output in boot log

**Diagnosis:**
```bash
# Run manually with longer timeout
timeout 60 qemu-system-x86_64 \
  -bios /usr/share/ovmf/OVMF.fd \
  -drive file=fat:rw:Binaries/EFI,format=raw \
  -nographic -serial stdio 2>&1 | tee boot.log

# Check boot.log for:
# - "OpenCore" banner
# - Boot picker
# - Kernel load
```

**Common Fixes:**
| Issue | Fix |
|---|---|
| OVMF path wrong | Find correct path: `find / -name "OVMF.fd" 2>/dev/null` |
| EFI partition not found | Ensure `Binaries/EFI` structure correct |
| Memory too low | Add `-m 2G` |
| CPU flags | Add `-cpu qemu64,+ssse3,+sse4.1,+sse4.2,+popcnt` |

### 6.3 Boot Regression (Functional Failure)

**Symptoms:**
- QEMU boots but OpenCore fails (no picker, panic, etc.)

**Diagnosis:**
- Compare with upstream build
- Check if patch introduces regression
- Verify Config.plist valid with `ocvalidate`

---

## 7. Release Failures

### 7.1 Release Workflow Not Triggering

**Symptoms:**
- Tag pushed but no release created

**Causes:**
| Cause | Fix |
|---|---|
| Tag format wrong | Must match `v*` (e.g., `v1.0.8-aegis.1+170b538`) |
| Workflow permissions | `contents: write` required |
| Concurrency group stuck | Cancel previous release run |

### 7.2 Artifact Upload Fails

**Symptoms:**
- Release created but missing assets

**Fix:**
- Check `Binaries/` has `.zip` files
- Verify `verify-distro.sh` generated checksums
- Check GitHub Actions logs for upload errors

### 7.3 SBOM / Provenance Generation Fails

**Symptoms:**
- `release.yml` fails at SBOM/provenance step

**Fix:**
- SBOM is currently a placeholder template
- For production: integrate `syft` or `cyclonedx-cli`
- Provenance: requires SLSA GitHub Generator

---

## 8. Patch Management Issues

### 8.1 Patch Won't Apply

**Symptoms:**
- `apply-patches.sh --check` shows `REJECTED / CONFLICT`

**Resolution:**
```bash
# 1. Identify the conflicting patch
# 2. Create test branch from upstream
git checkout -b test-patch origin/master

# 3. Try apply with verbose output
git am --3way Patches/000X-failing.patch

# 4. Resolve conflicts in affected files
# 5. git am --continue
# 6. Generate updated patch
git format-patch -1 --stdout > Patches/000X-failing.patch

# 7. Update patch metadata
```

### 8.2 Patch Already Applied (False Positive)

**Symptoms:**
- Script reports `ALREADY_APPLIED` but patch not in history

**Fix:**
```bash
# Check if patch content matches current tree
git apply --check Patches/000X.patch  # Should pass if already applied

# Or verify with reverse check
git apply --reverse --check Patches/000X.patch
```

### 8.3 Patch Stack Growing Unbounded

**Symptoms:**
- Many patches accumulating in `Patches/`
- No retirement happening

**Process:**
1. Review each patch monthly
2. Check upstream status (PR merged? issue closed?)
3. Retire merged patches immediately
4. Escalate stuck patches to upstream maintainers

---

## 9. Git & Remote Issues

### 9.1 Wrong Remote Configuration

**Symptoms:**
- Pushing to upstream instead of fork
- Fetching from wrong remote

**Fix:**
```bash
# Verify remotes
git remote -v

# Should be:
# origin  https://github.com/acidanthera/OpenCorePkg.git (fetch)
# fork    https://github.com/aegisboot/aegisboot.git   (push)

# Fix if wrong:
git remote set-url origin https://github.com/acidanthera/OpenCorePkg.git
git remote set-url fork https://github.com/aegisboot/aegisboot.git
```

### 9.2 Force Push Blocked on Main

**Symptoms:**
- `git push fork main --force` rejected

**Expected:** This is CORRECT behavior. Branch protection on `main` blocks force pushes.

**Resolution:** Never force-push to `main`. Use sync branch workflow.

### 9.3 Diverged History

**Symptoms:**
- Local and upstream have different history
- `git status` shows "diverged"

**Fix:**
```bash
# If local has NO valuable commits (only sync commits):
git fetch origin master
git reset --hard origin/master
git push fork main --force-with-lease  # Only if you're sure

# If local has valuable commits:
# Create sync branch, PR, go through normal process
```

---

## 10. Docker Issues

### 10.1 Docker Compose Fails

**Symptoms:**
- `docker compose run build-oc` fails

**Fixes:**
| Error | Fix |
|---|---|
| AppArmor | Run `docker-apparmor.sh` |
| Permission denied | `sudo usermod -aG docker $USER && newgrp docker` |
| No space left | `docker system prune -af` |
| Image pull fails | Check network, try `docker pull` manually |

### 10.2 Build in Docker Hangs

**Symptoms:**
- Container runs but no output

**Fix:**
```bash
# Run with TTY
docker compose run --rm -T build-oc

# Or check container logs
docker compose logs build-oc
```

---

## 11. Version Metadata Issues

### 11.1 Version Extraction Fails

**Symptoms:**
- `generate-version-metadata.py` returns default "1.0.8"

**Fix:**
```bash
# Check header exists
ls -la Include/Acidanthera/Library/OcMainLib.h

# Check version macro
grep OPEN_CORE_VERSION Include/Acidanthera/Library/OcMainLib.h

# Run with debug
python3 scripts/generate-version-metadata.py --repo-root . --output /tmp/test.json
cat /tmp/test.json
```

### 11.2 Distro Version Format Wrong

**Symptoms:**
- Release tag doesn't match expected format

**Expected:** `v<upstream>-aegis.<rev>+<sha>`

**Fix:** Ensure `generate-version-metadata.py` runs in release workflow before tagging.

---

## 12. Emergency Procedures

### 12.1 Critical Boot Regression in Release

**Immediate Actions:**
1. **Yank release:** Mark as pre-release, add `[YANKED]` to title
2. **Redeploy known-good:** Tag previous working commit as new downstream revision
3. **Investigate:** Bisect to find breaking commit
4. **Patch:** Create workaround patch if upstream fix not available
5. **Communicate:** Post incident report

### 12.2 Upstream Force-Push Detected

**Immediate Actions:**
1. **Stop sync workflow:** Disable cron temporarily
2. **Assess damage:** `git log --oneline HEAD..origin/master` vs `origin/master..HEAD`
3. **Coordinate:** Contact upstream if possible
4. **Recover:** Manual reconciliation required

### 12.3 Compromised CI Token

**Immediate Actions:**
1. **Revoke token:** Settings → Developer settings → Personal access tokens
2. **Rotate secrets:** Update all `GITHUB_TOKEN` / `GH_TOKEN` references
3. **Audit:** Check workflow logs for unauthorized access
4. **Report:** GitHub Security if needed

---

## 13. Getting Help

### 13.1 Internal Resources

| Resource | Location |
|---|---|
| Health check | `./scripts/health-check.sh` |
| Environment check | `./scripts/check-env.sh` |
| Policy docs | `docs/*.md` |
| CI logs | GitHub Actions tab |

### 13.2 External Resources

| Resource | URL |
|---|---|
| OpenCorePkg Issues | https://github.com/acidanthera/OpenCorePkg/issues |
| OpenCorePkg Discussions | https://github.com/acidanthera/OpenCorePkg/discussions |
| Dortania Install Guide | https://dortania.github.io/OpenCore-Install-Guide/ |
| EDK II Docs | https://github.com/tianocore/edk2/tree/master/Docs |
| GitHub Actions Docs | https://docs.github.com/en/actions |

### 13.3 Reporting Issues

Use the appropriate template:
- **Bug:** `.github/ISSUE_TEMPLATE/bug_report.yml`
- **Feature:** `.github/ISSUE_TEMPLATE/feature_request.yml`
- **Sync Conflict:** `.github/ISSUE_TEMPLATE/sync_issue.yml`

---

## 14. Common Command Reference

```bash
# Sync manually
./scripts/sync-upstream.sh

# Check patches
./scripts/apply-patches.sh --check

# Apply patches
./scripts/apply-patches.sh

# Verify distribution
./scripts/verify-distro.sh

# Generate version metadata
python3 scripts/generate-version-metadata.py --output Binaries/distro-version.json

# Check build drift
./scripts/check-build-drift.sh

# Health check
./scripts/health-check.sh

# Environment check
./scripts/check-env.sh

# Run unit tests
python -m unittest discover -s tests

# Validate workflows
python scripts/validate_workflows.py --strict

# List sync PRs
gh pr list --label "sync:upstream" --state open

# View latest workflow run
gh run list --workflow=sync.yml --limit 1
gh run view <run-id> --log
```

---

## 15. Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-08-19 | Initial troubleshooting guide |