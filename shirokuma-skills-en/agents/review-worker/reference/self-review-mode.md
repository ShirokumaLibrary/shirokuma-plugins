# Self-Review Mode Reference

Behavioral specification when review-worker is launched with the `self-review #{number}` argument.

## State Transitions

```text
[REVIEW] Execute reviewing-on-issue / reviewing-claude-config (Agent tool unavailable → execute skill steps directly)
    ↓  Post PR comment before returning structured data
[PARSE] Parse YAML frontmatter + PASS/NEEDS_FIX/FAIL determination
    ↓
  ├── PASS → [COMPLETE]
  ├── NEEDS_FIX (Auto-fixable: yes) → [FIX]
  └── FAIL (Auto-fixable: no) → [COMPLETE] (return as FAIL)

[FIX] Fix based on findings directly (using Read/Edit tools) → git add → git commit → git push
    ↓
[CONVERGE] Convergence check
    ↓
  ├── Progress → [REVIEW] (re-review)
  ├── Not converging → [COMPLETE] (report remaining issues)
  └── Safety limit (5) → [COMPLETE] (report remaining issues)

[COMPLETE] Create out-of-scope Issues → Classify recommendations → Plan-gap determination → Post response complete comment → Return final output
```

## File Category Detection

Get changed files via `git diff --name-only develop..HEAD` and classify:

| Category | Condition |
|----------|-----------|
| config | Files under `.claude/skills/`, `.claude/rules/`, `.claude/agents/`, `.claude/output-styles/`, `.claude/commands/`, `plugin/` |
| code | `.ts`, `.tsx`, `.js`, `.jsx` files |
| docs | `.md` files (excluding config paths above) |

### Review Routing

| File Composition | Review Method |
|-----------------|---------------|
| config only | Execute `reviewing-claude-config` steps directly (fall back to docs role if not injected as skill) |
| code/docs only (no config) | Execute `reviewing-on-issue` steps directly |
| mixed (config + code/docs) | Execute `reviewing-on-issue` → `reviewing-claude-config` sequentially → merge results |

**Important**: review-worker is a sub-agent, so Agent tool and Skill tool cannot be used internally. `reviewing-on-issue` is injected via the `skills` frontmatter, so execute its 6-step procedure (Role Selection → Knowledge Loading → Lint → Analysis → Report Generation → Report Saving) directly.

### Result Merging Rules (Mixed Case)

- Status: either FAIL → FAIL; either NEEDS_FIX (and no FAIL) → NEEDS_FIX; both PASS → PASS
- Critical: sum of both
- Fixable-warning: sum of both
- Out-of-scope: sum of both
- Files with issues: merge
- Auto-fixable: either no → no
- Out-of-scope items: merge

## Direct Fix Execution

When fixes are needed, review-worker fixes directly using Read/Edit/Bash tools (does NOT use `Task(general-purpose)`).

### Fix Procedure

1. Identify files for each finding in `### Detail`
2. Read file with Read tool
3. Apply fix with Edit tool
4. Stage with `git add`
5. Commit and push

### Commit Message

```
fix: address self-review findings [iter {n}] (#{issue-number})
```

### When Fix Is Not Possible

Unfixable findings are reported as remaining issues in [COMPLETE].

## Convergence Check Logic

Compare the total count of `critical + fixable-warning` against the previous iteration.

| State | Logic | Action |
|-------|-------|--------|
| Total decreased from previous | Progress | Continue |
| Total same as previous | Grace period | Continue once (fix may have introduced different issues) |
| Total not decreased for 2 consecutive iterations | Not converging | Proceed to [COMPLETE] (report remaining) |
| Total increased from previous | Worsening | Immediately proceed to [COMPLETE] |
| Total = 0 | Complete | PASS |
| Safety limit (5) reached | Failsafe | Proceed to [COMPLETE] |

**Safety limit rationale (5 iterations)**: Up to 2 for critical fixes + up to 2 for fixable-warning fixes + 1 buffer.

**Safety limit fallback**: Convert remaining fixable-warnings to follow-up Issues.

## Recommendations Classification Logic

Extract recommendations from the review report at PASS determination (or convergence completion) and classify into 4 categories:

| Classification | Example | Action |
|---------------|---------|--------|
| `[rule]` | "Use exported types from external libraries when available" | Record as Evolution signal |
| `[trigger:{condition}]` | "Re-evaluate on major update" | Create follow-up Issue |
| `[one-off]` | "Refactor this function to abstract the pattern" | Create follow-up Issue |
| `[trivial]` | "Narrow the type" (2-line change) | Propose immediate fix |

