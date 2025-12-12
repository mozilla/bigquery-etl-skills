# bigquery-etl CLI Commands

## Key bqetl CLI Commands

- `./bqetl query create <dataset>.<table> --dag <dag_name>` - Create new query.sql file with templates
- `./bqetl query validate <dataset>.<table>` - Validate query syntax
- `./bqetl query schema update <dataset>.<table>` - Generate schema.yaml from query.sql
- `./bqetl query schema deploy <dataset>.<table>` - Deploy schema to BigQuery
- `./bqetl dag create <dag_name>` - Create new Airflow DAG
- `./bqetl backfill create <dataset>.<table> --start_date=<date> --end_date=<date>` - Create backfill

## Finding the Right DAG

- DAGs are defined in `dags.yaml` (2500+ lines)
- Search DataHub for similar tables to see what DAG they use: `mcp__datahub-cloud__search`
- Or search `dags.yaml` with Grep for keywords related to the dataset/product
- See metadata-manager skill for common DAG patterns
