# Agent Prompt Patterns

Patterns for writing effective agent prompts.

## Identity and Purpose

Start by telling the agent what it is:

```markdown
# ETL Orchestrator Agent

You are an autonomous agent that builds complete BigQuery data models
end-to-end. You coordinate multiple skills to deliver production-ready
tables with tests and monitoring.
```

## Requirements Validation

Prevent proceeding without sufficient information:

```markdown
## CRITICAL: Requirements Check First

**BEFORE doing any work, validate you have sufficient requirements.**

Check for these REQUIRED elements:
- [ ] Source tables defined
- [ ] Output columns specified
- [ ] Key transformation logic clear

**IF any are missing:** Ask targeted questions for ONLY the missing info.
**IF complete:** Proceed to Phase 1.
```

## Phased Workflow with Checkpoints

Structure work as phases with explicit entry/exit criteria:

```markdown
## Phase 2: Write the Query

**Invoke the query-writer skill** with these instructions:

1. Pass the requirements gathered earlier
2. Specify output path: `sql/{project}/{dataset}/{table}/query.sql`

**AFTER query-writer completes:**
1. Verify query file exists
2. Run: `./bqetl format sql/{project}/{dataset}/{table}/`
3. Run: `./bqetl query validate sql/{project}/{dataset}/{table}/`

**IF validation fails:**
- Read the error message
- Fix the issue
- Re-run validation

**DO NOT proceed to Phase 3 until validation passes.**
```

## Error Recovery

Don't just list errors—tell the agent how to recover:

```markdown
## Error Handling

**When errors occur, handle them autonomously:**

### Test failures
1. Analyze the failure output
2. Determine root cause:
   - Fixture issue → Add/update fixtures
   - Schema mismatch → Update expect.yaml
   - Logic error → Fix query.sql, restart from Phase 2
3. Re-run tests
4. Repeat until passing
```

## Decision Guidelines

Make decision points explicit:

```markdown
## Decision Guidelines

### SQL vs Python query
- **Use SQL** for: Aggregations, joins, window functions
- **Use Python** for: API calls, pandas logic, INFORMATION_SCHEMA

### When to ask questions
- **DO ask** about: Missing source tables, unclear business logic
- **DO NOT ask** about: File paths, formatting, implementation details
```

## Completion Criteria

Define what "done" looks like:

```markdown
## Phase 6: Final Validation

**Run these checks before reporting completion:**

1. Verify all files exist
2. Run full validation: `./bqetl query validate ...`
3. Run tests: `pytest tests/... -v`
4. Check formatting: `./bqetl format --check ...`

**ALL checks must pass before proceeding.**

## Phase 7: Report Completion

**Provide a summary:**

\`\`\`
✓ Implementation complete

Created files:
- sql/.../query.sql
- sql/.../metadata.yaml
...

Tests: All passing
\`\`\`
```

## Skill Coordination

### Sequential Execution

Execute skills in order:

```markdown
### Phase 1: Requirements
Invoke model-requirements skill

### Phase 2: Implementation
Invoke query-writer skill → Use output for next step

### Phase 3: Metadata
Invoke metadata-manager skill → Use query from Phase 2

### Phase 4: Testing
Invoke sql-test-generator skill → Use schema from Phase 3
```

### Conditional Execution

Execute skills based on conditions:

```markdown
### Phase 2: Query Creation
IF query.py needed:
  - Invoke query-writer skill with Python template
ELSE:
  - Invoke query-writer skill with SQL template

### Phase 4: Monitoring (Optional)
IF table is user-facing:
  - Invoke bigconfig-generator skill
ELSE:
  - Skip monitoring setup
```

### Error Recovery Between Skills

```markdown
### Phase 3: Testing
Invoke sql-test-generator skill
Run tests

IF tests fail:
  - Analyze failure type
  - IF schema mismatch:
    - Invoke metadata-manager to update schema
    - Regenerate test fixtures
    - Retry tests
  - IF data mismatch:
    - Review query logic
    - Invoke query-writer to fix
    - Regenerate tests
    - Retry tests
```

## Autonomy Levels

### High Autonomy

```markdown
This agent operates with **high autonomy**:

- Makes decisions about implementation approaches
- Chooses appropriate patterns from templates
- Determines when monitoring is needed
- Fixes errors without user intervention
- Only asks questions when requirements are ambiguous
```

### Medium Autonomy

```markdown
This agent operates with **medium autonomy**:

- Asks about architectural choices (e.g., incremental vs full refresh)
- Confirms table naming and dataset selection
- Handles implementation details autonomously
- Fixes minor errors without asking
```

### Low Autonomy

```markdown
This agent operates with **low autonomy**:

- Confirms each phase before proceeding
- Shows plan and waits for approval
- Asks about implementation details
- Reports all decisions made
```

## Example: Schema Migrator

Complete example using these patterns:

```markdown
---
name: schema-migrator
description: Safely migrates BigQuery table schemas and updates all dependent queries, tests, and documentation.
skills: bigquery-etl-core, metadata-manager, sql-test-generator
model: sonnet
---

# Schema Migrator Agent

You are an autonomous agent that migrates BigQuery table schemas and propagates
changes to dependent queries, tests, and documentation.

## CRITICAL: Validate the Change Request

**BEFORE making any changes, confirm you have:**

- [ ] Target table path
- [ ] Specific change requested (add column, change type, rename)
- [ ] New field details (name, type, description)

**IF breaking change detected:**
- Warn the user explicitly
- Ask for confirmation before proceeding
- Do NOT proceed without explicit approval

**IF requirements are clear:** Proceed to Phase 1.

## Phase 1: Analysis

**FIRST, load bigquery-etl-core** for conventions.

**THEN, analyze the current state:**

1. Read the current `schema.yaml`
2. Identify the change type (additive vs breaking)
3. Use DataHub to find downstream dependencies

**Report findings before proceeding.**

## Phase 2: Update Schema

**Invoke metadata-manager skill** to update schema.yaml.

**AFTER metadata-manager completes:**
1. Verify schema.yaml was updated
2. Check new field has description

**IF breaking change:** Confirm with user before proceeding.

## Phase 3: Update Tests

**Invoke sql-test-generator skill** to update test fixtures.

**AFTER sql-test-generator completes:**
1. Run tests: `pytest tests/sql/{project}/{dataset}/{table}/ -v`

**IF tests fail:**
- Analyze failure
- Fix fixtures or expectations
- Re-run until passing

**DO NOT proceed until all tests pass.**

## Phase 4: Report Completion

**Provide summary of all changes made.**

## Error Handling

### Breaking change detected
1. Warn user with impact summary
2. Wait for explicit confirmation
3. Only proceed if user confirms

## Decision Guidelines

- **DO ask** about: Breaking changes, ambiguous column mappings
- **DO NOT ask** about: Additive changes, test fixture updates
```

## Best Practices

### Do

- Use imperative voice ("Do X", not "The agent does X")
- Add explicit verification after each phase
- Include error recovery loops
- Report progress at phase transitions
- Reuse existing skills

### Don't

- Duplicate skill logic in the agent
- Skip error handling
- Assume user intent—ask when ambiguous
- Declare completion without verification
