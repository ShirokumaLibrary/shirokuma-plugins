---
name: reviewing-on-pr
description: Takes a PR number, performs code review execution and processes unresolved review threads in an automated chain. Triggers: "review response", "PR review", "code review PR", "/reviewing-on-pr #123".
allowed-tools: Bash, Read, Grep, Glob, TodoWrite, AskUserQuestion, Agent
---

# PR Review Response

Takes a PR number and performs code review execution (via `review-worker`) and processes unresolved review threads through an automated chain: classify, fix, commit, reply, and resolve.

## Responsibility Boundary

| Skill | Responsibility |
|-------|---------------|
| `review-issue` | Code review execution engine. Invoked via `review-worker` |
| `reviewing-on-pr` (this skill) | PR review orchestrator (review execution + thread response). Entry point for a new conversation |

## Arguments

| Format | Example | Behavior |
|--------|---------|----------|
| PR number | `#123` or `123` | Fetch and address review threads for the PR |
| No argument | — | Ask for PR number via AskUserQuestion |

## Workflow

### Step 1: Context Restoration (Required — Must Run First)

> **This step must always run first.** Cannot be skipped.

1. Fetch PR information and record `review_count` and `linked_issues` (used for branching in Step 2):
   ```bash
   shirokuma-docs pr show {PR#}
   ```
   Fields to extract:
   - `review_count`: Number of submitted reviews (0 = triggers new review mode)
   - `linked_issues`: Related Issue numbers (used for context restoration)
   - `base_ref_name`: Base branch (used to fetch diff)

2. If a related Issue exists, reference its plan for context:
   ```bash
   shirokuma-docs show {issue-number}
   ```
3. Review the PR diff:
   ```bash
   # Base branch (typically develop, integration branch for sub-issues)
   git diff origin/{base-branch}...HEAD
   ```

### Step 2: Review State Assessment and Branching

First check the `review_count` obtained in Step 1:

**If `review_count: 0` → proceed to new review mode (Step 2a)**

**If `review_count > 0` → fetch unresolved threads and branch**:

```bash
shirokuma-docs pr comments {PR#}
```

- 0 unresolved threads → display completion report and propose re-review ("Would you like to run a re-review with `review-worker`?" via AskUserQuestion). If user accepts, transition to Step 2a
- Unresolved threads exist → proceed to existing flow (Step 3 onwards)

### Step 2a: Review Execution Mode (when `review_count: 0`)

When no review has been submitted yet, invoke `review-worker` via the Agent tool to perform a code review.

1. Invoke `review-worker` via Agent tool to perform a code review on the PR diff:
   ```text
   Agent(
     description: "review-worker PR #{PR#}",
     subagent_type: "review-worker",
     prompt: "Perform a code review for PR #{PR#}."
   )
   ```
2. `review-worker` posts the review results as a PR comment
3. Extract `comment_id` from `review-worker`'s output frontmatter (present when `review-worker` posted an issue comment)
4. Check for unresolved threads:
   ```bash
   shirokuma-docs pr comments {PR#}
   ```
   - Unresolved threads exist (`unresolved_threads > 0`) → proceed to Step 2b (review result confirmation)
   - No unresolved threads but `comment_id` present → proceed to Step 2b (review result confirmation). This occurs when `review-worker` posts improvement suggestions as an issue comment
   - No unresolved threads and no `comment_id` → display completion report and exit (see Step 6)

### Step 2b: Review Result Confirmation (User Control Point)

> **Scope:** This step applies only after Step 2a (new review execution, `review_count: 0`). When processing existing threads with `review_count > 0`, the user is already aware of the review content, so UCP is not required.

After `review-worker` completes in Step 2a and unresolved threads or `comment_id` (an issue comment posted by review-worker) exist, present the review results to the user and confirm the response approach. `review-worker` may post findings as review threads or as issue comments; the UCP must trigger for either format.

1. Display a summary of review results (number of issues, breakdown by type) to the user
2. Confirm via `AskUserQuestion`:
   - "Please review the results. Would you like to start addressing them?"
   - Options: "Start addressing" / "No fixes needed (complete as-is)" / "Address selected threads only"
3. Branch based on user response:
   - **Start addressing** → proceed to thread response flow (Step 3 onwards)
   - **No fixes needed** → display completion report and exit (Step 6)
   - **Selected threads only** → display numbered thread list and confirm which threads to address via `AskUserQuestion`, then process selected threads only (Step 3 onwards)

### Step 3: Thread Classification

Classify each unresolved thread into one of 4 types:

| Type | Criteria | Handling |
|------|----------|----------|
| Code fix | Requests a code change | Fix → commit → reply → resolve |
| Comment fix | Points out error in a previous AI comment | Edit comment → reply → resolve |
| Question | Asks for explanation or rationale | Reply → resolve |
| Disagreement | Reviewer and AI differ in judgment | Reply (do NOT resolve) |

### Step 4: TodoWrite Registration

Register all thread processing steps in TodoWrite based on classification:

```
1. [Code fix] Thread: {summary} — fix, commit & push, reply, resolve
2. [Question] Thread: {summary} — reply, resolve
3. [Disagreement] Thread: {summary} — reply only
4. Display completion report
```

### Step 5: Sequential Thread Processing

#### Code Fix Threads

