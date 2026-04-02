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

Default recommended chain target after creation:

| Condition | Default Recommendation | Reason |
|-----------|----------------------|--------|
| Size XS/S and requirements are clear (pattern replacement, type fix, rename, etc.) | `/implement-flow` (start immediately) | Small task that needs no planning |
| Size M+ or requirements ambiguous | `/review-issue plan` (review then plan) | Review ensures requirements and spec alignment |
| User explicitly says "work on it now" | `/implement-flow` | Explicit intent |
| User explicitly says "plan this" | `/prepare-flow` | Explicit intent |
| Issue created from in-conversation problem | Follow default recommendation above, confirm | Context is warm, can start immediately |
| Batch creation (multiple issues in sequence) | Place in Backlog | Individual work is inefficient |
| Priority: Low | Place in Backlog | Not urgent |
| Priority: Critical/High | Follow Size-based default above (XS/S → `/implement-flow`, M+ → `/review-issue plan`) | High urgency, Size determines path |

### Requirements Clarity Criteria

"Requirements are clear" means:

- The change target is specifically identified (e.g., "change this function to X", "fix the wording in this rule")
- Completes as a mechanical transformation (pattern replacement, type fix, rename, format change)
- No ambiguity in implementation scope

"Requirements unclear" — recommend `/review-issue plan` when:

- Only "I want to improve X" with no concrete change specified
- Multiple implementation approaches are possible
- Impact scope is not clear

## Review Execution Conditions

Cases where review (`/review-issue plan`) is recommended after item creation, before proceeding to `prepare-flow` / `implement-flow`:

| Condition | Recommend Review | Reason |
|-----------|-----------------|--------|
| Size M or larger | Yes | Broad impact scope — verify requirements and spec alignment first |
| Requirements are ambiguous | Yes | Validate requirements before planning |
| Significant impact on existing specs | Yes | Detect breaking changes and broad impact via review |
| Size XS/S and requirements clear | No | Mechanical transformation, review unnecessary |
| User explicitly skips | No | Respect user intent |

**Purpose of review**: A gate before planning (`prepare-flow`) to verify that the item's requirements align with existing project specs and have no conflicts. The `review-issue` plan role evaluates requirements coverage, impact scope, and risks.

**Post-review flow**: After `/review-issue plan #{number}` completes, the user proceeds to `/prepare-flow #{number}` or `/implement-flow #{number}` based on the review findings. The chain does not auto-execute — the user selects the next action.

## Backlog-Only Path

Keep in Backlog without chaining when:

- User explicitly says "later" or "not now"
- During batch issue creation
- Another issue is currently In Progress (WIP limit)

## Relationship with `implement-flow` Step 1a

When `implement-flow` is invoked with text description only (no issue number), Step 1a calls `creating-item`. `creating-item` creates the Issue and returns the number, and `implement-flow` continues. In this case, chain decision is not needed (as `implement-flow` automatically continues).

> **Note:** The chain from `creating-item` delegates to `implement-flow`. `implement-flow` evaluates the issue size and plan state — XS/S without planning proceeds directly to `code-issue`, while M+ delegates to `prepare-flow`. For M+ or ambiguous requirements, `creating-item` recommends `/review-issue plan` before proceeding to planning/implementation.
