# Skills vs Agents: When to Use Which

Understanding the difference between skills and agents will help you work more effectively with the BigQuery ETL Skills plugin.

## Quick Comparison

| Aspect | Skills | Agents |
|--------|--------|--------|
| **What they are** | Instruction sets for specific tasks | Autonomous orchestrators |
| **How they work** | Claude follows instructions | Agent makes decisions |
| **Invocation** | Automatic (based on task) | Explicit (user requests) |
| **Scope** | Single focused task | Multi-step workflows |
| **State** | Stateless | Maintains context |
| **Error handling** | Interactive with user | Autonomous recovery |
| **Speed** | Fast (focused) | Slower (comprehensive) |
| **Control** | High (you guide each step) | Lower (agent decides) |

## The Mental Model

### Skills: Tools in Claude's Toolbox

Think of skills as **specialized knowledge** that Claude can reference:

```
User: "Write a SQL query for user retention"
        ↓
Claude: "I need to write a query, let me load the query-writer skill"
        ↓
Claude: [Reads skill instructions, templates, conventions]
        ↓
Claude: [Writes query following the patterns]
        ↓
Result: query.sql file
```

**You're in control**: Claude asks you about decisions, shows you drafts, follows your guidance.

### Agents: Autonomous Assistants

Think of agents as **independent workers** that use skills:

```
User: "Build a user_retention_daily table that calculates
       7-day rolling retention from events_daily, partitioned by date"
        ↓
Agent: "I have clear requirements, I'll handle this end-to-end"
        ↓
Agent: [Validates requirements are sufficient]
Agent: [Uses query-writer skill → creates query]
Agent: [Uses metadata-manager skill → generates schema]
Agent: [Uses sql-test-generator skill → creates tests]
Agent: [Runs tests, fixes issues, validates]
        ↓
Result: Complete table with query, schema, metadata, tests, monitoring
```

**Agent is in control**: It makes implementation decisions, handles errors, iterates until complete.

## Decision Tree: Which Should I Use?

### Start Here: What's Your Task?

#### 1️⃣ Single Task → Use a Skill

**Examples:**

- "Write a SQL query for X"
- "Add tests for this query"
- "Generate a schema for this table"
- "Update the metadata.yaml"

**Why a skill:**

- ✅ Fast and focused
- ✅ You control the pace
- ✅ Easy to iterate with Claude
- ✅ Review each output

**Which skill:**

- Writing/updating queries → `query-writer`
- Creating/updating tests → `sql-test-generator`
- Schema/metadata work → `metadata-manager`
- Monitoring setup → `bigconfig-generator`

#### 2️⃣ Multi-Step Workflow → Use an Agent

**Examples:**

- "Build a complete table for user retention"
- "Implement a new derived table with tests and monitoring"
- "Create a data model for search metrics"

**Why an agent:**

- ✅ Handles everything automatically
- ✅ Coordinates multiple steps
- ✅ Fixes errors autonomously
- ✅ Delivers production-ready output

**Which agent:**
- Complete table creation → `etl-orchestrator`
- Schema changes → `schema-migrator` (if available)

## Detailed Scenarios

### Scenario 1: "I need to write a new SQL query"

**✅ Use: `query-writer` skill**

Claude will:

1. Load query-writer skill
2. Read relevant templates and conventions
3. Ask you about the query logic
4. Write the query.sql file
5. Show it to you for review

**Why not an agent?**
- Single file to create
- You might want to iterate on the logic
- No other files need updating
- Faster to use the skill directly

---

### Scenario 2: "Build a new table for user retention with 7-day rolling window from events_daily"

