# Service Migration Patterns

Patterns for changing existing service configurations, such as image changes, container renames, and volume migrations.

## Image Migration (e.g., Redis → Valkey)

### Background

Redis 7+ changed its license (SSPLv1). For OSS projects, migrating to Valkey (BSD-3-Clause) is recommended. Valkey provides a Redis-compatible API, so no application code changes are needed.

### Steps

```bash
# 1. Stop existing container
docker compose stop {old-service}

# 2. Update image in docker-compose.yml
#    image: redis:7-alpine → image: valkey/valkey:8-alpine

# 3. Update container_name (optional)
#    container_name: {project}-redis → container_name: {project}-valkey

# 4. Start new service
docker compose up -d {new-service}

# 5. Remove old container
docker compose rm -f {old-service}
```

### docker-compose.yml Change Example

```yaml
# Before
redis:
  image: redis:7-alpine
  container_name: {project}-redis
  ports:
    - "${REDIS_PORT:-6379}:6379"
  volumes:
    - redis-data:/data

# After
valkey:
  image: valkey/valkey:8-alpine
  container_name: {project}-valkey
  ports:
    - "${VALKEY_PORT:-6379}:6379"
  volumes:
    - valkey-data:/data
```

### Related Files to Update

When a service name change is involved, check and update the following:

| File | Update |
|------|--------|
| `docker-compose.yml` | Service name, image, volume names |
| `.env` / `.env.example` | Environment variable keys (`REDIS_URL` → `VALKEY_URL`, etc.) |
| Other services with `depends_on` | Update dependency service names |
| App config files | Connection strings (when hostname is the service name) |
| `scripts/*.sh` | Startup scripts that reference service names |

## Container Name Change

When changing only the container name (image stays the same):

```bash
# Stop and remove old container
docker compose stop {old-name}
docker compose rm -f {old-name}

# After updating container_name in docker-compose.yml
docker compose up -d {service-key}
```

## Volume Migration

When renaming a volume while retaining data:

```bash
# 1. Copy data from source volume via temporary container
docker run --rm \
  -v {old-volume}:/source:ro \
  -v {new-volume}:/dest \
  alpine sh -c "cp -av /source/. /dest/"

# 2. Verify migration
docker run --rm -v {new-volume}:/data alpine ls /data

# 3. Update volume names in docker-compose.yml and start
docker compose up -d
```

## Rollback Procedure

If issues occur during migration:

```bash
# Stop new service
docker compose stop {new-service}

# Revert docker-compose.yml to old configuration
git checkout docker-compose.yml

# Restart old service
docker compose up -d {old-service}
```

## Checklist

Items to verify after migration:

- [ ] New service health check is passing
- [ ] Application connects successfully
- [ ] Old containers and volumes are cleaned up
- [ ] `.env.example` is updated
- [ ] Service list in README or CLAUDE.md is updated
