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
| Size XS/S and requirements are clear (pattern replacement, type fix, rename, etc.) | `/working-on-issue` (start immediately) | Small task that needs no planning |
| Size M or larger | `/preparing-on-issue` (create a plan first) | Planning ensures quality |
| User explicitly says "work on it now" | `/working-on-issue` | Explicit intent |
| User explicitly says "plan this" | `/preparing-on-issue` | Explicit intent |
| Issue created from in-conversation problem | Follow default recommendation above, confirm | Context is warm, can start immediately |
| Batch creation (multiple issues in sequence) | Place in Backlog | Individual work is inefficient |
| Priority: Low | Place in Backlog | Not urgent |
| Priority: Critical/High | Follow Size-based default above (XS/S → `/working-on-issue`, M+ → `/preparing-on-issue`) | High urgency, Size determines path |

### Requirements Clarity Criteria

"Requirements are clear" means:

- The change target is specifically identified (e.g., "change this function to X", "fix the wording in this rule")
- Completes as a mechanical transformation (pattern replacement, type fix, rename, format change)
- No ambiguity in implementation scope

"Requirements unclear" — recommend `preparing-on-issue` when:

- Only "I want to improve X" with no concrete change specified
- Multiple implementation approaches are possible
- Impact scope is not clear

## Backlog-Only Path

Keep in Backlog without chaining when:

- User explicitly says "later" or "not now"
- During batch issue creation
- Another issue is currently In Progress (WIP limit)

## Relationship with `working-on-issue` Step 1a

When `working-on-issue` is invoked with text description only (no issue number), Step 1a calls `creating-item`. `creating-item` creates the Issue and returns the number, and `working-on-issue` continues. In this case, chain decision is not needed (as `working-on-issue` automatically continues).

> **Note:** The chain from `creating-item` delegates to `working-on-issue`. `working-on-issue` evaluates the issue size and plan state — XS/S without planning proceeds directly to `code-issue`, while M+ delegates to `preparing-on-issue`.
