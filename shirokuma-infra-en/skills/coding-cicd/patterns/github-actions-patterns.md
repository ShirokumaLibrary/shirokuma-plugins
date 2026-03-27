# GitHub Actions Pattern Collection

## OIDC Authentication Setup

Obtain temporary credentials using GitHub Actions OIDC tokens without storing IAM access keys (long-term credentials).

### Creating AWS IAM OIDC Provider (first time only)

```bash
# Create OIDC provider
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### IAM Role Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::{ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:{ORG}/{REPO}:*"
        }
      }
    }
  ]
}
```

> For additional security, restrict the `sub` condition to `ref:refs/heads/main` for branch-specific access. When separating environment-specific roles, add `environment:{env-name}` as a condition.

### Workflow Usage

```yaml
permissions:
  id-token: write   # Required for OIDC token acquisition
  contents: read    # Required for code checkout

steps:
  - name: Configure AWS credentials (OIDC)
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: ${{ secrets.DEPLOY_ROLE_ARN }}
      aws-region: ${{ vars.AWS_REGION }}
```

### Secrets vs Variables

| Item | Type | Reason |
|------|------|--------|
| `DEPLOY_ROLE_ARN` | Secret | ARN contains account ID |
| `AWS_REGION` | Variable | Not sensitive (region name) |
| `ECR_REGISTRY` | Variable | Public information |
| `DATABASE_URL` | Secret | Connection string (contains password) |

## Cache Strategy

### npm / pnpm / yarn Cache

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'pnpm'                          # Specify npm / pnpm / yarn
    cache-dependency-path: pnpm-lock.yaml  # Path to lock file

- name: Install dependencies
  run: pnpm install --frozen-lockfile
```

### Docker Layer Cache

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ env.ECR_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    cache-from: type=gha                # Use GitHub Actions cache
    cache-to: type=gha,mode=max
```

### Manual Cache Clearing

GitHub UI: Actions → Caches → Delete

```bash
# List caches with GitHub CLI
gh cache list

# Delete a specific cache
gh cache delete {cache-id}
```

## Reusable Workflows

Share common jobs across multiple workflows.

### Definition (.github/workflows/reusable-deploy.yml)

```yaml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image-tag:
        required: true
        type: string
    secrets:
      DEPLOY_ROLE_ARN:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.DEPLOY_ROLE_ARN }}
          aws-region: ap-northeast-1

      - name: Deploy
        run: |
          echo "Deploying ${{ inputs.image-tag }} to ${{ inputs.environment }}"
```

### Caller

```yaml
jobs:
  deploy-dev:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: dev
      image-tag: ${{ needs.build.outputs.image-tag }}
    secrets:
      DEPLOY_ROLE_ARN: ${{ secrets.DEPLOY_ROLE_ARN }}
```

## Security Best Practices

### Minimizing Permissions

```yaml
# Grant only what is needed at the job level
permissions:
  contents: read     # Code checkout
  id-token: write    # OIDC (only if AWS auth is needed)
  packages: write    # Only if pushing to GHCR
  pull-requests: write  # Only if posting PR comments
```

### Pinning Third-Party Actions

```yaml
# NG: Tag reference (risk of tag rewrite)
uses: actions/checkout@v4

# OK: Pin to commit SHA (tamper detection)
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

> Configure a dependency bot (Dependabot / Renovate) to automate SHA updates.

### Restricting Secret Scope

```yaml
# NG: Using repository-level secrets accessible to all environments
secrets:
  PROD_DB_URL: ${{ secrets.DATABASE_URL }}  # Accessible from all jobs

# OK: Use GitHub Environments secrets
# (accessible only from jobs with the matching environment)
environment: production
# → secrets.DATABASE_URL is retrieved from production environment secrets
```

### GITHUB_TOKEN Permission Check

```yaml
# Default is read-all. Explicitly grant write when needed
permissions:
  contents: write    # When creating releases or pushing tags
```

## Matrix Build

Run tests in parallel across multiple versions and operating systems.

```yaml
jobs:
  test:
    strategy:
      fail-fast: false   # Continue other jobs if one fails
      matrix:
        node-version: ['18', '20', '22']
        os: [ubuntu-latest, windows-latest]
        exclude:
          - os: windows-latest
            node-version: '18'   # Exclude specific combinations

    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

## Conditional Execution Patterns

```yaml
# Run only on PR
if: github.event_name == 'pull_request'

# Run only on push to main branch
if: github.ref == 'refs/heads/main' && github.event_name == 'push'

# Run on push to develop or main branches
if: github.ref_name == 'develop' || github.ref_name == 'main'

# Run only on tag push (release)
if: startsWith(github.ref, 'refs/tags/v')

# Run only on specific file changes (combine with paths filter)
on:
  push:
    paths:
      - 'src/**'
      - 'package.json'
```
