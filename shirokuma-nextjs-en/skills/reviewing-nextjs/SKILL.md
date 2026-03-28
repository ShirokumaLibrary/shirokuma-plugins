---
name: reviewing-nextjs
description: Reviews Next.js application code with framework-specific perspectives. Covers App Router, Server Components, Server Actions, middleware, performance, and security. Triggers: "Next.js review", "App Router review", "Server Actions review", "nextjs review", "framework review".
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

# Next.js Code Review

Review Next.js code from a framework-specific perspective. Focus on App Router conventions, Server/Client Component boundaries, Server Action security, and performance patterns.

## Scope

- **Category:** Investigation Worker
- **Scope:** Code reading (Read / Grep / Glob / Bash read-only), generating review reports. No code modifications.
- **Out of scope:** Code modifications or implementation (delegate to `coding-nextjs`), running tests

## Review Criteria

### App Router / Routing

| Check | Issue | Fix |
|-------|-------|-----|
| Page file naming | Non-standard names other than `page.tsx` / `layout.tsx` | Follow App Router conventions |
| Route groups | Incorrect use of `(group)` | Verify alignment with layout-sharing intent |
| Loading / Error UI | Missing `loading.tsx` / `error.tsx` | Recommend adding for improved UX |
| Metadata API | Choosing between static `metadata` and dynamic `generateMetadata` | Use dynamic when data-dependent |

### Server Components / Client Components

| Check | Issue | Fix |
|-------|-------|-----|
| SC/CC boundary | Data fetching in CC | Move to SC; CC handles interaction only |
| Overuse of `"use client"` | Unnecessary conversion to CC | Reconsider whether SC can be used |
| Async in CC | Using `async/await` directly in CC | Fetch in SC and pass via Props |
| SC to CC data passing | Deep Props drilling | Consider composition pattern |
| Server-only imports | Importing `server-only` modules in CC | Protect with `server-only` package |

### Server Actions

| Check | Issue | Fix |
|-------|-------|-----|
| Auth check | Actions without authentication | Add session validation at the top |
| CSRF protection | Mutations without CSRF token verification | Use Better Auth or next-safe-action CSRF features |
| Input validation | Unvalidated user input | Server-side validation with Zod or equivalent |
| Error handling | Only throwing errors | Return user-friendly error messages |
| `@serverAction` annotation | Missing JSDoc annotation | Add `@serverAction` + `@param` |
| Direct DB access | Raw SQL without ORM | Use Drizzle or another ORM |

### Performance

| Check | Issue | Fix |
|-------|-------|-----|
| `next/image` | Using `<img>` tags | Replace with `Image` component |
| Cache strategy | No `fetch` cache configuration | Explicitly set `cache: 'force-cache'` / `revalidate` |
| Dynamic imports | Large CC with static imports | Use `next/dynamic` for lazy loading |
| Font optimization | Manually defined `@font-face` | Use `next/font` |
| Streaming | SC with long wait times | Use `Suspense` for progressive rendering |

### Security

| Check | Issue | Fix |
|-------|-------|-----|
| CVE-2025-29927 | Middleware-only authentication | Double-check at Edge + Server |
| Env variable exposure | Non-`NEXT_PUBLIC_` secret variables referenced in CC | Use server-side only |
| Header injection | Using `headers()` values without sanitization | Sanitization required |
| Open redirect | Building redirect URL from user input | Restrict with allowlist |

### i18n (next-intl)

| Check | Issue | Fix |
|-------|-------|-----|
| Hardcoded strings | UI strings embedded directly in JSX | Use `useTranslations()` |
| Missing message keys | Translation keys missing on one side | Add to both ja/en message files |
| Locale routing | Routes without `[locale]` | Verify i18n routing configuration |

## Workflow

### 1. Identify Target Files

```bash
# Check changed files
git diff --name-only origin/develop...HEAD 2>/dev/null || git diff --name-only HEAD~1 HEAD

# Check App Router structure
find app -name "*.tsx" -o -name "*.ts" | head -30

# Check Server Actions
grep -r '"use server"' --include="*.ts" --include="*.tsx" -l
```

### 2. Run Lints

```bash
# Run all lints at once (recommended)
shirokuma-docs lint all -p .

# Or individually
shirokuma-docs lint code -p . -f terminal
shirokuma-docs lint annotations -p . -f terminal
```

### 3. Code Analysis

Read changed files and apply the review criteria tables.

Priority check order:
1. Server Action security (auth / CSRF / validation)
2. Appropriateness of SC/CC boundaries
3. Performance patterns (`next/image`, caching)
4. i18n consistency

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
{List Critical/High issues}

### Improvements
{List Medium/Low improvement suggestions}

### Best Practices
{Acknowledge good implementation patterns}
```

### 5. Save Report

When PR context is present:
```bash
shirokuma-docs items add comment {PR#} --file /tmp/shirokuma-docs/review-nextjs.md
```

When no PR context:
```bash
# Set title: "[Review] next.js: {target}" and category: Reports in frontmatter first
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/review-nextjs.md
```

## Review Verdict

State clearly upon review completion:

- **PASS**: `**Review result:** PASS` — No critical issues
- **FAIL**: `**Review result:** FAIL` — Critical/High issues found

## Notes

- **Do not modify code** — Report findings only. Fixes are handled by `coding-nextjs`
- When delegated from `review-issue`'s `nextjs` role, follow `review-issue`'s report saving logic
- Always check `known-issues.md` rule for the Next.js version (e.g., CVE-2025-29927)
