# Environment Configuration Management Patterns

## Comparison of Three Approaches

| Approach | Use Case | Pros | Cons |
|----------|----------|------|------|
| `cdk.json` contexts | Non-secret config (region, instance types, etc.) | Simple; version-controlled | No secrets; context keys grow complex |
| Props injection | Passing config between stacks | Type-safe; easy to test | Config concentrates in `bin/app.ts` |
| SSM Parameter Store | Secrets and environment-specific sensitive values | Secure; supports rotation | Requires SSM access during deploy |

## Recommended Pattern: Props Injection + SSM (for secrets only)

```typescript
// bin/app.ts - Centralize environment-specific configuration
const app = new cdk.App();

// Non-secret config from cdk.json context or defined directly
const env = app.node.tryGetContext('env') ?? 'dev';
const config = getConfig(env);

new AppStack(app, `AppStack-${env}`, {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'ap-northeast-1' },
  environment: env,
  instanceType: config.instanceType,
  desiredCount: config.desiredCount,
});

function getConfig(environment: string) {
  const configs: Record<string, { instanceType: string; desiredCount: number }> = {
    dev: { instanceType: 't3.small', desiredCount: 1 },
    staging: { instanceType: 't3.medium', desiredCount: 2 },
    prod: { instanceType: 't3.large', desiredCount: 4 },
  };
  return configs[environment] ?? configs['dev'];
}
```

## Using `cdk.json` Contexts

Manage non-secret, environment-independent configuration here.

```json
{
  "app": "npx ts-node --prefer-ts-exts bin/app.ts",
  "context": {
    "env": "dev",
    "@aws-cdk/aws-apigateway:usagePlanKeyOrderInsensitiveId": true,
    "@aws-cdk/aws-lambda:recognizeLayerVersion": true,
    "vpcCidr": "10.0.0.0/16",
    "availabilityZones": ["ap-northeast-1a", "ap-northeast-1c"]
  }
}
```

Accessing from a construct:

```typescript
const vpcCidr = this.node.tryGetContext('vpcCidr') as string ?? '10.0.0.0/16';
```

## Environment-Specific Stack Separation Pattern

Separate stacks by environment within the same CDK app to control deploy units.

```typescript
// bin/app.ts
const envs = ['dev', 'staging', 'prod'] as const;

for (const env of envs) {
  const config = getConfig(env);

  new NetworkStack(app, `Network-${env}`, {
    env: awsEnv,
    environment: env,
    vpcCidr: config.vpcCidr,
  });

  new DatabaseStack(app, `Database-${env}`, {
    env: awsEnv,
    environment: env,
    // cross-stack reference: receive output from NetworkStack
    vpc: NetworkStack.vpcFromExportedValues(app, env),
  });
}
```

## Configuration Injection via SSM Parameter Store

### Non-secret configuration (StringParameter)

```typescript
// Write non-secret config (managed separately in CDK)
new ssm.StringParameter(this, 'ApiEndpoint', {
  parameterName: `/myapp/${props.environment}/api-endpoint`,
  stringValue: `https://api.${props.environment}.example.com`,
});

// Read (resolved at deploy time)
const apiEndpoint = ssm.StringParameter.valueForStringParameter(
  this,
  `/myapp/${props.environment}/api-endpoint`,
);
```

### Secrets (SecureString)

```typescript
// Via Secrets Manager (recommended)
const dbSecret = secretsmanager.Secret.fromSecretNameV2(
  this,
  'DbSecret',
  `/myapp/${props.environment}/db-password`,
);

// Reference secrets in ECS task definition
taskDefinition.addContainer('App', {
  secrets: {
    DB_PASSWORD: ecs.Secret.fromSecretsManager(dbSecret),
    API_KEY: ecs.Secret.fromSsmParameter(
      ssm.StringParameter.fromSecureStringParameterAttributes(this, 'ApiKey', {
        parameterName: `/myapp/${props.environment}/api-key`,
        version: 1,
      }),
    ),
  },
});
```

## Environment-Specific RemovalPolicy

```typescript
// Switch deletion policy based on environment
const removalPolicy = props.environment === 'prod'
  ? cdk.RemovalPolicy.RETAIN     // Production: prevent accidental deletion
  : cdk.RemovalPolicy.DESTROY;   // Non-production: easy cleanup

new s3.Bucket(this, 'DataBucket', {
  removalPolicy,
  autoDeleteObjects: props.environment !== 'prod', // false in production
});
```

## Deploy Commands (with environment)

```bash
# Specify environment via context
npx cdk deploy --context env=dev
npx cdk deploy --context env=prod

# Deploy specific stacks only
npx cdk deploy "Network-prod" "Database-prod" --context env=prod

# Check diff
npx cdk diff --context env=prod
```
