# Preventing Production Queries in Tests

## The Problem

**The #1 way tests accidentally query production data:**
- Missing fixture files for ANY table referenced in FROM/JOIN/UNION clauses
- When a fixture is missing, BigQuery falls back to querying the production table

This is especially critical for UNION/UNION ALL queries that reference multiple data sources.

## How to Prevent Production Queries

### Step 1: Identify ALL Source Tables

Before creating fixtures, identify every table the query references:

```bash
grep -E "FROM|JOIN" query.sql
```

Write down EVERY table you find. This is your checklist.

**Example output:**
```
FROM moz-fx-data-shared-prod.telemetry.clients_daily
LEFT JOIN moz-fx-data-shared-prod.telemetry.main_summary
UNION ALL
SELECT * FROM moz-fx-data-shared-prod.glean.baseline
UNION ALL
SELECT * FROM moz-fx-data-shared-prod.ads.impression_stats
```

Your checklist:
- [ ] moz-fx-data-shared-prod.telemetry.clients_daily
- [ ] moz-fx-data-shared-prod.telemetry.main_summary
- [ ] moz-fx-data-shared-prod.glean.baseline
- [ ] moz-fx-data-shared-prod.ads.impression_stats

### Step 2: Create Fixtures for ALL Tables

Create a fixture file for EVERY table on your checklist, even if it contributes minimal data:

```bash
tests/sql/<project>/<dataset>/<table>/<test_name>/
  ├── moz-fx-data-shared-prod.telemetry.clients_daily.yaml
  ├── moz-fx-data-shared-prod.telemetry.main_summary.yaml
  ├── moz-fx-data-shared-prod.glean.baseline.yaml
  ├── moz-fx-data-shared-prod.ads.impression_stats.yaml
  ├── query_params.yaml
  └── expect.yaml
```

**Critical:** File naming must match how the table is referenced in the query:
- Query uses `moz-fx-data-shared-prod.dataset.table` → file: `moz-fx-data-shared-prod.dataset.table.yaml`
- Query uses `dataset.table` → file: `dataset.table.yaml`
- Query uses `table` → file: `table.yaml`

### Step 3: Verify You're NOT Querying Production

After running `pytest`, check these indicators:

#### ✅ Signs you're using test fixtures correctly:

1. **"Initialized" lines in pytest output** - one for each source table:
   ```
   Initialized moz-fx-data-shared-prod.telemetry.clients_daily
   Initialized moz-fx-data-shared-prod.telemetry.main_summary
   Initialized moz-fx-data-shared-prod.glean.baseline
   Initialized moz-fx-data-shared-prod.ads.impression_stats
   ```
   Count should match your checklist from Step 1.

2. **Fast execution** - tests complete in <30 seconds

3. **Small result sets** - typically <10 rows, matching your expect.yaml

#### ❌ Signs you're querying production:

1. **Missing "Initialized" line** for one or more tables → add that fixture file

2. **Thousands of rows** in test output instead of a handful

3. **Real production values** in results (real client IDs, tile IDs, etc.)

4. **Slow execution** - taking >30 seconds or minutes

5. **Results much larger than expect.yaml**

## Production Query Checklist

Before finalizing tests, verify:
- [ ] I ran `grep -E "FROM|JOIN" query.sql` to find all source tables
- [ ] I created a fixture file for each source table found
- [ ] File naming matches how tables are referenced in the query
- [ ] I checked pytest output for "Initialized" messages matching each source table
- [ ] Test results are small and match my expect.yaml
- [ ] Test runs quickly (<30 seconds)

## UNION/UNION ALL Special Considerations

UNION queries are particularly prone to production query issues because they reference multiple tables.

### ❌ Wrong Approach: Separate Tests Per Source

```
tests/sql/.../table/test_legacy_only/
  └── moz-fx-data-shared-prod.legacy_source.table.yaml
  # Missing glean and ads fixtures → queries production!

tests/sql/.../table/test_glean_only/
  └── moz-fx-data-shared-prod.glean_source.table.yaml
  # Missing legacy and ads fixtures → queries production!
```

### ✅ Right Approach: One Comprehensive Test

```
tests/sql/.../table/test_union_all_sources/
  ├── moz-fx-data-shared-prod.legacy_source.table.yaml
  ├── moz-fx-data-shared-prod.glean_source.table.yaml
  ├── moz-fx-data-shared-prod.ads_source.table.yaml
  ├── query_params.yaml
  └── expect.yaml
```

All source fixtures in ONE test directory ensures no table hits production.

### When to Create Multiple Tests for UNION Queries

Create separate tests only when different date ranges or filter conditions change which sources contribute:

```
tests/sql/.../table/test_modern_date/
  # submission_date: 2024-12-15 (after cutoff)
  ├── moz-fx-data-shared-prod.legacy_source.table.yaml
  ├── moz-fx-data-shared-prod.glean_source.table.yaml
  ├── moz-fx-data-shared-prod.ads_source.table.yaml
  └── ...

tests/sql/.../table/test_historical_date/
  # submission_date: 2024-11-15 (before cutoff)
  ├── moz-fx-data-shared-prod.legacy_source.table.yaml
  ├── moz-fx-data-shared-prod.glean_source.table.yaml
  ├── moz-fx-data-shared-prod.ads_source.table.yaml
  └── ...
```

Each test still includes ALL source fixtures, just with different dates/conditions.

## If You Want a Source to Contribute No Data

Instead of omitting the fixture file (which causes production queries), use WHERE clause filtering:

```yaml
# moz-fx-data-shared-prod.legacy_source.table.yaml
# Query has WHERE loaded IS NULL - this data gets filtered out
- submission_timestamp: "2024-12-15 10:00:00"
  document_id: "filtered_out"
  loaded: 1  # Will be filtered by WHERE loaded IS NULL
  other_field: "value"
```

The fixture provides valid schema but the data gets filtered out by the query's WHERE clause.

## Environment Configuration

Tests require proper Google Cloud authentication:

```bash
export GOOGLE_PROJECT_ID=bigquery-etl-integration-test
gcloud config set project $GOOGLE_PROJECT_ID
gcloud auth application-default login
```

After running tests, switch back to main project:
```bash
export GOOGLE_PROJECT_ID=mozdata
gcloud config set project $GOOGLE_PROJECT_ID
```
