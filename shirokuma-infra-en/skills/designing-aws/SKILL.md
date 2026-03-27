---
name: designing-aws
description: Designs mappings from local development environment (docker-compose) to production AWS resources. Covers resource selection, architecture design, and CDK construct decisions (L2 vs L3, Props design). Triggers: "AWS design", "resource design", "infrastructure design", "production architecture", "CDK design", "cloud design".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# AWS Resource Design

Map local development services to production AWS resources, and produce architecture decisions including CDK construct design.

> **AWS resource design is this skill's responsibility.** `coding-cdk` is responsible for implementing CDK constructs based on the design determined here.

## Scope

- **Category:** Investigation Worker
- **Scope:** Reading project configuration and existing infrastructure (Read / Grep / Glob / Bash read-only commands), generating AWS resource design documents (Write/Edit — for design artifacts), appending design sections to Issue bodies.
- **Out of scope:** Implementing CDK constructs (delegate to `coding-cdk`), actually provisioning AWS resources, designing with other IaC tools (Terraform, Pulumi, etc.)

> **Writing design artifacts**: When this skill uses Write/Edit on Issue bodies or design documents, it is producing design process outputs — not modifying production code. This is a permitted exception for Investigation Workers.

## Workflow

### 0. Tech Stack Check

**First**, read the project `CLAUDE.md` and confirm:
- Framework (Next.js, Node.js, etc.) and runtime
- Service configuration defined in the existing docker-compose.yml
- CDK version (v1 / v2) and language (TypeScript / Python, etc.)
- Existing CDK stack structure (`infra/` or `cdk/` directory, etc.)
- Target AWS account / region

Also check `tech-stack.md` in `.claude/rules/`.

### 1. Design Context Check

When delegated from `design-flow`, a Design Brief and requirements are passed. Use them as-is.

When invoked standalone, understand requirements from the Issue body and plan section.

### 2. Local-to-Production Mapping Analysis

List services from the existing docker-compose.yml and determine the corresponding AWS resource for each service.

See [patterns/local-to-prod-mapping.md](patterns/local-to-prod-mapping.md) for the detailed mapping table.

#### Design Perspectives

| Perspective | When to Address | Pattern Reference |
|------------|----------------|------------------|
| Compute selection | How to host the application | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - Compute |
| Data store selection | Choosing RDS / DynamoDB / ElastiCache | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - Data Stores |
| Messaging selection | Choosing SQS / SNS / EventBridge | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - Messaging |
| Storage selection | S3 bucket design, lifecycle | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - Storage |
| Network design | VPC, subnets, security groups | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - Network |
| CDK construct design | L2 vs L3, Props design | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - CDK |
| Security design | IAM roles, Secrets Manager | [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) - Security |

#### Decision Framework

Evaluate each perspective:

1. **Requirements**: What functionality does the local service serve? What are availability and scale requirements?
2. **Constraints**: Cost limits, region constraints, team's AWS proficiency
3. **Options**: List viable AWS services (refer to aws-resource-patterns.md)
4. **Trade-offs**: Compare options using a decision matrix
5. **Decision**: Select the resource with justification

### 3. Design Output

Produce the AWS resource design as a structured document:

```markdown
## AWS Resource Design

### Service Mapping
| Local (docker-compose) | AWS Resource | Notes |
|------------------------|-------------|-------|
| {service-name} | {AWS service} | {configuration approach} |

### Resource Details

#### {Resource Name}
- **Service**: {AWS service identifier}
- **Configuration**: {key configuration parameters}
- **Scaling**: {auto-scaling strategy}
- **Cost estimate**: {rough estimate}

### CDK Construct Design
| Construct | Level | Reason |
|-----------|-------|--------|
| {construct-name} | L2 / L3 | {selection rationale} |

### Network Architecture
{VPC, subnet, and security group design}

### Security Design
{IAM roles, least-privilege principle, secret management approach}

### Key Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| {topic} | {service/pattern} | {reason} |
```

### 4. Review Checklist

- [ ] Every local service has a corresponding AWS resource defined
- [ ] CDK construct level (L1/L2/L3) selection is justified
- [ ] IAM roles follow the principle of least privilege
- [ ] Secrets (DB passwords, etc.) are managed via Secrets Manager / Parameter Store
- [ ] Private subnets are used appropriately in the VPC design
- [ ] Scaling strategy matches requirements
- [ ] Multi-AZ support is considered
- [ ] Cost estimates are within realistic bounds

## Reference Documents

| Document | Content | When to Read |
|----------|---------|-------------|
| [patterns/aws-resource-patterns.md](patterns/aws-resource-patterns.md) | AWS resource selection patterns | When selecting resources or designing CDK constructs |
| [patterns/local-to-prod-mapping.md](patterns/local-to-prod-mapping.md) | Local-to-production mapping table | When verifying mappings |
| [patterns/env-mapping.md](patterns/env-mapping.md) | Environment variable mapping patterns | When designing environment variables |
| `coding-infra` skill [localstack.md](../coding-infra/patterns/localstack.md) | LocalStack endpoint switching patterns | When referencing SDK configuration |

## Anti-Patterns

| Pattern | Problem | Alternative |
|---------|---------|-------------|
| Placing all resources in public subnets | Security risk | Move DBs and internal services to private subnets |
| Overusing L1 constructs | Ends up writing CloudFormation raw JSON in TypeScript | Start with L2; only drop to L1 when fine-grained control is needed |
| Passing secrets directly as environment variables | Security risk, hard to rotate | Use Secrets Manager + ECS task definition `secrets` field |
| Single-AZ architecture | Zero availability design | Apply multi-AZ to RDS / ALB |
| Putting everything in one CDK stack | Large deploy unit; higher risk per change | Split into Network / Stateful (DB) / Stateless (App) stacks |
| Oversized resource selection | Cost overrun | Start with the minimum service that meets requirements and scale up |

## Next Steps

When called via `design-flow`, control automatically returns to the orchestrator.

When invoked standalone:

```
AWS resource design complete. Next steps:
-> Implement CDK constructs with coding-cdk skill
-> Use /design-flow for a full design workflow
```

## Notes

- **Design decisions are the top priority** — CDK implementation details are `coding-cdk`'s responsibility
- **Build verification is not needed** — This skill generates design documents, not executable code
- When a Design Brief is provided, design based on it. When standalone, understand requirements from the Issue first
- Be aware of AWS service availability differences across regions (especially limitations in ap-northeast-1)
- Cost estimates are rough approximations; delegate detailed calculations to the AWS Pricing Calculator
