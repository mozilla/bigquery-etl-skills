# DAG Creation Guide

## When to Create a New DAG

Before creating a new DAG, **always check if an existing DAG can be used**. Use the DAG discovery methods in `dag_discovery.md` first.

Create a new DAG when:
1. **New product or service** - A new Mozilla product needs its own data pipeline
2. **Different scheduling requirements** - Existing DAGs don't match the required schedule
3. **Isolated dependencies** - Tables have unique dependencies that don't fit existing DAGs
4. **Team ownership boundaries** - A team needs independent control over their pipeline
5. **Different SLAs or impact tiers** - Tables require different reliability guarantees

**DO NOT create a new DAG if:**
- An existing DAG covers the same product area
- The schedule can be accommodated with existing DAGs
- Tables can be logically grouped with existing pipelines

## DAG Creation Workflow

### Step 1: Determine DAG Requirements

Answer these questions before creating a DAG:

**Scheduling:**
- What schedule is needed? (daily, hourly, custom cron)
- What time should it run? (consider dependencies and data availability)
- Does it need catchup enabled?

**Ownership:**
- Who owns this DAG? (email address)
- Who should be notified on failures? (email list)
- What team is responsible?

**Configuration:**
- What start date? (when should historical processing begin)
- How many retries on failure? (typically 1-2)
- What retry delay? (typically 5m-30m)
- What impact tier? (tier_1 for critical, tier_2 for important, tier_3 for nice-to-have)

**Naming:**
- Follow pattern: `bqetl_<product>` or `bqetl_<product>_<schedule>` if multiple schedules
- Examples: `bqetl_pocket`, `bqetl_ads_hourly`, `bqetl_vpn_derived`

### Step 2: Choose a Template

Based on scheduling requirements:

**Daily DAG (most common):**
- Schedule: `0 2 * * *` (2 AM UTC daily)
- Use for: Daily aggregations, once-per-day processing
- Template: `dag_template_daily.yaml`

**Hourly DAG:**
- Schedule: `30 * * * *` (30 minutes past each hour)
- Use for: Near real-time processing, frequent updates
- Template: `dag_template_hourly.yaml`

**Custom Schedule:**
- Define cron or interval pattern
- Use for: Weekly, multi-hour, or specific time requirements
- Template: `dag_template_custom.yaml`

### Step 3: Add DAG to dags.yaml

**Location:** Add new DAG entry at the **bottom** of `dags.yaml` file

**Required fields:**
```yaml
bqetl_<dag_name>:
  schedule_interval: 0 2 * * *  # or '3h' for intervals
  description: |
    Brief description of what this DAG does.
    Include data sources, purpose, and any important notes.
  default_args:
    owner: your_email@mozilla.com
    start_date: "YYYY-MM-DD"
    email: ["telemetry-alerts@mozilla.com", "your_email@mozilla.com"]
    retries: 1
    retry_delay: 10m
  tags:
    - impact/tier_2  # or tier_1, tier_3
```

**Optional fields:**
```yaml
  catchup: true  # Enable backfilling (default: false)
  depends_on_past: false  # Require previous run success (default: varies)
```

### Step 4: Present Options to User

When a new DAG is needed, present these options to the user:

**Option 1: Use similar existing DAG (if close match)**
- List DAGs with similar characteristics
- Explain trade-offs

**Option 2: Create new DAG**
- Present template with inferred values (based on dataset, product area, etc.)
- Ask user to confirm/modify:
  - Schedule
  - Owner
  - Start date
  - Impact tier

**Option 3: User specifies exact DAG configuration**
- If user has specific requirements, use their specification

### Step 5: Validate DAG Configuration

After adding to dags.yaml:

```bash
./bqetl dag validate <dag_name>
```

This checks:
- YAML syntax
- Required fields present
- Schedule format valid
- No naming conflicts

### Step 6: Test DAG Creation

Create a test query using the new DAG:

```bash
./bqetl query create <dataset>.<table> --dag <dag_name>
```

Verify that metadata generation works correctly.

## DAG Configuration Reference

### Schedule Interval Formats

**Cron format:**
- `0 2 * * *` - Daily at 2 AM UTC
- `30 * * * *` - Every hour at 30 minutes past
- `0 */3 * * *` - Every 3 hours at the top of the hour
- `0 0 * * 0` - Weekly on Sunday at midnight

**Interval format:**
- `3h` - Every 3 hours
- `30m` - Every 30 minutes
- `1d` - Every day

### Impact Tiers

**impact/tier_1** (Critical)
- Used by: Key dashboards, executive reports, critical business metrics
- SLA: High priority for fixes
- Examples: Main user metrics, revenue data, core product KPIs

