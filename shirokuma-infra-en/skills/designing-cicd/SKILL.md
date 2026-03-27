---
name: designing-cicd
description: Designs CI/CD pipeline architecture. Covers GitHub Actions workflow configuration design, deployment strategy selection (Blue/Green, Rolling, Canary), environment isolation design (dev/staging/prod), and OIDC authentication design. Triggers: "CI/CD design", "pipeline design", "deployment strategy design", "GitHub Actions design", "environment isolation design", "deploy architecture".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# CI/CD Pipeline Design

Design GitHub Actions CI/CD pipeline architecture, deployment strategy selection, and environment isolation.

> **Scope boundary:** `coding-cicd` handles GitHub Actions workflow file implementation, while this skill handles pipeline configuration design decisions — what to design and how.

## Scope

- **Category:** Investigation Worker
- **Scope:** Reading existing workflow files (Read / Grep / Glob / Bash read-only commands), generating CI/CD design documents (Write/Edit — for design artifacts), appending design sections to Issue bodies.
- **Out of scope:** GitHub Actions workflow file implementation (delegated to `coding-cicd`), CDK construct design (delegated to `designing-cdk`), AWS resource design (delegated to `designing-aws`)

> **Writing design artifacts**: When this skill uses Write/Edit on Issue bodies or design documents, it is producing design process outputs — not modifying production code. This is a permitted exception for Investigation Workers.

## Workflow

### 0. Check Existing CI/CD Configuration

**First**, read the project `CLAUDE.md` and existing files:

- Contents of the existing `.github/workflows/` directory
- Deployment target (AWS ECS / Lambda / Vercel, etc.)
- Branch strategy (develop / staging / main, etc.)
- Package manager and lock file in use

```bash
ls -la .github/workflows/ 2>/dev/null
cat .github/workflows/*.yml 2>/dev/null | head -50
```

### 1. Design Context Check

When delegated from `design-flow`, a Design Brief and requirements are passed. Use them as-is.

When invoked standalone, understand design requirements from the Issue body and plan section.

### 2. Pipeline Configuration Design

#### Workflow Classification

| Workflow | Trigger | Purpose |
|---------|---------|---------|
| CI (test) | PR, push | Quality checks: lint → test → build |
| CD (deploy) | main/develop merge | Environment-specific deployment |
| Manual run | workflow_dispatch | Hotfix, rollback |
| Scheduled | cron | Periodic security scans, etc. |

#### CI Pipeline Design

| Job | Run Condition | Can Parallelize |
|-----|-------------|----------------|
| lint | All PRs | Yes (parallel with test) |
| typecheck | All PRs | Yes |
| test | All PRs | Yes (parallel with lint) |
| build | After lint + test pass | No (dependent) |
| security-scan | cron / PR | Yes |

#### CD Pipeline Design

| Environment | Trigger | Approval Flow |
|------------|---------|--------------|
| dev | develop branch merge | None (automatic) |
| staging | develop merge or manual | Optional |
| prod | main branch merge | Required (manual approval) |

### 3. Deployment Strategy Selection

#### Strategy Comparison

| Strategy | Description | Downtime | Rollback Speed | Best For |
|---------|-------------|---------|---------------|---------|
| Rolling | Incrementally replace old version | None | Slow | Standard app updates |
| Blue/Green | Switch between parallel environments | None | Fast | Production zero-downtime requirement |
| Canary | Gradually shift traffic | None | Fast | High-risk changes, A/B testing |
| Recreate | Stop all, then start | Yes | N/A | DB migrations, etc. |

#### Selection Criteria

```
High availability required → Blue/Green or Canary
Gradual release required → Canary
Cost-focused / simple → Rolling
Involves DB schema changes → Recreate (with maintenance window)
```

### 4. Environment Isolation Design

#### GitHub Environments Design

| Environment Name | Protection Rules | Secrets |
|----------------|-----------------|---------|
| `dev` | None | `DEV_ROLE_ARN` |
| `staging` | Optional (reviewer approval) | `STAGING_ROLE_ARN` |
| `production` | Required (reviewer approval) | `PROD_ROLE_ARN` |

#### OIDC Authentication Design

Obtain temporary credentials via OIDC federation without using IAM access keys:

```
GitHub Actions → OIDC token issued → AWS STS (AssumeRoleWithWebIdentity) → Temporary credentials
```

Add `token.actions.githubusercontent.com` to the IAM role trust policy.

### 5. Design Output

```markdown
## CI/CD Pipeline Design

### Workflow List
| Filename | Trigger | Role |
|---------|---------|------|
| `ci.yml` | PR, push | CI (lint/test/build) |
| `cd.yml` | main merge | CD (environment-specific deploy) |

### CI Job Design
| Job Name | Parallel Group | Success Condition |
|---------|--------------|------------------|
| {job} | {group} | {condition} |

### CD Environment-Specific Deploy Design
| Environment | Deploy Target | Strategy | Approval |
|------------|-------------|---------|---------|
| {env} | {target} | {strategy} | {approval} |

### OIDC Role Design
| Environment | Role ARN Pattern | Minimum Permission Scope |
|------------|----------------|------------------------|
| {env} | `arn:aws:iam::{account}:role/{role}` | {scope} |

### Key Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| {topic} | {content} | {reason} |
```

### 6. Review Checklist

- [ ] OIDC authentication is used; no long-term IAM credentials stored as secrets
- [ ] `permissions` follows least privilege (`id-token: write`, `contents: read`)
- [ ] Manual approval is configured for the prod environment
- [ ] Job parallelism optimizes CI runtime
- [ ] Lock file is used for cache key (`cache-dependency-path`)
- [ ] `needs:` dependencies are correct
- [ ] Branch strategy aligns with CD triggers

## Next Steps

When called via `design-flow`, control automatically returns to the orchestrator.

When invoked standalone:

```
CI/CD pipeline design complete. Next steps:
-> Implement GitHub Actions workflows with coding-cicd skill
-> Use /design-flow for a full design workflow
```

## Notes

- **Do not generate workflow files** — Output design documents only. YAML implementation is `coding-cicd`'s responsibility
- **Do not venture into CDK deploy details** — Delegate to `designing-cdk` if CDK construct design is needed
- Confirm with the user during design if auto-deploying to prod (without manual approval) is intended
- The `environment:` name in GitHub Actions must exactly match the environment name in GitHub Settings
