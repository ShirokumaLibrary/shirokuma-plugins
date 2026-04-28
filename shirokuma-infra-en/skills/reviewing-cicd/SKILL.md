---
name: reviewing-cicd
description: Reviews GitHub Actions workflow files. Covers deployment strategies, secret management, permission design, and job configuration. Triggers: "CICD review", "GitHub Actions review", "workflow review", "cicd review", "deployment pipeline review".
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# CI/CD Pipeline Code Review

Review GitHub Actions workflows. Focus on security (secret management / permissions), deployment strategies, and efficiency (caching / parallelism).

## Scope

- **Category:** Investigation Worker
- **Scope:** GitHub Actions workflow file reading (Read / Grep / Glob / Bash read-only), generating review reports. No code modifications.
- **Out of scope:** Workflow modifications (delegate to `coding-cicd`), actual deployment execution

## Review Criteria

### Security (Secret Management)

| Check | Issue | Fix |
|-------|-------|-----|
| Secret logging | `echo ${{ secrets.KEY }}` | Do not echo secrets |
| Secret exposure via ENV | `env: SECRET: ${{ secrets.KEY }}` set on all jobs | Limit to required jobs only |
| Hardcoded values | API keys / passwords written in workflow | Use GitHub Secrets |
| `pull_request_target` | Risk of secret leakage on fork PRs | Use `pull_request`, or control carefully |
| Unpinned third-party actions | `uses: actions/checkout@v3` | Pin with SHA (e.g., `@abc1234`) |

### Permission Design

| Check | Issue | Fix |
|-------|-------|-----|
| Excessive `permissions` | `permissions: write-all` | Explicitly specify minimum permissions (`contents: read` etc.) |
| GITHUB_TOKEN scope | Broad default scope | Restrict `permissions` per job |
| OIDC not used | Long-lived AWS credentials stored in Secrets | Use `aws-actions/configure-aws-credentials` + OIDC |

### Job Configuration / Efficiency

| Check | Issue | Fix |
|-------|-------|-----|
| Dependency caching | Full `npm install` every time | Cache `node_modules` with `actions/cache` |
| Parallel execution | Test / lint / build running serially | Set `needs` correctly for parallelism |
| Matrix strategy | Manually repeating tests for multiple environments | Use `strategy.matrix` |
| Timeout | `timeout-minutes` not set | Default 360 min is too long; set appropriate value |
| Failure artifacts | Cannot retrieve logs on test failure | Upload artifacts with `if: failure()` |

### Deployment Strategy

| Check | Issue | Fix |
|-------|-------|-----|
| Environment-based deploys | Direct prod deploy on push to `main` | Use `environment` with approver configuration |
| Rollback strategy | No rollback procedure | Document rollback to previous version |
| No Blue/Green | Deployment with downtime | Consider ECS Blue/Green / Lambda alias switching |
| No canary deploy | Switching all traffic at once | Consider phased deploy (10% → 50% → 100%) |
| Drift detection | No drift check after CDK deploy | Add `cdk diff` as post-deploy step |

### CDK Specific

| Check | Issue | Fix |
|-------|-------|-----|
| `cdk bootstrap` | Executing every time | Run only on first time (idempotent but slow) |
| `--require-approval` | Requesting interactive approval | Use `--require-approval never` in CI |
| `--all` flag | Always deploying all stacks | Target only changed stacks |
| CloudFormation failure | Not verifying rollback on deploy failure | Do not use `--no-rollback` |

### Code Quality

| Check | Issue | Fix |
|-------|-------|-----|
| Lint / type check | No lint in CI | Add `pnpm lint` / `tsc --noEmit` to jobs |
| Tests | No or skipped tests | Make test job required |
| Build verification | Deploying without build step | Enforce build → test → deploy order |
| Security scan | No dependency vulnerability check | Add `npm audit` / `pnpm audit` |

## Workflow

### 1. Identify Target Files

```bash
# Check GitHub Actions workflows
find .github/workflows -name "*.yml" -o -name "*.yaml" | head -20

# Check secret usage
grep -r "secrets\." .github/workflows/ | head -20

# Check OIDC configuration
grep -r "aws-actions/configure-aws-credentials" .github/workflows/ | head -10
```

### 2. Code Analysis

Read workflow files and apply the review criteria tables.

Priority check order:
1. Secret leakage risk
2. Permission minimization (OIDC usage)
3. Deployment strategy safety
4. CI efficiency (caching / parallelism)

### 3. Generate Report

```markdown
## Review Summary

### Issue Summary
| Severity | Count |
|----------|-------|
| Critical | {n} |
| High | {n} |
| Medium | {n} |
| Low | {n} |
| **Total** | **{n}** |

### Critical Issues
{List secret leakage / excessive permission issues}

### Improvements
{List CI efficiency / deployment strategy improvement suggestions}
```

### 4. Save Report

When PR context is present:
```bash
shirokuma-docs issue comment {PR#} --file /tmp/shirokuma-docs/review-cicd.md
```

When no PR context:
```bash
# Set title: "[Review] cicd: {target}" and category: Reports in frontmatter first
shirokuma-docs discussion add --file /tmp/shirokuma-docs/review-cicd.md
```

## Review Verdict

- **PASS**: `**Review result:** PASS` — No critical issues
- **FAIL**: `**Review result:** FAIL` — Critical/High issues found (secret leakage / `permissions: write-all`, etc.)

## Notes

- **Do not modify code** — Report findings only
- GitHub Actions versions update frequently. Suggesting upgrades like `@v3` → `@v4` is appropriate
- OIDC-based AWS authentication is more secure than long-lived credentials — always recommend it
