# Code Review Role

## Responsibilities

Comprehensive code quality review covering:
- TypeScript best practices
- Error handling patterns
- Async operations
- Code structure and organization
- Naming conventions
- Code smells detection

## Required Knowledge

Load these files for context:

**Skill files (explicit load):**
- `../criteria/code-quality.md` - Quality criteria
- `../criteria/coding-conventions.md` - Coding conventions (naming, imports, structure)
- `../patterns/server-actions.md` - Server Action patterns
- `../patterns/drizzle-orm.md` - Database patterns
- `../patterns/jsdoc.md` - JSDoc documentation patterns

**Rules (auto-loaded from `.claude/rules/`):**
- `tech-stack.md` - Version information
- `lib-structure.md` - lib/ directory structure rules
- `known-issues.md` - Known issues

## Review Checklist

### TypeScript
- [ ] No `any` types (use `unknown`)
- [ ] Explicit return types on public APIs
- [ ] Type guards for runtime checks
- [ ] Strict mode compliance

### Error Handling
- [ ] No empty catch blocks
- [ ] Error context included
- [ ] Appropriate error types
- [ ] No internal error exposure

### Async Patterns
- [ ] `Promise.all()` for parallel ops
- [ ] Proper rejection handling
- [ ] No mixed async patterns

### Code Style
- [ ] Small, focused functions
- [ ] Max 3 nesting levels
- [ ] Descriptive naming
- [ ] Consistent conventions

### Code Smells
- [ ] No God objects
- [ ] No magic numbers
- [ ] No dead code
- [ ] No duplicate code
- [ ] Short parameter lists

### Coding Conventions
- [ ] File names use kebab-case
- [ ] Variables/functions use camelCase
- [ ] Components use PascalCase
- [ ] Constants use UPPER_SNAKE_CASE
- [ ] Imports organized (framework → npm → monorepo → local → relative)
- [ ] Booleans have `is`/`has`/`can` prefix
- [ ] Unused variables prefixed with `_`
- [ ] Max 3 levels of nesting
- [ ] Server Actions follow structure (auth → validate → try/catch)

### lib/ Directory Structure
- [ ] No files directly under `lib/` (directories only)
- [ ] Each directory has `index.ts` for re-exports
- [ ] External imports use `@/lib/{module}` (not direct file paths)
- [ ] `__tests__/` directory exists for testable modules
- [ ] `@module` and `@feature` tags present

See: `patterns/lib-structure.md` for detailed rules

### Documentation Quality
- [ ] Public functions have JSDoc comments
- [ ] All `@param` tags present and descriptive
- [ ] All `@returns` tags present
- [ ] Complex functions have `@example`
- [ ] Functions have `@category` for TypeDoc
- [ ] Related functions linked with `@see`
- [ ] Error cases documented with `@throws`
- [ ] Internal functions marked with `@internal`
- [ ] Types/interfaces have property comments

### Annotation Consistency (shirokuma-docs)
- [ ] `@usedComponents` matches actual imports
- [ ] `@usedActions` matches actual function calls
- [ ] `@dbTables` matches actual Drizzle queries
- [ ] `@route` matches actual file path
- [ ] `@usedInScreen` bidirectionally consistent
- [ ] No typos in component/action names

See: `workflows/annotation-consistency.md` for detailed verification

## Anti-patterns to Detect

Check for the following violations during review:

### TypeScript Anti-patterns
- [ ] Using `any` type (should use `unknown`)
- [ ] Type assertions (`as`) without justification
- [ ] Implicit `any` allowed

### Error Handling Anti-patterns
- [ ] Empty catch blocks
- [ ] Swallowing errors (no handling in catch)
- [ ] Exposing internal error details to users
- [ ] Only using console.log/error for error handling

### Async Anti-patterns
- [ ] Sequential `await` when parallelizable
- [ ] Unhandled Promise rejections
- [ ] Mixing `.then()` with `async/await`

### Code Style Anti-patterns
- [ ] God objects (classes/modules with too many responsibilities)
- [ ] Magic numbers (unexplained numeric literals)
- [ ] Dead code (unused functions/variables/imports)
- [ ] Duplicate code (same logic in multiple places)
- [ ] Long parameter lists (4+ parameters)
- [ ] Deep nesting (4+ levels)

