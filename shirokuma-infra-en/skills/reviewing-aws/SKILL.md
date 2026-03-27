---
name: reviewing-aws
description: Reviews AWS infrastructure configuration. Covers IAM policies, security groups, Well-Architected Framework, cost optimization, and availability design. Triggers: "AWS review", "infrastructure review", "IAM review", "aws review", "security group review", "Well-Architected review".
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# AWS Infrastructure Configuration Review

Review AWS resource configuration code. Focus on IAM least privilege, security group design, Well-Architected Framework compliance, and cost optimization.

## Scope

- **Category:** Investigation Worker
- **Scope:** CDK code / IaC file reading (Read / Grep / Glob / Bash read-only), generating review reports. No code modifications or AWS resource provisioning.
- **Out of scope:** CDK code modifications (delegate to `coding-cdk`), actual AWS resource changes

## Review Criteria

### IAM Security (Least Privilege)

| Check | Issue | Fix |
|-------|-------|-----|
| Wildcard Action | `"Action": "*"` or `"Action": "s3:*"` | Enumerate required Actions |
| Wildcard Resource | `"Resource": "*"` | Specify exact resource ARN |
| IAM PassRole | Overly broad PassRole permissions | Restrict to specific role ARN |
| Inline policies | Using inline policies | Prefer managed policies |
| MFA enforcement | No MFA for administrative operations | Add MFA condition to Condition block |
| Cross-account | `"Principal": "*"` | Specify specific account ID / IAM entity |

### Network / Security Groups

| Check | Issue | Fix |
|-------|-------|-----|
| 0.0.0.0/0 inbound | Allowing access from all IPs | Restrict to specific CIDR / security group reference |
| SSH/RDP open | Port 22/3389 open to all IPs | Use VPN / SSM Session Manager |
| DB in public subnet | RDS / ElastiCache in public placement | Move to private subnet |
| Security group referencing | CIDR-only references | Use security group-to-security group references |
| Missing NACLs | No additional network layer | Recommend NACLs for sensitive subnets |

### Availability / Fault Tolerance

| Check | Issue | Fix |
|-------|-------|-----|
| Single AZ | Resources concentrated in single AZ | Recommend multi-AZ configuration |
| Single instance | Single EC2 without ASG | Introduce Auto Scaling Group |
| RDS failover | Multi-AZ not configured | Set `multiAz: true` |
| Backup configuration | Short or no RDS backup retention | Recommend minimum 7 days |
| Health checks | No health checks on ALB targets | Set appropriate path and thresholds |

### Cost Optimization

| Check | Issue | Fix |
|-------|-------|-----|
| Instance sizing | Over-provisioned | Check Compute Optimizer recommendations |
| Reserved instances | On-demand only | Consider RI / Savings Plans for long-running workloads |
| NAT gateway | NAT GW in every AZ | Reduce based on traffic patterns |
| Unused EIPs | Unattached Elastic IPs | Delete or release |
| Lifecycle policies | No lifecycle policy on S3 bucket | Set Glacier transition for old objects |

### Data Protection

| Check | Issue | Fix |
|-------|-------|-----|
| Encryption | No encryption for EBS / RDS / S3 | Enable encryption with KMS key |
| Bucket public access | S3 bucket is public | Set `blockPublicAccess: BlockPublicAccess.BLOCK_ALL` |
| Secret management | Plaintext secrets in Lambda env vars | Use Secrets Manager / Parameter Store |
| CloudTrail | API logging not configured | Enable CloudTrail |
| GuardDuty | Threat detection not configured | Recommend enabling GuardDuty |

### Tagging

| Check | Issue | Fix |
|-------|-------|-----|
| Missing required tags | No `Environment` / `Project` tags | Enforce tagging with CDK Aspects |
| Cost allocation tags | No team/feature tags | Add `CostCenter` tag |

## Workflow

### 1. Identify Target Files

```bash
# Check CDK stack files
find . -path "*/lib/*-stack.ts" | head -20
find . -path "*/bin/*.ts" | head -10

# Check IAM policies
grep -r "PolicyStatement\|addToPolicy\|attachInlinePolicy" --include="*.ts" -l | head -10

# Check security groups
grep -r "SecurityGroup\|addIngressRule\|addEgressRule" --include="*.ts" -l | head -10
```

### 2. Code Analysis

Read CDK code and apply the review criteria tables.

Priority check order:
1. IAM least privilege violations (security risk)
2. Network exposure issues
3. Availability design (single AZ)
4. Data protection (encryption / secret management)
5. Cost optimization

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
{List IAM / network / encryption issues}

### Improvements
{List availability / cost optimization suggestions}
```

### 4. Save Report

When PR context is present:
```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/review-aws.md
```

When no PR context:
```bash
shirokuma-docs discussions create \
  --category Reports \
  --title "[Review] aws: {target}" \
  --body-file /tmp/shirokuma-docs/review-aws.md
```

## Review Verdict

- **PASS**: `**Review result:** PASS` — No critical issues
- **FAIL**: `**Review result:** FAIL` — Critical/High issues found (IAM wildcards / public access / no encryption, etc.)

## Notes

- **Do not modify code** — Report findings only
- Keep the Well-Architected Framework's 6 pillars in mind (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability)
- Be aware of region-specific limitations (especially ap-northeast-1)
