# Requirements Review Role

## Responsibilities

Quality review of the Issue body (purpose, overview, reproduction steps, expected behavior, deliverables, and considerations):
- Completeness (presence and sufficiency of required sections)
- Clarity (no ambiguous expressions or room for multiple interpretations)
- Implementability (sufficient information to serve as input for planning and implementation)
- Consistency (no contradictions or inconsistencies between sections)

## Distinction from `plan` Role

| Aspect | `review-issue` requirements role | `review-issue` plan role |
|--------|----------------------------------|--------------------------|
| Review target | Issue body (requirements/specs) itself | Plan content in the plan issue |
| Timing | Any time before `prepare-flow` execution | Second opinion after planning |
| Purpose | Quality gate for requirements and specs | Quality gate for plan implementability |
| Invocation | `/review-issue requirements #N` | `/review-issue plan #N` |

## Required Knowledge

Load these files for context:
- Project's `CLAUDE.md` - Project overview and conventions
- `.claude/rules/` - Project-specific rules (auto-loaded)

## Requirements Role Specific Workflow

```
1. Role selection: "requirements review" or "要件レビュー"
2. Fetch Issue body: shirokuma-docs items context {number} (→ Read .shirokuma/github/{org}/{repo}/issues/{number}/body.md)
3. Lint execution: Skip (target is not code files)
4. Issue body analysis: Analyze each section against review criteria
5. Report generation: Template format
6. Report saving: Issue comment
```

## Review Checklist

### Purpose Section Completeness
- [ ] `## Purpose` section exists
- [ ] "Who" (role/user type) is specifically stated
- [ ] "What" (feature/change to achieve) is clearly stated
- [ ] "Why" (reason/motivation) is not omitted
- [ ] Purpose is concrete and measurable (not just abstract statements)

### Overview Section Clarity
- [ ] `## Overview` section exists
- [ ] Change content is specifically described
- [ ] Implementation scope is clearly defined
- [ ] Out-of-scope items are explicitly stated (when applicable)
- [ ] Terminology is used consistently

### Reproduction Steps and Expected Behavior (for bugs/defects)
- [ ] `## Reproduction Steps` exists (for bug issues)
- [ ] Steps are numbered and specifically described
- [ ] Actual behavior and expected behavior are clearly separated
- [ ] Environment information (OS, browser, version, etc.) is included (when needed)

### Deliverables Specificity
- [ ] `## Deliverables` section exists (for Feature/Chore issues)
- [ ] Each deliverable is described in a concrete and verifiable form
- [ ] Completion criteria for deliverables are clear (e.g., "should be able to do X")
- [ ] Number and scope of deliverables is appropriate (not too many or too few)

### Considerations Sufficiency
- [ ] `## Considerations` section exists (for M+ issues)
- [ ] Technical constraints and dependencies are documented
- [ ] Alternative approaches and rejected options are documented (when applicable)
- [ ] Risks and cautions are explicitly stated

### Sufficient as Input for Planning and Implementation
- [ ] Requirements can be fully understood from the Issue body alone
- [ ] No ambiguous areas that would cause the implementer to be unsure
- [ ] Not overly dependent on external context (other issues, PRs, conversations, etc.)
- [ ] Priority and urgency are appropriately set

## Anti-patterns to Detect

### Missing Purpose
- [ ] `## Purpose` section does not exist
- [ ] Purpose is only "fix X" with no motivation stated
- [ ] "Who is affected" is not documented

### Vague Overview
- [ ] Only "improve" or "optimize" with no specific change content
- [ ] Implementation scope is unclear (what is in scope is unknown)
- [ ] Technical terms are not defined, leaving room for interpretation

### Unclear Deliverables
- [ ] `## Deliverables` section is empty or only states "it should work"
- [ ] Deliverables are not verifiable ("should become easier to use", etc.)
- [ ] Multiple deliverables are mixed and indistinguishable

### Unimplementable Requirements
- [ ] Requirements contradict each other
- [ ] Requirements include technically infeasible items
- [ ] Dependencies are unresolved

## Design Assessment

During the requirements review process, assess whether the issue requires a design phase and output `**Design assessment:** NEEDED / NOT_NEEDED` as structured output.

### Assessment Criteria

| Criterion | Assessment |
|-----------|-----------|
| Requirements have novelty that existing patterns cannot address | NEEDED |
| New creation or major changes to UI / screens | NEEDED |
| Addition or modification of data model / schema | NEEDED |
| New external API or integration | NEEDED |
| `area:frontend` / `area:ui` label present | NEEDED |
| `area:database` label present | NEEDED |
| Body keywords: `UI`, `screen`, `schema`, `data model` | NEEDED (when used in new creation / modification context) |
| Refactoring of existing code or minor modifications | NOT_NEEDED |
| Configuration changes, documentation additions, bug fixes | NOT_NEEDED |
| None of the above NEEDED criteria apply | NOT_NEEDED |

### Assessment Priority

If any single NEEDED criterion applies, the result is `NEEDED` (OR, not AND). Keyword-based assessment is weaker supplementary to label-based assessment; if a keyword appears in the context of "modifying existing functionality", it does not trigger NEEDED.

## Report Format

Use template from `templates/report.md`:

1. **Summary**: Overall quality summary of the Issue body
2. **Critical Issues**: Missing required sections, fatal ambiguities, unimplementable requirements
3. **Improvements**: Enrichment of descriptions, improved specificity, consistency fixes
4. **Best Practices**: Appropriate description patterns found
5. **Recommendations**: Prioritized action items

## Trigger Keywords

- "requirements review"
- "要件レビュー"
- "requirements check"
- "要件確認"
