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
