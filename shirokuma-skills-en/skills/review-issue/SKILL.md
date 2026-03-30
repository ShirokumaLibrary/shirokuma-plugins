---
name: review-issue
description: Provides comprehensive review workflow with specialized roles for code quality, security, testing patterns, documentation, plan quality, design quality, and research quality. Triggers: "review", "security audit", "security check", "test review", "test quality", "Next.js review", "docs review", "plan review", "design review", "research review", "code review", "config review".
allowed-tools: Read, Grep, Glob, Bash, WebSearch, WebFetch
---

## Project Rules

!`shirokuma-docs rules inject --scope review-worker`

# Issue Reviewing Skill

Comprehensive review workflow with specialized roles for different review types.

## Available Roles

| Role | Focus | Trigger |
|------|-------|---------|
| **code** | Quality, patterns, style | "review", "コードレビュー" |
| **config** | Config file quality, best practices compliance | Auto-detected from `code` role, or "config review", "設定レビュー" |
| **code+annotation** | JSDoc annotations | "annotation review", "アノテーションレビュー" |
| **security** | OWASP, CVEs, auth | "security review", "セキュリティ" |
| **testing** | TDD, coverage, mocks | "test review", "テストレビュー" |
| **nextjs** | Framework, patterns (delegates to `reviewing-nextjs` with fallback) | "Next.js review", "プロジェクト" |
| **docs** | Markdown structure, links, terminology | "docs review", "ドキュメントレビュー" |
| **plan** | Requirements coverage, task granularity, risks | "plan review", "計画レビュー" |
| **design** | Design Brief, Aesthetic Direction, UI implementation | "design review", "設計レビュー" |
| **research** | Requirement alignment, research quality, implementability | "research review", "リサーチレビュー" |

## Workflow

```
Role Selection → Load Knowledge → Run Lints → Analyze Code/Plan → Generate Report → Save Report
```

**6 Steps**: Select Role → Load → **Lint** → Analyze → Report → Save

### 1. Role Selection

Based on user request, select appropriate role:

| Keyword | Role | Files to Load |
|---------|------|---------------|
| "review", "レビュー" | code | criteria/code-quality, criteria/coding-conventions, patterns/server-actions, patterns/drizzle-orm, patterns/jsdoc |
| "config review", "設定レビュー" | config | `reviewing-claude-config/SKILL.md` validation rules |
| "annotation", "アノテーション" | code+annotation | roles/code.md |
| "security", "セキュリティ" | security | criteria/security, patterns/better-auth |
| "test", "テスト" | testing | criteria/testing, patterns/e2e-testing |
| "Next.js", "nextjs" | nextjs | Discover `reviewing-nextjs` via `skills routing reviewing`; fall back to ALL knowledge files if not installed |
| "docs", "ドキュメント" | docs | roles/docs.md |
| "plan", "計画レビュー" | plan | roles/plan.md |
| "design", "設計レビュー", "デザイン" | design | criteria/design, roles/design |
| "research", "リサーチレビュー" | research | roles/research, criteria/research |

#### `nextjs` Role Dynamic Delegation (`skills routing reviewing` Integration)

When the `nextjs` role is selected, attempt dynamic discovery of `reviewing-*` skills:

```bash
shirokuma-docs skills routing reviewing
```

If a `key: "nextjs"` entry exists in the `routes` array (`reviewing-nextjs` is installed):
- **Delegate via Skill** to `reviewing-nextjs` to execute the review
- Receive the completion report from `reviewing-nextjs` and use this skill's report-saving logic to determine the output destination

If no `key: "nextjs"` entry exists (`shirokuma-nextjs` is not installed):
- Fallback: execute the traditional `nextjs` role processing (load all knowledge files)

Similarly, for other review targets (Drizzle, shadcn/ui, AWS, CDK, etc.), check the `routes` array and delegate to plugin-specific `reviewing-*` skills when available.

#### Multi-Role Auto-Detection

Scan all keywords in the user request. When 2 or more code review roles match, switch to multi-role mode.

**Detection Flow:**

```
User request
  ↓ Scan all keywords
  ↓ Generate list of matched roles
  ↓
  [1 role] → Normal single-role execution
  [2+ roles] → Sequential execution based on role execution order table
```

**Role Execution Order Table:**

