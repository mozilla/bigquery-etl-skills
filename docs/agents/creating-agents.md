# Creating Agents

Create autonomous agents that coordinate skills to accomplish complex workflows.

## Prerequisites

1. **Understand existing skills**: Review [available skills](../skills/available-skills.md)
2. **Identify the workflow**: Define the multi-step process to automate
3. **Determine autonomy level**: Decide how much the agent should decide vs ask

## When to Create an Agent

Create an agent when you have:

- A **multi-step workflow** combining multiple skills
- Need for **autonomous decision-making**
- **Error recovery** between steps
- A **reusable orchestration pattern**

Don't create an agent when:

- A single skill can handle the task
- User interaction is needed at each step
- The task is a one-off

## File Structure

Create agent files in the `agents/` directory:

```
bigquery-etl-skills/
├── agents/
│   ├── etl-orchestrator.md
│   └── your-new-agent.md
```

## File Format

Agents use Markdown with YAML frontmatter. Content should be **imperative instructions to the agent**, not documentation about the agent.

```markdown
---
name: agent-name
description: What it does and when to use it
skills: skill1, skill2, skill3
model: sonnet
---

# Agent Name

You are an autonomous agent that [does X]. You coordinate skills to [deliver Y].

## CRITICAL: Requirements Check First

**BEFORE doing any work, validate you have sufficient requirements.**

Check for these REQUIRED elements:
- [ ] Element 1
- [ ] Element 2

**IF any are missing:** Ask targeted clarifying questions.
**IF requirements are complete:** Proceed to Phase 1.

## Phase 1: [Name]

**FIRST, do X.**

**THEN, do Y:**

1. Step one
2. Step two

**IF validation fails:**
- Read the error
- Fix the issue
- Re-run validation

**DO NOT proceed until validation passes.**

## Phase 2: [Name]

**Invoke the [skill-name] skill.**

**AFTER skill completes:**
1. Verify output exists
2. Run validation

## Error Handling

**When errors occur, handle them autonomously:**

### Error Type 1
1. Read the error message
2. Fix it
3. Re-run validation

## Decision Guidelines

- **DO ask** about: [list]
- **DO NOT ask** about: [list]
```

## Key Principles

Based on [Anthropic's agent guidelines](https://www.anthropic.com/engineering/claude-code-best-practices):

1. **Imperative voice**: "Do X", "Run Y" - not "The agent does X"

2. **Explicit verification**: Agents declare work complete prematurely. Add checks:
   ```markdown
   **AFTER Phase 2:**
   1. Verify file exists
   2. Run validation
   3. **DO NOT proceed until validation passes**
   ```

3. **Phased structure**: Break work into phases with entry/exit criteria

4. **IF/THEN logic**: Make decision points explicit

5. **Error recovery loops**: Tell the agent how to recover, not just what errors exist

6. **Progress reporting**: Keep users informed at each phase

### What NOT to Include

```markdown
❌ "This agent autonomously..."        → ✅ "You are an agent that..."
❌ "When to Use This Agent"            → ✅ (put in description field)
❌ "Example Invocations"               → ✅ (not needed in prompt)
```

## Frontmatter Fields

### Required

| Field | Description |
|-------|-------------|
| `name` | Unique identifier (lowercase, hyphens) |
| `description` | What it does + when to use (for discovery) |

### Optional

| Field | Description | Default |
|-------|-------------|---------|
| `skills` | Comma-separated skills to auto-load | None |
| `model` | `sonnet`, `opus`, `haiku`, or `inherit` | `inherit` |
| `tools` | Comma-separated tools to allow | All |
| `permissionMode` | `default`, `acceptEdits`, `bypassPermissions`, `plan` | `default` |

### Description Tips

The description determines when Claude invokes your agent. Make it:

- **Specific**: State what tasks the agent handles
- **Keyword-rich**: Use terms users would naturally say

```yaml
# Good
description: Autonomously builds complete BigQuery data models end-to-end from requirements through testing and monitoring. Use when implementing full ETL pipelines or new tables.

# Good
description: Safely migrates BigQuery schemas and updates all dependent queries, tests, and documentation. Use when changing table schemas or adding columns.
```

### Model Selection

- **`sonnet`**: Best balance - use for most agents
- **`opus`**: Complex reasoning - use sparingly
- **`haiku`**: Fast/cheap - use for simple orchestration

## Publishing

1. Add to `.claude-plugin/marketplace.json`:
   ```json
   "agents": [
     "./agents/etl-orchestrator.md",
     "./agents/your-new-agent.md"
   ]
   ```

2. Document in `docs/agents/available-agents.md`

3. Test thoroughly (see [Testing Agents](testing-agents.md))

4. Submit PR

## Next Steps

- [Agent Prompt Patterns](agent-prompt-patterns.md) - Detailed patterns and examples
- [Testing Agents](testing-agents.md) - Test your agent locally
- [Available Agents](available-agents.md) - See existing agents
