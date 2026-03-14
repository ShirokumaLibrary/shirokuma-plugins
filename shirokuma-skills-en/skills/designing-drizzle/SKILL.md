---
name: designing-drizzle
description: Designs data models using Drizzle ORM. Covers table design, relations, index strategy, migrations, and soft delete patterns. Triggers: "data model design", "table design", "schema design", "DB design", "migration design".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# Drizzle Data Model Design

Design Drizzle ORM data models with informed pattern selection. Focuses on design decisions and trade-off analysis; implementation is delegated to `code-issue`.

> **Data model design is this skill's responsibility.** `code-issue` handles implementation based on the schema decisions made here.

## Scope

- **Category:** Investigation Worker
- **Scope:** Reading tech stack and existing schema files (Read / Grep / Glob / Bash read-only commands), generating data model design documents (Write/Edit — for design artifact outputs), appending design sections to Issue bodies.
- **Out of scope:** Implementing production code or creating schema files (delegated to `code-issue`), running migrations, build verification

> **Design artifact writes**: When this skill uses Write/Edit on Issue bodies or design documents, it is producing design artifacts — not modifying production code. This is permitted as an exception for Investigation Workers.

## Workflow

### 0. Tech Stack Check

**First**, read project `CLAUDE.md` to confirm:
- Drizzle ORM version
- Database engine (PostgreSQL / MySQL / SQLite)
- Migration tool (drizzle-kit)
- Auth solution (Better Auth, NextAuth — session/user table constraints)
- Existing schema file structure (`src/db/schema/` etc.)

Also check `.claude/rules/` for `tech-stack.md`.

### 1. Design Context Check

When delegated from `designing-on-issue`, Design Brief and requirements are provided. Use them as-is.

When invoked standalone, gather requirements by reading the issue body and plan section.

### 2. Data Model Analysis

For each design concern relevant to the issue, apply the decision framework:

#### Design Concerns

| Concern | When to Address | Pattern Reference |
|---------|----------------|-------------------|
| Table Design | New entities, normalization level | [patterns/data-model-patterns.md](patterns/data-model-patterns.md) - Table Design |
| Relation Design | Entity relationships, join strategies | [patterns/data-model-patterns.md](patterns/data-model-patterns.md) - Relations |
| Index Strategy | Query performance, search conditions | [patterns/data-model-patterns.md](patterns/data-model-patterns.md) - Indexes |
| Soft Delete | Entities requiring logical deletion | [patterns/data-model-patterns.md](patterns/data-model-patterns.md) - Soft Delete |
| Migration | Schema changes, data migration | [patterns/data-model-patterns.md](patterns/data-model-patterns.md) - Migration |

#### Decision Framework

For each concern, evaluate:

1. **Requirements**: What data structure does the feature need?
2. **Constraints**: DB engine, existing schema, performance requirements
3. **Options**: List viable patterns (see data-model-patterns.md)
4. **Trade-offs**: Compare options with a decision matrix
5. **Decision**: Select pattern with rationale

### 3. Design Output

Produce data model design as a structured document:

```markdown
## Data Model Design

### Entity List
| Entity | Description | Key Columns |
|--------|-------------|-------------|
| {name} | {purpose} | {key columns} |

### Table Definitions
{Drizzle schema definitions for each table (types, constraints, defaults)}

### Relations
{Relation definitions between entities and join strategies}

### Indexes
{Index definitions required for performance with rationale}

### Migration Strategy
{Schema change application order and data migration procedures}

### Key Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| {topic} | {pattern} | {why} |
```

### 4. Review Checklist

- [ ] Table names are snake_case and plural
- [ ] Primary keys are appropriate (UUID vs serial)
- [ ] Foreign key constraints and ON DELETE behavior are explicit
- [ ] Indexes match query patterns
- [ ] Tables requiring soft delete have `deletedAt` column
- [ ] Migrations are backward-compatible (when needed)
- [ ] Design aligns with existing schema patterns

## Reference Documents

| Document | Content | When to Read |
|----------|---------|-------------|
| [patterns/data-model-patterns.md](patterns/data-model-patterns.md) | Pattern comparison tables | Data model decisions |
| `tech-stack.md` (rule) | Recommended tech stack | Tech selection |
| Existing `src/db/schema/` | Project's existing schema | Pattern consistency check |

## Anti-Patterns

| Pattern | Problem | Alternative |
|---------|---------|------------|
| Over-normalization | Too many JOINs degrade performance | Consider denormalization for read-heavy data |
| Unindexed foreign keys | Slow join queries | Add indexes on foreign key columns |
| Soft delete on all tables | Query complexity, missed WHERE conditions | Apply only where needed |
| String-typed status columns | No type safety, typo risk | Use Drizzle enum types |
| Data changes in migrations | Hard to rollback | Separate schema changes from data migration |

## Next Steps

When invoked via `designing-on-issue`, control returns automatically to the orchestrator.

When invoked standalone:

```
Data model design complete. Next steps:
-> /commit-issue to stage and commit your changes
-> Use /designing-on-issue for the full design workflow
```

## Notes

- **Design decisions are this skill's priority** -- implementation details are `code-issue`'s responsibility
- **Build verification is not needed** -- this skill produces design documents, not runnable code
- When Design Brief is provided, design based on it. When standalone, gather requirements from the issue before designing
- Always check DB engine-specific constraints (PostgreSQL array types, SQLite ALTER TABLE limitations, etc.)
