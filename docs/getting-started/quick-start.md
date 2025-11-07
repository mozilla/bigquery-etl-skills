# Quick Start

Get hands-on with BigQuery ETL Skills through practical examples.

## Your First Query

Let's create a simple aggregation query from scratch:

```
Write a query that counts daily active users from clients_daily for Firefox Desktop
```

Claude will:

1. ✅ Use **bigquery-etl-core** to understand conventions
2. ✅ Use **query-writer** to create the SQL
3. ✅ Use **metadata-manager** to generate schema and metadata files
4. ✅ Optionally use **sql-test-generator** to create unit tests

## Common Tasks

### Create Unit Tests

```
Create unit tests for telemetry_derived/events_daily_v1
```

### Update an Existing Query

```
Add a new field to telemetry_derived/clients_daily_v6
that calculates the ratio of searches with ads
```

### Gather Requirements

```
I need to create a table tracking campaign click-through rates.
Help me gather requirements.
```

### Add Monitoring

```
Add Bigeye monitoring for telemetry_derived/clients_daily_v6
```

## How It Works

!!! info "Automatic Skill Selection"
    Claude automatically selects the right skills based on your request. You don't need to explicitly invoke them—just describe what you want naturally!

When you make a request, Claude:

1. Analyzes your intent
2. Selects appropriate skills
3. Executes the workflow
4. Iterates based on your feedback

## Tips for Success

!!! tip "Be Specific"
    - ✅ "Create a daily aggregation query for active users"
    - ❌ "Help with a query"

!!! tip "Include Paths"
    Mention specific tables: `telemetry_derived/clients_daily_v6`

!!! tip "Work in Context"
    Launch Claude from your bigquery-etl directory for file operations

