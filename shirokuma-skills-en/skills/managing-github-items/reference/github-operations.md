# GitHub Operations Reference

Shared reference for all session/GitHub skills. Single source of truth for CLI commands, workflows, and conventions.

## Contents

- Architecture: Issues + Projects Hybrid
- Prerequisites
- DraftIssue vs Issue
- shirokuma-docs CLI Reference
- `--from-file` vs `--body-file` Usage Guide
- Status Workflow
- Labels Convention
- Common Error Handling

## Architecture: Issues + Projects Hybrid

| Component | Purpose |
|-----------|---------|
| **Issues** | Task management, `#123` references, history |
| **Projects** | Status/Priority/Size field management |
| **Labels** | Supplementary area classification (`area:cli`, `area:plugin`, etc.) |
| **Discussions** | Handovers, Specs, Decisions, Q&A |

**Status is managed via Projects fields** (not Labels).

Project naming convention: Project name = repository name (e.g., `blogcms` repo → `blogcms` project).

## Prerequisites

- `gh` CLI installed and authenticated
- GitHub Project configured (run `/setting-up-project` if not)
- Discussions enabled with categories: Handovers, Ideas, Q&A (optional)

## DraftIssue vs Issue

| Feature | DraftIssue | Issue |
|---------|-----------|-------|
| `#number` | No | Yes (`#123`) |
| External reference | No | Yes |
| Comments | No | Yes |
| Use case | Lightweight memo | Full task |

**Recommendation**: Use `issue add` by default for `#number` support.

## shirokuma-docs CLI Reference

Prefer shirokuma-docs CLI over direct `gh` commands. Config in `shirokuma-docs.config.yaml`.

### Issues (Primary Interface)

```bash
shirokuma-docs issue list                            # Open issues
shirokuma-docs issue list --all                      # Include closed
shirokuma-docs issue list --status "In progress"     # Filter by status
shirokuma-docs issue context {number}                # Fetch details and cache (→ Read .shirokuma/github/{org}/{repo}/issues/{number}/body.md)
shirokuma-docs issue add --file /tmp/shirokuma-docs/new-issue.md  # Metadata + body in one file
shirokuma-docs issue update {number} --body /tmp/shirokuma-docs/{number}-body.md  # Update body
shirokuma-docs issue update {number} --title "New title"                           # Update title
shirokuma-docs issue update {number} --labels "area:cli,area:plugin"               # Update labels
shirokuma-docs issue update {number} --assignees "@me"                             # Update assignees
shirokuma-docs status transition {number} --to "In progress"                        # Status transition
shirokuma-docs issue comment {number} --file /tmp/shirokuma-docs/{number}-comment.md
shirokuma-docs issue comments {number}                   # List comments
shirokuma-docs issue update {number} --comment-id {comment-id} --body /tmp/shirokuma-docs/{number}-comment-fix.md  # Edit comment
shirokuma-docs issue close {number}
shirokuma-docs issue cancel {number}
shirokuma-docs issue reopen {number}
```

### Pull Requests

```bash
shirokuma-docs pr create --from-file /tmp/shirokuma-docs/pr.md             # Metadata + body in one file
shirokuma-docs pr create --base main --head develop --title "release: v0.2.0"  # Release workflow (metadata only)
shirokuma-docs pr list                                      # PR list (default: open)
shirokuma-docs pr list --state merged --limit 5            # Filtering
shirokuma-docs pr show {number}                             # PR details (body, diff stats, linked issues)
shirokuma-docs pr comments {number}                         # Review comments and threads
shirokuma-docs pr merge {number} --squash                   # Merge + status update
shirokuma-docs pr reply {number} --reply-to {id} --body-file - <<'EOF'
Reply content
EOF
shirokuma-docs pr resolve {number} --thread-id {id}        # Resolve thread
```

### Projects (Item Operations)

```bash
shirokuma-docs project update {number} --field-status "Done"  # Field update (only way)
shirokuma-docs project add-issue {number}                     # Add issue to project
shirokuma-docs project delete PVTI_xxx                        # Delete item
```

### Discussions

```bash
shirokuma-docs discussion list --category Handovers --limit 5
shirokuma-docs discussion search "keyword"            # Discussion search
shirokuma-docs issue search --type discussions "keyword"     # Via issue search
shirokuma-docs issue context {number}   # Fetch details and cache (→ Read .shirokuma/github/{org}/{repo}/issues/{number}/body.md)
shirokuma-docs discussion add --file /tmp/shirokuma-docs/discussion.md  # Metadata + body in one file
```