Process code fix threads together. Delegate fixes to `coding-worker` and commits to `commit-worker`.

1. **Fix**: Delegate to `coding-worker` with the thread information (file paths, review feedback) for all threads at once:
   ```text
   Agent(
     description: "coding-worker PR #{PR#} review fixes",
     subagent_type: "coding-worker",
     prompt: "Address the review feedback for PR #{PR#}.\n\n{fix instructions for each thread}"
   )
   ```
   After `coding-worker` completes, parse its output following the unified pattern in `working-on-issue/reference/worker-completion-pattern.md`.

2. **Commit & Push**: Delegate all fix commits and pushes to `commit-worker`:
   ```text
   Agent(
     description: "commit-worker PR #{PR#} review fixes",
     subagent_type: "commit-worker",
     prompt: "Commit and push the review fixes. Use `shirokuma-docs git commit-push` for committing."
   )
   ```

3. **Reply**: Reply to each thread referencing the commit (use numeric `database_id` from `pr comments` output for `--reply-to`)
   ```bash
   shirokuma-docs pr reply {PR#} --reply-to {database_id} --body-file - <<'EOF'
   Fixed in {commit-hash}.

   {description of the fix}
   EOF
   ```
4. **Resolve**: Resolve the thread (use `PRRT_`-prefixed ID from `pr comments` output for `--thread-id`)
   ```bash
   shirokuma-docs pr resolve {PR#} --thread-id {PRRT_id}
   ```

#### Comment Fix Threads

1. **Edit comment**: Fix the erroneous comment
   ```bash
   shirokuma-docs issues comment-edit {comment-id} --body-file /tmp/shirokuma-docs/{number}-updated.md
   ```
2. **Reply**: Reply noting the correction
3. **Resolve**: Resolve the thread

#### Question Threads

1. **Reply**: Explain referencing code and plan
2. **Resolve**: Resolve the thread

#### Disagreement Threads

1. **Reply**: Explain concerns and trade-offs
2. Do **not** resolve — let the reviewer decide

#### PR Summary Comment

After completing thread responses that include code fixes, post a summary comment to the PR so that reviewers can track all response actions within the PR history.

```bash
shirokuma-docs comment {PR#} --body-file /tmp/shirokuma-docs/pr-{PR#}-review-response.md
```

Content of `/tmp/shirokuma-docs/pr-{PR#}-review-response.md`:

````markdown
## Review Response Complete

Addressed {N} threads.

| Thread | Type | Commit |
|--------|------|--------|
| {summary} | Code fix | {commit-hash} |
| {summary} | Question | — |
````

> **Note**: Skip this step if there are no code fix threads (only questions/disagreements).

### Step 6: Completion Report

```markdown
## Review Response Complete: PR #{PR#}

**Threads processed:** {resolved}/{total}

| Thread | Type | Result |
|--------|------|--------|
| {summary} | Code fix | Resolved |
| {summary} | Question | Resolved |
| {summary} | Disagreement | Unresolved (awaiting reviewer) |

[**Commits:** {commit-count}]
```

## Rules

1. **Process all threads before reporting back** — Do not ask the user between threads
2. **Reply and Resolve are paired** — Every reply should be followed by a resolve (except disagreements)
3. **Use correct IDs** — `--reply-to` takes numeric `database_id` from `pr comments` output, `--thread-id` takes `PRRT_`-prefixed ID from `pr comments` output
4. **Commit per fix** — Do not mix fixes for different threads in one commit (call `git commit-push` once per fix)
5. **Do not resolve disagreements** — Let the reviewer decide
6. **Restore context first** — Step 1 must always run first; obtain `review_count` before branching
7. **Review execution via `review-worker`** — Step 2a invokes `review-worker` via Agent tool; do not write reviews directly
8. **Code fixes via worker delegation** — Step 5 code fixes are delegated to `coding-worker` / `commit-worker`; the orchestrator does not modify code directly

## Edge Cases

| Situation | Action |
|-----------|--------|
| `review_count: 0` | Execute code review via `review-worker` in review execution mode (Step 2a) |
| 0 unresolved threads (`review_count > 0`) | Display completion report and propose re-review |
| Thread already resolved | Skip |
| Outdated comment (code changed) | Reply if feedback is still valid, reference the relevant commit |
| Reviewer requests re-review | Reply but leave thread open |
| PR has no related Issue | Skip Issue reference in context restoration |
| No unresolved threads but `comment_id` present | `review-worker` posted improvement suggestions as issue comment. Identified via frontmatter `comment_id`. Trigger Step 2b UCP |
| Code fix affects other threads | Check impact and address together |
| User decides no fixes needed (UCP) | Display completion report and exit. Skip thread resolution |
| User selects partial addressing (UCP) | Process only specified threads, leave the rest unresolved |

## Tool Usage

| Tool | When |
|------|------|
| Agent | Code review execution via `review-worker` (Step 2a), code fixes and commits via `coding-worker` / `commit-worker` (Step 5) |
| Bash | `shirokuma-docs pr comments`, `pr reply`, `pr resolve`, git operations |
| Read | Code review, plan reference |
| TodoWrite | Track thread processing progress |

## References

| Reference | Usage |
|-----------|-------|
| `working-on-issue/reference/worker-completion-pattern.md` | Worker completion unified pattern, UCP check |
