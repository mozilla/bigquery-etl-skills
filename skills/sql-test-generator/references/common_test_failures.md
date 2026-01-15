# Common Test Failures and How to Fix Them

This document captures real-world test failures and their solutions, learned from actual test development.

## Quick Reference: Most Common Failures

1. **Timestamp format mismatches** → Use ISO format with timezone: `2025-06-01T10:00:00+00:00` (see section 3)
2. **Ordering mismatches** → Run test, copy "Actual:" output order to expect.yaml (see section 2)
3. **NULL fields in expect.yaml** → Remove NULL fields entirely from expect.yaml (see section 1)
4. **Missing "Initialized" messages** → Add fixture files for all source tables (see preventing_production_queries.md)
5. **Non-deterministic results** → Make ORDER BY fields unique or copy actual order (see section 2)

## 1. NULL Fields in expect.yaml

### ❌ Problem
```yaml
# expect.yaml - WRONG
- submission_date: "2025-01-15"
  country_code: "US"
  avg_sidebar_time_seconds: null  # This will cause test failure!
  engagement_rate: 0.5
```

**Error:** Test fails because BigQuery completely omits NULL fields from query results. The expected output includes a NULL field that doesn't appear in actual results.

### ✅ Solution
**Completely omit NULL fields from expect.yaml:**
```yaml
# expect.yaml - CORRECT
- submission_date: "2025-01-15"
  country_code: "US"
  # avg_sidebar_time_seconds omitted entirely - no NULL value
  engagement_rate: 0.5
```

**Rule:** If a field will be NULL in the results, **do not include it at all** in expect.yaml.

## 2. Non-Deterministic ORDER BY and Result Ordering

### ❌ Problem: Row-Level Ordering
Query has:
```sql
ORDER BY submission_date DESC, total_users DESC
```

But test data has all rows with same `submission_date` and `total_users`:
```yaml
- submission_date: "2025-01-15"
  total_users: 1
  shopping_site: "amazon"

- submission_date: "2025-01-15"
  total_users: 1
  shopping_site: "walmart"
```

**Error:** Test fails because row order is non-deterministic when ORDER BY fields have duplicate values.

### ❌ Problem: Nested Field Ordering (Maps, Arrays)
Query returns map or array fields that may have non-deterministic ordering:
```yaml
# expect.yaml - order might not match actual results
- client_id: "client_existing_1"
  ad_click_history:
    - key: "2025-01-10"
      value: 2
    - key: "2025-01-15"
      value: 7
    - key: "2025-01-14"
      value: 5
```

**Error:** Test fails because:
1. The row order (which client appears first) may differ from expected
2. The order of keys within `ad_click_history` map may differ from expected

### ✅ Solutions

**Option 1: Create test data with different ORDER BY values**
```yaml
# Make total_users different to ensure deterministic ordering
- submission_date: "2025-01-15"
  total_users: 5  # Highest - appears first
  shopping_site: "amazon"

- submission_date: "2025-01-15"
  total_users: 3  # Middle
  shopping_site: "walmart"

- submission_date: "2025-01-15"
  total_users: 1  # Lowest - appears last
  shopping_site: "bestbuy"
```

**Option 2: Run test and copy actual output order to expect.yaml** ⭐ RECOMMENDED FOR ORDERING ISSUES

When you encounter test failures with ordering differences, this is the fastest solution:

1. Run the test once to see the actual output:
```bash
pytest tests/sql/.../test_name/ -v
```

2. Look at the "Actual:" section in pytest output
3. Copy the EXACT order shown in "Actual:" to your expect.yaml

**Important for nested fields (maps, arrays):**
- Copy the exact row order (e.g., `client_existing_2` before `client_existing_1`)
- Copy the exact key order within maps (e.g., newer dates may appear before older dates)
- Match both the top-level row ordering AND the nested field ordering

Example fix:
```yaml
# Before (failed test) - wrong ordering
- client_id: "client_existing_1"  # Wrong: appears first
  ad_click_history:
    - key: "2025-01-10"  # Wrong: old date first
      value: 2
    - key: "2025-01-15"  # Wrong: new date last
      value: 7

# After (from Actual output) - correct ordering
- client_id: "client_existing_2"  # Correct: this client appears first
  ad_click_history:
    - key: "2025-01-15"  # Correct: new date appears first
      value: 4
    - key: "2025-01-12"
      value: 1
- client_id: "client_existing_1"
  ad_click_history:
    - key: "2025-01-15"  # Correct: new date first
      value: 7
    - key: "2025-01-10"  # Correct: old date last
      value: 2
```

