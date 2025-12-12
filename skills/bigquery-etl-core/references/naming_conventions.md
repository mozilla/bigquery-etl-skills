# Naming Conventions

## Table Names

- Use snake_case: `clients_daily_event_v1`
- Include version suffix: `_v1`, `_v2`, etc.
- Descriptive names indicating content and granularity
- Common suffixes: `_daily`, `_hourly`, `_aggregates`, `_summary`

## Field Names

- Use snake_case: `submission_date`, `client_id`, `n_total_events`
- Prefix counts with `n_`: `n_events`, `n_sessions`

### Common Mozilla Field Names

- `submission_date` - Date of data submission (partition field)
- `client_id` - Unique client identifier
- `sample_id` - Sample identifier (0-99)
- `normalized_channel` - Release channel (release, beta, nightly)
- `normalized_country_code` or `country` - Country code
- `app_version` - Application version

## Reserved/Common Patterns

- Avoid `date` alone (use `submission_date`, `event_date`, etc.)
- `_derived` suffix for datasets, not individual tables
- `_external` for datasets with externally synced data
- UDF naming: `mozfun.category.function_name` (e.g., `mozfun.map.get_key`)

## Project Names

- **Production**: `moz-fx-data-shared-prod` (primary data warehouse)
- **Other environments**: `moz-fx-{product}-{environment}` (e.g., `moz-fx-cjms-nonprod-9a36`, `moz-fx-data-marketing-prod`)
- **Functions library**: `mozfun` (UDFs accessible across projects)
