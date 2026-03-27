# docker-compose Pattern Collection

## Basic Structure

### File Naming

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Standard (recommended) |
| `compose.yml` | Docker Compose v2 preferred name |
| `docker-compose.override.yml` | Local overrides (gitignored) |

### Basic Service Definition

```yaml
services:
  {service-name}:
    image: {image}:{version}        # Pin version, avoid latest
    container_name: {project}-{service}  # Project name prefix recommended
    restart: unless-stopped
    environment:
      - ENV_VAR=${ENV_VAR:-default}  # Environment variables from .env
    ports:
      - "${PORT:-5432}:5432"         # Parameterize ports too
    volumes:
      - {volume-name}:/data
    networks:
      - {project}-network
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  {volume-name}:
    name: {project}-{volume-name}   # Volume names with prefix too

networks:
  {project}-network:
    name: {project}-network
```

## Service Type Patterns

### Database (PostgreSQL)

```yaml
postgres:
  image: postgres:16-alpine
  container_name: {project}-postgres
  restart: unless-stopped
  environment:
    - POSTGRES_USER=${POSTGRES_USER:-postgres}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
    - POSTGRES_DB=${POSTGRES_DB:-app}
  ports:
    - "${POSTGRES_PORT:-5432}:5432"
  volumes:
    - postgres-data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Cache (Valkey / Redis-compatible)

```yaml
valkey:
  image: valkey/valkey:8-alpine
  container_name: {project}-valkey
  restart: unless-stopped
  ports:
    - "${VALKEY_PORT:-6379}:6379"
  volumes:
    - valkey-data:/data
  healthcheck:
    test: ["CMD", "valkey-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

> **Note**: Use Valkey instead of Redis for new additions (maintains OSS license).

### Mail (Mailpit)

```yaml
mailpit:
  image: axllent/mailpit:v1.21-alpine
  container_name: {project}-mailpit
  restart: unless-stopped
  ports:
    - "${MAILPIT_SMTP_PORT:-1025}:1025"   # SMTP
    - "${MAILPIT_HTTP_PORT:-8025}:8025"   # Web UI
  environment:
    - MP_MAX_MESSAGES=500
  healthcheck:
    test: ["CMD", "wget", "--spider", "-q", "http://localhost:8025"]
    interval: 10s
    timeout: 5s
    retries: 5
```

## Dependency Patterns

### depends_on (with health check)

```yaml
app:
  depends_on:
    postgres:
      condition: service_healthy
    valkey:
      condition: service_healthy
```

## Startup Script Patterns

### Up script (all services)

```sh
#!/bin/sh
set -e
docker compose up -d
echo "All services started."
```

### Up script (plugin overlay)

When overlaying multiple compose files:

```sh
#!/bin/sh
set -e
docker compose -f docker-compose.yml -f docker-compose.plugins.yml up -d
```

## Volume Naming Convention

| Pattern | Example |
|---------|---------|
| `{project}-{service}-data` | `myapp-postgres-data` |
| `{project}-{service}-config` | `myapp-valkey-config` |

Project name prefix prevents volume conflicts across different projects.

## Common Issues and Solutions

| Problem | Cause | Solution |
|---------|-------|---------|
| Service startup order issues | depends_on doesn't wait for readiness | Use `condition: service_healthy` |
| Port conflicts | Same port used across multiple projects | Parameterize ports in `.env` |
| Data loss | Stopped without volumes | Always use named volumes |
| Breaking changes from `latest` tag | Image update changes behavior | Pin explicit version tags |
