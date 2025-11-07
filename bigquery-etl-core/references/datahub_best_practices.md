# DataHub MCP Best Practices

## Token Optimization Strategy

DataHub queries can return large amounts of metadata. Follow these practices to minimize token usage while getting the schema information you need.

## Priority Order for Schema Discovery

**Always follow this priority order:**

1. **Local schema.yaml files** - Check `sql/*/schema.yaml` in bigquery-etl repo FIRST
2. **Glean Dictionary** - For `_live`/`_stable` tables, use https://dictionary.telemetry.mozilla.org/
3. **Local metadata.yaml files** - Check `sql/*/metadata.yaml` for additional table metadata
4. **BigQuery documentation** - Check https://mozilla.github.io/bigquery-etl/ dataset browser
5. **DataHub MCP** - **Limited use only:**
   - When schema files don't exist in `/sql` or Glean Dictionary
   - When schema files exist but fields lack descriptions (Glean Dictionary → DataHub hierarchy)
   - For lineage/dependencies when can't infer from bqetl (telemetry sources, syndicated datasets)

## When to Use DataHub (Construction Focus)

**DataHub is appropriate for table construction:**

1. **Downstream impact analysis (CRITICAL when modifying existing tables):**
   - Check what tables/dashboards/queries depend on a table you're modifying
   - Warn about schema changes that will affect downstream consumers
   - Use `get_lineage(upstream=False)` to find downstream dependencies

