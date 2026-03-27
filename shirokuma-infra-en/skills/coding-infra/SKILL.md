---
name: coding-infra
description: Implements and modifies local development infrastructure (docker-compose, scripts). Adding services, container configuration changes, startup script setup. Triggers: "add container", "add service", "modify docker-compose", "create startup script", "infra configuration".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, TaskGet, TaskList
---

# Infrastructure Coding

Implementation and modification of local development infrastructure using docker-compose and shell scripts.

> **Scope**: Focus on local development environment (docker-compose, startup scripts, env templates). Production infrastructure (AWS, Terraform, CI/CD) is out of scope.

## Before Starting

1. Check project `CLAUDE.md` for service configuration and naming conventions
2. Read the existing `docker-compose.yml` (or `compose.yml`) structure and follow it
3. Review naming conventions and patterns in [patterns/infra-conventions.md](patterns/infra-conventions.md)

## Workflow

### Step 1: Implementation Plan

Create a progress tracker with TaskCreate.

```markdown
## Implementation Plan

### Files to Change
- [ ] `docker-compose.yml` - Add/modify service
- [ ] `scripts/up-all.sh` - Update startup script

### Verification
- [ ] Port conflict check
- [ ] Dependency (depends_on) consistency
- [ ] Health check configuration
```

### Step 2: Implementation

Use `templates/`:
- `docker-compose-service.yml.template` - Service definition template

See [patterns/docker-compose.md](patterns/docker-compose.md) for patterns.

For service migrations (image changes, etc.), see [patterns/service-migration.md](patterns/service-migration.md).

### Step 3: Verification

```bash
# Syntax check
docker compose config

# Start service
docker compose up -d {service-name}

# Check logs
docker compose logs -f {service-name}

# Check health status
docker compose ps
```

### Step 4: Completion Report

Record changes as a comment on the Issue.

## Reference Documents

| Document | Content | When to Read |
|----------|---------|-------------|
| [patterns/docker-compose.md](patterns/docker-compose.md) | docker-compose pattern collection | When adding/modifying services |
| [patterns/service-migration.md](patterns/service-migration.md) | Service migration patterns | When changing images or renaming |
| [patterns/infra-conventions.md](patterns/infra-conventions.md) | Naming conventions, port assignments, health checks | Before any infrastructure work |
| [patterns/localstack.md](patterns/localstack.md) | LocalStack service definition, init scripts, AWS service availability | When adding AWS service emulation |
| [patterns/dockerfile.md](patterns/dockerfile.md) | Dockerfile multi-stage builds, pnpm cache, security best practices | When creating or modifying Dockerfiles |
| [templates/docker-compose-service.yml.template](templates/docker-compose-service.yml.template) | Service definition template | When adding new services |

## Quick Commands

```bash
docker compose up -d              # Start all services (background)
docker compose down               # Stop all services
docker compose ps                 # Check service status
docker compose logs -f {service}  # Follow logs
docker compose config             # Validate configuration syntax
docker compose pull               # Update images
```

## Next Steps

When invoked standalone (not via `implement-flow` chain):

```
Implementation complete. Next step:
→ `/commit-issue` to stage and commit your changes
```

## Notes

- **Follow existing structure** — Adhere to the project's docker-compose structure and naming conventions
- **Port management** — Refer to the port assignment table in [patterns/infra-conventions.md](patterns/infra-conventions.md) to avoid conflicts
- **Health checks required** — Configure health checks for production-grade services
- **Pin versions** — Avoid `latest` tag; always specify explicit versions
