---
name: review-flow
description: Takes a PR number, performs code review execution and processes unresolved review threads in an automated chain. Triggers: "review response", "PR review", "code review PR", "/review-flow #123".
allowed-tools: Bash, Read, Grep, Glob, Skill, TaskCreate, TaskUpdate, TaskGet, TaskList, AskUserQuestion, Agent
---

# PR Review Response

Takes a PR number and performs code review execution (via `review-issue` Agent / `review-worker`) and processes unresolved review threads through an automated chain: classify, fix, commit, reply, and resolve.

## Responsibility Boundary

| Skill | Responsibility |
|-------|---------------|
| `review-issue` | Code review execution engine. Invoked via Agent tool (`review-worker`) |
| `review-flow` (this skill) | PR review orchestrator (review execution + thread response). Entry point for a new conversation |

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
   - PR body (`body`): Used for artifact detection

2. If a related Issue exists, reference its plan for context:
   ```bash
   shirokuma-docs items pull {issue-number}
   # → Read .shirokuma/github/{issue-number}.md
   ```
3. Review the PR diff:
   ```bash
   # Base branch (typically develop, integration branch for sub-issues)
   git diff origin/{base-branch}...HEAD
   ```

4. **Artifact Detection**: Identify "review target artifacts" from the PR body:

   **Detection Rules:**
   - Extract all `#N` references from the PR body
   - Exclude references matching `Closes #N` / `Fixes #N` / `Refs #N` / `References #N` patterns as linked issues
   - The remaining `#N` references in the `## Summary` / `## 概要` section, or any `#N` references in the `## Artifacts` / `## 成果物` section, become artifact candidates
   - If 0 artifact candidates → skip artifact review (diff-only review as before)
   - If artifact candidates exist → use `shirokuma-docs items pull {N}` to cache and read `.shirokuma/github/{N}.md` frontmatter `type` field to identify Discussion / Issue / PR type, and include only Discussions and Issues as review targets
   - **Limit**: Up to 10 artifacts maximum. If exceeded, review only the first 10 and output a warning

   Record as **artifact candidate list** (format: `#N (Discussion)`, `#N (Issue)`, etc.)

### Step 2: Review State Assessment and Branching

First check the `review_count` obtained in Step 1:

**If `review_count: 0` → proceed to new review mode (Step 2a)**

**If `review_count > 0` → fetch unresolved threads and branch**:

```bash
shirokuma-docs pr comments {PR#}
```

- 0 unresolved threads → display completion report and propose re-review ("Would you like to run a re-review with `review-issue`?" via AskUserQuestion). If user accepts, transition to Step 2a
- Unresolved threads exist → proceed to existing flow (Step 3 onwards)

### Step 2a: Review Execution Mode (when `review_count: 0`)

When no review has been submitted yet, invoke `review-issue` via the Agent tool (`review-worker`) to perform a code review.

1. Invoke `review-issue` via Agent tool to perform a code review on the PR diff:

   If artifact candidates exist, include an "Artifact review targets:" section in the prompt:
   ```text
   Agent(
     description: "review-worker code PR #{PR#}",
     subagent_type: "review-worker",
     prompt: "code PR #{PR#}\n\nArtifact review targets:\n- #1592 (Discussion)\n- #1593 (Discussion)"
   )
   ```

   If no artifact candidates, use the conventional form:
   ```text
   Agent(
     description: "review-worker code PR #{PR#}",
     subagent_type: "review-worker",
     prompt: "code PR #{PR#}"
   )
   ```
2. `review-issue` posts the review results as a PR comment. Scan the Agent tool output body for review results
3. If `review-issue` posted an issue comment, check for its presence via `pr comments`
4. Check for unresolved threads:
   ```bash
   shirokuma-docs pr comments {PR#}
   ```
   - Unresolved threads exist (`unresolved_threads > 0`) → proceed to Step 2b (review result confirmation)
   - No unresolved threads but `issue_comments` contains a review comment → proceed to Step 2b (review result confirmation). This occurs when `review-issue` posts improvement suggestions as an issue comment
   - No unresolved threads and no review comment in `issue_comments` → display completion report and exit

### Step 2b: Review Result Confirmation (User Control Point)

