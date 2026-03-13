# Worker Completion Pattern

Common flow executed by all orchestrators after a worker / skill completes.

## Extended Structured Data Schema

In addition to the base fields (`action`, `next`, `status`, `ref`, `comment_id`), the following fields are added:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `ucp_required` | No | boolean | Set to `true` when the worker requires user judgment |
| `suggestions_count` | No | number | Number of improvement suggestions. 0 or omitted means no suggestions |
| `followup_candidates` | No | string[] | List of follow-up Issue candidates |

### Complete Field Definitions

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `action` | Yes | `CONTINUE` / `STOP` / `REVISE` | Behavioral directive for orchestrator (first field) |
| `next` | Conditional | skill name | Skill to invoke when `action: CONTINUE` |
| `status` | Yes | `SUCCESS` / `PASS` / `NEEDS_FIX` / `FAIL` / `NEEDS_REVISION` | Result state |
| `ref` | Conditional | GitHub reference | Human-readable reference when GitHub write occurred |
| `comment_id` | Conditional | numeric (database_id) | Only when a comment was posted. For reply-to / edit |
| `ucp_required` | No | boolean | Set to `true` when the worker requires user judgment |
| `suggestions_count` | No | number | Number of improvement suggestions |
| `followup_candidates` | No | string[] | Follow-up Issue candidates |

The `Summary` field is abolished. Instead, the **body's first line** is treated as the summary.

## Unified Processing Flow

After receiving subagent output, all orchestrators execute the following common flow:

```text
worker / skill completes → Parse YAML frontmatter
  → action = STOP → Stop chain, report to user
  → action = CONTINUE →
    → ucp_required = true OR suggestions_count > 0 →
      → Present to user via AskUserQuestion
        - suggestions_count > 0: Reference Suggestions posted by worker in Issue comment and display
        - followup_candidates: Propose follow-up Issue candidates
      → After user approval, proceed to next step
    → ucp_required = false AND suggestions_count = 0 →
      → Immediately proceed to next step
```

### Output Parse Checkpoint

On receiving subagent output, execute these checks in order:

1. **Extract YAML frontmatter** (block delimited by `---`)
2. **action field**: Read `action` → STOP/REVISE/CONTINUE determines the next behavior
3. **status field**: Read `status` → log for record
4. **UCP check**: If `ucp_required` or `suggestions_count > 0` → present to user via AskUserQuestion
5. **Body first line**: Extract the first line of the body after frontmatter → one-line summary
6. **action = CONTINUE with no UCP**: Immediately invoke the skill in the `next` field

### UCP Presentation Template

```markdown
**Worker result:** {status}

{If suggestions_count > 0:}
### Improvement Suggestions ({suggestions_count} items)
Please review the comment posted by the worker at #{ref}.

{If followup_candidates exist:}
### Follow-up Candidates
- {candidate}

Would you like to proceed?
```

## Application Points

| Orchestrator | Worker / Skill | Next Step |
|--------------|---------------|-----------|
| preparing-on-issue | planning-worker | → review-worker |
| preparing-on-issue | review-worker (plan) | → status update |
| designing-on-issue | design skill group | → review-worker |
| designing-on-issue | review-worker (design) | → visual evaluation or completion |
| working-on-issue | coding-worker | → commit-worker |
| reviewing-on-pr | review-worker (code) | → thread response |
| reviewing-on-pr | coding-worker (fixes) | → commit-worker |

## Status → Action Mapping

| Status | Action | Used By | Chain Behavior |
|--------|--------|---------|----------------|
| SUCCESS | CONTINUE | commit-issue, create-pr-issue, code-issue | Proceed to next step |
| PASS | CONTINUE | review-issue | Proceed to next step (Suggestions presented via UCP) |
| NEEDS_FIX | FIX | code-issue | Test fix loop (TDD cycle) |
| FAIL | STOP | All subagent skills | Chain stop, report to user |
| NEEDS_REVISION | REVISE | review-issue (plan/design review) | Enter revision loop |
