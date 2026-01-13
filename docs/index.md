# BigQuery ETL Skills

A comprehensive Claude Code plugin that accelerates development workflows on Mozilla's [bigquery-etl](https://github.com/mozilla/bigquery-etl) repository using [Claude Code Skills](https://support.claude.com/en/articles/12512176-what-are-skills) and specialized agents.


!!! note "Designed for bigquery-etl"
    This plugin works best when launched from your local development environment within the [bigquery-etl](https://github.com/mozilla/bigquery-etl) repository.

## What's Included

### Skills

Skills are specialized instruction sets that Claude loads dynamically to complete specific tasks. This plugin includes skills covering:

- Query writing (SQL and Python)
- Test generation
- Metadata and schema management
- Data quality monitoring
- Requirements gathering

**Learn more**: [Skills Overview](skills/overview.md)

### Agents

Agents are autonomous assistants that coordinate multiple skills to accomplish complex, multi-step workflows. This plugin includes agents for:

- End-to-end data model creation
- Schema migration (coming soon)
- And more...

**Learn more**: [Agents Overview](agents/overview.md)

### Not Sure Which to Use?

See the [Skills vs Agents guide](getting-started/skills-vs-agents.md) for a detailed comparison and decision framework.

## What You Can Do

Once installed, you can:

- **Build complete data models**: Let the ETL orchestrator agent handle everything from requirements through testing and monitoring

- **Work step-by-step with skills**: Use individual skills for focused tasks like writing queries or generating tests

- **Modify existing queries safely**: Check downstream dependencies and update queries with proper conventions

- **Add comprehensive unit tests**: Generate test fixtures with realistic input/output data

- **Set up production monitoring**: Create Bigeye data quality configurations

## Getting Started

For more information about skills and agents:

- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Equipping agents for the real world with Agent Skills](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)


## Quick Links

<div class="grid cards" markdown>

- :material-download: **[Installation Guide](getting-started/installation.md)**

    Get up and running in minutes

- :material-lightning-bolt: **[Quick Start](getting-started/quick-start.md)**

    Jump right in with practical examples

- :material-thought-bubble: **[Skills vs Agents](getting-started/skills-vs-agents.md)**

    Understand when to use skills vs agents

- :material-cog: **[Available Skills](skills/available-skills.md)**

    See all 7 specialized skills

- :material-robot: **[Available Agents](agents/available-agents.md)**

    Explore agents

</div>