When classification is ambiguous, fall back to `[one-off]`.

## Plan-Gap Determination Logic

Cross-reference out-of-scope items with the Issue body's purpose and scope description.

### Procedure

1. Fetch Issue body via `shirokuma-docs show {number}` (extract Issue number from the `self-review #{number}` argument)
2. Extract `## Purpose` / `## Summary` sections (or `## 目的` / `## 概要` for JA)
3. For each out-of-scope item, cross-reference:

| Condition | Sub-classification |
|-----------|-------------------|
| Outside PR scope but within Issue scope | `[plan-gap]` (improvement material for planning-on-issue) |
| Outside PR scope and outside Issue scope | `[true-out-of-scope]` (create follow-up Issue) |

## PR Comment Posting

### Review Result Comment (Each Iteration)

Follow reviewing-on-issue Step 6 to post a review summary as a PR comment for each iteration. Since review-worker executes skill steps directly, Step 6 comment posting is also executed directly.

### Response Complete Comment

review-worker posts the response complete comment to the PR in the [COMPLETE] state.

```bash
shirokuma-docs issues comment {PR#} --body-file /tmp/shirokuma-docs/{number}-review-response.md
```

**Template (no fixes — PASS):**

```markdown
## Self-Review Response Complete

**Fixed:** None (no issues detected)
```

**Template (fixes applied — PASS):**

```markdown
## Self-Review Response Complete

**Iterations:** {n}
**Fixed:** {critical} critical, {fixable-warning} warning

### Fix List
| File | Fix Description | Classification | Commit |
|------|----------------|----------------|--------|
| `path/to/file.ts` | {fix description} | critical | {short-hash} |

[If follow-up Issues exist:]
### Follow-up Issues
- #{follow-up-number}: {title} (out-of-scope)
```

**Template (cannot converge):**

```markdown
## Self-Review Response Complete (Not Converged)

**Iterations:** {n}
**Unresolved:** {critical} critical, {fixable-warning} warning

### Remaining Issues
- {issue description}

Manual review and fixes required.
```

## Out-of-Scope Follow-up Issue Creation

After self-review loop completion, if the final iteration's structured data contains `Out-of-scope items` with `[true-out-of-scope]` entries, create follow-up Issues. `[plan-gap]` items do not create Issues — they are returned as a plan-gap count in the final output.

**Deduplication**: Only use the out-of-scope list from the final iteration.

```bash
shirokuma-docs issues create --from-file /tmp/shirokuma-docs/{number}-out-of-scope.md \
  --field-status "Backlog"
```

**Conditional execution**: Skip if `[true-out-of-scope]` count is 0.

## Review Findings Comment Verification

In [COMPLETE] processing, verify that Step 6 PR comment posting was completed.

### Verification Procedure

```bash
shirokuma-docs issues comments {PR#}
```

### Fallback

If review findings comments are missing:

1. Display warning
2. Post a simplified comment from the structured data summary:

```markdown
## Self-Review Findings (Fallback)

**Status:** {PASS | FAIL}
**Critical:** {n} / **Fixable-warning:** {n} / **Out-of-scope:** {n}

> This comment was auto-generated from the subagent output summary because the review skill's Step 6 was not executed.
```

## Final Output Template

Detailed version of the template defined in AGENT.md. Returned to the caller after all [COMPLETE] processing is done:

```yaml
---
action: {CONTINUE | STOP}
status: {PASS | NEEDS_FIX_RESOLVED | FAIL}
ref: "PR #{pr-number}"
---

{one-line result summary}

### Self-Review Result
**Iterations:** {n}
**Fixed:** {critical} critical, {fixable-warning} warning
**Remaining:** {critical} critical, {fixable-warning} warning
**Out-of-scope:** {n} ({plan-gap} plan-gap, {true-out-of-scope} true-out-of-scope)
**Follow-up Issues:** #{issue1}, #{issue2}

### Recommendations
- [rule] {pattern}: {description}
- [trigger:{condition}] {description}
- [one-off] {description}
- [trivial] {description} ({change size})

### Response Complete Comment
**comment_id:** {database-id}
```

**Status → Action mapping:**

| Status | Action | Description |
|--------|--------|-------------|
| PASS | CONTINUE | No issues, or out-of-scope only |
| NEEDS_FIX_RESOLVED | CONTINUE | Issues found but all auto-fixed |
| FAIL | STOP | Non-auto-fixable issues remain |
