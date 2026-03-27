# Infrastructure Naming Conventions and Configuration Patterns

Naming conventions and configuration patterns for local development infrastructure (docker-compose).

## Naming Conventions

### Container Names

```
{project}-{service}
```

| Example | Description |
|---------|------------|
| `myapp-postgres` | PostgreSQL database |
| `myapp-valkey` | Valkey (Redis-compatible) cache |
| `myapp-mailpit` | Local mail server |

The project name prefix prevents container name conflicts when multiple projects run on the same host.

### Volume Names

```
{project}-{service}-data
```

| Example | Description |
|---------|------------|
| `myapp-postgres-data` | PostgreSQL data |
| `myapp-valkey-data` | Valkey persistent data |

### Network Names

```
{project}-network
```

Use a single project network for inter-service communication.

### Environment Variable Names

```
{SERVICE}_{PARAM}
```

| Example | Description |
|---------|------------|
| `POSTGRES_PORT` | PostgreSQL host-published port |
| `POSTGRES_USER` | PostgreSQL username |
| `VALKEY_PORT` | Valkey host-published port |
| `MAILPIT_SMTP_PORT` | Mailpit SMTP port |
| `MAILPIT_HTTP_PORT` | Mailpit Web UI port |
| `LOCALSTACK_PORT` | LocalStack unified endpoint port |
| `LOCALSTACK_SERVICES` | Comma-separated list of enabled AWS services |

## Port Assignments

Default ports for local development (overridable via environment variables):

| Service | Default Port | Environment Variable |
|---------|-------------|---------------------|
| PostgreSQL | 5432 | `POSTGRES_PORT` |
| Valkey / Redis | 6379 | `VALKEY_PORT` |
| Mailpit SMTP | 1025 | `MAILPIT_SMTP_PORT` |
| Mailpit Web UI | 8025 | `MAILPIT_HTTP_PORT` |
| LocalStack | 4566 | `LOCALSTACK_PORT` |

When running multiple projects simultaneously, offset ports in `.env` (e.g., `POSTGRES_PORT=5433`).

## Service Selection Criteria

| Purpose | Recommended Service | Reason |
|---------|-------------------|--------|
| Relational DB | PostgreSQL 16 | Matches production environment |
| Cache / Session | Valkey 8 | OSS license (BSD-3-Clause) |
| Local mail | Mailpit | Lightweight, includes Web UI |
| AWS service emulation | LocalStack Community Edition | Free, no AWS account required |

> **Redis is discouraged**: Redis 7.4+ uses SSPLv1 (not OSS-compatible). Use Valkey for new additions.

## File Structure

```
{project}/
├── docker-compose.yml        # Main compose definition
├── .env                      # Local environment variables (gitignored)
├── .env.example              # Environment variable template (git-tracked)
└── scripts/
    ├── up-all.sh             # All services startup script
    └── up-plugins.sh         # Plugin (additional services) startup script
```

## Health Check Requirements

Configure health checks for production-grade services.

| Service | test command |
|---------|-------------|
| PostgreSQL | `["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]` |
| Valkey | `["CMD", "valkey-cli", "ping"]` |
| MySQL | `["CMD", "mysqladmin", "ping", "-h", "localhost"]` |
| Mailpit | `["CMD", "wget", "--spider", "-q", "http://localhost:8025"]` |
| LocalStack | `["CMD", "curl", "-f", "http://localhost:4566/_localstack/health"]` |

Health checks enable `depends_on: condition: service_healthy`.

## Image Version Policy

- **No `latest` tag**: Specify explicit versions (e.g., `postgres:16-alpine`)
- **Prefer `-alpine` variants**: Smaller image size
- **Pin major version**: Minor version can float (e.g., `16-alpine`)
- **Update timing**: Use `docker compose pull` to synchronize across the team

## .env.example Template

```dotenv
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app
POSTGRES_PORT=5432

# Valkey
VALKEY_PORT=6379

# Mailpit
MAILPIT_SMTP_PORT=1025
MAILPIT_HTTP_PORT=8025

# LocalStack
LOCALSTACK_PORT=4566
LOCALSTACK_SERVICES=s3,sqs,sns
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```
