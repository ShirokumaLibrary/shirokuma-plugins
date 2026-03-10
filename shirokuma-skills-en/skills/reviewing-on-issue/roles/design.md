# Design Review Role

## Responsibilities

Quality review of design artifacts (Design Brief, Aesthetic Direction, UI implementation):
- Design Brief quality (clarity of purpose, context, and differentiation)
- Aesthetic Direction validity (tone selection, design token definitions)
- Requirements alignment
- Technical feasibility (framework constraints such as shadcn/ui, Tailwind CSS v4)
- UI implementation quality (component composition, responsive design)

## Distinction from `designing-on-issue`

| Aspect | `designing-on-issue` built-in check | `reviewing-on-issue` design role |
|--------|--------------------------------------|----------------------------------|
| Timing | Iterative checks during design phase | Gate review after design completion |
| Purpose | Confirm design direction | Independent second opinion |
| Invocation | Within `designing-on-issue` loop | `/reviewing-on-issue design #N` |

## Required Knowledge

Load these files for context:
- Project's `CLAUDE.md` - Project overview and conventions
- `.claude/rules/` - Project-specific rules (auto-loaded)

## Design Role Specific Workflow

```
1. Role selection: "design review" or design-related Issue
2. Fetch Issue body: shirokuma-docs show {number}
3. Lint execution: Skip (target is not code files)
4. Design analysis: Review Design Brief, Aesthetic Direction, UI implementation
5. Report generation: Template format
6. Report saving: Issue comment
```

## Review Checklist

### Design Brief Quality
- [ ] Design Brief exists
- [ ] Purpose is clear (specific problem being solved is documented)
- [ ] Context is comprehensive (technical constraints, alignment with existing design system documented)
- [ ] Differentiation is specific (non-abstract uniqueness is defined)
- [ ] Target users are clearly defined

### Aesthetic Direction Validity
- [ ] Tone is clearly selected (e.g., professional, playful, minimal)
- [ ] Design tokens are defined (colors, spacing, typography)
- [ ] Alignment with shadcn/ui theme
- [ ] Consistency with project's existing UI is maintained
- [ ] Decorative elements (borders, shadows, etc.) are defined

### Requirements Alignment
- [ ] All Issue requirements are covered in the design
- [ ] Design does not exceed requirements scope (scope creep)
- [ ] Alignment with user stories/personas

### Technical Feasibility
- [ ] Complies with framework constraints (shadcn/ui, Tailwind CSS v4)
- [ ] Radix UI hydration pattern is considered
- [ ] Responsive design is considered
- [ ] Accessibility (a11y) standards are met

### UI Implementation Quality (post-implementation review)
- [ ] Component decomposition is appropriate
- [ ] Design tokens are used consistently
- [ ] Dark mode/light mode consideration (when applicable)
- [ ] Animations/transitions are appropriate (including performance impact)

## Anti-patterns to Detect

### Missing Design Brief
- [ ] Design Brief does not exist
- [ ] Brief is empty or insufficient (heading only, no content)

### Undefined Design Tokens
- [ ] Colors and spacing are hardcoded
- [ ] Inconsistency with existing design system
- [ ] Direct values used instead of Tailwind CSS v4 utilities

### Requirements Divergence
- [ ] Design does not meet requirements
- [ ] Excessive decoration (performance risk)
- [ ] Out-of-scope features included in design

### Accessibility Violations
- [ ] Insufficient contrast
- [ ] Keyboard navigation not supported
- [ ] Missing aria labels
- [ ] Improper focus management

## Report Format

Use template from `templates/report.md`:

1. **Summary**: Overall design quality summary
2. **Critical Issues**: Missing Design Brief, uncovered requirements, accessibility violations
3. **Improvements**: Design token additions, responsive improvements, etc.
4. **Best Practices**: Appropriate design patterns found
5. **Recommendations**: Prioritized action items

## Trigger Keywords

- "design review"
- "設計レビュー"
- "review design"
- "デザインレビュー"
