# Item Body Maintenance — Detailed Procedures

For Issues / Discussions / PRs. Supplements the overview in the `project-items` rule.

## Contents

- When to Update
- How to Update
- File-Based Body Editing
- Workflow Order (Comment First)
- Updating Body from Review Results
- Guidelines

## When to Update

| Trigger | Action |
|---------|--------|
| New findings or corrections added via comments | Consolidate into body |
| Investigation results posted as comments | Merge into body's relevant section |
| Requirements changed via comments | Update body's Tasks/Deliverable sections |
| Decision made in comment thread | Record in body |
| 3+ comments accumulated since last body update | Consolidate into body |

## How to Update

```bash
# Issues
shirokuma-docs issues update {number} --body-file /tmp/shirokuma-docs/{number}-body.md

# Discussions
shirokuma-docs discussions update {number} --body-file /tmp/shirokuma-docs/{number}-body.md
```

## File-Based Body Editing

### Temp File Naming Convention

| Timing | Pattern | Example |
|--------|---------|---------|
| After number assigned | `/tmp/shirokuma-docs/{number}-body.md` | `42-body.md` |
| After number (purpose-specific) | `/tmp/shirokuma-docs/{number}-{purpose}.md` | `42-review-summary.md` |
| Before number assigned | `/tmp/shirokuma-docs/{slug}-body.md` | `add-format-option-body.md` |
| Not tied to an issue | `/tmp/shirokuma-docs/{purpose}.md` | `handover.md` |

### Write/Edit Workflow

| Operation | Tool | Condition |
|-----------|------|-----------|
| Initial creation | Write | File does not exist |
| Partial update | Read + Edit | File exists, only partial changes |
| Full rewrite | Write | Structure changes significantly |

**Decision criteria**: Use Read + Edit when 2+ iterative updates are expected. Use Write for one-time updates.

Always pass the file name to the CLI (`--body-file /tmp/shirokuma-docs/{number}-body.md`). Inlining the full body via heredoc on every update is discouraged for Tier 2 operations.

> See `github-operations.md` for `--body-file` tier guide. Tier 1 (stdin) is for comments/replies with no iterative updates; Tier 2 (file) is where this pattern applies.

## Workflow Order (Comment First)

### Why Comment First

The purpose of the comment-first principle is to preserve AI's **thinking process as a primary record**.

- **Judgment error analysis**: Without recorded thinking, it is impossible to retroactively analyze why a wrong decision was made
- **Evolution loop input source**: Evolution signals in the `rule-evolution` rule are detected from decision rationale and investigation results recorded in comments. The body alone captures "what was done" but loses "why it was done"
- **Hallucination detection**: By comparing the reasoning process recorded in comments with actual results, detection and correction of AI's incorrect assumptions or reasoning becomes possible

### Order

When updating a body, ALWAYS follow this order:

1. **Record thinking process as a comment** — Record decision rationale, investigation results, alternatives considered — the "why" — as a primary record
2. **Consolidate into body** — Structure the comment content and integrate it into the relevant body section

**Prohibited**: Updating the body directly and then adding a comment after the fact (reverse order). Updating the body without any comment.

### Comment Content Requirements

Merely following the comment→body order is not enough. Comments must have **independent value as primary records** of the work.

**Heuristic**: If deleting a comment would not lose any information absent from the body, that comment is not substantive.

**Content that should be primary records in comments**:
- Decision rationale and alternatives considered
- Facts discovered during investigation
- Summary of review findings
- Reasons for requirement changes

**When consolidating into body**: Structure and merge comment content into relevant sections. Comments remain as historical record.

### Anti-Patterns

| Bad (Formal compliance) | Good (Substantive compliance) |
|------------------------|-------------------------------|
| "Plan created. See body for details." | "Selected approach A. Also considered B (reason), rejected due to X." |
| "Updated issue body." | "Investigation found module X is also affected. Added to tasks." |
| "Reflected review results." | "Review detected N issues: {summary of specific findings}" |

## Updating Body from Review Results

When `review-issue` posts review results as PR comments or Issue comments, and a caller skill needs to update the body accordingly.

### Procedure

1. **Confirm review comment is already posted** — `review-issue` Step 6 has completed comment posting
2. **Consolidate into relevant body sections** — Update task lists or add new sections based on review results

### Examples

| Scenario | Comment (already posted) | Body consolidation |
|----------|------------------------|-------------------|
| Missing task found in review | "Review detected X processing is not implemented. Adding to tasks." | Add `- [ ] Add X processing` to tasks section |
| Security finding | "Security review found 2 auth check gaps: {specific locations}" | Add fix tasks to tasks section |
| Plan review improvement | "Plan review noted impact on module A is missing from the plan." | Add to changed files in plan section |

### Notes

- `review-issue` runs as an Agent tool (subagent), so it only posts comments and does not update bodies
- Body updates are the responsibility of caller skills (`create-pr-issue`, `working-on-issue`)
- **PASS case**: The review comment itself serves as the primary record, so no additional comment is needed (the review comment = the "comment" in comment-first)

## Guidelines

1. **Preserve structure** — Keep the original body template sections
2. **Update task checkboxes** — Check completed items, add new tasks discovered
3. **Summarize, don't duplicate** — Consolidate comment threads into concise body updates
4. **Comment first** — Always post a comment before updating the body (see Workflow Order above)
