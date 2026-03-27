---
name: coding-aws
description: Implements application code using the AWS SDK, or provides setup guidance for AWS service configuration. Handles SDK code, console operations, and AWS CLI-based tasks — not IaC (CDK/Terraform). Triggers: "AWS SDK", "AWS configuration", "S3 implementation", "SES implementation", "SNS implementation", "SQS implementation", "Cognito implementation", "AWS CLI setup", "IAM role setup".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TaskGet, TaskList
---

# AWS Coding

Implement application code using the AWS SDK, or provide guidance for AWS service configuration and setup.

> **Scope boundary:** IaC (CDK constructs, CloudFormation) is `coding-cdk`'s responsibility. This skill focuses on SDK-based application code implementation and console/AWS CLI-based service configuration.

## Scope

- **Category:** Mutation Worker
- **Scope:** Implementing application code using the AWS SDK v3 (Write / Edit), providing AWS CLI-based service configuration guidance (Bash), managing environment-specific configuration.
- **Out of scope:** CDK construct implementation (delegated to `coding-cdk`), AWS resource design (delegated to `designing-aws`), docker-compose configuration (delegated to `coding-infra`)

## Before Starting

1. Check the project `CLAUDE.md` for AWS services in use and SDK version
2. Review existing AWS SDK configuration files (`src/lib/aws.ts`, etc.)
3. Read `designing-aws` design artifacts if available
4. Confirm whether LocalStack emulation is needed (local development environment)

## Workflow

### Step 1: Implementation Plan

Create a progress tracker with TaskCreate.

```markdown
## Implementation Plan

### Files to Change
- [ ] `src/lib/aws-client.ts` - AWS client configuration
- [ ] `src/services/{service}.ts` - Service implementation

### Verification
- [ ] Environment-specific endpoint switching (LocalStack vs production)
- [ ] IAM permissions (minimum required Actions)
- [ ] Error handling (retry, timeout)
- [ ] Type safety (leverage AWS SDK v3 type definitions)
```

### Step 2: AWS SDK Client Configuration

#### Environment-specific Endpoint Switching

```typescript
// Pattern for switching between local (LocalStack) and production
import { S3Client } from '@aws-sdk/client-s3';

const isLocal = process.env.NODE_ENV === 'development';

export const s3Client = new S3Client({
  region: process.env.AWS_REGION ?? 'ap-northeast-1',
  ...(isLocal && {
    endpoint: process.env.AWS_ENDPOINT_URL ?? 'http://localhost:4566',
    credentials: {
      accessKeyId: 'test',
      secretAccessKey: 'test',
    },
    forcePathStyle: true,  // Required for LocalStack
  }),
});
```

### Step 3: Service-Specific Implementation Patterns

#### S3 Operations

| Operation | SDK Command | Use Case |
|-----------|-----------|---------|
| Upload file | `PutObjectCommand` | Upload images, documents |
| Get file | `GetObjectCommand` | File download |
| Pre-signed URL | `getSignedUrl + GetObjectCommand` | Temporary download URL |
| List buckets | `ListBucketsCommand` | Admin operations |
| Delete object | `DeleteObjectCommand` | Cleanup |

#### SES Email

| Operation | SDK Command | Use Case |
|-----------|-----------|---------|
| Send email | `SendEmailCommand` | Transactional email |
| Template email | `SendTemplatedEmailCommand` | Dynamic content email |

#### SQS Messaging

| Operation | SDK Command | Use Case |
|-----------|-----------|---------|
| Send message | `SendMessageCommand` | Enqueue to queue |
| Receive message | `ReceiveMessageCommand` | Dequeue from queue |
| Delete message | `DeleteMessageCommand` | Delete after processing |

#### SNS Notifications

| Operation | SDK Command | Use Case |
|-----------|-----------|---------|
| Publish notification | `PublishCommand` | Publish to topic |
| Subscribe | `SubscribeCommand` | Register endpoint |

#### Cognito Authentication

| Operation | SDK Command | Use Case |
|-----------|-----------|---------|
| User registration | `SignUpCommand` | Self-service signup |
| Authentication | `InitiateAuthCommand` | Login |
| Token refresh | `InitiateAuthCommand (REFRESH_TOKEN)` | Extend session |

### Step 4: AWS CLI Setup Guidance

When console operations or CLI-based service configuration is needed:

#### IAM Role Configuration

```bash
# Create OIDC provider (for GitHub Actions)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list {thumbprint}

# Create IAM role
aws iam create-role \
  --role-name {role-name} \
  --assume-role-policy-document file://trust-policy.json
```

#### S3 Bucket Configuration

```bash
# Create bucket
aws s3api create-bucket \
  --bucket {bucket-name} \
  --region ap-northeast-1 \
  --create-bucket-configuration LocationConstraint=ap-northeast-1

# Enable bucket encryption
aws s3api put-bucket-encryption \
  --bucket {bucket-name} \
  --server-side-encryption-configuration '{
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket {bucket-name} \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Step 5: Validation

```bash
# TypeScript type check
npx tsc --noEmit

# Verify with local (LocalStack)
aws --endpoint-url=http://localhost:4566 s3 ls

# Unit tests (with mocks)
pnpm test {service}.test.ts
```

### Step 6: Completion Report

Record changes as a comment on the Issue.

## Error Handling Patterns

```typescript
import { S3ServiceException } from '@aws-sdk/client-s3';

try {
  await s3Client.send(new GetObjectCommand({ Bucket, Key }));
} catch (error) {
  if (error instanceof S3ServiceException) {
    if (error.name === 'NoSuchKey') {
      throw new NotFoundError(`Object not found: ${Key}`);
    }
    if (error.$retryable) {
      // Retryable error (throttling, etc.)
      throw new RetryableError(error.message);
    }
  }
  throw error;
}
```

## Quick Commands

```bash
# LocalStack operations
aws --endpoint-url=http://localhost:4566 s3 ls
aws --endpoint-url=http://localhost:4566 sqs list-queues
aws --endpoint-url=http://localhost:4566 sns list-topics

# Production AWS operations
aws s3 ls --region ap-northeast-1
aws iam list-roles --query 'Roles[?contains(RoleName, `github`)]'
aws sts get-caller-identity  # Check current credentials
```

## Next Steps

When invoked standalone (not via `implement-flow` chain):

```
Implementation complete. Next step:
→ `/commit-issue` to stage and commit your changes
```

## Notes

- **Do not implement CDK code** — IaC is `coding-cdk`'s responsibility. This skill focuses on SDK code and service configuration
- **Never embed IAM access keys in code** — Use environment variables / Secrets Manager / OIDC
- **Always configure LocalStack endpoint switching** — Use the `AWS_ENDPOINT_URL` environment variable pattern
- **Use AWS SDK v3** — v2 (`aws-sdk`) is deprecated. Use `@aws-sdk/client-*` packages
- **Do not hardcode regions** — Read from `process.env.AWS_REGION`
