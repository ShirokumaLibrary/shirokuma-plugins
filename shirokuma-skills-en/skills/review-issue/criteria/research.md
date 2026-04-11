# Research Review Criteria

> **Deprecated**: This file has been migrated to `analyze-issue/criteria/`. This file is retained for backward compatibility but will be removed in the future.

## Requirement Alignment

| Criterion | Evaluation Aspect |
|-----------|-------------------|
| Tech stack compatibility | Are recommended patterns compatible with the project's tech-stack (CLAUDE.md / tech-stack.md)? |
| Existing pattern consistency | Do recommendations not contradict existing implementation patterns in the project? |
| Dependency compatibility | Do recommended libraries/versions not conflict with existing dependencies? |
| Architecture fit | Does the recommended approach align with the project's architecture policies? |

## Research Quality

| Criterion | Evaluation Aspect |
|-----------|-------------------|
| Source diversity | Is there corroboration from multiple independent sources (at least 1 official documentation)? |
| Version consistency | Does the referenced documentation version match the project's version in use? |
| Source attribution | Do all recommendations have source URLs? |
| Currency | Are there no references to deprecated APIs or outdated patterns? |

## Implementability

| Criterion | Evaluation Aspect |
|-----------|-------------------|
| Specificity | Are recommendations concrete with code examples (not abstract advice)? |
| Incremental adoption | For large changes, is an incremental adoption path provided? |
| Risk identification | Are potential risks and caveats explicitly stated? |

## Mismatch Decision

| Alignment | Condition | Action |
|-----------|-----------|--------|
| Full match | Recommendations align with existing patterns | Adopt as-is |
| Partial match | Only some recommendations are applicable | Extract applicable parts, document reasons for non-applicable parts |
| Mismatched but useful | Best practice but conflicts with current architecture | Create adoption proposal (document impact scope, adoption path, risks) |
| Mismatched and inapplicable | Fundamentally incompatible with the project's tech stack or requirements | Document rejection reasons, explore alternatives |