> **Scope:** This step applies only after Step 2a (new review execution, `review_count: 0`). When processing existing threads with `review_count > 0`, the user is already aware of the review content, so UCP is not required.

After `review-issue` completes in Step 2a and unresolved threads or review issue comments exist, present the review results to the user and confirm the response approach. `review-issue` may post findings as review threads or as issue comments; the UCP must trigger for either format.

Scan the Agent tool (`review-worker`) output body for the `**Review result:**` string to obtain the PASS / FAIL judgment.

1. Display a summary of review results (number of issues, breakdown by type) to the user
2. Confirm via `AskUserQuestion`:
   - "Please review the results. Would you like to start addressing them?"
   - Options: "Start addressing" / "No fixes needed (complete as-is)" / "Address selected threads only"
3. Branch based on user response:
   - **Start addressing** → proceed to thread response flow (Step 3 onwards)
   - **No fixes needed** → display completion report and exit
   - **Selected threads only** → display numbered thread list and confirm which threads to address via `AskUserQuestion`, then process selected threads only (Step 3 onwards)

### Step 3: Thread Classification

Classify each unresolved thread into one of 4 types:

| Type | Criteria | Handling |
|------|----------|----------|
| Code fix | Requests a code change | Fix → commit → reply → resolve |
| Comment fix | Points out error in a previous AI comment | Edit comment → reply → resolve |
| Question | Asks for explanation or rationale | Reply → resolve |
| Disagreement | Reviewer and AI differ in judgment | Reply (do NOT resolve) |

### Step 4: Task Registration (Required)

> **TaskCreate registration is mandatory.** Cannot be skipped. Proceeding to Step 5 without task registration is prohibited. To prevent the LLM from halting mid-chain during long processing sequences, all thread processing steps must be pre-registered via TaskCreate and progress tracked via TaskUpdate.

Register tasks via TaskCreate based on classification using the following templates:

**When code fix threads exist:**

| # | content | activeForm |
|---|---------|------------|
| 1 | Code fix: {thread summary 1}, {thread summary 2}, ... | Applying code fixes |
| 2 | Commit and push code fixes | Committing and pushing |
| 3 | Simplify and improve code | Improving code |
| 4 | Run security review | Running security review |
| 5 | Push improvement commit (only if changes were made) | Committing and pushing |
| 6 | Reply and resolve each thread | Replying and resolving threads |
| 7 | Post PR summary comment | Posting PR summary |

Dependencies: step 2 blockedBy 1, step 3 blockedBy 2, step 4 blockedBy 3, step 5 blockedBy 4, step 6 blockedBy 5, step 7 blockedBy 6.

**When only question/disagreement threads exist:**

| # | content | activeForm |
|---|---------|------------|
| 1 | Reply and resolve each thread | Replying and resolving threads |

When code fix threads and question/disagreement threads coexist, use the code fix template and process all thread types together in the reply/resolve step.

### Step 5: Sequential Thread Processing

> **TaskUpdate progress tracking is mandatory.** Update each task to `in_progress` when starting and `completed` when finished. Continue to the next task within the same response as long as `pending` tasks remain in the TaskList.

#### Code Fix Threads

Process code fix threads together. Delegate fixes to `code-issue` via Skill tool and commits to `commit-worker` via Agent tool.

1. **Fix**: Delegate to `code-issue` with the thread information (file paths, review feedback) for all threads at once:
   ```text
   Skill(
     skill: "code-issue",
     args: "Address the review feedback for PR #{PR#}.\n\n{fix instructions for each thread}"
   )
   ```
   `code-issue` runs via Skill tool (main context), so no YAML output parsing is needed. Proceed to next step if no errors.

2. **Commit & Push**: Delegate all fix commits and pushes to `commit-worker`:
   ```text
   Agent(
     description: "commit-worker PR #{PR#} review fixes",
     subagent_type: "commit-worker",
     prompt: "Commit and push the review fixes. Use `shirokuma-docs git commit-push` for committing."
   )
   ```

3. **Simplify and improve code**: Run `/simplify` via Skill tool:
   ```text
   Skill(skill: "simplify")
   ```
   Continue even if no changes are made (extra commit only needed when changes occur).

