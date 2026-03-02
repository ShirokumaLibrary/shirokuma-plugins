---
name: coding-on-issue
description: Handles generic coding tasks by delegating to framework-specific skills or performing direct edits based on work type. Automatically delegated from working-on-issue. Not intended for direct invocation.
context: fork
agent: general-purpose
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Generic Coding

Generic coding skill delegated from `working-on-issue`. Routes to framework-specific skills (`coding-nextjs`) via Skill delegation or performs direct editing based on work type.

## Context

The following context is passed as arguments from `working-on-issue`:

- Issue number
- Plan section (work content)
- Labels (`area:*` etc.)
- Work type classification result

No need to re-fetch the issue.

## Dispatch

| Work Type | Condition | Route |
|-----------|-----------|-------|
| Next.js implementation | `area:frontend`, `area:cli` + Next.js related | Skill delegate to `coding-nextjs` |
| Bug fix (code) | Affects code files | Skill delegate to `coding-nextjs` |
| Markdown / documentation editing | `.md` file changes | Direct edit |
| Skill / rule / agent editing | Under `plugin/`, `.claude/` | Direct edit (reference `managing-*` skill best practices) |
| Refactoring | `refactor` keyword | Direct edit |
| Config / Chore | `config`, `chore` keywords | Direct edit |

## Work Type Guidance

### Next.js Implementation / Bug Fix

Skill delegate to `coding-nextjs`. Pass plan section and issue context.

### Markdown / Documentation Editing

- Follow existing documentation structure and style
- Comply with `output-language` rule
- Verify link integrity

### Skill / Rule / Agent Editing

- Reference `managing-rules`, `managing-skills`, `managing-agents` skill best practices
- Edit both EN/JA versions when both need updating
- Files under `plugin/` — note `plugin-version-bump` rule (version bumps at release time only)

### Refactoring

- Focus on structural improvement without changing behavior
- If tests exist, run them to confirm no regressions

### Config / Chore

- Follow config file schema and format
- Verify impact scope for dependency changes

## Constraints

- `context: fork` — `TodoWrite` / `AskUserQuestion` are not available
- Progress management is handled by the manager (main AI, `working-on-issue`)
- TDD workflow is managed by `working-on-issue` wrapping `coding-on-issue` calls with TDD steps (`coding-on-issue` focuses solely on implementation)
- UI design tasks (new UI pages, visual redesigns, design system token changes) are handled by `designing-ui-on-issue` → `designing-shadcn-ui`. See `working-on-issue/docs/designing-reference.md` for responsibility boundaries

## Fork Result Return

After work completes, return the following structured data to the caller. Code changes are the deliverable, so no GitHub write is performed (GitHub writes are handled by subsequent `committing-on-issue` / `creating-pr-on-issue`).

```text
## Fork Result
**Status:** SUCCESS
**Summary:** {file count} files changed. {one-line change summary}
**Next:** Proceed to committing-on-issue
```

On failure:

```text
## Fork Result
**Status:** FAIL
**Summary:** {error description}
```

**Note**: `Ref` field is omitted (no GitHub write).
