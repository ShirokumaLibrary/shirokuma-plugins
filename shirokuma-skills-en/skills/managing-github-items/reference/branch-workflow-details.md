# Branch Workflow Details

Supplementary details for the `branch-workflow` rule. Covers hotfix, release, maintenance branch, and default branch setup procedures.

## Default Branch Setup

To switch the default branch from `main` to `develop`:

### 1. Create the develop branch (if it doesn't exist)

```bash
git checkout main
git checkout -b develop
git push -u origin develop
```

### 2. Change default branch on GitHub

```bash
gh repo edit --default-branch develop
```

Or: GitHub Settings > General > Default branch > Change to `develop`

### 3. Update local HEAD reference

```bash
git remote set-head origin develop
```

### 4. Protect both branches

Ensure branch protection rules are set for both `main` and `develop`:
- Require PR reviews before merging
- Require status checks to pass
- No direct pushes

## Hotfix Workflow

For urgent production fixes that cannot wait for the normal develop cycle.

### When to Use

- Critical bug in production (`main`)
- Security vulnerability requiring immediate patch
- NOT for regular bug fixes (use normal workflow via `develop`)

### Steps

```bash
# 1. Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/{issue-number}-{slug}

# 2. Fix the issue, commit

# 3. Create PR to main
git push -u origin hotfix/{issue-number}-{slug}
shirokuma-docs items pr create --from-file /tmp/shirokuma-docs/pr.md

# 4. After merge to main, sync to develop
git checkout develop
git pull origin develop
git cherry-pick {hotfix-commit-hash}
# Or: git merge main (if multiple commits)
git push origin develop
```

**Important:** Always sync the fix to `develop` after merging to `main` to prevent regression.

## Release Workflow

Releases are created by merging `develop` into `main`.

### Steps

```bash
# 1. Create PR from develop to main
shirokuma-docs items pr create --from-file /tmp/shirokuma-docs/pr.md

# 2. After PR merge, tag the release
git checkout main
git pull origin main
git tag v{version}
git push origin v{version}
```

### Tagging Convention

```
v{major}.{minor}.{patch}
```

All versions are recorded as tags. Release branches are NOT created for regular releases.

## Maintenance Branches

### When to Create `release/X.x`

Only when ALL of these conditions are met:
- A new major version has been released
- The old major version still needs patches
- Users cannot upgrade to the new major version

### How to Use

```bash
# Create from the last tag of that major version
git checkout v1.2.3
git checkout -b release/1.x
git push -u origin release/1.x

# Apply fixes on this branch
git checkout release/1.x
git checkout -b fix/{issue-number}-{slug}
# ... fix and PR to release/1.x

# Tag the patch release
git tag v1.2.4
git push origin v1.2.4
```

Do NOT merge `release/X.x` back to `develop` or `main`.