4. **Security review**: Run `/security-review` via Bash subprocess:
   ```bash
   claude -p "/security-review"
   ```
   If `claude` is not available, output a warning and continue.
   > **⚠️ Do NOT truncate output**: Do not pipe through `| tail` / `| head` / `| grep`. Security review findings will be lost if output is truncated.

5. **Improvement commit (only if changes were made)**: If `/simplify` or `/security-review` produced code changes, delegate an additional commit to `commit-worker`:
   ```text
   Agent(
     description: "commit-worker PR #{PR#} simplify/security improvements",
     subagent_type: "commit-worker",
     prompt: "Commit and push improvements from simplify/security-review. Use `shirokuma-docs git commit-push` for committing."
   )
   ```
   If no changes were made, skip this step, update the task to `completed`, and continue.

6. **Reply**: Reply to each thread referencing the commit (use numeric `database_id` from `pr comments` output for `--reply-to`)
   ```bash
   shirokuma-docs pr reply {PR#} --reply-to {database_id} --body-file - <<'EOF'
   Fixed in {commit-hash}.

   {description of the fix}
   EOF
   ```
7. **Resolve**: Resolve the thread (use `PRRT_`-prefixed ID from `pr comments` output for `--thread-id`)
   ```bash
   shirokuma-docs pr resolve {PR#} --thread-id {PRRT_id}
   ```

#### Comment Fix Threads

1. **Edit comment**: Fix the erroneous comment
   ```bash
   shirokuma-docs items push {number} {comment-id}
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
shirokuma-docs items add comment {PR#} --file /tmp/shirokuma-docs/pr-{PR#}-review-response.md
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

## Rules

1. **Process all threads before reporting back** — Do not ask the user between threads
2. **Reply and Resolve are paired** — Every reply should be followed by a resolve (except disagreements)
3. **Use correct IDs** — `--reply-to` takes numeric `database_id` from `pr comments` output, `--thread-id` takes `PRRT_`-prefixed ID from `pr comments` output
4. **Commit per fix** — Do not mix fixes for different threads in one commit (call `git commit-push` once per fix)
5. **Do not resolve disagreements** — Let the reviewer decide
6. **Restore context first** — Step 1 must always run first; obtain `review_count` before branching
7. **Review execution via `review-issue`** — Step 2a invokes `review-issue` via Agent tool (`review-worker`); do not write reviews directly
8. **Code fixes via skill/subagent delegation** — Step 5 code fixes are delegated to `code-issue` (Skill) / `commit-worker` (Agent); the orchestrator does not modify code directly

## Edge Cases

| Situation | Action |
|-----------|--------|
| `review_count: 0` | Execute code review via `review-issue` Agent (`review-worker`) in review execution mode (Step 2a) |
| 0 unresolved threads (`review_count > 0`) | Display completion report and propose re-review |
| Thread already resolved | Skip |
| Outdated comment (code changed) | Reply if feedback is still valid, reference the relevant commit |
| Reviewer requests re-review | Reply but leave thread open |
| PR has no related Issue | Skip Issue reference in context restoration |
| No artifact candidates in PR body | Skip artifact review (diff only) |
| Artifact candidates exceed 10 | Review only first 10 and display warning |
| Artifact is a PR type | PRs are not artifact review targets (only Discussion / Issue) |
| Unresolved threads present and review comment present | `unresolved_threads > 0` takes priority. Proceed to Step 2b (review result confirmation) |
| No unresolved threads but review comment present | `review-issue` posted improvement suggestions as issue comment. Identified via `pr comments` `issue_comments`. Trigger Step 2b UCP |
| Code fix affects other threads | Check impact and address together |
| User decides no fixes needed (UCP) | Display completion report and exit. Skip thread resolution |
| User selects partial addressing (UCP) | Process only specified threads, leave the rest unresolved |

## Tool Usage

| Tool | When |
|------|------|
| Skill | Code fixes via `code-issue` (Step 5) |
| Agent | Code review execution via `review-worker` (Step 2a), commits and pushes via `commit-worker` (Step 5) |
| Bash | `shirokuma-docs pr comments`, `pr reply`, `pr resolve`, git operations |
| Read | Code review, plan reference |
| TaskCreate, TaskUpdate | Track thread processing progress |

## References

| Reference | Usage |
|-----------|-------|
| `implement-flow` skill | Worker completion unified pattern, UCP check |
