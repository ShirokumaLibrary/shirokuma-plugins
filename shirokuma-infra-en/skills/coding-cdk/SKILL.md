---
name: coding-cdk
description: Implements and modifies AWS CDK (TypeScript) infrastructure constructs. Takes design artifacts from designing-aws and handles L2/L3 construct implementation, stack splitting, environment configuration management, and CI/CD integration. Triggers: "CDK implementation", "CDK constructs", "CDK stacks", "infra implementation", "cdk deploy", "cdk synth".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TaskGet, TaskList
---

# CDK Coding

Implement and modify AWS CDK (TypeScript) constructs based on the AWS resource design produced by `designing-aws`.

## Scope

- **Category:** Mutation worker
- **Scope:** CDK construct implementation and modification (Write / Edit / Bash). Implements L2/L3 constructs, stack splitting, environment configuration management, and CI/CD integration based on `designing-aws` design artifacts. Assumes CDK v2 TypeScript.
- **Out of scope:** AWS resource selection and design decisions (delegated to `designing-aws`), local environment setup with docker-compose (delegated to `coding-infra`)

## Before Starting

1. Check project `CLAUDE.md` for CDK version (v1/v2), language, and directory structure
2. Read `designing-aws` design artifacts (the "AWS Resource Design" section in the Issue body)
3. Review existing CDK stack structure (`infra/` or `cdk/` directory)
4. Check L2/L3 usage guidelines in [patterns/cdk-constructs.md](patterns/cdk-constructs.md)

## Workflow

### Step 1: Project Structure Check

```bash
# Check CDK project structure
ls -la {infra-dir}/
cat {infra-dir}/cdk.json
cat {infra-dir}/package.json | grep -E '"aws-cdk|constructs'

# List existing stacks
find {infra-dir} -name '*.ts' | head -20
```

Items to verify:
- CDK version (`aws-cdk-lib` version)
- Entry point (`bin/*.ts`)
- Existing stack/construct structure
- `cdk.json` `context` keys

### Step 2: Implementation Plan

Create a progress tracker with TaskCreate.

```markdown
## Implementation Plan

### Files to Change
- [ ] `bin/app.ts` - Stack entry point
- [ ] `lib/{stack-name}-stack.ts` - Stack definition
- [ ] `lib/constructs/{construct-name}.ts` - Construct implementation

### Verification
- [ ] Confirm L2/L3 construct selection rationale
- [ ] Props interface design (Required vs Optional)
- [ ] Cross-stack references between stacks
- [ ] Environment-specific configuration injection method
```

### Step 3: Implementation

Implement with reference to patterns:

- L2/L3 construct usage: [patterns/cdk-constructs.md](patterns/cdk-constructs.md)
- Environment-specific configuration: [patterns/environment-config.md](patterns/environment-config.md)
- Governance (tagging, encryption enforcement): [patterns/cdk-aspects.md](patterns/cdk-aspects.md)

Multi-stack structure: [templates/stack-structure.ts.template](templates/stack-structure.ts.template)

CI/CD integration: [templates/github-actions-cdk.yml.template](templates/github-actions-cdk.yml.template)

**Implementation checklist**:
- Define `interface Props` per Stack/Construct for type safety
- Inject environment variables and secrets via SSM / Secrets Manager
- Resolve cross-stack dependencies via `cdk.Fn.importValue` or Props

### Step 4: Validation

```bash
# Type check
cd {infra-dir} && npx tsc --noEmit

# Generate template (syntax validation)
npx cdk synth

# Check diff (before deploy)
npx cdk diff

# Snapshot tests (if they exist)
npm test
```

### Step 5: Completion Report

Record the changes as a comment on the Issue.

## Reference Documents

| Document | Content | When to Read |
|----------|---------|-------------|
| [patterns/cdk-constructs.md](patterns/cdk-constructs.md) | L2/L3 construct usage, Props design, composition patterns | When implementing constructs |
| [patterns/environment-config.md](patterns/environment-config.md) | Environment-specific config management (cdk.json / Props / SSM) | When separating stacks by environment |
| [patterns/cdk-aspects.md](patterns/cdk-aspects.md) | Aspects for tagging, encryption, cost governance | When implementing governance requirements |
| [templates/stack-structure.ts.template](templates/stack-structure.ts.template) | Network/Stateful/Stateless 3-stack split template | When designing stack structure |
| [templates/github-actions-cdk.yml.template](templates/github-actions-cdk.yml.template) | OIDC auth, cdk diff/deploy workflow | When setting up CI/CD |

## Quick Commands

```bash
npx cdk list                          # List stacks
npx cdk synth                         # Generate CloudFormation templates
npx cdk diff [stack-name]             # Diff against current deployment
npx cdk deploy [stack-name]           # Deploy (with manual approval)
npx cdk deploy --require-approval never  # Auto-approve deploy (for CI/CD)
npx cdk destroy [stack-name]          # Destroy stack
npx cdk bootstrap                     # CDK bootstrap (first time only)
npx tsc --noEmit                      # Type check (always run before deploy)
```

## Next Steps

When invoked standalone (not via `implement-flow` chain):

```
Implementation complete. Next step:
→ `/commit-issue` to stage and commit your changes
```

## Notes

- **Don't override design decisions** — If resource selection or L2/L3 choices need changing, escalate back to `designing-aws`
- **Always run `cdk synth`** — Catch syntax errors via template generation before deploying
- **L1 constructs are a last resort** — First consider `addPropertyOverride` or escape hatch on L2
- **Never embed secrets in code** — Always use SSM Parameter Store / Secrets Manager for passwords and API keys
- **Preserve stack split** — Don't break the Network / Stateful / Stateless separation principle
- **Avoid `any` type** — Define Props interfaces properly to maintain type safety
