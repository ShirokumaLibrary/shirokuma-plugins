---
name: coding-cicd
description: Helps build and modify CI/CD pipelines. On first use, confirms and records the project's CI/CD approach. Provides GitHub Actions templates (CI: lint→test→build, CD: dev→staging→prod environment-specific deploy). Has a clear boundary with coding-cdk. Triggers: "CI/CD", "GitHub Actions", "pipeline", "deploy workflow", "ci-test", "cd-deploy", "deploy automation".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TaskGet, TaskList
---

# CI/CD Coding

Helps build and modify CI/CD pipelines. On first use, confirms and records the project's CI/CD approach, then guides implementation using GitHub Actions templates.

## Scope

- **Category:** Mutation worker
- **Scope:** GitHub Actions workflow file implementation and modification (Write / Edit / Bash). Covers both CI (test/build) and CD (environment-specific deploy) workflows.
- **Out of scope:** AWS resource design (delegated to `designing-aws`), CDK construct implementation (delegated to `coding-cdk`), local environment setup with docker-compose (delegated to `coding-infra`)

### Boundary with coding-cdk

| Responsibility | Skill |
|----------------|-------|
| CDK diff/deploy job only | `coding-cdk` (see `templates/github-actions-cdk.yml.template`) |
| Full CI pipeline (lint/test/build) | `coding-cicd` (this skill) |
| Full CD pipeline (environment-specific deploy) | `coding-cicd` (this skill) |
| CDK deploy steps within CD | `coding-cicd` cross-references `coding-cdk` template |

## Before Starting

1. Check `CLAUDE.md` or `designing-aws` design artifacts for an existing CI/CD policy
2. Review existing `.github/workflows/` directory to avoid duplicate workflows
3. Review OIDC authentication setup in [patterns/github-actions-patterns.md](patterns/github-actions-patterns.md)

## Workflow

### Step 1: Confirm CI/CD Approach

Check whether a CI/CD policy is already recorded in `CLAUDE.md`, the Issue body, or `designing-aws` design artifacts.

**If policy exists** → Follow the recorded policy and proceed to Step 2.

**If no policy exists** → Use AskUserQuestion to confirm:

| Item | Example Options |
|------|----------------|
| CI/CD tool | GitHub Actions / CircleCI / GitLab CI / Jenkins / Not needed (manual deploy) |
| CI scope | lint + test + build / test only / not needed |
| CD scope | Environment-specific auto-deploy / manual deploy / not needed |
| Deploy target | AWS (ECS / Lambda / S3) / Vercel / other |
| Environments | dev + staging + prod / dev + prod / prod only |

After confirmation, ask the user where to record the policy (`CLAUDE.md` tech stack section / Issue body / other). Record the decision and proceed to Step 2.

> **If CI/CD is not needed**: If the user decides CI/CD is unnecessary, record that decision and stop. Do not push CI/CD adoption.

### Step 2: Review Existing Configuration

```bash
# Check existing workflows
ls -la .github/workflows/ 2>/dev/null || echo "No workflows found"

# Check package manager and scripts
cat package.json | grep -E '"(test|build|lint|typecheck)'

# Check Node.js version
cat .nvmrc 2>/dev/null || cat .node-version 2>/dev/null || echo "No version file"
```

Items to verify:
- Duplicate/conflicting existing workflows
- Test, build, and lint command names
- Package manager (npm / pnpm / yarn)
- Lock file for cache configuration

### Step 3: Implementation Plan

Create a progress tracker with TaskCreate.

```markdown
## Implementation Plan

### Files to Create/Modify
- [ ] `.github/workflows/ci.yml` - CI workflow (lint/test/build)
- [ ] `.github/workflows/cd.yml` - CD workflow (environment-specific deploy)

### Verification
- [ ] GitHub Environments setup (dev/staging/production)
- [ ] OIDC role ARN Secrets configuration
- [ ] Branch strategy (develop→dev, main→staging/prod)
- [ ] Alignment with coding-cdk template when CDK deploy is included
```

### Step 4: Implementation

Implement with reference to patterns:

- Deploy strategy selection: [patterns/deploy-strategies.md](patterns/deploy-strategies.md)
- GitHub Actions patterns (OIDC, cache, Reusable Workflows): [patterns/github-actions-patterns.md](patterns/github-actions-patterns.md)

CI workflow template: [templates/ci-test-build.yml.template](templates/ci-test-build.yml.template)

CD workflow template: [templates/cd-deploy.yml.template](templates/cd-deploy.yml.template)

When including CDK deploy in CD: Reference `coding-cdk`'s `templates/github-actions-cdk.yml.template` and integrate the deploy job

**Implementation checklist**:
- Use OIDC authentication; never store IAM access keys in Secrets
- Minimize `permissions` scope (`id-token: write`, `contents: read`, etc.)
- Specify `cache-dependency-path` with lock file to enable caching
- Set approval flow via `environment:` key using GitHub Environments

### Step 5: Validation

```bash
# YAML syntax check (if actionlint is installed)
actionlint .github/workflows/*.yml 2>/dev/null || echo "actionlint not installed"

# Manually review workflow syntax
cat .github/workflows/ci.yml
cat .github/workflows/cd.yml
```

Validation checklist:
- `on:` triggers are set to intended branches and paths
- `needs:` job dependencies are correct
- `environment:` references the correct environment name (must match GitHub settings)
- Secret names (`secrets.DEPLOY_ROLE_ARN`, etc.) are consistent

### Step 6: Completion Report

Record changes as a comment on the Issue.

## Reference Documents

| Document | Content | When to Read |
|----------|---------|-------------|
| [patterns/deploy-strategies.md](patterns/deploy-strategies.md) | Blue/Green, Rolling, Canary strategy comparison; GitHub Environments approval flow; rollback procedures | When selecting deploy strategy |
| [patterns/github-actions-patterns.md](patterns/github-actions-patterns.md) | OIDC authentication setup, cache strategy, Reusable Workflows, secrets management | When implementing workflows |
| [templates/ci-test-build.yml.template](templates/ci-test-build.yml.template) | lint→test→build CI pipeline template | When creating CI workflow |
| [templates/cd-deploy.yml.template](templates/cd-deploy.yml.template) | dev→staging→prod environment-specific deploy template | When creating CD workflow |

## Quick Commands

```bash
# List workflow files
ls -la .github/workflows/

# Local validation with actionlint (requires installation)
brew install actionlint && actionlint

# Local execution with act (requires installation)
act pull_request --dry-run

# Check workflow run status with GitHub CLI
gh run list --limit 10
gh run view {run-id}
```

## Next Steps

When invoked standalone (not via `implement-flow` chain):

```
Implementation complete. Next step:
→ `/commit-issue` to stage and commit your changes
```

## Notes

- **Never embed IAM access keys in code** — Use OIDC authentication; never use long-term credentials
- **Minimum `permissions` scope** — Explicitly grant only required scopes
- **Cross-reference `coding-cdk` template for CDK deploy steps** — Don't implement independently
- **Environment names must match GitHub Environments** — `environment: dev` must exactly match the GitHub environment name
- **prod approval is mandatory** — Always configure manual approval for production environment
- **Specify lock file in `cache-dependency-path`** — Use `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` to enable caching