2. **Upstream validation (when user isn't completely sure):**
   - Validate that upstream tables exist
   - Confirm available columns for joins
   - Use after user provides table names, not for exploration

3. **Schema lookup as last resort:**
   - No schema.yaml file exists in `/sql` directory
   - Not available in Glean Dictionary
   - Syndicated datasets (directories without query.sql/query.py/view.sql)

4. **Field descriptions (follow this hierarchy):**
   - **FIRST:** Try Glean Dictionary for `_live`/`_stable` tables
   - **SECOND:** Use DataHub if not found in Glean Dictionary
   - Extract only essential description information

**Syndicated Datasets:**
Special cases where DataHub may be the only option:
- Directories without `query.sql`, `query.py`, or `view.sql` files
- Usually data from dev teams' postgres databases in their own GCP projects
- Won't have schema files in bqetl repository
- Check `metadata.yaml` files for any available information first
- Examples: External service integrations, third-party data syncs

**DO NOT use DataHub for:**
- ❌ Exploratory discovery of what data exists (out of scope)
- ❌ Finding alternative tables to use (user provides source tables)
- ❌ First attempt at schema lookup (check `/sql` and Glean Dictionary first)
- ❌ Description lookup without trying Glean Dictionary first (for `_live`/`_stable` tables)
- ❌ Batch queries for multiple tables without checking local files first

## Token-Efficient DataHub Query Patterns

### 1. Search Before Get Entity

Use `search` to find tables efficiently, then only call `get_entity` if you need full details:

```python
# GOOD: Search first to find table URNs
mcp__datahub-cloud__search(
  query="/q impression_stats",
  filters={
    "entity_type": ["dataset"],
    "platform": ["bigquery"]
  },
  num_results=5
)

# Then only get_entity for the specific table you need
mcp__datahub-cloud__get_entity(
  urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,moz-fx-data-shared-prod.activity_stream_live.impression_stats_v1,PROD)"
)
```

```python
# BAD: Getting entity without searching first
mcp__datahub-cloud__get_entity(urn="...")  # Returns everything
```

### 2. Extract Only Required Fields

When you receive DataHub responses, extract ONLY what you need:

**For SQL test generation:**
- Table name
- Column names
- Column types (STRING, INT64, TIMESTAMP, etc.)

**Ignore these to save tokens:**
- Column descriptions
- Tags
- Ownership information
- Glossary terms
- Custom properties (unless specifically needed)

### 3. Limit Search Results

Always specify `num_results` to avoid retrieving too many entities:

```python
# GOOD: Limit results
mcp__datahub-cloud__search(
  query="/q newtab",
  filters={"entity_type": ["dataset"]},
  num_results=5  # Only get top 5 matches
)

# BAD: Default might return 10+ results
mcp__datahub-cloud__search(
  query="/q newtab",
  filters={"entity_type": ["dataset"]}
)
```

### 4. Use Specific Search Queries

Use the `/q` prefix with specific terms to get precise matches:

```python
# GOOD: Specific search with + operator for multi-word terms
mcp__datahub-cloud__search(
  query="/q impression+stats",  # Requires both terms
  filters={"platform": ["bigquery"]}
)

# GOOD: Wildcard for version patterns
mcp__datahub-cloud__search(
  query="/q newtab_interactions_hourly*",  # Matches v1, v2, etc.
  filters={"entity_type": ["dataset"]}
)

# BAD: Too broad
mcp__datahub-cloud__search(
  query="/q interactions"  # Returns too many results
)
```

### 5. Constrain Lineage Queries

Lineage queries can return massive graphs. Always constrain them:

```python
# GOOD: Limited lineage with filters
mcp__datahub-cloud__get_lineage(
  urn="urn:li:dataset:...",
  column=None,  # Set to null for table-level lineage
  upstream=True,
  max_hops=1,  # Only immediate dependencies
  filters={"entity_type": ["dataset"]}  # Only datasets, not charts/dashboards
)

# BAD: Unconstrained lineage
mcp__datahub-cloud__get_lineage(
  urn="urn:li:dataset:...",
  column=None,
  upstream=True,
  max_hops=3  # Can return hundreds of entities
)
```

### 6. Batch Schema Lookups

If you need schemas for multiple tables, consider whether you really need all of them:

```python
# GOOD: Only query tables that are actually used in the query
tables_in_query = ["impression_stats_v1", "newtab_v1"]
for table in tables_in_query:
    # Query schema

# BAD: Querying schemas for all possible tables
for table in all_tables_in_database:  # Hundreds of tables
    # Query schema
```

## DataHub Query Decision Tree

```
Need schema information?
├─ Is this a bigquery-etl managed table?
│  ├─ YES → Check sql/*/schema.yaml FIRST
│  └─ NO → Continue
├─ Is this a _live or _stable table?
│  ├─ YES → Check Glean Dictionary FIRST
│  │  ├─ Found → Use Glean Dictionary descriptions
│  │  └─ Not found → Use DataHub
│  └─ NO → Continue
├─ Is this a syndicated dataset (no query.sql/query.py/view.sql)?
│  ├─ YES → Check metadata.yaml, then use DataHub
│  └─ NO → Continue
├─ Is this documented in Mozilla data docs?
│  ├─ YES → Check https://mozilla.github.io/bigquery-etl/
│  └─ NO → Continue
└─ Use DataHub MCP
   ├─ Search for table first (num_results=5)
   ├─ Get entity for specific table only (or use get_lineage with max_hops=0)
   └─ Extract only: table name, column names, column types
```

## Example: Efficient Schema Lookup for Test Generation

```python
# Step 1: Check local files first
# Look for sql/moz-fx-data-shared-prod/activity_stream_live/impression_stats_v1/metadata.yaml

# Step 2: If not found locally, use DataHub efficiently
search_result = mcp__datahub-cloud__search(
  query="/q impression+stats+v1",
  filters={
    "entity_type": ["dataset"],
    "platform": ["bigquery"]
  },
  num_results=3
)

# Step 3: Get entity only if needed
if search_result.total_count > 0:
    entity = mcp__datahub-cloud__get_entity(
      urn=search_result.results[0].urn
    )

    # Step 4: Extract ONLY what you need
    schema = {
        "table": entity.name,
        "columns": [
            {"name": col.name, "type": col.type}
            for col in entity.schema.fields
        ]
    }
    # Discard descriptions, tags, etc.
```

## Handling "Response Exceeds Maximum Tokens" Errors

If you encounter errors like "MCP tool response (50425 tokens) exceeds maximum allowed tokens (25000)", the entity you're querying is too large. Here's how to handle it:

### Problem: get_entity Returns Too Much Data

The `get_entity` tool returns ALL metadata for an entity, including:
- Complete schema with descriptions
- Lineage information
- Ownership and governance metadata
- Tags, glossary terms, domains
- Properties, documentation
- Usage statistics

For large tables (especially those with many columns or extensive metadata), this can easily exceed 25k-50k tokens.

### Solution: Use Targeted Query Alternatives

**Option 1: Use get_lineage for Schema Only**

Instead of `get_entity`, use `get_lineage` with strict filters to get just the columns:

```python
# INSTEAD OF: get_entity (returns 50k+ tokens)
# mcp__datahub-cloud__get_entity(urn="urn:li:dataset:...")

# USE: get_lineage with max_hops=0 (returns just the entity)
mcp__datahub-cloud__get_lineage(
  urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,moz-fx-data-shared-prod.table_name,PROD)",
  column=None,
  upstream=False,  # Don't fetch upstream
  max_hops=0,  # Only the entity itself, no lineage
  filters={"entity_type": ["dataset"]}
)
# This returns MUCH less data - just the core entity without full metadata
```

**Option 2: Use get_dataset_queries for Column-Specific Information**

If you need information about specific columns:

```python
# Get queries that use specific columns
mcp__datahub-cloud__get_dataset_queries(
  urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,moz-fx-data-shared-prod.table_name,PROD)",
  column="column_name",  # Specific column, or None for table-level
  count=5,  # Limit number of queries returned
  start=0
)
```

**Option 3: Progressive Refinement with Search Facets**

Use search facets to understand the entity without fetching it:

```python
# Search returns lightweight metadata + facets
search_result = mcp__datahub-cloud__search(
  query="/q table_name",
  filters={
    "entity_type": ["dataset"],
    "platform": ["bigquery"]
  },
  num_results=1
)
# Use search result metadata (table name, platform, URN)
# Avoid get_entity entirely if you only need basic info
```

**Option 4: Query Local Files Instead**

```bash
# Check if schema exists locally
Read(file_path="sql/moz-fx-data-shared-prod/dataset/table/schema.yaml")
Read(file_path="sql/moz-fx-data-shared-prod/dataset/table/metadata.yaml")
```

### Updated Decision Tree

```
Need schema information?
├─ Is this a bigquery-etl managed table?
│  ├─ YES → Read local schema.yaml/metadata.yaml (500-2k tokens)
│  └─ NO → Continue
├─ Do you need full metadata or just schema?
│  ├─ JUST SCHEMA → Use get_lineage(max_hops=0) (5-10k tokens)
│  └─ FULL METADATA → Continue to get_entity
└─ Use get_entity (but expect 25k-50k+ tokens)
   ├─ If it errors with "exceeds maximum tokens"
   │  ├─ Fall back to get_lineage(max_hops=0)
   │  └─ Or use get_dataset_queries for column info
```

## Common Mistakes to Avoid

1. **Don't query DataHub before checking local files**
2. **Don't use get_entity without filters/search first**
3. **Don't retrieve full entity metadata when you only need schema**
4. **Don't query lineage with max_hops > 1 unless necessary**
5. **Don't search without num_results limit**
6. **Don't use broad search terms without filters**
7. **Don't use get_entity on large tables - use get_lineage(max_hops=0) instead**
8. **Don't retry get_entity if it fails - switch to alternative methods**

## Token Usage Comparison

| Approach | Approximate Tokens | When to Use |
|----------|-------------------|-------------|
| Local schema.yaml | 500-2000 | Bigquery-etl managed tables |
| DataHub search only | 1000-3000 | Finding table URNs |
| DataHub get_lineage (max_hops=0) | 3000-8000 | Just need schema/columns |
| DataHub get_dataset_queries | 2000-5000 | Need column-specific info |
| DataHub get_entity (minimal extraction) | 3000-8000 | Small tables, need metadata |
| DataHub get_entity (full metadata) | 10000-50000+ | Large tables - **AVOID** |
| DataHub lineage (max_hops=1) | 5000-15000 | Direct dependencies only |
| DataHub lineage (max_hops=2+) | 20000-100000+ | Avoid unless critical |

## Summary

**Golden Rule**: Prefer local files → Glean Dictionary → DataHub (last resort/validation)

**Construction-Focused Usage:**
1. **Downstream impact (CRITICAL):** Check dependencies when modifying existing tables
2. **Upstream validation:** Confirm tables exist when user isn't completely sure
3. **Schema lookup:** Last resort when not in `/sql` or Glean Dictionary

**Priority for schema lookup:**
1. Check `sql/*/schema.yaml` first (bigquery-etl managed tables)
2. Check Glean Dictionary for `_live`/`_stable` tables (https://dictionary.telemetry.mozilla.org/)
3. Check `metadata.yaml` for syndicated datasets
4. Use DataHub only when schema unavailable elsewhere

**When using DataHub:**
- **For downstream impact:** Use `get_lineage(upstream=False)` when modifying tables
- **For upstream validation:** Confirm tables exist after user provides them
- **For schema:** When not available in `/sql` or Glean Dictionary
- **For descriptions:** Glean Dictionary first, then DataHub
- Always search first, then get specific entities
- Extract only essential fields

**When you hit token limits:**
1. NEVER retry `get_entity` - it will fail again
2. Use `get_lineage(urn=..., column=None, upstream=False, max_hops=0)` instead
3. Or check if schema exists locally in schema.yaml/metadata.yaml
4. Or check Glean Dictionary for `_live`/`_stable` tables
5. Or use `get_dataset_queries` for specific column information

**For syndicated datasets:**
- Look for directories without query.sql/query.py/view.sql
- Check metadata.yaml first for available information
- DataHub may be the only option for schema and lineage

By following these practices, you can reduce DataHub token usage by 70-90% while still getting the schema information needed for SQL development and testing.
