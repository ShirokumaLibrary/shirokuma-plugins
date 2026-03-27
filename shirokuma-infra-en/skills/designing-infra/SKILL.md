---
name: designing-infra
description: Designs local development infrastructure. Covers docker-compose service configuration design, multi-stage Dockerfile design, local development environment service partitioning strategy, and port assignment planning. Triggers: "infra design", "docker-compose design", "local environment design", "container design", "Dockerfile design", "dev environment design".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# Local Development Infrastructure Design

Design docker-compose service configuration, Dockerfile structure, and local development environment architecture.

> **Scope boundary:** `coding-infra` handles docker-compose and script implementation, while this skill handles design decisions — what to configure and how. AWS production environment design is handled by `designing-aws`.

## Scope

- **Category:** Investigation Worker
- **Scope:** Reading existing docker-compose and Dockerfile files (Read / Grep / Glob / Bash read-only commands), generating infrastructure design documents (Write/Edit — for design artifacts), appending design sections to Issue bodies.
- **Out of scope:** docker-compose implementation and modification (delegated to `coding-infra`), AWS production infrastructure design (delegated to `designing-aws`), CI/CD design (delegated to `designing-cicd`)

> **Writing design artifacts**: When this skill uses Write/Edit on Issue bodies or design documents, it is producing design process outputs — not modifying production code. This is a permitted exception for Investigation Workers.

## Workflow

### 0. Check Existing Infrastructure Configuration

**First**, read the project `CLAUDE.md` and existing files:

- Technology stack (framework, runtime, DB, etc.)
- Structure and service list of the existing docker-compose.yml
- Existing Dockerfile structure (multi-stage or not)
- Current port assignments

```bash
cat docker-compose.yml 2>/dev/null || cat compose.yml 2>/dev/null
find . -name "Dockerfile*" | head -10
```

### 1. Design Context Check

When delegated from `design-flow`, a Design Brief and requirements are passed. Use them as-is.

When invoked standalone, understand design requirements from the Issue body and plan section.

### 2. Service Configuration Design

#### Service Categories

| Category | Service Examples | Design Considerations |
|---------|-----------------|----------------------|
| Application | Next.js, Node.js API | Hot reload config, env files |
| Database | PostgreSQL, MySQL | Persistent volumes, init scripts |
| Cache | Redis | Volatile vs persistent storage choice |
| Messaging | RabbitMQ, Kafka | Management UI ports |
| AWS Emulation | LocalStack | Service configuration, startup order |
| Dev tools | MailHog, Adminer | Development-only startup |

#### Service Design Decisions

| Aspect | Design Content |
|--------|---------------|
| Dependencies | Control service startup order using `depends_on` and `healthcheck` |
| Networking | Network design for inter-service communication (bridge vs custom network) |
| Volumes | Choosing between persistent data volumes and bind mounts for hot reload |
| Environment variables | `.env` file management, `.env.example` template |
| Port management | Mapping externally exposed ports to container ports |

### 3. Dockerfile Design

Design multi-stage builds when needed:

#### Stage Design

| Stage | Purpose | Contents |
|-------|---------|---------|
| `base` | Common dependencies | Runtime, package manager |
| `deps` | Dependency installation | `node_modules` (production) |
| `dev-deps` | Development dependencies | Including devDependencies |
| `builder` | Build execution | TypeScript compile, asset build |
| `runner` | Production runtime | Minimal runtime + build artifacts |

#### Base Image Selection

| Criteria | Recommendation |
|---------|---------------|
| Security-focused | `node:{version}-alpine` |
| Compatibility-focused | `node:{version}-slim` |
| Developer convenience | `node:{version}-bookworm` |

### 4. Design Output

```markdown
## Local Development Infrastructure Design

### Service Configuration
| Service Name | Image | Role | Exposed Ports | Dependencies |
|-------------|-------|------|--------------|--------------|
| {service} | {image} | {role} | {ports} | {deps} |

### Volume Design
| Volume Name | Type | Purpose |
|------------|------|---------|
| {volume} | named/bind | {purpose} |

### Dockerfile Multi-Stage Design
{Stage configuration and the role of each stage}

### Port Assignments
| Service | Host Port | Container Port |
|---------|-----------|---------------|
| {service} | {host} | {container} |

### Environment Variable Design
{Configuration strategy for .env files}

### Key Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| {topic} | {content} | {reason} |
```

### 5. Review Checklist

- [ ] All services (production-grade) have `healthcheck` configured
- [ ] `depends_on` uses `condition: service_healthy`
- [ ] Ports do not conflict with other services
- [ ] Services requiring data persistence have named volumes configured
- [ ] An `.env.example` template exists
- [ ] Dockerfile pins specific versions (avoid `latest`)
- [ ] Multi-stage build minimizes the production image size

## Next Steps

When called via `design-flow`, control automatically returns to the orchestrator.

When invoked standalone:

```
Local development infrastructure design complete. Next steps:
-> Implement docker-compose with coding-infra skill
-> Use /design-flow for a full design workflow
```

## Notes

- **Do not generate implementation files** — Output design documents only. Implementation of docker-compose.yml etc. is `coding-infra`'s responsibility
- **Do not venture into AWS production design** — Delegate to `designing-aws` if local-to-production mapping is needed
- Port conflicts are common in local development environments. Always verify existing port assignments before designing
- The `version:` field in docker-compose is deprecated in v3.8+; prefer `compose-spec` compliance
