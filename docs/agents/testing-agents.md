# Testing Agents

Test your agent locally before publishing.

## Setup

Use the dev setup script to symlink your local agent files:

```bash
./scripts/dev-setup.sh
```

This creates symlinks from `~/.claude/agents/` to your local repo. Changes to agent files are reflected immediately.

See [Local Development](../getting-started/local-development.md) for full setup details.

## Test Workflow

```bash
# 1. Set up symlinks (once)
./scripts/dev-setup.sh

# 2. Start Claude Code
claude

# 3. Give a task that matches your agent's description
"Build a new table for user retention metrics"
```

## What to Verify

### Agent invocation
- Agent is selected for appropriate tasks
- Skills load correctly (check for errors)
- Agent can invoke each skill

### Workflow execution
- Phases execute in order
- Checkpoints work (validation before proceeding)
- Progress is reported at each phase

### Error handling
- Intentionally cause failures to test recovery
- Invalid query → Agent should detect and fix
- Test failure → Agent should diagnose and retry
- Missing info → Agent should ask (not assume)

### Output validation
- All expected files created
- Files in correct locations
- Validation commands pass
- Tests pass

## Debugging

**Agent not invoked?**

- Check the `description` field matches user intent
- Try more explicit phrasing that matches keywords

**Skills not loading?**

- Verify `skills` field in frontmatter lists correct skill names
- Check skill files exist and have valid frontmatter

**Premature completion?**

- Add explicit verification steps after each phase
- Use "DO NOT proceed until..." checkpoints

## Cleanup

Remove symlinks when done:

```bash
./scripts/dev-setup.sh --clean
```
