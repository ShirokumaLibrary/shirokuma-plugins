# Plan Review Role

> **Note**: This role has been migrated to `analyze-issue`. For the current implementation, see `analyze-issue/roles/plan.md`.
> When `review-issue plan` is invoked, the backward compatibility stub in the `review-issue` SKILL.md automatically delegates to `analyze-issue`.

## Responsibilities

Quality review of the plan (plan issue or `## Plan` / `## 計画` section):
- Requirements coverage (all requirements from overview/tasks covered in plan)
- Changed files validity (no missing or extraneous files)
- Task granularity (1 task ≈ 1 commit principle)
- Risk analysis (breaking changes, performance impact oversight)
- Issue description sufficiency (plan understandable from the plan issue body alone)

> **Plan issue approach**: Plans are created as child issues of the parent issue (issues with titles starting with "Plan:" or "計画:"). Identify the plan issue from `subIssuesSummary`, fetch its body via `items context {plan-issue-number}`, and review. When no plan issue exists but the parent issue body contains a `## Plan` / `## 計画` section (legacy approach), use it as a fallback.

## Distinction from `plan-issue`

| Aspect | `plan-issue` built-in review | `analyze-issue` plan role |
|--------|-------------------------------------|-------------------------------|
| Timing | Immediate check right after planning | User-initiated at any time |
| Data retrieval | Issue body embedded in Task agent | Plan issue identified from Issue number, fetched via `shirokuma-docs items context` |
| Purpose | Initial quality gate for plan | Independent second opinion |
| Invocation | Auto-executed at `plan-issue` step 4 | `analyze-issue plan #N` |

## Required Knowledge

Load these files for context:
- Project's `CLAUDE.md` - Project overview and conventions
- `.claude/rules/` - Project-specific rules (auto-loaded)

## Plan Role Specific Workflow

```
1. Role selection: "plan review" or Review Issue
2. Fetch Issue body: shirokuma-docs items context {number} (→ Read .shirokuma/github/{org}/{repo}/issues/{number}/body.md)
3. Identify plan issue: Find child issue with title starting with "Plan:" from subIssuesSummary, fetch body via items context {plan-issue-number} (fallback: ## Plan section in body)
4. Lint execution: Skip (target is not code files)
5. Plan analysis: Review plan issue body (or legacy plan section) against review criteria
6. Report generation: Template format
7. Report saving: Issue comment
```

## Review Checklist

### Purpose Section Validity
- [ ] `## Purpose` section exists
- [ ] "Who" (role/user type) is specifically stated
- [ ] "What" (feature/change to achieve) is clearly stated
- [ ] "Why" (reason/motivation) is not omitted
- [ ] Purpose and plan approach are consistent

### Language & Style Compliance
- [ ] Plan section language complies with `output-language` rule
- [ ] Follows `github-writing-style` rule bullet-point guidelines (parallel structure, max 2 nesting levels, etc.)
- [ ] Heading levels are appropriate (`## Plan` > `### Approach` > `### Task Breakdown` etc.)
- [ ] Technical terms and project terminology are consistent

### Requirements Coverage
- [ ] All requirements from the Issue "Overview" section are covered in the plan
- [ ] All items from the Issue "Considerations" section are addressed in the plan
- [ ] Each item in "Deliverables" section has a corresponding task
- [ ] Implicit requirements (tests, version bump, etc.) are not overlooked

### Changed Files Validity
- [ ] Changed files list is documented
- [ ] No missing files (all changes inferred from requirements are included)
- [ ] No extraneous files (no out-of-scope changes)
- [ ] New files and existing file updates are clearly distinguished
- [ ] When `src/` source files are being changed, corresponding `__tests__/` test files are included in the changed files list (including indirect references such as snapshot tests)

### Task Granularity
- [ ] Each task is specific and actionable (not just "implement" but what and how)
- [ ] 1 task ≈ 1 commit granularity
- [ ] Task dependencies are clear (logical ordering)
- [ ] Number of tasks is appropriate for Issue size (not too many, not too few)

### Risk Analysis
- [ ] Breaking changes have their impact scope documented
- [ ] Performance impact is considered
- [ ] Impact on existing features is evaluated
- [ ] Rollback procedure or mitigation exists (when needed)

### Issue Description Sufficiency
- [ ] Plan is fully understandable from Issue body alone
- [ ] Approach rationale (why this method was chosen) is documented
- [ ] Alternative approaches considered are documented (when applicable)
- [ ] Prerequisites and constraints are explicitly stated

## Anti-patterns to Detect

### Missing Plan Section
- [ ] `## Plan` / `## 計画` section does not exist
- [ ] Plan section is empty or insufficient (heading only, no content)

### Tasks Too Abstract
- [ ] Only "implement" or "fix" with no specific change details
- [ ] Files or functions to change are not identified
- [ ] Mapping to deliverables is unclear

### Missing Changed Files List
- [ ] Standard/detailed level plan lacks changed files list
- [ ] File paths are inaccurate (referencing non-existent paths)

### Missing Risk Documentation
- [ ] Detailed level plan lacks risk analysis
- [ ] Breaking changes exist but impact scope is not documented

### Deliverables Mismatch
- [ ] "Deliverables" section items have no corresponding tasks
- [ ] Tasks fulfill completion criteria but diverge from deliverables
- [ ] Deliverables are vague ("it works" only)

## Report Format

Use template from `templates/report.md`:

1. **Summary**: Overall plan quality summary
2. **Critical Issues**: Missing requirements, significant inconsistencies
3. **Improvements**: Task granularity improvements, risk additions, etc.
4. **Best Practices**: Appropriate planning patterns found
5. **Recommendations**: Prioritized action items

## Trigger Keywords (migrated to analyze-issue)

- "plan review" → `analyze-issue plan`
- "計画レビュー" → `analyze-issue plan`
- "review plan" → `analyze-issue plan`
- "計画チェック" → `analyze-issue plan`
