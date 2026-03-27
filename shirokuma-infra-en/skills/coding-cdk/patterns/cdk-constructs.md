# CDK Construct Patterns

## L2/L3 Construct Usage Matrix

| Construct Level | Condition | Recommendation | Reason |
|----------------|-----------|----------------|--------|
| L3 (pattern) | Matches AWS Solutions Constructs or CDK Patterns | Top priority | Battle-tested; default settings follow best practices |
| L2 (high-level) | Standard AWS service configuration coverable by Props | Recommended | Type-safe; hides CloudFormation details |
| L2 + escape hatch | Settings not available in L2 Props | Conditionally recommended | Fine-grained control while keeping L2 |
| L1 (CloudFormation) | New service with no L2/L3, or fine-grained control is essential | Last resort | Writing CloudFormation raw properties in TypeScript |

### Decision Flow

```
Review requirements
    ↓
Matches AWS Solutions Constructs / CDK Patterns? → YES → Use L3
    ↓ NO
Does aws-cdk-lib have a corresponding L2 construct? → YES → Use L2
    ↓ NO
Can L2's CfnXxx.addPropertyOverride() handle it? → YES → Use L2 + escape hatch
    ↓ NO
Use L1 (CfnXxx) — document the reason in a comment
```

## Props Design Guide

### Interface design pattern

```typescript
// Basic Props interface pattern
export interface MyConstructProps {
  // Required: essential for the construct to work
  readonly vpc: ec2.IVpc;
  readonly environment: 'dev' | 'staging' | 'prod';

  // Optional: items with sensible defaults
  readonly instanceType?: ec2.InstanceType;
  readonly removalPolicy?: cdk.RemovalPolicy;
  readonly enableDeletionProtection?: boolean;
}
```

### Required vs Optional decision criteria

| Decision | Required | Optional |
|----------|----------|----------|
| The construct cannot function without it | YES | — |
| A safe default value exists | — | YES |
| The value differs per environment (dev/prod) | YES | — |
| The same value is used in most cases | — | YES |

### Setting defaults

```typescript
export class MyConstruct extends Construct {
  constructor(scope: Construct, id: string, props: MyConstructProps) {
    super(scope, id);

    // Resolve defaults in the constructor
    const instanceType = props.instanceType
      ?? ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.SMALL);

    const removalPolicy = props.removalPolicy
      ?? (props.environment === 'prod'
        ? cdk.RemovalPolicy.RETAIN
        : cdk.RemovalPolicy.DESTROY);
  }
}
```

## Escape Hatch Pattern

Technique for accessing L1 from an L2 construct to set properties not available in L2.

```typescript
// Create an L2 construct
const bucket = new s3.Bucket(this, 'Bucket', {
  versioned: true,
  encryption: s3.BucketEncryption.S3_MANAGED,
});

// Access L1 (CfnBucket) to set properties not supported by L2
const cfnBucket = bucket.node.defaultChild as s3.CfnBucket;
cfnBucket.addPropertyOverride('ObjectLockEnabled', true);
cfnBucket.addPropertyOverride('ObjectLockConfiguration', {
  ObjectLockEnabled: 'Enabled',
  Rule: {
    DefaultRetention: {
      Mode: 'COMPLIANCE',
      Years: 7,
    },
  },
});
```

### Escape hatch notes

- Use `as` cast to make the type explicit rather than `!` assertion when `node.defaultChild` might be undefined
- CloudFormation property names are PascalCase (e.g., `ObjectLockEnabled`)
- Leave a comment so it's easy to replace when L2 eventually adds support

## Construct Composition Pattern

Group multiple AWS resources into a single construct for improved reusability.

### Example: ECS service construct

```typescript
export interface AppServiceProps {
  readonly vpc: ec2.IVpc;
  readonly cluster: ecs.ICluster;
  readonly image: ecs.ContainerImage;
  readonly environment: Record<string, string>;
  readonly secrets: Record<string, ecs.Secret>;
  readonly desiredCount?: number;
}

export class AppService extends Construct {
  public readonly service: ecs.FargateService;
  public readonly loadBalancer: elbv2.ApplicationLoadBalancer;

  constructor(scope: Construct, id: string, props: AppServiceProps) {
    super(scope, id);

    const taskDefinition = new ecs.FargateTaskDefinition(this, 'TaskDef', {
      memoryLimitMiB: 512,
      cpu: 256,
    });

    taskDefinition.addContainer('App', {
      image: props.image,
      environment: props.environment,
      secrets: props.secrets,
      logging: ecs.LogDrivers.awsLogs({ streamPrefix: id }),
    });

    this.loadBalancer = new elbv2.ApplicationLoadBalancer(this, 'ALB', {
      vpc: props.vpc,
      internetFacing: true,
    });

    this.service = new ecs.FargateService(this, 'Service', {
      cluster: props.cluster,
      taskDefinition,
      desiredCount: props.desiredCount ?? 2,
    });

    // ALB → ECS routing
    const listener = this.loadBalancer.addListener('Listener', { port: 80 });
    listener.addTargets('Target', {
      port: 80,
      targets: [this.service],
      healthCheck: { path: '/health' },
    });
  }
}
```

### Composition pattern guidelines

- Each construct has a **single responsibility** (ECS service, RDS cluster, etc.)
- Expose resources that external constructs need to reference as `public readonly`
- Pass cross-stack dependencies via Props (use interface types like `IVpc`, `ICluster`)
- Construct `id` must be unique within a stack

## Naming Conventions

```typescript
// Stack: PascalCase
class NetworkStack extends cdk.Stack {}

// Construct: PascalCase
class AppService extends Construct {}

// Resource ID: PascalCase (CloudFormation logical ID)
new s3.Bucket(this, 'DataBucket', { ... });

// CDK outputs: kebab-case recommended (export name)
new cdk.CfnOutput(this, 'VpcId', {
  exportName: `${id}-vpc-id`,
  value: this.vpc.vpcId,
});
```
