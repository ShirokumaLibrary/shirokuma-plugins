# Project Items Details

Supplementary details for the `project-items` rule. Covers epic status management, built-in automations, labels, item body maintenance, and item creation guidelines.

## Epic Status Management

Epics (`subIssuesSummary.total > 0`) follow these rules:

| Event | Epic Action |
|-------|-------------|
| First sub-issue becomes In Progress | Epic → In Progress |
| Sub-issue PR merged | Epic remains In Progress |
| Final PR: integration → develop merged | Epic → Done |
| Sub-issue blocked | Epic → Pending (manual, reason comment required) |

Epic Done is determined by the final integration branch merge, not by individual sub-issue completions. See `epic-workflow` reference for details.

## Built-in Automations

GitHub Projects V2 provides built-in automation workflows that complement the CLI-based status updates.

### Recommended Automations

| Workflow | Trigger | Action | Status |
|----------|---------|--------|--------|
| Item closed | Issue is closed | Set Status → Done | **Enable** |
| Pull request merged | PR merged | Set Status → Done | **Enable** |

### How to Enable

Built-in automations are configured via the GitHub UI (not API):

1. Navigate to your GitHub Project's **Settings > Workflows**
2. Enable "Item closed" → set target status to **Done**
3. Enable "Pull request merged" → set target status to **Done**

### CLI Compatibility

| CLI Feature | Behavior with Automations |
|-------------|--------------------------|
| `session end --review` | Sets Review. When PR merges, automation moves to Done |
| `session end --review` (PR already merged) | Auto-promotes to Done via `findMergedPrForIssue()` — idempotent with automation |
| `session end --done` | Sets Done directly — idempotent with automation |
| `session check` | Reports disabled recommended automations as warnings |
| `session check --fix` | Fixes inconsistencies — compatible with automation |
| `issues cancel` | Sets Not Planned after close. May race with "Item closed → Done" automation — CLI update usually wins. Use `session check --fix` to detect/correct. |

### Checking Automation Status

```bash
shirokuma-docs projects workflows
```

Reports all workflows with their enabled/disabled status and recommendations.

## Labels

Labels indicate **where** work applies (cross-cutting attribute). Work type classification uses Issue Types (Type field).

| Label type | Role | Example |
|------------|------|---------|
| Area labels | Scope of impact | `area:cli`, `area:plugin` |
| Operational labels | Triage | `duplicate`, `invalid`, `wontfix` |

### Label Rules

1. **Area labels are optional** - Use when the affected area is not obvious from the title
2. **Multiple area labels allowed** - Cross-cutting issues may have multiple areas
3. **Operational labels for triage** - `duplicate`, `invalid`, `wontfix` are set when closing or redirecting

### Label Categories

| Prefix | Purpose | Examples |
|--------|---------|---------|
| `area:` | Codebase area affected | `area:cli`, `area:plugin`, `area:github` |
| (none) | Operational / triage | `duplicate`, `invalid`, `wontfix` |

## Item Body Maintenance (Issues / Discussions / PRs)

**The body is the source of truth.** Comments serve as historical record; body must always be the latest consolidated version. For detailed procedures, see `managing-github-items/reference/item-maintenance.md`.

> **Comment-first rule**: Always post a comment before updating the body. Comments must have independent value as primary records of work.

Comment operation CLI commands:

| Operation | Command | Notes |
|-----------|---------|-------|
| Add comment | `issues comment {number}` | Works for Issues and PRs |
| List comments | `issues comments {number}` | JSON output |
| Edit comment | `issues comment-edit {comment-id}` | Works for Issues and PRs, `--body-file` accepts file/stdin |

## Creating Items

When creating new items:

1. Set all required fields immediately
2. Use the body template
3. XL items should be split into smaller items
4. Link related items in body if applicable

### Initial Status Guidelines

`issues create` automatically sets Status to **Backlog** by default. Override with `--field-status` when needed:

| Scenario | Status |
|----------|--------|
| Default (planned work) | Backlog |
| Starting immediately | In Progress |
| Low priority / future idea | Icebox |
| Needs requirements review | Spec Review |