**✅ Use: `etl-orchestrator` agent** (you've provided clear requirements)

The agent will:
1. Validate requirements are sufficient
2. Create query.sql
3. Generate schema.yaml with descriptions
4. Create metadata.yaml with DAG config
5. Generate test fixtures
6. Run tests and fix any issues
7. Add monitoring if appropriate
8. Report what was created

!!! tip "What if requirements are unclear?"
    If you're not sure what you need, use the `model-requirements` skill first to gather requirements interactively, then invoke the agent.

**Why not skills?**
- Multiple files needed (query, schema, metadata, tests)
- Coordination between components required
- Want production-ready deliverable
- Benefit from autonomous error handling

---

### Scenario 3: "Update the query to add a new field"

**✅ Use: `query-writer` skill**

Claude will:
1. Load query-writer skill
2. Read the existing query
3. Add the new field
4. Update the query
5. Ask if you want to update tests (or use `sql-test-generator`)

**Why not an agent?**
- Simple change to existing file
- You might want to review before updating tests
- Faster iteration with direct skill use

---

### Scenario 4: "Add a column to events_daily and update everything that depends on it"

**✅ Use: `schema-migrator` agent (if available)**

The agent will:
1. Analyze the schema change
2. Identify downstream dependencies
3. Update schema.yaml
4. Update dependent queries
5. Regenerate affected tests
6. Run tests and validate
7. Report all changes made

**Why not skills?**
- Multiple files affected
- Need dependency analysis
- Risk of missing updates
- Benefit from comprehensive validation

---

### Scenario 5: "I want to understand this table's structure"

**✅ Use: `bigquery-etl-core` skill (or just ask Claude)**

Claude will:
1. Optionally load bigquery-etl-core for context
2. Read relevant files
3. Explain the structure to you

**Why not an agent?**
- This is exploration/understanding
- No files being created or modified
- Interactive Q&A works best

---

### Scenario 6: "Create tests for this existing query"

**✅ Use: `sql-test-generator` skill**

Claude will:
1. Load sql-test-generator skill
2. Read the query
3. Generate test directory structure
4. Create input fixtures for source tables
5. Generate expected output
6. Show you the tests

**Why not an agent?**
- Single focused task (test creation)
- Query already exists
- You might want to review fixtures before running
- Faster with direct skill use

---

### Scenario 7: "Review this data model and add appropriate monitoring"

**✅ Use: `bigconfig-generator` skill**

Claude will:
1. Load bigconfig-generator skill
2. Analyze the table structure
3. Recommend monitoring checks
4. Create bigconfig.yml
5. Show you the configuration

**Why not an agent?**
- Focused task (monitoring only)
- Table already exists
- You might want to adjust thresholds
- Quick iteration with skill

## When Agent Autonomy Makes Sense

Use agents when you want:

### ✅ End-to-End Delivery
"Build me a complete, production-ready table"
- Agent handles everything from requirements to monitoring

### ✅ Error Recovery
"Implement this, and fix any issues you find"
- Agent runs tests, detects failures, fixes autonomously

### ✅ Decision Making
"Build the best solution for X use case"
- Agent chooses patterns, approaches, configurations

### ✅ Iterative Refinement
"Make this production-ready"
- Agent validates, improves, polishes until complete

## When Skill Guidance is Better

Use skills when you want:

### ✅ Step-by-Step Control
"Let me review each piece before continuing"
- You guide Claude through each step

### ✅ Learning and Understanding
"Help me understand how this works"
- Interactive exploration with skill context

### ✅ Quick Updates
"Just update this one file"
- Fast focused changes without orchestration overhead

### ✅ Iterative Development
"Let's try different approaches"
- Quick iteration on specific components

## Can I Mix Them?

**Yes!** It's common to:

### Start with a Skill, Escalate to Agent

```
1. User: "Write a query for user retention"
   → Claude uses query-writer skill
   → Creates query.sql

2. User: "Now add tests and monitoring too"
   → Could continue with skills (sql-test-generator + bigconfig-generator)
   → Or invoke etl-orchestrator agent to handle comprehensively
```

### Use Agent, Then Skills for Refinement

```
1. User: "Build a complete retention table"
   → Agent creates everything
   → Delivers production-ready table

2. User: "Actually, change the retention window from 7 to 14 days"
   → Claude uses query-writer skill to update
   → Quick focused change
```

## Common Patterns

### Pattern 1: Prototype with Skills

```
Use query-writer → Review query
Use metadata-manager → Review schema
Use sql-test-generator → Review tests

When happy: Consider agent for next table
```

**Benefit**: Learn conventions through guided process

### Pattern 2: Production with Agents

```
Use etl-orchestrator for new tables
Use skills for subsequent updates
```

**Benefit**: Fast production deployment, efficient updates

### Pattern 3: Complex with Both

```
Use agent for initial implementation
Use skills for iterative refinement
Use agent when ready for next version
```

**Benefit**: Best of both worlds

## Summary Cheat Sheet

| Task | Use This |
|------|----------|
| Write query | `query-writer` skill |
| Update query | `query-writer` skill |
| Add tests | `sql-test-generator` skill |
| Update tests | `sql-test-generator` skill |
| Create schema | `metadata-manager` skill |
| Update schema | `metadata-manager` skill |
| Add monitoring | `bigconfig-generator` skill |
| **Build complete table** | **`etl-orchestrator` agent** |
| **Migrate schema + dependencies** | **`schema-migrator` agent** |
| **End-to-end workflow** | **Agent** |
| **Quick single-file update** | **Skill** |
| **Learn/explore** | **Skill** |
| **Production delivery** | **Agent** |

## Still Unsure?

### Default to Skills if:
- You're learning the codebase
- You want control over each step
- The task is small or focused
- You're experimenting

### Default to Agents if:
- You want a complete deliverable
- Multiple files need coordination
- You trust the agent to decide details
- Speed to production matters

When in doubt, **start with a skill** - you can always escalate to an agent if the task grows!

## Quick Links

<div class="grid cards" markdown>

- :material-cog: **[Available Skills](../skills/available-skills.md)**

    See all skills and when to use them

- :material-robot: **[Available Agents](../agents/available-agents.md)**

    See all agents and their capabilities

- :material-robot-outline: **[Agent Overview](../agents/overview.md)**

    Deep dive into how agents work

- :material-thought-bubble: **[Skills Overview](../skills/overview.md)**

    Understanding skill structure

</div>
