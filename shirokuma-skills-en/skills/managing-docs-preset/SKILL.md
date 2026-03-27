---
name: managing-docs-preset
description: Standardizes adding/updating/versioning BUILTIN_PRESETS. Use this when registering a new library's documentation source.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Docs Preset Management

Skill for adding, updating, and versioning entries in `BUILTIN_PRESETS`.

## Versioning Convention

Defined in `.shirokuma/rules/shirokuma-docs/docs-preset-versioning.md`. Key points:

- Format: `{name}-{version}` (hyphen-separated)
- Version is determined by **the version introducing new features**
- Semantic versioning → major version (e.g., `react-19`, `vitest-4`)
- 0.x libraries → `{name}-0` (e.g., `drizzle-0`)
- Exceptions (no version): `claude-code`, `shadcn-ui`

## Steps to Add a Preset

### 1. Determine the preset name

```
{library-name}-{major-version}
```

### 2. Choose a strategy

| Strategy | Use case |
|----------|---------|
| `individual` | Fetch individual MD files from llms.txt links |
| `full-split` | Split and fetch from llms-full.txt |
| `{library}-github` | Fetch .md files from GitHub (per-library strategy file) |

Check if llms.txt is available:

```bash
curl -I https://{domain}/llms.txt
```

### 3. Add an entry to `BUILTIN_PRESETS`

File: `src/commands/docs/fetch.ts`

**llms.txt-based (individual):**
```typescript
"zod-4": {
  url: "https://zod.dev/llms.txt",
  linkFormat: "md",   // or "clean"
  fetchStrategy: "individual",
  packageNames: ["zod"],
},
```

**llms-full.txt-based (full-split):**
```typescript
"svelte-5": {
  url: "https://svelte.dev/llms.txt",
  fullUrl: "https://svelte.dev/llms-full.txt",
  linkFormat: "clean",
  fetchStrategy: "full-split",
  splitPattern: "^# ",
  sectionFormatter: "passthrough",
  packageNames: ["svelte"],
},
```

**GitHub-based (per-library strategy):**

For GitHub repos, create a **per-library strategy file**. Each library's docs structure differs, so no generic strategy is used.

1. Create `src/commands/docs/strategies/{library}-github.ts` (copy an existing strategy and adjust)
2. Set `fetchStrategy` to the file name

```typescript
"handlebars-4": {
  url: "https://github.com/handlebars-lang/docs",
  fetchStrategy: "handlebars-github",  // per-library strategy file
  repoPath: "src",
  branch: "master",
  packageNames: ["handlebars"],
},
```

### 4. Update tests if needed

- `__tests__/commands/docs.test.ts` — preset existence check
- `__tests__/commands/docs/detect.test.ts` — packageNames check

### 5. Verify build and tests

```bash
pnpm build && pnpm test -- --testPathPattern="docs"
```

## Determining linkFormat

```bash
curl -s https://{domain}/llms.txt | head -20
```

| Link format | linkFormat |
|------------|-----------|
| `[text](https://example.com/page.md)` with `.md` | `"md"` |
| `[text](https://example.com/page)` without extension | `"clean"` |

## Completion Report Template

```
## Preset Addition Complete

**Preset name:** {name}-{version}
**Strategy:** {fetchStrategy}
**packageNames:** {packages}
**File:** src/commands/docs/fetch.ts
```
