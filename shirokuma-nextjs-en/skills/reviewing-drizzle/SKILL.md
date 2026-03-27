---
name: reviewing-drizzle
description: Reviews Drizzle ORM code. Covers schema design, query quality, migration safety, N+1 problems, and index strategy. Triggers: "Drizzle review", "schema review", "query review", "ORM review", "drizzle review", "migration review".
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# Drizzle ORM Code Review

Review Drizzle ORM schema design, query patterns, and migration safety. Focus on performance issues (N+1) and data integrity risks.

## Scope

- **Category:** Investigation Worker
- **Scope:** Code reading (Read / Grep / Glob / Bash read-only), generating review reports. No code modifications or migration execution.
- **Out of scope:** Schema implementation (delegate to `coding-nextjs` / `code-issue`), running migrations

## Review Criteria

### Schema Design

| Check | Issue | Fix |
|-------|-------|-----|
| Primary key design | Using `serial` / `int` primary keys in new tables | Prefer UUID / CUID2 |
| Foreign key constraints | Undefined `references()` | Ensure referential integrity |
| Nullability | Required fields marked as `nullable()` | Align with business rules |
| Indexes | No indexes on search/join keys | Add `index()` |
| Soft delete | Type of `deletedAt` field | Verify `timestamp` + `default(null)` pattern |
| Timestamps | No `$onUpdate` for `updatedAt` | Set to auto-update on change |
| Naming conventions | Inconsistent table/column names | Maintain snake_case |

### Query Quality

| Check | Issue | Fix |
|-------|-------|-----|
| N+1 problem | Individual queries inside loops | Use `with` for batch relation loading |
| SELECT * | Fetching all columns | Specify only required columns |
| Filtering | Filtering on application side | Move to WHERE clause |
| Pagination | List queries without `limit` | Enforce `limit` + `offset` / cursor |
| Transactions | Multi-table writes outside transactions | Wrap with `db.transaction()` |
| Prepared statements | Rebuilding same query repeatedly | Optimize with `db.$with` / `prepare()` |

### Migration Safety

| Check | Issue | Fix |
|-------|-------|-----|
| Adding NOT NULL | Adding NOT NULL to existing data columns | Set default value or use staged migration |
| Column deletion | Deleting referenced columns | Remove references first |
| Column renaming | Direct rename | 3-step: add → copy → delete |
| Adding indexes | Synchronous index addition to large tables | Use `CONCURRENTLY` (PostgreSQL) |
| Adding foreign keys | Not verifying existing data integrity | Verify data integrity first |
| Migration idempotency | Cannot re-run after failure | Proper rollback plan |

### Security

| Check | Issue | Fix |
|-------|-------|-----|
| SQL injection | Building queries with string concatenation | Use Drizzle's type-safe queries |
| Missing permission check | No owner verification before queries | Enforce `WHERE userId = sessionUserId` |
| Secret exposure | DB URL hardcoded in code | Manage with env variables + `.env.local` |

### Better Auth Integration

| Check | Issue | Fix |
|-------|-------|-----|
| Session table | `session.userId` foreign key | Verify it references `users.id` |
| Custom fields | Extending Better Auth schema | Use `auth.onSession()` / `auth.onUser()` hooks |
| `users` table | Directly modifying Better Auth-managed tables | Use Better Auth API |

## Workflow

### 1. Identify Target Files

```bash
# Check schema files
find src -path "*/db/schema*" -name "*.ts" | head -20
find src -path "*/schema*" -name "*.ts" | head -20

# Check migration files
find . -name "*.sql" -path "*/migrations/*" | sort | tail -10

# Check query files
grep -r "from 'drizzle-orm'" --include="*.ts" -l | head -20
```

### 2. Run Lints

```bash
shirokuma-docs lint code -p . -f terminal
```

### 3. Code Analysis

Read schema and query files and apply the review criteria tables.

Priority check order:
1. Migration safety (risk of data loss)
2. Security (permission checks / SQL injection)
3. N+1 query problems
4. Schema design consistency

### 4. Generate Report

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
{List migration safety / security issues}

### Improvements
{List query optimization / schema improvement suggestions}
```

### 5. Save Report

When PR context is present:
```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/review-drizzle.md
```

When no PR context:
```bash
shirokuma-docs discussions create \
  --category Reports \
  --title "[Review] drizzle: {target}" \
  --body-file /tmp/shirokuma-docs/review-drizzle.md
```

## Review Verdict

- **PASS**: `**Review result:** PASS` — No critical issues
- **FAIL**: `**Review result:** FAIL` — Critical/High issues found (including migration safety / risk of data loss)

## Notes

- **Treat migration changes as Critical** — Data loss is irreversible
- **Do not modify code** — Report findings only
- Drizzle API differs by version. Check version in `package.json`
