---
name: reviewing-cdk
description: Reviews AWS CDK code. Covers construct design, Aspects patterns, stack splitting, testing, and type safety. Triggers: "CDK review", "construct review", "cdk review", "IaC review", "stack review".
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# AWS CDK Code Review

Review CDK construct design quality, Aspects patterns, stack splitting strategy, and test coverage.

## Scope

- **Category:** Investigation Worker
- **Scope:** CDK TypeScript code reading (Read / Grep / Glob / Bash read-only), generating review reports. No code modifications or `cdk deploy`.
- **Out of scope:** CDK code modifications (delegate to `coding-cdk`), AWS resource provisioning

## Review Criteria

### Construct Design

| Check | Issue | Fix |
|-------|-------|-----|
| Overuse of L1 constructs | Using `CfnXxx` directly | Start with L2, use L1 only when needed |
| Props design | All fields are Required | Use `Partial<>` / optional fields with defaults |
| Construct granularity | All resources defined in Stack | Split into feature-based constructs |
| ID naming | Meaningless IDs (`Resource1`, `Lambda`) | Use descriptive IDs that reflect purpose |
| Scope appropriateness | Passing parent scope instead of `this` | Use minimum scope |

### Stack Splitting

| Check | Issue | Fix |
|-------|-------|-----|
| Monolithic stack | All resources in a single stack | Split into Network / Stateful / Stateless |
| Circular references | Circular dependencies between stacks | Maintain unidirectional dependency |
| Cross-stack references | Overuse of `Fn.importValue` | Prefer Props passing between stacks |
| Too many stacks | Over-granular stack splitting | Consolidate to appropriate deployment units |

### CDK Aspects

| Check | Issue | Fix |
|-------|-------|-----|
| Manual tagging | `Tags.of().add()` per resource | Use `Aspects.of(app).add(new TaggingAspect())` |
| Manual encryption enforcement | Encryption checks per resource | Enforce with Aspects |
| Cost management tags | Missing tags on some resources | Use Aspects as fallback guarantee |

### Type Safety

| Check | Issue | Fix |
|-------|-------|-----|
| Use of `any` type | `any` in Props or variables | Use appropriate CDK types |
| Token references | Not checking `cdk.Token.isUnresolved()` | Handle Token references properly |
| Env variable types | Using `process.env.X` directly | `process.env.X ?? throwIfMissing()` |
| construct.node.scope | Getting scope via type assertion | Use proper CDK types |

### Testing

| Check | Issue | Fix |
|-------|-------|-----|
| Snapshot tests only | Not testing logic | Add fine-grained assertions |
| Insufficient tests | Low coverage | Add tests for major constructs |
| Not using `Template.fromStack()` | Asserting with raw CloudFormation | Use CDK assertions API |
| Prop validation | Not testing invalid Props | Add boundary / error case tests |

### Environment Configuration

| Check | Issue | Fix |
|-------|-------|-----|
| Hardcoded ARNs | `"arn:aws:..."` hardcoded | Externalize via SSM Parameter / context |
| Hardcoded account IDs | `"123456789012"` hardcoded | Use `cdk.Aws.ACCOUNT_ID` or context |
| Environment branching | dev/prod separation unclear | Separate with Context / Environment class |
| Secrets in `cdk.json` | Storing secret values in context | Use Secrets Manager / SSM |

## Workflow

### 1. Identify Target Files

```bash
# Check CDK structure
find . -path "*/lib/*.ts" | grep -v "test" | head -20
find . -path "*/bin/*.ts" | head -10
find . -name "*.test.ts" -path "*/cdk/*" -o -name "*.spec.ts" -path "*/cdk/*" | head -10

# Check Aspects usage
grep -r "Aspects\|IAspect" --include="*.ts" -l | head -10

# Check test files
grep -r "Template.fromStack\|assertions" --include="*.ts" -l | head -10
```

### 2. Run Lints

```bash
shirokuma-docs lint code -p . -f terminal
```

### 3. Code Analysis

Read CDK files and apply the review criteria tables.

Priority check order:
1. Type safety (compilation error risk)
2. Security-related design (IAM / encryption)
3. Appropriateness of stack splitting
4. Test coverage
5. Construct design quality

### 4. Generate Report

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
{List type safety / security design issues}

### Improvements
{List construct design / test improvement suggestions}
```

### 5. Save Report

When PR context is present:
```bash
shirokuma-docs items add comment {PR#} --file /tmp/shirokuma-docs/review-cdk.md
```

When no PR context:
```bash
# Set title: "[Review] cdk: {target}" and category: Reports in frontmatter first
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/review-cdk.md
```

## Review Verdict

- **PASS**: `**Review result:** PASS` — No critical issues
- **FAIL**: `**Review result:** FAIL` — Critical/High issues found

## Notes

- **Do not modify code** — Report findings only
- Assumes CDK v2. Be aware of API differences between v1 and v2
- When CloudFormation template output from `cdk synth` is available, also reference it
