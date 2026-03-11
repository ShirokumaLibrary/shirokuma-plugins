---
name: reviewing-on-pr
description: Takes a PR number, batch-fetches unresolved review threads, classifies them (code fix / question / disagreement), fixes code, commits, replies, and resolves threads in an automated chain. Triggers: "review response", "PR review", "/reviewing-on-pr #123".
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, TodoWrite, AskUserQuestion
---

# PR Review Response

Takes a PR number and processes unresolved review threads through an automated chain: batch-fetch, classify, fix, commit, reply, and resolve.

## Responsibility Boundary

| Skill | Responsibility |
|-------|---------------|
| `reviewing-on-issue` | Self-review (review your own code). Invoked via `review-worker` |
| `reviewing-on-pr` (this skill) | PR review response (address reviewer feedback). Entry point for a new conversation |

## Arguments

| Format | Example | Behavior |
|--------|---------|----------|
| PR number | `#123` or `123` | Fetch and address review threads for the PR |
| No argument | — | Ask for PR number via AskUserQuestion |

## Workflow

### Step 1: Context Restoration

1. Fetch PR information:
   ```bash
   shirokuma-docs pr show {PR#}
   ```
2. If a related Issue exists, reference its plan for context:
   ```bash
   shirokuma-docs show {issue-number}
   ```
3. Review the PR diff:
   ```bash
   # Base branch (typically develop, integration branch for sub-issues)
   git diff origin/{base-branch}...HEAD
   ```

### Step 2: Batch-Fetch Unresolved Threads

```bash
shirokuma-docs pr comments {PR#}
```

If 0 unresolved threads → display completion report and exit.

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
1. [Code fix] Thread: {summary} — fix, commit, reply, resolve
2. [Question] Thread: {summary} — reply, resolve
3. [Disagreement] Thread: {summary} — reply only
4. Push changes
5. Display completion report
```

### Step 5: Sequential Thread Processing

#### Code Fix Threads

Process code fix threads together. Fix → individual commit, then batch push, reply, and resolve after all fixes.

1. **Fix**: Modify code based on review feedback
2. **Commit**: Commit per fix (reference Issue number)
   ```bash
   git add {modified-files}
   git commit -m "$(cat <<'EOF'
   fix: {description of fix} (#{issue-number})
   EOF
   )"
   ```
3. **Push**: Push once after all code fix commits
   ```bash
   git push
   ```
4. **Reply**: Reply to each thread referencing the commit
   ```bash
   shirokuma-docs pr reply {PR#} --reply-to {database_id} --body-file - <<'EOF'
   Fixed in {commit-hash}.

   {description of the fix}
   EOF
   ```
5. **Resolve**: Resolve the thread
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
3. **Use correct IDs** — `--reply-to` takes numeric `database_id`, `--thread-id` takes GraphQL `PRRT_` ID
4. **Commit per fix** — Do not mix fixes for different threads in one commit
5. **Push once** — Push once after all code fix commits
6. **Do not resolve disagreements** — Let the reviewer decide
7. **Restore context first** — Review Issue plan and PR diff before addressing threads

## Edge Cases

| Situation | Action |
|-----------|--------|
| 0 unresolved threads | Display completion report and exit |
| Thread already resolved | Skip |
| Outdated comment (code changed) | Reply if feedback is still valid, reference the relevant commit |
| Reviewer requests re-review | Reply but leave thread open |
| PR has no related Issue | Skip Issue reference in context restoration |
| Code fix affects other threads | Check impact and address together |

## Tool Usage

| Tool | When |
|------|------|
| Bash | `shirokuma-docs pr comments`, `pr reply`, `pr resolve`, git operations |
| Read | Code review, plan reference |
| Edit | Code fixes |
| TodoWrite | Track thread processing progress |
