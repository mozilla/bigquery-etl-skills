# Creating Agents

Learn how to create new autonomous agents that coordinate skills to accomplish complex workflows.

## Prerequisites

Before creating an agent:

1. **Understand existing skills**: Review [available skills](../skills/available-skills.md) that your agent can use
2. **Identify the workflow**: Define the multi-step process your agent will automate
3. **Determine autonomy level**: Decide how much the agent should decide vs ask

## When to Create an Agent

Create a new agent when:

✅ You have a **multi-step workflow** that combines multiple skills
✅ The workflow requires **autonomous decision-making**
✅ You need **error recovery** between steps
✅ The task benefits from **iterative refinement**
✅ You want a **reusable orchestration pattern**

Don't create an agent when:

❌ A single skill can handle the task
❌ The workflow is highly variable and doesn't follow a pattern
❌ User interaction is needed at each step
❌ The task is a one-off that won't be repeated

## Agent Structure

### File Location

Create agent files in the `agents/` directory:

```
bigquery-etl-skills/
├── agents/
│   ├── etl-orchestrator.md
│   ├── your-new-agent.md      ← New agent here
│   └── ...
```

### File Format

Agents use Markdown with YAML frontmatter:

```markdown
---
name: agent-name
description: Clear description of what this agent does and when to use it
skills: skill1, skill2, skill3
model: sonnet
permissionMode: default
---

# Agent Display Name

Detailed description of the agent's purpose and capabilities.

## What This Agent Does

Bullet list of what the agent accomplishes...

## When to Use This Agent

Clear criteria for when to invoke...

## When NOT to Use This Agent

When to use individual skills instead...

## How It Works

### Phase 1: [Phase Name]
Description of what happens...

### Phase 2: [Phase Name]
Description of what happens...

## Error Handling

How the agent handles common errors...

## Autonomy Level

Describe how much the agent decides vs asks...

## Output

What the agent produces...

## Example Invocations

\`\`\`
"Example user request that would invoke this agent"
\`\`\`
```

