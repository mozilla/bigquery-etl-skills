-- Template for bigeye_custom_rules.sql
-- Custom SQL validation rules for Bigeye monitoring
--
-- Each rule consists of:
-- 1. JSON configuration comment
-- 2. SQL query that returns validation result
--
-- For "value" alert_conditions: Query should return percentage (0-100)
-- For "count" alert_conditions: Query should return row count
--
-- Available Jinja variables:
--   {{ project_id }}  - Project ID (e.g., moz-fx-data-shared-prod)
--   {{ dataset_id }}  - Dataset name
--   {{ table_name }}  - Table name
-- Example 1: Percentage-based validation
-- Check that version field follows expected pattern
-- {
--   "name": "Version format validation",
--   "alert_conditions": "value",
--   "range": {
--     "min": 0,
--     "max": 1
--   },
--   "collections": ["Operational Checks"],
--   "owner": "your-email@mozilla.com",
--   "schedule": "Default Schedule - 13:00 UTC"
-- }
SELECT
  ROUND((COUNTIF(NOT REGEXP_CONTAINS(version, r"^[0-9]+\..+$"))) / COUNT(*) * 100, 2) AS perc
FROM
  `{{ project_id }}.{{ dataset_id }}.{{ table_name }}`;

-- Example 2: Count-based validation
-- Check for negative revenue values
-- {
--   "name": "Negative revenue check",
--   "alert_conditions": "count",
--   "range": {
--     "min": 0,
--     "max": 0
--   },
--   "collections": ["Operational Checks"],
--   "owner": "your-email@mozilla.com",
--   "schedule": "Default Schedule - 13:00 UTC"
-- }
SELECT
  COUNT(*) AS negative_revenue_count
FROM
  `{{ project_id }}.{{ dataset_id }}.{{ table_name }}`
WHERE
  revenue < 0;

-- Example 3: Cross-column validation
-- Check that start_date is before end_date
-- {
--   "name": "Date range validation",
--   "alert_conditions": "value",
--   "range": {
--     "min": 0,
--     "max": 1
--   },
--   "collections": ["Operational Checks"],
--   "owner": "your-email@mozilla.com",
--   "schedule": "Default Schedule - 13:00 UTC"
-- }
SELECT
  ROUND((COUNTIF(start_date > end_date)) / COUNT(*) * 100, 2) AS perc
FROM
  `{{ project_id }}.{{ dataset_id }}.{{ table_name }}`
WHERE
  start_date IS NOT NULL
  AND end_date IS NOT NULL;
