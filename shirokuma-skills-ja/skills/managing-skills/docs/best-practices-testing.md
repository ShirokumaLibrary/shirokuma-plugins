# Testing Strategy and Evaluation

Testing approaches, common patterns, and quality assurance for skills.

For core principles and organization, see [best-practices.md](best-practices.md).
For writing instructions, see [best-practices-writing.md](best-practices-writing.md).

## Evaluation-First Development

Create test scenarios BEFORE extensive documentation.

1. Identify capability gaps
2. Define expected behaviors
3. Create 3+ test scenarios
4. Build skill to pass tests
5. Iterate based on results

### Test scenario template

```markdown
## Test Scenario: [Name]

- **Description**: [What this tests]

##### Input

\```
[Exact input]
\```

##### Expected Output

\```
[Exact expected output]
\```

##### Expected Behavior

- Performance: [timing requirements]
- Error handling: [error scenarios]
- Edge cases: [edge case handling]

##### Success Criteria

- [ ] Output matches expected
- [ ] Completes within time limit
- [ ] Handles errors gracefully
- [ ] Works across models (Haiku, Sonnet, Opus)
```

## Multi-Model Testing Matrix

Test across Claude models:

| Test Case | Haiku | Sonnet | Opus | Notes |
|-----------|-------|--------|------|-------|
| Basic parsing | Pass | Pass | Pass | All pass |
| Complex transforms | Fail | Pass | Pass | Haiku fails edge cases |
| Error recovery | Partial | Pass | Pass | Haiku needs explicit steps |
| Multi-step workflow | Fail | Partial | Pass | Simplified for Haiku/Sonnet |

**Legend**: Pass, Partial (works with modifications), Fail

## Iterative Development with Claude

### Two-instance approach

**Claude A (Development)**:
- Create and refine skill
- Iterate on documentation
- Implement fixes

**Claude B (Testing)**:
- Use skill on real tasks
- No knowledge of implementation
- Provides user perspective

### Workflow

1. Claude A creates initial skill
2. Claude B tests on real task
3. Observe where B struggles
4. Claude A refines based on B's struggles
5. Repeat until B succeeds consistently

## Monitor Usage Patterns

Observe Claude's behavior to improve skills.

### Which files does Claude read?

- Expected files read → good organization
- Unexpected files → missing navigation cues
- Ignored files → poor linking or unclear names

### Navigation patterns

- Direct to needed file → good structure
- Wandering → unclear organization
- Re-reading same file → missing information

### Content interaction

- Uses examples → good examples
- Ignores examples → examples not relevant
- Misinterprets instructions → ambiguous writing

---

## Common Patterns

### Pattern 1: Form Processing

```markdown
# Form Processing Skill

## Workflow

1. **Analyze Form Structure**
   - Identify fields (input, select, textarea)
   - Determine required vs optional
   - Extract validation rules

2. **Prepare Data**
   - Map user data to form fields
   - Validate against rules
   - Format appropriately

3. **Submit Form**
   - Construct request
   - Handle authentication
   - Process response

See [FORMS.md](FORMS.md) for form type catalog.
See [VALIDATION.md](VALIDATION.md) for validation rules.
```

### Pattern 2: Data Transformation

```markdown
# Data Transformation Skill

## Workflow

1. **Detect Input Format**
   - Parse file extension
   - Validate structure
   - Load appropriate parser

2. **Transform Data**
   - Apply transformations
   - Handle edge cases
   - Maintain data integrity

3. **Output in Target Format**
   - Format according to spec
   - Validate output
   - Write to file

See [FORMATS.md](FORMATS.md) for supported formats.
```

### Pattern 3: Code Analysis

```markdown
# Code Analysis Skill

## Workflow

1. **Scan Codebase**
   - Find relevant files
   - Parse code structure
   - Extract metrics

2. **Analyze**
   - Identify patterns
   - Detect issues
   - Calculate metrics

3. **Generate Report**
   - Summarize findings
   - Prioritize issues
   - Provide recommendations

See [METRICS.md](METRICS.md) for available metrics.
```

---

## Anti-Patterns to Avoid

### 1. Too Many Options

**Bad (overwhelming)**:
```markdown
Choose one of these 15 approaches:
1. Approach A (option X, Y, or Z)
2. Approach B (with variations I, II, III)
3. Approach C...
```

**Good (defaults + optional)**:
```markdown
Use Approach A (recommended).

Alternative: Approach B for legacy systems.
```

### 2. Vague Naming

| Bad | Good |
|-----|------|
| helper-utils | parsing-json-data |
| processing-tool | validating-email-addresses |
| data-handler | generating-pdf-reports |
| misc-operations | transforming-csv-to-xml |

### 3. Deeply Nested References

**Bad**: SKILL.md → guide.md → details.md → specifics.md (nested chain)

**Good**: SKILL.md → guide.md, details.md, specifics.md (flat)

### 4. Windows Paths

**Bad**:
```markdown
Run: `python scripts\validate.py`
Config: `config\settings.json`
```

**Good**:
```markdown
Run: `python scripts/validate.py`
Config: `config/settings.json`
```

