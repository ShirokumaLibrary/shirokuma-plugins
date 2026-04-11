---
name: finalize-changes
description: Small orchestrator that runs the common post-processing chain (/simplify → security review → improvement commit) after code changes. Called from implement-flow and review-flow.
allowed-tools: Bash, Agent, Skill
---

# Finalize Changes

Common post-processing chain shared by `implement-flow` and `review-flow`. Runs `/simplify` and `reviewing-security` after code changes, and pushes an improvement commit only when changes were made.

## Callers

| Skill | When Called |
|-------|------------|
| `implement-flow` | After PR creation (post-processing chain for steps 4-5) |
| `review-flow` | After review fix commit (post-processing in step 5) |

## Workflow

### Step 1: Simplify and Improve Code

Run `/simplify` via Skill tool:

```text
Skill(skill: "simplify")
```

Continue even if no changes are made (extra commit only when changes occur).

> **Error handling**: If `/simplify` fails, continue to the security review. Output a warning and proceed to the next step.

### Step 2: Security Review

Run the `reviewing-security` skill via Skill tool:

```text
Skill(skill: "reviewing-security")
```

> **Error handling**: If the security review fails, proceed to the improvement commit check (`reviewing-security` handles errors internally).

### Step 3: Improvement Commit (Only When Changes Were Made)

If `/simplify` or `reviewing-security` produced code changes, delegate an additional commit to `commit-worker`:

```bash
# Check if changes exist
git diff --stat
```

If changes exist:

```text
Agent(
  description: "commit-worker simplify/security improvements",
  subagent_type: "commit-worker",
  prompt: "Commit and push improvements from simplify/security-review. Use `shirokuma-docs git commit-push` for committing."
)
```

If no changes, skip this step and continue.

## Rules

1. **Continue even if `/simplify` fails** — Do not skip the security review
2. **Skip if no changes** — Confirm with `git diff --stat` before running the improvement commit
3. **Do not truncate output** — Do not pipe security review output through `| tail` / `| head` / `| grep`
4. **Caller owns the work summary** — This skill does not post work summaries

## Tool Usage

| Tool | When |
|------|------|
| Skill | `/simplify` (Step 1), `reviewing-security` (Step 2) |
| Bash | `git diff --stat` to check for changes (Step 3) |
| Agent | `commit-worker` for improvement commit (Step 3, if changes exist) |
