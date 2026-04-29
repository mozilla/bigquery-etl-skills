---
name: metadata-manager
description: Use this skill when creating or updating DAG configurations (dags.yaml) and metadata.yaml files for BigQuery tables. Handles creating new DAGs when needed and coordinates test updates when queries are modified (invokes sql-test-generator as needed). Works with bigquery-etl-core, query-writer, and sql-test-generator skills. For schema.yaml creation and description enrichment, use the schema-enricher or schema-creation-agent instead.
---

# Metadata Manager

**Composable:** Works with bigquery-etl-core (for conventions), query-writer (for queries), and sql-test-generator (for test updates)
**When to use:** Creating/updating DAG configurations and metadata.yaml files, coordinating test updates when queries are modified

> **Note:** Schema.yaml creation and description enrichment are handled by the `schema-enricher` skill and `schema-creation-agent`. Use those for schema work.

## Overview

Generate and manage metadata.yaml files and DAG configurations following Mozilla BigQuery ETL conventions. This skill handles:
- Creating new DAGs when no suitable existing DAG is found
- Generating metadata.yaml files for new tables
- Coordinating test updates when queries are modified (handles simple updates directly, invokes sql-test-generator for complex fixture creation)

**For comprehensive documentation, see:**
- Creating derived datasets: https://mozilla.github.io/bigquery-etl/cookbooks/creating_a_derived_dataset/
- Scheduling reference: https://mozilla.github.io/bigquery-etl/reference/scheduling/
- Recommended practices: https://mozilla.github.io/bigquery-etl/reference/recommended_practices/

## 🚨 REQUIRED READING - Start Here

**BEFORE creating or modifying metadata/DAG files, READ these references:**

1. **DAG Discovery:** READ `references/dag_discovery.md`
   - How to find the right Airflow DAG for your table
   - Common DAG patterns

2. **DAG Creation:** READ `references/dag_creation_guide.md` (when creating new DAGs)
   - When to create a new DAG vs reuse existing
   - Complete DAG creation workflow
   - Configuration options and best practices

3. **Metadata YAML Guide:** READ `references/metadata_yaml_guide.md`
   - All metadata.yaml options and their meanings
   - Scheduling configuration
   - Partitioning and clustering options
   - Ownership and labels

## 📋 Templates - Copy These Structures

**When creating a new DAG, READ and COPY from these templates:**

- **Daily scheduled DAG?** → READ `assets/dag_template_daily.yaml`
  - Most common pattern for daily processing at 2 AM UTC

- **Hourly scheduled DAG?** → READ `assets/dag_template_hourly.yaml`
  - For real-time or frequent processing (every hour)

- **Custom schedule DAG?** → READ `assets/dag_template_custom.yaml`
  - For weekly, multi-hour, or specific time requirements

**When creating metadata.yaml, READ and COPY from these templates:**

- **Daily partitioned table?** → READ `assets/metadata_template_daily_partitioned.yaml`
  - Most common pattern for daily aggregations

- **Hourly partitioned table?** → READ `assets/metadata_template_hourly_partitioned.yaml`
  - For real-time or hourly aggregations

- **Full refresh table?** → READ `assets/metadata_template_full_refresh.yaml`
  - For tables that recalculate all data each run

## Quick Start

### Creating New Table Metadata

**Step 1: Find or create the appropriate DAG (use this priority order)**
1. **FIRST:** Search local `dags.yaml` files using grep for keywords related to the dataset/product
2. **SECOND:** Check `references/dag_discovery.md` for common DAG patterns
3. **IF NO SUITABLE DAG EXISTS:** Create a new DAG
   - **READ `references/dag_creation_guide.md` for when to create vs reuse**
   - Present DAG options to the user (existing similar DAG vs new DAG)
   - If creating new DAG:
     - Choose template: `assets/dag_template_daily.yaml`, `dag_template_hourly.yaml`, or `dag_template_custom.yaml`
     - Infer values from context (dataset name, product area, similar tables)
     - Ask user to confirm/modify: schedule, owner, start_date, impact tier
     - Add new DAG entry to the **bottom** of `dags.yaml`
     - Validate with `./bqetl dag validate <dag_name>`

**Step 2: Create directory structure**
```bash
./bqetl query create <dataset>.<table> --dag <dag_name>
```

**Step 3: Create metadata.yaml**
- Use templates from `assets/` as a starting point
- Choose the appropriate template based on partitioning strategy
- Customize with owners, description, labels, scheduling, and BigQuery config
- See `references/metadata_yaml_guide.md` for detailed options

