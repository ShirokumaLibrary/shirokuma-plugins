---
name: auditing-security
description: Analyzes Node.js (npm/pnpm/yarn) dependency security vulnerabilities and records critical/high vulnerabilities as Issues. Triggers: "security audit", "audit", "vulnerability check", "dependency audit".
allowed-tools: Read, Bash, Glob, Grep
---

# Security Audit

A skill that auto-scans dependency vulnerabilities using `lint security` and presents analysis and response recommendations.

## Scope

- **Category:** Investigation Worker
- **Scope:** Vulnerability scanning via `shirokuma-docs lint security` (Bash read-only commands), analyzing and prioritizing results, generating security reports, presenting Issue creation candidates.
- **Out of scope:** Automatically updating dependency packages, auto-creating Issues without user confirmation. Issue creation is performed via CLI (`shirokuma-docs items add issue`) only after user confirmation

> **Bash exception**: `shirokuma-docs lint security`, `shirokuma-docs search`, and similar read/search commands are permitted. Package update commands (`pnpm update`, etc.) are prohibited.

## Workflow

```
Scan → Analyze (dev/prod · severity · fixability) → Duplicate check → Report → Present Issue creation candidates
```

## Steps

### 1. Security Scan

```bash
shirokuma-docs lint security -p . --format json
```

Omitting `--severity` defaults to high and above. To detect moderate:

```bash
shirokuma-docs lint security -p . --format json --severity moderate
```

### 2. Analyze Results

Classify the `vulnerabilities` array in the JSON output by:

| Aspect | Criteria |
|--------|----------|
| Urgency | severity: critical > high > moderate > low |
| Impact scope | isDev=false (production) > isDev=true (dev only) |
| Actionability | fixAvailable=true > false |

**Response priority matrix:**

| severity | isDev | fixAvailable | Priority |
|----------|-------|-------------|----------|
| critical | false | true | P0 (immediate) |
| critical | false | false | P1 (workaround) |
| high | false | true | P1 (current sprint) |
| high | false | false | P2 (monitor) |
| critical/high | true | any | P2 (dev env only) |
| moderate | any | any | P3 (planned) |

### 3. Duplicate Issue Check

```bash
shirokuma-docs items list --search "security" --search "vulnerability"
```

Or search by package name:

```bash
shirokuma-docs search "{package-name} vulnerability"
```

If a duplicate Issue exists, skip creation and update the existing Issue instead.

### 4. Generate Report

Report to the user in this format:

```markdown
## Security Audit Results

**Scan date:** {date}
**Package Manager:** {pm}

### Summary
| severity | count |
|----------|-------|
| Critical | {n} |
| High | {n} |
| Moderate | {n} |

### P0 (Immediate action required)
| Package | severity | Fix version |
|---------|----------|------------|
| {name} | critical | {fixedIn} |

### Issue creation candidates
- [ ] {package-name}: {description} (CVE: {cve})
```

### 5. Create Issues (after user confirmation)

Create Issues only after confirming with the user. This skill does not auto-create Issues.

```bash
shirokuma-docs items add issue --file /tmp/shirokuma-docs/security-issue.md
```

Issue body template:

```markdown
## Purpose
Fix the {severity} vulnerability in {package-name} to eliminate security risk.

## Summary
{description}

## Background
- **CVE**: {cve-ids}
- **Affected versions**: {range}
- **Fix version**: {fixedIn}
- **isDev**: {isDev}

## Tasks
- [ ] {pm} update {package-name}
- [ ] Verify build and tests pass
- [ ] Confirm production deployment

## Deliverable
{package-name} is updated to the fix version or above, and `lint security` returns clean.
```

## Notes

- **No network connection**: `lint security` skips and returns exit 0. Verify network connectivity in CI environments.
- **Dev dependencies**: isDev=true vulnerabilities don't affect production, but check impact on CI/CD pipelines.
- **fixAvailable=false**: When no patch is available, consider migrating to an alternative package or disabling the feature.

## Quick Reference

```bash
# Basic scan
shirokuma-docs lint security -p .

# JSON output (for analysis)
shirokuma-docs lint security -p . --format json

# Detect moderate and above
shirokuma-docs lint security -p . --severity moderate

# Strict mode (for CI)
shirokuma-docs lint security -p . --strict
```
