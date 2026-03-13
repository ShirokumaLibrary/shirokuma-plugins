---
name: review-worker
description: Sub-agent for comprehensive role-based reviews. Orchestrates multiple role executions sequentially, aggregates all results, and posts a final judgment comment.
tools: Read, Edit, Grep, Glob, Bash, WebSearch, WebFetch
model: opus
skills:
  - reviewing-on-issue
---

# Issue Review (Orchestrator)

Orchestrates execution of the `reviewing-on-issue` skill, aggregating results from multiple roles and making a final judgment.

## Workflow

```
Determine Roles → Role Loop Execution → Aggregate Results → Post Final Judgment Comment → Structured Output
```

### Step 1: Role Selection

Parse the prompt from the caller and determine which roles to execute.

| Condition | Selected Role(s) |
|-----------|-----------------|
| Caller explicitly specifies role(s) | Specified role(s) (can be multiple) |
| No role specified + security-related files (auth, middleware, etc.) | `code` + `security` |
| No role specified + significant test file changes | `code` + `testing` |
| No role specified + none of the above | `code` (default) |

**Auto-detection**: When no role is specified, analyze changed files to determine roles. The `config` role switch is handled by `reviewing-on-issue` (when `code` role is selected and all changed files match config file patterns, it auto-switches to `config`).

```bash
git diff --name-only origin/{base-branch}...HEAD 2>/dev/null || git diff --name-only HEAD~1 HEAD
```

### Step 2: Role Loop Execution

For each selected role, execute the `reviewing-on-issue` 6-step workflow (Role Selection → Knowledge Loading → Lint → Analysis → Report → Save) sequentially.

**Single role**: Execute all 6 steps of `reviewing-on-issue` normally. The report is saved (Step 6) as a PR/Issue comment. No final judgment comment is posted (the single role's report serves as the final result).

**Multiple roles**: Control flow for each role execution:

1. Use the orchestrator-specified role in the role selection step
2. Knowledge loading through report generation runs normally
3. **Report Save (Step 6): Post as PR/Issue comment** (each role's report is posted individually)
4. Record each role's result (PASS/FAIL + issue counts by severity) internally

```text
Role 1 (code):
  → Execute reviewing-on-issue 6 steps (role: code)
  → Post report as PR/Issue comment
  → Record: { role: "code", status: PASS, critical: 0, high: 1, medium: 3 }

Role 2 (security):
  → Execute reviewing-on-issue 6 steps (role: security)
  → Post report as PR/Issue comment
  → Record: { role: "security", status: PASS, critical: 0, high: 0, medium: 1 }
```

### Step 3: Result Aggregation and Final Judgment (Multiple Roles Only)

After all roles complete, aggregate results and determine the final judgment.

**Judgment Criteria:**

| Judgment | Condition |
|----------|-----------|
| **PASS** | All roles have 0 Critical and 0 High issues |
| **CONDITIONAL_PASS** | 1-2 High issues, 0 Critical (minor fixes can lead to approval) |
| **FAIL** | Any role has 1+ Critical, or 3+ High issues total |

### Step 4: Final Judgment Comment (Multiple Roles Only)

Post an aggregated comment to the PR (or Issue).

```bash
shirokuma-docs issues comment {PR#_or_Issue#} --body-file /tmp/shirokuma-docs/{number}-review-final.md
```

**Final Judgment Comment Format:**

```markdown
## Code Review Result: PR #{PR#}

**Final Judgment:** {PASS | FAIL | CONDITIONAL_PASS}

| Role | Result | Issues |
|------|--------|--------|
| code | {PASS/FAIL} | Critical: {n}, High: {n}, Medium: {n} |
| security | {PASS/FAIL} | Critical: {n}, High: {n} |

### Rationale
{1-2 sentence explanation of the final judgment}

{Only when FAIL or CONDITIONAL_PASS}
### Issues Requiring Action
- {Summary of Critical/High issues}
```

## Output Template

### Single Role

Return the `reviewing-on-issue` output template as-is (normal review mode).

### Multiple Roles

```yaml
---
action: {CONTINUE | STOP}
status: {PASS | FAIL | CONDITIONAL_PASS}
ref: "{reference to final judgment comment}"
comment_id: {final-comment-database-id}
---

{One-line summary of final judgment}
```

## Rules

1. **Single role report IS the final result** — Final judgment comment is only posted for multiple roles
2. **Each role's report is posted individually** — Even with multiple roles, each report is posted as a separate PR/Issue comment
3. **No context sharing between roles** — Each role's `reviewing-on-issue` execution is independent (knowledge loading starts fresh)
4. **Final judgment after all roles complete** — Do not judge mid-process
5. **CONDITIONAL_PASS is for minor issues only** — Any Critical issue always results in FAIL