### lib/ Structure Anti-patterns
- [ ] Files directly under `lib/` (e.g., `lib/utils.ts`)
- [ ] Missing `index.ts` in lib subdirectories
- [ ] Direct file imports (e.g., `from "@/lib/auth/config"`)
- [ ] Logic in `index.ts` (should only re-export)
- [ ] Missing `__tests__/` for modules with testable logic
- [ ] Deep nesting in lib (more than 2 levels)

### Documentation Anti-patterns
- [ ] Missing JSDoc on public APIs
- [ ] Outdated JSDoc not matching implementation
- [ ] Commented-out code remaining

### Annotation Anti-patterns (shirokuma-docs)
- [ ] `@usedComponents` missing imported components
- [ ] `@usedComponents` listing unused components
- [ ] `@usedActions` not matching actual calls
- [ ] `@dbTables` missing accessed tables
- [ ] Stale `@usedInScreen` references
- [ ] Typos in annotation values (e.g., `SideBarGroup` vs `SidebarGroup`)

### Server Action Anti-patterns (Next.js)
- [ ] Processing before auth check
- [ ] Skipping CSRF validation
- [ ] Using data before Zod validation
- [ ] Including sensitive data in response

### Test Anti-patterns
- [ ] Tests written after implementation (TDD violation)
- [ ] Tests commented out or skipped
- [ ] Over-mocking (not testing real code)
- [ ] Testing implementation details (should test behavior)

## Report Format

Use template from `templates/report.md`:

1. **Summary**: Brief overview of findings
2. **Critical Issues**: Must fix before merge
3. **Anti-patterns Detected**: "Don't" rule violations
4. **Improvements**: Recommended changes
5. **Code Smells**: Detected anti-patterns
6. **Coding Conventions**: Naming, imports, structure violations
7. **Documentation Issues**: Missing or incomplete JSDoc
8. **Best Practices**: Patterns to follow

## GitHub Document Review Perspectives

Perspectives applied when reviewing PR artifacts (Discussion / Issue). Used only in the artifact review substep (see `review-issue/SKILL.md`).

### Review Checklist

#### Format Compliance
- [ ] For Discussions: does the format match the category? (ADR → ADR format, Knowledge → Knowledge format)
- [ ] For Issues: are required sections present? (`## Purpose`, `## Summary`, `## Background`, `## Deliverable`)
- [ ] Is the title format correct? (ADR: `ADR-{NNN}: {title}`, Knowledge: topic name, Research: `[Research] {topic}`)

#### YAML Frontmatter Leakage Check
- [ ] No metadata block starting with `---` leaking into the body
- [ ] Frontmatter not rendered as Markdown body text

#### Cross-Reference Consistency
- [ ] Referenced `#N` items actually exist (no incorrect numbers)
- [ ] For ADRs: referenced ADR numbers are correct
- [ ] `Closes #N` / `Refs #N` references are contextually appropriate

#### Consistency with Codebase
- [ ] Commands, paths, and APIs described in the document match the actual implementation
- [ ] Version information is consistent with the codebase (`package.json`, config files, etc.)
- [ ] Sample code is in a working format

#### Terminology Consistency
- [ ] The same concept uses the same term throughout the document (no mixing of e.g., "skill" and "Skill")
- [ ] Numbers, units, and abbreviations are consistently formatted

### Anti-patterns

| Pattern | Problem |
|---------|---------|
| Frontmatter leakage | Metadata starting with `---` appears in the body |
| Reference to non-existent number | References like `#999` for an Issue/Discussion that doesn't exist |
| Command path mismatch | Path in documentation differs from actual file structure |
| Terminology drift | Multiple expressions for the same concept (e.g., `review-worker` vs `review worker`) |
| Outdated version info | Version number differs from current codebase |

## Trigger Keywords

- "code review"
- "review code"
- "レビューして"
- "コードレビュー"
- "annotation review", "アノテーションレビュー"
- "check usedComponents", "usedComponents確認"
- "verify annotations", "アノテーション検証"
