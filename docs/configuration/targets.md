# dbt Targets

Configure how dmp-af resolves dbt targets for model execution.

## Overview

dmp-af supports running different models with different dbt targets (e.g., dev, prod, different warehouses).

## Target Resolution

See the [Advanced Project Tutorial](../tutorials/advanced-project.md#how-is-the-target-determined) for detailed information on how targets are resolved.

## Configuration

### Explicit Target

```yaml
models:
  - name: my_model
    config:
      dbt_target: "prod"
```

### Cluster Targets

```yaml
# dbt_project.yml

models:
  my_project:
    my_domain:
      sql_cluster: "prod"
      py_cluster: "prod_python"
      daily_sql_cluster: "prod"
      bf_cluster: "backfill_cluster"
```

## Related Topics

- [Advanced Project Tutorial](../tutorials/advanced-project.md)
- [Model Configuration](model-config.md)
