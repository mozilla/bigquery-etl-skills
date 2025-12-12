# Mozilla Data Platform Ecosystem - Construction Focus

Skills in the bigquery-etl repository can extend beyond SQL queries to encompass configuration generation, validation, and monitoring for the Mozilla data platform. Understanding these tools and documentation sources helps create construction-focused skills.

## Core Documentation Hubs

**Mozilla Telemetry Docs** - https://docs.telemetry.mozilla.org/
- Comprehensive data platform documentation
- **Key sections for construction skills:**
  - **Metric Hub**: https://docs.telemetry.mozilla.org/concepts/metric_hub.html
    - YAML-based metric definitions for configuration generation
    - **Skill opportunity:** metric-hub-generator for creating metric configurations
  - **BigQuery Cookbooks**: https://docs.telemetry.mozilla.org/cookbooks/bigquery/
    - Patterns for creating derived datasets
  - **Glean Documentation**: https://docs.telemetry.mozilla.org/concepts/glean/glean.html
    - Schema structure for Glean tables (used in construction)

**BigQuery ETL Docs** - https://mozilla.github.io/bigquery-etl/
- Repository-specific documentation
- **Key sections for construction skills:**
  - **Cookbooks**: https://mozilla.github.io/bigquery-etl/cookbooks/
    - Creating derived datasets, testing, deployment workflows
  - **Reference**: https://mozilla.github.io/bigquery-etl/reference/
    - Configuration files: bigquery.yaml, dags.yaml, schema.yaml, metadata.yaml
    - Scheduling, incremental queries, recommended practices
  - **mozfun UDFs**: https://mozilla.github.io/bigquery-etl/mozfun/
    - Reusable functions for query construction

## Mozilla GitHub Organization

**Mozilla Public Repositories** - https://github.com/mozilla/?q=&type=public&language=&sort=

When creating skills, explore relevant Mozilla repositories to:

1. **Identify construction automation opportunities:**
   - Look for config files (YAML, JSON) that could be auto-generated
   - Find validation logic that could be automated
   - Look at Issues for common pain points in construction workflows

2. **Understand configuration patterns:**
   - See how different repos structure their config files
   - Find common conventions for validation and testing

**Key repositories for construction skills:**
- `mozilla/bigquery-etl` - Main BigQuery ETL repository
- `mozilla/metric-hub` - Metric definitions and configurations
- `mozilla/opmon` - Operational monitoring configurations
- `mozilla/jetstream` - Experiment analysis configurations

## Key Configuration-Focused Repositories

**Metric Hub** - https://github.com/mozilla/metric-hub
- YAML configuration files for metric definitions
- **Construction skill opportunity:** metric-hub-generator to create/validate metric configs

**OpMon (Operational Monitoring)** - https://github.com/mozilla/opmon
- Configuration-based monitoring definitions
- **Construction skill opportunity:** opmon-config-generator for monitoring configs

**Jetstream** - https://github.com/mozilla/jetstream
- Configuration-based experiment analysis
- **Construction skill opportunity:** jetstream-config-generator for analysis configs

**Experimenter** - https://github.com/mozilla/experimenter
- Experimentation platform with configuration files
- **Construction skill opportunity:** experiment-config-helper for experiment configurations

## Key APIs and Services for Construction

**ProbeInfo API** - https://probeinfo.telemetry.mozilla.org/
- Programmatic access to Glean metric metadata for construction
- Endpoints:
  - Metrics: `https://probeinfo.telemetry.mozilla.org/glean/{product}/metrics`
  - Pings: `https://probeinfo.telemetry.mozilla.org/glean/{product}/pings`
- **Construction uses:**
  - Fetch metric schemas for query generation
  - Validate metric references in queries

**DataHub MCP** - Available via `mcp__datahub-cloud__*` tools
- **Construction uses:**
  - Schema lookup (last resort after local files and Glean Dictionary)
  - Downstream impact analysis when modifying tables
  - Upstream validation when user provides table names
- **Already integrated** - existing skills use these tools following construction-focused patterns

## Configuration File Types

Understanding Mozilla's configuration files helps create validation and generation skills:

**bigquery.yaml** - BigQuery-specific configurations
- Table clustering, partitioning, labels
- Located alongside query.sql files

**dags.yaml** - Airflow DAG definitions
- Scheduling configuration for queries
- Located in `dags/` directory

**metric_hub configs** - Metric definitions in YAML
- Located in metric-hub repository
- Define metrics, dimensions, and data sources

**opmon configs** - Monitoring configurations
- Define monitoring for experiments/features

## Creating Construction Skills for the Broader Ecosystem

When creating skills that extend beyond bigquery-etl queries:

1. **Research the tool's documentation:**
   - Start at https://docs.telemetry.mozilla.org/
   - Find the tool's GitHub repository
   - Read README, docs/, and example config files
   - Understand configuration formats and workflows

2. **Identify construction automation opportunities:**
   - What files are manually created repeatedly?
   - What validation is tedious or error-prone?
   - Look at Issues in the repo for common pain points in building/modifying configs

3. **Consider integration points:**
   - How does this tool relate to bigquery-etl construction?
   - Can queries auto-generate configs for this tool?
   - Check how other Mozilla repos integrate with this tool

4. **Include proper references:**
   - Link to official documentation (docs.telemetry.mozilla.org)
   - Reference GitHub repositories (github.com/mozilla/*)
   - Include API endpoints if applicable (ProbeInfo for schemas)
   - Add example configuration files from the repo

## Example Construction Skill Ideas Beyond bigquery-etl

**metric-hub-generator:**
- Generate Metric Hub YAML configs from BigQuery queries
- Validate metric definitions against schemas
- References: https://docs.telemetry.mozilla.org/concepts/metric_hub.html

**opmon-config-generator:**
- Generate operational monitoring configs
- Create monitoring for new experiments
- Validate OpMon YAML files
- References: https://github.com/mozilla/opmon

**jetstream-config-generator:**
- Generate experiment analysis configurations
- Validate Jetstream config files
- References: https://github.com/mozilla/jetstream
