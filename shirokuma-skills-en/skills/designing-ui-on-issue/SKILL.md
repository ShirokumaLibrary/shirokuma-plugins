---
name: designing-ui-on-issue
description: Orchestrates the design workflow including discovery and visual evaluation loops, then delegates implementation to designing-shadcn-ui. Triggers: "design", "UI", "memorable", "impressive".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, AskUserQuestion, TodoWrite, Skill
---

# Design Workflow (Orchestrator)

Orchestrate design discovery, implementation delegation, and visual evaluation loops. Delegates implementation to `designing-shadcn-ui` and ensures design quality through iterative user interaction.

**Note**: Delegated from `working-on-issue`, but also supports standalone invocation. Non-subagent skill (requires iterative user interaction via AskUserQuestion).

## Workflow

### Phase 1: Context Reception

Receive the following context from `working-on-issue`:

| Field | Required | Content |
|-------|----------|---------|
| Issue number | Yes | `#{number}` |
| Plan section | Yes (if exists) | Extracted from `## Plan` in issue body |
| Design requirements | No | Design-related requirements from issue body |

For standalone invocation, confirm issue number via `AskUserQuestion` or understand work from text description.

### Phase 2: Design Discovery

Establish design direction before writing code.

#### 2a. Create Design Brief

```markdown
## Design Brief

**Purpose**: What problem does this interface solve?
**Context**: Technical constraints, existing design system
**Differentiation**: What makes this UNFORGETTABLE?
```

#### 2b. Reference Design Research (Optional)

Use `WebSearch` to research design references and trends as needed.

#### 2c. Determine Aesthetic Direction

```markdown
## Aesthetic Direction

**Tone**: [Choose ONE]
- Brutally minimal / Maximalist chaos / Retro-futuristic
- Organic/natural / Luxury/refined / Playful/toy-like
- Editorial/magazine / Brutalist/raw / Art deco/geometric

**Typography**: [Font pairing and rationale]
**Color Palette**: [5-7 HEX codes]
**Motion Strategy**: [Key animation moments]
```

#### 2d. User Confirmation

Present design direction via `AskUserQuestion` and obtain approval:

- Design Brief summary
- Aesthetic Direction
- Reference designs (if researched)

### Phase 3: Delegate to designing-shadcn-ui

Invoke `designing-shadcn-ui` via `Skill` tool. Pass the following context:

- Design Brief
- Aesthetic Direction
- Technical constraints (from Phase 1 context)
- Plan section (if available)

### Phase 4: Visual Evaluation Loop

After implementation completes, conduct visual evaluation with user.

#### 4a. Dev Server Check

```bash
# Check if dev server is running
lsof -i :3000 2>/dev/null || echo "dev server not running"
```

Suggest starting it if needed.

#### 4b. User Review

Present via `AskUserQuestion`:

- List of changed file paths
- Review URL (if dev server is running)
- Review checklist:
  - [ ] Typography is distinctive
  - [ ] Color palette is cohesive
  - [ ] Motion/animation impression
  - [ ] Layout visual interest
  - [ ] Overall impression

Present choices:
1. **Approve** → Proceed to Phase 5
2. **Request changes** → Receive feedback, return to Phase 3
3. **Change direction** → Return to Phase 2

#### 4c. Safety Limit

Visual evaluation loop is limited to **3 iterations maximum**. On reaching the limit, proceed with current state and suggest follow-up Issue for further improvements.

### Phase 5: Completion

Design work is complete once approved. When in `working-on-issue` chain, control returns automatically to the orchestrator.

## Standalone Invocation

Additional steps when invoked standalone:

1. Confirm issue number (`AskUserQuestion`)
2. Execute all Phases
3. Suggest next steps after completion

## Next Steps

When in `working-on-issue` chain, control returns automatically to the orchestrator.

When invoked standalone:

```
Design complete. Next steps:
→ `/committing-on-issue` to stage and commit your changes
→ Use `/working-on-issue` for the full workflow
```

## Extensibility

Initial implementation delegates to `designing-shadcn-ui` only, but future delegation to other design implementation skills is anticipated:

| Delegate To | Condition | Status |
|-------------|-----------|--------|
| `designing-shadcn-ui` | shadcn/ui + Tailwind projects | Supported |
| (Future) other design skills | Different stacks | Not implemented |

## Tool Usage

| Tool | When |
|------|------|
| AskUserQuestion | Design direction confirmation, visual evaluation loop |
| TodoWrite | Phase progress tracking |
| Skill | Delegation to `designing-shadcn-ui` |
| WebSearch | Design reference research (optional) |
| Bash | Dev server check, build verification |

## Notes

- Non-subagent skill (requires iterative user interaction via AskUserQuestion)
- Confirm design direction with user before implementation — implementing without alignment risks extensive rework
- Visual evaluation loop limited to 3 iterations maximum
- `designing-shadcn-ui` handles build verification (not needed in this skill)
