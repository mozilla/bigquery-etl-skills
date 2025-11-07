# Schema & Description Resources for Construction

This reference provides guidance on finding schema descriptions when building and modifying BigQuery tables.

## Priority Order for Schema Lookup

When constructing queries and schemas, follow this priority order:

### 1. Local Files (ALWAYS CHECK FIRST)

**schema.yaml and metadata.yaml files:**
- Location: `sql/{project}/{dataset}/{table_name}/`
- Most reliable and up-to-date source
- Contains field descriptions written by table owners
- Already validated and deployed

**How to search:**
```bash
# Find schema for a specific table
find sql -name "schema.yaml" -path "*{dataset}/{table}*"

# Search for field descriptions
grep -r "field_name" sql/*/schema.yaml
```

### 2. Glean Dictionary (For _live and _stable tables)

**URL Pattern:**
```
https://dictionary.telemetry.mozilla.org/apps/{app_id}/tables/{table_name}
```

**Examples:**
- firefox_desktop_live.events_v1 → https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
- org_mozilla_fenix_stable.metrics_v1 → https://dictionary.telemetry.mozilla.org/apps/fenix/tables/metrics

**Use WebFetch with targeted prompts:**
```
URL: https://dictionary.telemetry.mozilla.org/apps/firefox_desktop/tables/events
Prompt: "Extract the name, type, mode, and description for these fields: event.name, event.category"
```

**Contains:**
- Metric descriptions from Glean schema definitions
- Field types and structures
- Example values

### 3. ProbeInfo API (For Glean Metric Metadata)

**Endpoints:**
- Metrics: `https://probeinfo.telemetry.mozilla.org/glean/{product}/metrics`
- Pings: `https://probeinfo.telemetry.mozilla.org/glean/{product}/pings`

**Product names (use kebab-case):**
- `firefox-desktop`, `firefox-ios`, `firefox-android`, `fenix`, `focus-android`, `focus-ios`

**Use for:**
- Validating metric references in queries
- Getting programmatic access to metric definitions
- Understanding metric types and structures

### 4. DataHub MCP (LAST RESORT)

**CRITICAL:** **READ `datahub_best_practices.md` BEFORE any DataHub queries**

**Use DataHub for:**
- Schema lookup when NOT available in local files or Glean Dictionary
- Downstream impact analysis when modifying tables
- Upstream validation when user provides table names

**Pattern:**
```
# Search for table
mcp__datahub-cloud__search: query="/q table_name", filters={"platform": ["bigquery"]}

# Get schema with minimal tokens
mcp__datahub-cloud__get_lineage: urn="...", column=null, max_hops=0
# Extract ONLY column names, types, descriptions
```

**Key principles:**
- Extract ONLY necessary fields (names, types, descriptions)
- Avoid `get_entity` (returns 50K+ tokens)
- Use `get_lineage` with `max_hops=0` instead

## Product Naming Across Systems

Mozilla products use different naming conventions:

| System | Format | Example |
|--------|--------|---------|
| ProbeInfo API | kebab-case | `firefox-desktop`, `firefox-ios` |
| Glean Dictionary URLs | snake_case | `firefox_desktop`, `firefox_ios` |
| BigQuery datasets | snake_case | `firefox_desktop`, `fenix`, `org_mozilla_firefox` |

## Common UDFs (mozfun)

**Browse available functions:** https://mozilla.github.io/bigquery-etl/mozfun/

**Commonly used:**
- `mozfun.map.get_key()` - Extract values from key-value maps
- `mozfun.norm.truncate_version()` - Normalize version strings
- `mozfun.stats.mode_last()` - Statistical mode calculation
- `mozfun.hist.extract()` - Extract histogram values

**UDF source code:** `sql/mozfun/` directory

## Documentation Resources

Key documentation for construction:

**BigQuery ETL docs:** https://mozilla.github.io/bigquery-etl/
- Dataset browser
- Derived table documentation
- Configuration references

**Mozilla Data Docs:** https://docs.telemetry.mozilla.org/
- Comprehensive data platform documentation
- BigQuery cookbooks
- Data collection references

**Specific guides:**
- **Creating derived datasets**: https://mozilla.github.io/bigquery-etl/cookbooks/creating_a_derived_dataset/
- **Recommended practices**: https://mozilla.github.io/bigquery-etl/reference/recommended_practices/
- **Incremental queries**: https://mozilla.github.io/bigquery-etl/reference/incremental/
- **Testing**: https://mozilla.github.io/bigquery-etl/cookbooks/testing/
- **BigQuery optimization**: https://docs.telemetry.mozilla.org/cookbooks/bigquery/optimization.html

## Summary: Schema Description Priority

1. **Local files** - `sql/*/schema.yaml` (ALWAYS CHECK FIRST)
2. **Glean Dictionary** - For `_live` and `_stable` tables
3. **ProbeInfo API** - For programmatic metric metadata
4. **DataHub MCP** - Last resort, follow best practices

This order optimizes for:
- ✅ Reliability (local files are source of truth)
- ✅ Token efficiency (avoid large API responses)
- ✅ Construction focus (descriptions for building, not exploring)
