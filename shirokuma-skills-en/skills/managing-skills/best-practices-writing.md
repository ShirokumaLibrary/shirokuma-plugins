# Writing Effective Instructions

Guidelines for writing clear, actionable skill instructions.

For core principles and organization, see [best-practices.md](best-practices.md).
For testing and evaluation, see [best-practices-testing.md](best-practices-testing.md).

## Checklists for Complex Tasks

### Provide copyable progress trackers

```markdown
## Task Progress

Copy and update:
- [ ] Step 1: Analyze input files
- [ ] Step 2: Extract data
- [ ] Step 3: Transform format
- [ ] Step 4: Validate output
- [ ] Step 5: Generate report

Status: [  ] / 5 complete
```

### Why

Helps Claude track multi-step workflows and maintain state

## Validation Loops

### Structure as iterative improvement

```markdown
## Workflow

1. Generate initial output
2. Run validator
3. If errors found:
   a. Analyze error messages
   b. Fix identified issues
   c. Return to step 2
4. If validation passes: Complete
```

### With explicit limits

```markdown
## Workflow with Safety

Repeat up to 3 times:
1. Generate output
2. Validate
3. Fix errors

If still failing after 3 attempts:
- Report specific errors
- Suggest manual intervention
```

## Template Pattern

### Strict requirements (low freedom)

```markdown
## Output Format (EXACT)

\```json
{
  "status": "success" | "error",
  "data": {
    "field1": "value1",
    "field2": "value2"
  },
  "timestamp": "ISO-8601 format"
}
\```

Do NOT deviate from this structure.
```

### Flexible requirements (high freedom)

```markdown
## Suggested Output Format

Consider using:
\```json
{
  "status": "...",
  "data": {...},
  "metadata": {...}
}
\```

Adapt as needed for your use case.
```

## Examples Pattern

### Input/output pairs demonstrate desired behavior

```markdown
## Example 1: Simple Case

##### Input

\```csv
name,age,city
John,30,NYC
\```

##### Output

\```json
[{"name": "John", "age": 30, "city": "NYC"}]
\```

## Example 2: Edge Case

##### Input

\```csv
name,age,city
John,"30,5",NYC
\```

##### Output

\```json
[{"name": "John", "age": "30,5", "city": "NYC"}]
\```

Note: Age preserved as string due to comma.
```

## Conditional Workflow Pattern

### Guide through decision points

```markdown
## Workflow

### Step 1: Determine Operation Type

Creating new content?
→ Follow "Creation Workflow" below

Editing existing content?
→ Follow "Editing Workflow" below

Migrating or converting?
→ Follow "Migration Workflow" below

### Creation Workflow
1. Generate structure
2. Populate content
3. Validate output

### Editing Workflow
1. Load existing content
2. Apply modifications
3. Preserve metadata

### Migration Workflow
1. Parse source format
2. Transform data
3. Validate conversion
```

---

## Code and Scripts

### Solve, Don't Punt

Handle errors explicitly, don't assume Claude will handle them.

**Bad (punting to Claude)**:
```python
result = requests.get(url)
data = result.json()
```

**Good (explicit error handling)**:
```python
try:
    result = requests.get(url, timeout=30)
    result.raise_for_status()
    data = result.json()
except requests.Timeout:
    print("ERROR: Request timed out after 30 seconds")
    sys.exit(1)
except requests.HTTPError as e:
    print(f"ERROR: HTTP {e.response.status_code}")
    sys.exit(1)
except json.JSONDecodeError:
    print("ERROR: Invalid JSON response")
    sys.exit(1)
```

### Justify Constants

Explain magic numbers with comments.

**Unexplained**:
```python
timeout=30
```

**Justified**:
```python
timeout=30  # HTTP requests typically complete within 30 seconds
MAX_RETRIES=3  # Balance between reliability and performance
CHUNK_SIZE=8192  # Optimal buffer size for file I/O
```

### Utility Scripts

Pre-made scripts are more reliable than generated code.