**Step 4: Create schema.yaml**
> Schema.yaml creation and description enrichment are owned by the `schema-enricher` skill.
> Invoke `schema-enricher` or `schema-creation-agent` for this step.

**Step 5: Deploy schema (if updating existing table)**
```bash
./bqetl query schema deploy <dataset>.<table>
```

### Updating Existing Queries

When modifying an existing query.sql, follow the test update workflow:

**1. Check for existing tests:**
```bash
ls tests/sql/<project>/<dataset>/<table>/
```

**2. Update the query.sql file** with your changes

**3. Update schema.yaml if output changed:**
> Delegate schema.yaml updates to the `schema-enricher` skill.

**4. If tests exist, update them:**
- **New source tables added?** → **Invoke sql-test-generator skill** to add fixtures to ALL tests
- **Source tables removed?** → Delete fixture files
- **Output schema changed?** → Update expect.yaml
- **Logic changed?** → Review and update test data/expectations

**5. Run tests:**
```bash
pytest tests/sql/<project>/<dataset>/<table>/ -v
```

**6. Handle test failures:**
- ✅ Expected failures (schema/logic changes) → Update expect.yaml
- ✅ Missing fixtures → **Invoke sql-test-generator skill**
- ❌ Production queries (thousands of rows) → **STOP, invoke sql-test-generator skill**
- ❌ Unexpected failures → Debug query changes

See `../query-writer/references/test_update_workflow.md` for complete details and the query modification checklist.

## DAG Management

### When to Create a New DAG

Before creating a new DAG, **always search for existing DAGs** that could be reused. Create a new DAG only when:
- **New product or service** requires isolated pipeline
- **Different scheduling requirements** than existing DAGs
- **Unique dependencies** that don't fit existing DAGs
- **Team ownership boundaries** require separate control

**DO NOT create a new DAG if** an existing DAG covers the same product area or schedule.

### Creating a New DAG

When no suitable DAG exists:

**1. Present options to the user:**
- List similar existing DAGs (if any close matches)
- Propose creating a new DAG with inferred configuration

**2. Choose appropriate template:**
- **Daily DAG** (`assets/dag_template_daily.yaml`) - Most common for daily aggregations
- **Hourly DAG** (`assets/dag_template_hourly.yaml`) - For real-time/frequent processing
- **Custom schedule** (`assets/dag_template_custom.yaml`) - Weekly, multi-hour, or specific times

**3. Gather required information:**
- **DAG name:** `bqetl_<product>` or `bqetl_<product>_<schedule>`
- **Schedule:** When should it run? (cron format or interval like "3h")
- **Owner:** Email address of primary owner
- **Start date:** When should processing begin? (YYYY-MM-DD)
- **Impact tier:** tier_1 (critical), tier_2 (important), tier_3 (nice-to-have)
- **Description:** Purpose, data sources, important notes

**4. Add DAG to dags.yaml:**
- Add new entry at the **bottom** of `dags.yaml`
- Use template as base and customize with gathered information
- Include all required fields: schedule_interval, default_args, owner, start_date, email, tags

**5. Validate:**
```bash
./bqetl dag validate <dag_name>
```

**See `references/dag_creation_guide.md` for:**
- Complete DAG creation workflow
- Configuration reference (schedules, retries, impact tiers)
- Common patterns and examples
- Best practices and troubleshooting

## Metadata Files (metadata.yaml)

Metadata files define table ownership, scheduling, partitioning, and BigQuery configuration.

**Required fields:**
- `friendly_name` - Human-readable table name
- `description` - Multi-line description of purpose
- `owners` - List of email addresses and/or GitHub teams (e.g., `mozilla/ads_data_team`)
  - **Use team detection script to find relevant teams:**
    ```bash
    python scripts/detect_teams.py
    ```
  - Recommends teams based on existing metadata files in `/sql`
  - Teams provide better coverage than individual emails
  - **See "Script Maintenance" section below for testing and troubleshooting**

**Common sections:**
- `labels` - application, schedule, table_type, dag, owner1
- `scheduling` - dag_name, date_partition_parameter, start_date
- `bigquery.time_partitioning` - type, field, expiration_days
- `bigquery.clustering` - fields for clustering (max 4)

**See `references/metadata_yaml_guide.md` for:**
- Complete scheduling options
- Partitioning strategies (day/hour)
- Clustering best practices
- Common label values
- Data retention policies

## Integration with Other Skills

### Works with bigquery-etl-core
- References core skill for conventions and patterns
- Uses common metadata structures and labeling

### Works with query-writer
- **After query-writer creates queries:** Use metadata-manager to generate metadata.yaml
- **Invocation:** After query.sql is written

