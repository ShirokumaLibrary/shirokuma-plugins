---
scope:
  - main
category: general
priority: required
---

# Memory Operations

## Principle

**Memory is for pointers and working context only.**

## What to Store in Memory

| Type | Example |
|------|---------|
| GitHub reference pointers | `See Discussion #343` `Issue #342` |
| Working context | Test commands, skill counts, quick lookups |

## What NOT to Store → Use GitHub

| Type | Where |
|------|-------|
| Research findings | Discussion (Research) |
| Ideas / proposals | Discussion |
| Architecture decisions | Discussion (ADR) |
| Implementation tasks | Issue |
| Patterns / learnings | Discussion (Knowledge) → Rule extraction |

See `discussions-usage` rule for details.

## Constraints

1. **No duplication with CLAUDE.md or rules** — single source of truth
2. **Topic files should be minimal** — GitHub reference pointers only

## Directive Language in Config Files

Config files are all loaded in parallel into the same context. Relative directives make it unclear which file's instruction is being referenced.

| Bad | Good |
|-----|------|
| "here", "this", "this file" | Use explicit file/section names |
| "the above rule" | `branch-workflow rule` |

## Workarounds Are Plugin Deficiency Signals

When memory contains a workaround (e.g., "in case X, manually do Y"), it signals a deficiency in the plugin (skills, rules, agents). Memory is a temporary record, not a permanent workaround repository.

**How to apply**: When creating feedback-type memories, if it's a problem the plugin should solve, record it as an Evolution signal and connect it to improvement proposals.

## Memory Accumulation → Evolution Flow

Information stored in memory should be treated as future input for updating agents and skills. When memories accumulate, use the `evolving-rules` skill to analyze them and turn them into improvement proposals.

**Flow**: Save memory → detect accumulation → record as Evolution signal → analyze with `evolving-rules` → promote to skill/rule and delete memory.

## Inventory Criteria

Memory should ideally be empty. Keep only items that require ongoing investigation. Periodically inventory existing memories using the flow below.

The Evolution flow handles continuous triage at the moment a memory is created (detecting promotion candidates as they appear). Inventory is the offline counterpart: a periodic, whole-store review that re-applies the four-way classification to everything that has accumulated.

### Four-Way Classification

| Classification | Criteria | Action |
|----------------|----------|--------|
| Promote to plugin rule | Generic rule valid across all projects | Append to `plugin/shirokuma-skills-{ja,en}/rules/` and delete |
| Promote to project-specific rule | Tied to this repo's internal spec or operations | Append to `.shirokuma/rules/{project}/` or `.claude/rules/` and delete |
| Delete | Enforced by code / record of completed work | Delete file and `MEMORY.md` entry |
| Keep | Unresolved issue under ongoing investigation | Retain with a name that identifies it as "under investigation" |

### Plugin vs Project-Specific Criteria

| Condition | Promotion Target |
|-----------|-----------------|
| Valid for any project using the shirokuma-docs CLI | Plugin side |
| Governs the plugin's own skills/workflow | Plugin side |
| Claude Code behavioral principles (investigation, review approach, etc.) | Plugin side |
| Tied to this repo's internal architecture, spec, or CLI subcommands | Project-specific (`.shirokuma/rules/{project}/`) |
| Specific to this repo's dev environment (scripts, settings) | Project-specific (`.claude/rules/`) |
| Project-specific decisions/constraints (e.g., pre-release) | Project-specific |

### Deletion Criteria

A memory is a deletion candidate if any of the following applies.

- Already enforced by code/rule/hook, with a canonical doc source elsewhere
- Records of completed work on a specific Issue/PR (git log is the canonical source)
- One-shot research results (already saved in Discussion or no longer needed)
- Point-in-time snapshots where "in memory = still valid" no longer holds

### How to Run the Inventory

Inventory is an investigation task. Run it in the main context; do not delegate to a subagent (read each memory yourself and classify it). Strictly distinguish plugin vs project-specific promotion using the criteria above.
