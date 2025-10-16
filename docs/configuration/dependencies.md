# Dependencies Configuration

Configure how models depend on other models across domains and schedules.

## Overview

dmp-af automatically detects dependencies from `ref()` and `source()` in your dbt models. You can customize this behavior with dependency configuration.

## Dependency Config Options

### `skip`

Skip waiting for an upstream dependency.

**Type**: `bool` (default: `False`)

**Use Case**: When you want to ignore a dependency relationship.

```yaml
models:
  - name: my_model
    config:
      dependencies:
        upstream_model:
          skip: true
```

The model will run without waiting for `upstream_model`.

### `wait_policy`

Control how to wait for upstream models.

**Type**: `str` - either `"last"` or `"all"`

#### `last` (default)

Wait only for the last run of the upstream model based on execution date.

```yaml
models:
  - name: daily_model
    config:
      schedule: "@daily"
      dependencies:
        hourly_model:
          wait_policy: last
```

`daily_model` waits for the single most recent `hourly_model` run.

#### `all`

Wait for all runs of the upstream model between execution intervals.

```yaml
models:
  - name: daily_summary
    config:
      schedule: "@daily"
      dependencies:
        hourly_events:
          wait_policy: all
```

`daily_summary` waits for all 24 hourly runs of `hourly_events` before executing.

## Configuration Examples

### Skip a Dependency

```yaml
# models/schema.yml

models:
  - name: orders_summary
    config:
      dependencies:
        # This model refs raw_orders, but we don't want to wait
        raw_orders:
          skip: true
```

### Cross-Schedule Dependencies

```yaml
# Hourly model
models:
  - name: hourly_metrics
    config:
      schedule: "@hourly"

# Daily model that depends on hourly
  - name: daily_rollup
    config:
      schedule: "@daily"
      dependencies:
        hourly_metrics:
          wait_policy: all  # Wait for all 24 hourly runs
```

### Cross-Domain Dependencies

```yaml
# Domain: svc_orders
models:
  - name: svc_orders.stg.orders
    config:
      schedule: "@daily"

# Domain: dmn_analytics (different DAG)
  - name: dmn_analytics.orders_summary
    config:
      schedule: "@daily"
      dependencies:
        svc_orders.stg.orders:
          wait_policy: last
```

Models in different domains/DAGs can depend on each other using external task sensors.

### Multiple Dependencies

```yaml
models:
  - name: combined_model
    config:
      dependencies:
        model_a:
          wait_policy: last
        model_b:
          skip: true
        model_c:
          wait_policy: all
```

## How Dependencies Work

### Same Domain, Same Schedule

Dependencies within the same DAG use standard Airflow task dependencies (`>>` operator).

```python
# Generated Airflow code (simplified)
upstream_task >> downstream_task
```

### Different Domains or Schedules

Cross-DAG dependencies use `ExternalTaskSensor`:

```python
# Generated Airflow code (simplified)
ExternalTaskSensor(
    task_id=f"wait_for_{upstream_model}",
    external_dag_id="upstream_dag",
    external_task_id="upstream_task",
)
```

### Wait Policy Behavior

#### With `wait_policy: last`

```
Upstream (hourly):  [00:00] [01:00] [02:00] ... [23:00]
                                                    ↓
Downstream (daily):                            [00:00 next day]
```

Waits for the 23:00 run only.

#### With `wait_policy: all`

```
Upstream (hourly):  [00:00] [01:00] [02:00] ... [23:00]
                       ↓      ↓      ↓           ↓
Downstream (daily):                   [00:00 next day]
```

Waits for all 24 hourly runs.

## Dependency Visualization

View dependencies in Airflow:

- **Graph View**: Shows task dependencies within a DAG
- **Task Instance Details**: Shows sensor wait status

![Dependency Graph](../static/cross_domain_dependencies.png)

## Best Practices

### Use `wait_policy: all` for Aggregations

When rolling up frequent data:

```yaml
models:
  - name: daily_summary
    config:
      schedule: "@daily"
      dependencies:
        hourly_facts:
          wait_policy: all  # Ensure all hourly data is ready
```

### Use `wait_policy: last` for Incremental

When processing incrementally:

```yaml
models:
  - name: incremental_model
    config:
      schedule: "@hourly"
      dependencies:
        source_model:
          wait_policy: last  # Just need latest
```

### Use `skip` for Soft Dependencies

When a dependency is optional:

```yaml
models:
  - name: report
    config:
      dependencies:
        optional_enrichment:
          skip: true  # Run even if enrichment fails
```

### Document Cross-Domain Dependencies

Add comments explaining why cross-domain dependencies exist:

```yaml
models:
  - name: analytics_model
    config:
      dependencies:
        # Depends on service layer for cleaned data
        svc_orders.clean_orders:
          wait_policy: last
```

## Troubleshooting

### Sensor Timeouts

If `ExternalTaskSensor` times out:

1. Check upstream DAG is enabled
2. Verify upstream task completed successfully
3. Increase sensor timeout in configuration
4. Check sensor pool has available slots

### Circular Dependencies

dmp-af validates at compile time:

```
Error: Circular dependency detected: model_a -> model_b -> model_a
```

Solution: Restructure your model dependencies.

### Missing Dependencies

If a dependency isn't being enforced:

1. Verify the `ref()` exists in the model
2. Check model names are correct in config
3. Ensure manifest is up-to-date (`dbt compile`)

### Dependencies Not Skipped

If `skip: true` isn't working:

1. Verify the configuration is in the correct model
2. Check YAML syntax
3. Recompile manifest and restart Airflow

## Advanced Patterns

### Conditional Dependencies

Use `enable_from_dttm` with dependencies:

```yaml
models:
  - name: new_model
    config:
      enable_from_dttm: "2024-06-01T00:00:00"
      dependencies:
        upstream:
          wait_policy: last
```

### Dependency Chains

Create multi-hop dependencies:

```yaml
# A -> B -> C

models:
  - name: model_a
    config:
      schedule: "@hourly"

  - name: model_b
    config:
      schedule: "@hourly"
      # Implicit dependency from ref('model_a')

  - name: model_c
    config:
      schedule: "@daily"
      dependencies:
        model_b:
          wait_policy: all
```

## Related Topics

- [Dependency Management Tutorial](../tutorials/dependencies.md) - Step-by-step guide
- [Schedules](schedules.md) - Understanding schedule interactions
- [Cross-Domain Dependencies Feature](../features/cross-domain-deps.md) - Architecture details
