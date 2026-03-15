# Data Model Patterns

Pattern comparison tables for Drizzle ORM data model design decisions.

## Table Design

### Primary Key Strategy

| Pattern | When to Use | Trade-offs |
|---------|------------|------------|
| UUID (`uuid().defaultRandom()`) | Distributed systems, public IDs | Random, lower index efficiency |
| CUID2 (`text().$default(createId)`) | URL-safe public IDs | Shorter than UUID, not a native DB type |
| Serial (`serial()`) | Internal IDs, small tables | Predictable, not suitable for distributed |
| UUID v7 (`uuid().$default(uuidv7)`) | Time-sorted + uniqueness | Latest standard, requires additional library |

### Decision: UUID vs Serial

| Criterion | UUID | Serial |
|-----------|------|--------|
| ID exposed in public API | Recommended | Security risk |
| Sorting by insertion order | Use UUID v7 | Natural ordering |
| Foreign key join cost | Slightly higher (16 bytes) | Lower (4 bytes) |
| Multi-tenant / distributed | Recommended | Collision risk |
| Simple admin tables | Overhead | Recommended |

### Common Column Patterns

| Pattern | Columns | Purpose |
|---------|---------|---------|
| Timestamps | `createdAt`, `updatedAt` | Audit trail |
| Soft delete | `deletedAt` | Logical deletion |
| Versioning | `version` | Optimistic locking |
| Tenant isolation | `tenantId` | Multi-tenancy |
| Creator tracking | `createdBy`, `updatedBy` | Operation attribution |

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Table names | snake_case, plural | `users`, `blog_posts` |
| Column names | camelCase (Drizzle standard) | `createdAt`, `userId` |
| Foreign keys | `{entity}Id` | `userId`, `postId` |
| Junction tables | `{entity1}_to_{entity2}` | `users_to_roles` |
| Indexes | `{table}_{columns}_idx` | `posts_author_id_idx` |
| Unique constraints | `{table}_{columns}_unique` | `users_email_unique` |

## Relation Design

### Relation Types

| Pattern | Drizzle Definition | When to Use |
|---------|-------------------|------------|
| One-to-One | `one(target, { fields, references })` | User ↔ Profile |
| One-to-Many | `one()` + `many()` | Author → Posts |
| Many-to-Many | Junction table + `many()` x2 | Users ↔ Roles |
| Self-referential | `one()` to same table | Category parent-child |

### ON DELETE Strategy

| Behavior | When to Use | Risk |
|----------|------------|------|
| `CASCADE` | Children always share parent lifecycle | Unintended mass deletion |
| `SET NULL` | Data should survive reference deletion | NULL checks needed |
| `RESTRICT` | Prevent deletion when children exist | Operation errors |
| `NO ACTION` | Application-level control | Orphaned records risk |

### Decision: CASCADE vs SET NULL vs RESTRICT

| Criterion | CASCADE | SET NULL | RESTRICT |
|-----------|---------|----------|----------|
| Comments → Post (on post delete) | Recommended | — | — |
| Orders → User (on user delete) | Dangerous | Recommended | Recommended |
| Profile → User (1:1) | Recommended | — | — |
| Tagging → Tag (on tag delete) | Recommended | — | — |
| Invoices → Customer (legal retention) | Prohibited | Recommended | Recommended |

### Query Join Patterns

| Pattern | When to Use | Drizzle API |
|---------|------------|------------|
| Relational queries | Nested results needed | `db.query.users.findMany({ with: { posts: true } })` |
| SQL joins | Aggregation, complex conditions | `db.select().from(users).leftJoin(posts, eq(...))` |
| Subqueries | EXISTS / NOT EXISTS checks | `db.select().from(users).where(exists(...))` |

## Index Strategy

### Index Types