**Option 3: Suggest adding more ORDER BY fields** (if modifying query is acceptable)
```sql
ORDER BY
  submission_date DESC,
  total_users DESC,
  shopping_site ASC  -- Add tiebreaker for deterministic results
```

### Common Scenarios with Ordering Issues

1. **Queries without explicit ORDER BY**: Results may come back in any order
2. **Map operations** (like `mozfun.map.set_key`): Keys within maps may have specific ordering
3. **FULL OUTER JOIN**: Left vs right side may appear in unexpected order
4. **GROUP BY without ORDER BY**: Groups may appear in any order

**Best Practice:** Always run the test at least once and adjust expect.yaml to match the actual output order.

## 3. TIMESTAMP Format Mismatches ⚠️ VERY COMMON

### ❌ Problem

BigQuery returns TIMESTAMP and DATETIME fields in ISO 8601 format with timezone information:

```yaml
# What BigQuery actually returns
campaign_created_at: "2025-06-01T10:00:00+00:00"
campaign_updated_at: "2025-07-01T12:00:00+00:00"
```

But you might create expect.yaml with a different format:

```yaml
# expect.yaml - WRONG FORMAT
- campaign_created_at: "2025-06-01 10:00:00"  # Missing 'T' and timezone
  campaign_updated_at: "2025-07-01 12:00:00"
```

**Error message:** Test fails with timestamp format mismatch:
```
'campaign_created_at': '2025-06-01T10:00:00+00:00' != '2025-06-01 10:00:00'
                                  ^        ++++++
```

### ✅ Solution

**Always use ISO 8601 format with timezone in expect.yaml:**

```yaml
# expect.yaml - CORRECT FORMAT
- campaign_created_at: "2025-06-01T10:00:00+00:00"
  campaign_updated_at: "2025-07-01T12:00:00+00:00"
```

### Format Rules

**TIMESTAMP fields:**
- ✅ Use: `2025-06-01T10:00:00+00:00` (ISO 8601 with timezone)
- ❌ Don't use: `2025-06-01 10:00:00` (missing T and timezone)

**DATE fields:**
- ✅ Use: `2025-06-01` (YYYY-MM-DD format)
- ❌ Don't use: `06/01/2025` or other formats

**Microseconds (if present):**
- ✅ Use: `2025-06-01T10:00:00.123456+00:00` (with microseconds)

### Quick Fix When Tests Fail

When you see timestamp format errors:

1. **Run the test** to see actual output:
   ```bash
   pytest tests/sql/.../test_name/ -vv
   ```

2. **Copy the exact timestamp format** from the "Actual:" section in pytest output

3. **Update expect.yaml** with the ISO 8601 format

Example fix:
```diff
# Before (failed)
- campaign_created_at: "2025-06-01 10:00:00"
+ campaign_created_at: "2025-06-01T10:00:00+00:00"
```

### Input Fixtures vs expect.yaml

**Input fixtures** (YAML sources) can use either format - BigQuery will parse both:
```yaml
# Input fixture - both formats work
- campaign_created_at: "2025-06-01 10:00:00"  # This is fine for input
```

**expect.yaml** must match BigQuery's output format (ISO 8601):
```yaml
# expect.yaml - must use ISO 8601
- campaign_created_at: "2025-06-01T10:00:00+00:00"
```

**Best practice:** Use ISO 8601 format everywhere to avoid confusion.

## 4. Timestamp Calculations in Events

**Note:** For timestamp FORMAT issues, see section 3. This section covers timestamp CALCULATIONS.

### Pattern: Calculating Time Between Events

When calculating duration between events (e.g., time sidebar was open):

```sql
-- Time between surface_displayed and surface_closed
TIMESTAMP_DIFF(
  MAX(CASE WHEN name = 'surface_closed' THEN submission_timestamp END),
  MIN(CASE WHEN name = 'surface_displayed' THEN submission_timestamp END),
  SECOND
)
```

### Test Fixture Example

Use clear, calculable timestamp differences:

```yaml
- submission_timestamp: "2025-01-15T10:00:00+00:00"  # Base time (ISO 8601 format)
  events:
    - category: "shopping"
      name: "surface_displayed"
      timestamp: 1000000  # Event started
    - category: "shopping"
      name: "surface_closed"
      timestamp: 1030000  # 30 seconds later
```

**Expected result:** `avg_sidebar_time_seconds: 30.0`

### Common Mistakes

