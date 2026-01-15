# Making Assets and References Explicit

**Problem:** Even when skills have well-organized `assets/` and `references/` directories, Claude may not proactively read them before generating output. This leads to incomplete or incorrect results compared to what would be produced if the resources were used.

**Solution:** Make reading these resources an explicit, mandatory step in the skill workflow using prominent instructions and clear decision trees.

## Test Results Demonstrating the Impact

**Test Setup:** Created two identical queries requiring Glean event fixtures, once without explicit instructions and once with explicit "READ" instructions.

**Without Explicit Instructions (from memory):**
```yaml
- submission_timestamp: "2024-12-01 10:00:00"
  client_info:
    client_id: "client-001"
  events:
    - category: "navigation"
      name: "page_load"
```
**Missing:** `document_id`, `app_display_version`, proper `extra` structure

**With Explicit "READ assets/glean_events_fixture.yaml" Instructions:**
```yaml
- submission_timestamp: "2024-12-01 10:00:00"
  document_id: "doc123"
  client_info:
    client_id: "client-001"
    app_display_version: "121.0.0"
  events:
    - category: "navigation"
      name: "page_load"
      extra:
        - key: "url"
          value: "https://example.com"
```
**Complete:** All fields present, proper nested structure, multiple test clients

**Result:** Explicit instructions produced complete, correctly-structured fixtures that matched the template. Without explicit instructions, critical fields were omitted.

## Standardized Structure Pattern

Every skill should include these two sections near the top of SKILL.md (after Overview, before detailed content):

### 1. "🚨 REQUIRED READING - Start Here" Section

**Purpose:** Identify foundational reference files that MUST be read before any work begins.

**Template:**
```markdown
## 🚨 REQUIRED READING - Start Here

**BEFORE [performing this skill's task], you MUST read these files:**

1. **[Category/Purpose]:** READ `references/critical_file.md`
   - Brief explanation of what it contains
   - Why it's critical to read this first

2. **[Category/Purpose]:** READ `references/another_file.md`
   - Brief explanation of what it contains
   - Why it's needed
```

**Example from sql-test-generator:**
```markdown
## 🚨 REQUIRED READING - Start Here

**BEFORE creating any test fixtures, you MUST read these files:**

1. **CRITICAL FOR SAFETY:** Read `references/preventing_production_queries.md`
   - Prevents accidentally querying production data
   - Explains how to verify fixtures are working correctly
   - Required reading before ANY test creation

2. **UNDERSTAND TEST PATTERNS:** Read `references/test_strategy_patterns.md`
   - Learn which test scenarios are needed for different query types
   - Understand how many tests to create
   - See examples of test coverage strategies
```

**Best Practices:**
- Use CAPS and bold for emphasis: "**BEFORE doing X, you MUST read these files:**"
- Number the files to show reading order
- Use clear category labels: "CRITICAL FOR SAFETY", "UNDERSTAND PATTERNS"
- Explain WHY each file matters, not just WHAT it contains
- Keep this section short (2-4 critical files maximum)

### 2. "📋 Templates - Copy These Structures" Section

**Purpose:** Provide decision-tree guidance for which templates to read and use based on the specific task.

**Template:**
```markdown
## 📋 Templates - Copy These Structures

**When [doing task X], READ and COPY the structure from these template files:**

**For [scenario A]:**
- **[Condition]?** → READ `assets/template_a.ext` and copy its structure
  - Shows [key features]
  - Use this for [specific use case]

**For [scenario B]:**
- **[Condition]?** → READ `assets/template_b.ext`
  - Shows [key features]
  - Use for [specific use case]
```

**Example from sql-test-generator:**
```markdown
## 📋 Templates - Copy These Structures

**When creating test fixtures, READ and COPY the structure from these template files:**

**For Input Fixtures:**
- **Glean events?** → READ `assets/glean_events_fixture.yaml` and copy its structure
  - Shows proper `client_info`, `events`, and `extra` formatting
  - Use this for any `*_stable.events_v1` or Glean ping tables

- **Legacy telemetry with arrays?** → READ `assets/legacy_array_fixture.yaml`
  - Shows how to structure array fields that get UNNESTed
  - Use for legacy telemetry tables with array columns

- **Simple table?** → READ `assets/simple_test_input.yaml`
  - Basic fixture structure for flat tables

**For Query Parameters:**
- READ `assets/query_params_example.yaml` - Must be array format, not key-value pairs
```

**Best Practices:**
- Use question format for decision points: "Glean events?", "Nested fields?"
- Use arrows (→) to show: condition → action to take
- Add brief explanations of what each template shows
- Include when to use each template
- Group related templates together (Input Fixtures, Output, Parameters)

## Writing Effective "READ" Instructions

