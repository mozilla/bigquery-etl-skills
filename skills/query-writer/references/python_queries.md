# Python Query Files (query.py)

## When to Use Python vs SQL

**Use query.sql for:**
- Standard data transformations (95% of tables)
- Aggregations and GROUP BY operations
- Joins between tables in the same project
- CTEs and window functions
- Standard BigQuery operations

**Use query.py for:**
- API calls to external services
- Complex data transformations using pandas/Python libraries
- Multi-project queries or INFORMATION_SCHEMA operations
- Custom business logic clearer in Python than SQL

## Standard Structure

See `assets/python_query_template.py` for complete template.

## Common Python Patterns

**Multi-project queries:**
- Loop through projects with `WRITE_APPEND` to combine results
- See: `sql/moz-fx-data-shared-prod/monitoring_derived/bigquery_table_storage_v1/query.py`

**External API integration:**
- Use `requests` to fetch data, `pandas` to transform
- Load with `client.load_table_from_dataframe()`
- See: `sql/moz-fx-data-shared-prod/bigeye_derived/user_service_v1/query.py`

## Python Best Practices

- Always include docstrings
- Use ArgumentParser for configuration
- Use `WRITE_TRUNCATE` for full refresh
- Use `WRITE_APPEND` for incremental loads
- Handle errors with try/except
- Use logging for operations
- Clean up old tables: `client.delete_table(table, not_found_ok=True)`
