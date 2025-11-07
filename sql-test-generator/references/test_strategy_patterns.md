# Test Strategy Patterns

## Determining Number of Tests

### Simple Queries (1 test)
- Single SELECT with basic WHERE clause
- Simple aggregation (COUNT, SUM) with GROUP BY
- No complex joins or logic branches

**Example:** Basic daily aggregation of client metrics

### Moderate Complexity (1-2 tests)
- LEFT/INNER JOIN with filtering
- CASE statements with 2-3 branches
- Simple UDF usage

**Example:** Join clients with search data, filtering by country

### Complex Queries (3-5 tests)
- FULL OUTER JOIN (test both matched and unmatched sides)
- Complex CASE/IF logic with multiple branches
- Map operations (test empty, existing, new values)
- Incremental logic (test first run vs subsequent runs)
- Multiple CTEs with interdependencies

**Example:** Multi-source aggregation with map updates and full outer joins

### UNION/UNION ALL Queries (1 test per date/filter branch)
- Create ONE comprehensive test with fixtures for ALL sources
- Only create separate tests for different date ranges or filter conditions that change query behavior

## Test Scenarios by Query Pattern

### Date-Based Filtering

When queries have date thresholds that control which data sources contribute:

```sql
-- Example: Legacy data only included before cutoff
SELECT * FROM legacy_source
WHERE submission_date < '2024-12-01'

UNION ALL

SELECT * FROM modern_source
WHERE submission_date >= '2024-12-01'
```

**Test strategy:**
- `test_historical_data` with submission_date: "2024-11-15"
- `test_modern_data` with submission_date: "2024-12-15"

Each test includes fixtures for BOTH sources, but different dates activate different branches.

### Version-Based Filtering

When queries filter on application versions:

```sql
SELECT
  CASE
    WHEN version <= '120' THEN 'legacy'
    ELSE 'modern'
  END AS version_type
```

**Test strategy:**
- Use three-part versions ("120.0.0", "121.0.0") to avoid YAML float parsing
- Test both sides of version threshold

**Fixtures:**
```yaml
# Test legacy version
- version: "120.0.0"
  other_field: "value"

# Test modern version
- version: "121.0.0"
  other_field: "value"
```

### Join Patterns

#### LEFT JOIN
Test:
1. Rows that match (both sides have data)
2. Rows with no match (NULL on right side)

#### FULL OUTER JOIN
Test:
1. Rows that match (both sides have data)
2. Left-only rows (NULL on right side)
3. Right-only rows (NULL on left side)

#### INNER JOIN
Test:
1. Basic case with matches
2. Edge case: no matches returns empty result

**Example fixtures for FULL OUTER JOIN:**

```yaml
# left_table.yaml
- id: 1  # Matches
  left_field: "A"
- id: 2  # Left-only
  left_field: "B"

# right_table.yaml
- id: 1  # Matches
  right_field: "X"
- id: 3  # Right-only
  right_field: "Z"
```

### Aggregation Patterns

#### GROUP BY
Test:
1. Single row per group
2. Multiple rows per group
3. NULL values in grouping column (if relevant)

#### Window Functions
Test:
1. Single partition
2. Multiple partitions
3. Edge cases (first/last row in partition)

### UDF and Map Operations

#### mozfun.map.mode_last
Test:
1. Empty map (no updates)
2. Existing key update
3. New key addition
4. Multiple updates

**Example:**
```yaml
# Test existing key update
- client_id: "abc123"
  existing_map:
    - key: "setting1"
      value: "old_value"
  new_updates:
    - key: "setting1"
      value: "new_value"

# Expected: setting1 → "new_value"
```

### Incremental Queries

Incremental queries process new data and merge with historical state.

Test:
1. **First run** - no historical data exists
2. **Subsequent run** - merging with existing data
3. **Update existing records** - same key, different values

**Example structure:**
```
test_first_run/
  ├── new_data.yaml  # Today's data
  └── expect.yaml

test_update_existing/
  ├── historical_data.yaml  # Previous state
  ├── new_data.yaml  # Today's updates
  └── expect.yaml
```

### UNNEST Patterns (Legacy Telemetry)

Legacy telemetry often uses arrays that get unnested:

```sql
FROM table_name
CROSS JOIN UNNEST(tiles) AS flattened_tiles
WHERE flattened_tiles.click IS NOT NULL
```

Test:
1. Multiple items in array
2. Some items filtered out
3. NULL values in array elements

**Example fixture:**
```yaml
- document_id: "doc1"
  tiles:
    - id: 1001
      click: 1  # Included
      block: null
    - id: 1002
      click: null  # Filtered out
      block: null
```

### Glean Events with Extras

Test:
1. Single event per ping
2. Multiple events per ping
3. Events without extras
4. Events with multiple extra fields

**Example fixture:**
```yaml
- document_id: "doc1"
  events:
    - category: "pocket"
      name: "impression"
      extra:
        - key: "recommendation_id"
          value: "rec_001"
        - key: "tile_id"
          value: "2001"
    - category: "pocket"
      name: "click"
      extra:
        - key: "recommendation_id"
          value: "rec_001"
```

## Test Naming Conventions

Use descriptive snake_case that explains what scenario is being tested:

**Good names:**
- `test_new_clients_only`
- `test_full_outer_join_all_branches`
- `test_map_update_existing_key`
- `test_union_all_sources`
- `test_modern_date_after_cutoff`
- `test_historical_data_before_cutoff`
- `test_first_run_no_history`
- `test_update_existing_records`

**Bad names:**
- `test_1`, `test_2`
- `test_basic`
- `test_query`
- `test_data`

## Balancing Test Coverage vs Simplicity

**Prefer fewer comprehensive tests over many narrow tests:**
- ✅ 1 test with fixtures for all sources and multiple scenarios
- ❌ 5 tests each covering one specific scenario, missing fixtures

**Exception:** Create separate tests when:
- Different date ranges activate different query branches
- Version thresholds change query behavior
- Incremental logic requires testing first run vs updates

**Remember:** Every test must include fixtures for ALL source tables to avoid querying production.
