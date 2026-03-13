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
| Create command | `projects create` | `issues create` |
| Use case | Lightweight memo | Full task |

**Recommendation**: Use `issues create` by default for `#number` support.

## shirokuma-docs CLI Reference

Prefer shirokuma-docs CLI over direct `gh` commands. Config in `shirokuma-docs.config.yaml`.

### Issues (Primary Interface)

```bash
shirokuma-docs issues list                          # Open issues
shirokuma-docs issues list --all                    # Include closed
shirokuma-docs issues list --status "In Progress"   # Filter by status
shirokuma-docs show {number}                  # Details
shirokuma-docs issues create --from-file /tmp/shirokuma-docs/new-issue.md  # Metadata + body in one file
shirokuma-docs issues update {number} --field-status "In Progress"
shirokuma-docs issues update {number} --add-label "area:cli"       # Add label
shirokuma-docs issues update {number} --remove-label "area:docs"   # Remove label
shirokuma-docs issues comment {number} --body-file - <<'EOF'
Comment content
EOF
shirokuma-docs issues comments {number}                 # List comments
shirokuma-docs issues comment-edit {comment-id} --body-file /tmp/shirokuma-docs/comment.md  # Works for Issue/PR comments
shirokuma-docs issues close {number}
shirokuma-docs issues reopen {number}
```

### Pull Requests

```bash
shirokuma-docs pr create --from-file /tmp/shirokuma-docs/pr.md             # Metadata + body in one file
shirokuma-docs pr create --base main --head develop --title "release: v0.2.0"  # Release workflow (metadata only)
shirokuma-docs pr list                                      # PR list (default: open)
shirokuma-docs pr list --state merged --limit 5            # Filtering
shirokuma-docs pr list --head {branch-name}                # Resolve PR from branch name
shirokuma-docs pr show {number}                             # PR details (body, diff stats, linked issues)
shirokuma-docs pr comments {number}                         # Review comments and threads
shirokuma-docs pr merge {number} --squash                   # Merge + status update
shirokuma-docs pr reply {number} --reply-to {id} --body-file - <<'EOF'
Reply content
EOF
shirokuma-docs pr resolve {number} --thread-id {id}        # Resolve thread
```

### Projects (Low-level Access)

```bash
shirokuma-docs projects list                        # Project items
shirokuma-docs projects fields                      # Show field options
shirokuma-docs projects add-issue {number}          # Add issue to project
shirokuma-docs projects create \
  --title "Title" --body-file /tmp/shirokuma-docs/body.md \
  --field-status "Backlog" --priority "Medium"               # DraftIssue
shirokuma-docs projects get PVTI_xxx                # By item ID
shirokuma-docs projects update {number} --field-status "Done"
```

### Discussions

```bash
shirokuma-docs discussions list --category Handovers --limit 5
shirokuma-docs show {number}
shirokuma-docs discussions create --from-file /tmp/shirokuma-docs/discussion.md  # Metadata + body in one file
```

### Repository

```bash
shirokuma-docs repo info
shirokuma-docs repo labels
```

### Cross-repo Operations

```bash
shirokuma-docs issues list --repo docs
shirokuma-docs issues create --repo docs --from-file /tmp/shirokuma-docs/new-issue.md
```

### gh Fallback (CLI unsupported only)

```bash
# Label management
gh label list
gh label create "name" --color "0E8A16" --description "Desc"

# Authentication
gh auth login
gh auth status

```

## `--from-file` vs `--body-file` Usage Guide

| Pattern | Commands | Reason |
|---------|----------|--------|
| `--from-file` recommended | `issues create`, `pr create`, `discussions create` | Metadata + body in one file, prevents flag combination errors |
| `--body-file` kept | `issues comment`, `pr reply`, `issues comment-edit`, `session end` | Body only, no metadata needed |
| `--body-file` kept | `issues update` (body-only update) | `--body-file` is sufficient for rewriting existing Issue body |
| `--from-file` also | `issues update` (metadata + body bulk update) | Round-trip: `--to-file` → edit → `--from-file` |

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
| `issues create` / `issues update` | `title`, `type`, `priority`, `size`, `labels` |
| `pr create` | `title`, `base`, `head` |
| `discussions create` | `title`, `category` |

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
  Icebox --> Backlog --> Preparing --> Designing --> SpecReview[Spec Review] --> InProgress[In Progress]
  InProgress --> Review --> Testing --> Done --> Released
  InProgress <--> Pending["Pending (blocked)"]
```

| Status | Description |
|--------|-------------|
| Icebox | Low priority, not yet planned |
| Backlog | Planned for future work |
| Preparing | Plan being created |
| Designing | Design being created |
| Spec Review | Requirements being reviewed |
| In Progress | Currently working on |
| Pending | Blocked (document reason) |
| Review | Code review |
| Testing | QA testing |
| Done | Completed |
| Released | Deployed to production |

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
