# Schema Discovery Guide

## Overview

When generating schema.yaml files for derived tables, follow this guide to get source table schemas efficiently and create high-quality field descriptions for table construction.

## Priority Order for Schema Discovery

**Use this order to find source table schemas:**

### 1. Local `/sql` Directory (FIRST - Always check here)

**When to use:**
- For any derived table (`_derived` dataset)
- For tables created in bigquery-etl repository
- Most efficient - already on disk, no API calls

**How to find:**
```bash
# Find schema.yaml for a source table
find sql/ -path "*/<dataset>/<table>/schema.yaml"

# Example: Finding clients_daily schema
find sql/ -path "*/telemetry_derived/clients_daily_v1/schema.yaml"
```

**What to extract:**
- Field names and types
- Field descriptions (use as base, improve if needed)
- Field modes (NULLABLE, REQUIRED, REPEATED)
- Nested structure (RECORD types)

**Advantages:**
- Fast - no network calls
- Complete schema with all metadata
- Includes internal derived tables not in other sources
- Token-efficient

### 2. Glean Dictionary (SECOND - For live telemetry tables)

**When to use:**
- Tables ending in `_live` or `_stable`
- Tables in datasets like: `firefox_desktop_live`, `fenix_stable`, `org_mozilla_firefox_live`
- These tables are NOT in the `/sql` directory

**How to access:**
- **URL:** https://dictionary.telemetry.mozilla.org/
- Search for table/app name (e.g., "firefox_desktop events")
- Browse to table and view all fields with descriptions
- Click on fields for detailed metric definitions
- Use WebFetch tool to retrieve specific table schemas when needed

**IMPORTANT - Token Management:**
- Glean Dictionary pages can have **very large** schemas (thousands of columns)
- Use WebFetch with targeted prompts to extract only the fields you need
- Request specific field information rather than full table schemas

**What to extract:**
- Field name
- Field type
- Field description (these are usually high-quality from Glean schemas)
- Nested fields for event extras, metrics

**Advantages:**
- Official source for Glean telemetry schemas
- High-quality descriptions from probe definitions
- Includes all metrics, events, and structured fields

**Example workflow:**
```bash
# 1. Check if table is a Glean telemetry table
# Pattern: *_live, *_stable, org_mozilla_*, firefox_desktop_live, etc.

# 2. Use WebFetch to get field information from Glean Dictionary
# URL pattern: https://dictionary.telemetry.mozilla.org/apps/<app>/tables/<table>
# Example: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events

# 3. Request specific fields rather than full schema
# WebFetch prompt: "Extract the schema for fields: event.name, event.category, event.timestamp"
```

### 3. DataHub MCP (Last resort or for validation)

**When to use DataHub for construction:**

1. **Downstream impact analysis (CRITICAL when modifying existing tables):**
   - Check what depends on a table you're modifying
   - Warn about schema changes that will affect downstream consumers
   - Use `get_lineage(upstream=False)` to find downstream dependencies

