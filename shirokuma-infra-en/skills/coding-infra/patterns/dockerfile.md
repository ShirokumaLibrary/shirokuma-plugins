# Dockerfile Pattern Collection

> **Scope**: Build and deployment preparation. Covers Dockerfile authoring and .dockerignore configuration. Production deployment (orchestration, registry push, CI/CD pipelines) is out of scope.

## Next.js Standalone Output Multi-stage Build

Optimized for Next.js `output: "standalone"` configuration.

### next.config.ts

```typescript
const nextConfig = {
  output: "standalone",
};
export default nextConfig;
```

### Dockerfile

```dockerfile
# syntax=docker/dockerfile:1

# ---- Base ----
FROM node:20-alpine AS base
RUN corepack enable

# ---- Dependencies ----
FROM base AS deps
WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# ---- Builder ----
FROM base AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# ---- Runner ----
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

## Generic Node.js Application Pattern

For CLI tools, API servers, and other Node.js applications.

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine AS base
RUN corepack enable

FROM base AS deps
WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --prod

FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser

COPY --from=deps --chown=appuser:nodejs /app/node_modules ./node_modules
COPY --chown=appuser:nodejs . .

USER appuser

EXPOSE 8080
CMD ["node", "dist/index.js"]
```

## pnpm Cache Optimization

Use BuildKit cache mounts to speed up builds.

```dockerfile
# Mount pnpm store as cache (not included in image layer)
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile
```

| Option | Description |
|--------|-------------|
| `--mount=type=cache` | Persistent cache across builds |
| `id=pnpm` | Shared cache ID across stages |
| `target=...` | pnpm store path (auto-detected by pnpm) |
| `--frozen-lockfile` | Fail if lockfile is out of sync |

> **npm equivalent**: `--mount=type=cache,target=/root/.npm`

## Security Best Practices

### Non-root User

```dockerfile
# Create system group and user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser

# Apply ownership when copying files
COPY --chown=appuser:nodejs . .

# Switch to non-root user
USER appuser
```

> Always run containers as non-root. Compromised containers cannot write to the host system.

### .dockerignore

```gitignore
# Dependencies (rebuild in container)
node_modules

# Build output
.next
dist
build

# Local dev files
.env
.env.local
.env.*.local

# Version control
.git
.gitignore

# Editor settings
.vscode
.idea
*.swp

# Logs
*.log
npm-debug.log*

# Test files
__tests__
*.test.ts
*.spec.ts
coverage

# Documentation
*.md
docs

# Docker files (no need to copy into image)
Dockerfile*
docker-compose*
.dockerignore
```

## Image Size Optimization

### Multi-stage Build Strategy

| Stage | Purpose | Included in Final Image |
|-------|---------|------------------------|
| `base` | Common base image | No |
| `deps` | Install all dependencies | No |
| `builder` | Build application | No |
| `runner` | Production runtime | Yes |

Only the `runner` stage ends up in the final image. Build tools and dev dependencies are excluded.

### Alpine Images

```dockerfile
FROM node:20-alpine  # ~50MB vs ~330MB for debian
```

> **Note**: Some native modules (bcrypt, canvas) may not work on Alpine. Use `node:20-slim` if issues arise.

### Minimize Layer Count

```dockerfile
# Bad: Multiple RUN creates multiple layers
RUN apk add --no-cache curl
RUN apk add --no-cache git

# Good: Single RUN reduces to one layer
RUN apk add --no-cache curl git
```

## Build Arguments and Environment Variables

```dockerfile
# Build-time variable (not included in image by default)
ARG NEXT_PUBLIC_API_URL

# Runtime environment variable
ENV NODE_ENV=production

# Pass ARG to ENV (persisted in image)
ARG BUILD_VERSION
ENV APP_VERSION=$BUILD_VERSION
```

| Type | Syntax | Available at Build | Available at Runtime |
|------|--------|--------------------|---------------------|
| ARG | `ARG KEY=default` | Yes | No (unless copied to ENV) |
| ENV | `ENV KEY=value` | Yes | Yes |

> **Security**: Never pass secrets (API keys, passwords) as ARG or ENV. Use Docker secrets or runtime environment injection.

## Common Issues and Solutions

| Problem | Cause | Solution |
|---------|-------|---------|
| Large image size | `node_modules` copied from host | Always copy from `deps` stage, never from host |
| Build fails in CI | Cache miss | Use `--mount=type=cache` with consistent `id` |
| Permission denied in container | Running as root or wrong ownership | Add non-root user and `--chown` on COPY |
| `.env` file included in image | Missing `.dockerignore` | Always add `.env*` to `.dockerignore` |
| Native module build error | Alpine incompatibility | Switch to `node:20-slim` (Debian-based) |
