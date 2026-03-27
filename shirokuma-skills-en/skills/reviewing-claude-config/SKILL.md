---
name: reviewing-claude-config
description: Reviews Claude Code configuration files (skills, rules, agents, output-styles, plugins) for quality, consistency, and Anthropic's best practices. Use PROACTIVELY after creating or updating any .claude/ configuration. Triggers: "config review", "quality check", "review config".
allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
---

# Claude Config Reviewer

Reviews Claude Code configuration files for quality and Anthropic's best practices.

> Reference: [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

## Core Responsibilities

- Validate structure against best practices
- Detect anti-patterns and temporary markers
- Check for broken internal links
- Verify required sections exist
- Report issues with severity levels

## Workflow

1. **Discover**: Find all config files in `.claude/` and `.claude/plugins/`
2. **Categorize**: Group by type (agents, skills, commands, output-styles, plugins)
3. **Validate**: Check each file against its type-specific rules
4. **Report**: Generate findings with severity and fix suggestions

## Validation Rules

### All Files

| Check | Severity | Pattern (and variations) |
|-------|----------|--------------------------|
| Temporary markers | Warning | `**NEW**`, `TODO:`, `FIXME:`, `WIP`, `TBD`, `DRAFT`, `PLACEHOLDER`, `XXX:` |
| Manual date stamps | Warning | `Last Updated:`, `Updated:`, `Modified:`, `Created:`, `Date:`, `Version:`, `Rev:` |
| ASCII art diagrams | Warning | Box-drawing characters, repeated decorators (`===`, `---` as borders) |
| Broken links | Error | `[text](path)` where path doesn't exist |
| Parent reference loop | Warning | `[../CLAUDE.md]`, `See parent project` |
| Missing language in code blocks | Info | ` ``` ` without language specifier |
| File too long | Warning | > 500 lines for SKILL.md |
| Direct reference to another skill's reference path | Warning | Rule `.md` references `skill-name/reference/xxx.md` format. **Rationale**: Claude Code uses a 3-layer loading model (metadata → instruction body → resources), and each config type has its own context space. Rules are always loaded but reference/ files are not auto-resolved, resulting in dead references. Fix: include necessary details in the rule body or mention only the skill name (e.g., "this is managed by skill-name skill") |
| Inappropriate guidance phrases | Warning | Rule `.md` contains phrases like "invoke the skill to check", "refer to reference/ when executing", "read the reference/" that direct readers to access skill reference files. Rule loading context cannot access skill references — such guidance is misleading. Fix: include specifics in the rule body or reference by skill name only |

**Pattern Matching**: Use fuzzy matching for similar patterns:
- Dates: `/\d{4}[-/]\d{2}[-/]\d{2}/` outside code blocks
- Markers: Case-insensitive (`TODO`, `Todo`, `todo`)
- Versions: `v1.0`, `1.0.0`, `ver. 1.0`
- ASCII art: `/[+\-|]{3,}/` forming boxes

### Skills (`.claude/skills/` and `.claude/plugins/*/skills/`)

| Check | Severity |
|-------|----------|
| Missing SKILL.md | Error |
| No description in SKILL.md frontmatter | Error |
| Reference to non-existent file | Error |
| Direct reference to another skill's `reference/` path (e.g., `skill-name/reference/xxx.md`). Cross-context-boundary reference/ files are not auto-resolved between skills | Warning |

### Agents (`.claude/agents/`)

| Check | Severity |
|-------|----------|
| Missing `name` in frontmatter | Error |
| Missing `description` in frontmatter | Error |
| Invalid name format (must be lowercase-hyphen) | Error |
| Description without invocation triggers | Warning |
| No workflow section | Warning |
| Excessive tools (> 5 without justification) | Info |

**Anthropic Best Practices Checks**:

| Check | Severity | Rationale |
|-------|----------|-----------|
| Heavy agent (> 500 lines, ~25k+ tokens) | Warning | Bottlenecks in multi-agent workflows |
| Kitchen sink pattern (all tools + broad scope) | Warning | Violates single responsibility |
| Too many responsibilities (> 3 core tasks) | Warning | "Start simple" principle |
| Missing "When to Use" guidance | Info | Clear invocation triggers needed |
| Reviewer with Write/Edit tools | Warning | Checker agents should be read-only |
| Generator without Write tool | Info | May be incomplete |

### Commands (`.claude/commands/`)

| Check | Severity |
|-------|----------|
| Empty command file | Error |
| No description comment at top | Warning |

### Output Styles (`.claude/output-styles/`)

| Check | Severity |
|-------|----------|
| Missing style definition | Error |

### Plugins (`plugin/`)

| Check | Severity | Detection |
|-------|----------|-----------|
| Any `plugin.json` `version` field doesn't match root `package.json` `version` field | Warning | Compare all 7 plugin.json files against `package.json`: `plugin/shirokuma-skills-en/.claude-plugin/plugin.json`, `plugin/shirokuma-skills-ja/.claude-plugin/plugin.json`, `plugin/shirokuma-hooks/.claude-plugin/plugin.json`, `plugin/shirokuma-nextjs-en/.claude-plugin/plugin.json`, `plugin/shirokuma-nextjs-ja/.claude-plugin/plugin.json`, `plugin/shirokuma-infra-en/.claude-plugin/plugin.json`, `plugin/shirokuma-infra-ja/.claude-plugin/plugin.json` |

### Document Structure (directory-format skills/agents)

Applies to directory-format configs with multiple supporting files:

| Check | Severity | Criteria |
|-------|----------|---------|
| Single source of truth violation | Warning | Same information duplicated in multiple files (e.g., reference.md re-stating code from patterns/) |
| Pattern file too long | Info | `patterns/*.md` exceeds 200 lines (80-150 lines is ideal) |
| Code block missing language specifier | Info | ` ``` ` without language (`typescript`, `bash`, `json`, etc.) |

### `coding-*` / `designing-*` Specialist Skills

Applies to specialist skills delegated from `code-issue` / `design-flow`:

| Check | Severity | Criteria |
|-------|----------|---------|
| Contains `AskUserQuestion` or `TaskCreate` / `TaskUpdate` | Warning | Specialist skills run inside worker subagents — interactive tools prohibited |
| No context reception section | Info | Should handle both delegated and standalone modes |
| Missing `coding-` / `designing-` prefix | Warning | Prefix required for automatic discovery |

## Anti-Patterns to Detect

```text
# Temporary markers (case-insensitive, with variations)
**NEW**, **WIP**, **DRAFT**, **PLACEHOLDER**
TODO:, TODO(xxx):, FIXME:, HACK:, XXX:, NOTE:
TBD, N/A, COMING SOON, IN PROGRESS
[WIP], [DRAFT], [TODO]

# Manual date stamps (git tracks this - detect variations)
Last Updated: 2025-xx-xx
Updated:, Modified:, Created:, Revised:
Date: xxxx-xx-xx
Version: 1.0.0, v1.0, Rev. 1.0
(any YYYY-MM-DD or YYYY/MM/DD outside code blocks)

# Stale references
(patterns/old-file.md)  # file doesn't exist
(../missing.md)         # broken relative link

# Vague descriptions
description: Does stuff
description: Agent for things
description: [TODO]

# Kitchen sink agents (violates single responsibility)
tools: All
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, Task  # Too many

# Checker agents with write access (Creator-Checker violation)
name: code-reviewer
tools: Read, Write, Edit      # Reviewers should be read-only

# Cross-context-boundary inappropriate guidance (in rules)
"See skill-name/reference/xxx.md for details"  # Rules cannot access skill references
"Invoke the skill to check"                     # Skills are not invoked at rule load time
"Refer to reference/ when executing the skill"  # Rule readers are not in a skill execution context
"Read the reference/ to confirm"                # reference/ is not resolved from rule context
```

**ASCII Art Alternatives** (context-size conscious):

| Instead of | Use |
|------------|-----|
| Box diagrams | Markdown tables, bullet lists |
| Flow arrows | Numbered steps, `1. → 2. → 3.` |
| Tree structures | Indented lists, file path notation |
| Decorative borders | Markdown headings (`##`) |

## Report Format

```markdown
# Claude Config Review

**Scanned**: {count} files in .claude/
**Issues**: {error_count} errors, {warning_count} warnings, {info_count} info

## Errors (Must Fix)

- [{file}] {issue description}
  Fix: {suggestion}

## Warnings (Should Fix)

- [{file}] {issue description}
  Fix: {suggestion}

## Info (Consider)

- [{file}] {issue description}

## Summary

{Overall assessment and next steps}

**Review result:** {PASS | FAIL}
```

**Review result determination:**
- Error > 0 → `**Review result:** FAIL`
- Error = 0 → `**Review result:** PASS`

The report must always end with `**Review result:** PASS` or `**Review result:** FAIL`.

## Workflow Pattern Recognition

When reviewing skills/agents, identify which pattern they follow:

| Pattern | Indicators | Recommendation |
|---------|------------|----------------|
| **Analyzer** | Read-only tools, "review/check/analyze" in description | Ensure no Write/Edit tools |
| **Generator** | Write tool, "create/generate" in description | Verify output format defined |
| **Transformer** | Edit tool, "refactor/migrate/update" in description | Check safety rules exist |
| **Investigator** | Bash + Read, "debug/diagnose" in description | Ensure root cause workflow |
| **Orchestrator** | Task tool, coordinates subagents | Verify delegation logic |

**Creator-Checker Pair Detection**:
- If name contains "reviewer/auditor/checker" should be read-only
- If name contains "builder/generator/coder" needs Write tool

## Key Points

- Run after any `.claude/` file creation or update
- Focus on actionable issues with clear fixes
- Errors must be fixed, warnings are recommended
- Keep report concise and scannable
- Reference Anthropic's best practices when suggesting fixes
- Runs via Skill tool in the main context, enabling access to project-specific rules for quality validation

## Anti-Patterns

- Report issues without auto-fixing — the reviewer role maintains objectivity by separating analysis from implementation
- Exclude plugin-generated rules in `.claude/rules/shirokuma/` — these are managed by the plugin and overwritten on update

## Why This Is a Skill (Not an Agent)

`reviewing-claude-config` runs via the Skill tool in the main context deliberately. This is required because:

- **Project-specific rules access**: Quality checks must validate against `.shirokuma/rules/` content (e.g., `skill-authoring-quality.md`, `skill-scope-boundaries.md`). These rules are only accessible in the main context where rules are injected.
- **Rules injection model**: The `rules inject` mechanism delivers project-specific context to the main context at session start. Subagents (Agent tool) do not receive this injection automatically.
- **Cross-reference validation**: Checking whether a skill properly uses project conventions requires reading both the skill and the project rules together in the same context.

A subagent variant (`config-review-worker`) was considered but removed — the same quality validation can be achieved by running this skill in the main context without the overhead of a separate agent.

