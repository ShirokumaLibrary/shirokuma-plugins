---
name: designing-nextjs
description: Designs Next.js application architecture including routing, component hierarchy, Server Actions, API Routes, and middleware. Triggers: "architecture design", "routing design", "component structure", "API design", "middleware design".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

!`shirokuma-docs rules inject --scope design-worker`


# Next.js Architecture Design

Design Next.js application architecture with informed pattern selection. Focuses on design decisions and trade-off analysis; implementation is delegated to `coding-nextjs`.

> **Architecture design is this skill's responsibility.** `coding-nextjs` handles implementation based on the architecture decisions made here.

## Scope

- **Category:** Investigation Worker
- **Scope:** Reading tech stack and project structure (Read / Grep / Glob / Bash read-only commands), generating architecture design documents (Write/Edit — for design artifact outputs), appending design sections to Issue bodies.
- **Out of scope:** Implementing production code (delegated to `coding-nextjs`), build verification

> **Design artifact writes**: When this skill uses Write/Edit on Issue bodies or design documents, it is producing design artifacts — not modifying production code. This is permitted as an exception for Investigation Workers.

## Workflow

### 0. Tech Stack Check

**First**, read project `CLAUDE.md` to confirm:
- Next.js version (App Router / Pages Router)
- React version (Server Components support)
- TypeScript configuration
- Styling approach (Tailwind v3/v4, CSS Modules)
- Database / ORM (Drizzle, Prisma)
- Auth solution (Better Auth, NextAuth)
- i18n setup (next-intl, messages structure)

Also check `.claude/rules/` for `tech-stack.md` and `known-issues.md`.

### 1. Design Context Check

When delegated from `design-flow`, Design Brief and requirements are provided. Use them as-is.

When invoked standalone, gather requirements by reading the issue body and plan section.

### 2. Architecture Analysis

For each design concern relevant to the issue, apply the decision framework:

#### Design Concerns

| Concern | When to Address | Pattern Reference |
|---------|----------------|-------------------|
| Routing | New pages, route groups, layouts | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - Routing |
| Component Hierarchy | New features, page structure | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - Component Hierarchy |
| Server Actions / API Routes | Data mutations, external API integration | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - Data Layer |
| Middleware | Auth, redirects, headers, i18n | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - Middleware |
| Data Flow | State management, caching | [patterns/architecture-patterns.md](patterns/architecture-patterns.md) - Data Flow |

#### Decision Framework

For each concern, evaluate:

1. **Requirements**: What does the feature need?
2. **Constraints**: Framework version, existing patterns, performance budget
3. **Options**: List viable patterns (see architecture-patterns.md)
4. **Trade-offs**: Compare options with a decision matrix
5. **Decision**: Select pattern with rationale

### 3. Design Output

Produce architecture design as a structured document:

```markdown
## Architecture Design

### Routing Structure
{Route tree with layout boundaries}

### Component Hierarchy
{Component tree with Server/Client boundary markers}

### Data Layer
{Server Actions / API Routes with responsibility assignment}

### Middleware Chain
{Middleware layers with execution order}

### Key Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| {topic} | {pattern} | {why} |
```

### 4. Review Checklist

- [ ] Routing structure follows App Router conventions
- [ ] Server/Client component boundary is intentional
- [ ] Server Actions handle auth, CSRF, validation
- [ ] Middleware layers are ordered correctly
- [ ] No known-issues.md violations
- [ ] Design aligns with existing project patterns

## Reference Documents

| Document | Content | When to Read |
|----------|---------|-------------|
| [patterns/architecture-patterns.md](patterns/architecture-patterns.md) | Pattern comparison tables | Architecture decisions |
| `tech-stack.md` (rule) | Recommended tech stack | Tech selection |
| `known-issues.md` (rule) | Framework-specific issues | Constraint check |
| `coding-nextjs` patterns | Implementation patterns | Verifying implementability |

## Anti-Patterns

| Pattern | Problem | Alternative |
|---------|---------|------------|
| Client Component for static content | Unnecessary bundle size | Use Server Component |
| API Route for same-origin mutations | Extra network hop | Use Server Actions |
| Middleware for per-page logic | Middleware runs on all routes | Use layout/page-level checks |
| Deeply nested route groups | Hard to reason about layouts | Flatten with shared layouts |
| Prop drilling through 3+ levels | Tight coupling | Use composition or context |

## Next Steps

When invoked via `design-flow`, control returns automatically to the orchestrator.

When invoked standalone:

```
Architecture design complete. Next steps:
-> /commit-issue to stage and commit your changes
-> Use /design-flow for the full design workflow
```

## Notes

- **Design decisions are this skill's priority** -- implementation details are `coding-nextjs`'s responsibility
- **Build verification is not needed** -- this skill produces design documents, not runnable code
- When Design Brief is provided, design based on it. When standalone, gather requirements from the issue before designing
- Always check `known-issues.md` for framework version constraints
