# Progress Report Examples

Progress reporting format examples for each role.

## Standard Role (security example)

```text
Step 1/6: Selecting role...
  Role: security
  Files to load: tech-stack, security, better-auth, known-issues

Step 2/6: Loading knowledge...

Step 3/6: Running shirokuma-docs lints...

Step 4/6: Analyzing code...
  lib/auth.ts - 3 findings
  lib/actions/users.ts - 1 finding

Step 5/6: Generating report...
  2 Critical, 1 Warning, 1 Info

Step 6/6: Saving report...
  GitHub Discussions (Reports)
```

## config role

```text
Step 1/6: Selecting role...
  Role: code → config (auto-switched by changed file analysis)
  Changed files: plugin/shirokuma-skills-ja/skills/review-issue/SKILL.md etc. 2 files
  Files to load: reviewing-claude-config/SKILL.md

Step 2/6: Loading knowledge...

Step 3/6: Running lints... Skipped (config role)

Step 4/6: Analyzing config files...
  SKILL.md - 0 temporary markers, 0 broken links
  plugin.json - version consistency OK

Step 5/6: Generating report...
  0 Critical, 1 Warning

Step 6/6: Saving report...
  PR #{number} comment
```

## plan role

```text
Step 1/6: Selecting role...
  Role: plan
  Files to load: CLAUDE.md, .claude/rules/

Step 2/6: Loading knowledge...

Step 3/6: Running lints... Skipped (plan role)

Step 4/6: Analyzing plan...
  Issue #42 - Plan section analysis
  Requirements coverage: 5/5, Task granularity: appropriate

Step 5/6: Generating report...
  0 Critical, 2 Improvements

Step 6/6: Saving report...
  Issue #42 comment
```

## design role

```text
Step 1/6: Selecting role...
  Role: design
  Files to load: CLAUDE.md, .claude/rules/, criteria/design

Step 2/6: Loading knowledge...

Step 3/6: Running lints... Skipped (design role)

Step 4/6: Analyzing design...
  Issue #42 - Design Brief, Aesthetic Direction analysis
  Design Brief quality: appropriate, Token definitions: 3 missing

Step 5/6: Generating report...
  0 Critical, 3 Improvements

Step 6/6: Saving report...
  Issue #42 comment
```

## Multi-Role (Auto-Detection Mode)

```text
Step 1/6: Selecting role...
  Multi-role detected: code, security
  Execution order: code → security

[code role]
Step 2/6: Loading knowledge...
Step 3/6: Running shirokuma-docs lints...
Step 4/6: Analyzing code...
Step 5/6: Generating report...
Step 6/6: Saving report...

[security role]
Step 2/6: Loading knowledge...
Step 3/6: Running shirokuma-docs lints...
Step 4/6: Analyzing code...
Step 5/6: Generating report...
Step 6/6: Saving report...
```