## Frontmatter Fields

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Unique identifier (lowercase, hyphens) | `etl-orchestrator` |
| `description` | What it does + when to use (critical for Claude's discovery) | `Autonomously builds complete BigQuery data models end-to-end...` |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `skills` | Comma-separated skills to auto-load | None (no skills loaded) |
| `model` | Model to use: `sonnet`, `opus`, `haiku`, or `inherit` | `inherit` |
| `tools` | Comma-separated tools to allow (omit to inherit all) | All tools |
| `permissionMode` | Permission handling: `default`, `acceptEdits`, `bypassPermissions`, `plan`, `ignore` | `default` |

### Field Details

#### `description`

The description is **critical** - it's how Claude decides when to invoke your agent. Make it:

- **Specific**: Clearly state what tasks the agent handles
- **Contextual**: Include when/why users would want this
- **Keyword-rich**: Use terms users would naturally say

Good examples:
```yaml
description: Autonomously builds complete BigQuery data models end-to-end from requirements through testing and monitoring. Use when implementing full ETL pipelines, new tables, or complex multi-step data workflows.
```

```yaml
description: Safely migrates BigQuery schemas and updates all dependent queries, tests, and documentation. Use when changing table schemas, adding columns, or modifying data types.
```

#### `skills`

List skills that your agent needs. These are automatically loaded when the agent starts:

```yaml
skills: bigquery-etl-core, query-writer, metadata-manager, sql-test-generator
```

The agent can then invoke these skills as needed during execution.

#### `model`

Choose the right model for your agent's complexity:

- **`sonnet`** (default): Best balance of capability and cost - use for most agents
- **`opus`**: More powerful for highly complex reasoning - use sparingly
- **`haiku`**: Faster and cheaper for simpler workflows - use for straightforward orchestration

#### `permissionMode`

Control how the agent handles file operations:

- **`default`**: Ask for permission before file edits (safest)
- **`acceptEdits`**: Auto-accept edit operations
- **`bypassPermissions`**: Skip permissions entirely (use with caution)
- **`plan`**: Start in planning mode before execution
- **`ignore`**: Ignore permission errors and continue

## Agent Content Guidelines

### 1. Clear Purpose Statement

Start with a concise summary of what the agent does:

```markdown
# ETL Orchestrator Agent

The ETL Orchestrator is an autonomous agent that builds complete BigQuery
data models from start to finish, coordinating multiple skills to deliver
production-ready tables with tests and monitoring.
```

### 2. Define "When to Use"

Provide specific scenarios:

```markdown
## When to Use This Agent

Use the ETL orchestrator when you need:

- **Complete table implementation**: "Build a new table for user retention metrics"
- **End-to-end workflows**: "Implement this data model with tests and monitoring"
- **Complex multi-step tasks**: "Create a derived table that aggregates events by user"
```

### 3. Define "When NOT to Use"

Help users avoid over-using the agent:

```markdown
## When NOT to Use This Agent

Don't use this agent for:

- **Simple updates**: Use individual skills directly (e.g., just updating a query)
- **Single-skill tasks**: Use the specific skill instead
- **Quick fixes**: Direct skill invocation is faster
```

### 4. Document the Workflow

Describe what phases/steps the agent executes:

```markdown
## How It Works

### Phase 1: Planning
- Loads bigquery-etl-core for context
- Invokes model-requirements to understand requirements
- Creates implementation plan

### Phase 2: Implementation
- Invokes query-writer to create query
- Invokes metadata-manager for schema
- Validates all components

### Phase 3: Testing
- Invokes sql-test-generator
- Runs tests and validates
- Fixes any issues found
```

### 5. Explain Error Handling

Document how the agent handles failures:

```markdown
## Error Handling

The orchestrator handles errors autonomously:

- **Query errors**: Revises query logic and retries
- **Test failures**: Analyzes failures, fixes issues, reruns tests
- **Schema mismatches**: Updates schema to match query output
```

### 6. Show Example Invocations

Provide concrete examples of how users would invoke the agent:

```markdown
## Example Invocations

```
"Build a new table called user_retention_daily that calculates
7-day rolling retention from events_daily"
```
```
"Implement a derived table for client attribution with proper
tests and monitoring"
```

```

### 7. Describe the Output

Show what users get when the agent completes:

```markdown
## Output

Upon completion, you'll have:

\`\`\`
sql/{project}/{dataset}/{table_name}/
├── query.sql
├── metadata.yaml
├── schema.yaml
├── tests/
└── bigconfig.yml
\`\`\`

All files properly formatted, documented, and tested.
```

## Skill Coordination Patterns

### Sequential Execution

Most common pattern - execute skills in order:

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

### Error Recovery

Handle failures between skills:

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

## Autonomy Guidelines

Define how autonomous your agent should be:

### High Autonomy

Agent makes most decisions:

```markdown
## Autonomy Level

This agent operates with **high autonomy**:

- Makes decisions about implementation approaches
- Chooses appropriate patterns from templates
- Determines when monitoring is needed
- Fixes errors without user intervention
- Only asks questions when requirements are ambiguous
```

### Medium Autonomy

Agent confirms major decisions:

```markdown
## Autonomy Level

This agent operates with **medium autonomy**:

- Asks about architectural choices (e.g., incremental vs full refresh)
- Confirms table naming and dataset selection
- Handles implementation details autonomously
- Fixes minor errors without asking
```

### Low Autonomy

Agent confirms each step:

```markdown
## Autonomy Level

This agent operates with **low autonomy**:

- Confirms each phase before proceeding
- Shows plan and waits for approval
- Asks about implementation details
- Reports all decisions made
```

## Testing Your Agent

### 1. Test Locally

Add the agent to your local marketplace and test:

```bash
# Agent appears in /agents command
/agents

# Invoke with test request
"Build a test table to validate the etl-orchestrator"
```

### 2. Verify Skill Loading

Ensure the agent can access its skills:

```markdown
Test that the agent:
- Loads skills specified in frontmatter
- Can invoke each skill successfully
- Receives skill outputs correctly
```

### 3. Test Error Handling

Intentionally cause errors to verify recovery:

```markdown
- Create invalid query → Agent should detect and fix
- Cause test failure → Agent should diagnose and retry
- Missing dependency → Agent should identify and report
```

### 4. Validate Output

Ensure the agent produces correct outputs:

```markdown
- All files created in correct locations
- Files follow formatting conventions
- Tests pass
- Documentation is complete
```

## Best Practices

### ✅ Do

- **Be specific** in agent descriptions for better discovery
- **Document workflows** clearly so users understand what happens
- **Handle errors** gracefully with retry logic
- **Report progress** so users know what's happening
- **Reuse existing skills** rather than duplicating logic
- **Test thoroughly** with various inputs
- **Set appropriate autonomy** for the task complexity

### ❌ Don't

- **Duplicate skill logic** - invoke skills instead
- **Create overly broad agents** - keep them focused
- **Skip error handling** - agents should be robust
- **Assume user intent** - ask clarifying questions when ambiguous
- **Make agents too autonomous** - confirm major decisions
- **Forget to document** - users need to understand what agents do

## Example: Schema Migrator Agent

Here's a complete example of a new agent:

```markdown
---
name: schema-migrator
description: Safely migrates BigQuery table schemas and updates all dependent queries, tests, and documentation. Use when changing table schemas, adding columns, or modifying data types.
skills: bigquery-etl-core, metadata-manager, sql-test-generator
model: sonnet
---

# Schema Migrator Agent

The Schema Migrator safely updates BigQuery table schemas and automatically
propagates changes to all dependent queries, tests, and documentation.

## What This Agent Does

This agent autonomously:

1. Analyzes the requested schema change
2. Identifies all downstream dependencies
3. Updates the schema.yaml file
4. Updates dependent queries that reference the table
5. Regenerates affected test fixtures
6. Validates all changes with test runs
7. Reports migration summary and potential impacts

## When to Use This Agent

Use the schema migrator when you need:

- **Add columns**: "Add a user_cohort column to events_daily"
- **Change types**: "Change timestamp from INT64 to TIMESTAMP in clicks table"
- **Rename fields**: "Rename user_id to client_id in retention table"
- **Schema refactoring**: "Restructure nested fields in the events schema"

## When NOT to Use This Agent

Don't use this agent for:

- **New tables**: Use etl-orchestrator instead
- **Only updating schema**: Use metadata-manager skill directly
- **Breaking changes**: Requires manual review and migration plan

## How It Works

### Phase 1: Analysis
- Loads bigquery-etl-core for conventions
- Analyzes current schema
- Validates requested changes
- Identifies downstream dependencies using DataHub

### Phase 2: Schema Update
- Invokes metadata-manager to update schema.yaml
- Validates new schema structure
- Checks for breaking changes

### Phase 3: Dependency Updates
- Updates queries that SELECT from this table
- Updates JOINs that reference changed columns
- Modifies test expectations

### Phase 4: Test Regeneration
- Invokes sql-test-generator for affected tests
- Updates fixtures to match new schema
- Runs all affected tests

### Phase 5: Validation
- Runs full test suite
- Reports test results
- Lists all modified files
- Highlights potential issues

## Error Handling

- **Breaking changes**: Warns and asks for confirmation
- **Test failures**: Diagnoses and fixes automatically
- **Missing dependencies**: Reports but continues
- **Type incompatibilities**: Suggests casting or conversion

## Autonomy Level

This agent operates with **medium autonomy**:

- Asks before making breaking changes
- Confirms scope of dependency updates
- Handles non-breaking changes automatically
- Reports all modifications made

## Output

Upon completion, you'll have:

- Updated schema.yaml with new structure
- Modified dependent queries (if any)
- Regenerated test fixtures
- Migration summary report

All changes tested and validated.

## Example Invocations

\`\`\`
"Add a country_code STRING column to events_daily"
\`\`\`

\`\`\`
"Change submission_timestamp from INT64 to TIMESTAMP in
main_summary_v4"
\`\`\`
```

## Publishing Your Agent

Once your agent is ready:

1. **Add to [`.claude-plugin/marketplace.json`](https://github.com/mozilla/bigquery-etl-skills/blob/main/.claude-plugin/marketplace.json)**: Add your agent to the `agents` array:
   ```json
   "agents": [
     "./agents/etl-orchestrator.md",
     "./agents/your-new-agent.md"
   ]
   ```

2. **Document in [`docs/agents/available-agents.md`](https://github.com/mozilla/bigquery-etl-skills/blob/main/docs/agents/available-agents.md)**: Add your agent to the list with description and usage

3. **Test thoroughly**: Validate with various scenarios

4. **Submit PR**: Include agent file and documentation updates

## Quick Links

<div class="grid cards" markdown>

- :material-robot-outline: **[Agents Overview](overview.md)**

    Understand how agents work

- :material-robot: **[Available Agents](available-agents.md)**

    See existing agents for examples

- :material-cog: **[Available Skills](../skills/available-skills.md)**

    Skills your agent can use

</div>
