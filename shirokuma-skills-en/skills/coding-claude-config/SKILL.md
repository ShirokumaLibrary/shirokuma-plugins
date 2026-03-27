---
name: coding-claude-config
description: Creates, updates, and implements Claude Code configuration files (skills, rules, agents, output-styles, plugins) following best practices. Automatically delegated from code-issue. Triggers: "create skill", "update skill", "create rule", "create agent", "create plugin", "create output style", "implement SKILL.md", "changes under plugin/", "changes under .claude/".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Claude Code Configuration Implementation

Creates and updates Claude Code configuration files following official best practices.

> **Implementation is this skill's responsibility.** `reviewing-claude-config` handles quality checks.

## Config Type Dispatch

Determine the config type from the issue context and target files, then reference the appropriate guide.

| Target | Config Type | Reference |
|--------|-------------|-----------|
| `*/skills/*/SKILL.md`, `.claude/skills/` | Skills | [reference/skills/](reference/skills/) |
| `*/rules/*.md`, `.claude/rules/` | Rules | [reference/rules/rules.md](reference/rules/rules.md) |
| `*/agents/*.md`, `.claude/agents/` | Agents | [reference/agents/](reference/agents/) |
| `*/plugins/`, `plugin.json` | Plugins | [reference/plugins/](reference/plugins/) |
| `*/output-styles/*.md` | Output Styles | [reference/output-styles/](reference/output-styles/) |
| `plugin/` overall structure | Plugin distribution | [reference/platform.md](reference/platform.md) |
| `coding-*` / `designing-*` skills | Orchestrator integration | [reference/orchestrator.md](reference/orchestrator.md) |

## Workflow

### 0. Pre-work Check

1. Read the issue's `## Plan` and `## Deliverable` to understand scope
2. Read the current state of target files with the Read tool (for existing files)
3. Reference the appropriate guide for the config type

### 1. Implement JA Version

Implement following the best practices in the corresponding reference.

**Required Checks (all config types):**
- [ ] Frontmatter has `name` and `description`
- [ ] SKILL.md / AGENT.md is under 500 lines
- [ ] References are one level deep (SKILL.md → supporting files)
- [ ] Paths always use forward slashes
- [ ] No temporary markers (TODO, FIXME, WIP, TBD)
- [ ] No cross-context-boundary references (see below)

**Context Boundary Constraints:**
- Rules must not reference skill `reference/` (rule context cannot access skill references) → include necessary details in the rule body or mention only the skill name (e.g., "this is managed by coding-claude-config skill")
- Skill A must not reference Skill B's `reference/` by path → mention only the skill name
- Agents do not auto-inherit main context rules → inject via `skills:` frontmatter or instruct explicit Read in initialization

### 2. Implement EN Version

After completing the JA version, create the EN version.

- Maintain the same structure as the JA version, translate content to English
- EN version paths are under `plugin/shirokuma-skills-en/skills/`
- Also translate the `description` field
- Convert trigger phrases in description to English patterns

### 3. Update Related Files

Some config types require updating related files:

- Adding skills under `plugin/` → Update Bundled Skills table in CLAUDE.md
- Adding rules → Update Bundled Rules table in CLAUDE.md

### 4. For Deletion Tasks

When deleting files:

1. Check for references with Grep before deleting
2. Update references as well
3. Delete the target directory with `rm -rf`

## EN/JA Sync Rules

| Element | Rule |
|---------|------|
| File structure | Full EN/JA correspondence (same filenames/directories) |
| Frontmatter `name` | Identical (language-independent) |
| Frontmatter `description` | Translated (JA/EN respectively) |
| Body content | Translated |
| Commands in code blocks | Identical |
| Template files | Identical (language-neutral) |

## Version Bump Rules

Follow the `plugin-version-bump` rule: version bumps only at release time. Do not bump for daily config changes.

## Templates

| Template | Use |
|----------|-----|
| [templates/simple-agent.md](templates/simple-agent.md) | Simple agent boilerplate |
| [templates/complex-agent.md](templates/complex-agent.md) | Complex agent boilerplate |
| [templates/creator-checker-pair.md](templates/creator-checker-pair.md) | Creator-Checker pair boilerplate |

## Notes

- Config files are **model-invoked** (skills) or **user-invoked** (commands)
- After changes, review with `reviewing-claude-config`
- Strictly enforce the 500-line SKILL.md limit — move content to supporting files if exceeded
- Files under `plugin/` must always sync-update both EN and JA versions
