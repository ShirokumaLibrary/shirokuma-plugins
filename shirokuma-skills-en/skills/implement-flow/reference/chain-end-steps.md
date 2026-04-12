# Chain End Steps Reference

Details of the final steps executed at the end of the `implement-flow` chain.

## Work Summary (Issue Comment)

After PR creation, post a technical work summary to the Issue as a comment. This is the primary context record referenced in future conversations for Issue context.

The work summary focuses on **technical work details** — what was changed, which files were modified, and technical decisions made.

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-work-summary.md
```

Where `/tmp/shirokuma-docs/{number}-work-summary.md` contains:

```markdown
## Work Summary

### Changes
{What was implemented or fixed — technical details}

### Modified Files
- `path/file.ts` - {Change description}

### Pull Request
PR #{pr-number}

### Technical Decisions
- {Decision and rationale}
```

Skip this step if no issue number is associated with the work.

**Standalone completion**: When `implement-flow` completes its chain (standalone or within a session), the Work Summary is automatically posted.

## Status Update (End of Chain)

**IMPORTANT**: Do NOT update Status to Review at PR creation time. The `finalize-changes` post-processing step must complete first. Update Status only after work summary is posted.

Update Status to Review for issues with a number:

```bash
shirokuma-docs items transition {number} --to Review
```

**Status fallback verification**: After chain completion, if the transition was skipped or failed, run `shirokuma-docs items transition {number} --to Review` again (idempotent: re-updating to Review when already Review is harmless).

## Plan Issue Done Update (End of Chain)

After the Status update, update the plan issue to Done if one exists.

**Top-level issue case** (no parent issue):
Identify the plan issue from the `subIssuesSummary` of the issue fetched in Step 1 — look for a child issue whose title starts with "Plan:" or "計画:".

**Sub-issue case** (has a parent issue):
Re-run `shirokuma-docs items context {parent-number}` at the end of the chain to get the latest `subIssuesSummary` (other sub-issue statuses may have changed during chain execution). Look for a sibling issue whose title starts with "Plan:" or "計画:".

**Epic case** (parent issue has multiple work sub-issues):
Similarly, re-fetch the parent issue at the end of the chain to use the latest `subIssuesSummary`. Only update the plan issue to Done if all work sub-issues (excluding the plan issue itself) have a status of Done or Cancelled. If any work sub-issue remains in another status, skip the update.

**Plan issue update procedure**:

```bash
shirokuma-docs items transition {plan-number} --to Done
```

- **Pull skip condition**: For the top-level issue case, the plan issue was already fetched in Step 1 — proceed directly to Step 2 (frontmatter edit) and Step 3 (push). For sub-issue / epic cases, pull is required since the plan issue was not pre-fetched.
- **Plan issue not found**: Silent skip (no warning). Covers cases like XS/S direct implementation path where no plan issue exists.
- **Idempotent**: Re-updating to Done when already Done is harmless.

## Next Steps Suggestion (End of Chain)

After Status update, present next action candidates to the user. Extract the PR number from `open-pr-issue`'s output to provide specific guidance. If the PR number is unavailable (e.g., PR not created), omit the `/review-flow` line.

```
## Next Steps

- `/review-flow #{pr-number}` — Run self-review on the PR
```

## No-Changes Path (when `coding-worker` completes with `changes_made: false`)

When `coding-worker` returns `changes_made: false`, skip the normal chain (commit → PR → finalize-changes) and execute the following procedure.

### No-Changes Work Summary

Since no PR exists, use a dedicated template that omits the `### Pull Request` section. Record as an investigation result ("already implemented", "spec-correct", "cannot reproduce", etc.).

```bash
shirokuma-docs items add comment {number} --file /tmp/shirokuma-docs/{number}-no-changes-summary.md
```

Where `/tmp/shirokuma-docs/{number}-no-changes-summary.md` contains:

```markdown
## Work Summary (No Changes)

### Investigation Result
{What coding-worker confirmed — why no change was needed}

### Determination
{e.g., Already implemented, Spec-correct, Cannot reproduce, etc.}

### Files Examined
- `path/file.ts` - {What was checked}

### Technical Decisions
- {Decision and rationale}
```

### Status Determination for No Changes

When the chain ends with no changes, there is no code change or PR, so the issue cannot progress from `In Progress` through the normal `Review` / `Done` transitions (see `STATUS_TRANSITIONS` in `status-workflow.ts`). The valid routes are:

| Option | Transition Command | Use Case |
|--------|--------------------|----------|
| Cancelled | `shirokuma-docs items cancel {n} --comment "{reason}"` | Close the issue as "no changes needed" (recommended) |
| On Hold | `shirokuma-docs items transition {n} --to "On Hold"` | Pending reconsideration or more information |
| Backlog | `shirokuma-docs items transition {n} --to Backlog` | Re-evaluate later |

> **Important**: `Cancelled` must be set via the dedicated **`items cancel`** command. Using `items transition --to Cancelled` leaves the issue open and breaks consistency (see `status-workflow.ts` L121).

Implementation:

```text
reason = extract_first_line(body)  # coding-worker body first-line summary
user_choice = AskUserQuestion(
    "Completed with no changes. Reason: {reason}. How should the status be handled?",
    options=[
      "Cancelled (recommended)",
      "On Hold (reconsider)",
      "Backlog (re-evaluate later)"
    ]
)

if user_choice == "Cancelled":
    run: shirokuma-docs items cancel {number} --comment "{reason}"
else:
    run: shirokuma-docs items transition {number} --to {user_choice}
```

In headless mode (`--headless`), skip AskUserQuestion and run `items cancel {number} --comment "{reason}"` as the default action (Cancelled can be reversed via `items reopen` + `items transition`).

### Next Steps Suggestion for No Changes

Since no PR exists, omit the `/review-flow` line and present only:

```
## Next Steps

No changes were deemed necessary. If needed:
- `/implement-flow #{number}` — Re-run (in case the determination was incorrect)
```
