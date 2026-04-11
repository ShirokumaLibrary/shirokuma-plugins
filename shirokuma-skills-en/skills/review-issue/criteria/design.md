# Design Review Criteria

> **Deprecated**: This file has been migrated to `analyze-issue/criteria/`. This file is retained for backward compatibility but will be removed in the future.

## UI Design Artifacts

### Design Brief

| Criterion | Evaluation Aspect |
|-----------|-------------------|
| Purpose | Is the problem being solved described specifically? Are there measurable goals rather than vague "improve"? |
| Context | Are tech stack constraints, existing design system, and browser requirements covered? |
| Differentiation | Is differentiation from competitors/existing UI specific? Not abstract expressions like "make it modern"? |
| Target Users | Are user personas or roles clearly defined? |

### Aesthetic Direction

| Criterion | Evaluation Aspect |
|-----------|-------------------|
| Tone definition | Is a clear tone (professional, playful, minimal, etc.) selected with rationale? |
| Colors | Are primary, secondary, accent, background, and text colors defined? |
| Spacing | Is a spacing system (4px/8px grid, etc.) defined? |
| Typography | Are font family, size scale, and weights defined? |
| Borders & Shadows | Are border radii and shadow levels defined? |
| shadcn/ui theme alignment | Do CSS variables follow shadcn/ui theme structure? |

### UI Implementation

| Criterion | Evaluation Aspect |
|-----------|-------------------|
| Component composition | Single responsibility, appropriately granular decomposition? |
| Tailwind CSS v4 | Are utility classes used appropriately? Compliance with v4-specific patterns like `@theme inline`? |
| Responsive | Are breakpoints (sm, md, lg, xl) appropriately set? |
| Animations | Are transitions in the 200-300ms range? No excessive animations? |
| Accessibility | WCAG 2.1 AA compliance (contrast ratio 4.5:1+, keyboard navigation, aria attributes) |
| Radix UI hydration | Is `mounted` state pattern used where needed? |

## Architecture Design (Future Extension)

## Data Model Design (Future Extension)
