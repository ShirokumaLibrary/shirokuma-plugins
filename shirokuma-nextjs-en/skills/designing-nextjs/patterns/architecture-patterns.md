# Architecture Patterns

Pattern comparison tables for Next.js architecture design decisions.

## Routing Design

### Route Organization

| Pattern | When to Use | Trade-offs |
|---------|------------|------------|
| Flat routes (`app/page/page.tsx`) | Simple apps, few pages | Simple but doesn't scale |
| Route groups (`app/(group)/page/`) | Shared layouts, auth boundaries | More directories, but clear boundaries |
| Parallel routes (`@slot`) | Dashboard panels, modals | Complex but enables independent loading |
| Intercepting routes (`(.)path`) | Modal overlays with shareable URLs | Powerful but hard to debug |

### Layout Boundaries

| Pattern | When to Use | Example |
|---------|------------|---------|
| Root layout | Global shell (nav, footer) | `app/layout.tsx` |
| Route group layout | Auth-gated sections | `app/(dashboard)/layout.tsx` |
| Nested layout | Section-specific chrome | `app/(dashboard)/settings/layout.tsx` |
| No layout (page only) | Standalone pages (login, error) | `app/login/page.tsx` |

### Decision: Route Groups vs Flat

| Criterion | Route Groups | Flat |
|-----------|-------------|------|
| Shared layout needed | Recommended | Layout duplication |
| Auth boundary | Recommended | Middleware-only |
| 5+ related pages | Recommended | Acceptable |
| 1-3 independent pages | Overhead | Recommended |

## Component Hierarchy

### Server vs Client Component Boundary

| Pattern | Use When | Example |
|---------|----------|---------|
| Server Component (default) | Static content, data fetching, no interactivity | Page, layout, data display |
| Client Component (`"use client"`) | Event handlers, useState, useEffect, browser APIs | Forms, interactive widgets |
| Composition (Server wraps Client) | Mix of static + interactive | Server fetches data, passes to Client form |
| Client-only subtree | Heavily interactive section | Dashboard with drag-and-drop |

### Component Boundary Rules

```
Page (Server)
  -> Layout sections (Server)
    -> Data display (Server)
    -> Interactive widget (Client)
      -> Client children (Client - boundary inherited)
```

**Key principle**: Push `"use client"` as deep as possible. Keep data-fetching components as Server Components.

### Composition Patterns

| Pattern | When to Use | Example |
|---------|------------|---------|
| Container/Presentational | Data fetching separated from display | `UserContainer` (Server) -> `UserCard` (Client) |
| Slot pattern | Flexible layout composition | `<Layout sidebar={<Sidebar />}>` |
| Render props via children | Server Component passes content to Client | `<Modal>{serverContent}</Modal>` |
| Parallel data fetching | Independent data sources | `Promise.all([getUser(), getPosts()])` |

## Data Layer

### Server Actions vs API Routes

| Criterion | Server Actions | API Routes |
|-----------|---------------|------------|
| Same-origin form submission | Recommended | Overhead |
| External API consumption | Possible but awkward | Recommended |
| Webhook endpoints | Not supported | Recommended |
| Progressive enhancement | Built-in | Manual |
| File uploads | Supported (FormData) | Supported |
| Third-party client access | Not supported | Recommended |

### Server Action Patterns

| Pattern | When to Use | Structure |
|---------|------------|-----------|
| Single action per file | Simple CRUD | `lib/actions/create-user.ts` |
| Grouped actions | Related operations | `lib/actions/user-actions.ts` |
| Action with revalidation | After mutation | `revalidatePath()` / `revalidateTag()` |
| Action with redirect | After create/delete | `redirect('/path')` |

### Security Checklist for Server Actions

1. **Auth check**: Verify session at the start
2. **CSRF protection**: Framework-level (built into Server Actions)
3. **Input validation**: Zod schema validation
4. **Authorization**: Verify ownership/permissions
5. **Rate limiting**: For destructive operations

## Middleware

### Middleware Responsibilities

| Responsibility | Appropriate | Why |
|----------------|------------|-----|
| Auth redirect (unauthenticated -> login) | Yes | Runs before page render |
| i18n locale detection | Yes | Needs to run on all routes |
| Security headers | Yes | Global concern |
| Feature flags (header-based) | Yes | Low overhead |
| Heavy data fetching | No | Blocks all routes |
| Per-page authorization | No | Use layout/page-level checks |
| Complex business logic | No | Hard to test and debug |

### Middleware Ordering

```
Request
  -> 1. Security headers
  -> 2. i18n locale detection
  -> 3. Auth check (redirect if unauthenticated)
  -> 4. Feature flags
  -> Page render
```

### Matcher Configuration

| Pattern | When to Use |
|---------|------------|
| `matcher: ['/dashboard/:path*']` | Protect specific sections |
| `matcher: ['/((?!api\|_next\|static).*)']` | Protect all except static/API |
| Conditional in middleware body | Complex path-based logic |

## Data Flow

### State Management Decision

| Approach | When to Use | Trade-offs |
|----------|------------|------------|
| Server Component props | Static or server-fetched data | Simplest, no client JS |
| URL search params | Filterable/sortable lists | Shareable, but limited types |
| React Context | Shared client state (theme, auth) | Re-renders on change |
| Zustand/Jotai | Complex client state | Extra dependency |
| Server Actions + revalidation | Mutation -> refetch cycle | Framework-native |

### Caching Strategy

| Layer | Mechanism | When |
|-------|-----------|------|
| Request deduplication | `fetch` in Server Components | Same request in multiple components |
| Data Cache | `fetch` with `revalidate` option | API responses |
| Full Route Cache | Static/dynamic rendering | Entire pages |
| Router Cache | Client-side navigation | Previously visited routes |

### Revalidation Patterns

| Pattern | When to Use |
|---------|------------|
| `revalidatePath('/path')` | After mutation affecting a specific page |
| `revalidateTag('tag')` | After mutation affecting tagged fetches |
| `router.refresh()` | Client-side force refresh |
| Time-based (`revalidate: 60`) | Stale-while-revalidate for semi-static data |
