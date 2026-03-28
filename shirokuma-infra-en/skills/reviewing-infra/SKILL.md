---
name: reviewing-infra
description: Reviews local development infrastructure code. Covers Dockerfile best practices, docker-compose design, LocalStack configuration, and security. Triggers: "Dockerfile review", "docker-compose review", "local environment review", "infra review", "container review", "LocalStack review".
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# Local Development Infrastructure Code Review

Review Dockerfile, docker-compose.yml, and LocalStack configuration. Focus on image size, build cache efficiency, security, and local-to-production consistency.

## Scope

- **Category:** Investigation Worker
- **Scope:** Infrastructure file reading (Read / Grep / Glob / Bash read-only), generating review reports. No code modifications.
- **Out of scope:** Code modifications (delegate to `coding-infra`), building or running Docker images

## Review Criteria

### Dockerfile

| Check | Issue | Fix |
|-------|-------|-----|
| Base image | Using `latest` tag | Use pinned version tag (e.g., `node:20-alpine3.19`) |
| Multi-stage build | Single stage including all dependencies | Separate dev / build / production stages |
| Layer caching | `COPY . .` placed at the top | Order: `package.json` → `npm install` → source code |
| Running as root | No USER set (runs as root) | Set non-root user like `USER node` |
| Unnecessary COPY | No `.dockerignore` or incomplete | Exclude `node_modules`, `.git`, `dist` |
| Secrets | Passing secrets via `ARG SECRET_KEY` | Use `--secret` flag / BuildKit secret |
| `apt-get` cleanup | Missing cache deletion | Add `&& rm -rf /var/lib/apt/lists/*` |
| EXPOSE | No EXPOSE for service port | Add EXPOSE for documentation purposes |

### docker-compose.yml

| Check | Issue | Fix |
|-------|-------|-----|
| version field | Old `version: "3"` | Optional in v1.29+ (Compose Spec compliant) |
| Health checks | No `healthcheck` | Add `healthcheck` to dependent services |
| `depends_on` | No condition | Use `condition: service_healthy` |
| Env var management | Hardcoded environment variables | Use `.env` files with `env_file` |
| Volume naming | Anonymous volumes | Use named volumes for management |
| Network isolation | Default network only | Define purpose-specific networks (frontend / backend) |
| Port binding | `0.0.0.0:5432:5432` | Use `127.0.0.1:5432:5432` for local-only access |
| Restart policy | `restart: always` | Prefer `restart: unless-stopped` for development |

### LocalStack Configuration

| Check | Issue | Fix |
|-------|-------|-----|
| Endpoint hardcoding | `http://localhost:4566` hardcoded in code | Switch via `LOCALSTACK_ENDPOINT` env var |
| Service activation | No `SERVICES` env var | List only required services (faster startup) |
| Data persistence | LocalStack data resets every time | Set `PERSISTENCE=1` or use named volume |
| `localstack/localstack` image | Using Pro image without needing Pro features | Check if `localstack/localstack:latest` is sufficient |
| Profile isolation | LocalStack and production AWS configs mixed | Separate with `AWS_PROFILE` or `AWS_DEFAULT_REGION` |

### Security

| Check | Issue | Fix |
|-------|-------|-----|
| `.env` committed | `.env` file not in `.gitignore` | Add to `.gitignore` and provide `.env.example` |
| Default passwords | Using `POSTGRES_PASSWORD=password` etc. | Manage random values in `.env` |
| Privileged container | Using `privileged: true` | Grant only required capabilities |

## Workflow

### 1. Identify Target Files

```bash
# Check Dockerfiles
find . -name "Dockerfile*" | head -10

# Check docker-compose files
find . -name "docker-compose*.yml" -o -name "docker-compose*.yaml" | head -10

# Check .dockerignore
find . -name ".dockerignore" | head -5

# Check .env files
find . -name ".env*" -not -name "*.example" | head -10
```

### 2. Code Analysis

Read infrastructure files and apply the review criteria tables.

Priority check order:
1. Security (secret leakage / root execution)
2. Dockerfile best practices (build cache / multi-stage)
3. docker-compose health design (health checks / dependencies)
4. LocalStack configuration appropriateness

### 3. Generate Report

```markdown
## Review Summary

### Issue Summary
| Severity | Count |
|----------|-------|
| Critical | {n} |
| High | {n} |
| Medium | {n} |
| Low | {n} |
| **Total** | **{n}** |

### Critical Issues
{List security / root execution issues}

### Improvements
{List Dockerfile optimization / docker-compose improvement suggestions}
```

### 4. Save Report

When PR context is present:
```bash
shirokuma-docs items add comment {PR#} --file /tmp/shirokuma-docs/review-infra.md
```

When no PR context:
```bash
# Set title: "[Review] infra: {target}" and category: Reports in frontmatter first
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/review-infra.md
```

## Review Verdict

- **PASS**: `**Review result:** PASS` — No critical issues
- **FAIL**: `**Review result:** FAIL` — Critical/High issues found (secret leakage / root execution, etc.)

## Notes

- **Do not modify code** — Report findings only
- Local development infrastructure should align with production. Also flag deviations from the `designing-aws` design
