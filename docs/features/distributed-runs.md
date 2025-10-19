# Distributed Runs

Each dbt model becomes an independent Airflow task.

## Benefits

- **Parallel Execution**: Models run simultaneously when possible
- **Granular Retries**: Retry individual models, not entire runs
- **Better Monitoring**: Track each model separately
- **Resource Optimization**: Allocate resources per model

## How It Works

Instead of:
```
one_big_dbt_run [runs all 100 models sequentially]
```

You get:
```
model_a → model_c
model_b → model_c
model_d
...
```

Each model is a separate task with proper dependencies.

## Idempotency

Every task receives execution dates:
- `start_dttm`: Interval start
- `end_dttm`: Interval end

Use these in your models for idempotent processing.

### Time Interval Variables

dmp-af automatically passes time interval variables to each dbt model via the `--vars` flag. These variables enable idempotent, incremental processing.

#### Available Variables

Each model receives these variables:

- **`start_dttm`**: Start of the processing interval (ISO 8601 format)
- **`end_dttm`**: End of the processing interval (ISO 8601 format)
- **`overlap`**: Boolean flag (default: `false`)

Access these in your dbt models using Jinja:

```sql
-- models/my_model.sql
SELECT *
FROM raw_events
WHERE event_time >= '{{ var("start_dttm") }}'
  AND event_time < '{{ var("end_dttm") }}'
```

#### How Intervals Are Determined

The time interval logic varies based on how the task is triggered:

**1. Scheduled Runs (Most Common)**

For normal scheduled DAG runs, the interval matches Airflow's data interval:

```
start_dttm = data_interval_start
end_dttm = data_interval_end
```

Example for a daily DAG:
- `data_interval_start`: `2024-01-15T00:00:00`
- `data_interval_end`: `2024-01-16T00:00:00`
- → Model processes data for Jan 15

**2. Manual Triggers**

When manually triggering a DAG (without custom conf), Airflow sets `data_interval_start == data_interval_end`. In this case, dmp-af runs for a full day starting from midnight:

```
start_dttm = data_interval_start.date() at 00:00:00
end_dttm = start_dttm + 1 day
```

Example:
- Manual trigger at `2024-01-15T14:30:00`
- `data_interval_start == data_interval_end`: `2024-01-15T14:30:00`
- → `start_dttm`: `2024-01-15T00:00:00`
- → `end_dttm`: `2024-01-16T00:00:00`
- → Model processes full day of Jan 15

**3. User-Defined Parameters**

You can override the automatic interval by passing `start_dttm` and `end_dttm` in the DAG run configuration:

```json
{
  "start_dttm": "2024-01-01T00:00:00",
  "end_dttm": "2024-01-10T00:00:00"
}
```

This is useful for:
- Backfilling specific date ranges
- Processing custom time windows
- Running the `dbt_run_model` DAG

When provided, these values are used directly (and renamed to `dbt_start_dttm` and `dbt_end_dttm` internally before being exposed as `start_dttm` and `end_dttm` to dbt models).

#### Additional Variables

Any extra parameters passed via DAG configuration are also forwarded to dbt models:

```json
{
  "start_dttm": "2024-01-01T00:00:00",
  "end_dttm": "2024-01-10T00:00:00",
  "custom_param": "value",
  "region": "us-west"
}
```

Access these in dbt models:
```sql
WHERE region = '{{ var("region") }}'
```

**Note on array/list values**: Arrays are converted to PostgreSQL-compatible tuple format:
- `["a", "b", "c"]` → `("a","b","c")`
- `[]` → `("")` (empty string for compatibility with string fields)

#### Best Practices

1. **Always use intervals**: Design models to process specific time ranges, not full table scans
2. **Use half-open intervals**: Filter with `>= start_dttm AND < end_dttm` to avoid duplicate processing at boundaries
3. **Handle timezone-aware timestamps**: Ensure your data and intervals use consistent timezones
4. **Test with different intervals**: Verify your model works for daily, hourly, and custom ranges

#### Example Model

```sql
-- models/incremental_events.sql
{{
    config(
        materialized='incremental',
        unique_key='event_id'
    )
}}

SELECT
    event_id,
    user_id,
    event_time,
    event_type
FROM {{ source('raw', 'events') }}
WHERE event_time >= '{{ var("start_dttm") }}'
  AND event_time < '{{ var("end_dttm") }}'

{% if is_incremental() %}
  -- Optional: Add additional logic for incremental runs
  AND event_time > (SELECT MAX(event_time) FROM {{ this }})
{% endif %}
```

This pattern ensures each run processes exactly one time interval, making reruns safe and predictable.
