---
name: designing-shadcn-ui
description: Creates distinctive, production-grade frontend interfaces using shadcn/ui. Triggers: "memorable design", "distinctive UI", "unique design", "landing page", "impressive UI", or when avoiding generic look and creating unique visual aesthetics.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch
---

# shadcn/ui Design

Create memorable, production-grade interfaces that avoid generic "AI slop" aesthetics.

## Workflow

### 0. Tech Stack Check

**First**, read project `CLAUDE.md` to confirm:
- Frontend framework (Next.js version, React version)
- Styling (Tailwind v3/v4, CSS Modules)
- Component library (shadcn/ui stable/canary)
- i18n setup (next-intl, messages structure)

### 1. Design Brief Check

When delegated from `designing-on-issue`, Design Brief and Aesthetic Direction are provided. Use them as-is.

When invoked standalone, Design Brief can be skipped. However, if aesthetic direction is unclear, minimal direction confirmation is recommended.

### 2. Implementation

- Production quality and functional
- Visually impactful and memorable
- Cohesive aesthetic vision

### 3. Build Verification (Required)

```bash
pnpm --filter {app-name} build
```

### 4. Review Checklist

- [ ] Typography is distinctive (not Inter, Roboto, Arial)
- [ ] Color palette is cohesive and intentional
- [ ] Motion/animation adds delight
- [ ] Layout has visual interest
- [ ] Build passes without errors

## Design Guidelines

### Typography

**DO**: Distinctive display fonts, intentional sizing scale
**DON'T**: Inter, Roboto, Arial, system fonts

### Color & Theme

**DO**: Cohesive aesthetic, CSS variables, dominant color + sharp accent
**DON'T**: Purple gradient on white, muted even palette

### Motion & Animation

**DO**: High-impact moments, staggered reveals, surprising hover states
**DON'T**: Purposeless motion

### Spatial Composition

**DO**: Asymmetry, overlap, grid-breaking elements
**DON'T**: Predictable 12-column grid only

## Anti-Patterns

| Pattern | Alternative |
|---------|------------|
| Purple gradient on white | Bold color choices |
| Inter/Roboto everywhere | Distinctive font pairing |
| Centered card grid | Asymmetric layout |
| Generic icons | Custom icon set |

## Next Steps

When invoked via `designing-on-issue`, control returns automatically to the orchestrator.

When invoked standalone:

```
Implementation complete. Next steps:
→ `/committing-on-issue` to stage and commit your changes
→ Use `/designing-on-issue` for the full workflow
```

## Notes

- **Memorability is the top priority**
- **Build must pass**
- When Design Brief is provided, implement based on it. When standalone, confirm aesthetic direction with user before implementation