**Benefits**:
- Consistent behavior
- Pre-tested
- Token efficient
- No generation errors

**Example structure**:
- `skill-name/SKILL.md`
- `skill-name/scripts/validate.py`
- `skill-name/scripts/transform.sh`
- `skill-name/scripts/helpers/parser.py`
- `skill-name/scripts/helpers/formatter.py`

**Usage in SKILL.md**:
```markdown
## Validation

Run the validation script:
\```bash
python scripts/validate.py input.json --strict
\```

See script help for options:
\```bash
python scripts/validate.py --help
\```
```

### Visual Analysis

Convert PDFs to images for layout understanding.

```python
# For PDF layout analysis
import pdf2image

# Convert first page to image
images = pdf2image.convert_from_path(
    'document.pdf',
    first_page=1,
    last_page=1
)

# Claude can analyze image layout
# Better than text-only for complex layouts
```

**Why**: Text extraction loses spatial relationships; images preserve layout.

### Verifiable Intermediate Outputs

Plan-validate-execute pattern for batch operations:

```markdown
## Batch Processing Workflow

### Step 1: Generate Plan
Create operation plan:
\```json
{
  "operations": [
    {"file": "doc1.md", "action": "transform", "params": {...}},
    {"file": "doc2.md", "action": "transform", "params": {...}}
  ]
}
\```

### Step 2: Validate Plan
Review plan with user before execution.

### Step 3: Execute
Process each operation.

### Step 4: Report Results
Summary of successes and failures.
```

**Benefits**:
- User can review before execution
- Errors caught early
- Auditability

### File Path Requirements

Always use forward slashes for cross-platform compatibility.

**Cross-platform**:
```python
script_path = "scripts/helper.py"
config_path = "config/settings.json"
```

**Windows-only** (breaks on Unix):
```python
script_path = "scripts\\helper.py"  # Bad
config_path = "config\\settings.json"  # Bad
```

**Use pathlib for robustness**:
```python
from pathlib import Path

script_path = Path("scripts") / "helper.py"
config_path = Path("config") / "settings.json"
```

---

## No Implicit References (Session-Independent Writing)

Content that skills write to GitHub (Issue comments, PR bodies, Discussions) must be written assuming **the next session's AI has no access to the conversation history**.

### Why This Matters

When a session transfers, the next AI can only access what was written to GitHub. `starting-session #N` restores context by fetching Issue comments via `shirokuma-docs issues comments {N}`, so the quality of GitHub writes directly affects session continuity.

### Patterns to Avoid (Implicit References)

| NG Pattern | Problem | Fix |
|-----------|---------|-----|
| "as discussed earlier" | Implicit reference to conversation | Write the discussed content explicitly |
| "as mentioned above" | Reference to earlier text in same comment | Repeat the specific content |
| "as we agreed" | Implicit reference to in-session agreement | State the agreement explicitly |
| "as mentioned earlier" | Reference to a prior comment | Quote the comment ID or content |
| "as decided in the previous session" | Cross-session implicit reference | Describe the decision concretely |

### Recommended Pattern

```markdown
# NG: Implicit reference
As discussed, we'll go with Approach A.

# OK: Self-contained
We adopt Approach A (add a new parseXml function in `src/utils/parser.ts`).
Reason: Approach B risks conflicting with the existing JSON parser.
```

```markdown
# NG: Implicit reference
as discussed, this fixes the issue.

# OK: Self-contained
This commit fixes the null pointer exception in `getUser()` (Issue #342).
Root cause: The `id` field was not validated before the database lookup.
```

### Impact on Skill Design

When designing GitHub write templates:
- Avoid phrases like "see previous discussion" or "as above" in templates
- Use variable placeholders (`{concrete content}`) to enforce self-contained descriptions
- Leverage Issue numbers (`#{number}`) and values obtained via git/CLI commands (commit hashes, etc.)

See also `best-practices.md` for the "GitHub Output Quality" section.
