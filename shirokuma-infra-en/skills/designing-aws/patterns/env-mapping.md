# Environment Variable Mapping Patterns

Strategies for mapping environment variables and connection strings between local development (docker-compose / LocalStack) and production (AWS).

## Environment Variable Naming Conventions

Standardize prefixes by service category to make differences between environments explicit.

| Prefix | Target Service | Example |
|--------|---------------|---------|
| `DATABASE_` | RDS / PostgreSQL / MySQL | `DATABASE_URL`, `DATABASE_HOST` |
| `CACHE_` | ElastiCache / Redis / Valkey | `CACHE_URL`, `CACHE_HOST` |
| `MAIL_` | SES / Mailhog / Mailpit | `MAIL_HOST`, `MAIL_FROM` |
| `STORAGE_` | S3 / MinIO / LocalStack S3 | `STORAGE_BUCKET`, `STORAGE_ENDPOINT` |
| `QUEUE_` | SQS / LocalStack SQS | `QUEUE_URL`, `QUEUE_REGION` |
| `AWS_` | AWS SDK common settings | `AWS_REGION`, `AWS_ENDPOINT_URL` |
| `NEXT_PUBLIC_` | Browser-exposed variables (Next.js) | `NEXT_PUBLIC_APP_URL` |

## Service-Level Variable Mapping Tables

### Database (PostgreSQL / RDS)

| Variable | Local Value (.env.local) | Production Value (.env.production) |
|----------|------------------------|----------------------------------|
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/myapp` | `{injected from Secrets Manager}` |
| `DATABASE_HOST` | `localhost` | `{RDS endpoint}` |
| `DATABASE_PORT` | `5432` | `5432` |
| `DATABASE_SSL` | `false` | `true` |

### Cache (Redis / ElastiCache Valkey)

| Variable | Local Value (.env.local) | Production Value (.env.production) |
|----------|------------------------|----------------------------------|
| `CACHE_URL` | `redis://localhost:6379` | `rediss://{ElastiCache endpoint}:6379` |
| `CACHE_TLS` | `false` | `true` |

> Use `rediss://` (with TLS) in production. ElastiCache Valkey supports in-transit encryption by default.

### Storage (S3 / LocalStack / MinIO)

| Variable | Local Value (.env.local) | Production Value (.env.production) |
|----------|------------------------|----------------------------------|
| `STORAGE_BUCKET` | `my-bucket` | `my-app-prod-bucket` |
| `STORAGE_ENDPOINT` | `http://localhost:4566` | `(omit — SDK uses default)` |
| `STORAGE_REGION` | `us-east-1` | `ap-northeast-1` |
| `STORAGE_FORCE_PATH_STYLE` | `true` | `false` |

### Mail (Mailhog / SES)

| Variable | Local Value (.env.local) | Production Value (.env.production) |
|----------|------------------------|----------------------------------|
| `MAIL_HOST` | `localhost` | `email-smtp.ap-northeast-1.amazonaws.com` |
| `MAIL_PORT` | `1025` | `587` |
| `MAIL_FROM` | `no-reply@localhost` | `no-reply@yourdomain.com` |
| `MAIL_USER` | `(omit)` | `{SES SMTP user}` |
| `MAIL_PASSWORD` | `(omit)` | `{injected from Secrets Manager}` |

### AWS SDK Common

| Variable | Local Value (.env.local) | Production Value (.env.production) |
|----------|------------------------|----------------------------------|
| `AWS_ENDPOINT_URL` | `http://localhost:4566` | `(do not set — SDK uses default)` |
| `AWS_ACCESS_KEY_ID` | `test` | `(do not set — use IAM Task Role)` |
| `AWS_SECRET_ACCESS_KEY` | `test` | `(do not set — use IAM Task Role)` |
| `AWS_DEFAULT_REGION` | `us-east-1` | `ap-northeast-1` |

> By leaving `AWS_ENDPOINT_URL` unset in production, the SDK automatically uses the real AWS endpoints. For SDK implementation patterns with endpoint switching, see [local-to-prod-mapping.md](local-to-prod-mapping.md).

## `.env` File Structure Strategy

### File Role Separation