**Strong (Explicit):**
- "READ `references/file.md` for complete documentation"
- "**Before creating fixtures, READ `assets/template.yaml`**"
- "Step 1: Read the required reference files"
- "**COPY the structure from `assets/template.yaml`**"

**Weak (Implicit):**
- "See `references/file.md` for details" ← Doesn't require reading
- "Templates are available in `assets/`" ← Doesn't specify which to read
- "Reference materials are provided" ← Too vague
- "You can find examples in..." ← Optional, not mandatory

**Pattern: Use action verbs + specific paths**
- READ, COPY, FOLLOW → Strong directives
- See, available, can find → Weak suggestions

## Integrating Reading Steps into Workflows

**Before (Implicit):**
```markdown
## Workflow

1. Read the query.sql file
2. Create test fixtures
3. Run tests
```

**After (Explicit):**
```markdown
## Workflow

### Step-by-Step Process

1. **Read the required reference files** (from "REQUIRED READING" section above)
   - READ `references/preventing_production_queries.md`
   - READ `references/test_strategy_patterns.md`

2. **Read the query.sql file**

3. **Read the appropriate template files** for your data sources:
   - For Glean events tables → READ `assets/glean_events_fixture.yaml`
   - For legacy telemetry with arrays → READ `assets/legacy_array_fixture.yaml`
   - For simple tables → READ `assets/simple_test_input.yaml`

4. **Create test fixtures:**
   - **Copy the structure from the template files you read in step 3**
   - Each fixture needs at least one row of data
   - Match the file naming to how the table is referenced in the query

5. **Run tests and verify**
```

**Pattern: Make reading an explicit numbered step**
- Don't bury it in the middle of other instructions
- Reference back to the "REQUIRED READING" section
- Use conditional logic to guide which templates to read
- Emphasize copying structure from templates

## When to Use This Pattern

**Use explicit READ instructions when:**
- ✅ Assets/references contain non-obvious structure or format requirements
- ✅ Missing information leads to incorrect output (like missing fields in fixtures)
- ✅ There are multiple templates requiring decision-tree guidance
- ✅ The skill has common failure modes that templates prevent
- ✅ Type inference or formatting issues require following exact patterns

**Less critical when:**
- ❌ The skill is purely conceptual with no templates
- ❌ Resources are optional advanced topics, not core workflow
- ❌ The information is simple and obvious (no specialized structure)

## Measuring Effectiveness

**Before applying this pattern, skills produced:**
- Incomplete structures (missing fields)
- Incorrect formats (wrong YAML syntax)
- Type inference errors (version numbers as floats)

**After applying this pattern, skills produce:**
- Complete structures matching templates
- Correct formats following examples
- Proper handling of edge cases documented in templates

**Validation:** Create test tasks before and after adding explicit instructions, compare quality of output.

## Updating Existing Skills

When updating existing skills to use this pattern:

1. **Audit current assets/references:**
   - Which files are most critical?
   - Which templates prevent common errors?
   - What reading order makes sense?

2. **Add REQUIRED READING section:**
   - 2-4 most critical reference files
   - Clear categorization and WHY statements
   - Bold emphasis on mandatory reading

3. **Add Templates section:**
   - Decision-tree for choosing templates
   - Question format with arrows
   - Brief explanations of what each shows

4. **Update workflow steps:**
   - Add explicit reading steps with file paths
   - Reference back to REQUIRED READING section
   - Use "COPY the structure from..." language

5. **Test the changes:**
   - Use the skill on a real task
   - Verify resources are being read
   - Compare output quality to before

## Example: query-writer Skill Update

**Before:**
```markdown
## Quick Start

Use query.sql for standard transformations.
See `assets/` for templates and `references/` for conventions.
```

**After:**
```markdown
## 🚨 REQUIRED READING - Start Here

**BEFORE writing any query, READ these reference files to understand patterns:**

1. **SQL Conventions:** READ `references/sql_formatting_conventions.md`
2. **Common Patterns:** READ `references/common_query_patterns.md`
3. **Partitioning:** READ `references/partitioning_patterns.md`

## 📋 Templates - Copy These Structures

**When writing queries, READ and COPY from these template files:**

- **Basic aggregation?** → READ `assets/basic_query_example.sql`
- **Need CTEs?** → READ `assets/cte_query_example.sql`
- **Joining tables?** → READ `assets/join_example.sql`
- **UNNESTing arrays?** → READ `assets/unnest_example.sql`

## Quick Start

### Step 1: Read the required references
Follow the "REQUIRED READING" section above to understand SQL conventions,
common patterns, and partitioning requirements.

### Step 2: Choose and read the appropriate template
Based on your query type, READ the matching template from the "Templates" section.

### Step 3: Write your query
COPY the structure from the template and adapt for your use case.
```

**Impact:** Claude now consistently reads conventions and templates before writing queries, resulting in properly formatted SQL that follows Mozilla patterns from the start.
