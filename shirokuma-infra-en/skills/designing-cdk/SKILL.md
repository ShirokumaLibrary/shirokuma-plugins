---
name: designing-cdk
description: Designs CDK construct structure. Covers stack splitting strategy, L2/L3 construct selection rationale, Props interface design, and Aspects governance design. More focused on CDK structure and design patterns than designing-aws. Triggers: "CDK design", "construct design", "stack design", "CDK architecture", "Aspects design", "CDK structure design".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# CDK Construct Design

Design AWS CDK construct structure, stack splitting, Props design, and Aspects governance.

> **Scope boundary:** `designing-aws` handles AWS resource selection (what to use), while this skill handles CDK code structure and design patterns (how to implement it). Implementation is handled by `coding-cdk`.

## Scope

- **Category:** Investigation Worker
- **Scope:** Reading existing CDK code (Read / Grep / Glob / Bash read-only commands), generating CDK design documents (Write/Edit — for design artifacts), appending design sections to Issue bodies.
- **Out of scope:** AWS resource selection (delegated to `designing-aws`), CDK construct implementation (delegated to `coding-cdk`), docker-compose design (delegated to `designing-infra`)

> **Writing design artifacts**: When this skill uses Write/Edit on Issue bodies or design documents, it is producing design process outputs — not modifying production code. This is a permitted exception for Investigation Workers.

## Workflow

### 0. Check Existing CDK Structure

**First**, read the project `CLAUDE.md` and examine existing CDK code:

- CDK version (v1 / v2) and language (TypeScript / Python, etc.)
- CDK directory structure (`infra/` or `cdk/`, etc.)
- Number of existing stacks and splitting approach
- L2/L3 constructs currently in use
- `cdk.json` context key configuration

```bash
find . -path "*/infra/*.ts" -o -path "*/cdk/*.ts" | head -20
cat {infra-dir}/cdk.json 2>/dev/null
```

### 1. Design Context Check

When delegated from `design-flow`, a Design Brief and requirements are passed. Use them as-is.

When invoked standalone, understand design requirements from the Issue body and plan section.

### 2. Stack Splitting Design

#### Splitting Principles

| Split Axis | Description | Example |
|-----------|-------------|---------|
| Stateful / Stateless | Separate persistent data (DB) from application | Stateful: RDS / S3, Stateless: ECS |
| Change frequency | Isolate rarely-changed resources in stable stacks | Network stack: rare, App stack: frequent |
| Team ownership | Align splits with team responsibility boundaries | Infrastructure team vs application team |
| Deployment risk | Minimize blast radius of changes | Network changes don't affect app deploys |

#### Recommended Structure (3-Stack Split)

```
Network Stack    - VPC, subnets, security groups, VPC Endpoints
Stateful Stack   - RDS, ElastiCache, S3 (persistent data)
Stateless Stack  - ECS, Lambda, ALB (application layer)
```

Dependency order: Network → Stateful → Stateless

### 3. L2/L3 Construct Selection Design

#### Selection Framework

| Level | When to Use | Example |
|-------|------------|---------|
| L3 (Patterns Library) | Standard use case requiring a complete pattern | `ApplicationLoadBalancedFargateService` |
| L2 (Intent-based) | Need best-practice defaults with customization | `aws_rds.DatabaseInstance` |
| L1 (CloudFormation) | Need to control a property unavailable in L2 | Via Escape Hatch |

#### Design Decision Record

Record the design rationale for each construct:

```markdown
### Construct Design Decisions

| Construct | Level | Rationale | Notes |
|-----------|-------|-----------|-------|
| {construct} | L2/L3 | {reason} | {caveats} |
```

### 4. Props Interface Design

#### Design Principles

- **Inject environment-specific differences via Props** — avoid hardcoding
- **Clearly distinguish Required vs Optional** — use types to separate mandatory and optional settings
- **Maximize type safety** — prefer `aws_ec2.InstanceType` over plain `string`

```typescript
// Props design template
interface {StackName}Props extends cdk.StackProps {
  // Environment identifier
  environment: 'dev' | 'staging' | 'prod';

  // Required: scaling configuration
  readonly desiredCount: number;
  readonly instanceType: ec2.InstanceType;

  // Optional: cost optimization
  readonly enableDeletionProtection?: boolean;  // default: true in prod
  readonly multiAz?: boolean;                   // default: false in dev
}
```

### 5. Aspects Governance Design

When governance requirements exist, design Aspects-based enforcement:

| Aspects Use Case | Implementation Example |
|-----------------|----------------------|
| Enforce tagging | `Environment`, `Project`, `CostCenter` tags |
| Enforce encryption | Check encryption on EBS, RDS, S3 |
| Cost management | Limit resource sizes in non-production environments |

### 6. Design Output

```markdown
## CDK Construct Design

### Stack Configuration
| Stack | Resources | Change Frequency | Dependencies |
|-------|-----------|-----------------|--------------|
| {stack-name} | {resource list} | Low/Medium/High | {deps} |

### Construct Design Decisions
| Construct | Level | Rationale |
|-----------|-------|-----------|
| {construct} | L2/L3 | {reason} |

### Props Interface Design
{Key Props structure}

### Aspects Governance
{Governance requirements and implementation approach}

### Cross-Stack Reference Strategy
{How values are passed between stacks}
```

### 7. Review Checklist

- [ ] Stack split respects the stateful/stateless boundary
- [ ] L3 constructs eliminate redundant implementation where applicable
- [ ] Props appropriately abstract environment-specific differences
- [ ] `interface Props` extends `cdk.StackProps`
- [ ] Cross-stack references are correct (no circular dependencies)
- [ ] Aspects ensure tagging and encryption governance
- [ ] No `any` types are used

## Next Steps

When called via `design-flow`, control automatically returns to the orchestrator.

When invoked standalone:

```
CDK construct design complete. Next steps:
-> Implement CDK constructs with coding-cdk skill
-> Use /design-flow for a full design workflow
```

## Notes

- **Do not generate implementation code** — Output design documents only. Code implementation is `coding-cdk`'s responsibility
- **Do not make AWS resource selection decisions** — Delegate to `designing-aws` if resource type selection is needed
- Assumes CDK v2 (`aws-cdk-lib`). Note individual package names if using v1
- Clearly define the scope of Aspects application during design, as implementation can be complex
