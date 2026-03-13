---
name: code-issue
description: Handles generic coding tasks by delegating to framework-specific skills or performing direct edits based on work type. Automatically delegated from working-on-issue. Not intended for direct invocation.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Skill, WebSearch, WebFetch
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

## Skill Discovery (Run Before Dispatch)

In addition to fixed dispatch table entries, dynamically detect project-specific skills:

```bash
shirokuma-docs skills routing coding
```

Refer to the `description` of each entry in the output `routes` array and route to the skill that best matches the issue requirements.
Entries with `source: "discovered"` / `source: "config"` are project-specific skills.
If a fixed table skill is optimal, it takes precedence regardless of discovery results.

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

- As an Agent tool (subagent), `TodoWrite` / `AskUserQuestion` are not available
- Progress management is handled by the manager (main AI, `working-on-issue`)
- TDD workflow is managed by `working-on-issue` wrapping `code-issue` calls with TDD steps (`code-issue` focuses solely on implementation)
- UI design tasks (new UI pages, visual redesigns, design system token changes) are handled by `designing-on-issue` → `designing-shadcn-ui`, not by this skill
- **Commit, push, and PR creation are outside the scope of this skill**. This skill is responsible for code changes only — `commit-issue` handles commits and `create-pr-issue` handles PR creation in the subsequent chain. Do not directly execute `git commit` / `git push` / `gh pr create` / `shirokuma-docs pr create`

## Output Template

After work completes, return the following structured data to the caller. Code changes are the deliverable, so no GitHub write is performed (GitHub writes are handled by subsequent `commit-issue` / `create-pr-issue`).

```yaml
---
action: CONTINUE
next: commit-issue
status: SUCCESS
---

{file count} files changed. {one-line change summary}

### Changed Files
- `src/path/file.ts` - {change description}
- `src/path/other.ts` - {change description}
```

On failure:

```yaml
---
action: STOP
status: FAIL
---

{error description}
```

**Note**: `ref` field is omitted (no GitHub write).
