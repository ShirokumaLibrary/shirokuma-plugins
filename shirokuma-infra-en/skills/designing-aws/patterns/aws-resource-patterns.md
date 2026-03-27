# AWS Resource Design Patterns

## Compute

### Selection Matrix

| Use Case | Recommended Service | Reason |
|---------|-------------------|--------|
| Web app (containers) | ECS Fargate | Serverless, low operational overhead |
| Web app (high traffic) | ECS EC2 + Auto Scaling | Cost-optimized, flexible CPU/memory |
| Short-lived batch processing | Lambda | Event-driven, cost-efficient |
| Long-running batch processing | ECS Fargate Tasks | Supports tasks exceeding 15 minutes |
| Monolith migration | App Runner | Minimal ops, deploy directly from container image |
| ML inference | SageMaker Inference | GPU support, integrated model management |

### ECS Fargate Configuration Patterns

```
CPU: 0.25vCPU (256), 0.5vCPU (512), 1vCPU (1024), 2vCPU (2048)
Memory: 512MB to 4GB per CPU unit
Task count: Minimum 2 (multi-AZ)
```

### ALB + ECS Architecture (Standard Pattern)

```
Internet Gateway
    ↓
ALB (public subnets)
    ↓
ECS Fargate tasks (private subnets)
    ↓
RDS / ElastiCache (DB subnets)
```

---

## Data Stores

### Relational Database Selection Matrix

| Use Case | Recommended | Reason |
|---------|------------|--------|
| Standard web app | RDS PostgreSQL | Fully managed, multi-AZ support |
| Read-heavy workloads | Aurora PostgreSQL | Cluster auto-scaling |
| Development / staging | RDS PostgreSQL t4g.micro | Minimum cost |
| Production (small scale) | RDS PostgreSQL t4g.small / db.t4g.medium | Cost balance |

### Cache Selection Matrix

| Use Case | Recommended | Reason |
|---------|------------|--------|
| Sessions and general caching | Valkey (ElastiCache) | OSS, Redis-compatible |
| Simple caching only | ElastiCache Serverless | Zero ops, pay-per-use |
| Read-heavy caching | DAX (when using DynamoDB) | In-memory, auto-scaling |

> **Note**: Due to the Redis OSS license change (2024), Valkey is recommended for new adoptions. ElastiCache supports the Valkey engine (since 2024).

### Local-to-Production Mapping

| Local | Production AWS |
|-------|---------------|
| PostgreSQL (Docker) | RDS PostgreSQL / Aurora PostgreSQL |
| Redis / Valkey (Docker) | ElastiCache (Valkey engine) |
| MySQL (Docker) | RDS MySQL / Aurora MySQL |
| MongoDB (Docker) | DocumentDB (verify compatibility) |

---

## Messaging

### Selection Matrix

| Use Case | Recommended | Reason |
|---------|------------|--------|
| Async task queues | SQS Standard | Simple, high throughput |
| Ordering required | SQS FIFO | Order guarantee, deduplication |
| Pub/Sub (one-to-many) | SNS + SQS fan-out | Deliver to multiple consumers |
| Event-driven architecture | EventBridge | Rule-based routing |
| Streaming | Kinesis Data Streams | Real-time, multiple consumers |

### SQS + Lambda Pattern (Async Processing)

```
Producer (ECS) → SQS → Lambda (consumer)
                  ↓ (on failure)
                 DLQ (Dead Letter Queue)
```

---

## Storage

### S3 Bucket Design

| Use Case | Configuration Approach |
|---------|----------------------|
| User uploads | Bucket policy allowing only CloudFront access |
| Static assets | CloudFront + S3 Origin |
| Backups | Lifecycle rule to Glacier after 90 days |
| Log retention | S3 Intelligent-Tiering |

### S3 Security Configuration

```
Block Public Access: All enabled (default)
Encryption: SSE-S3 or SSE-KMS
Versioning: Enable for production buckets
Access logs: Record to a dedicated log bucket
```

---

## Network

### Standard VPC Architecture

