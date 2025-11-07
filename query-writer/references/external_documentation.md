# External Documentation Links

## Official Documentation

- Creating derived datasets: https://mozilla.github.io/bigquery-etl/cookbooks/creating_a_derived_dataset/
- Recommended practices: https://mozilla.github.io/bigquery-etl/reference/recommended_practices/
- Query optimization: https://docs.telemetry.mozilla.org/cookbooks/bigquery/optimization.html
- Common workflows: https://mozilla.github.io/bigquery-etl/cookbooks/common_workflows/
- Scheduling reference: https://mozilla.github.io/bigquery-etl/reference/scheduling/

## Reference Examples in Repository

**Simple query:**
- `sql/moz-fx-data-shared-prod/mozilla_vpn_derived/users_v1/query.sql`

**Aggregation with GROUP BY:**
- `sql/moz-fx-data-shared-prod/telemetry_derived/clients_daily_event_v1/query.sql`

**Complex with CTEs:**
- `sql/moz-fx-data-shared-prod/telemetry_derived/event_events_v1/query.sql`

**Python INFORMATION_SCHEMA:**
- `sql/moz-fx-data-shared-prod/monitoring_derived/bigquery_table_storage_v1/query.py`

**Python External API:**
- `sql/moz-fx-data-shared-prod/bigeye_derived/user_service_v1/query.py`

**Hourly queries:**
- `sql/moz-fx-data-shared-prod/telemetry_derived/newtab_interactions_hourly_v1/`
