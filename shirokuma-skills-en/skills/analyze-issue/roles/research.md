# Research Role

## Purpose

Verify that research results align with system requirements and architecture, and provide a proposal/confirmation flow when adopting mismatched best practices.

## Review Perspectives

Evaluate using the criteria defined in `criteria/research.md` (Requirement Alignment, Research Quality, Implementability, Mismatch Decision).

## Mismatch Handling

### Adoption Proposal Flow

When adopting a mismatched but useful best practice:

```
Mismatch detected → Impact assessment → Create adoption proposal → Include in review report
```

1. **Impact assessment**: Evaluate the volume of changes and risks required for adoption
2. **Create adoption proposal**: Document in the following format

```markdown
### Adoption Proposal: {Pattern Name}

**Recommended pattern:** {Best practice overview}
**Current pattern:** {Project's current state}
**Reason for mismatch:** {Why it cannot be directly applied}
**Adoption method:** {Incremental adoption path}
**Impact scope:** {Number of files/components that need changes}
**Risk:** {Potential risks}
```

3. **Include in review report**: Return as NEEDS_REVISION so the orchestrator confirms with the user

## Report Generation

The research role report uses the following structure:

```markdown
## Research Review: {Topic}

### Summary
{1-2 line summary of research quality and requirement alignment}

### Requirement Alignment
| Recommendation | Alignment | Notes |
|---------------|-----------|-------|
| {Recommendation 1} | Full / Partial / Mismatch | {Details} |

### Research Quality
- Sources: {n} (official: {m})
- Version consistency: {OK / Warning}
- Source attribution: {All / Some missing}

### Issues
{If issues were detected}

### Adoption Proposals
{If mismatched but useful patterns exist}

### Recommendations
{Improvement suggestions}
```

## Output Template

```yaml
---
action: {CONTINUE | REVISE}
status: {PASS | NEEDS_REVISION}
ref: "#{issue-number}"
comment_id: {comment-database-id}
---

{One-line review result summary}
```

- **PASS**: No critical issues in research findings, aligned with requirements
- **NEEDS_REVISION**: Insufficient sources, version inconsistencies, critical mismatches with requirements, or adoption proposals present
