# Skill / Agent Worker Completion Pattern

Common flow executed by all orchestrators after a Skill (Skill tool) or Agent Worker (Agent tool) completes.

## Skill Tool Completion Pattern

Skills invoked via Skill tool (main context) — `review-issue`, `analyze-issue`, `plan-issue`, `reviewing-claude-config` — run in the same context as the main AI. Post-completion handling follows these rules:

| Skill | Completion Handling |
|-------|-------------------|
| `plan-issue` | If no errors, proceed to next step (review) |
| `review-issue` | Output contains `**Review result:** PASS` / `NEEDS_REVISION` / `FAIL`. Orchestrator uses this string for determination |
| `analyze-issue` | Output contains `**Review result:** PASS` / `NEEDS_REVISION`. Orchestrator uses this string for determination |
| `reviewing-claude-config` | Output contains `**Review result:** PASS` / `FAIL`. Orchestrator uses this string for determination |

**No YAML parsing needed**. Skill tools complete within the main context, so structured data communication is not used.

## Agent Tool Completion Pattern

Workers invoked via Agent tool (subagent) — `coding-worker`, `commit-worker`, `pr-worker`, `research-worker` — run in a separate process and return structured data in YAML frontmatter format.

### Extended Structured Data Schema

In addition to the base fields (`action`, `next`, `status`, `ref`, `comment_id`), the following fields are added:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `ucp_required` | No | boolean | Set to `true` when the worker requires user judgment |
| `suggestions_count` | No | number | Number of improvement suggestions. 0 or omitted means no suggestions |
| `followup_candidates` | No | string[] | List of follow-up Issue candidates |
| `changes_made` | Conditional | boolean | `coding-worker` only. Whether file changes occurred. When `false`, `implement-flow` skips commit / PR / finalize-changes and proceeds to the no-changes chain |

### Complete Field Definitions

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `action` | Yes | `CONTINUE` / `STOP` | Behavioral directive for orchestrator (first field) |
| `next` | Conditional | skill name | Skill to invoke when `action: CONTINUE` |
| `status` | Yes | `SUCCESS` / `FAIL` | Result state |
| `ref` | Conditional | GitHub reference | Human-readable reference when GitHub write occurred |
| `comment_id` | Conditional | numeric (database_id) | Only when a comment was posted. For reply-to / edit |
| `ucp_required` | No | boolean | Set to `true` when the worker requires user judgment |
| `suggestions_count` | No | number | Number of improvement suggestions |
| `followup_candidates` | No | string[] | Follow-up Issue candidates |
| `changes_made` | Conditional | boolean | `coding-worker` only. Whether file changes occurred (see "No-Changes Branch" below) |

### No-Changes Branch (`coding-worker` only)

`coding-worker` must always return the `changes_made` field on completion:

- `changes_made: true` — file changes occurred. Proceed to the normal chain (`commit-worker` → `pr-worker` → `finalize-changes` → Work Summary → Status=Review)
- `changes_made: false` — no file changes (already implemented, spec-correct, cannot reproduce, etc.). `implement-flow` skips commit / PR / `finalize-changes` and proceeds to the no-changes chain

See the "No-Changes Path" section in [chain-end-steps.md](chain-end-steps.md) for details on the no-changes chain.

The `Summary` field is abolished. Instead, the **body's first line** is treated as the summary.

### Unified Processing Flow

After receiving Agent tool output, all orchestrators execute the following common flow:

```text
Agent Worker completes → Parse YAML frontmatter
  → action = STOP → Stop chain, report to user
  → action = CONTINUE →
    → [coding-worker only] changes_made = false →  (highest priority: evaluated before UCP)
      → Branch to no-changes chain (see chain-end-steps.md)
      → ucp_required / suggestions_count are ignored on this path
        (the no-changes path already confirms status via AskUserQuestion,
         so UCP would be redundant)
    → ucp_required = true OR suggestions_count > 0 →
      → Present to user via AskUserQuestion
        - suggestions_count > 0: Reference Suggestions posted by worker in Issue comment and display
        - followup_candidates: Propose follow-up Issue candidates
      → After user approval, proceed to next step
    → ucp_required = false AND suggestions_count = 0 →
      → Immediately proceed to next step
```

> **Priority rule**: `changes_made: false` is evaluated **before the UCP check**. The no-changes chain already confirms status via AskUserQuestion in `chain-end-steps.md`, so stacking another UCP on top would cause a double confirmation. When `changes_made: false`, ignore `ucp_required` / `suggestions_count` and proceed directly to the no-changes path.

### Output Parse Checkpoint

On receiving Agent tool output, execute these checks in order:

1. **Extract YAML frontmatter** (block delimited by `---`)
2. **action field**: Read `action` → STOP/CONTINUE determines the next behavior
3. **status field**: Read `status` → log for record
4. **changes_made check** (`coding-worker` only): If `changes_made: false` → branch to no-changes chain (ignore `next` field and UCP). **Evaluated before the UCP check**
5. **UCP check** (only when `changes_made` is not `false`): If `ucp_required` or `suggestions_count > 0` → present to user via AskUserQuestion
6. **Body first line**: Extract the first line of the body after frontmatter → one-line summary
7. **action = CONTINUE with no UCP and changes_made != false**: Immediately invoke the skill in the `next` field

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

### Skill Tool Skills (No YAML Parsing)

| Orchestrator | Skill | Completion Handling | Next Step |
|--------------|-------|-------------------|-----------|
| prepare-flow | plan-issue | No errors → success | → analyze-issue |
| prepare-flow | analyze-issue (plan) | `**Review result:** PASS` / `NEEDS_REVISION` | → status update or revision loop |
| design-flow | design skill group | No errors → success | → analyze-issue |
| design-flow | analyze-issue (design) | `**Review result:** PASS` / `NEEDS_REVISION` | → visual evaluation or completion |
| review-flow | review-issue (code) | `**Review result:** PASS` / `FAIL` | → thread response |

### Agent Tool Workers (YAML Parsing Required)

| Orchestrator | Worker | Next Step |
|--------------|--------|-----------|
| implement-flow | coding-worker | `changes_made: true` → commit-worker / `changes_made: false` → no-changes chain |
| implement-flow | commit-worker | → pr-worker |
| implement-flow | pr-worker | → manager-managed steps |
| review-flow | coding-worker (fixes) | → commit-worker |
| review-flow | commit-worker | → reply and resolve |
