# Skills vs Agents

When extending this plugin, choose the right building block for your use case.

## At a Glance

| | Skills | Agents |
|--|--------|--------|
| **Purpose** | Domain expertise | Workflow orchestration |
| **Structure** | Instructions + references + assets | Phased instructions with decision logic |
| **Composition** | Can reference other skills | Invoke skills in sequence |
| **Autonomy** | Claude follows instructions | Agent makes decisions and iterates |

## When to Build a Skill

Build a skill when you have **domain-specific expertise** to encode:

- SQL patterns and conventions
- File format specifications (schema.yaml, metadata.yaml)
- Tool usage (bqetl commands, DataHub queries)
- Reference material that Claude should consult

**Skills are building blocks.** They're focused, reusable, and composable.

### Skill Structure

```
skills/my-skill/
├── skill.md           # Instructions (imperative voice)
├── references/        # Detailed documentation
└── assets/            # Templates and examples
```

The `skill.md` tells Claude what to do. References provide depth. Assets give copy-paste starting points.

## When to Build an Agent

Build an agent when you need **multi-step orchestration**:

- Coordinate multiple skills in sequence
- Make decisions based on intermediate results
- Handle errors and iterate autonomously
- Deliver complete outcomes (not just single files)

**Agents are orchestrators.** They invoke skills and manage workflow.

### Agent Structure

```
agents/my-agent.md     # Single file with phased instructions
```

The agent prompt defines:

1. **Requirements validation** - What must be known before starting
2. **Phases** - Sequential steps with clear checkpoints
3. **Decision criteria** - When to take which path
4. **Error handling** - How to recover from failures
5. **Completion criteria** - When the work is done

## How They Compose

```
┌─────────────────────────────────────────┐
│              etl-orchestrator           │
│                  (agent)                │
├─────────────────────────────────────────┤
│  Phase 1: Load bigquery-etl-core        │
│  Phase 2: Invoke query-writer      ─────┼──→ query-writer (skill)
│  Phase 3: Invoke metadata-manager  ─────┼──→ metadata-manager (skill)
│  Phase 4: Invoke sql-test-generator ────┼──→ sql-test-generator (skill)
│  Phase 5: Invoke bigconfig-generator ───┼──→ bigconfig-generator (skill)
│  Phase 6: Validate and report           │
└─────────────────────────────────────────┘
```

Skills can also reference each other:

```
query-writer (skill)
  └── references bigquery-etl-core for conventions
  └── coordinates with sql-test-generator for test updates
```

## Decision Guide

**Build a skill if:**

- The knowledge is useful standalone
- Multiple agents or workflows could use it
- It's focused on one domain (queries, schemas, tests)

**Build an agent if:**

- The workflow spans multiple skills
- Autonomous decision-making adds value
- Error recovery should be automatic
- The deliverable is a complete outcome

**Start with skills.** Build agents when you find yourself repeatedly coordinating the same skills in sequence.

## Examples in This Plugin

### Skills (domain expertise)

- **query-writer**: SQL/Python query patterns
- **metadata-manager**: schema.yaml and metadata.yaml conventions
- **sql-test-generator**: Test fixture creation
- **bigconfig-generator**: Bigeye monitoring configuration

### Agents (orchestration)

- **etl-orchestrator**: Coordinates all skills to build complete tables

## Further Reading

- [Creating Agents](../agents/creating-agents.md) - How to write agent prompts
- [Skills Overview](../skills/overview.md) - Skill structure and conventions
- [Local Development](local-development.md) - Test your changes