### Works with schema-enricher / schema-creation-agent
- **For schema.yaml creation and description enrichment:** Delegate to `schema-enricher` or `schema-creation-agent`
- **Invocation:** After metadata.yaml is created, invoke schema-enricher for schema work

### Works with sql-test-generator
- **When queries are modified:** Coordinates test update workflow
- **Handles simple updates directly:** expect.yaml changes, removing fixtures for deleted tables
- **Delegates complex fixture creation:** Invokes sql-test-generator for new source tables, JOINs, or production query issues
- **Invocation:** When new source tables added, tests query production, or complex test fixtures needed

### Typical Workflows

**Creating new table:**
1. query-writer creates query.sql
2. **metadata-manager** generates metadata.yaml and DAG configuration
3. **schema-enricher** or **schema-creation-agent** creates and enriches schema.yaml
4. metadata-manager invokes sql-test-generator for tests

**Updating existing query:**
1. Modify query.sql
2. **schema-enricher** updates schema.yaml
3. **metadata-manager** coordinates test updates (handles simple updates, invokes sql-test-generator for complex fixture creation)
4. Run tests to validate

## Key Commands Reference

```bash
# Create new query directory with templates
./bqetl query create <dataset>.<table> --dag <dag_name>

# Deploy schema to BigQuery (updates existing table)
./bqetl query schema deploy <dataset>.<table>

# Validate query and metadata
./bqetl query validate <dataset>.<table>

# Validate DAG configuration
./bqetl dag validate <dag_name>

# Run tests
pytest tests/sql/<project>/<dataset>/<table>/ -v
```

## Best Practices

### ⚠️ Configuration Standards

**CRITICAL: Only use documented configurations or patterns from existing metadata files.**

- **DO:** Reference Mozilla BigQuery ETL documentation
- **DO:** Copy patterns from existing metadata.yaml files in `/sql`
- **DO:** Use configurations seen in templates in `assets/`
- **DO NOT:** Invent new configuration options
- **DO NOT:** Use undocumented fields or values

When uncertain about a configuration:
1. Check `references/metadata_yaml_guide.md`
2. Search existing metadata files: `grep -r "field_name" sql/*/metadata.yaml`
3. Ask user if the configuration is supported

### For metadata.yaml
- List at least 2 owners for redundancy (individuals and/or GitHub teams like `mozilla/team_name`)
- Use `python scripts/detect_teams.py` to find relevant GitHub teams (see "Script Maintenance" for testing)
- Write clear descriptions explaining purpose and use cases
- Use consistent labels matching similar tables
- Set appropriate partitioning and clustering for query patterns
- Consider data retention policies (expiration_days)

### For test updates
- **Always run tests after query changes**
- Invoke sql-test-generator for new source tables or complex changes
- Update expect.yaml for schema/output changes
- Add new test scenarios for new logic paths
- Never commit tests that query production tables

## Helper Scripts

This skill provides helper scripts in `scripts/`:
- **`detect_teams.py`** - Find GitHub teams from metadata.yaml files
- **`datahub_lineage.py`** - Generate DataHub lineage query parameters

**See `references/script_maintenance.md` for:**
- Testing all scripts
- Auto-update workflow when scripts fail
- Common issues and solutions
- Adding new scripts

## Reference Examples

**In the repository:**
- Simple metadata: `sql/moz-fx-data-shared-prod/mozilla_vpn_derived/users_v1/metadata.yaml`
- Partitioned metadata: `sql/moz-fx-data-shared-prod/telemetry_derived/clients_daily_event_v1/metadata.yaml`

**In this skill:**
- See `assets/` directory for metadata and DAG templates
- See `references/` directory for complete documentation

### DataHub Usage (CRITICAL for Token Efficiency)

**BEFORE using any DataHub MCP tools (`mcp__datahub-cloud__*`), you MUST:**
- **READ `../bigquery-etl-core/references/datahub_best_practices.md`** - Token-efficient patterns for DAG discovery
- Always prefer local files (dags.yaml, metadata.yaml) over DataHub queries

**Use DataHub for:**
- Lineage/dependencies when can't infer from bqetl:
  - Tables from Glean telemetry or older telemetry sources
  - Syndicated datasets (directories without query.sql/query.py/view.sql)
  - These are often from dev teams' postgres databases in their own projects
  - Check metadata.yaml for available information first

**For lineage queries, use the helper script:**
```bash
python scripts/datahub_lineage.py <table_identifier>
```

This provides parameters for efficient DataHub queries that return only essential lineage information.

**See "Script Maintenance" section below for testing and troubleshooting.**
