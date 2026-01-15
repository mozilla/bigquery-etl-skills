# Local Development

Test changes to skills and agents locally before committing.

## Quick Start

From the repo root:

```bash
# Set up local development symlinks
./scripts/dev-setup.sh

# Start Claude Code to test
claude

# Clean up when done
./scripts/dev-setup.sh --clean
```

## How It Works

The `dev-setup.sh` script creates symlinks from your local repo to `~/.claude/`:

```
~/.claude/
├── skills/
│   └── bigquery-etl-skills -> /path/to/repo/skills/
└── agents/
    └── etl-orchestrator.md -> /path/to/repo/agents/etl-orchestrator.md
```

Changes you make to skills or agents in the repo are immediately available in Claude Code sessions.

## Testing Skills

After running `dev-setup.sh`:

1. Start a new Claude Code session: `claude`
2. Invoke a skill: `/query-writer` or `/metadata-manager`
3. Verify your changes work as expected
4. Iterate on the skill files and test again

!!! tip "No restart needed"
    Skills are loaded fresh each time they're invoked. You don't need to restart Claude Code after editing a skill.

## Testing Agents

After running `dev-setup.sh`:

1. Start a new Claude Code session: `claude`
2. Give a task that would invoke the agent
3. The agent prompt is loaded when the Task tool spawns a subagent

!!! note "Agent testing"
    Agents run as subagents via the Task tool. To test an agent directly, you can also paste its content into a conversation and give it a task.

## Development Workflow

### For skill changes

```bash
# 1. Set up (once)
./scripts/dev-setup.sh

# 2. Edit skill files
# skills/query-writer/skill.md
# skills/query-writer/references/*.md
# skills/query-writer/assets/*

# 3. Test in Claude Code
claude
# > /query-writer
# > [test your changes]

# 4. Iterate until satisfied

# 5. Clean up (optional - symlinks don't hurt)
./scripts/dev-setup.sh --clean
```

### For agent changes

```bash
# 1. Set up (once)
./scripts/dev-setup.sh

# 2. Edit agent file
# agents/etl-orchestrator.md

# 3. Test in Claude Code
claude
# > Build a new table for user metrics...
# > [agent should be invoked]

# 4. Or test by pasting the prompt directly:
# > [paste agent prompt content]
# > ---
# > Build a new table for user metrics...
```

## Cleanup

Remove symlinks when you're done testing:

```bash
./scripts/dev-setup.sh --clean
```

This removes only the symlinks created by the setup script, leaving other `~/.claude` content intact.

## Troubleshooting

### Skills not appearing

1. Verify symlinks exist: `ls -la ~/.claude/skills/`
2. Start a **new** Claude Code session
3. Check for errors in setup: `./scripts/dev-setup.sh`

### Agent not being invoked

Agents are invoked automatically when appropriate tasks are given. To force-test an agent:

1. Copy the agent prompt content
2. Paste it at the start of a conversation
3. Give a task that matches the agent's purpose

### Conflicts with installed plugin

If you have the plugin installed via marketplace AND local symlinks:

1. Local symlinks take precedence for agents (same filename)
2. Skills may conflict - uninstall the marketplace version during development:
   ```bash
   /plugin uninstall bigquery-etl-skills
   ```
3. Re-install when done testing:
   ```bash
   /plugin install bigquery-etl-skills
   ```

## Team Workflow

When multiple team members are developing:

1. Each developer runs `./scripts/dev-setup.sh` locally
2. Make changes on a feature branch
3. Test locally with Claude Code
4. Push and create PR
5. Reviewers can check out the branch and test with the same setup
6. Merge to main when approved
7. Plugin updates are available to all users on next sync
