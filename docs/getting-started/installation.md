# Installation

Install the BigQuery ETL Skills plugin directly from a Claude Code session in your IDE

## Prerequisites

- Claude Code installed and configured

## Installation Steps

### 1. Launch Claude Code

Open your terminal and launch Claude Code:

```bash
claude
```

### 2. Add the Marketplace

Add this repository as a plugin marketplace in Claude Code:

```bash
/plugin marketplace add https://github.com/mozilla/bigquery-etl-skills.git
```

### 3. Install the Plugin

Install the bigquery-etl-skills plugin:

```bash
/plugin install bigquery-etl-skills
```

### 4. Verify Installation

The skills should now be available. Open a new Claude Code session and ask:

```
What skills are available?
```

You should see all 7 BigQuery ETL skills listed.

## Next Steps

Once installed:

- Check out the [Quick Start](quick-start.md) guide for hands-on examples
- Read about [Using Skills](using-skills.md) to understand how to work with the plugin
- Explore the [Skills Reference](../skills/overview.md) for detailed documentation

## Troubleshooting

!!! tip "Skills Not Available?"
    If skills don't appear after installation, try:

    1. Restart Claude Code
    2. Open a new session
    3. Verify the marketplace was added: `/plugin marketplace list`
    4. Check plugin status: `/plugin list`

!!! note "Working Directory"
    For best results with BigQuery ETL file generation, launch Claude Code from within your local bigquery-etl repository directory.
