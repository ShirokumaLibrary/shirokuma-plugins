# CDK Aspects Governance Patterns

## How CDK Aspects Work

Aspects traverse the CDK construct tree and apply policies to every node.

```
App
└── Stack
    ├── VpcConstruct
    ├── DatabaseConstruct
    │   ├── CfnDBInstance  ← Aspect visits down to here
    │   └── CfnSubnetGroup
    └── AppService
        └── CfnTaskDefinition
```

When an Aspect is applied at the Stack level, every L1/L2/L3 construct in the stack is traversed.

### Applying aspects

```typescript
// Apply to the whole stack
const stack = new AppStack(app, 'AppStack', { ... });
cdk.Aspects.of(stack).add(new RequiredTagsAspect({
  project: 'my-app',
  environment: props.environment,
}));

// Apply to a specific construct only
cdk.Aspects.of(myDatabase).add(new EncryptionEnforcementAspect());
```

## Required Tags Aspect

Enforce required tags on all resources for cost allocation and resource tracking.

```typescript
import { IAspect, IConstruct, TagManager, Tags } from 'aws-cdk-lib';

export interface RequiredTagsProps {
  readonly project: string;
  readonly environment: string;
  readonly owner?: string;
  readonly costCenter?: string;
}

export class RequiredTagsAspect implements IAspect {
  constructor(private readonly props: RequiredTagsProps) {}

  visit(node: IConstruct): void {
    // Apply only to resources that support tagging
    if (TagManager.isTaggable(node)) {
      Tags.of(node).add('Project', this.props.project);
      Tags.of(node).add('Environment', this.props.environment);

      if (this.props.owner) {
        Tags.of(node).add('Owner', this.props.owner);
      }
      if (this.props.costCenter) {
        Tags.of(node).add('CostCenter', this.props.costCenter);
      }

      // Management tag (auto-set)
      Tags.of(node).add('ManagedBy', 'CDK');
    }
  }
}
```

### Usage example

```typescript
// bin/app.ts
const stack = new AppStack(app, 'AppStack', { environment: 'prod' });

cdk.Aspects.of(stack).add(new RequiredTagsAspect({
  project: 'my-service',
  environment: 'prod',
  owner: 'platform-team',
  costCenter: 'CC-1234',
}));
```

## Encryption Enforcement Aspect

Check that encryption is enabled on S3, RDS, EBS, etc. and emit warnings or errors on violations.

```typescript
import { IAspect, IConstruct, Annotations } from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as rds from 'aws-cdk-lib/aws-rds';

export class EncryptionEnforcementAspect implements IAspect {
  constructor(private readonly errorOnViolation = false) {}

  visit(node: IConstruct): void {
    // Check S3 bucket encryption
    if (node instanceof s3.CfnBucket) {
      if (!node.bucketEncryption) {
        this.report(node, 'S3 bucket has no encryption configured');
      }
    }

    // Check RDS instance encryption
    if (node instanceof rds.CfnDBInstance) {
      if (node.storageEncrypted !== true) {
        this.report(node, 'RDS instance storage encryption is disabled');
      }
    }
  }

  private report(node: IConstruct, message: string): void {
    if (this.errorOnViolation) {
      Annotations.of(node).addError(message);
    } else {
      Annotations.of(node).addWarning(message);
    }
  }
}
```

### Usage example

```typescript
// In production, violations are errors (causes cdk synth/deploy to fail)
cdk.Aspects.of(stack).add(
  new EncryptionEnforcementAspect(props.environment === 'prod'),
);
```

## Cost Control Aspect

Restrict the use of specific instance types or high-cost resources.

```typescript
import { IAspect, IConstruct, Annotations } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

export interface CostControlProps {
  /** Instance families to block (e.g., ['p3', 'p4d']) */
  readonly blockedInstanceFamilies?: string[];
  /** Maximum allowed instance size (e.g., 'xlarge') */
  readonly maxInstanceSize?: string;
}

export class CostControlAspect implements IAspect {
  private static readonly SIZE_ORDER = [
    'nano', 'micro', 'small', 'medium', 'large',
    'xlarge', '2xlarge', '4xlarge', '8xlarge', '12xlarge', '16xlarge',
  ];

  constructor(private readonly props: CostControlProps) {}

  visit(node: IConstruct): void {
    if (node instanceof ec2.CfnInstance) {
      const instanceType = node.instanceType as string | undefined;
      if (!instanceType) return;

      const [family, size] = instanceType.split('.');

      // Check blocked instance families
      if (this.props.blockedInstanceFamilies?.includes(family)) {
        Annotations.of(node).addError(
          `Instance family ${family} is not allowed`,
        );
      }

      // Check maximum size
      if (this.props.maxInstanceSize && size) {
        const maxIndex = CostControlAspect.SIZE_ORDER.indexOf(this.props.maxInstanceSize);
        const currentIndex = CostControlAspect.SIZE_ORDER.indexOf(size);
        if (currentIndex > maxIndex) {
          Annotations.of(node).addWarning(
            `Instance size ${size} exceeds the limit ${this.props.maxInstanceSize}`,
          );
        }
      }
    }
  }
}
```

## Custom Aspect Pattern

Template for implementing your own governance policies.

```typescript
import { IAspect, IConstruct } from 'aws-cdk-lib';

export class CustomPolicyAspect implements IAspect {
  visit(node: IConstruct): void {
    // 1. Filter to the target resource type only
    if (!(node instanceof TargetCfnResource)) return;

    // 2. Check policy
    if (this.violatesPolicy(node)) {
      // 3. Report violation
      //    addError: fails cdk synth/deploy (production guard)
      //    addWarning: warning only (dev notification)
      //    addInfo: informational only
      Annotations.of(node).addError('Policy violation: {reason}');
    }

    // 4. Auto-fix (when possible)
    this.applyFix(node);
  }

  private violatesPolicy(node: TargetCfnResource): boolean {
    // Policy evaluation logic
    return false;
  }

  private applyFix(node: TargetCfnResource): void {
    // Auto-fix logic (optional)
  }
}
```

## Aspect Application Order

```typescript
// When applying multiple Aspects, they traverse in registration order
cdk.Aspects.of(stack).add(new RequiredTagsAspect({ ... }));          // 1st
cdk.Aspects.of(stack).add(new EncryptionEnforcementAspect(true));    // 2nd
cdk.Aspects.of(stack).add(new CostControlAspect({ ... }));           // 3rd
```

## Verification

```bash
# Aspects are applied during synth; errors/warnings appear in output
npx cdk synth

# Example error (from addError)
# [Error at /AppStack/DataBucket] S3 bucket has no encryption configured

# Example warning (from addWarning)
# [Warning at /AppStack/AppServer] Instance size 4xlarge exceeds the limit xlarge
```