| Priority | Role | Reason |
|----------|------|--------|
| 1 | code | Foundation role. Code quality insights benefit other roles |
| 2 | security | Security analysis builds on code structure understanding |
| 3 | testing | Code and security insights inform test perspectives |
| 4 | nextjs | Framework-specific insights |
| 5 | docs | Document analysis is independent of code analysis |
| 6 | code+annotation | Special mode of code |

**Excluded roles:** plan / design / research are excluded from multi-role auto-detection (they are issue analysis roles, and mixing with code review roles is unnatural).

**Exclusion rules:**
- `code` and `config` are subject to auto-switching, so when both match, the existing `config` auto-detection logic takes priority (no multi-role).
- `code` and `code+annotation` are mutually exclusive. When both match, `code+annotation` takes priority (it is a superset of `code`).

#### `config` Role Auto-Detection (when `code` role is selected)

When the role resolves to `code`, analyze changed files to auto-determine the review strategy:

```bash
git diff --name-only origin/{base-branch}...HEAD 2>/dev/null || git diff --name-only HEAD~1 HEAD
```

Match the file list against the following config file patterns:

| Pattern | Target |
|---------|--------|
| `plugin/**/*.md` | Skill files (SKILL.md), rule files (rules/*.md), agent files (AGENT.md) |
| `plugin/**/*.json` | plugin.json and other config |
| `.claude/**/*.md` | Project-local rules and skills |
| `.claude/**/*.json` | Project-local config |
| `.claude/**/*.yaml` | Project-local YAML config |

| Result | Action |
|--------|--------|
| All files match config file patterns | Switch to `config` role |
| Some or all files do not match | Keep `code` role |
| Cannot retrieve changed files | Fall back to `code` role |
| `config` explicitly specified | Skip file analysis, use `config` role |

### 2. Load Knowledge

Read required knowledge files based on role:

```
1. Auto-loaded: .claude/rules/*.md (based on file paths)
2. Role-specific: roles/{role}.md
3. Criteria: criteria/{relevant}.md
4. Patterns: patterns/{relevant}.md
```

**Note**: Project-specific rules are auto-loaded from `.claude/rules/` - no manual loading needed.

#### 2a. Local Documentation Check (code / security / testing / nextjs roles)

For code review roles (code, security, testing, nextjs), reference locally fetched documentation to improve review accuracy:

```bash
# Check available documentation sources
shirokuma-docs docs detect --format json
```

If `status: "ready"` sources exist, search with keywords related to the tech stack in the code under review:

```bash
shirokuma-docs docs search "<tech keyword>" --source <source-name> --section --limit 3
```

Skip this substep if no local documentation is available (no `ready` sources).

### 3. Run shirokuma-docs Lints (REQUIRED)

**Execute automated checks before manual review. Lint commands vary by role:**

| Role | Lint Commands |
|------|--------------|
| code, code+annotation, nextjs | `lint all` (all types at once) recommended. Individual: lint tests, lint coverage, lint code, lint structure, lint annotations |
| security | lint security, lint code, lint structure (security-related only) |
| testing | lint tests, lint coverage (test-related only) |
| docs | lint docs (document structure only) |
| config | Skip (config files are analyzed using `reviewing-claude-config` validation logic) |
| plan | Skip (target is Issue body, not code/document files) |
| design | Skip (target is Issue body / design artifacts, not code/document files) |
| research | Skip (target is research findings, not code/document files) |

**code / code+annotation / nextjs roles:**

```bash
# Recommended: run all lints at once
shirokuma-docs lint all -p .

# Individual execution (when only specific lints are needed):
# Test documentation (@testdoc, @skip-reason)
shirokuma-docs lint tests -p . -f terminal

# Implementation-test coverage
shirokuma-docs lint coverage -p . -f summary

# Code structure (Server Actions, annotations)
shirokuma-docs lint code -p . -f terminal

# Project structure (directories, naming)
shirokuma-docs lint structure -p . -f terminal

# Annotation consistency (@usedComponents, @screen)
shirokuma-docs lint annotations -p . -f terminal
```

**docs role:**

```bash
# Document structure validation
shirokuma-docs lint docs -p . -f terminal
```

**Key rules to check:**

| Rule | Description |
|------|-------------|
| `skipped-test-report` | Reports `.skip` tests (ensure `@skip-reason` present) |
| `testdoc-required` | All tests need `@testdoc` |
| `lint coverage` | Source files need corresponding tests |
| `annotation-required` | Server Actions need `@serverAction` |

See project-specific workflow documentation for detailed fix instructions.

### 4. Analyze Code / Plan

**Code roles (code, security, testing, nextjs, docs):**

1. Read target files
2. Apply criteria from loaded knowledge
3. Check against known issues
4. Cross-reference with shirokuma-docs lint results
5. Identify violations and improvements

**Config role:**

Reference the validation logic in `reviewing-claude-config/SKILL.md` and check the changed config files for:

1. Temporary markers (`TODO:`, `FIXME:`, `WIP`, `TBD`, `DRAFT`, `PLACEHOLDER`, `XXX:`, `**NEW**`)
2. Broken internal links (verify referenced files exist)
3. Required frontmatter fields (skills: `name`, `description`; agents: `name`, `description`)
4. Trigger keywords present in `description`
5. File length check (SKILL.md over 500 lines is Warning)
6. `plugin.json` version consistency (match against `package.json`)
7. Manual date stamps
8. ASCII art diagrams

**Plan role:**

1. Fetch the parent Issue via `shirokuma-docs items pull {number}` and read `.shirokuma/github/{number}.md`
2. Identify the plan issue from `subIssuesSummary` — the child issue with a title starting with "Plan:" or "計画:"
3. Fetch the plan issue body via `shirokuma-docs items pull {plan-issue-number}` and read `.shirokuma/github/{plan-issue-number}.md`
4. Extract the `## Plan` / `## 計画` section from the plan issue body as the review target
5. Evaluate each item in review checklist (`roles/plan.md`)
6. Check against anti-patterns
7. Verify consistency with requirements and deliverables

**Backward compatibility**: When no plan issue (child issue) exists but the parent issue body contains a `## Plan` / `## 計画` section (legacy approach), use the parent issue's plan section as the review target.

**Design role:**

1. Fetch Issue body via `shirokuma-docs items pull {number}` and read `.shirokuma/github/{number}.md`
2. Extract Design Brief, Aesthetic Direction, and UI implementation results
3. Evaluate each item in review checklist (`roles/design.md`)
4. Check against review criteria (`criteria/design.md`)
5. Check against anti-patterns
6. Verify requirements alignment and technical feasibility

**Research role:**

1. Fetch research findings (Discussion or Issue comment)
2. Verify requirement alignment (`criteria/research.md`)
3. Evaluate research quality (source diversity, version consistency, source attribution)
4. Verify implementability (specificity, incremental adoption, risk identification)
5. Assess alignment level using the mismatch decision matrix (`roles/research.md`)
6. Create adoption proposals for mismatched but useful patterns

**Artifact Review (only when prompt contains "Artifact review targets:" or "成果物レビュー対象:" in a PR context):**

For each `#N` listed in the "Artifact review targets:" / "成果物レビュー対象:" section of the prompt:

1. Fetch the Discussion or Issue body via `shirokuma-docs items pull {N}` and read `.shirokuma/github/{N}.md`
2. Apply the "GitHub Document Review Perspectives" from `roles/code.md`:
   - Format compliance (format appropriate for the Discussion category)
   - YAML frontmatter leakage check (metadata starting with `---` must not appear in the body)
   - Cross-reference consistency (referenced items must exist and have correct numbers)
   - Consistency with codebase (must not contradict the actual implementation)
   - Terminology consistency (no terminology drift within a single document)
3. Append artifact review results to the main code review report (using the "Artifact Review Results" section in `templates/report.md`)

This substep is skipped when neither the "Artifact review targets:" nor the "成果物レビュー対象:" section is present (backward compatibility preserved).

### 5. Generate Report

Use `templates/report.md` format:

1. Summary (include shirokuma-docs lint summary)
2. **Issue Summary** (breakdown table of detected issues by severity)
3. Critical Issues
4. Improvements
5. Best Practices
6. Recommendations

**Issue summary table** (placed immediately after the Summary section):

```markdown
### Issue Summary
| Severity | Count |
|----------|-------|
| Critical | {n} |
| High | {n} |
| Medium | {n} |
| Low | {n} |
| **Total** | **{n}** |
```

If 0 issues are found, state "No issues were detected" and omit the table.

### 6. Save Report

Route the output based on the review context.

#### PR Review (when PR number is in context)

Post review summary as a PR issuecomment (not a review thread comment):

```bash
# Write tool でファイル作成後
shirokuma-docs items add comment {PR#} --file /tmp/shirokuma-docs/{number}-review-summary.md
```

> **Note**: `items add comment` posts an issuecomment on the PR. These appear in the `issue_comments` section of `pr comments` output, separate from review thread comments.

Only save a detailed report to Discussions when there are many critical issues (severity: error, 5 or more), and link the Discussion URL in the PR comment.

#### File/Directory Review (no PR number)

Create Discussion in Reports category (existing behavior):

```bash
shirokuma-docs items add discussion --file /tmp/shirokuma-docs/review-report.md
```

Report the Discussion URL to the user.

#### Routing Summary

| Context | Primary Output | Detailed Report |
|---------|---------------|-----------------|
| PR number specified | PR comment (summary) | Discussion only if 5+ errors |
| File/directory | Discussion (Reports) | — |
| Issue number specified (plan role) | Issue comment | — |
| Issue number specified (design role) | Issue comment | — |
| Issue number specified (research role) | Issue comment | — |

> See `rules/output-destinations.md` for the full output destination policy.

## Knowledge Update

When user requests `--update`:

Technical knowledge (CVEs, versions, framework patterns, etc.) is centrally managed by the knowledge-manager agent. Delegate knowledge updates to knowledge-manager:

```
ソース更新して
```

knowledge-manager will use web search to update:
- Next.js releases and CVEs
- React updates
- Tailwind CSS changes
- Better Auth updates
- OWASP updates

After updating, run `配布して` to redistribute knowledge to skills.

## Progressive Disclosure

For token efficiency:

1. **Auto-loaded**: `.claude/rules/*.md` based on file paths being reviewed
2. **On Demand**: Load knowledge files based on role/findings
3. **Minimal Output**: Summary first, details on request

## Quick Reference

```bash
"review lib/actions/"              # Code quality
"annotation review components/"    # Annotation consistency
"security review lib/actions/"     # Security
"test review"                      # Testing
"Next.js review"                   # Next.js project
"plan review #42"                  # Plan review
"design review #42"                # Design review
"research review #42"              # Research review
"security + code review src/"      # Multi-role
"reviewer --update"                # Update knowledge
```

## Next Steps

When invoked standalone (not via `implement-flow`), suggest the next workflow step after the review:

```
Review complete. If changes were made based on findings:
→ `/commit-issue` to stage and commit your changes
```

## Execution Context

When invoked via Skill tool, this skill runs in the main context with access to project-specific rules from `.claude/rules/`. This enables rule-compliant reviews.

### Progress Reporting

See `reference/progress-report-examples.md` for progress reporting format examples for each role.

### Error Recovery

If analysis is incomplete:
1. Identify missing coverage
2. Load additional patterns
3. Re-analyze missed areas
4. Update report

## Multi-Role Execution Mode

When multiple roles are requested, this skill is invoked repeatedly for each role. There are 2 paths for multi-role execution.

### Invocation Paths

| Path | Trigger | Role Determination |
|------|---------|-------------------|
| Internal auto-detection | User request contains keywords matching multiple roles | Detected by Step 1 multi-role auto-detection |
| Caller-specified | Caller explicitly specifies multiple roles | Uses roles specified by the caller |

### Behavioral Differences

| Aspect | Normal (Single Role) | Multi-Role |
|--------|---------------------|------------|
| Role Selection | Determined from user request | Auto-detected or caller-specified |
| Execution | 6-step workflow executed once | 6-step workflow executed sequentially for each role |
| Report Save | Posted as PR/Issue comment | Posted individually per role |
| Output Template | Normal review mode output template | Same (no change) |

Each role's report is posted individually.

### Auto-Detection Mode Progress Reporting Example

See the "Multi-Role" section in `reference/progress-report-examples.md` for the multi-role progress reporting example.

### Context Sharing Between Roles

Results from earlier roles (lint results, detected issues) are available as context for subsequent roles. However, each role's report is generated independently.

## Notes

- **Reports saved**: Route based on context (PR → PR comment, files → Discussion Reports, see `rules/output-destinations.md`)
- **Role-based**: Load only relevant knowledge files
- **Progressive**: Summary first, details on request
- **Updateable**: Use `--update` to refresh knowledge
- **Rules auto-loaded**: Project conventions from `.claude/rules/` (including paths-based rules when running in main context)
- **Main context execution**: Runs via Skill tool in the main context, enabling access to project-specific rules
- **Caller's comment-first compliance**: This skill posts review comments but does not update bodies. When caller skills (`open-pr-issue`, `implement-flow`) update Issue/PR bodies based on review results, they must follow the comment-first principle in `item-maintenance.md`
- **Context boundary constraint**: When proposing fixes to config files (rules, skills) during review, do not suggest referencing other skills' `reference/` by file path. Rule context cannot access skill references — include necessary details in the rule body or mention only the skill name

## Review Result Expressions

On review completion, output the following standard expressions so that the calling orchestrator can consistently determine the result.

### Plan Review Mode (plan role)

When invoked from `prepare-flow` with plan role, post the plan review result as an Issue comment and include the following verdict.

- **PASS**: `**Review result:** PASS` — No critical issues in the plan (Suggestions may still be present)
- **NEEDS_REVISION**: `**Review result:** NEEDS_REVISION` — Missing requirements, significant inconsistencies, or anti-patterns detected

On NEEDS_REVISION, classify issues into `[Plan]` and `[Issue description]`. `plan-issue` uses this classification to perform fixes.

### Design Review Mode (design role)

When invoked with design role, post the design review result as an Issue comment and include the following verdict.

- **PASS**: `**Review result:** PASS` — No critical issues in the design (improvement suggestions may still be present)
- **NEEDS_REVISION**: `**Review result:** NEEDS_REVISION` — Missing Design Brief, uncovered requirements, accessibility violations, significant inconsistencies

### Research Review Mode (research role)

When invoked with research role, post the research review result as an Issue comment and include the following verdict.

- **PASS**: `**Review result:** PASS` — No critical issues in research findings, aligned with requirements
- **NEEDS_REVISION**: `**Review result:** NEEDS_REVISION` — Insufficient sources, version inconsistencies, critical mismatches with requirements

### Normal Review Mode (code / security / testing / docs / config roles)

Save the report to GitHub and include the following verdict.

- **PASS**: `**Review result:** PASS` — No critical issues
- **FAIL**: `**Review result:** FAIL` — Critical issues found

## Language

Review reports (PR comments, Discussions) must follow the language specified in the `output-language` rule.

## Anti-Patterns

- Avoid modifying code — the reviewer role is to report findings, not implement fixes (mixing both roles dilutes review objectivity)
- Avoid loading all knowledge files at once — role-specific loading keeps context focused and prevents information overload

## Reference Documents

| Directory | Files |
|-----------|-------|
| `criteria/` | [code-quality](criteria/code-quality.md), [coding-conventions](criteria/coding-conventions.md), [security](criteria/security.md), [testing](criteria/testing.md), [design](criteria/design.md), [research](criteria/research.md) |
| `patterns/` | [server-actions](patterns/server-actions.md), [server-actions-structure](patterns/server-actions-structure.md), [drizzle-orm](patterns/drizzle-orm.md), [better-auth](patterns/better-auth.md), [e2e-testing](patterns/e2e-testing.md), [tailwind-v4](patterns/tailwind-v4.md), [radix-ui-hydration](patterns/radix-ui-hydration.md), [jsdoc](patterns/jsdoc.md), [nextjs-patterns](patterns/nextjs-patterns.md), [i18n](patterns/i18n.md), [code-quality](patterns/code-quality.md), [account-lockout](patterns/account-lockout.md), [audit-logging](patterns/audit-logging.md), [docs-management](patterns/docs-management.md) |
| `reference/` | [tech-stack](reference/tech-stack.md), [progress-report-examples](reference/progress-report-examples.md) |
| `roles/` | [code](roles/code.md), [security](roles/security.md), [testing](roles/testing.md), [nextjs](roles/nextjs.md), [docs](roles/docs.md), [plan](roles/plan.md), [design](roles/design.md), [research](roles/research.md) |
| `templates/` | [report](templates/report.md) |
| `docs/setup/` | [auth-setup](docs/setup/auth-setup.md), [database-setup](docs/setup/database-setup.md), [infra-setup](docs/setup/infra-setup.md), [project-init](docs/setup/project-init.md), [styling-setup](docs/setup/styling-setup.md) |
| `docs/workflows/` | [annotation-consistency](docs/workflows/annotation-consistency.md), [shirokuma-docs-verification](docs/workflows/shirokuma-docs-verification.md) |

See the role selection table in Step 1 for per-role file loading.
