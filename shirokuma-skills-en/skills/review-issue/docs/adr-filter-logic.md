# ADR Filter Logic Specification

> **Note**: This role has been migrated to `analyze-issue`. For the current specification, see `analyze-issue/docs/adr-filter-logic.md`.

Defines the ADR filtering method used by `analyze-issue requirements` when performing Project Requirement Consistency checks.

## Overview

**Confirmed method:** Extract 3-5 keywords from the Issue title and `##`-level headings → Use `shirokuma-docs items discussions search "<keywords>"` for initial filtering → Retrieve details for up to 5 results (`items adr get {number}`)

```bash
# Initial filtering
shirokuma-docs items discussions search "<extracted keywords>"

# Retrieve details (top 5)
shirokuma-docs items adr get {number}
```

## Keyword Extraction Rules

### Extraction Targets

- Nouns and proper nouns in the Issue title
- Nouns and proper nouns in `##`-level headings in the body

### Stop Words to Exclude

Exclude the following generic terms:

- Generic verbs: "add", "fix", "handle", "implement", "change", "update", "create", "delete"
- Generic nouns: "project", "feature", "process", "target", "method", "approach", "content", "configuration"

### Priority Order (when more than 3-5 candidates exist)

1. First word(s) in the title
2. Heading words
3. Body keywords

### Label Supplementation

Add the value portion of `area:*` labels as additional keywords (e.g., `area:plugin` → `plugin`, `area:cli` → `cli`).

## Fallback

When search returns zero results:

```bash
shirokuma-docs items adr list
```

Retrieve the full list of ADR titles and switch to lightweight title-only reference (do not retrieve body details).

## Upper Limit

- Retrieve details for a maximum of 5 results
- When more than 5 results hit: narrow down to top 5 by relevance score (title match priority)

## Exclusion Conditions

Exclude ADRs with Superseded/Deprecated status from filtered results.

**Exception:** For the "re-adoption check" (check item 3), review Superseded ADRs separately:

```bash
# Search including Deprecated/Superseded ADRs (for re-adoption check only)
shirokuma-docs items discussions search "<keyword>"
# → Identify entries with "Deprecated" or "Superseded" in the title and review them
```

## Execution Example

Issue title: "Change the trigger keyword design for skills"
Labels: `area:plugin`

1. Keyword extraction: "skill", "trigger keyword", "design", "plugin" (4 items)
2. Search: `shirokuma-docs items discussions search "skill trigger keyword"`
3. Hits: ADR-003 (skill architecture), ADR-007 (branch model) → prioritize ADR-003
4. Detail retrieval: `shirokuma-docs items adr get {ADR-003 discussion number}`
5. Consistency check: Compare ADR-003 content with the Issue's direction