❌ **Using event timestamps instead of submission_timestamp:**
```sql
-- WRONG - event timestamp is microseconds since ping start, not absolute time
TIMESTAMP_DIFF(events.timestamp, events.timestamp, SECOND)
```

✅ **Using submission_timestamp with CASE logic:**
```sql
-- CORRECT - use submission_timestamp from different event rows
TIMESTAMP_DIFF(
  MAX(CASE WHEN name = 'end_event' THEN submission_timestamp END),
  MIN(CASE WHEN name = 'start_event' THEN submission_timestamp END),
  SECOND
)
```

## 4. Glean Events Extra Field Handling

### Pattern: Extracting Extra Fields

```sql
-- Extract shopping_site from event extras
ARRAY_AGG(
  mozfun.map.get_key(extra, 'shopping_site')
  IGNORE NULLS
  ORDER BY submission_timestamp
)[SAFE_OFFSET(0)] AS shopping_site
```

### Test Fixture with Extra Fields

```yaml
- submission_timestamp: "2025-01-15T10:00:00+00:00"  # ISO 8601 format
  client_info:
    client_id: "client_001"
  events:
    - category: "shopping"
      name: "address_bar_icon_displayed"
      extra:
        - key: "shopping_site"
          value: "amazon"
        - key: "another_field"
          value: "some_value"
```

### Handling Missing Extra Fields

When `extra` is empty or key doesn't exist, `mozfun.map.get_key` returns NULL:

```yaml
# Event without extras - results in NULL for extracted fields
- submission_timestamp: "2025-01-15T10:00:00+00:00"
  events:
    - category: "shopping"
      name: "some_event"
      extra: []  # Empty extras
```

**In expect.yaml:** Either handle with COALESCE in query or omit the NULL field.

## 6. Test Ordering Best Practices

### When Creating Test Data

1. **Match the query's ORDER BY** - Structure test data so expected order is obvious
2. **Use different values for ORDER BY fields** - Ensures deterministic results
3. **Document the expected order** - Add comments explaining why rows are in that order

### Example with Good Ordering

```yaml
# expect.yaml
# Ordered by: submission_date DESC, total_users DESC, country_code ASC

# Most recent date, highest users
- submission_date: "2025-01-16"
  total_users: 100
  country_code: "CA"

# Same date and users, ordered by country_code
- submission_date: "2025-01-16"
  total_users: 100
  country_code: "US"

# Older date
- submission_date: "2025-01-15"
  total_users: 50
  country_code: "UK"
```

## 7. Aggregation Edge Cases

### Problem: Aggregations with No Matching Rows

If test data gets filtered out entirely, aggregations may behave unexpectedly:

```sql
SELECT
  COUNT(DISTINCT client_id) AS total_users,
  AVG(metric) AS avg_metric
FROM table
WHERE date = '2025-01-15'
  AND metric > 100  -- Filters out all test rows!
```

### Solution: Ensure Test Data Passes Filters

```yaml
# Input fixture - make sure data passes WHERE clauses
- submission_date: "2025-01-15"
  metric: 150  # Greater than 100 - passes filter
  client_id: "client_001"
```

## 8. SAFE_DIVIDE and Division by Zero

### Pattern in Query

```sql
SAFE_DIVIDE(
  COUNT(DISTINCT CASE WHEN opened = 1 THEN client_id END),
  NULLIF(COUNT(DISTINCT CASE WHEN saw_icon = 1 THEN client_id END), 0)
) AS engagement_rate
```

### Test Cases Needed

1. **Normal case** - denominator > 0
2. **Division by zero case** - denominator = 0, results in NULL

```yaml
# Test case 1: Normal division
- saw_icon: 1
  opened: 1
  # Expected engagement_rate: 1.0

# Test case 2: Division by zero
- saw_icon: 0
  opened: 1
  # Expected engagement_rate: null (or omit from expect.yaml)
```

## Summary Checklist

Before finalizing expect.yaml:

- [ ] **TIMESTAMPS use ISO 8601 format:** `2025-06-01T10:00:00+00:00` (section 3)
- [ ] NULL fields are completely omitted (not set to `null`) (section 1)
- [ ] Row order matches query's ORDER BY or test has been run to verify order (section 2)
- [ ] Test data has different values for ORDER BY fields when possible (section 2)
- [ ] All WHERE clause filters pass with test data (section 7)
- [ ] Division by zero cases are handled correctly (section 8)
- [ ] Glean event extras are structured correctly (section 5)
- [ ] Timestamp calculations use realistic, calculable differences (section 4)
