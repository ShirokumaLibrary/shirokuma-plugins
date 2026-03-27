# Local-to-Production Mapping Table

Correspondence table between local development environment (docker-compose) and production AWS services.

## Service Mapping Overview

| Local Service | Image Example | Production AWS Service | Notes |
|--------------|-------------|----------------------|-------|
| PostgreSQL | `postgres:16` | RDS PostgreSQL / Aurora PostgreSQL | Multi-AZ recommended |
| MySQL | `mysql:8` | RDS MySQL / Aurora MySQL | Multi-AZ recommended |
| Redis / Valkey | `valkey/valkey:8` | ElastiCache (Valkey engine) | Consider cluster mode |
| S3 (LocalStack) | `localstack/localstack:4` | Amazon S3 | Bucket policy + encryption required |
| SQS (LocalStack) | `localstack/localstack:4` | Amazon SQS | Choose Standard or FIFO |
| SNS (LocalStack) | `localstack/localstack:4` | Amazon SNS | Fan-out pattern |
| Mailhog / Mailpit | `mailhog/mailhog` | Amazon SES | Sender verification + bounce handling |
| MinIO | `minio/minio` | Amazon S3 | MinIO and S3 APIs are compatible |
| Elasticsearch | `elasticsearch:8` | Amazon OpenSearch Service | Index design is portable |
| MinIO + nginx | nginx | CloudFront + S3 | Static asset delivery |
| App container | custom | ECS Fargate / App Runner | Check port and health check path |
| nginx (reverse proxy) | `nginx` | ALB (Application Load Balancer) | Path-based routing |
| DynamoDB Local | `amazon/dynamodb-local` | Amazon DynamoDB | Table design migrates as-is |
| Lambda (SAM local) | `amazon/aws-sam-cli-emulation-*` | AWS Lambda | Check runtime, memory, and timeout |
| EventBridge (LocalStack) | `localstack/localstack:4` | Amazon EventBridge | Rule syntax is compatible |
| Secrets Manager (LocalStack) | `localstack/localstack:4` | AWS Secrets Manager | Credential management |

## Endpoint Switching Patterns

### Environment Variable Based Switching (Recommended)

```dotenv
# .env.local (local development)
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
DATABASE_URL=postgresql://user:password@localhost:5432/myapp

# .env.production (production — no endpoint override)
AWS_DEFAULT_REGION=ap-northeast-1
DATABASE_URL={injected from Secrets Manager}
# Credentials are automatically provided by IAM Task Role
```

### SDK Configuration Pattern

```typescript
// lib/aws-clients.ts
import { S3Client } from "@aws-sdk/client-s3";
import { SQSClient } from "@aws-sdk/client-sqs";

const isLocal = process.env.NODE_ENV === "development" || !!process.env.AWS_ENDPOINT_URL;

const localConfig = isLocal
  ? {
      endpoint: process.env.AWS_ENDPOINT_URL ?? "http://localhost:4566",
      region: process.env.AWS_DEFAULT_REGION ?? "us-east-1",
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID ?? "test",
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY ?? "test",
      },
      forcePathStyle: true, // Required for S3
    }
  : {};

export const s3Client = new S3Client(localConfig);
export const sqsClient = new SQSClient(localConfig);
```

> **SDK v3.x**: The `AWS_ENDPOINT_URL` environment variable is automatically recognized by AWS SDK v3.x. `forcePathStyle` for S3 is only needed when using LocalStack, so control it via an environment variable.

### Next.js Server Actions / API Routes Pattern

```typescript
// lib/s3.ts — environment-agnostic client
import { S3Client } from "@aws-sdk/client-s3";

export function getS3Client(): S3Client {
  if (process.env.NODE_ENV === "development") {
    return new S3Client({
      endpoint: process.env.AWS_ENDPOINT_URL ?? "http://localhost:4566",
      region: "us-east-1",
      forcePathStyle: true,
      credentials: { accessKeyId: "test", secretAccessKey: "test" },
    });
  }
  // Production: IAM Task Role automatically provides credentials
  return new S3Client({ region: process.env.AWS_DEFAULT_REGION });
}
```

## Per-Service Migration Checklists

### PostgreSQL → RDS PostgreSQL

- [ ] `max_connections` setting (RDS default: depends on instance type)
- [ ] SSL connection required (RDS can enforce SSL by default)
- [ ] Backup retention period configured (default: 7 days)
- [ ] Multi-AZ enabled (recommended for production)
- [ ] Parameter group customization

### Redis → ElastiCache (Valkey)

- [ ] Cluster mode vs standalone selection
- [ ] Automatic failover configured (multi-AZ)
- [ ] Security group allows access only from ECS tasks
- [ ] TLS enabled (encryption in transit)

### SQS (LocalStack) → Amazon SQS

- [ ] Standard Queue (order not required) vs FIFO Queue (order guaranteed) selection
- [ ] Visibility timeout configured (roughly 1.5x processing time)
- [ ] DLQ (Dead Letter Queue) configured (maxReceiveCount: 3 recommended)
- [ ] Message retention period (default: 4 days, max: 14 days)

### S3 (LocalStack/MinIO) → Amazon S3

- [ ] Block public access configured (all enabled recommended)
- [ ] Bucket encryption (SSE-S3 or SSE-KMS)
- [ ] CORS configured (when direct uploads from frontend)
- [ ] Lifecycle policy (expire old files, transition to Glacier)
- [ ] Versioning enabled (recommended for production buckets)

### Email (Mailhog/Mailpit) → Amazon SES

- [ ] Sender domain verified (DNS TXT record)
- [ ] Sandbox mode exit request submitted (for production use)
- [ ] Bounce and complaint notifications configured (via SNS)
- [ ] Sending limits confirmed (default: 200 emails/day)

## Cost Estimates (ap-northeast-1, as of 2024)

| Service | Minimum Configuration | Monthly Estimate |
|---------|----------------------|-----------------|
| RDS PostgreSQL t4g.micro (Single AZ) | Development / staging | ~$15 |
| RDS PostgreSQL t4g.small (Multi AZ) | Small-scale production | ~$60 |
| ElastiCache Valkey cache.t4g.micro | Small cache | ~$15 |
| ECS Fargate (0.25vCPU / 0.5GB × 2 tasks) | Minimum configuration | ~$15 |
| ALB (minimal traffic) | — | ~$20 |
| NAT Gateway | 1 per AZ | ~$45/AZ |

> These are reference values. Use the AWS Pricing Calculator for actual cost estimates.
