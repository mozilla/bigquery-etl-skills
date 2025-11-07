# YAML Format Guide for SQL Tests

## Correct Array Syntax

All fixture files must use array syntax with dashes:

```yaml
# Correct - array syntax
- field1: value1
  field2: value2
- field1: value3
  field2: value4
```

```yaml
# Wrong - document separators (will error)
---
field1: value1
---
field1: value2
```

## Type Inference Pitfalls

### Version Numbers

YAML auto-parses certain number formats, which can cause type mismatches:

```yaml
# ✅ Good - three-part version prevents float parsing
version: "120.0.0"

# ✅ Good - simple integer string
version: "120"

# ❌ Bad - parsed as FLOAT64 instead of STRING
version: "120.0"

# ❌ Bad - unquoted string
version: v120
```

**Problem:** When a query uses `SPLIT(version, '.')`, BigQuery expects a STRING type. If YAML parses "120.0" as a float, the query will fail with a type mismatch error.

**Solution:** Always use three-part versions ("120.0.0") or simple integers ("120") for version fields.

### Dates and Timestamps

```yaml
# ✅ Good - quoted date strings
submission_date: "2025-01-01"
submission_timestamp: "2024-12-15 14:30:00"

# ❌ Bad - unquoted may be parsed as something else
submission_date: 2025-01-01
```

### NULL Values

```yaml
# ✅ Good - explicit null keyword
loaded: null
block: null

# Include NULL fields in input fixtures
- client_id: "abc123"
  loaded: null  # Include even if null

# Omit NULL fields from expect.yaml
- client_id: "abc123"
  # loaded field omitted because it's null
```

## Empty Arrays - Critical Warning

**Never create empty array fixtures:**

```yaml
# ❌ Wrong - causes "Schema has no fields" error
[]
```

**Why this is a problem:**
- BigQuery needs at least one row to infer the schema
- Empty arrays provide no schema information
- Tests will fail with schema errors

**Solution:**
Always include at least one row of data:

```yaml
# ✅ Right - at least one row with all fields
- submission_timestamp: "2024-12-15 10:00:00"
  document_id: "doc1"
  field1: "value1"
  field2: null
```

If you want a source to contribute no data to the test results, use WHERE clause filtering instead:

```yaml
# Create data that gets filtered out by the query
- submission_timestamp: "2024-12-15 10:00:00"
  document_id: "filtered_out"
  loaded: 1  # Query has WHERE loaded IS NULL, so this row is excluded
```

## Nested Structures

### Glean Client Info

```yaml
client_info:
  client_id: "client_123"
  app_display_version: "121.0.0"
  os: "Android"
```

### Glean Events with Extras

```yaml
events:
  - category: "pocket"
    name: "impression"
    extra:
      - key: "recommendation_id"
        value: "rec_001"
      - key: "tile_id"
        value: "2001"
```

**Note:** The `extra` field is an array of key-value pairs, not a map.

### Legacy Telemetry Arrays (for CROSS JOIN UNNEST)

```yaml
tiles:
  - id: 1001
    pos: 0
    click: 1
    block: null
  - id: 1002
    pos: 1
    click: null
    block: null
```

## Common Mistakes

1. **Using document separators (`---`)**: Not supported in fixture files
2. **Empty arrays (`[]`)**: Causes schema errors
3. **Two-part version numbers**: Parsed as floats, causes type errors
4. **Unquoted dates**: May be parsed incorrectly
5. **Omitting required fields**: Include all fields the query references, even if NULL
