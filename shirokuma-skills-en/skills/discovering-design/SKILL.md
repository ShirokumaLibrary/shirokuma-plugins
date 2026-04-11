---
name: discovering-design
description: Establishes design direction before writing code. Creates a Design Brief, determines Aesthetic Direction, and obtains user confirmation. Called as Phase 2 of design-flow via Skill tool.
allowed-tools: WebSearch, AskUserQuestion
---

# Design Discovery

Establishes design direction before writing code. Called as Phase 2 of `design-flow`.

## Context

The following context is passed from the calling `design-flow`:

- Issue body (design requirements)
- Plan section (if available)
- Technical constraints (framework, existing design system, etc.)

## Workflow

### Step 1: Create Design Brief

Create a Design Brief using the following format:

```markdown
## Design Brief

**Purpose**: What problem does this interface solve?
**Context**: Technical constraints, existing design system
**Differentiation**: What makes this UNFORGETTABLE?
```

### Step 2: Reference Design Research (Optional)

Use `WebSearch` to research design references and trends as needed.

Run this step when the issue requirements do not specify a concrete design style, or when designing new UI components.

### Step 3: Determine Aesthetic Direction

Determine the Aesthetic Direction using the following format:

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

### Step 4: User Confirmation

Present the design direction via `AskUserQuestion` and obtain approval:

- Design Brief summary
- Aesthetic Direction
- Reference designs (if researched)

Present choices:
1. **Approve** → Design discovery complete, return to caller
2. **Request changes** → Receive feedback and redo from Step 3
3. **Re-research** → Redo from Step 2

## Output

Once user approval is obtained, return the following to the caller (`design-flow`):

- Finalized Design Brief
- Finalized Aesthetic Direction
- Reference designs (if researched)

## Tool Usage

| Tool | When |
|------|------|
| WebSearch | Design reference research (optional) |
| AskUserQuestion | Design direction confirmation (Step 4) |

## Notes

- Do not proceed to implementation without user approval — implementing without alignment risks extensive rework
- This skill uses `AskUserQuestion` and must be called via Skill tool (main context); Agent delegation is not allowed