2. **Upstream validation (when user isn't completely sure):**
   - Validate that upstream tables provided by user actually exist
   - Confirm available columns for joins after user specifies tables

3. **Schema lookup (last resort):**
   - Schema files don't exist in `/sql` directory
   - Not available in Glean Dictionary
   - Syndicated datasets (directories without query.sql/query.py/view.sql)

4. **Field descriptions (use this hierarchy):**
   - **FIRST:** Check Glean Dictionary (for `_live`/`_stable` tables)
   - **SECOND:** Use DataHub if not found in Glean Dictionary
   - DataHub descriptions can be verbose, so extract only what's needed

**DO NOT use DataHub for:**
- ❌ Exploratory discovery of what data exists (out of scope)
- ❌ Finding alternative tables to use (user provides source tables)
- ❌ Schema lookup when local files or Glean Dictionary have the information
- ❌ First attempt at getting descriptions (try Glean Dictionary first for `_live`/`_stable` tables)
- ❌ General exploration (use local files first)

**Syndicated Datasets:**
Syndicated datasets are special cases where DataHub may be needed:
- Directories without `query.sql`, `query.py`, or `view.sql` files
- Usually from dev teams' postgres databases in their own GCP projects
- Won't have schema files in bqetl
- Sometimes `metadata.yaml` files will have more information
- Examples: Data synced from external services, third-party integrations

**For lineage queries, use the helper script:**
```bash
# Use the DataHub lineage helper script
python .claude/skills/metadata-manager/scripts/datahub_lineage.py <table_urn>
```

This script filters DataHub responses to return only essential lineage information.

## Schema Generation Workflow

### Step 1: Identify Source Tables

Parse the query.sql to identify all source tables:

```bash
# Extract FROM and JOIN tables
grep -E "FROM|JOIN" query.sql | grep -oE "`[^`]+`"
```

### Step 2: Discover Schemas Using Priority Order

For each source table:

1. **Check `/sql` directory first:**
   ```bash
   find sql/ -path "*/<dataset>/<table>/schema.yaml"
   ```

2. **If not found, check if it's a live/stable table:**
   - Pattern: `*_live`, `*_stable`, `org_mozilla_*`
   - Search Glean Dictionary

3. **For lineage/usage only:**
   - Use DataHub lineage helper script
   - Extract upstream tables, then repeat schema discovery for those

### Step 3: Extract Field Information

For each source table schema:

**Extract:**
- Field name
- Field type
- Field description
- Field mode (NULLABLE, REQUIRED, REPEATED)
- Nested fields (if RECORD type)

**Create mapping:**
```
source_table.field_name → {
  type: STRING,
  mode: NULLABLE,
  description: "Original description from source"
}
```

### Step 4: Check for Missing Descriptions in Source Tables

**Before generating the derived schema, check source tables for missing descriptions:**

1. **Count missing descriptions:**
   ```bash
   # Check a source table for missing descriptions
   grep -c 'description: ""' sql/.../schema.yaml
   ```

2. **Calculate percentage:**
   - Total fields vs fields with descriptions
   - If > 50% missing, source table needs improvement

3. **Notify user and ask:**
   - Present clear opportunity for metadata completeness
   - Ask if they want to generate descriptions for source table
   - Explain benefits: helps all downstream consumers

4. **If user says YES:**
   - Read full source table schema.yaml
   - Generate descriptions for ALL fields (not just the ones you're using)
   - Update source table's schema.yaml with Edit tool
   - Then proceed with derived table

5. **If user says NO:**
   - Proceed with derived table
   - Use basic descriptions based on field names

**See `schema_description_improvements.md` for:**
- Complete workflow for asking user
- How to generate descriptions
- Example user notifications

### Step 5: Generate Derived Schema

When generating schema.yaml for the derived table:

1. **Use source descriptions as base:**
   - Copy descriptions from source tables (now complete if user added them!)
   - Maintain consistency across derived tables

2. **Improve descriptions when needed:**
   - Add context specific to the derived table
   - Clarify transformations or aggregations
   - Add business context not in source

3. **Recommend updates (for existing but unclear descriptions):**
   - If source description exists but is unclear or vague
   - If you generated a better description
   - Recommend updating the source table's schema.yaml

### Step 6: Document Description Improvements

When you improve a source table's description:

**Create a recommendation:**
```markdown
## Recommended Source Schema Updates

The following source table descriptions could be improved:

### `moz-fx-data-shared-prod.telemetry_derived.clients_daily_v1`

**Field:** `active_hours_sum`
**Current description:** "Sum of active hours"
**Recommended description:** "Total active hours for the client during the submission date, calculated as sum of active_ticks * 5 seconds / 3600"
**Why:** Original description lacks detail about calculation method

**Field:** `search_count`
**Current description:** "Number of searches"
**Recommended description:** "Total count of search interactions across all search engines and access points (urlbar, searchbar, etc.)"
**Why:** Original description lacks scope and sources
```

## Special Cases

### Live and Stable Tables

**Characteristics:**
- End in `_live` or `_stable`
- NOT in `/sql` directory
- Can have **hundreds of columns** (events, metrics, client_info, etc.)

**Strategy:**
1. Search Glean Dictionary for the table
2. **DO NOT** read entire file - it may be massive
3. Extract only fields used in your query:
   ```bash
   # Get list of fields from your query
   grep -oE "field_name" query.sql | sort -u

   # Search for those specific fields in Glean Dictionary
   for field in $fields; do
     grep -A 5 "$field" /path/to/glean-dict/table.md
   done
   ```

### Cross-Project Tables

**Examples:**
- `moz-fx-data-shared-prod.*` → Main project (check /sql)
- `moz-fx-data-marketing-prod.*` → Other projects (not in /sql)

**Strategy:**
- Check if table is in bigquery-etl /sql directory
- If not, may need to check other repositories or use DataHub for lineage only
- For schemas, prefer documentation or Glean Dictionary if available

### External Tables (GCS, Sheets, etc.)

**Strategy:**
- These won't be in /sql or Glean Dictionary
- Use `./bqetl query schema update` to generate from BigQuery
- Add descriptions manually based on data source documentation

## Token Efficiency Best Practices

### DO:
- ✅ Use local /sql files whenever possible
- ✅ Search for specific fields in Glean Dictionary
- ✅ Extract only needed fields from large files
- ✅ Use helper scripts for DataHub queries
- ✅ Read Glean Dictionary files in targeted chunks

### DON'T:
- ❌ Read entire Glean Dictionary files for tables with hundreds of columns
- ❌ Use DataHub MCP for schema discovery
- ❌ Query DataHub for field descriptions
- ❌ Read multiple large files in parallel

## Examples

### Example 1: Derived Table from clients_daily

**Query uses:** `telemetry_derived.clients_daily_v1`

**Discovery steps:**
```bash
# 1. Check /sql directory
find sql/ -path "*/telemetry_derived/clients_daily_v1/schema.yaml"
# Found: sql/moz-fx-data-shared-prod/telemetry_derived/clients_daily_v1/schema.yaml

# 2. Read schema.yaml
# Extract field descriptions for fields used in query

# 3. Generate derived schema using those descriptions
```

### Example 2: Live Events Table

**Query uses:** `firefox_desktop_live.events_v1`

**Discovery steps:**
```bash
# 1. Check /sql directory
find sql/ -path "*/firefox_desktop_live/events_v1/schema.yaml"
# Not found - this is a live table

# 2. Use WebFetch to access Glean Dictionary
# URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events

# 3. Extract only fields used in the query (not all hundreds of fields)
# From query.sql: event.name, event.timestamp, event.category
# WebFetch prompt: "Extract the name, type, mode, and description for these fields: event.name, event.timestamp, event.category"

# 4. Generate schema with extracted fields
```

### Example 3: Need Lineage Information

**Query uses:** Unknown upstream of `telemetry_derived.main_summary_v4`

**Discovery steps:**
```bash
# 1. Use DataHub lineage helper (NOT for schema)
python .claude/skills/metadata-manager/scripts/datahub_lineage.py \
  "urn:li:dataset:(urn:li:dataPlatform:bigquery,moz-fx-data-shared-prod.telemetry_derived.main_summary_v4,PROD)"

# 2. Script returns filtered upstream tables
# 3. For each upstream table, use schema discovery priority order
```

## Summary

**Priority Order:**
1. 🥇 `/sql` directory - Fast, complete, token-efficient (always check first)
2. 🥈 Glean Dictionary - For `_live`/`_stable` tables, extract targeted fields
3. 🥉 DataHub - **Limited use only:**
   - Schema definitions when not available in `/sql` or Glean Dictionary
   - Field descriptions when missing (Glean Dictionary → DataHub)
   - Lineage/dependencies when can't infer from bqetl (telemetry sources, syndicated datasets)

**For schema generation:**
- **Check for missing descriptions first** - if > 50% missing, ask user if they want to add them
- If yes: Generate descriptions for ALL fields in source table (improves metadata completeness)
- Use source descriptions as base
- Improve descriptions with context
- Recommend updates to source schemas when existing descriptions are unclear

**For live/stable tables:**
- Search Glean Dictionary for field descriptions first
- If not in Glean Dictionary, use DataHub
- Extract only needed fields
- Don't read entire massive files

**For syndicated datasets:**
- Look for directories without query.sql/query.py/view.sql
- Check metadata.yaml for available information
- Use DataHub for schema and lineage (usually only option)
- These are often from dev teams' postgres databases

**For metadata completeness:**
- Proactively detect source tables with missing descriptions
- Notify user and ask if they want to generate descriptions
- Update source tables to benefit all downstream consumers
