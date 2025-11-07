# DAG Discovery Guide

## Finding the Appropriate DAG

When creating new table metadata, you need to identify the correct Airflow DAG. Here are strategies for DAG discovery:

## Methods

### 1. Search DataHub for Similar Tables

Use the DataHub MCP search to find similar tables in the same dataset:

```
mcp__datahub-cloud__search
```

Look at what DAG those tables use in their metadata.

### 2. Search dags.yaml

Search the `dags.yaml` file for keywords related to the dataset or product:

```bash
grep -i "keyword" dags.yaml
```

### 3. Check Dataset Patterns

Many datasets follow naming conventions that hint at the appropriate DAG.

## Common DAG Patterns

### Firefox Desktop Telemetry
- **DAG:** `bqetl_main_summary`
- **Datasets:** `telemetry_derived`, `firefox_desktop_derived`
- **Use for:** Desktop telemetry, main ping data, client summaries

### Mobile Products
- **DAG:** `bqetl_nondesktop`
- **Datasets:** `fenix_derived`, `firefox_ios_derived`, `focus_android_derived`
- **Use for:** Mobile app telemetry, Fenix, Focus, Firefox iOS

### Firefox Accounts
- **DAG:** `bqetl_accounts_derived`
- **Datasets:** `accounts_derived`, `accounts_db_derived`
- **Use for:** FxA data, authentication events, account metrics

### Search Metrics
- **DAG:** `bqetl_search`
- **Datasets:** `search_derived`, `search_terms_derived`
- **Use for:** Search interactions, search revenue, SAP data

### Subscription Platform
- **DAG:** `bqetl_subplat`
- **Datasets:** `subscription_platform_derived`, `stripe_derived`
- **Use for:** Subscription data, Stripe events, revenue

### Ads & Contextual Services
- **DAG:** `bqetl_ads`
- **Datasets:** `ads_derived`, `contextual_services_derived`
- **Use for:** Ad impressions, clicks, sponsored content

### Monitoring & Operations
- **DAG:** `bqetl_monitoring`
- **Datasets:** `monitoring_derived`, `operational_monitoring_derived`
- **Use for:** System health, query performance, operational metrics

### Activity Stream (New Tab)
- **DAG:** `bqetl_activity_stream`
- **Datasets:** `activity_stream_derived`
- **Use for:** New Tab interactions, Pocket recommendations

### Mozilla VPN
- **DAG:** `bqetl_mozilla_vpn`
- **Datasets:** `mozilla_vpn_derived`
- **Use for:** VPN usage, subscription data

### General ETL
- **DAG:** `bqetl_core`
- **Datasets:** Various
- **Use for:** Foundational tables, cross-product aggregations

## DAG Selection Checklist

When choosing a DAG, consider:

1. **Data source:** Where does the data originate?
2. **Product area:** Which product or service does this support?
3. **Update frequency:** Daily, hourly, weekly?
4. **Dependencies:** What other tables does this depend on?
5. **Team ownership:** Which team owns the upstream data?

## Validation

After selecting a DAG:

1. Check that the DAG exists in `dags.yaml`
2. Verify the schedule matches your requirements
3. Ensure the DAG runs in the appropriate environment
4. Confirm dependencies are compatible

## Getting Help

If unsure about DAG selection:
- Consult with the data engineering team
- Check similar tables in the same dataset
- Review the DAG documentation in `dags.yaml`

## When No Suitable DAG Exists

If you cannot find an appropriate existing DAG after following the discovery methods above, you may need to **create a new DAG**.

### Decision: Reuse vs Create

**Prefer reusing an existing DAG when:**
- The product area matches (e.g., Firefox Desktop, Mobile, FxA)
- The schedule is close enough (within an hour or two)
- The dependencies align with existing DAGs
- The team ownership overlaps

**Create a new DAG when:**
- **New product or service** - A new Mozilla product that doesn't fit existing categories
- **Different scheduling requirements** - Need hourly when only daily exists, or specific time requirements
- **Isolated dependencies** - Tables have unique upstream dependencies
- **Team ownership boundaries** - A team needs independent control over their pipeline
- **Different SLAs** - Tables require different reliability guarantees (impact tier)

### Creating a New DAG

**See `dag_creation_guide.md` for complete instructions on:**
- Full DAG creation workflow
- When to create vs reuse (detailed criteria)
- Configuration options (schedules, retries, impact tiers)
- Template selection (daily, hourly, custom)
- Best practices and examples

**Quick steps:**
1. Read `dag_creation_guide.md` for when to create vs reuse
2. Choose template: `assets/dag_template_daily.yaml`, `dag_template_hourly.yaml`, or `dag_template_custom.yaml`
3. Present options to the user (similar existing DAG vs new DAG)
4. If creating new:
   - Gather: DAG name, schedule, owner, start_date, impact tier
   - Add to **bottom** of `dags.yaml`
   - Validate with `./bqetl dag validate <dag_name>`
