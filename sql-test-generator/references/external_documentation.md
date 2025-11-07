# External Documentation

## Official BigQuery ETL Testing Guide

**Primary resource:** https://mozilla.github.io/bigquery-etl/cookbooks/testing/

This guide covers:
- Test structure and file organization
- Environment setup with Google Cloud
- Running tests with pytest
- Troubleshooting common issues
- Integration test configuration

## Key Documentation Sections

### Testing Cookbook
- **URL:** https://mozilla.github.io/bigquery-etl/cookbooks/testing/
- **Topics:**
  - Setting up test fixtures
  - Running SQL query tests
  - Python query tests
  - Integration testing

### Query Structure
- **URL:** https://mozilla.github.io/bigquery-etl/cookbooks/query_structure/
- **Topics:**
  - SQL file conventions
  - Query parameters
  - Partitioning and clustering

### Common Patterns
- **URL:** https://mozilla.github.io/bigquery-etl/cookbooks/common_workflows/
- **Topics:**
  - Working with user-facing datasets
  - Incremental queries
  - Backfilling data

## Mozilla BigQuery UDFs

**Repository:** https://github.com/mozilla/bigquery-etl/tree/main/sql/mozfun

Common UDFs used in queries:
- `mozfun.map.mode_last` - Map updates keeping last value
- `mozfun.map.get_key` - Extract value from map by key
- `mozfun.norm.*` - Normalization functions
- `mozfun.hist.*` - Histogram functions

## BigQuery Documentation

### Standard SQL Reference
- **URL:** https://cloud.google.com/bigquery/docs/reference/standard-sql/
- Key topics for tests:
  - Data types (especially STRING vs FLOAT64 for version numbers)
  - ARRAY and STRUCT handling
  - Date and timestamp functions

### Test Framework
- **pytest-bigquery-mock:** Used by bigquery-etl for mocking BigQuery queries
- Allows running tests without hitting production BigQuery

## Environment Setup

### Google Cloud CLI
- **Installation:** https://cloud.google.com/sdk/docs/install
- **Auth setup:** https://cloud.google.com/docs/authentication/application-default-credentials

### pytest Configuration
Tests use pytest with custom bigquery-etl fixtures:
- Automatic schema inference from YAML
- Table initialization from fixtures
- Query parameter substitution

## Schema Discovery (NOT DataHub!)

**IMPORTANT: Do NOT use DataHub for schema lookups. Use these token-efficient alternatives:**

### Schema Discovery Priority Order

1. **🥇 Local schema.yaml files (BEST - zero tokens):**
   ```bash
   # Check for derived tables
   find sql/ -path "*/dataset/table/schema.yaml"

   # Example
   cat sql/moz-fx-data-shared-prod/telemetry_derived/clients_daily_v1/schema.yaml
   ```

2. **🥈 Glean Dictionary for _live and _stable tables:**
   ```bash
   # Find the table
   find /Users/mozilla/Documents/GitHub/glean-dictionary/src/data/ \
     -name "*events*" -path "*/tables/*"

   # Extract ONLY specific fields (token-efficient)
   grep -A 10 "## event\.name" /path/to/table.md
   ```

   **See `../metadata-manager/references/glean_dictionary_patterns.md` for:**
   - Token-efficient extraction strategies
   - How to handle large files (200+ columns)
   - Common table patterns

3. **🥉 BigQuery ETL Documentation:**
   - https://mozilla.github.io/bigquery-etl/
   - Browse dataset schemas online

### When to Use DataHub (Lineage ONLY)

**DataHub is for discovering table relationships, NOT schemas:**

```bash
# Use the lineage helper script
python ../metadata-manager/scripts/datahub_lineage.py telemetry_derived.clients_daily_v1
```

**What DataHub is good for:**
- ✅ Finding upstream/downstream dependencies
- ✅ Understanding which tables are related
- ✅ Discovering table usage patterns

**What DataHub is BAD for:**
- ❌ Getting schemas (use /sql or Glean Dictionary)
- ❌ Getting field descriptions (too verbose, token-heavy)
- ❌ General exploration (use other methods)

### Complete Schema Discovery Workflow

**See `../metadata-manager/references/schema_discovery_guide.md` for:**
- Complete workflow with examples
- Token efficiency best practices
- Handling live/stable tables
- Special cases and troubleshooting

**Key principle:** Always prefer local files → Glean Dictionary → DataHub (lineage only)

## Related Skills Documentation

### bigquery-etl-core
Provides foundational knowledge about:
- Repository structure
- Naming conventions
- Common patterns

### metadata-manager
Works with sql-test-generator for:
- Updating tests when queries change
- Managing schema files
- Keeping tests in sync with query logic

### query-writer
Creates queries that sql-test-generator then tests:
- SQL query patterns
- Jinja templating
- Python query scripts