| Type | When to Use | Drizzle Definition |
|------|------------|-------------------|
| Single column | Equality lookup, foreign keys | `index('idx_name').on(table.column)` |
| Composite | Multi-condition WHERE | `index('idx_name').on(table.col1, table.col2)` |
| Unique | Uniqueness constraint | `uniqueIndex('idx_name').on(table.column)` |
| Partial | Conditional index (PostgreSQL) | `index('idx_name').on(table.column).where(sql`...`)` |

### Index Design Rules

| Rule | Description |
|------|-------------|
| Always index foreign keys | Basic JOIN performance |
| Index frequently used WHERE columns | Match search conditions |
| Composite: high selectivity first | Put highest-cardinality column first |
| Consider covering indexes | Include SELECT targets (read optimization) |
| Be conservative on write-heavy tables | INSERT/UPDATE overhead |

### Decision: When to Add an Index

| Criterion | Add Index | Skip Index |
|-----------|-----------|-----------|
| Foreign key column | Always | — |
| Frequent WHERE clause usage | Recommended | — |
| Table rows < 1000 | — | Full scan is sufficient |
| Writes > reads | Carefully | Avoid excessive indexes |
| LIKE '%keyword%' | — | B-Tree ineffective (consider full-text search) |

## Soft Delete

### Implementation Patterns

| Pattern | Column | Pros | Cons |
|---------|--------|------|------|
| Nullable timestamp | `deletedAt: timestamp()` | Records deletion time | NULL check required |
| Boolean flag | `isDeleted: boolean().default(false)` | Simple | No deletion timestamp |
| Status enum | `status: statusEnum()` | Multiple states | Complex |

### Recommended: Nullable Timestamp

```
deletedAt: timestamp('deleted_at', { mode: 'date' })
```

- `NULL` = active, non-NULL = deleted
- Deletion timestamp useful for audit trail
- Can be combined with partial indexes (PostgreSQL)

### Soft Delete Applicability

| Criterion | Soft Delete | Hard Delete |
|-----------|------------|------------|
| Legal data retention requirements | Recommended | Prohibited |
| User can restore from trash | Recommended | — |
| Audit trail needed | Recommended | — |
| Temporary data (sessions, etc.) | — | Recommended |
| Storage cost concerns | — | Recommended |
| Referenced by foreign keys | Recommended | CASCADE needed |

### Query Patterns

| Operation | Query |
|-----------|-------|
| Get active records | `.where(isNull(table.deletedAt))` |
| Get all including deleted | No filter |
| Soft delete | `.set({ deletedAt: new Date() })` |
| Restore | `.set({ deletedAt: null })` |
| Permanent delete | `.delete().where(isNotNull(table.deletedAt))` |

## Migration Strategy

### drizzle-kit Workflow

| Command | Purpose | When |
|---------|---------|------|
| `drizzle-kit generate` | Generate SQL migration files | After schema changes |
| `drizzle-kit migrate` | Apply migrations | At deploy time |
| `drizzle-kit push` | Apply schema directly to DB | Development only |
| `drizzle-kit studio` | Launch DB browser | Debugging |

### Migration Classification

| Type | Example | Risk | Mitigation |
|------|---------|------|------------|
| Additive | Add column, add table | Low | Set default values |
| Alterative | Change column type, rename | Medium | Consider downtime |
| Destructive | Drop column, drop table | High | Implement gradually (deprecate → drop) |
| Data | Transform existing data | High | Separate from schema changes |

### Safe Migration Procedure

1. **Additive changes first**: Add new columns/tables (with default values)
2. **Update application code**: Modify to use the new schema
3. **Data migration**: Convert existing data as needed
4. **Destructive changes last**: Drop old columns/tables

### Decision: push vs generate+migrate

| Criterion | `push` (dev) | `generate` + `migrate` (production) |
|-----------|-------------|-------------------------------------|
| Local development | Recommended (fast) | Overhead |
| Staging / production | Prohibited | Recommended |
| Team development | Risky | Recommended (history tracking) |
| Data preservation needed | Risky | Recommended |
