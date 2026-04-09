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
| Normal (regardless of Size or requirements) | `/review-issue requirements` (review first) | Always verify requirements and spec quality |
| User explicitly says "work on it now" | `/implement-flow` | Explicit intent |
| User explicitly says "plan this" | `/prepare-flow` | Explicit intent |
| Issue created from in-conversation problem | `/review-issue requirements` (default) | Verify quality while context is warm |
| Batch creation (multiple issues in sequence) | Place in Backlog | Individual work is inefficient |
| Priority: Low | Place in Backlog | Not urgent |
| Priority: Critical/High | `/review-issue requirements` → `/implement-flow` | Verify requirements even for urgent tasks |

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

Cases where review (`/review-issue requirements`) is recommended after item creation, before proceeding to `prepare-flow` / `implement-flow`:

| Condition | Recommend Review | Reason |
|-----------|-----------------|--------|
| Normal (regardless of Size or requirements) | **Always yes** | Verifying requirements immediately after creation is best practice |
| User explicitly skips | No | Respect user intent |
| During batch creation | No | Prioritize Backlog placement over individual reviews during bulk creation |

**Purpose of review**: A gate before planning (`prepare-flow`) to verify the quality of the Issue body's requirements and specs. The `review-issue` requirements role evaluates completeness, clarity, and implementability.

**Post-review flow**: After `/review-issue requirements #{number}` completes, the user proceeds to `/prepare-flow #{number}` or `/implement-flow #{number}` based on the review findings. The chain does not auto-execute — the user selects the next action.

## Backlog-Only Path

Keep in Backlog without chaining when:

- User explicitly says "later" or "not now"
- During batch issue creation
- Another issue is currently In Progress (WIP limit)

## Relationship with `implement-flow` Step 1a

When `implement-flow` is invoked with text description only (no issue number), Step 1a calls `create-item-flow`. `create-item-flow` creates the Issue and returns the number, and `implement-flow` continues. In this case, chain decision is not needed (as `implement-flow` automatically continues).

> **Note:** The chain from `create-item-flow` delegates to `implement-flow`. `implement-flow` evaluates the issue size and plan state — XS/S without planning proceeds directly to `code-issue`, while M+ delegates to `prepare-flow`. For M+ or ambiguous requirements, `create-item-flow` recommends `/review-issue requirements` before proceeding to planning/implementation.