**impact/tier_2** (Important)
- Used by: Regular reporting, team dashboards, important analytics
- SLA: Standard priority
- Examples: Product feature metrics, team-specific reports

**impact/tier_3** (Nice-to-have)
- Used by: Exploratory analysis, experimental tables, low-priority reports
- SLA: Best effort
- Examples: Prototypes, deprecated tables being phased out

### Retry Configuration

**For stable data sources:**
```yaml
retries: 1
retry_delay: 5m
```

**For external APIs or unstable sources:**
```yaml
retries: 2-4
retry_delay: 30m-60m
```

**For critical with dependencies:**
```yaml
retries: 2
retry_delay: 10m
depends_on_past: true
```

## Common Patterns

### Product-Specific DAG
```yaml
bqetl_pocket:
  schedule_interval: 0 2 * * *
  description: |
    Daily aggregations for Pocket data.
    Processes user interactions, recommendations, and content metrics.
  default_args:
    owner: pocket-team@mozilla.com
    start_date: "2024-01-01"
    email: ["telemetry-alerts@mozilla.com", "pocket-team@mozilla.com"]
    retries: 1
    retry_delay: 10m
  tags:
    - impact/tier_2
```

### Hourly Real-Time DAG
```yaml
bqetl_ads_hourly:
  schedule_interval: 30 * * * *
  description: |
    Hourly processing of ad impressions and clicks.
    Provides near real-time metrics for monitoring.
  default_args:
    owner: ads-team@mozilla.com
    start_date: "2024-06-01"
    email: ["telemetry-alerts@mozilla.com", "ads-team@mozilla.com"]
    retries: 2
    retry_delay: 15m
  tags:
    - impact/tier_1
```

### Multi-Source Integration DAG
```yaml
bqetl_cross_product:
  schedule_interval: 0 4 * * *
  description: |
    Cross-product aggregations combining Firefox Desktop, Mobile, and FxA data.
    Runs later to ensure upstream DAGs complete.
  default_args:
    owner: data-eng@mozilla.com
    start_date: "2024-03-01"
    email: ["telemetry-alerts@mozilla.com", "data-eng@mozilla.com"]
    retries: 2
    retry_delay: 20m
  tags:
    - impact/tier_1
```

## Best Practices

### Naming Conventions
- Use `bqetl_` prefix for all DAGs
- Use lowercase with underscores
- Include product/service name
- Add schedule suffix if multiple DAGs for same product (e.g., `_hourly`, `_daily`)

### Scheduling Considerations
- **Avoid peak hours** - Don't schedule at 0:00 UTC (midnight) when many DAGs run
- **Consider dependencies** - Schedule after upstream DAGs complete
- **Time for data availability** - Schedule after external data arrives
- **Stagger related DAGs** - Space them out to avoid resource contention

### Email Configuration
- **Always include** `telemetry-alerts@mozilla.com` for monitoring
- **Add team email** for alerts
- **Add owner email** for direct notifications
- **Consider rotation** - Use team emails, not just individuals

### Documentation
- **Write clear descriptions** - Explain purpose, data sources, dependencies
- **Note special cases** - Document expected failures or timing issues
- **Link to issues** - Reference relevant GitHub issues or documentation
- **Update when changing** - Keep descriptions current

### Start Date Selection
- **Historical data** - Set to earliest date you need to process
- **New product** - Set to product launch date
- **Recent data only** - Set to recent date (e.g., 30 days ago)
- **Be cautious with catchup** - Old start dates + catchup = long backfills

## Troubleshooting

### DAG Not Found
- Check spelling in dags.yaml
- Verify YAML syntax (no tabs, correct indentation)
- Run `./bqetl dag validate <dag_name>`

### Schedule Not Running as Expected
- Verify cron format with online cron checker
- Check for catchup setting
- Review start_date (must be in past)

### Validation Errors
- Required fields missing (schedule_interval, default_args, owner, start_date)
- Invalid email format
- Invalid date format (use "YYYY-MM-DD")
- Invalid schedule_interval format

## Examples in Repository

Reference these existing DAGs as examples:

**Simple daily DAG:**
- `bqetl_core` - Basic daily processing

**Complex daily DAG:**
- `bqetl_fxa_events` - Multiple sources, detailed description

**Hourly DAG:**
- `bqetl_error_aggregates` - 3-hour interval schedule

**High-reliability DAG:**
- `bqetl_subplat` - Critical tier_1, multiple retries, catchup enabled

## Getting Help

If uncertain about DAG configuration:
1. Check similar existing DAGs in dags.yaml
2. Review common patterns above
3. Consult with data engineering team
4. Test with a simple query first
