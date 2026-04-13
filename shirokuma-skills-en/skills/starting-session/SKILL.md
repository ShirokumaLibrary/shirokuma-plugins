---
name: starting-session
description: Conversation initialization skill that loads rules and displays project state at the start of a conversation. Triggers: "start session", "begin work", "session start", "initialize conversation", "init session".
allowed-tools: Bash, Read, Grep
---

!`shirokuma-docs rules inject --scope main`

# Conversation Initialization

A simple entry point that loads rules and displays project state for a new conversation.

## Workflow

### Step 1: Fetch Project State

```bash
shirokuma-docs items dashboard
```

This returns JSON with:
- `repository` - Current repository
- `git` - Git state (`branch`, `uncommitted_changes`, `unpushed_commits`, etc.)
- `lastHandover` - Latest handover (null if none)
- `backups` - PreCompact session backups (if any exist from interrupted sessions)
- `issues` - Active issues with project fields (Done excluded)
- `total_issues` - Count of active issues
- `openPRs` - Open pull requests with review status

### Step 1b: Backup Detection

If the `backups` field is present, a previous session may have been interrupted before proper handover.
Show the backup contents (branch, uncommitted changes, recent commits) to help the user recover context.

### Step 2: Display Project State

Parse the JSON output and display:

```markdown
## Session Started

**Repository:** {repository}
**Time:** {current time}
**Branch:** {git.branch} {git.uncommitted_changes > 0 ? "(uncommitted changes)" : "(clean)"}

### Open PRs
| # | Title | Review | Threads |
|---|-------|--------|---------|
| #42 | feat: Add new feature | APPROVED | 0 |

{If no PRs, show "No open PRs."}

### Active Issues

**In Progress:**
- #{number} {title} (Priority: {priority}, Size: {size})

**Backlog ({count}):**
- #{number} {title}
```

Group issues by status: In Progress → Backlog → Pending → (no status). Fold issues in `@deprecated` statuses (Ready / Completed) into the Backlog group so legacy issues remain visible.

If there are uncommitted changes (`git.uncommitted_changes > 0`), inform the user before proceeding.

## Issue-Bound Mode (when `#N` provided)

When invoked with `/starting-session #N`, display the issue state and route to `implement-flow #N`:

```
Skill: implement-flow
Args: #{N}
```

Status-based routing is handled by `implement-flow` — `starting-session` does not perform additional confirmation.

## Batch Candidate Suggestion

After displaying active issues (Step 2), check for batch candidates among Backlog items.

### Detection

1. Filter issues from `items dashboard` output: Status = Backlog, Size = XS or S
2. Group by `area:*` label (primary) or title keyword similarity (fallback: 2+ common nouns)
3. Show groups with 3+ issues, max 3 groups

### Display

If candidates found, add after the Active Issues section:

```markdown
### Batch Candidates
| Group | Issues | Area |
|-------|--------|------|
| Plugin fixes | #101, #102, #105 | area:plugin |
| CLI improvements | #110, #112, #115 | area:cli |
```

To start batch processing, run `/implement-flow #101 #102 #105`.

## Evolution Signal Reminder

After context display (Step 2), check if signals have accumulated in Evolution Issues (see `evolution-details.md` "Standard Search & Creation Flow" for the search command).

```bash
shirokuma-docs items list --issue-type Evolution --limit 1
```

If signals are accumulated, show a single line after the Active Issues section:

```markdown
> 🧬 Evolution signals are accumulated. Run `/evolving-rules` to analyze.
```

- **No auto-execution** — reminder only (user decides whether to invoke)
- **Hidden when empty** — avoid noise

## Multi-Developer Mode

In team development, add options to `items dashboard`:

```bash
# Show handovers from a specific user
shirokuma-docs items dashboard --user {username}

# Show handovers from all members (no filter)
shirokuma-docs items dashboard --all

# Team dashboard (grouped by member)
shirokuma-docs items dashboard --team
```

| Option | Behavior |
|--------|----------|
| (default) | Fetches only handovers created by the current GitHub user |
| `--user {username}` | Fetches handovers from the specified user |
| `--all` | Fetches handovers from all members (no filter) |
| `--team` | Groups handovers and issues by member for team overview |

## Error Handling

| Error | Action |
|-------|--------|
| `shirokuma-docs: command not found` | Install: `pnpm install` in shirokuma-docs |
| `gh: command not found` | Install: `brew install gh` or `sudo apt install gh` |
| `not logged in` | Run: `gh auth login` |
| issues is empty | Show "No active issues" |
| git pull fails | Warn and continue with local base branch |
| `items dashboard: command not found` | Upgrade shirokuma-docs: `shirokuma-docs update` |

## Next Steps

After displaying state, the user selects the next action:

- Work on a specific issue: `/implement-flow #N`
- Create a new issue: `/create-item-flow`
- Start planning: `/prepare-flow #N`
- Batch processing: `/implement-flow #N1 #N2 #N3`

## Notes

- Always show current time in session header
- Show items in priority order within each status
- Done items are automatically excluded by `items dashboard`
- Use `shirokuma-docs items dashboard` instead of raw `gh` commands — the CLI aggregates handover, issues, and PRs in one call, saving context window
- Handover save/restore is not this skill's responsibility. Issue status updates are managed via `items update-status` CLI, not directly by this skill