| File | Purpose | Git Tracking |
|------|---------|--------------|
| `.env.example` | List of required variables (no values or sample values) | **Track** |
| `.env.local` | Actual values for local development | **Do not track** (add to `.gitignore`) |
| `.env.production` | Production settings (no secrets) | **Do not track** |
| `.env.test` | Test environment settings | Decide case by case |

### `.env.example` Template

```dotenv
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp

# Cache
CACHE_URL=redis://localhost:6379

# Storage
STORAGE_BUCKET=my-bucket
STORAGE_ENDPOINT=http://localhost:4566
STORAGE_REGION=us-east-1
STORAGE_FORCE_PATH_STYLE=true

# Mail
MAIL_HOST=localhost
MAIL_PORT=1025
MAIL_FROM=no-reply@localhost

# AWS SDK (set only for local development)
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

### Next.js Variable Scope

In Next.js, variable scope is controlled by naming convention:

| Scope | Naming Rule | Accessible From |
|-------|------------|----------------|
| Server-side only | No prefix (e.g., `DATABASE_URL`) | Server Components, Server Actions, API Routes only |
| Browser-exposed | `NEXT_PUBLIC_` prefix | All components (exposed to the browser) |

> **Important**: `NEXT_PUBLIC_` variables are embedded at build time. Never put secrets (API keys, DB passwords, etc.) in `NEXT_PUBLIC_` variables.

```dotenv
# Server-side only (not exposed to the browser)
DATABASE_URL=postgresql://...
AWS_ENDPOINT_URL=http://localhost:4566

# Exposed to the browser as well
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## Secret Management Patterns

### Local Development: Plain Text in `.env.local`

```dotenv
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
```

### Production: Inject from AWS Secrets Manager / SSM Parameter Store

#### Pattern A: ECS Task Definition `secrets` Field (Recommended)

Inject secrets into the ECS task definition via CDK:

```typescript
// CDK construct example (implementation handled by coding-cdk skill)
import { Secret } from "aws-cdk-lib/aws-secretsmanager";
import { ContainerImage, Secret as EcsSecret } from "aws-cdk-lib/aws-ecs";

const dbSecret = Secret.fromSecretNameV2(this, "DbSecret", "myapp/prod/database");

taskDefinition.addContainer("AppContainer", {
  image: ContainerImage.fromEcrRepository(repo),
  secrets: {
    DATABASE_URL: EcsSecret.fromSecretsManager(dbSecret, "url"),
  },
});
```

> Application code only needs to read `process.env.DATABASE_URL`. No secret-retrieval logic is required in the app.

#### Pattern B: Retrieve from SSM Parameter Store (in Application)

```typescript
// lib/config.ts — fetch config from SSM (once at startup)
import { SSMClient, GetParameterCommand } from "@aws-sdk/client-ssm";

const ssmClient = new SSMClient({ region: process.env.AWS_DEFAULT_REGION });

export async function getConfig() {
  if (process.env.NODE_ENV === "development") {
    return {
      databaseUrl: process.env.DATABASE_URL,
    };
  }

  const { Parameter } = await ssmClient.send(
    new GetParameterCommand({
      Name: "/myapp/prod/database-url",
      WithDecryption: true,
    })
  );

  return {
    databaseUrl: Parameter?.Value,
  };
}
```

> Prefer Pattern A (ECS `secrets` field). It eliminates the need for secret-retrieval logic in the application and simplifies IAM permission management.

### Secret Management Selection Criteria

| Use Case | Recommendation | Reason |
|----------|---------------|--------|
| Apps running on ECS / App Runner | ECS `secrets` field | Automatically injected at task startup; no app changes needed |
| Lambda functions | SSM Parameter Store | Lower latency during cold starts |
| Secrets shared across multiple services | Secrets Manager | Version management and automatic rotation support |
| Non-sensitive configuration values | SSM Parameter Store (Standard) | More cost-efficient |

## Related Patterns

| Pattern | Document | When to Reference |
|---------|---------|------------------|
| SDK configuration (LocalStack endpoint switching) | [local-to-prod-mapping.md](local-to-prod-mapping.md) | When initializing AWS clients in TypeScript code |
| AWS resource selection in general | [aws-resource-patterns.md](aws-resource-patterns.md) | When designing RDS, ElastiCache, and other resources |
