# Schedules

Configure when and how often your dbt models run.

## Supported Schedule Tags

dmp-af supports the following schedule tags:

### `@monthly`

Runs once a month on the first day at midnight.

- **Cron**: `0 0 1 * *`
- **Use Case**: Monthly reports, aggregations

```yaml
models:
  - name: monthly_revenue
    config:
      schedule: "@monthly"
```

### `@weekly`

Runs once a week on Sunday at midnight.

- **Cron**: `0 0 * * 0`
- **Use Case**: Weekly summaries, reports

```yaml
models:
  - name: weekly_summary
    config:
      schedule: "@weekly"
```

### `@daily`

Runs once a day at midnight.

- **Cron**: `0 0 * * *`
- **Use Case**: Daily models, most common schedule

```yaml
models:
  - name: daily_orders
    config:
      schedule: "@daily"
```

### `@hourly`

Runs every hour at the beginning of the hour.

- **Cron**: `0 * * * *`
- **Use Case**: Near real-time updates, frequent refreshes

```yaml
models:
  - name: hourly_metrics
    config:
      schedule: "@hourly"
```

### `@every15minutes`

Runs every 15 minutes.

- **Cron**: `*/15 * * * *`
- **Use Case**: Very frequent updates, real-time dashboards

```yaml
models:
  - name: realtime_events
    config:
      schedule: "@every15minutes"
```

### `@manual`

No automatic schedule - run manually only.

- **Use Case**: Backfills, one-off runs, triggered by other DAGs

```yaml
models:
  - name: backfill_model
    config:
      schedule: "@manual"
```

See [Manual Scheduling Tutorial](../tutorials/manual-scheduling.md) for details.

## Schedule Shifts

Offset your schedule by a specified amount using `schedule_shift` and `schedule_shift_unit`.

### Configuration

```yaml
models:
  - name: delayed_model
    config:
      schedule: "@daily"
      schedule_shift: 2
      schedule_shift_unit: "hour"
```

This model runs daily, but 2 hours after midnight (02:00 instead of 00:00).

### Supported Units

- `minute`
- `hour`
- `day`
- `week`

### DAG Naming

Shifted schedules create separate DAGs:

```
<domain>_<schedule>_shift_<N>_<unit>s
```

Example: `sales_daily_shift_2_hours`

### Use Cases

- **Dependency delays**: Wait for upstream data
- **Resource distribution**: Spread load across time
- **Timezone adjustments**: Align with business hours

## Examples

### Multiple Schedules per Domain

```yaml
models:
  - name: hourly_events
    config:
      schedule: "@hourly"

  - name: daily_summary
    config:
      schedule: "@daily"

  - name: weekly_report
    config:
      schedule: "@weekly"
```

This creates three DAGs:

- `domain_hourly`
- `domain_daily`
- `domain_weekly`

### Shifted Schedule

```yaml
models:
  - name: after_hours_model
    config:
      schedule: "@daily"
      schedule_shift: 18
      schedule_shift_unit: "hour"
```

Runs at 18:00 (6 PM) instead of midnight.

### Coordinating Dependencies

```yaml
# Runs at midnight
models:
  - name: source_model
    config:
      schedule: "@daily"

# Runs at 01:00, after source_model
  - name: derived_model
    config:
      schedule: "@daily"
      schedule_shift: 1
      schedule_shift_unit: "hour"
      dependencies:
        source_model:
          wait_policy: last
```

## Best Practices

### Choose Appropriate Frequency

- **@every15minutes**: Only for models that truly need real-time data
- **@hourly**: For frequently changing data
- **@daily**: Default for most analytical workloads
- **@weekly/@monthly**: For summary and reporting tables

### Consider Resource Usage

More frequent schedules mean:

- Higher compute costs
- More database load
- More Airflow task slots used

### Use Schedule Shifts

Instead of creating custom cron schedules, use shifts:

```yaml
# Good
schedule: "@daily"
schedule_shift: 6
schedule_shift_unit: "hour"

# Avoid custom cron (not supported)
schedule: "0 6 * * *"  # This won't work!
```

### Group by Schedule

Models with the same schedule in the same domain run in one DAG:

```yaml
models:
  - name: model_a
    config:
      schedule: "@daily"

  - name: model_b
    config:
      schedule: "@daily"  # Same DAG as model_a

  - name: model_c
    config:
      schedule: "@hourly"  # Different DAG
```

## Troubleshooting

### Model Not Running on Schedule

1. Check DAG is enabled in Airflow UI
2. Verify schedule tag spelling
3. Check Airflow scheduler is running
4. Review DAG catchup settings

### Wrong Schedule Time

1. Verify timezone in Airflow configuration
2. Check `schedule_shift` settings
3. Review `domain_start_date`

### Too Many DAGs Created

Each combination of domain + schedule creates a DAG. Consider:

- Consolidating schedules
- Using schedule shifts instead of different schedules
- Grouping models by domain

## Related Topics

- [Dependencies](dependencies.md) - Managing cross-schedule dependencies
- [Manual Scheduling Tutorial](../tutorials/manual-scheduling.md) - Using @manual
- [Model Configuration](model-config.md) - All model config options