```
VPC: 10.0.0.0/16

Public Subnets (per AZ):
  ap-northeast-1a: 10.0.0.0/24  ← ALB, NAT Gateway
  ap-northeast-1c: 10.0.1.0/24

Private Subnets (per AZ):
  ap-northeast-1a: 10.0.10.0/24  ← ECS tasks, Lambda
  ap-northeast-1c: 10.0.11.0/24

DB Subnets (per AZ):
  ap-northeast-1a: 10.0.20.0/24  ← RDS, ElastiCache
  ap-northeast-1c: 10.0.21.0/24
```

### Security Group Design Principles

| Layer | Inbound | Outbound |
|-------|---------|---------|
| ALB | 0.0.0.0/0:443 (HTTPS) | ECS SG:8080 |
| ECS | ALB SG:8080 | DB SG:5432, 0.0.0.0/0:443 (HTTPS) |
| RDS | ECS SG:5432 | None |
| ElastiCache | ECS SG:6379 | None |

### NAT Gateway vs VPC Endpoint

| Use Case | Recommended |
|---------|------------|
| General outbound traffic | NAT Gateway (in public subnet) |
| Access to S3 / DynamoDB | VPC Endpoint (Gateway type: free) |
| Secrets Manager / ECR | VPC Endpoint (Interface type: consider cost) |

---

## CDK Construct Design

### Construct Level Selection

| Level | Overview | When to Use |
|-------|---------|------------|
| **L1** | Direct CloudFormation resource mapping (`Cfn*`) | New services, when fine-grained control is needed |
| **L2** | High-level API with AWS defaults and security best practices applied | **Recommended default** |
| **L3** | Complete architecture patterns combining multiple L2 constructs (`patterns.*`) | Building a standard full architecture in one shot |

### Recommended L2 Constructs

```typescript
// RDS: L2 DatabaseInstance
const db = new rds.DatabaseInstance(this, 'Database', {
  engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_16 }),
  instanceType: ec2.InstanceType.of(ec2.InstanceClass.T4G, ec2.InstanceSize.SMALL),
  vpc,
  vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
  multiAz: true,
  deletionProtection: true,
});

// ECS: L2 FargateService
const service = new ecs.FargateService(this, 'Service', {
  cluster,
  taskDefinition,
  desiredCount: 2,
  vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
});
```

### Stack Splitting Pattern

| Stack | Resources | Change Frequency |
|-------|-----------|-----------------|
| `NetworkStack` | VPC, subnets, security groups | Low |
| `StatefulStack` | RDS, ElastiCache, S3 | Low |
| `AppStack` | ECS, ALB, Lambda, IAM roles | High |

> Use `stack.exportValue()` / `Fn.importValue()` for cross-stack references. Note that CloudFormation cross-stack references can block deletion due to dependencies.

### Props Design Principles

```typescript
// Good: receive environment-varying values via Props
interface AppStackProps extends cdk.StackProps {
  environment: 'staging' | 'production';
  desiredCount: number;
  dbInstanceType: ec2.InstanceType;
}

// Bad: trying to handle environment differences with hardcoded conditionals
// if (process.env.ENV === 'production') { ... }
```

---

## Security

### IAM Role Design Principles

| Principle | Implementation |
|-----------|--------------|
| Least privilege | Allow only the required actions and resources |
| Role-based | Avoid granting permissions directly to users; attach roles instead |
| Task role separation | Separate ECS task role (for app) from task execution role (for ECS control plane) |

### Secret Management

| Secret Type | Recommended Service | Reason |
|------------|-------------------|--------|
| DB credentials | Secrets Manager | Automatic rotation support |
| API keys | Secrets Manager | Version control, audit logs |
| Configuration values (non-sensitive) | SSM Parameter Store | Lower cost (free tier) |
| Environment variables (non-sensitive) | ECS task definition `environment` | Simple |

### CDK Secret Injection Pattern

```typescript
// Injecting secrets into ECS task definition
const secret = secretsmanager.Secret.fromSecretNameV2(this, 'DbSecret', 'myapp/db');

taskDefinition.addContainer('app', {
  // ...
  secrets: {
    DATABASE_URL: ecs.Secret.fromSecretsManager(secret, 'url'),
  },
});
```