### 5. Time-Sensitive Information

**Bad**:
```markdown
## As of 2024
Use new API...

## Before 2024
Use old API...
```

**Good**:
```markdown
## Current API
Use v2 endpoint...

<details>
<summary>Legacy API (Deprecated)</summary>
Old v1 endpoint...
</details>
```

---

## 構造化 eval シナリオ

eval を JSON 形式の構造化シナリオで形式化する。プロジェクトの eval ディレクトリに `scenarios.json` として配置する。

### シナリオ種別

| 種別 | 目的 | 最低件数 |
|------|------|---------|
| trigger | description のトリガー精度を検証（起動すべき/すべきでない） | 5 件以上 |
| quality | ワークフロー遵守度と出力の正確性を検証 | 3 件以上 |

### trigger eval 形式

```json
{
  "id": "trigger-01",
  "type": "trigger",
  "prompt": "CSV を JSON に変換して",
  "expected": "should_trigger",
  "rationale": "データ変換の基本的なトリガー表現"
}
```

- **should_trigger**: このプロンプトでスキルが起動されるべき
- **should_not_trigger**: このプロンプトでスキルが起動されるべきではない（別スキルの責務）
- 両方を含めて description フィールドの精度と再現率をテストする

### quality eval 形式

```json
{
  "id": "quality-01",
  "type": "quality",
  "prompt": "users.csv を JSON 形式に変換して",
  "context": {
    "input_format": "CSV",
    "output_format": "JSON",
    "has_headers": true
  },
  "assertions": [
    {
      "text": "入力ファイルを Read で読み込んでから処理する",
      "category": "workflow"
    },
    {
      "text": "出力が有効な JSON であることを検証する",
      "category": "output"
    }
  ]
}
```

**assertion カテゴリ**: `workflow`（ステップ順序、事前条件の確認）、`convention`（命名規約、フォーマット）、`tooling`（ツール使用）、`output`（出力形式、成果物）

**重要ルール**: assertion は**観測可能な行動**を記述する。主観的な品質ではない。「入力ファイルを Read で読み込む」（検証可能）vs「良い変換を行う」（主観的）。

### ファイル構成

```json
{
  "skill_name": "converting-data",
  "version": "1.0.0",
  "scenarios": []
}
```

トップレベルに `skill_name`（SKILL.md の name と一致）と `version`（スキルバージョン）を含める。スキル更新時にシナリオの更新も必要か確認する。

---

## Evaluation and Iteration

### Build Evaluations First

Before writing extensive documentation:

1. Define success criteria
2. Create 3+ test scenarios
3. Document expected behaviors
4. Build to pass tests

### Iterative Refinement Cycle

1. **Create** initial skill (Claude A)
2. **Test** with fresh instance (Claude B)
3. **Observe** where B struggles
4. **Analyze** root causes
5. **Refine** documentation (Claude A)
6. **Repeat** until consistent success

### What to observe

- Misunderstood instructions → ambiguous writing
- Wrong file accessed → poor navigation
- Ignored relevant content → bad organization
- Repeated mistakes → missing explicit guidance

### Team Feedback Questions

1. **Clarity**: Are instructions clear?
2. **Completeness**: Are examples helpful?
3. **Discoverability**: Do triggers make sense?
4. **Accuracy**: Does it work as described?
5. **Edge cases**: Are errors handled well?

### Feedback incorporation

- Add clarifying examples
- Improve ambiguous instructions
- Expand trigger phrases
- Document discovered edge cases

---

## Pre-Launch Checklist

### Core Quality

- [ ] Description is specific with key trigger terms
- [ ] SKILL.md under 500 lines
- [ ] No time-sensitive information (use collapsible sections for deprecated content)
- [ ] Consistent terminology throughout
- [ ] Concrete examples included
- [ ] References are one level deep from SKILL.md

### Code & Scripts

- [ ] Explicit error handling (no punting to Claude)
- [ ] Constants have justifications (comments explaining magic numbers)
- [ ] Required packages/dependencies listed
- [ ] No Windows paths (forward slashes only)
- [ ] Scripts have execute permissions (`chmod +x`)
- [ ] Validation steps for critical operations

### Organization

- [ ] Table of contents in files >100 lines
- [ ] Clear, descriptive file names
- [ ] Supporting files referenced from SKILL.md
- [ ] No nested references (one level deep only)

### Testing

- [ ] Three or more evaluation scenarios created
- [ ] Tested across models (Haiku, Sonnet, Opus)
- [ ] Real-world usage patterns validated
- [ ] Team feedback incorporated

### Documentation

- [ ] Name uses gerund form (-ing)
- [ ] Name is lowercase with hyphens only
- [ ] Description is third person voice
- [ ] Description includes specific triggers
- [ ] YAML frontmatter is valid (spaces, not tabs)
- [ ] All paths use forward slashes

### Platform Considerations

- [ ] Cross-platform compatibility verified
- [ ] Agent SDK configuration documented (if applicable)
- [ ] Plugin integration tested (if distributing as plugin)
- [ ] Version information included
