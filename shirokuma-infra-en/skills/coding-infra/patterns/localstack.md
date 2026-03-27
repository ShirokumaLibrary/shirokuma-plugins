# LocalStack Pattern Collection

## Overview

LocalStack Community Edition provides AWS service emulation for local development. No AWS account or costs required.

## Docker Compose Service Definition

```yaml
localstack:
  image: localstack/localstack:4
  container_name: {project}-localstack
  restart: unless-stopped
  ports:
    - "${LOCALSTACK_PORT:-4566}:4566"   # Unified endpoint
  environment:
    - SERVICES=${LOCALSTACK_SERVICES:-s3,sqs,sns}
    - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
    - LOCALSTACK_AUTH_TOKEN=${LOCALSTACK_AUTH_TOKEN:-}  # Pro edition only
  volumes:
    - localstack-data:/var/lib/localstack
    - ./scripts/localstack/init:/etc/localstack/init/ready.d:ro  # Init scripts
    - /var/run/docker.sock:/var/run/docker.sock  # Required for some services
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:4566/_localstack/health"]
    interval: 10s
    timeout: 5s
    retries: 5

volumes:
  localstack-data:
    name: {project}-localstack-data
```

## Initialization Scripts

Place shell scripts in `/etc/localstack/init/ready.d/` to run after LocalStack starts.

### Directory Structure

```text
scripts/
└── localstack/
    └── init/
        └── 01-setup-resources.sh
```

> **Note**: Files are executed in alphabetical order. Use numeric prefixes (`01-`, `02-`) to control execution order.

### Example: Create S3 Bucket and SQS Queue

```sh
#!/bin/bash
set -e

ENDPOINT="http://localhost:4566"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

echo "=== LocalStack Initialization ==="

# Create S3 bucket
awslocal s3 mb s3://my-app-uploads --region "$REGION"
echo "S3 bucket created: my-app-uploads"

# Create SQS queue
awslocal sqs create-queue --queue-name my-app-jobs --region "$REGION"
echo "SQS queue created: my-app-jobs"

echo "=== Initialization complete ==="
```

## awslocal CLI vs aws --endpoint-url

Two approaches to interact with LocalStack:

| Approach | Command | When to Use |
|----------|---------|-------------|
| `awslocal` | `awslocal s3 ls` | Local development (simpler) |
| `aws --endpoint-url` | `aws s3 ls --endpoint-url http://localhost:4566` | Scripting (endpoint is explicit) |

### awslocal Installation

```bash
pip install awscli-local
```

`awslocal` is a wrapper around `aws` that automatically sets `--endpoint-url` and dummy credentials. Recommended for interactive use.

### Dummy Credentials (Required for aws CLI)

```dotenv
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

LocalStack accepts any credential values. Use `test` / `test` as convention.

## Community Edition Service Availability

| Service | Available | Notes |
|---------|-----------|-------|
| S3 | Yes | Full support |
| SQS | Yes | Full support |
| SNS | Yes | Full support |
| DynamoDB | Yes | Full support |
| Lambda | Yes | Requires Docker socket |
| EventBridge | Yes | Basic support |
| Secrets Manager | Yes | Basic support |
| SSM Parameter Store | Yes | Basic support |
| SES | Yes | Basic support |
| API Gateway | Partial | Some limitations |
| RDS | No | Pro edition only |
| ElastiCache | No | Pro edition only |
| Cognito | Partial | Limited features |

> Full list: https://docs.localstack.cloud/references/coverage/

## Endpoint Configuration Patterns

### Application-side Configuration (Local vs Production)

```typescript
// lib/aws-config.ts
import { S3Client } from "@aws-sdk/client-s3";

const isLocal = process.env.NODE_ENV === "development";

export const s3Client = new S3Client({
  region: process.env.AWS_DEFAULT_REGION ?? "us-east-1",
  ...(isLocal && {
    endpoint: process.env.AWS_ENDPOINT_URL ?? "http://localhost:4566",
    forcePathStyle: true,  // Required for LocalStack S3
    credentials: {
      accessKeyId: "test",
      secretAccessKey: "test",
    },
  }),
});
```

### Environment Variable Pattern

```dotenv
# .env (local development)
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

```dotenv
# .env.production (production — no endpoint override)
AWS_DEFAULT_REGION=ap-northeast-1
# Credentials injected via IAM Role / ECS Task Role
```

### Next.js / Node.js SDK v3 Pattern

```typescript
// Automatically uses AWS_ENDPOINT_URL if set
const client = new S3Client({
  region: process.env.AWS_DEFAULT_REGION,
  // SDK v3.x reads AWS_ENDPOINT_URL env var automatically
});
```

> **SDK v3.x**: `AWS_ENDPOINT_URL` environment variable is automatically recognized (since v3.x). Explicit `endpoint` config is not needed when using this env var.

## Health Check Configuration

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:4566/_localstack/health"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Dependency Configuration

```yaml
app:
  depends_on:
    localstack:
      condition: service_healthy
```

## Common Issues and Solutions

| Problem | Cause | Solution |
|---------|-------|---------|
| Init scripts not executed | Wrong mount path | Mount to `/etc/localstack/init/ready.d/` |
| Init scripts not executed | Missing execute permission | Add `chmod +x` or run `awslocal` directly |
| S3 path-style URL error | `forcePathStyle` not set | Set `forcePathStyle: true` in SDK config |
| Lambda cold start slow | Docker image pull on first run | Pre-pull Lambda runtime images |
| Data not persisted after restart | Volume not configured | Mount `localstack-data` volume |
