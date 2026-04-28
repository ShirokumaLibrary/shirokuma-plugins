---
name: reviewing-shadcn-ui
description: Reviews UI code using shadcn/ui and Tailwind CSS v4. Covers component usage patterns, accessibility, Tailwind v4-specific issues, and hydration safeguards. Triggers: "UI review", "shadcn review", "Tailwind review", "component review", "accessibility review".
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# shadcn/ui UI Code Review

Review shadcn/ui component usage patterns, correct Tailwind CSS v4 usage, accessibility, and hydration issues.

## Scope

- **Category:** Investigation Worker
- **Scope:** Code reading (Read / Grep / Glob / Bash read-only), generating review reports. No code modifications.
- **Out of scope:** UI implementation (delegate to `designing-shadcn-ui` / `coding-nextjs`)

## Review Criteria

### shadcn/ui Components

| Check | Issue | Fix |
|-------|-------|-----|
| Direct DOM manipulation | Using `ref.current.style` inside Radix UI components | Control via state / className |
| Component overrides | Directly modifying shadcn component internals | Customize with `className` prop |
| Nested Dialogs | Nesting `Dialog` inside another `Dialog` | Check portal configuration |
| Form integration | Missing `react-hook-form` integration | Use `FormField` / `useFormContext` pattern |
| Toast / Sonner | Mixing old `useToast` with new `sonner` | Unify to project standard |

### Radix UI Hydration

| Check | Issue | Fix |
|-------|-------|-----|
| SSR hydration mismatch | Radix components crashing during SSR | Use `mounted` state pattern |
| Hydration mismatch | Different server/client DOM | Initialize state with `useEffect` |

**Required pattern:**
```tsx
const [mounted, setMounted] = useState(false)
useEffect(() => { setMounted(true) }, [])
if (!mounted) return <PlaceholderWithoutRadixUI />
return <ComponentWithRadixUI />
```

### Tailwind CSS v4

| Check | Issue | Fix |
|-------|-------|-----|
| CSS variable syntax | `w-[--width]` (v3 syntax) | `w-[var(--width)]` (v4 syntax) |
| `@apply` usage | Behavior changed in v4 | Prefer CSS variables + `@theme` |
| `@property` inheritance | CSS custom property inheritance issue | Use `@theme inline` |
| Dark mode | Manual `dark:` class toggling | Verify integration with `next-themes` |
| Color tokens | Direct color values used | Use tokens defined in `@theme` |
| Overuse of arbitrary values | Frequent `w-[347px]` etc. | Use design tokens or spacing scale |

### Accessibility

| Check | Issue | Fix |
|-------|-------|-----|
| aria-label | Interactive elements without aria-label / aria-labelledby | Add labels for screen readers |
| Keyboard operation | `onClick` only, no `onKeyDown` | Add Enter / Space key handlers |
| Focus ring | `outline-none` hiding focus indicator | Keep `focus-visible:ring` |
| Color contrast | Below WCAG AA standard (4.5:1) | Verify contrast ratio |
| img alt | `<Image>` missing or empty `alt` | Add meaningful alt text |
| Loading state | No `aria-busy` during button loading | Add `aria-busy="true"` |
| Dialog aria | Missing `DialogTitle` | Add as `sr-only` at minimum |

### Performance

| Check | Issue | Fix |
|-------|-------|-----|
| Animations | Overuse of `transition-all` | Specify properties (`transition-colors` etc.) |
| Unnecessary re-renders | Inline functions / anonymous objects in Props | Consider `useCallback` / `useMemo` |
| Large components | Too much logic in one file | Suggest splitting |

### Design Consistency

| Check | Issue | Fix |
|-------|-------|-----|
| Spacing | Mix of `p-3` and `p-4` | Unify spacing scale |
| Font size | Arbitrary values (`text-[15px]`) | Use Tailwind type scale |
| Color usage | Primary color as both `blue-500` and `primary` | Unify to `@theme` tokens |

## Workflow

### 1. Identify Target Files

```bash
# Check component files
find components -name "*.tsx" | head -30
find app -name "*.tsx" | head -20

# Check shadcn component usage
grep -r "from '@/components/ui/" --include="*.tsx" -l | head -20

# Check direct Radix UI usage
grep -r "from '@radix-ui/" --include="*.tsx" -l | head -10
```

### 2. Run Lints

```bash
shirokuma-docs lint code -p . -f terminal
shirokuma-docs lint structure -p . -f terminal
```

### 3. Code Analysis

Read component files and apply the review criteria tables.

Priority check order:
1. Hydration issues (runtime crash)
2. Accessibility violations (Critical)
3. Tailwind v4 syntax issues
4. Design consistency

### 4. Generate Report

```markdown
## Review Summary

### Issue Summary
| Severity | Count |
|----------|-------|
| Critical | {n} |
| High | {n} |
| Medium | {n} |
| Low | {n} |
| **Total** | **{n}** |

### Critical Issues
{List hydration / accessibility issues}

### Improvements
{List Tailwind v4 migration / design consistency suggestions}
```

### 5. Save Report

When PR context is present:
```bash
shirokuma-docs issue comment {PR#} --file /tmp/shirokuma-docs/review-shadcn-ui.md
```

When no PR context:
```bash
# Set title: "[Review] shadcn-ui: {target}" and category: Reports in frontmatter first
shirokuma-docs discussion add --file /tmp/shirokuma-docs/review-shadcn-ui.md
```

## Review Verdict

- **PASS**: `**Review result:** PASS` — No critical issues
- **FAIL**: `**Review result:** FAIL` — Critical/High issues found (including hydration crashes / serious accessibility violations)

## Notes

- **Do not modify code** — Report findings only
- Check Tailwind CSS version (v3 / v4) in `package.json` before applying v4-specific checks
- Accessibility violations should be treated as High or above (Critical when legal risk exists)
