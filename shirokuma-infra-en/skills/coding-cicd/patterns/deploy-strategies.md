# Deploy Strategy Patterns

## Strategy Comparison Matrix

| Strategy | Overview | Downtime | Rollback Speed | Complexity | Recommended Use Case |
|----------|----------|----------|----------------|------------|---------------------|
| Rolling | Gradually replace old version with new version | None (ECS/K8s) | Medium (re-deploy) | Low | Standard container services |
| Blue/Green | Run old (Blue) and new (Green) in parallel, switch DNS | None | Fast (DNS switch) | Medium | Zero-downtime required, rollback critical |
| Canary | Gradually shift traffic (5%→25%→100%) to new version | None | Medium (reweight) | High | Staged new feature releases, risk minimization |
| Recreate | Stop old version then start new version | Yes | Medium (re-deploy) | Lowest | Dev environments, stateful apps |

### Implementation in GitHub Actions

| Strategy | GitHub Actions Implementation |
|----------|------------------------------|
| Rolling | ECS Update Service / Kubernetes apply (default behavior) |
| Blue/Green | ECS Blue/Green (CodeDeploy integration) or ALB weighted routing |
| Canary | ALB weighted target groups / Lambda alias weighting |
| Recreate | `docker compose down && docker compose up` / ECS Force New Deployment |

## GitHub Environments Approval Flow Design

### Recommended Configuration (3 environments)

```
develop branch push → dev environment (auto-deploy)
                              ↓ success
main branch push    → staging environment (auto-deploy)
                              ↓ success + manual approval
                       production environment (deploy after manual approval)
```

### GitHub Environments Setup Steps

1. Repository Settings → Environments → New environment
2. Create each environment:
   - `dev`: No protection rules (automatic)
   - `staging`: No protection rules (automatic) or Required reviewers (1 person)
   - `production`: Required reviewers (minimum 1 person) + Wait timer (optional)

### Workflow Reference

```yaml
jobs:
  deploy-dev:
    environment: dev          # Auto-deploy
    runs-on: ubuntu-latest

  deploy-staging:
    environment: staging      # Auto or lightweight approval
    needs: deploy-dev

  deploy-prod:
    environment: production   # Required manual approval
    needs: deploy-staging
```

> The name specified in `environment:` must exactly match the GitHub Environments name.

### Deployment Protection Rules

| Rule | Configuration Location | Recommended Value |
|------|----------------------|-------------------|
| Required reviewers | GitHub Environments settings | production: minimum 1 person |
| Wait timer | GitHub Environments settings | production: 0–5 minutes (final review window before deploy) |
| Branch policy | GitHub Environments settings | production: allow main branch only |

## Rollback Procedures

### Pattern 1: Re-deploy Previous Release Tag (Recommended)

Re-push the previous tag to trigger the CD workflow. Requires immutable image tags.

```bash
# Check previous release tags
git tag -l --sort=-version:refname | head -5

# Create a branch from the previous tag's commit and merge to main (or revert PR)
git revert --no-commit HEAD
git commit -m "revert: {description} (#N)"
git push origin main
```

### Pattern 2: GitHub Actions Re-run (Emergency)

Re-run a previously successful run from the GitHub UI or CLI.

```bash
# Check previous runs
gh run list --workflow=cd.yml --limit 5

# Re-run a specific run
gh run rerun {run-id}
```

### Pattern 3: ECS Manual Rollback (Last Resort)

```bash
# Check current service configuration
aws ecs describe-services \
  --cluster {cluster-name} \
  --services {service-name} \
  --query 'services[0].taskDefinition'

# Roll back to previous task definition revision
aws ecs update-service \
  --cluster {cluster-name} \
  --service {service-name} \
  --task-definition {family-name}:{previous-revision}
```

## Pre-deploy Checklist

| Checklist Item | Verification Method |
|----------------|--------------------|
| All tests pass | Check CI workflow result |
| Build succeeded | Check CI build job |
| Staging validation | Run tests / smoke tests |
| Migration plan | If DB schema changes, verify forward/backward compatibility |
| Rollback feasibility | Check for irreversible changes (DB migrations) |
| Monitoring setup | Verify alert thresholds and notification targets after deploy |
