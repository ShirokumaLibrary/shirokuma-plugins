---
name: designing-generic
description: Performs framework-agnostic architecture design. Covers module composition, interface design, migration design, and build pipeline design for CLI tools, libraries, and general TypeScript projects. Triggers: "CLI design", "module design", "interface design", "migration design", "architecture design", "generic design".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

!`shirokuma-docs rules inject --scope design-worker`


# Generic Architecture Design

Framework-agnostic architecture design. Focuses on design decisions and trade-off analysis; implementation is delegated to `code-issue`.

> **Architecture design is this skill's responsibility.** `code-issue` handles implementation based on the design decisions made here.

## Scope

- **Category:** Investigation Worker
- **Scope:** Reading tech stack and existing code structure (Read / Grep / Glob / Bash read-only commands), generating architecture design documents (Write/Edit — for design artifact outputs), appending design sections to Issue bodies
- **Target domains:** CLI tools, libraries, general TypeScript / Node.js projects
- **Out of scope:** Implementing production code (delegated to `code-issue`), build verification, framework-specific design (Next.js → `designing-nextjs`, data models → `designing-drizzle`, UI → `designing-shadcn-ui`)

> **Design artifact writes**: When this skill uses Write/Edit on Issue bodies or design documents, it is producing design artifacts — not modifying production code. This is permitted as an exception for Investigation Workers.

## Workflow

### 0. Tech Stack Check

**First**, read project `CLAUDE.md` to confirm:
- Language/runtime (Node.js, Deno, etc.) and version
- Package manager (npm / pnpm / yarn)
- Build tools (TypeScript compiler, esbuild, rollup, etc.)
- Existing directory structure and module organization strategy
- Test framework (Jest, Vitest, etc.)

Also check `.claude/rules/` for `tech-stack.md`.

### 1. Design Context Check

When delegated from `design-flow`, Design Brief and requirements are provided. Use them as-is.

When invoked standalone, gather requirements by reading the issue body and plan section.

### 2. Architecture Analysis

For each design concern relevant to the issue, apply the decision framework:

#### Design Concerns

| Concern | When to Address | Key Considerations |
|---------|----------------|--------------------|
| Module Composition | Adding modules, splitting responsibilities | Single responsibility, dependency direction, public interface |
| Interface Design | Type definitions at module boundaries | Type safety, extensibility, backward compatibility |
| Dependency Management | Inter-module dependencies, circular dependencies | Dependency injection, factory pattern |
| Command Pattern | CLI command additions/changes | Command splitting, option design, error handling |
| Migration Design | Refactoring existing code, API changes | Incremental migration, backward compatibility, deprecation strategy |
| Build Pipeline | Build, bundling, output formats | ESM/CJS support, type definition output, tree shaking |

#### Decision Framework

For each concern, evaluate:

1. **Requirements**: Organize functional and non-functional requirements
2. **Constraints**: Existing code structure, Node.js version, dependent libraries
3. **Options**: List viable architectural patterns
4. **Trade-offs**: Compare options with a decision matrix
5. **Decision**: Select architecture with rationale

#### Common Patterns

| Pattern | When to Apply |
|---------|--------------|
| Command Pattern | CLI command encapsulation, undo support |
| Factory Pattern | Abstracting object creation, improving testability |
| Repository Pattern | Abstracting data access, swappable storage |
| Strategy Pattern | Switching algorithms/behaviors |
| Composite Pattern | Tree structures, recursive processing |
| Plugin Pattern | Extension points, dynamic loading |
| Dependency Injection | Testability, loose coupling between modules |

### 3. Design Output

Produce architecture design as a structured document:

```markdown
## Architecture Design

### Overview
{Summary of the change purpose and impact scope}

### Module Composition
{Directory structure or module dependency graph}

### Interface Definitions
{Key type definitions and interfaces (TypeScript format)}

### Migration Plan
{Migration steps from existing code (organized by phase)}
(Omit for new designs)

### Build/Distribution Impact
{Changes to package.json, output format changes, etc.}
(Omit if no impact)

### Key Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| {topic} | {pattern} | {why} |
```

### 4. Review Checklist

- [ ] Single responsibility — each module has a clear responsibility
- [ ] Dependency direction is one-way (no circular dependencies)
- [ ] Public interfaces are minimal (implementation details hidden)
- [ ] Type definitions are type-safe (avoid `any`)
- [ ] Impact on existing tests has been assessed
- [ ] Migration is incremental (backward compatible, or deprecation strategy is clear)
- [ ] Aligns with existing code patterns and naming conventions

## Reference Documents

| Document | Content | When to Read |
|----------|---------|-------------|
| `CLAUDE.md` | Project overview, tech stack | At design start |
| `tech-stack.md` (rule) | Recommended tech stack | Tech selection |
| Existing `src/` | Current code structure | Pattern consistency check |

## Anti-Patterns

| Pattern | Problem | Alternative |
|---------|---------|------------|
| God Class | Too many responsibilities, hard to change | Split following single responsibility principle |
| Circular Dependencies | Difficult to build, test, and understand | Organize dependencies one-way, extract shared interfaces |
| Over-abstraction | Excessive indirection hurts readability | YAGNI principle — don't abstract until actually needed |
| Giant Functions | Hard to test and change | Split into small pure functions |
| Hidden Dependencies | Hard to test, side effects invisible | Pass dependencies explicitly via arguments or DI |
| Big Bang Migration | High risk, partial rollback is difficult | Incremental migration, Strangler Fig pattern |

## Next Steps

When invoked via `design-flow`, control returns automatically to the orchestrator.

When invoked standalone:

```
Architecture design complete. Next steps:
-> /commit-issue to stage and commit your changes
-> Use /design-flow for the full design workflow
```

## Notes

- **Design decisions are this skill's priority** -- implementation details are `code-issue`'s responsibility
- **Build verification is not needed** -- this skill produces design documents, not runnable code
- When Design Brief is provided, design based on it. When standalone, gather requirements from the issue before designing
- For framework-specific design (Next.js, Drizzle, shadcn/ui), delegate to the dedicated skill