### Cross-search

```bash
shirokuma-docs issue search "keyword"                          # Issues / PR search (default)
shirokuma-docs issue search --type discussions "keyword"       # Discussions only
shirokuma-docs issue search --type issues,discussions "keyword" # Issues + Discussions cross-search
```

### Repository

```bash
shirokuma-docs repo info
shirokuma-docs repo labels
```

### Cross-repo Operations

```bash
shirokuma-docs issue list --repo docs
shirokuma-docs issue add --repo docs --file /tmp/shirokuma-docs/new-issue.md
```

### gh Fallback (CLI unsupported only)

```bash
# Label management
gh label list
gh label create "name" --color "0E8A16" --description "Desc"

# Repository info
gh repo view --json nameWithOwner -q '.nameWithOwner'

# Authentication
gh auth login
gh auth status

```

## `--from-file` vs `--body-file` Usage Guide

| Pattern | Commands | Reason |
|---------|----------|--------|
| `issue add` recommended | `issue add`, `discussion add` | Metadata + body in one file, prevents flag combination errors |
| `--body-file` kept | `pr reply`, `status update-batch` | Body only, no metadata needed |
| `issue update` / `status transition` | Status/body/title/labels/assignees update | Direct update without cache-edit workflow |

### `--from-file` Frontmatter Format

```markdown
---
title: Issue Title
type: Feature
priority: Medium
size: M
labels: [area:cli]
---

Body content goes here.
```

Safe frontmatter fields vary by command:

| Command | Safe Fields |
|---------|-------------|
| `issue add` | `title`, `type`, `priority`, `size`, `labels`, `state`, `state_reason`, `parent` |
| `pr create` | `title`, `base`, `head` |
| `discussion add` | `title`, `category` |

CLI flags take precedence when set. `--from-file` and `--body-file` are mutually exclusive (error if both specified).

### `--body-file` Tier Guide

| Tier | Pattern | Usage |
|------|---------|-------|
| Tier 1 (stdin) | `--body-file - <<'EOF'...EOF` | Comments, replies, short reasons |
| Tier 2 (file) | Write → `--body-file /tmp/shirokuma-docs/xxx.md` | Body updates, handovers |

Use `<<'EOF'` as heredoc delimiter (single quotes prevent variable expansion). When iteratively updating bodies via Tier 2, apply the Write/Edit pattern (initial Write → subsequent Edit for diff-only updates). See the "File-Based Body Editing" section in `item-maintenance.md` for details.

## Status Workflow

```mermaid
graph LR
  Pending2[Pending] --> Backlog --> Ready --> InProgress[In Progress]
  InProgress --> Review --> Done
  InProgress <--> OnHold["On Hold (blocked)"]
  InProgress --> Cancelled
  Backlog --> Cancelled
  Ready --> Cancelled
  Done --> Completed
```

| Status | Description |
|--------|-------------|
| Pending | Not yet triaged |
| Backlog | Planned for future work |
| Ready | Ready to start implementation |
| In Progress | Currently working on |
| On Hold | Blocked (document reason) |
| Review | Code review / plan review |
| Completed | Merged and closed (system-set) |
| Done | Approved and complete |
| Cancelled | Will not be implemented |

## Labels Convention

Work type classification is primarily handled by **Issue Types** (Organization-level Type field). Labels indicate the **affected area** as a supplementary mechanism:

| Mechanism | Role | Example |
|-----------|------|---------|
| Issue Types | **What** kind of work | Feature, Bug, Chore, Docs, Research, Evolution |
| Area labels | **Where** the work applies | `area:cli`, `area:plugin` |
| Operational labels | Triage / lifecycle | `duplicate`, `invalid`, `wontfix` |

Labels are added manually based on project structure. Status is managed via Projects fields.

## Common Error Handling

| Error | Action |
|-------|--------|
| `shirokuma-docs: command not found` | Install: `npm i -g @shirokuma-library/shirokuma-docs` |
| `gh: command not found` | Install: `brew install gh` or `sudo apt install gh` |
| `not logged in` / `not authenticated` | Run: `gh auth login` |
| No project found | Run `/setting-up-project` to create one |
| Discussions disabled/category not found | Use local file fallback |
| `HTTP 404` | Check repository name and permissions |
| API rate limit | Show cached/partial data |
