# Chain Decision Rules

## Issue Type Inference

Issue Type follows the type determination table in `managing-github-items`'s `reference/create-item.md`.

| Keyword | Type |
|---------|------|
| feature, new feature, implement, add | Feature |
| bug, defect, fix | Bug |
| refactoring, config change, tooling, chore | Chore |
| documentation, README, docs | Docs |
| research, investigation | Research |
| evolution, signal, evolve, rule improvement | Evolution |

## Priority / Size Inference

Follow `managing-github-items`'s `reference/create-item.md`.

## Chain Decision

Default recommended chain target after creation (3-way branching based on `review-issue requirements` result):

| Condition | Default Recommendation | Reason |
|-----------|----------------------|--------|
| `review-issue requirements` result is `**Design assessment:** NEEDED` | `/design-flow #{issue-number}` | Design phase is required before planning |
| Design NOT_NEEDED + Size M+ or requirements ambiguous | `/prepare-flow #{issue-number}` | Go to planning phase |
| Design NOT_NEEDED + Size XS/S and requirements clear | `/implement-flow #{issue-number}` | Implement directly |
| User explicitly skips | `/implement-flow` or `/prepare-flow` | Explicit intent |
| Batch creation (multiple issues in sequence) | Place in Backlog | Individual work is inefficient |
| Priority: Low | Place in Backlog | Not urgent |

### Requirements Clarity Criteria

"Requirements are clear" means:

- The change target is specifically identified (e.g., "change this function to X", "fix the wording in this rule")
- Completes as a mechanical transformation (pattern replacement, type fix, rename, format change)
- No ambiguity in implementation scope

"Requirements unclear" — recommend `/review-issue requirements` when:

- Only "I want to improve X" with no concrete change specified
- Multiple implementation approaches are possible
- Impact scope is not clear

## Review Execution Conditions

After Issue creation, `create-item-flow` Step 2b **automatically runs** `review-issue requirements` (skipped for Discussion).

| Condition | Auto-execute | Reason |
|-----------|--------------|--------|
| Issue creation (regardless of Size or requirements) | **Always yes** | Verify requirement quality immediately after creation and determine design assessment at the same time |
| Discussion creation | No | Discussions are out of scope; only next action candidates are presented |
| During batch creation | No | Prioritize Backlog placement over individual reviews during bulk creation |

**Purpose of review**: A quality gate for Issue body requirements, specs, and design necessity before planning (prepare-flow) or design (design-flow). The `review-issue` requirements role evaluates completeness, clarity, implementability, and design assessment.

**Post-review flow (3-way branching)**: After `review-issue requirements` completes, Step 2b results (`**Design assessment:**` and `**Review result:**`) automatically branch in 3 directions:

- Design needed (`**Design assessment:** NEEDED`) → `/design-flow #{issue-number}`
- Design not needed + planning needed (`**Design assessment:** NOT_NEEDED` and Size M+ or ambiguous) → `/prepare-flow #{issue-number}`
- Design not needed + planning not needed (`**Design assessment:** NOT_NEEDED` and Size XS/S and clear) → `/implement-flow #{issue-number}`

## Backlog-Only Path

Keep in Backlog without chaining when:

- User explicitly says "later" or "not now"
- During batch issue creation
- Another issue is currently In Progress (WIP limit)

## Relationship with `implement-flow` Step 1a

When `implement-flow` is invoked with text description only (no issue number), Step 1a calls `create-item-flow`. `create-item-flow` creates the Issue and returns the number, and `implement-flow` continues. In this case, chain decision is not needed (as `implement-flow` automatically continues).

> **Note:** When design assessment (`review-issue requirements`) returns NEEDED, `create-item-flow` guides to `/design-flow` first. After design completion, the chain proceeds to `/prepare-flow` → `/implement-flow`.
