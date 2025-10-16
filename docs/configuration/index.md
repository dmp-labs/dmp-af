# Configuration

dmp-af provides extensive configuration options to customize how your dbt models are executed in Airflow.

## Configuration Layers

Configuration in dmp-af happens at multiple levels:

### 1. Project Configuration

Set in your DAG file when calling `compile_dmp_af_dags()`:

```python
from dmp_af.conf import Config, DbtProjectConfig, DbtDefaultTargetsConfig

config = Config(
    dbt_project=DbtProjectConfig(...),
    dbt_default_targets=DbtDefaultTargetsConfig(...),
    # Other global settings
)
```

### 2. dbt Project Configuration

Set in `dbt_project.yml` for domain-wide settings:

```yaml
models:
  my_project:
    my_domain:
      sql_cluster: "prod"
      domain_start_date: "2024-01-01T00:00:00"
```

### 3. Model Configuration

Set in model-specific YAML files or in-model config blocks:

```yaml
models:
  - name: my_model
    config:
      schedule: "@daily"
      dependencies:
        upstream_model:
          wait_policy: last
```

## Configuration Topics

### Core Configuration

- **[Model Configuration](model-config.md)** - Per-model settings for schedules, dependencies, and behavior
- **[Schedules](schedules.md)** - Configure when and how often models run
- **[Dependencies](dependencies.md)** - Manage cross-model and cross-domain dependencies
- **[dbt Targets](targets.md)** - Configure dbt target resolution and multi-target setups

### Advanced Configuration

- **[Maintenance](maintenance.md)** - TTL, cleanup tasks, and source freshness
- **[Environment Variables](env-vars.md)** - Pass custom variables to dbt runs
- **[Advanced Options](advanced.md)** - Additional configuration for specialized use cases

## Configuration Entry Points

### dbt Model Config Block

The primary way to configure model behavior:

```sql
-- models/my_model.sql

{{
  config(
    schedule='@daily',
    materialized='table',
    meta={
      'dmp_af': {
        'dependencies': {
          'upstream_model': {'wait_policy': 'last'}
        }
      }
    }
  )
}}

SELECT * FROM {{ ref('upstream_model') }}
```

### Model YAML Files

For cleaner organization:

```yaml
# models/schema.yml

version: 2

models:
  - name: my_model
    config:
      schedule: "@daily"
      dbt_target: "prod"
      dependencies:
        upstream_model:
          wait_policy: last
```

### dbt_project.yml

For domain or project-wide defaults:

```yaml
# dbt_project.yml

models:
  my_project:
    # Applies to all models in my_project
    sql_cluster: "dev"

    staging:
      # Applies only to staging models
      schedule: "@hourly"

    marts:
      # Applies only to marts models
      schedule: "@daily"
      sql_cluster: "prod"
```

## Configuration Precedence

Settings are applied with the following precedence (highest to lowest):

1. **Model-level config** (in model YAML or config block)
2. **Subdirectory config** (in dbt_project.yml)
3. **Domain config** (in dbt_project.yml)
4. **Project config** (in dbt_project.yml)
5. **Global defaults** (in Config object)

Example:

```yaml
# dbt_project.yml
models:
  my_project:  # Project level
    schedule: "@weekly"

    staging:  # Directory level
      schedule: "@daily"

# models/staging/schema.yml
models:
  - name: orders  # Model level
    config:
      schedule: "@hourly"  # This wins!
```

The `orders` model will run `@hourly`.

## Common Configuration Patterns

### Development vs Production

```python
import os

config = Config(
    dbt_project=DbtProjectConfig(
        dbt_project_name='my_project',
        # ... paths ...
    ),
    dbt_default_targets=DbtDefaultTargetsConfig(
        default_target=os.getenv('ENV', 'dev')
    ),
    dry_run=(os.getenv('ENV') == 'dev'),
)
```

### Multi-Domain Setup

```yaml
# dbt_project.yml

models:
  my_project:
    service_layer:
      sql_cluster: "service_cluster"
      daily_sql_cluster: "service_cluster"

    data_marts:
      sql_cluster: "analytics_cluster"
      daily_sql_cluster: "analytics_cluster"
```

### Scheduled + Manual Models

```yaml
# Scheduled model
models:
  - name: daily_orders
    config:
      schedule: "@daily"

# Manual model
  - name: backfill_orders
    config:
      schedule: "@manual"
```

## Validation

dmp-af validates configuration at DAG compile time. Common validation errors:

- **Invalid schedule**: Use supported schedule tags
- **Missing targets**: Ensure all cluster configs are set
- **Circular dependencies**: Check model dependency graph
- **Invalid wait_policy**: Use 'last' or 'all'

## Quick Reference

| Setting | Level | Purpose |
|---------|-------|---------|
| `schedule` | Model | When the model runs |
| `dbt_target` | Model | Which dbt target to use |
| `dependencies` | Model | Cross-model dependencies |
| `enable_from_dttm` | Model | When to start running |
| `disable_from_dttm` | Model | When to stop running |
| `sql_cluster` | Project/Model | Default target for SQL models |
| `py_cluster` | Project/Model | Default target for Python models |
| `domain_start_date` | Domain | DAG start date |
| `env` | Model | Custom environment variables |

## Next Steps

Explore specific configuration topics:

- **[Model Configuration](model-config.md)** - Detailed model settings
- **[Schedules](schedules.md)** - Timing and frequency
- **[Dependencies](dependencies.md)** - Model relationships
- **[dbt Targets](targets.md)** - Target resolution logic
